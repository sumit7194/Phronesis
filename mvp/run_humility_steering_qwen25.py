"""Steer qwen2.5-7b-it with the diff-of-means humility direction at L20.

Tests whether the F126 NLA-readable humility direction is operationally effective.

Cells (run sequentially):
  Cell 1: v_humility (diff-of-means) — sweep α ∈ {-8, -5, -3, -1, 0, +1, +3, +5, +8}
  Cell 2: random control vector at same norm — same α sweep

Prompts: E1 (baseline abstains — neg α should break it), E2 (baseline overcommits — pos α should improve),
         ip-longest, eg-v2-10 (additional context).

Outputs: 4 prompts × 9 alphas × 2 cells = 72 generations.
"""
import json, time, os
from pathlib import Path
import numpy as np
import pyarrow.parquet as pq
import torch

# Make local mvp importable
import sys
sys.path.insert(0, str(Path.home() / "phronesis_run" / "mvp"))

# Reuse the existing steer infrastructure
from steer import AdditiveSteeringHook, generate_response, MODEL_CONFIGS, load_model

EXP_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "nla_qwen25_L20_experiment"
OUT_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "nla_steering_test"
OUT_DIR.mkdir(parents=True, exist_ok=True)
EVAL_PROMPTS_JSON = Path.home() / "phronesis_run" / "corpus" / "eval-prompts" / "sae-battery-primary.json"

# alphas to sweep
ALPHAS = [-8.0, -5.0, -3.0, -1.0, 0.0, 1.0, 3.0, 5.0, 8.0]

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

def get_v_humility():
    """Read diff-of-means humility direction from F126's arithmetic parquet."""
    tbl = pq.read_table(EXP_DIR / "activations_arithmetic.parquet").to_pandas()
    diff_row = tbl[tbl["triplet_id"] == "diff_v-nv_GLOBAL_MEAN_60"]
    assert len(diff_row) == 1, f"expected exactly one row for diff_v-nv_GLOBAL_MEAN_60, got {len(diff_row)}"
    v = np.array(diff_row.iloc[0]["activation_vector"], dtype=np.float32)
    norm = float(np.linalg.norm(v))
    log(f"  v_humility shape={v.shape}, L2-norm={norm:.2f}")
    return v, norm

def make_random_vec(d, target_norm):
    """Random unit vector rescaled to match v_humility's norm."""
    torch.manual_seed(42)
    v = torch.randn(d).numpy().astype(np.float32)
    v = v * (target_norm / float(np.linalg.norm(v)))
    return v

def run_cell(model, tok, device, prompts, vec, label, layer=20):
    """Run an alpha sweep on a vector."""
    results = []
    for i, p in enumerate(prompts):
        pid = p["id"]
        prompt = p["prompt"]
        cap = p.get("max_new_tokens", 2048)
        log(f"\n  [{i+1}/{len(prompts)}] {pid} (cap={cap})")
        # Baseline (no steering)
        resp_base = generate_response(model, tok, prompt, device, cap)
        entry = {"prompt_id": pid, "prompt_text": prompt,
                 "expected_behavior": p.get("expected_behavior", ""),
                 "baseline": {"response": resp_base, "word_count": len(resp_base.split())},
                 "steered": {}}

        for alpha in ALPHAS:
            if alpha == 0.0:
                # α=0 = baseline. Skip to avoid duplicate work.
                entry["steered"][f"{alpha:.4f}"] = {"response": resp_base,
                                                    "word_count": len(resp_base.split()),
                                                    "note": "alpha=0 (no-op, baseline copy)"}
                continue
            log(f"    α={alpha:+.1f}...")
            hook = AdditiveSteeringHook(layer, vec, alpha)
            hook.attach(model)
            try:
                resp = generate_response(model, tok, prompt, device, cap)
            finally:
                hook.detach()
            entry["steered"][f"{alpha:.4f}"] = {"response": resp,
                                                 "word_count": len(resp.split())}
        results.append(entry)
    return results

def main():
    log("Loading qwen2.5-7b-it...")
    model, tok, device = load_model("qwen2.5-7b-it")

    log("Loading v_humility from F126 parquet...")
    v_hum, hum_norm = get_v_humility()
    v_rand = make_random_vec(v_hum.shape[0], hum_norm)
    log(f"  v_random shape={v_rand.shape}, L2-norm={float(np.linalg.norm(v_rand)):.2f} (matched)")

    prompts = json.load(open(EVAL_PROMPTS_JSON))
    log(f"Loaded {len(prompts)} eval prompts: {[p['id'] for p in prompts]}")

    # ─── Cell 1: v_humility ───
    log("\n" + "="*60)
    log("CELL 1 — v_humility (diff-of-means at qwen2.5-7b L20)")
    log("="*60)
    results_hum = run_cell(model, tok, device, prompts, v_hum, "v_humility")
    out1 = {
        "config": {"model": "qwen2.5-7b-it", "vector": "diff_v-nv_GLOBAL_MEAN_60",
                   "layer": 20, "alphas": ALPHAS, "norm": hum_norm,
                   "source": "F126 diff-of-means humility direction",
                   "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")},
        "results": results_hum,
    }
    (OUT_DIR / "qwen25_L20_vhumility_sweep.json").write_text(json.dumps(out1, indent=2, ensure_ascii=False))
    log(f"\nWrote {OUT_DIR / 'qwen25_L20_vhumility_sweep.json'}")

    # ─── Cell 2: random control ───
    log("\n" + "="*60)
    log("CELL 2 — random control vector (matched norm)")
    log("="*60)
    results_rand = run_cell(model, tok, device, prompts, v_rand, "v_random")
    out2 = {
        "config": {"model": "qwen2.5-7b-it", "vector": "random_seed42_matched_norm",
                   "layer": 20, "alphas": ALPHAS, "norm": hum_norm,
                   "source": "Phase8 control",
                   "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")},
        "results": results_rand,
    }
    (OUT_DIR / "qwen25_L20_vrandom_sweep.json").write_text(json.dumps(out2, indent=2, ensure_ascii=False))
    log(f"\nWrote {OUT_DIR / 'qwen25_L20_vrandom_sweep.json'}")

    log("\nALL DONE.")

if __name__ == "__main__":
    main()
