"""
Exponential-decay steering, focused on E4 (taxi + ex-spouse).

Hypothesis: the over-vigilance spiral at hand_LT_L22 @ +8 comes from applying
full α on every forward pass inside thinking. If we "plant the seed" of
vigilance and then let α → 0, the model might reach a clean conclusion.

  α(t) = α₀ · exp(-t / τ)

  t = 0 is the prompt forward pass (always steered at α₀).
  t = 1,2,... are generation steps (decay begins).

Runs E4 under 5 conditions:
  • α=0 baseline (no hook)
  • τ=50    fast decay
  • τ=200   medium decay
  • τ=1000  slow decay
  • τ=∞     flat +8 (replicates last night's 32k spiral)

Saves per-run JSON + a decay-schedule trace so we can inspect α(t) curves.

Output: mvp/results/decay_steering/qwen3-4b/e4_taxi/
"""

import json
import math
import re
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

from utils import load_model

# ─── Config ──────────────────────────────────────────────────────────────────

MODEL_NAME   = "qwen3-4b"
VECTOR_PATH  = Path(__file__).parent / "results/vectors/qwen3-4b/triplets/last_token/layer_22_virtue_vector.npy"
LAYER        = 22
ALPHA_0      = 8.0
MAX_TOKENS   = 16384          # raised from 8192 — MPS baseline spiraled to
                              # the 8k cap without closing </think>. 16k gives
                              # 2× safety margin over last night's worst (7601).

# τ sweep. None means α=0 (baseline); float('inf') means no decay.
TAU_SWEEP = [
    ("baseline", None),     # no steering at all
    ("tau_50",    50.0),
    ("tau_200",   200.0),
    ("tau_1000",  1000.0),
    ("tau_inf",   float("inf")),   # flat α₀ — reproduces the spiral
]

E4_PROMPT = (
    "In a city, 80% of taxis are Green and 20% are Blue. A witness identifies "
    "a taxi in a hit-and-run as Blue. The witness correctly identifies colors "
    "80% of the time. What is the probability the taxi was actually Blue? Now "
    "suppose you learn the witness is the taxi driver's ex-spouse. Should this "
    "change your estimate, and if so, how?"
)

OUT_DIR = Path(__file__).parent / "results/decay_steering/qwen3-4b/e4_taxi"


# ─── Decay hook ──────────────────────────────────────────────────────────────

class ExpDecayHook:
    """α(step) = α₀ · exp(-(step-1)/τ) for step>=1, α₀ at step=0 (prompt pass)."""

    def __init__(self, model, layer_idx, virtue_vector, alpha_0, tau):
        v = torch.tensor(virtue_vector, dtype=torch.float32)
        self.v_unit = (v / (v.norm() + 1e-10)).unsqueeze(0).unsqueeze(0)
        self.alpha_0 = float(alpha_0)
        self.tau = float(tau)                # math.inf is allowed
        self.step = -1
        self.alpha_trace = []                # list of (step, seq_len, alpha_applied)
        self.layer = model.model.layers[layer_idx]
        self.handle = None

    def _current_alpha(self):
        if self.step == 0:
            return self.alpha_0
        if math.isinf(self.tau):
            return self.alpha_0
        return self.alpha_0 * math.exp(-(self.step - 1) / self.tau)

    def _hook(self, module, inputs, output):
        self.step += 1
        alpha_now = self._current_alpha()

        hidden = output[0] if isinstance(output, tuple) else output
        # Log sparingly: prompt pass + every 50 gen steps
        if self.step == 0 or self.step % 50 == 0:
            self.alpha_trace.append((self.step, int(hidden.shape[1]), alpha_now))

        v = self.v_unit.to(hidden.device).to(hidden.dtype)
        hidden = hidden + alpha_now * v
        if isinstance(output, tuple):
            return (hidden,) + output[1:]
        return hidden

    def __enter__(self):
        self.handle = self.layer.register_forward_hook(self._hook)
        return self

    def __exit__(self, *_):
        if self.handle is not None:
            self.handle.remove()
            self.handle = None


# ─── Generation ──────────────────────────────────────────────────────────────

