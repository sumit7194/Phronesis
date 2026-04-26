"""
Figure generation — matplotlib PNGs, static, no interactivity.

Produces three figures for the report:
  1. specificity_heatmap.png — 4×4 matrix of diagonal vs off-diagonal deltas
  2. mve_heatmap.png — pairwise |cos| between virtues per model
  3. per_layer_cosine.png — cosine across layers for each pair (MVE detail)

Public API:
  render_specificity_heatmap(deltas_df, config, out_path)
  render_mve_heatmap(mve_summary, config, out_path, model)
  render_per_layer_cosine(mve_df, config, out_path, model)
  render_all(deltas, mve_summaries_by_model, mve_dfs_by_model, config, out_dir) -> list[Path]
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # non-interactive backend, no display required
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Consistent styling across figures
DARK_BG = "#0d1117"
LIGHT_TEXT = "#d1d5db"
GRID_COLOR = "#30363d"


def _setup_ax(ax, title: str, dark: bool = False):
    if dark:
        ax.set_facecolor(DARK_BG)
        ax.tick_params(colors=LIGHT_TEXT)
        for spine in ax.spines.values():
            spine.set_color(GRID_COLOR)
    ax.set_title(title, fontsize=11, fontweight="bold", color=(LIGHT_TEXT if dark else "black"))


def render_specificity_heatmap(
    deltas_df: pd.DataFrame,
    config: dict,
    out_path: Path,
) -> Path:
    """4×4 heatmap per model: rows = steered vectors, cols = evals, cell = delta in target virtue.

    Diagonal cells (vector matches eval's target virtue) should show large positive delta;
    off-diagonal should be near zero. Cells annotated with value + CI hint.
    """
    if deltas_df.empty:
        # Produce a placeholder figure
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(0.5, 0.5, "No specificity data yet", ha="center", va="center", fontsize=14)
        ax.axis("off")
        fig.savefig(out_path, dpi=120, bbox_inches="tight")
        plt.close(fig)
        return out_path

    virtues = [v["name"] for v in config["virtues"]]
    evals = [e["name"] for e in config["evals"]]
    models = sorted(deltas_df["model"].unique())

    # Vector name mapping — first vector matching each virtue in the df
    def vector_for_virtue(virtue_name, model_df):
        # Steered virtue is inferred via `steered_virtue` column if present, else vector prefix
        if "steered_virtue" in model_df.columns:
            sub = model_df[model_df["steered_virtue"] == virtue_name]
        else:
            sub = model_df[model_df["vector"].str.startswith((virtue_name.upper() + "_", virtue_name.lower() + "_"))]
            if virtue_name == "CC":
                # CC vectors may start with just "L" (from existing registry)
                sub = pd.concat([sub, model_df[model_df["vector"].str.match(r"^L\d+$")]], ignore_index=True)
        if sub.empty:
            return None
        return sub["vector"].iloc[0]

    n_models = len(models)
    fig, axes = plt.subplots(1, n_models, figsize=(6 * n_models, 5), squeeze=False)

    for m_i, model in enumerate(models):
        m_df = deltas_df[deltas_df["model"] == model]
        matrix = np.full((len(virtues), len(evals)), np.nan)

        for r, v_name in enumerate(virtues):
            # For each (vector_virtue, eval) find the steered delta
            for c, eval_name in enumerate(evals):
                cell = m_df[(m_df["steered_virtue"] == v_name) & (m_df["eval"] == eval_name)] \
                    if "steered_virtue" in m_df.columns else m_df[m_df["eval"] == eval_name]
                if "steered_virtue" not in m_df.columns:
                    # Fallback: match by vector name prefix
                    mask = m_df["vector"].str.startswith((v_name.upper() + "_", v_name.lower() + "_"))
                    if v_name == "CC":
                        mask = mask | m_df["vector"].str.match(r"^L\d+$")
                    cell = m_df[mask & (m_df["eval"] == eval_name)]
                if not cell.empty:
                    matrix[r, c] = cell["delta"].iloc[0]

        ax = axes[0][m_i]
        vmax = np.nanmax(np.abs(matrix)) if np.any(~np.isnan(matrix)) else 1
        cmap = plt.cm.RdYlGn
        im = ax.imshow(matrix, cmap=cmap, vmin=-vmax, vmax=vmax, aspect="auto")

        ax.set_xticks(range(len(evals)))
        ax.set_xticklabels(evals, rotation=30, ha="right", fontsize=9)
        ax.set_yticks(range(len(virtues)))
        ax.set_yticklabels([f"v_{v}" for v in virtues], fontsize=10)
        ax.set_xlabel("eval")
        ax.set_ylabel("steered vector")
        ax.set_title(f"Specificity matrix — {model}", fontweight="bold")

        # Annotate cells
        for r in range(len(virtues)):
            for c in range(len(evals)):
                v = matrix[r, c]
                if np.isnan(v):
                    continue
                # Diagonal box
                if r == c:
                    ax.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1, fill=False,
                                               edgecolor="black", linewidth=2))
                ax.text(c, r, f"{v:+.1f}", ha="center", va="center",
                        color="black" if abs(v) < 0.6 * vmax else "white",
                        fontsize=10, fontweight="bold")

        plt.colorbar(im, ax=ax, label="delta (steered − baseline)", fraction=0.046, pad=0.04)

    fig.suptitle("Specificity matrix: diagonal = virtue self-drive, off-diagonal should be near 0",
                 fontsize=12, y=1.02)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out_path


def render_mve_heatmap(
    mve_summary: dict,
    config: dict,
    out_path: Path,
    model: str,
) -> Path:
    """N×N lower-triangle heatmap of mean |cos| between virtue pairs.

    Green = orthogonal (pass), yellow = partial, red = collapse.
    """
    virtues = [v["name"] for v in config["virtues"]]
    n = len(virtues)
    mtx = np.full((n, n), np.nan)
    verdicts = {}

    for pair in mve_summary.get("pairs", []):
        i = virtues.index(pair["virtue_a"])
        j = virtues.index(pair["virtue_b"])
        mtx[i, j] = pair["mean_abs_cos"]
        mtx[j, i] = pair["mean_abs_cos"]
        verdicts[(i, j)] = pair["verdict"]
        verdicts[(j, i)] = pair["verdict"]
    # Diagonal: self-cos = 1
    for i in range(n):
        mtx[i, i] = 1.0

    fig, ax = plt.subplots(figsize=(5.5, 5))
    cos_clean = config["mve"]["cos_clean_threshold"]
    cos_partial = config["mve"]["cos_partial_threshold"]
    # Custom cmap: green (0) → yellow (cos_partial) → red (1)
    cmap = plt.cm.RdYlGn_r
    im = ax.imshow(mtx, cmap=cmap, vmin=0, vmax=cos_partial * 1.2, aspect="equal")

    ax.set_xticks(range(n))
    ax.set_xticklabels(virtues, fontsize=10)
    ax.set_yticks(range(n))
    ax.set_yticklabels(virtues, fontsize=10)
    ax.set_title(f"Geometric MVE — {model}\nmean |cos| across layers (green=orthogonal, red=collapse)",
                 fontsize=11, fontweight="bold")

    for i in range(n):
        for j in range(n):
            if np.isnan(mtx[i, j]):
                continue
            v = mtx[i, j]
            ax.text(j, i, f"{v:.3f}", ha="center", va="center",
                    color="black" if v < 0.3 else "white", fontsize=9, fontweight="bold")

    # Threshold bar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.axhline(cos_clean, color="green", lw=1.5, linestyle="--")
    cbar.ax.axhline(cos_partial, color="orange", lw=1.5, linestyle="--")
    cbar.set_label("mean |cos|")

    fig.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out_path


def render_per_layer_cosine(
    mve_df: pd.DataFrame,
    config: dict,
    out_path: Path,
    model: str,
) -> Path:
    """Line plot: |cos| across layers for each virtue pair.
    Useful for seeing if separation varies by depth."""
    if mve_df.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(0.5, 0.5, "No MVE data yet", ha="center", va="center", fontsize=14)
        ax.axis("off")
        fig.savefig(out_path, dpi=120, bbox_inches="tight")
        plt.close(fig)
        return out_path

    fig, ax = plt.subplots(figsize=(8, 5))
    for (va, vb), g in mve_df.groupby(["virtue_a", "virtue_b"], sort=False):
        g = g.sort_values("layer")
        ax.plot(g["layer"], g["abs_cos"], marker="o", markersize=4,
                label=f"{va} ⊥ {vb}", linewidth=1.5)

    ax.axhline(config["mve"]["cos_clean_threshold"], color="green", lw=1, linestyle="--",
               label=f"clean-orthogonal (|cos|<{config['mve']['cos_clean_threshold']})")
    ax.axhline(config["mve"]["cos_partial_threshold"], color="orange", lw=1, linestyle="--",
               label=f"partial-overlap threshold")
    ax.set_xlabel("layer")
    ax.set_ylabel("|cos|")
    ax.set_title(f"Per-layer cosine similarity — {model}", fontweight="bold")
    ax.legend(loc="best", fontsize=9)
    ax.grid(alpha=0.3)
    ax.set_ylim(-0.02, 1.05)

    fig.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out_path


def render_all(
    deltas: pd.DataFrame,
    mve_summaries_by_model: dict,
    mve_dfs_by_model: dict,
    config: dict,
    out_dir: Path,
) -> list[Path]:
    """Render every figure the report needs. Returns list of output paths."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    paths = []
    paths.append(render_specificity_heatmap(deltas, config, out_dir / "specificity_heatmap.png"))

    for model, summary in mve_summaries_by_model.items():
        paths.append(render_mve_heatmap(summary, config, out_dir / f"mve_heatmap_{model}.png", model))
        df = mve_dfs_by_model.get(model, pd.DataFrame())
        paths.append(render_per_layer_cosine(df, config, out_dir / f"per_layer_cosine_{model}.png", model))

    return paths


if __name__ == "__main__":
    # Smoke test: generate figures from synthetic data
    from pathlib import Path
    from load_matrix import load_config
    from compute_effects import compute_cell_stats, compute_deltas
    from compute_mve import compute_mve_matrix, compute_mve_summary
    import numpy as np
    import random

    cfg = load_config(Path(__file__).parent / "config.yaml")

    # Synthetic specificity data
    random.seed(0)
    rows = []
    evals = [e["name"] for e in cfg["evals"]]
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
                    v_map = {"CC_L20": "cc_hedging_score", "IH_L20": "ih_abstention_score",
                             "EG_L20": "eg_score", "RT_L20": "rt_score"}
                    eval_target = {"aime": "cc_hedging_score", "abstention": "ih_abstention_score",
                                   "eg-eval": "eg_score", "rt-eval": "rt_score"}
                    if v_map[vector] == eval_target[eval_name]:
                        base_scores[v_map[vector]] += 8 + random.uniform(-1, 1)
                rows.append({
                    "model": "qwen3-4b", "vector": vector, "alpha": 0 if vector == "baseline" else 12,
                    "eval": eval_name, "item_id": f"p{i}", "tokens": 200, **base_scores,
                })
    df = pd.DataFrame(rows)
    cs = compute_cell_stats(df, cfg)
    dd = compute_deltas(cs, cfg)

    # Synthetic MVE data
    rng = np.random.default_rng(0)
    base_dirs = rng.standard_normal((4, 128))
    base_dirs /= np.linalg.norm(base_dirs, axis=1, keepdims=True)
    synthetic = {}
    for i, v in enumerate(["CC", "IH", "EG", "RT"]):
        synthetic[v] = {L: (base_dirs[i] + rng.standard_normal(128) * 0.02) * (2 + L) for L in range(5)}
    mve_df = compute_mve_matrix(synthetic, cfg)
    mve_summary = compute_mve_summary(mve_df, cfg)

    out_dir = Path(__file__).parent.parent / "results" / "analysis_report" / "_smoke_test"
    paths = render_all(
        dd,
        {"qwen3-4b": mve_summary},
        {"qwen3-4b": mve_df},
        cfg,
        out_dir,
    )
    for p in paths:
        print(f"wrote {p}")
