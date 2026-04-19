"""
Multi-vector steering experiment — testing the hydra-effect hypothesis.

Our single-vector sweep revealed layer specialization:
  - hand_LT_L20 handles E3/E4 (Bayesian) at many α
  - hand_LT_L22 handles N2 (conjunction) at narrow α=+8
  - Neither layer alone unlocks all 3 hard prompts

Literature (van der Weij 2024, Beyond Linear Steering 2025) says the
"hydra effect" — behaviors distributed across layers — is best addressed
by simultaneous layer-wise multi-vector steering rather than composing
two vectors at a single location.

This script tests that directly on our 5 hard prompts.

Output: mvp/results/multivector/qwen3-4b/
Resume-safe: per-cell JSON files; re-running skips existing cells.
"""

import json
import re
import time
import traceback
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

from utils import load_model

# ─── Config ──────────────────────────────────────────────────────────────────

MODEL_NAME = "qwen3-4b"

MVP = Path(__file__).parent
VECTOR_ROOT = MVP / "results" / "vectors" / "qwen3-4b"
PROMPTS_PATH = MVP.parent / "corpus" / "eval-prompts" / "focused-v2.json"
OUT_ROOT = MVP / "results" / "multivector" / "qwen3-4b"

# Vector registry
VEC_L20 = VECTOR_ROOT / "triplets/last_token/layer_20_virtue_vector.npy"
VEC_L22 = VECTOR_ROOT / "triplets/last_token/layer_22_virtue_vector.npy"

# Experiment configs — each is a list of (layer_idx, vector_name, alpha)
# alpha=0 means don't attach a hook at that layer (effectively unsteered there)
CONFIGS = [
    ("baseline",              []),
    ("solo_L20_mid",          [(20, "L20", 4.0)]),
    ("solo_L20_high",         [(20, "L20", 12.0)]),
    ("solo_L22_N2",           [(22, "L22", 8.0)]),
    ("combo_balanced",        [(20, "L20", 4.0), (22, "L22", 4.0)]),
    ("combo_L20strong",       [(20, "L20", 8.0), (22, "L22", 4.0)]),
    ("combo_L22strong",       [(20, "L20", 4.0), (22, "L22", 8.0)]),
    ("combo_strong",          [(20, "L20", 8.0), (22, "L22", 8.0)]),
    ("combo_ortho",           [(20, "L20", 4.0), (22, "L22_ortho", 4.0)]),  # special
]

# Only run the 5 "live" prompts where steering has signal to show
PROMPT_IDS_FILTER = {
    "E2-contested-science",
    "E3-bayesian-update",
    "E4-taxi-social",
    "N1-simpsons-paradox",
    "N2-conjunction-fallacy",
}


# ─── Logging ─────────────────────────────────────────────────────────────────

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    with open(OUT_ROOT / "run.log", "a") as f:
        f.write(line + "\n")


# ─── Hooks: single + multi + orthogonalized ──────────────────────────────────

class AdditiveHook:
    """Single-layer CAA: h' = h + alpha * unit(v)."""
    def __init__(self, model, layer_idx, virtue_vector, alpha):
        v = torch.tensor(virtue_vector, dtype=torch.float32)
        self.v_unit = (v / (v.norm() + 1e-10)).unsqueeze(0).unsqueeze(0)
        self.alpha = float(alpha)
        self.layer = model.model.layers[layer_idx]
        self.handle = None

    def _hook(self, module, inputs, output):
        hidden = output[0] if isinstance(output, tuple) else output
        v = self.v_unit.to(hidden.device).to(hidden.dtype)
        hidden = hidden + self.alpha * v
        if isinstance(output, tuple):
            return (hidden,) + output[1:]
        return hidden

    def attach(self):
        self.handle = self.layer.register_forward_hook(self._hook)

    def detach(self):
        if self.handle is not None:
            self.handle.remove()
            self.handle = None


class MultiHookContext:
    """Context manager: attach multiple AdditiveHooks at different layers, detach on exit."""
    def __init__(self, model, injections):
        # injections = list of (layer_idx, vector_ndarray, alpha)
        self.hooks = [AdditiveHook(model, l, v, a) for (l, v, a) in injections]

    def __enter__(self):
        for h in self.hooks:
            h.attach()
        return self

    def __exit__(self, *_):
        for h in self.hooks:
            h.detach()


def make_ortho_L22(v_L20: np.ndarray, v_L22: np.ndarray) -> np.ndarray:
    """Project v_L22 onto the plane orthogonal to v_L20."""
    u = v_L20 / (np.linalg.norm(v_L20) + 1e-10)
    parallel = (v_L22 @ u) * u
    ortho = v_L22 - parallel
    return ortho


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


