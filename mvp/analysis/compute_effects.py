"""
Compute per-cell effects for the specificity matrix.

Given a DataFrame of generations (one row per model × vector × eval × prompt),
returns:
  - per-cell mean score + bootstrap 95% CI
  - baseline-vs-steered delta for every (model, vector, eval) cell
  - pre-registered PASS/FLAG/FAIL verdicts per cell

Bootstrap CIs are computed by prompt-level resampling (non-parametric), which is
the conservative choice when effect size varies across prompts (per
docs/eg-rt-eval-spec.md §5.4).

Public API:
  compute_cell_stats(df, config) -> DataFrame of per-cell summaries
  compute_deltas(cell_stats, config) -> DataFrame of baseline-vs-steered deltas
  classify_specificity_matrix(deltas, config) -> dict with verdict per cell + overall
"""
from __future__ import annotations
from typing import Optional

import numpy as np
import pandas as pd


def _bootstrap_ci(
    values: np.ndarray,
    n_resamples: int = 2000,
    seed: int = 42,
    alpha: float = 0.05,
) -> tuple[float, float, float]:
    """Return (point_estimate, ci_low, ci_high) for the mean of `values`.

    Non-parametric bootstrap via prompt-level resampling. If n < 2, CI is (mean, mean).
    """
    arr = np.asarray(values, dtype=float)
    arr = arr[~np.isnan(arr)]
    n = len(arr)
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    if n < 2:
        return (float(arr[0]), float(arr[0]), float(arr[0]))

    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_resamples, n))
    resampled_means = arr[idx].mean(axis=1)
    lo = float(np.percentile(resampled_means, 100 * alpha / 2))
    hi = float(np.percentile(resampled_means, 100 * (1 - alpha / 2)))
    return (float(arr.mean()), lo, hi)


