"""
Cosine-similarity matrix across phi-3.5-mini-it extracted vectors.

Mirrors cosine_v2_analysis.py but for phi (single corpus generation; no v1
backup to compare against). Computes:

  - Pairwise cosine between virtue vectors at each layer (32 layers).
  - Vector L2 norms per virtue per layer.
  - Per-virtue self-cosine across adjacent layers (stability).

Outputs JSON for inspection. The headline question: does phi exhibit the
qwen3-4b cluster pattern (1 distinct + 3 clustered + 1 partial sub-carve-out)
or the gemma-clean pattern (all virtues orthogonal at probe-accuracy ≥85%)?

Usage on VM:
    python3 cosine_phi.py --output results/phi_cosine_matrix.json
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from datetime import datetime

import numpy as np


VECTOR_ROOT = Path(__file__).parent / "results" / "vectors" / "phi-3.5-mini-it"

VIRTUE_DIRS = {
    "EG":         "triplets-evidence-grounding",
    "RT":         "triplets-reasoning-transparency",
    "CC_full":    "triplets-combined",
    "CC_legacy":  "triplets",
    "CC_numeric": "triplets-cc-numeric-only-symlinks",
    "IH":         "triplets-intellectual-humility",
    "VC":         "triplets-verbosity-control",
}


def load_all_vectors() -> dict:
    out = {}
    for label, subdir in VIRTUE_DIRS.items():
        d = VECTOR_ROOT / subdir / "last_token"
        if not d.is_dir():
            continue
        layer_vecs = {}
        for npy in sorted(d.glob("layer_*_virtue_vector.npy")):
            try:
                layer = int(npy.stem.split("_")[1])
            except ValueError:
                continue
            v = np.load(npy)
            layer_vecs[layer] = v
        if layer_vecs:
            out[label] = layer_vecs
    return out


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    if a.shape != b.shape:
        return float("nan")
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0 or nb == 0:
        return float("nan")
    return float(np.dot(a, b) / (na * nb))


def build_matrix(vecs: dict) -> dict:
    labels = sorted(vecs.keys())
    all_layers = sorted({L for d in vecs.values() for L in d.keys()})

    pairs = {}
    for layer in all_layers:
        present = [lab for lab in labels if layer in vecs[lab]]
        row = {}
        for i, a in enumerate(present):
            for b in present[i + 1:]:
                row[f"{a}__vs__{b}"] = cosine(vecs[a][layer], vecs[b][layer])
        pairs[layer] = row

    norms = {lab: {L: float(np.linalg.norm(v)) for L, v in vecs[lab].items()} for lab in labels}

    # Per-virtue adjacent-layer stability
    stab = {}
    for lab in labels:
        ds = vecs[lab]
        sl = sorted(ds.keys())
        per = {}
        for i in range(len(sl) - 1):
            L0, L1 = sl[i], sl[i + 1]
            per[f"{L0}__vs__{L1}"] = cosine(ds[L0], ds[L1])
        stab[lab] = per

    return {
        "model": "phi-3.5-mini-it",
        "num_layers": len(all_layers),
        "labels": labels,
        "layers": all_layers,
        "pairwise_cosine_per_layer": pairs,
        "norms_per_layer": norms,
        "adjacent_layer_stability": stab,
        "generated": datetime.utcnow().isoformat() + "Z",
    }


def summary_print(m: dict):
    print("\n=== Phi-3.5-mini cosine summary ===")
    print(f"Labels: {m['labels']}")
    print(f"Layers covered: {len(m['layers'])} (0..{m['layers'][-1] if m['layers'] else '-'})")
    print()
    # Pick a few representative layers near AP-peak fractional positions from qwen
    # qwen used L7,L9,L15,L17 / 36 layers => fractions 19%,25%,42%,47%
    # phi has 32 layers => probable equivalent L6,L8,L13,L15
    sample = [L for L in [6, 8, 10, 13, 15, 17, 20, 25] if L in m["pairwise_cosine_per_layer"]]
    for L in sample:
        print(f"--- Layer {L} ---")
        row = m["pairwise_cosine_per_layer"][L]
        for k, v in sorted(row.items(), key=lambda kv: -abs(kv[1])):
            print(f"  {k:40s} cos={v:+.3f}")
        print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="results/phi_cosine_matrix.json")
    args = ap.parse_args()

    vecs = load_all_vectors()
    if not vecs:
        print(f"No vectors found under {VECTOR_ROOT}")
        return

    m = build_matrix(vecs)
    out_path = Path(__file__).parent / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(m, f, indent=2)
    print(f"Saved cosine matrix to {out_path}")

    summary_print(m)


if __name__ == "__main__":
    main()