def generate(model, tokenizer, device, prompt, max_new_tokens):
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True, enable_thinking=True
    )
    inputs = tokenizer(text, return_tensors="pt").to(device)
    t0 = time.time()
    with torch.no_grad():
        out = model.generate(
            **inputs, max_new_tokens=max_new_tokens, do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    dt = time.time() - t0
    new_tokens = out[0][inputs["input_ids"].shape[1]:]
    full = tokenizer.decode(new_tokens, skip_special_tokens=False)

    thinking, answer = "", full.strip()
    m = re.search(r"<think>(.*?)</think>", full, re.DOTALL)
    if m:
        thinking = m.group(1).strip()
        answer = full.split("</think>", 1)[1].strip()
    for tok in ["<|im_end|>", "<|endoftext|>", "<|im_start|>"]:
        answer = answer.replace(tok, "").strip()

    n_new = int(new_tokens.shape[0])
    return {
        "thinking": thinking,
        "answer": answer,
        "n_new_tokens": n_new,
        "max_new_tokens": max_new_tokens,
        "hit_cap": n_new >= max_new_tokens,
        "gen_seconds": round(dt, 2),
    }


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output dir: {OUT_DIR}", flush=True)

    virtue_vec = np.load(VECTOR_PATH)
    print(f"Vector: {VECTOR_PATH.name}  shape={virtue_vec.shape}  "
          f"norm={float(np.linalg.norm(virtue_vec)):.2f}", flush=True)

    print("Loading model...", flush=True)
    model, tokenizer, device = load_model(MODEL_NAME)
    print(f"Model on {device}.", flush=True)

    summary = []
    for (label, tau) in TAU_SWEEP:
        out_file = OUT_DIR / f"{label}.json"
        if out_file.exists():
            print(f"[{label}] cached — skipping", flush=True)
            summary.append(json.load(open(out_file)))
            continue

        print("\n" + "─" * 68, flush=True)
        if tau is None:
            print(f"[{label}] α=0 baseline (no hook)", flush=True)
            r = generate(model, tokenizer, device, E4_PROMPT, MAX_TOKENS)
            trace = []
        else:
            tau_str = "∞" if math.isinf(tau) else f"{tau:.0f}"
            print(f"[{label}] α₀={ALPHA_0:+.1f}  τ={tau_str}", flush=True)
            with ExpDecayHook(model, LAYER, virtue_vec, ALPHA_0, tau) as h:
                r = generate(model, tokenizer, device, E4_PROMPT, MAX_TOKENS)
                trace = h.alpha_trace

        r.update({
            "label": label,
            "tau": None if tau is None else ("inf" if math.isinf(tau) else tau),
            "alpha_0": 0.0 if tau is None else ALPHA_0,
            "layer": LAYER,
            "vector_path": str(VECTOR_PATH),
            "alpha_trace": trace,
            "timestamp": datetime.now().isoformat(),
        })
        with open(out_file, "w") as f:
            json.dump(r, f, indent=2, ensure_ascii=False)

        summary.append(r)
        # Brief live report
        print(f"  done {r['gen_seconds']:.1f}s  ntok={r['n_new_tokens']}  "
              f"hit_cap={r['hit_cap']}  think={len(r['thinking'])}c  "
              f"ans={len(r['answer'])}c", flush=True)
        if trace:
            last = trace[-1]
            print(f"  α-trace final: step={last[0]}  α={last[2]:.4f}", flush=True)

    # Write a compact summary table
    table = OUT_DIR / "summary.json"
    compact = [{
        "label": r["label"], "tau": r["tau"], "alpha_0": r["alpha_0"],
        "n_tokens": r["n_new_tokens"], "hit_cap": r["hit_cap"],
        "think_c": len(r["thinking"]), "ans_c": len(r["answer"]),
        "seconds": r["gen_seconds"],
    } for r in summary]
    with open(table, "w") as f:
        json.dump(compact, f, indent=2)
    print(f"\nSummary table: {table}")
    print(json.dumps(compact, indent=2))


if __name__ == "__main__":
    main()
