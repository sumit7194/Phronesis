"""
Compute geometric MVE matrix across N virtues for a given model.

For each pair (v_i, v_j) in the N virtues, computes:
  - cosine similarity across all layers
  - orthogonal-projection retention: |v_i - proj_{v_j}(v_i)| / |v_i|

Applies per-pair pass/fail thresholds from config and aggregates into a verdict
per the F98 pre-registration ("all_clean", "partial", "collapse").

Public API:
  load_vectors_for_model(model, config) -> dict[virtue_name, dict[layer, ndarray]]
  compute_mve_matrix(model_vectors, config) -> DataFrame of per-pair-per-layer stats
  compute_mve_summary(mve_df, config) -> dict with per-pair mean + pass/fail
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


# Default mapping of virtue name → (corpus-subdirectory, method-subdirectory) in vectors/
# This mirrors how extract_v2.py saves: vectors/{model}/{corpus}/{method}/layer_X_virtue_vector.npy
DEFAULT_VIRTUE_PATHS = {
    "CC": {
        "qwen3-4b": [("triplets", "last_token")],            # empirically-validated 50-hand corpus
        "gemma-4-E4B-it": [("triplets-combined", "last_token")],  # 166 triplets
    },
    "IH": {
        "qwen3-4b": [("triplets-intellectual-humility", "last_token")],
        "gemma-4-E4B-it": [("triplets-intellectual-humility", "last_token")],
    },
    "EG": {
        "qwen3-4b": [("triplets-evidence-grounding", "generation")],  # mvp-combined corpus
        "gemma-4-E4B-it": [("triplets-evidence-grounding", "generation")],
    },
    "RT": {
        "qwen3-4b": [("triplets-reasoning-transparency", "generation")],
        "gemma-4-E4B-it": [("triplets-reasoning-transparency", "generation")],
    },
}


def load_vectors_for_model(
    model: str,
    config: dict,
    vectors_root: Optional[Path] = None,
    paths_override: Optional[dict] = None,
) -> dict:
    """Load all virtue layer-vectors for a model.

    Returns dict: {virtue_name: {layer_idx: ndarray}}
    Skips missing files silently (logs info).
    """
    if vectors_root is None:
        vectors_root = Path(__file__).parent.parent / config["paths"]["vectors_dir"]

    paths = paths_override or DEFAULT_VIRTUE_PATHS

    out = {}
    for virtue in config["virtues"]:
        v_name = virtue["name"]
        if v_name not in paths or model not in paths[v_name]:
            continue
        vectors_by_layer = {}
        for corpus_subdir, method_subdir in paths[v_name][model]:
            d = vectors_root / model / corpus_subdir / method_subdir
            if not d.exists():
                continue
            for f in d.glob("layer_*_virtue_vector.npy"):
                if "_raw" in f.stem:
                    continue
                try:
                    layer_idx = int(f.stem.split("_")[1])
                except (IndexError, ValueError):
                    continue
                vectors_by_layer[layer_idx] = np.load(f)
        out[v_name] = vectors_by_layer
    return out


def cos_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def orthogonalise(v: np.ndarray, along: np.ndarray) -> np.ndarray:
    along_hat = along / (np.linalg.norm(along) + 1e-12)
    return v - np.dot(v, along_hat) * along_hat


def compute_mve_matrix(model_vectors: dict, config: dict) -> pd.DataFrame:
    """For each pair of virtues × each common layer, compute cos + retention.

    Returns DataFrame with columns:
        virtue_a, virtue_b, layer, cos, abs_cos, retention_a_orth_b
    """
    rows = []
    virtues_present = [v["name"] for v in config["virtues"] if v["name"] in model_vectors and model_vectors[v["name"]]]

    for i, va in enumerate(virtues_present):
        for vb in virtues_present[i+1:]:
            layers_a = set(model_vectors[va].keys())
            layers_b = set(model_vectors[vb].keys())
            common = sorted(layers_a & layers_b)
            for L in common:
                a = model_vectors[va][L]
                b = model_vectors[vb][L]
                if a.shape != b.shape:
                    continue
                c = cos_sim(a, b)
                v_orth = orthogonalise(a, b)
                ret = float(np.linalg.norm(v_orth) / (np.linalg.norm(a) + 1e-12))
                rows.append({
                    "virtue_a": va,
                    "virtue_b": vb,
                    "layer": L,
                    "cos": c,
                    "abs_cos": abs(c),
                    "retention_a_orth_b": ret,
                    "norm_a": float(np.linalg.norm(a)),
                    "norm_b": float(np.linalg.norm(b)),
                })

    return pd.DataFrame(rows)


def compute_mve_summary(mve_df: pd.DataFrame, config: dict) -> dict:
    """Aggregate per-pair mean |cos| + retention, apply pass/fail thresholds.

    Returns:
        {
          "pairs": [ {virtue_a, virtue_b, mean_abs_cos, mean_retention, verdict, n_layers} ],
          "n_pairs": N,
          "n_pass": K,
          "n_partial": M,
          "n_collapse": P,
          "overall_verdict": "all_clean" | "partial" | "collapse"
        }
    """
    if mve_df.empty:
        return {"pairs": [], "n_pairs": 0, "n_pass": 0, "n_partial": 0, "n_collapse": 0,
                "overall_verdict": "no_data"}

    cos_clean = config["mve"]["cos_clean_threshold"]
    cos_partial = config["mve"]["cos_partial_threshold"]
    ret_thresh = config["mve"]["retention_pass_threshold"]

    pair_rows = []
    for (va, vb), g in mve_df.groupby(["virtue_a", "virtue_b"], sort=False):
        mean_abs_cos = float(g["abs_cos"].mean())
        max_abs_cos = float(g["abs_cos"].max())
        mean_ret = float(g["retention_a_orth_b"].mean())
        min_ret = float(g["retention_a_orth_b"].min())

        if mean_abs_cos < cos_clean and mean_ret > ret_thresh:
            verdict = "pass"
        elif mean_abs_cos < cos_partial:
            verdict = "partial"
        else:
            verdict = "collapse"

        pair_rows.append({
            "virtue_a": va,
            "virtue_b": vb,
            "mean_abs_cos": mean_abs_cos,
            "max_abs_cos": max_abs_cos,
            "mean_retention": mean_ret,
            "min_retention": min_ret,
            "n_layers": len(g),
            "verdict": verdict,
        })

    n_pairs = len(pair_rows)
    n_pass = sum(1 for r in pair_rows if r["verdict"] == "pass")
    n_partial = sum(1 for r in pair_rows if r["verdict"] == "partial")
    n_collapse = sum(1 for r in pair_rows if r["verdict"] == "collapse")

    # Expected number of pairs: 4C2 = 6 for 4 virtues, generalises to N*(N-1)/2
    n_virtues = len(config["virtues"])
    expected_pairs = n_virtues * (n_virtues - 1) // 2

    # Overall verdict using exit criteria, but only if we have enough pairs to judge
    exit_c = config["exit_criteria"]
    if n_pairs < exit_c["partial"]["mve_pairs_pass"]:
        # Not enough data to declare any verdict beyond "insufficient"
        overall = "insufficient_data"
    elif n_pass >= exit_c["all_clean"]["mve_pairs_pass"]:
        overall = "all_clean"
    elif n_pass >= exit_c["partial"]["mve_pairs_pass"]:
        overall = "partial"
    else:
        overall = "collapse"

    return {
        "pairs": pair_rows,
        "n_pairs": n_pairs,
        "expected_pairs": expected_pairs,
        "n_pass": n_pass,
        "n_partial": n_partial,
        "n_collapse": n_collapse,
        "overall_verdict": overall,
    }


if __name__ == "__main__":
    # Smoke test with toy vectors
    from load_matrix import load_config

    cfg = load_config(__file__.replace("compute_mve.py", "config.yaml"))

    # Synthetic: 4 virtues × 5 layers, in 128-dim space, near-orthogonal
    rng = np.random.default_rng(0)
    synthetic = {}
    base_dirs = rng.standard_normal((4, 128))
    base_dirs /= np.linalg.norm(base_dirs, axis=1, keepdims=True)
    for i, v in enumerate(["CC", "IH", "EG", "RT"]):
        vecs = {}
        for L in range(5):
            # small noise per layer
            noise = rng.standard_normal(128) * 0.02
            vecs[L] = (base_dirs[i] + noise) * (2 + L)
        synthetic[v] = vecs

    df = compute_mve_matrix(synthetic, cfg)
    print(f"Synthetic MVE df: {len(df)} rows")
    print(df.to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    summary = compute_mve_summary(df, cfg)
    print(f"\nOverall: {summary['overall_verdict']}  ({summary['n_pass']}/{summary['n_pairs']} pass)")
    for pr in summary["pairs"]:
        print(f"  {pr['virtue_a']} ⊥ {pr['virtue_b']}: mean|cos|={pr['mean_abs_cos']:.4f}  "
              f"retention={pr['mean_retention']*100:.1f}%  [{pr['verdict']}]")
