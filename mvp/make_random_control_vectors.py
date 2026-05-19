"""Generate random unit-direction control vectors for the ablation battery.

These are the F121 hardening control per the ablation plan §8 (Risks):
ablating along a random direction (matched dimension, unit norm) should
NOT produce suppression. If random ablation ALSO suppresses, the effect
is non-specific (residual-stream-rank reduction, not feature-specific).

Outputs (overwritten on each run; deterministic via seed):
  qwen3-4b_L17_random_seed42.npy        shape (2560,) float32 unit-norm
  r1-distill_L31_random_seed42.npy      shape (4096,) float32 unit-norm

Run on VM:
  cd ~/phronesis_run/mvp && python3 make_random_control_vectors.py
"""
import argparse
from pathlib import Path

import numpy as np


SEED = 42
OUT_DIR = Path(__file__).parent / "results" / "sae_decoders"


def make_unit_random(rng: np.random.Generator, dim: int) -> np.ndarray:
    """Sample isotropic random unit vector via standard-normal then normalize."""
    v = rng.standard_normal(dim).astype(np.float32)
    v /= np.linalg.norm(v) + 1e-10
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    # qwen3-4b hidden_dim = 2560 (per MODEL_CONFIGS in utils.py)
    v_q3 = make_unit_random(rng, 2560)
    p_q3 = OUT_DIR / f"qwen3-4b_L17_random_seed{args.seed}.npy"
    np.save(p_q3, v_q3)
    print(f"wrote {p_q3}  shape={v_q3.shape}  dtype={v_q3.dtype}  norm={np.linalg.norm(v_q3):.6f}")

    # r1-distill-llama-8b hidden_dim = 4096 (Llama-3 architecture)
    v_r1 = make_unit_random(rng, 4096)
    p_r1 = OUT_DIR / f"r1-distill_L31_random_seed{args.seed}.npy"
    np.save(p_r1, v_r1)
    print(f"wrote {p_r1}  shape={v_r1.shape}  dtype={v_r1.dtype}  norm={np.linalg.norm(v_r1):.6f}")


if __name__ == "__main__":
    main()
