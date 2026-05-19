"""Phase 3 — Extreme-α v_humility on E2.

F129 tested α ∈ {±8} at most. Push further (±15, ±25, ±50) on E2 specifically to see
if higher magnitudes break the model out of its "high confidence flossing" baseline.

If even α=±50 doesn't move it, F121 is super-robust at qwen2.5-7b L20.
If high-α produces structural collapse (FM-structural-collapse style) → useful F-eligible nuance.
If positive-α=+30 or so suddenly produces clean contested-evidence acknowledgment → that
would be the smoking gun for "right operation, wrong magnitude" — major finding.
"""
import json, time
from pathlib import Path
import numpy as np
import pyarrow.parquet as pq
import sys
sys.path.insert(0, str(Path.home() / "phronesis_run" / "mvp"))
from steer import AdditiveSteeringHook, generate_response, load_model

EXP_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "nla_qwen25_L20_experiment"
OUT_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "nla_phase3_extreme_alpha"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXTREME_ALPHAS = [-50.0, -25.0, -15.0, +15.0, +25.0, +50.0]

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

def main():
    log("Loading qwen2.5-7b-it...")
    model, tok, device = load_model("qwen2.5-7b-it")

    # Load v_humility
    arith = pq.read_table(EXP_DIR / "activations_arithmetic.parquet").to_pandas()
    v_hum = np.array(arith[arith["triplet_id"] == "diff_v-nv_GLOBAL_MEAN_60"].iloc[0]["activation_vector"], dtype=np.float32)
    log(f"  v_humility shape={v_hum.shape}, L2-norm={np.linalg.norm(v_hum):.2f}")

    # E2 prompt
    e2 = json.load(open(Path.home() / "phronesis_run" / "corpus" / "eval-prompts" / "sae-battery-primary.json"))
    e2_p = [p for p in e2 if p["id"] == "E2-contested-science"][0]
    cap = e2_p.get("max_new_tokens", 2048)

    log(f"\nE2 prompt: {e2_p['prompt'][:80]}...")
    log(f"  cap: {cap}")

    # Baseline
    log("\nGenerating baseline (no steering)...")
    base = generate_response(model, tok, e2_p["prompt"], device, cap)
    log(f"  baseline ({len(base)} chars): {base[-200:]!r}")

    # Sweep extreme alphas
    results = {"prompt_id": "E2-contested-science", "prompt": e2_p["prompt"],
               "baseline": {"response": base, "word_count": len(base.split())},
               "steered": {}}
    for alpha in EXTREME_ALPHAS:
        log(f"\n  α={alpha:+.1f}...")
        hook = AdditiveSteeringHook(20, v_hum, alpha)
        hook.attach(model)
        try:
            resp = generate_response(model, tok, e2_p["prompt"], device, cap)
        finally:
            hook.detach()
        results["steered"][f"{alpha:.4f}"] = {"response": resp, "word_count": len(resp.split())}
        log(f"    {len(resp)} chars: {resp[-300:]!r}")

    out_file = OUT_DIR / "qwen25_L20_vhumility_extreme_alpha_E2.json"
    json.dump({"config": {"model": "qwen2.5-7b-it", "vector": "diff_v-nv_GLOBAL_MEAN_60",
                          "layer": 20, "alphas": EXTREME_ALPHAS, "norm": float(np.linalg.norm(v_hum)),
                          "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")},
               "results": [results]}, open(out_file, "w"), indent=2, ensure_ascii=False)
    log(f"\nWrote {out_file}")
    log("PHASE 3 COMPLETE")

if __name__ == "__main__":
    main()
