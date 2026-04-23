"""
Entry point for the specificity matrix analysis pipeline.

Reads specificity_matrix CSV + extracted vectors, produces a markdown
report with embedded PNG figures under mvp/results/analysis_report/.

Usage:
    python run_analysis.py                           # uses default config
    python run_analysis.py --config my_config.yaml
    python run_analysis.py --model qwen3-4b          # only one model
    python run_analysis.py --mve-only                # skip specificity (useful during extraction)
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

# Allow running from mvp/analysis/ or elsewhere
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import pandas as pd  # noqa: E402

from load_matrix import load_config, load_specificity_csvs  # noqa: E402
from compute_effects import compute_cell_stats, compute_deltas, classify_specificity_matrix  # noqa: E402
from compute_mve import load_vectors_for_model, compute_mve_matrix, compute_mve_summary  # noqa: E402
from figures import render_all  # noqa: E402
from report import render_report  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(HERE / "config.yaml"), help="path to config.yaml")
    ap.add_argument("--model", default=None,
                    help="optional: only compute for this model (default: all in config)")
    ap.add_argument("--mve-only", action="store_true",
                    help="only compute MVE (skip specificity — useful while extraction is still running)")
    ap.add_argument("--out-dir", default=None,
                    help="override output directory (default: config.paths.report_dir)")
    args = ap.parse_args()

    cfg = load_config(args.config)

    # Resolve paths (relative to mvp/ by default)
    mvp_root = HERE.parent
    spec_dir = mvp_root / cfg["paths"]["specificity_matrix_dir"]
    out_dir = Path(args.out_dir) if args.out_dir else mvp_root / cfg["paths"]["report_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)

    # -- Behavioral (specificity matrix) --
    if args.mve_only:
        print("[skip] --mve-only: skipping behavioral analysis")
        deltas = pd.DataFrame()
        classification = {"verdict": "no_data", "per_model": {}, "cells": []}
    else:
        print(f"[load] specificity CSVs from {spec_dir}")
        df = load_specificity_csvs(spec_dir, cfg, model_filter=args.model)
        if df.empty:
            print("      (no specificity data yet — matrix not run)")
        else:
            print(f"      {len(df)} rows loaded")
        cell_stats = compute_cell_stats(df, cfg)
        deltas = compute_deltas(cell_stats, cfg)
        classification = classify_specificity_matrix(deltas, cfg)
        print(f"[behavioral] verdict: {classification['verdict']}")
        for model, result in classification.get("per_model", {}).items():
            print(f"      {model}: diagonal_wins={result['diagonal_wins']}, "
                  f"off_diag_failures={result['off_diag_failures']}, verdict={result['verdict']}")

    # -- Geometric MVE --
    mve_summaries = {}
    mve_dfs = {}
    models_to_run = [args.model] if args.model else [m["name"] for m in cfg["models"]]
    for model in models_to_run:
        print(f"[mve] loading vectors for {model}")
        model_vectors = load_vectors_for_model(model, cfg)
        n_loaded = {v: len(layers) for v, layers in model_vectors.items() if layers}
        if not any(n_loaded.values()):
            print(f"      no vectors found for {model}; skipping MVE")
            continue
        print(f"      loaded: {n_loaded}")
        mve_df = compute_mve_matrix(model_vectors, cfg)
        mve_summary = compute_mve_summary(mve_df, cfg)
        mve_summaries[model] = mve_summary
        mve_dfs[model] = mve_df
        print(f"      MVE verdict: {mve_summary['overall_verdict']} "
              f"({mve_summary['n_pass']}/{mve_summary['n_pairs']} pairs pass)")

    # -- Render figures + report --
    print(f"[render] figures + markdown report → {out_dir}")
    fig_paths = render_all(deltas, mve_summaries, mve_dfs, cfg, out_dir)
    report_path = render_report(
        classification, deltas, mve_summaries, mve_dfs, cfg,
        out_dir / "report.md", fig_paths,
    )
    print(f"      {report_path}")
    for p in fig_paths:
        print(f"      {p}")

    # Also dump per-cell CSV for inspection
    if not deltas.empty:
        cells_csv = out_dir / "per_cell_table.csv"
        deltas.to_csv(cells_csv, index=False)
        print(f"      {cells_csv}")

    print("\ndone.")


if __name__ == "__main__":
    main()
