"""
Phronesis — Qwen3-4B steering sweep v3 (redesigned after last-night audit).

Changes from v2:
  • PER-PROMPT max_new_tokens (read from prompt JSON) — E3/E4 now get 8192,
    rest 2048, matching focused-v2's tight caps. Flat 4096 truncated E3/E4.
  • 8 prompts instead of 5 — adds N1 (Simpson's), N2 (conjunction),
    N3 (survivorship). N2 was last-night's strongest signal.
  • 8 vectors instead of 8 CP/LT mix:
      4 L22-neighborhood hand_LT layers (L20, L21, L22, L23)
      1 mid-late hand_LT (L27)
      2 cross-corpus sonnet (son_LT_L22, son_LT_L34)
      1 random_L22 control (re-uses GCP's random_vector_L22.npy)
    Dropped: hand_CP_* (weaker), hand_LT_L10 (underperformed), son_LT_L27.
  • 10 alphas: [-8, -4, -2, +1, +2, +4, +8, +12, +16, +20]
    Dropped +0.5 (noise). Added +16/+20 (E2 calibration only moved at +12).

Resume-safe: per-generation JSON files; re-running skips anything already
present. Per-prompt baselines saved once and reused across vectors.

Output layout:
    mvp/results/steering/qwen3-4b/
        manifest.json
        run.log
        summary.jsonl
        baselines/{pid}.json                        # α=0, one per prompt
        {vec_id}/a{signed_alpha}/{pid}.json         # one per steered gen
"""

import json
import re
import time
import traceback
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

from utils import MODEL_CONFIGS, RESULTS_DIR, load_model


# ─── Config ──────────────────────────────────────────────────────────────────

MODEL_NAME = "qwen3-4b"
DEFAULT_MAX_TOKENS = 4096  # fallback if prompt doesn't specify

VECTOR_ROOT = Path(__file__).parent / "results" / "vectors" / MODEL_NAME

# (short_id, path_to_npy_from_VECTOR_ROOT-or-absolute, layer_index)
# Focused design after analysis of first ~240 gens:
#   L27 dead (0/12 close hard prompts). L10 weak. CP vectors weaker probes.
#   L20 champions E3/E4, L22 champions N2. L21 added as bridge.
VECTORS = [
    ("hand_LT_L20",  "triplets/last_token/layer_20_virtue_vector.npy", 20),
    ("hand_LT_L21",  "triplets/last_token/layer_21_virtue_vector.npy", 21),
    ("hand_LT_L22",  "triplets/last_token/layer_22_virtue_vector.npy", 22),
    ("son_LT_L34",   "triplets-synthetic-sonnet/last_token/layer_34_virtue_vector.npy", 34),
    ("random_L22",   "random_L22_vector.npy", 22),
]

# Dropped extremes (-8, -2, +0.5, +16, +20) — no signal there.
ALPHAS = [-4.0, 1.0, 2.0, 4.0, 8.0, 12.0]

PROMPTS_PATH = Path(__file__).parent.parent / "corpus" / "eval-prompts" / "focused-v2.json"

# Only run the prompts that actually differentiate. E1/E5/N3 closed on every
# condition (no signal). Keep the 5 that move.
PROMPT_IDS_FILTER = {
    "E2-contested-science",
    "E3-bayesian-update",
    "E4-taxi-social",
    "N1-simpsons-paradox",
    "N2-conjunction-fallacy",
}
OUT_ROOT = Path(__file__).parent / "results" / "steering" / MODEL_NAME


# ─── Logging ─────────────────────────────────────────────────────────────────

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    with open(OUT_ROOT / "run.log", "a") as f:
        f.write(line + "\n")


# ─── Steering hook ───────────────────────────────────────────────────────────

class AdditiveHook:
    """CAA-style: h' = h + alpha * unit(v). alpha is in 'unit-vector multiples'."""
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
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    dt = time.time() - t0
    new_tokens = out[0][inputs["input_ids"].shape[1]:]
    full = tokenizer.decode(new_tokens, skip_special_tokens=False)

    thinking = ""
    answer = full.strip()
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
        "max_new_tokens_used": max_new_tokens,
        "hit_token_limit": n_new >= max_new_tokens,
        "gen_seconds": round(dt, 2),
    }


# ─── IO helpers ──────────────────────────────────────────────────────────────

def alpha_tag(a):
    sign = "+" if a >= 0 else "-"
    return f"a{sign}{abs(a):05.2f}"

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

def load_vector(rel_path):
    """Load .npy from VECTOR_ROOT/rel_path. Supports vectors at the root level."""
    p = VECTOR_ROOT / rel_path
    if not p.exists():
        raise FileNotFoundError(str(p))
    v = np.load(p)
    return v, str(p)


# ─── Main sweep ──────────────────────────────────────────────────────────────

