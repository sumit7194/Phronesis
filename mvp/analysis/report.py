"""
Render the final markdown report.

Pulls together:
  - Headline verdict (all_clean / partial / collapse) per the pre-registration
  - Specificity matrix table + heatmap PNG
  - Per-cell verdicts (diagonal wins, off-diagonal failures)
  - Per-model MVE tables + heatmap PNGs
  - Per-layer cosine detail
  - Raw data CSV references
  - Known caveats (scorer FMs, cross-source variance, etc.)

Output: one markdown file with inline PNG references (relative paths).
"""
from __future__ import annotations
from datetime import datetime
from pathlib import Path

import pandas as pd


VERDICT_BADGE = {
    "all_clean": "✅ **ALL CLEAN**",
    "partial": "⚠️ **PARTIAL**",
    "collapse": "❌ **COLLAPSE**",
    "insufficient_data": "⏳ **INSUFFICIENT DATA**",
    "no_data": "⏳ **NO DATA YET**",
}


def _render_specificity_table(deltas_df: pd.DataFrame, classification: dict) -> str:
    if deltas_df.empty:
        return "*(no specificity data yet — run specificity_matrix.py first)*\n"

    lines = []
    # Build a per-cell verdict lookup from classification
    cell_verdict = {}
    for c in classification.get("cells", []):
        key = (c["model"], c["vector"], c["eval"])
        cell_verdict[key] = c["verdict"]

    for model in sorted(deltas_df["model"].unique()):
        lines.append(f"\n### {model}\n")
        lines.append("| vector | eval | target virtue | diag? | baseline | steered | delta | CI | verdict |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        m_df = deltas_df[deltas_df["model"] == model].sort_values(["vector", "eval"])
        for _, r in m_df.iterrows():
            key = (r["model"], r["vector"], r["eval"])
            verdict = cell_verdict.get(key, "?")
            badge = {"win": "🟢 win", "flag": "🟡 flag", "fail": "🔴 fail", "ok": "✓ ok", "?": "?"}.get(verdict, verdict)
            diag = "◆" if r.get("is_diagonal") else ""
            ci = f"[{r['delta_ci_low']:+.2f}, {r['delta_ci_high']:+.2f}]"
            lines.append(
                f"| `{r['vector']}` | `{r['eval']}` | {r['target_virtue']} | {diag} | "
                f"{r['baseline_mean']:+.2f} | {r['steered_mean']:+.2f} | "
                f"**{r['delta']:+.2f}** | {ci} | {badge} |"
            )
    return "\n".join(lines)


def _render_mve_table(mve_summary: dict, model: str) -> str:
    if not mve_summary.get("pairs"):
        return "*(no MVE data yet — extraction in progress or no vectors found)*"

    lines = [
        f"\n#### {model}\n",
        "| pair | mean \\|cos\\| | max \\|cos\\| | mean retention | verdict |",
        "|---|---|---|---|---|",
    ]
    for pair in mve_summary["pairs"]:
        badge = {"pass": "🟢 pass", "partial": "🟡 partial", "collapse": "🔴 collapse"}.get(
            pair["verdict"], pair["verdict"]
        )
        lines.append(
            f"| {pair['virtue_a']} ⊥ {pair['virtue_b']} | "
            f"{pair['mean_abs_cos']:.4f} | {pair['max_abs_cos']:.4f} | "
            f"{pair['mean_retention']*100:.1f}% | {badge} |"
        )
    return "\n".join(lines)


def render_report(
    classification: dict,
    deltas_df: pd.DataFrame,
    mve_summaries: dict,     # model → mve_summary dict
    mve_dfs: dict,           # model → mve per-layer df
    config: dict,
    out_path: Path,
    figure_paths: list[Path] = None,
) -> Path:
    """Generate the markdown report.

    figure_paths is a list of already-rendered PNGs; they must live in the same dir
    as `out_path` (or a relative subdir) for the markdown image refs to resolve.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    figure_paths = figure_paths or []

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    # Overall verdict (worst of MVE and behavioral)
    # Order from best → worst, with special "pending" states at the end
    order = ["all_clean", "partial", "collapse", "insufficient_data", "no_data"]
    behavioral_verdict = classification.get("verdict", "no_data")
    mve_verdicts = [s.get("overall_verdict", "no_data") for s in mve_summaries.values()]
    worst = behavioral_verdict
    for v in mve_verdicts:
        # Treat unknown verdicts as worst-case
        v_rank = order.index(v) if v in order else len(order)
        worst_rank = order.index(worst) if worst in order else len(order)
        if v_rank > worst_rank:
            worst = v

    sections = []
    sections.append(f"# Phronesis — EG + RT specificity matrix analysis\n")
    sections.append(f"*Generated {now}*\n")
    sections.append(f"## Overall verdict: {VERDICT_BADGE.get(worst, worst)}\n")
    sections.append(
        "Per F98 pre-registration (`docs/findings.md`) and "
        "exit criteria in `docs/eg-rt-eval-spec.md` §5.7.\n"
    )

    # Behavioral verdict
    sections.append("## Behavioral (4×4 specificity matrix)\n")
    sections.append(f"**Verdict:** {VERDICT_BADGE.get(behavioral_verdict, behavioral_verdict)}\n")
    for model, pm in classification.get("per_model", {}).items():
        sections.append(
            f"- **{model}**: {pm['diagonal_wins']}/4 diagonal wins, "
            f"{pm['off_diag_failures']} off-diagonal failures → "
            f"{VERDICT_BADGE.get(pm['verdict'], pm['verdict'])}"
        )
    sections.append("")

    # Specificity heatmap
    spec_png = next((p for p in figure_paths if p.name == "specificity_heatmap.png"), None)
    if spec_png:
        rel = spec_png.relative_to(out_path.parent) if spec_png.is_absolute() else spec_png
        sections.append(f"\n![specificity heatmap]({rel})\n")

    sections.append("### Per-cell deltas\n")
    sections.append(_render_specificity_table(deltas_df, classification))

    # Geometric MVE
    sections.append("\n## Geometric MVE (pairwise orthogonality)\n")
    for model in sorted(mve_summaries.keys()):
        s = mve_summaries[model]
        verdict_badge = VERDICT_BADGE.get(s.get("overall_verdict"), s.get("overall_verdict"))
        expected = s.get("expected_pairs", 0)
        sections.append(
            f"- **{model}**: {s.get('n_pass', 0)}/{s.get('n_pairs', 0)} pairs pass "
            f"(expected {expected}) → {verdict_badge}"
        )

        sections.append(_render_mve_table(s, model))
        png = next((p for p in figure_paths if p.name == f"mve_heatmap_{model}.png"), None)
        if png:
            rel = png.relative_to(out_path.parent) if png.is_absolute() else png
            sections.append(f"\n![MVE heatmap {model}]({rel})\n")
        png2 = next((p for p in figure_paths if p.name == f"per_layer_cosine_{model}.png"), None)
        if png2:
            rel = png2.relative_to(out_path.parent) if png2.is_absolute() else png2
            sections.append(f"\n![per-layer cosine {model}]({rel})\n")

    # Caveats + provenance
    sections.append("\n## Caveats\n")
    sections.append(
        "- **Scorer false-positive risk** (per `docs/scoring.md` FM-6): "
        "deficiency-non-virtuous passages using evidence vocabulary while making confident-causation "
        "claims can score as EG-virtuous. Hand review corrects.\n"
        "- **Technical-jargon false negative** (FM-7): chemistry/engineering prose may be under-scored "
        "by EG regex. Affects absolute magnitudes more than the relative effects measured here.\n"
        "- **Cross-source length variance**: ChatGPT batch-2 triplets are ~180w vs Sonnet ~230-290w. "
        "Within-triad lengths are matched (±10% per triplet per `LEDGER.md`), "
        "so intra-cell direction is clean; absolute score magnitudes may vary by source.\n"
        "- **Pre-registration**: all thresholds in `config.yaml` were committed before any data existed "
        "(F98). Verdicts are computed mechanically, not tuned post-hoc.\n"
    )

    sections.append("\n## Provenance\n")
    sections.append(f"- Config: `mvp/analysis/config.yaml`\n")
    sections.append(f"- Raw specificity data: `{config['paths']['specificity_matrix_dir']}/all_generations_*.csv`\n")
    sections.append(f"- Extracted vectors: `{config['paths']['vectors_dir']}/{{model}}/{{corpus}}/{{method}}/`\n")
    sections.append(f"- Source documents: `docs/mvp-virtues.md`, `docs/eg-rt-eval-spec.md`, `docs/findings.md` F98\n")

    out_path.write_text("\n".join(sections))
    return out_path


if __name__ == "__main__":
    # Smoke test: render report with toy data
    from pathlib import Path
    from load_matrix import load_config
    from compute_effects import compute_cell_stats, compute_deltas, classify_specificity_matrix
    from compute_mve import compute_mve_matrix, compute_mve_summary
    from figures import render_all
    import numpy as np
    import random

    cfg = load_config(Path(__file__).parent / "config.yaml")

    # Toy specificity data
    random.seed(0)
    rows = []
    evals = [e["name"] for e in cfg["evals"]]
    for vector in ["baseline", "CC_L20", "IH_L20", "EG_L20", "RT_L20"]:
        for eval_name in evals:
            for i in range(3):
                scores = {
                    "cc_hedging_score": random.uniform(0, 2),
                    "ih_abstention_score": random.uniform(0, 2),
                    "eg_score": random.uniform(0, 3),
                    "rt_score": random.uniform(0, 3),
                }
                if vector != "baseline":
                    v_map = {"CC_L20": "cc_hedging_score", "IH_L20": "ih_abstention_score",
                             "EG_L20": "eg_score", "RT_L20": "rt_score"}
                    eval_target = {"aime-42": "cc_hedging_score", "abstention": "ih_abstention_score",
                                   "eg-eval": "eg_score", "rt-eval": "rt_score"}
                    if v_map[vector] == eval_target[eval_name]:
                        scores[v_map[vector]] += 8 + random.uniform(-1, 1)
                rows.append({
                    "model": "qwen3-4b", "vector": vector, "alpha": 0 if vector == "baseline" else 12,
                    "eval": eval_name, "item_id": f"p{i}", "tokens": 200, **scores,
                })
    df = pd.DataFrame(rows)
    cs = compute_cell_stats(df, cfg)
    dd = compute_deltas(cs, cfg)
    classification = classify_specificity_matrix(dd, cfg)

    # Toy MVE
    rng = np.random.default_rng(0)
    base_dirs = rng.standard_normal((4, 128))
    base_dirs /= np.linalg.norm(base_dirs, axis=1, keepdims=True)
    synthetic = {v: {L: (base_dirs[i] + rng.standard_normal(128) * 0.02) * (2 + L) for L in range(5)}
                 for i, v in enumerate(["CC", "IH", "EG", "RT"])}
    mve_df = compute_mve_matrix(synthetic, cfg)
    mve_summary = compute_mve_summary(mve_df, cfg)

    out_dir = Path(__file__).parent.parent / "results" / "analysis_report" / "_smoke_test"
    fig_paths = render_all(dd, {"qwen3-4b": mve_summary}, {"qwen3-4b": mve_df}, cfg, out_dir)
    report_path = render_report(
        classification, dd, {"qwen3-4b": mve_summary}, {"qwen3-4b": mve_df},
        cfg, out_dir / "report.md", fig_paths,
    )
    print(f"Report: {report_path}")
    print("\n--- First 40 lines of report ---")
    print("\n".join(report_path.read_text().splitlines()[:40]))
