"""
Phronesis -- Focused steering run (v2).

Targeted experiment: 3 virtue vectors + 1 random control, 4 alpha values,
8 prompts with per-prompt token limits.  Writes each result to disk
immediately as it completes.

Usage:
    cd mvp && .venv/bin/python -u run_focused_steering.py
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


# --- Config -------------------------------------------------------------------

MODEL_NAME = "qwen3-4b"

VECTORS = [
    # (short_id, corpus, method, layer)
    ("hand_LT_L22", "triplets",                  "last_token", 22),
    ("son_LT_L34",  "triplets-synthetic-sonnet",  "last_token", 34),
    ("hand_LT_L10", "triplets",                  "last_token", 10),
]

ALPHAS = [-4.0, 2.0, 8.0]          # baseline (0.0) is generated separately

RANDOM_SEED = 42
RANDOM_LAYER = 22                    # same layer as best virtue vector
HIDDEN_DIM = MODEL_CONFIGS[MODEL_NAME]["hidden_dim"]

OUT_ROOT = Path(__file__).parent / "results" / "steering_v2" / MODEL_NAME
VECTOR_ROOT = Path(__file__).parent / "results" / "vectors" / MODEL_NAME
PROMPTS_PATH = (Path(__file__).parent.parent / "corpus" /
                "eval-prompts" / "focused-v2.json")


# --- Logging ------------------------------------------------------------------

LOG_PATH = OUT_ROOT / "run.log"


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")


# --- Steering hook ------------------------------------------------------------

class AdditiveHook:
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


# --- Generation ---------------------------------------------------------------

SPECIAL_TOKENS = [
    "\u003c|im_end|\u003e",
    "\u003c|endoftext|\u003e",
    "\u003c|im_start|\u003e",
]


def generate(model, tokenizer, device, prompt, max_new_tokens):
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True,
        enable_thinking=True,
    )
    inputs = tokenizer(text, return_tensors="pt").to(device)

    t0 = time.time()
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=None,
            top_p=None,
            top_k=None,
            pad_token_id=tokenizer.eos_token_id,
        )
    dt = time.time() - t0
    new_tokens = out[0][inputs["input_ids"].shape[1]:]
    full = tokenizer.decode(new_tokens, skip_special_tokens=False)

    # Parse <think>...</think>
    thinking = ""
    answer = full.strip()
    m = re.search(r"\u003cthink\u003e(.*?)\u003c/think\u003e", full, re.DOTALL)
    if m:
        thinking = m.group(1).strip()
        answer = full.split("\u003c/think\u003e", 1)[1].strip()
    # strip special tokens from answer
    for tok in SPECIAL_TOKENS:
        answer = answer.replace(tok, "").strip()

    return {
        "thinking": thinking,
        "answer": answer,
        "n_new_tokens": int(new_tokens.shape[0]),
        "gen_seconds": round(dt, 2),
        "max_new_tokens_used": max_new_tokens,
        "hit_token_limit": int(new_tokens.shape[0]) >= max_new_tokens,
    }


# --- IO helpers ---------------------------------------------------------------

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


def load_vector(corpus, method, layer, kind="whitened"):
    name = "virtue_vector.npy" if kind == "whitened" else "virtue_vector_raw.npy"
    path = VECTOR_ROOT / corpus / method / f"layer_{layer}_{name}"
    meta_path = VECTOR_ROOT / corpus / method / f"layer_{layer}_metadata.json"
    v = np.load(path)
    meta = json.load(open(meta_path))
    return v, meta, str(path)


def generate_random_vector():
    """Generate a reproducible random unit vector at the same dimensionality."""
    rng = np.random.RandomState(RANDOM_SEED)
    v = rng.randn(HIDDEN_DIM).astype(np.float32)
    v = v / (np.linalg.norm(v) + 1e-10)
    save_path = OUT_ROOT / "random_vector_L22.npy"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(save_path, v)
    log(f"Generated random vector: dim={HIDDEN_DIM}, seed={RANDOM_SEED}")
    log(f"  Saved to {save_path}")
    return v


# --- Main run -----------------------------------------------------------------

def run_single(model, tokenizer, device, prompt_cfg, alpha, vector_id,
               vector_path, vector, layer, corpus=None, method=None):
    """Generate one steered (or baseline) response and write to disk."""
    pid = prompt_cfg["id"]
    max_tok = prompt_cfg.get("max_new_tokens", 4096)

    # Determine output path
    if alpha == 0.0:
        rpath = OUT_ROOT / "baselines" / f"{pid}.json"
    else:
        rpath = OUT_ROOT / vector_id / alpha_tag(alpha) / f"{pid}.json"

    # Skip if cached
    if rpath.exists():
        return "cached"

    t0 = time.time()
    try:
        if alpha == 0.0:
            r = generate(model, tokenizer, device, prompt_cfg["prompt"], max_tok)
        else:
            with AdditiveHook(model, layer, vector, alpha):
                r = generate(model, tokenizer, device, prompt_cfg["prompt"], max_tok)
    except Exception as e:
        log(f"      ERROR: {e}")
        log(traceback.format_exc())
        return "error"

    r.update({
        "prompt_id": pid,
        "prompt": prompt_cfg["prompt"],
        "alpha": alpha,
        "vector_id": vector_id if alpha != 0.0 else None,
        "vector_path": vector_path if alpha != 0.0 else None,
        "corpus": corpus,
        "method": method,
        "layer": layer if alpha != 0.0 else None,
        "category": prompt_cfg.get("category", ""),
        "timestamp": datetime.now().isoformat(),
    })

    # Write immediately
    write_json(rpath, r)

    # Append to summary
    append_summary({
        "kind": "baseline" if alpha == 0.0 else "steered",
        "vector_id": vector_id if alpha != 0.0 else None,
        "alpha": alpha,
        "prompt_id": pid,
        "n_tokens": r["n_new_tokens"],
        "seconds": r["gen_seconds"],
        "thinking_chars": len(r["thinking"]),
        "answer_chars": len(r["answer"]),
        "hit_limit": r["hit_token_limit"],
    })

    wall = time.time() - t0
    think_c = len(r["thinking"])
    ans_c = len(r["answer"])
    limit_flag = " [HIT LIMIT]" if r["hit_token_limit"] else ""
    log(f"      done {wall:.1f}s  think={think_c}c answer={ans_c}c "
        f"tok={r['n_new_tokens']}/{max_tok}{limit_flag}")
    return "generated"


def main():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    log("=" * 72)
    log("Qwen3-4B FOCUSED STEERING RUN (v2)")
    log("=" * 72)

    # Load prompts
    prompts = json.load(open(PROMPTS_PATH))
    log(f"Loaded {len(prompts)} prompts")
    for p in prompts:
        log(f"  {p['id']:30s}  max_tokens={p.get('max_new_tokens', 4096)}")

    # Load model
    log(f"Loading model {MODEL_NAME} ...")
    model, tokenizer, device = load_model(MODEL_NAME)
    log(f"Model on {device}. Ready.")

    # --- Baselines (alpha=0, no hook) ---
    log("")
    log("--- BASELINES (no steering) ---")
    for i, p in enumerate(prompts):
        log(f"  [{i+1}/{len(prompts)}] {p['id']}:")
        status = run_single(model, tokenizer, device, p,
                            alpha=0.0, vector_id=None, vector_path=None,
                            vector=None, layer=None)
        if status == "cached":
            log(f"      cached")

    # --- Load vectors ---
    all_runs = []  # list of (vector_id, layer, vector, alpha, corpus, method, vpath)

    for (vid, corpus, method, layer) in VECTORS:
        try:
            vec, vmeta, vpath = load_vector(corpus, method, layer)
        except FileNotFoundError as e:
            log(f"!! Vector not found for {vid}: {e}  (skipping)")
            continue
        probe = vmeta["whitened"]["probe_accuracy"]
        sep = vmeta["whitened"]["separation"]
        log(f"Loaded vector {vid}: probe={probe:.0%} sep={sep:+.2f}")
        for alpha in ALPHAS:
            all_runs.append((vid, layer, vec, alpha, corpus, method, vpath))

    # --- Random vector control ---
    random_vec = generate_random_vector()
    for alpha in ALPHAS:
        all_runs.append(("random_L22", RANDOM_LAYER, random_vec, alpha,
                         None, None, str(OUT_ROOT / "random_vector_L22.npy")))

    # --- Manifest ---
    manifest = {
        "model": MODEL_NAME,
        "started_at": datetime.now().isoformat(),
        "vectors": [v[0] for v in VECTORS] + ["random_L22"],
        "alphas": ALPHAS,
        "prompts": [p["id"] for p in prompts],
        "random_seed": RANDOM_SEED,
        "random_layer": RANDOM_LAYER,
    }
    write_json(OUT_ROOT / "manifest.json", manifest)

    total = len(all_runs) * len(prompts)
    done = 0
    gen_times = []
    run_start = time.time()

    log("")
    log(f"--- STEERED RUNS: {total} generations ---")
    log(f"  Vectors: {len(VECTORS)} virtue + 1 random")
    log(f"  Alphas: {ALPHAS}")
    log(f"  Prompts: {len(prompts)}")
    log("")

    current_vid = None
    for (vid, layer, vec, alpha, corpus, method, vpath) in all_runs:
        if vid != current_vid:
            log("=" * 60)
            log(f"VECTOR: {vid}  (layer {layer})")
            current_vid = vid

        tag = alpha_tag(alpha)
        log(f"  --- alpha={alpha:+.2f} ({tag}) ---")

        for i, p in enumerate(prompts):
            done += 1
            pid = p["id"]
            log(f"    [{done}/{total}] {pid}:")

            t0 = time.time()
            status = run_single(model, tokenizer, device, p,
                                alpha=alpha, vector_id=vid,
                                vector_path=vpath, vector=vec,
                                layer=layer, corpus=corpus, method=method)
            wall = time.time() - t0

            if status == "cached":
                log(f"      cached")
            elif status == "generated":
                gen_times.append(wall)

            # ETA based on running average of actual generation times
            if gen_times:
                avg = sum(gen_times) / len(gen_times)
                remaining = total - done
                eta_min = (avg * remaining) / 60
                log(f"      ETA: {eta_min:.0f} min "
                    f"(avg {avg:.0f}s/gen, {remaining} remaining)")

    elapsed = (time.time() - run_start) / 60
    log("=" * 72)
    log(f"FOCUSED RUN COMPLETE -- {done} generations in {elapsed:.1f} min")
    write_json(OUT_ROOT / "manifest.json",
               {**manifest, "finished_at": datetime.now().isoformat(),
                "total_generations": done, "elapsed_minutes": round(elapsed, 1)})


if __name__ == "__main__":
    main()