def compute_cell_stats(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Aggregate each (model, vector, eval) cell by target scorer.

    Also computes each virtue's scorer on each cell (for off-diagonal).

    Returns DataFrame with columns:
        model, vector, eval, target_virtue, scorer_column,
        n, mean, ci_low, ci_high,
        cc_mean, ih_mean, eg_mean, rt_mean  (4 virtue scorers' means for this cell)
    """
    if df.empty:
        return pd.DataFrame()

    bs_n = config["behavioral"].get("bootstrap_resamples", 2000)
    bs_seed = config["behavioral"].get("bootstrap_seed", 42)

    # Virtue name → scorer column in CSV
    virtue_to_scorer_col = {
        "CC": "cc_hedging_score",
        "IH": "ih_abstention_score",
        "EG": "eg_score",
        "RT": "rt_score",
    }
    # eval → target virtue (from config)
    eval_to_target = {ev["name"]: ev["target_virtue"] for ev in config["evals"]}

    rows = []
    grouped = df.groupby(["model", "vector", "eval"], sort=False)
    for (model, vector, eval_name), group in grouped:
        target_virtue = eval_to_target.get(eval_name)
        target_col = virtue_to_scorer_col.get(target_virtue, f"{target_virtue.lower()}_score")

        if target_col not in group.columns:
            # Skip cells where the target scorer column is missing
            continue

        target_vals = group[target_col].to_numpy()
        mean_, lo, hi = _bootstrap_ci(target_vals, n_resamples=bs_n, seed=bs_seed)

        # Compute each virtue's scorer mean on this cell (for off-diagonal cross-check)
        all_virtue_means = {}
        for v_name, v_col in virtue_to_scorer_col.items():
            if v_col in group.columns:
                vals = group[v_col].to_numpy()
                vals = vals[~np.isnan(vals)]
                all_virtue_means[f"{v_name.lower()}_mean"] = float(vals.mean()) if len(vals) else float("nan")
            else:
                all_virtue_means[f"{v_name.lower()}_mean"] = float("nan")

        rows.append({
            "model": model,
            "vector": vector,
            "eval": eval_name,
            "target_virtue": target_virtue,
            "scorer_column": target_col,
            "n": len(target_vals),
            "mean": mean_,
            "ci_low": lo,
            "ci_high": hi,
            **all_virtue_means,
        })

    return pd.DataFrame(rows)


def compute_deltas(cell_stats: pd.DataFrame, config: dict) -> pd.DataFrame:
    """For every (model, vector!='baseline', eval) cell, compute delta vs baseline
    in the target-virtue scorer.

    Returns DataFrame with columns:
        model, vector, eval, target_virtue,
        baseline_mean, steered_mean, delta, delta_ci_low, delta_ci_high,
        is_diagonal (bool)
    """
    if cell_stats.empty:
        return pd.DataFrame()

    # Pull baseline rows per (model, eval) for quick lookup
    baseline_idx = cell_stats[cell_stats["vector"] == "baseline"].set_index(["model", "eval"])

    # Vector ↔ virtue mapping (derived from vector name like "EG_L20" → "EG")
    def vector_to_virtue(v: str) -> Optional[str]:
        # Map common vector name prefixes to virtues
        # Vector registry names: L*, CC_L*, IH_L*, EG_L*, RT_L*
        if v.startswith(("EG_", "eg_")):
            return "EG"
        if v.startswith(("RT_", "rt_")):
            return "RT"
        if v.startswith(("IH_", "ih_")):
            return "IH"
        if v.startswith(("CC_", "cc_")) or v.startswith("L"):
            return "CC"
        return None

    rows = []
    steered = cell_stats[cell_stats["vector"] != "baseline"]
    for _, r in steered.iterrows():
        key = (r["model"], r["eval"])
        if key not in baseline_idx.index:
            continue
        b = baseline_idx.loc[key]
        # If multiple baseline rows exist (shouldn't), take first
        if isinstance(b, pd.DataFrame):
            b = b.iloc[0]

        delta = r["mean"] - b["mean"]
        # Simple CI for delta: combine via linear propagation
        # (conservative: use steered_ci widths; baseline is usually 1 sample-group)
        delta_ci_low = r["ci_low"] - b["mean"]
        delta_ci_high = r["ci_high"] - b["mean"]

        steered_virtue = vector_to_virtue(r["vector"])
        is_diagonal = (steered_virtue == r["target_virtue"])

        rows.append({
            "model": r["model"],
            "vector": r["vector"],
            "steered_virtue": steered_virtue,
            "eval": r["eval"],
            "target_virtue": r["target_virtue"],
            "baseline_mean": b["mean"],
            "steered_mean": r["mean"],
            "delta": delta,
            "delta_ci_low": delta_ci_low,
            "delta_ci_high": delta_ci_high,
            "is_diagonal": is_diagonal,
            "n": r["n"],
        })

    return pd.DataFrame(rows)


def classify_specificity_matrix(deltas: pd.DataFrame, config: dict) -> dict:
    """Apply pre-registered exit criteria from F98 / eg-rt-eval-spec.md §5.7.

    For each (model, diagonal_cell) determines:
      - "diagonal_win" if delta ≥ diagonal_min_delta AND delta ≥ off_diag_max × diagonal_ratio_vs_off
      - "flag" otherwise

    For each (model, off_diag_cell):
      - "off_diag_failure" if delta ≥ off_diag_failure_delta

    Overall verdict per model:
      - "all_clean": 4/4 diagonal wins, ≤ exit_criteria.all_clean.off_diag_failures_max failures
      - "partial": ≥ exit_criteria.partial.diagonal_wins_min diagonal wins, ≤ failures
      - "collapse": anything worse
    """
    if deltas.empty:
        return {"verdict": "no_data", "per_model": {}, "cells": []}

    thr = config["behavioral"]
    exit_c = config["exit_criteria"]

    per_cell = []
    for _, row in deltas.iterrows():
        cell = dict(row)
        if row["is_diagonal"]:
            # Need max off-diagonal in same ROW (same vector, other evals) to judge
            off_diag_same_row = deltas[
                (deltas["model"] == row["model"]) &
                (deltas["vector"] == row["vector"]) &
                (deltas["is_diagonal"] == False)
            ]
            max_off = off_diag_same_row["delta"].max() if not off_diag_same_row.empty else 0.0
            cell["max_off_diag_delta"] = float(max_off)

            pass_min = row["delta"] >= thr["diagonal_min_delta"]
            pass_ratio = row["delta"] >= thr["diagonal_ratio_vs_off"] * max(max_off, 1e-6) if max_off > 0 else pass_min
            cell["verdict"] = "win" if (pass_min and pass_ratio) else "flag"
        else:
            # Off-diagonal: failure if delta exceeds threshold
            cell["verdict"] = "fail" if row["delta"] >= thr["off_diag_failure_delta"] else "ok"
        per_cell.append(cell)

    # Per-model summaries
    per_model = {}
    for model in deltas["model"].unique():
        m_cells = [c for c in per_cell if c["model"] == model]
        diag_wins = sum(1 for c in m_cells if c["is_diagonal"] and c["verdict"] == "win")
        off_diag_fails = sum(1 for c in m_cells if not c["is_diagonal"] and c["verdict"] == "fail")

        # Classify per exit criteria
        if diag_wins >= exit_c["all_clean"]["diagonal_wins_min"] and off_diag_fails <= exit_c["all_clean"]["off_diag_failures_max"]:
            verdict = "all_clean"
        elif diag_wins >= exit_c["partial"]["diagonal_wins_min"] and off_diag_fails <= exit_c["partial"]["off_diag_failures_max"]:
            verdict = "partial"
        else:
            verdict = "collapse"

        per_model[model] = {
            "diagonal_wins": diag_wins,
            "off_diag_failures": off_diag_fails,
            "verdict": verdict,
        }

    # Overall: worst of per-model
    verdicts_order = ["all_clean", "partial", "collapse"]
    overall = "all_clean"
    for m_result in per_model.values():
        if verdicts_order.index(m_result["verdict"]) > verdicts_order.index(overall):
            overall = m_result["verdict"]

    return {
        "verdict": overall,
        "per_model": per_model,
        "cells": per_cell,
    }


if __name__ == "__main__":
    # Smoke test with toy data
    from load_matrix import load_config

    cfg = load_config(__file__.replace("compute_effects.py", "config.yaml"))

    # Toy specificity data: 3 prompts per cell, one model, 4 vectors, 4 evals
    # Diagonal cells get high target-virtue scores; off-diag near baseline
    rows = []
    virtues = ["CC", "IH", "EG", "RT"]
    evals = ["aime-42", "abstention", "eg-eval", "rt-eval"]
    # Include baseline
    import random
    random.seed(0)
    for vector in ["baseline", "CC_L20", "IH_L20", "EG_L20", "RT_L20"]:
        for eval_name in evals:
            for i in range(3):
                base_scores = {
                    "cc_hedging_score": random.uniform(0, 2),
                    "ih_abstention_score": random.uniform(0, 2),
                    "eg_score": random.uniform(0, 3),
                    "rt_score": random.uniform(0, 3),
                }
                if vector != "baseline":
                    # Diagonal boost
                    v_map = {"CC_L20": "cc_hedging_score", "IH_L20": "ih_abstention_score",
                             "EG_L20": "eg_score", "RT_L20": "rt_score"}
                    eval_target = {"aime-42": "cc_hedging_score", "abstention": "ih_abstention_score",
                                   "eg-eval": "eg_score", "rt-eval": "rt_score"}
                    if v_map[vector] == eval_target[eval_name]:
                        base_scores[v_map[vector]] += 8 + random.uniform(-1, 1)
                rows.append({
                    "model": "qwen3-4b",
                    "vector": vector,
                    "alpha": 0 if vector == "baseline" else 12,
                    "eval": eval_name,
                    "item_id": f"p{i}",
                    "tokens": 200,
                    **base_scores,
                })
    df = pd.DataFrame(rows)
    print(f"Toy df: {len(df)} rows")

    cs = compute_cell_stats(df, cfg)
    print(f"\nCell stats: {len(cs)} rows")
    print(cs[["vector", "eval", "target_virtue", "mean", "ci_low", "ci_high"]].head(10).to_string(index=False))

    dd = compute_deltas(cs, cfg)
    print(f"\nDeltas: {len(dd)} rows")
    print(dd[["vector", "eval", "delta", "is_diagonal"]].to_string(index=False))

    cls = classify_specificity_matrix(dd, cfg)
    print(f"\nOverall verdict: {cls['verdict']}")
    for m, r in cls["per_model"].items():
        print(f"  {m}: {r}")