# ─── IO ──────────────────────────────────────────────────────────────────────

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    tmp.replace(path)

def append_summary(row):
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    with open(OUT_ROOT / "summary.jsonl", "a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    log("=" * 72)
    log("Multi-vector steering experiment — START")

    # Load vectors
    v_L20 = np.load(VEC_L20)
    v_L22 = np.load(VEC_L22)
    v_L22_ortho = make_ortho_L22(v_L20, v_L22)
    cos_L20_L22 = float(v_L20 @ v_L22 / (np.linalg.norm(v_L20) * np.linalg.norm(v_L22)))
    log(f"vectors loaded: L20 norm={np.linalg.norm(v_L20):.2f}  L22 norm={np.linalg.norm(v_L22):.2f}")
    log(f"cosine(L20, L22) = {cos_L20_L22:.4f}  (ortho direction has norm {np.linalg.norm(v_L22_ortho):.2f})")

    VEC_BY_NAME = {"L20": v_L20, "L22": v_L22, "L22_ortho": v_L22_ortho}

    # Load prompts
    prompts = [p for p in json.load(open(PROMPTS_PATH)) if p["id"] in PROMPT_IDS_FILTER]
    log(f"prompts: {len(prompts)} ({[p['id'] for p in prompts]})")

    # Write manifest
    manifest = {
        "started_at": datetime.now().isoformat(),
        "model": MODEL_NAME,
        "cosine_L20_L22": cos_L20_L22,
        "configs": [
            {"id": cid, "injections": [
                {"layer": l, "vector": vn, "alpha": a} for (l, vn, a) in inj
            ]} for (cid, inj) in CONFIGS
        ],
        "prompts": [p["id"] for p in prompts],
        "per_prompt_caps": {p["id"]: p.get("max_new_tokens", 4096) for p in prompts},
    }
    write_json(OUT_ROOT / "manifest.json", manifest)

    log(f"Loading model {MODEL_NAME}...")
    model, tokenizer, device = load_model(MODEL_NAME)
    log(f"Model on {device}. Ready.")

    total = len(CONFIGS) * len(prompts)
    done = 0
    run_start = time.time()

    for (config_id, injections_spec) in CONFIGS:
        log("═" * 72)
        log(f"CONFIG: {config_id}  injections={injections_spec}")
        config_dir = OUT_ROOT / config_id
        config_dir.mkdir(parents=True, exist_ok=True)

        # Build concrete injections with actual vectors
        concrete_injections = [
            (layer, VEC_BY_NAME[vname], alpha)
            for (layer, vname, alpha) in injections_spec
        ]

        for p in prompts:
            pid = p["id"]
            cap = p.get("max_new_tokens", 4096)
            done += 1
            out_file = config_dir / f"{pid}.json"

            if out_file.exists():
                log(f"  [{done}/{total}] {pid}: cached")
                continue

            log(f"  [{done}/{total}] {pid}: generating (cap={cap})...")
            try:
                if concrete_injections:
                    with MultiHookContext(model, concrete_injections):
                        r = generate(model, tokenizer, device, p["prompt"], cap)
                else:
                    # baseline — no hooks
                    r = generate(model, tokenizer, device, p["prompt"], cap)
            except Exception as e:
                log(f"    ERROR: {e}\n{traceback.format_exc()}")
                continue

            r.update({
                "config_id": config_id,
                "injections": injections_spec,
                "prompt_id": pid,
                "prompt": p["prompt"],
                "category": p.get("category", ""),
                "timestamp": datetime.now().isoformat(),
            })
            write_json(out_file, r)
            append_summary({
                "config_id": config_id,
                "prompt_id": pid,
                "n_tokens": r["n_new_tokens"],
                "hit_cap": r["hit_cap"],
                "seconds": r["gen_seconds"],
                "think_c": len(r["thinking"]),
                "ans_c": len(r["answer"]),
            })
            elapsed = time.time() - run_start
            eta_s = (elapsed / max(done, 1)) * (total - done)
            log(f"    done {r['gen_seconds']:.1f}s  ntok={r['n_new_tokens']}  "
                f"hit_cap={r['hit_cap']}  think={len(r['thinking'])}c "
                f"ans={len(r['answer'])}c  ETA {eta_s/60:.0f}min")

    log("=" * 72)
    log(f"COMPLETE — {done} generations in {(time.time()-run_start)/60:.1f} min")
    write_json(OUT_ROOT / "manifest.json",
               {**manifest, "finished_at": datetime.now().isoformat(),
                "total_generations": done})


if __name__ == "__main__":
    main()