def main():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    log("=" * 72)
    log("Qwen3-4B steering sweep v3 — START")
    log(f"Vectors: {len(VECTORS)}  Alphas: {len(ALPHAS)}  Prompts: (loaded below)")

    all_prompts = json.load(open(PROMPTS_PATH))
    # Apply focused filter — only prompts that actually differentiate.
    prompts = [p for p in all_prompts if p["id"] in PROMPT_IDS_FILTER]
    log(f"Prompt filter: using {len(prompts)}/{len(all_prompts)} prompts")
    caps = [p.get("max_new_tokens", DEFAULT_MAX_TOKENS) for p in prompts]
    log(f"Prompts ({len(prompts)}):")
    for p, c in zip(prompts, caps):
        log(f"    {p['id']:30s}  cap={c}")
    total_target = len(prompts) + len(VECTORS) * len(ALPHAS) * len(prompts)
    log(f"Total generations target: {total_target}")

    manifest = {
        "version": 3,
        "model": MODEL_NAME,
        "started_at": datetime.now().isoformat(),
        "per_prompt_caps": {p["id"]: p.get("max_new_tokens", DEFAULT_MAX_TOKENS) for p in prompts},
        "vectors": [{"id": vid, "rel_path": rp, "layer": layer} for (vid, rp, layer) in VECTORS],
        "alphas": ALPHAS,
        "prompts": [p["id"] for p in prompts],
    }
    write_json(OUT_ROOT / "manifest.json", manifest)

    log(f"Loading model {MODEL_NAME} ...")
    model, tokenizer, device = load_model(MODEL_NAME)
    log(f"Model on {device}. Ready.")

    # ── Baselines (α=0, no hook) ──
    baseline_dir = OUT_ROOT / "baselines"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    log("─── BASELINES (no steering) ───")
    for i, p in enumerate(prompts):
        pid = p["id"]
        bpath = baseline_dir / f"{pid}.json"
        cap = p.get("max_new_tokens", DEFAULT_MAX_TOKENS)
        if bpath.exists():
            rec = json.load(open(bpath))
            log(f"  [{i+1}/{len(prompts)}] {pid}: cached (ntok={rec.get('n_new_tokens','?')})")
            continue
        log(f"  [{i+1}/{len(prompts)}] {pid}: generating (cap={cap})...")
        try:
            r = generate(model, tokenizer, device, p["prompt"], cap)
        except Exception as e:
            log(f"    ERROR: {e}\n{traceback.format_exc()}")
            continue
        r.update({"prompt_id": pid, "prompt": p["prompt"], "alpha": 0.0,
                  "vector_id": None,
                  "category": p.get("category", ""),
                  "timestamp": datetime.now().isoformat()})
        write_json(bpath, r)
        append_summary({"kind": "baseline", "prompt_id": pid, "cap": cap,
                        "n_tokens": r["n_new_tokens"], "hit_cap": r["hit_token_limit"],
                        "seconds": r["gen_seconds"],
                        "think_c": len(r["thinking"]), "ans_c": len(r["answer"])})
        log(f"    done {r['gen_seconds']:.1f}s  ntok={r['n_new_tokens']}  "
            f"hit_cap={r['hit_token_limit']}  think={len(r['thinking'])}c "
            f"ans={len(r['answer'])}c")

    # ── Steered sweep ──
    done = 0
    total_steered = len(VECTORS) * len(ALPHAS) * len(prompts)
    run_start = time.time()

    for (vid, rel_path, layer) in VECTORS:
        try:
            v_raw, vpath = load_vector(rel_path)
        except FileNotFoundError as e:
            log(f"!! vector not found for {vid}: {e}  (skipping)")
            done += len(ALPHAS) * len(prompts)
            continue

        log("═" * 72)
        log(f"VECTOR {vid} — path={rel_path}  layer=L{layer}  "
            f"raw_norm={float(np.linalg.norm(v_raw)):.2f}")

        for alpha in ALPHAS:
            tag = alpha_tag(alpha)
            adir = OUT_ROOT / vid / tag
            adir.mkdir(parents=True, exist_ok=True)

            log(f"  ─ α={alpha:+.2f} ({tag}) ─")
            with AdditiveHook(model, layer, v_raw, alpha):
                for i, p in enumerate(prompts):
                    pid = p["id"]
                    cap = p.get("max_new_tokens", DEFAULT_MAX_TOKENS)
                    done += 1
                    rpath = adir / f"{pid}.json"
                    if rpath.exists():
                        log(f"    [{done}/{total_steered}] {pid}: cached")
                        continue
                    log(f"    [{done}/{total_steered}] {pid}: generating (cap={cap})...")
                    try:
                        r = generate(model, tokenizer, device, p["prompt"], cap)
                    except Exception as e:
                        log(f"      ERROR: {e}\n{traceback.format_exc()}")
                        continue
                    r.update({
                        "prompt_id": pid, "prompt": p["prompt"],
                        "alpha": alpha, "vector_id": vid, "vector_path": vpath,
                        "layer": layer,
                        "category": p.get("category", ""),
                        "timestamp": datetime.now().isoformat(),
                    })
                    write_json(rpath, r)
                    append_summary({
                        "kind": "steered", "vector_id": vid, "alpha": alpha,
                        "prompt_id": pid, "cap": cap,
                        "n_tokens": r["n_new_tokens"], "hit_cap": r["hit_token_limit"],
                        "seconds": r["gen_seconds"],
                        "think_c": len(r["thinking"]),
                        "ans_c": len(r["answer"]),
                    })
                    elapsed = time.time() - run_start
                    eta_s = (elapsed / max(done, 1)) * (total_steered - done)
                    log(f"      done {r['gen_seconds']:.1f}s  ntok={r['n_new_tokens']}  "
                        f"hit_cap={r['hit_token_limit']}  "
                        f"think={len(r['thinking'])}c ans={len(r['answer'])}c  "
                        f"ETA {eta_s/60:.0f}min")

    log("=" * 72)
    log(f"SWEEP COMPLETE — total {done} generations in {(time.time()-run_start)/60:.1f} min")
    write_json(OUT_ROOT / "manifest.json",
               {**manifest, "finished_at": datetime.now().isoformat(),
                "total_generations": done + len(prompts)})


if __name__ == "__main__":
    main()
