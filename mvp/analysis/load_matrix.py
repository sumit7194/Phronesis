"""
Load specificity-matrix CSVs produced by specificity_matrix.py.

Each CSV row represents one (model, vector, eval, prompt_id) generation
with all 4 auto-scorer columns + (optionally) human-review columns.

Public API:
  load_config(path) -> dict
  load_specificity_csvs(dir, config) -> pandas.DataFrame
  load_review_csv(path) -> pandas.DataFrame

Returns pandas DataFrames with consistent columns across MVP (4 virtues) and
future Phase-5 (8 virtues) expansions.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import yaml


REQUIRED_CSV_COLUMNS = [
    "model", "vector", "alpha", "eval", "item_id",
    "tokens", "eg_score", "rt_score",
    "cc_hedging_score", "ih_abstention_score",
]

REVIEW_HUMAN_COLUMNS = [
    "human_cc_1to5", "human_ih_1to5", "human_eg_1to5", "human_rt_1to5",
    "gaming_flag", "degenerate_flag", "notes",
]


def load_config(path: str | Path) -> dict:
    """Load and lightly-validate the analysis config YAML.

    Raises ValueError if required sections are missing.
    """
    path = Path(path)
    with open(path) as f:
        cfg = yaml.safe_load(f)

    required_top = {"virtues", "evals", "models", "mve", "behavioral", "paths"}
    missing = required_top - set(cfg.keys())
    if missing:
        raise ValueError(f"config.yaml missing sections: {missing}")

    # Validate virtue × eval alignment
    virtue_names = {v["name"] for v in cfg["virtues"]}
    for ev in cfg["evals"]:
        if ev["target_virtue"] not in virtue_names:
            raise ValueError(
                f"eval {ev['name']} targets virtue {ev['target_virtue']} which is not declared"
            )

    return cfg


def load_specificity_csvs(
    dir_path: str | Path,
    config: Optional[dict] = None,
    model_filter: Optional[str] = None,
) -> pd.DataFrame:
    """Load all per-cell specificity matrix CSVs in a directory into one DataFrame.

    specificity_matrix.py writes files named like:
        {model}_{vector}_{eval}.csv
    plus an aggregated `all_generations_{model}.csv`.

    We prefer the aggregated file if present (one-file-per-model).

    Args:
        dir_path: directory path (typically mvp/results/specificity_matrix)
        config: optional loaded config (used only to validate column presence)
        model_filter: if set, only load rows for this model

    Returns:
        DataFrame with columns at minimum: REQUIRED_CSV_COLUMNS + any human-review columns.
        Returns empty DataFrame if no CSVs found (with correct column schema).
    """
    dir_path = Path(dir_path)
    if not dir_path.exists():
        return pd.DataFrame(columns=REQUIRED_CSV_COLUMNS)

    # Prefer per-model aggregated files
    aggregated = sorted(dir_path.glob("all_generations_*.csv"))
    if aggregated:
        dfs = [pd.read_csv(p) for p in aggregated]
    else:
        # Fall back to per-cell files
        per_cell = sorted(p for p in dir_path.glob("*.csv") if not p.name.startswith("summary"))
        if not per_cell:
            return pd.DataFrame(columns=REQUIRED_CSV_COLUMNS)
        dfs = [pd.read_csv(p) for p in per_cell]

    df = pd.concat(dfs, ignore_index=True)

    if model_filter is not None:
        df = df[df["model"] == model_filter].reset_index(drop=True)

    # Validate
    missing = [c for c in REQUIRED_CSV_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}. Found: {list(df.columns)}")

    return df


def load_review_csv(path: str | Path) -> pd.DataFrame:
    """Load a manual-review CSV. The CSV has the same auto-scorer columns PLUS
    the human_* + flags + notes columns."""
    path = Path(path)
    if not path.exists():
        return pd.DataFrame(columns=REQUIRED_CSV_COLUMNS + REVIEW_HUMAN_COLUMNS)
    return pd.read_csv(path)


def describe_df(df: pd.DataFrame) -> dict:
    """Quick summary of a loaded DataFrame for debugging."""
    if df.empty:
        return {"rows": 0}
    return {
        "rows": len(df),
        "models": sorted(df["model"].unique().tolist()),
        "vectors": sorted(df["vector"].unique().tolist()),
        "evals": sorted(df["eval"].unique().tolist()),
        "cells": df.groupby(["model", "vector", "eval"]).size().to_dict(),
    }


if __name__ == "__main__":
    # Sanity check: load config, print what we'd see
    import sys
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "config.yaml"
    cfg = load_config(cfg_path)
    print(f"Config loaded: {len(cfg['virtues'])} virtues, {len(cfg['evals'])} evals, {len(cfg['models'])} models")
    for v in cfg["virtues"]:
        print(f"  virtue {v['name']}: {v['full_name']} (concept {v['concept_number']})")

    spec_dir = Path(__file__).parent.parent / cfg["paths"]["specificity_matrix_dir"]
    df = load_specificity_csvs(spec_dir, cfg)
    desc = describe_df(df)
    print(f"\nSpecificity CSVs at {spec_dir}:")
    if desc["rows"] == 0:
        print("  (empty — no data yet, expected before specificity_matrix.py runs)")
    else:
        for k, v in desc.items():
            print(f"  {k}: {v}")
