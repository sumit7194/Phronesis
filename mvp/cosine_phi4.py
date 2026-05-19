"""
Cosine-similarity matrix across phi-4-mini-reasoning extracted vectors.
Adapted from cosine_phi.py — points to the phi-4 vector directory.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from datetime import datetime

import numpy as np


VECTOR_ROOT = Path(__file__).parent / "results" / "vectors" / "phi-4-mini-reasoning"

VIRTUE_DIRS = {
    "EG":         "triplets-evidence-grounding",
    "RT":         "triplets-reasoning-transparency",
    "CC_combined": "triplets-combined",
    "CC_numeric": "triplets-cc-numeric-only-symlinks",
    "IH":         "triplets-intellectual-humility",
    "VC":         "triplets-verbosity-control",
}


def load_all_vectors() -> dict:
    out = {}
    for label, subdir in VIRTUE_DIRS.items():
        d = VECTOR_ROOT / subdir / "last_token"
        if not d.is_dir():
            print(f"  [WARN] Not found: {d}")
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
            print(f"  Loaded {label}: {len(layer_vecs)} layers, shape {list(layer_vecs.values())[0].shape}")
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
        "model": "phi-4-mini-reasoning",
        "num_layers": len(all_layers),
        "labels": labels,
        "layers": all_layers,
        "pairwise_cosine_per_layer": pairs,
        "norms_per_layer": norms,
        "adjacent_layer_stability": stab,
        "generated": datetime.utcnow().isoformat() + "Z",
    }


def probe_accuracies(vecs: dict) -> dict:
    """Load probe accuracy metadata from companion files if available."""
    acc = {}
    for label, subdir in VIRTUE_DIRS.items():
        d = VECTOR_ROOT / subdir / "last_token"
        # Look for probe_accuracy.json or similar
        for probe_file in ["probe_accuracy.json", "probing_results.json", "metadata.json"]:
            p = d / probe_file
            if p.exists():
                with open(p) as f:
                    acc[label] = json.load(f)
                break
    return acc


def summary_print(m: dict):
    print(f"\n=== Phi-4-mini-reasoning cosine summary ===")
    print(f"Labels: {m['labels']}")
    print(f"Layers covered: {len(m['layers'])} (0..{m['layers'][-1] if m['layers'] else '-'})")
    print()

    # Key layers: early (L6-8), mid (L14-22), late (L26-30)
    sample = [L for L in [4, 8, 10, 14, 16, 18, 20, 21, 22, 24, 28, 30] if L in m["pairwise_cosine_per_layer"]]
    for L in sample:
        print(f"--- Layer {L} ---")
        row = m["pairwise_cosine_per_layer"][L]
        for k, v in sorted(row.items(), key=lambda kv: -abs(kv[1])):
            print(f"  {k:45s} cos={v:+.3f}")
        print()

    # Max cosine across all layers per pair
    print("=== Peak cosine per pair (across all layers) ===")
    all_pairs = set()
    for layer_row in m["pairwise_cosine_per_layer"].values():
        all_pairs.update(layer_row.keys())
    for pair in sorted(all_pairs):
        vals = [m["pairwise_cosine_per_layer"][L].get(pair, float("nan"))
                for L in m["layers"]]
        vals = [v for v in vals if not (v != v)]  # remove NaN
        if vals:
            print(f"  {pair:45s} max={max(vals):+.3f}  mean={sum(vals)/len(vals):+.3f}")

    # Norm profile — show peak norm layer per virtue
    print("\n=== Peak L2 norm layer per virtue ===")
    for lab, norms in m["norms_per_layer"].items():
        peak_l = max(norms, key=lambda L: norms[L])
        print(f"  {lab:15s} peak_norm={norms[peak_l]:.2f} at L{peak_l}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="results/phi4_cosine_matrix.json")
    args = ap.parse_args()

    print(f"Loading vectors from: {VECTOR_ROOT}")
    vecs = load_all_vectors()
    if not vecs:
        print(f"No vectors found under {VECTOR_ROOT}")
        return

    m = build_matrix(vecs)
    out_path = Path(__file__).parent / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(m, f, indent=2)
    print(f"\nSaved cosine matrix to {out_path}")

    summary_print(m)


if __name__ == "__main__":
    main()
