"""Phase 6 — random-vector negative control for F124.

Generate 20 random unit vectors at d_model=3584, write to parquet so they can be
fed through the same AV inference path as real activations. Tests: does AV
produce humility/commit-correlated vocab on pure random vectors, or only on
real model activations?
"""
import time
from pathlib import Path
import torch
import pyarrow as pa, pyarrow.parquet as pq

D = 3584
N = 20
OUT = Path.home() / "phronesis_run" / "mvp" / "results" / "nla_qwen25_L20_experiment" / "activations_random_control.parquet"

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

def main():
    torch.manual_seed(42)
    log(f"Generating {N} random unit vectors at d={D}...")
    # Activation distribution from Qwen residuals is roughly N(0, ~200 norm).
    # We sample standard normal and let injection_scale=150.0 do the rescale at
    # inject time (same path as real activations).
    rows = []
    for i in range(N):
        v = torch.randn(D)
        rows.append({
            "triplet_id": f"random_seed42_idx{i:02d}",
            "version": "random",
            "virtue": "random-control",
            "source": "Phase6_random_control",
            "n_tokens": 0,  # not applicable but keep schema consistent
            "activation_vector": v.float().tolist(),
        })

    pq.write_table(pa.table({k: [r[k] for r in rows] for k in rows[0].keys()}), OUT)
    log(f"Wrote {OUT} ({N} random vectors)")

if __name__ == "__main__":
    main()
