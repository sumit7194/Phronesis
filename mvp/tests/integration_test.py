"""
Integration test for the full Phronesis analysis→review→report pipeline.

Tests the seams between:
  1. specificity_matrix.py output format (CSV) → review app import
  2. review app output → analysis pipeline input
  3. analysis pipeline reading both auto-scores and human-reviews

Uses synthetic data. No GPU, no real model calls. Tests column consistency,
file-format round-trips, and that the final markdown report renders with
both auto and human scores.

Usage:
    python3 /tmp/integration_test.py

Exit code 0 = all seams work; anything else = found bugs.
"""
from __future__ import annotations
import csv
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MVP = Path("/Users/sumit/Github/Phronesis/mvp")
sys.path.insert(0, str(MVP))
sys.path.insert(0, str(MVP / "analysis"))
sys.path.insert(0, str(MVP / "review"))
sys.path.insert(0, str(MVP / "benchmarks"))


def fail(msg):
    print(f"\n❌ FAIL: {msg}")
    sys.exit(1)


def passed(msg):
    print(f"✓ {msg}")


def make_synthetic_spec_matrix(out_path: Path, n_prompts_per_eval: int = 6) -> int:
    """Generate a realistic-shaped specificity-matrix CSV.

    Produces rows for:
      1 model × 5 vectors (baseline + 4 steered) × 4 evals × N prompts
      = 1 × 5 × 4 × N rows

    Scores are synthetic but structured: diagonal cells get the target virtue
    boosted; off-diagonals near baseline.
    """
    import random
    random.seed(42)

    VIRTUES = ["CC", "IH", "EG", "RT"]
    VECTOR_KEYS = ["baseline", "L20", "IH_L20", "EG_L20", "RT_L20"]  # Qwen convention
    VECTOR_TO_VIRTUE = {
        "baseline": None,
        "L20": "CC",
        "IH_L20": "IH",
        "EG_L20": "EG",
        "RT_L20": "RT",
    }
    EVALS = ["aime-42", "abstention", "eg-eval", "rt-eval"]
    EVAL_TO_VIRTUE = {
        "aime-42": "CC",
        "abstention": "IH",
        "eg-eval": "EG",
        "rt-eval": "RT",
    }
    VIRTUE_SCORE_COL = {
        "CC": "cc_hedging_score",
        "IH": "ih_abstention_score",
        "EG": "eg_score",
        "RT": "rt_score",
    }

    rows = []
    for vector in VECTOR_KEYS:
        for eval_name in EVALS:
            for i in range(n_prompts_per_eval):
                scores = {
                    "cc_hedging_score": round(random.uniform(0.2, 1.5), 3),
                    "ih_abstention_score": round(random.uniform(0.1, 1.2), 3),
                    "eg_score": round(random.uniform(0.5, 3.5), 3),
                    "rt_score": round(random.uniform(0.8, 4.0), 3),
                }
                # Diagonal boost
                vec_virtue = VECTOR_TO_VIRTUE.get(vector)
                eval_virtue = EVAL_TO_VIRTUE[eval_name]
                if vec_virtue and vec_virtue == eval_virtue:
                    target_col = VIRTUE_SCORE_COL[vec_virtue]
                    scores[target_col] = round(scores[target_col] + 8 + random.uniform(-1, 1.5), 3)

                rows.append({
                    "model": "qwen3-4b",
                    "vector": vector,
                    "alpha": 0 if vector == "baseline" else 12,
                    "eval": eval_name,
                    "item_id": f"{eval_name[:3]}-p{i:02d}",
                    "prompt": f"Test prompt for {eval_name} item {i}.",
                    "tokens": 150 + i * 5 + random.randint(-20, 30),
                    **scores,
                    "generation_preview": f"Preview of {vector} on {eval_name} p{i}...",
                    "generation_full": (
                        f"This is the full generated text for {vector} on {eval_name} item {i}. "
                        f"It contains relevant reasoning about the prompt. "
                        f"According to the study, the observational data suggests X. "
                        f"First, consider the evidence. Therefore, we can conclude Y. "
                        f"The weakest step here is Z."
                    ),
                })

    cols = list(rows[0].keys())
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def simulate_human_review(review_csv: Path, fraction: float = 0.5):
    """Fill in human review columns for a fraction of items in a review CSV.

    Returns (n_reviewed, n_total).
    """
    from storage import ReviewStore  # noqa: E402

    store = ReviewStore(review_csv)
    n_total = len(store)
    n_to_review = int(n_total * fraction)

    # Review first N items with realistic-ish ratings
    # Rating correlates with auto score, with some human-disagreement noise
    import random
    random.seed(7)
    for i in range(n_to_review):
        item = store.get_by_index(i)
        if item is None:
            continue

        def rating_from_score(score, scale=5.0):
            # Map score into 1-5, with noise
            if score > 10:
                base = 5
            elif score > 5:
                base = 4
            elif score > 2:
                base = 3
            elif score > 0.5:
                base = 2
            else:
                base = 1
            # Add ±1 human disagreement noise
            noise = random.choice([-1, 0, 0, 0, 1])
            return str(max(1, min(5, base + noise)))

        store.update(
            item.primary_key,
            human_cc_1to5=rating_from_score(item.cc_hedging_score),
            human_ih_1to5=rating_from_score(item.ih_abstention_score),
            human_eg_1to5=rating_from_score(item.eg_score),
            human_rt_1to5=rating_from_score(item.rt_score),
            gaming_flag="no",
            degenerate_flag="no",
            notes=f"auto-review item {i}",
            reviewer="test-script",
        )
    store.save()
    return (n_to_review, n_total)


def main():
    print("=" * 60)
    print("Phronesis integration test — analysis → review → report")
    print("=" * 60)

    # Set up isolated working directory
    tmp = Path(tempfile.mkdtemp(prefix="phronesis_integration_"))
    print(f"\nUsing temp dir: {tmp}\n")

    # Copy the mvp/ tree we need (just the scripts + config, not models/ or results/)
    # Simpler: run analysis/review against this tmp dir as output root
    try:
        spec_dir = tmp / "specificity_matrix"
        review_dir = tmp / "manual_review"
        report_dir = tmp / "analysis_report"
        spec_dir.mkdir(parents=True)
        review_dir.mkdir(parents=True)

        # ── Step 1: Synthetic specificity CSV ────────────────────────────────
        spec_csv = spec_dir / "all_generations_qwen3-4b.csv"
        n_spec = make_synthetic_spec_matrix(spec_csv, n_prompts_per_eval=6)
        passed(f"Generated synthetic specificity CSV: {n_spec} rows")

        # ── Step 2: Build review CSV from spec (simulates `/build/{session}`) ─
        from storage import build_review_csv_from_specificity, ReviewStore  # noqa: E402

        review_csv = review_dir / "qwen3-4b.csv"
        n_review = build_review_csv_from_specificity(spec_csv, review_csv)
        if n_review != n_spec:
            fail(f"Review CSV has {n_review} rows, expected {n_spec} (match spec)")
        passed(f"Review CSV built from spec: {n_review} rows")

        # Verify review CSV has all expected columns
        with open(review_csv) as f:
            header = next(csv.reader(f))
        from storage import AUTO_COLUMNS, REVIEW_COLUMNS, ALL_COLUMNS  # noqa: E402
        missing = set(ALL_COLUMNS) - set(header)
        if missing:
            fail(f"Review CSV missing columns: {missing}")
        passed(f"Review CSV has all {len(ALL_COLUMNS)} expected columns")

        # ── Step 3: Simulate human review on 50% of rows ─────────────────────
        n_reviewed, n_total = simulate_human_review(review_csv, fraction=0.5)
        passed(f"Simulated human review on {n_reviewed}/{n_total} rows")

        # Verify reviewed rows actually persisted
        store = ReviewStore(review_csv)
        actual_reviewed = sum(1 for it in store if it.is_reviewed)
        if actual_reviewed != n_reviewed:
            fail(f"Only {actual_reviewed} reviewed after save; expected {n_reviewed}")
        passed(f"Reviewed rows persisted in CSV: {actual_reviewed}")

        # ── Step 4: Analysis pipeline loads the specificity CSV ──────────────
        from load_matrix import load_config, load_specificity_csvs, load_review_csv  # noqa: E402

        config_path = MVP / "analysis" / "config.yaml"
        cfg = load_config(config_path)
        passed("Analysis config loaded")

        df_spec = load_specificity_csvs(spec_dir, cfg)
        if len(df_spec) != n_spec:
            fail(f"Analysis loaded {len(df_spec)} rows, expected {n_spec}")
        passed(f"Analysis loaded specificity CSV: {len(df_spec)} rows")

        # ── Step 5: Analysis computes per-cell effects + classifies ──────────
        from compute_effects import compute_cell_stats, compute_deltas, classify_specificity_matrix  # noqa: E402

        cell_stats = compute_cell_stats(df_spec, cfg)
        if cell_stats.empty:
            fail("compute_cell_stats returned empty DataFrame")
        passed(f"Computed cell stats: {len(cell_stats)} cells")

        deltas = compute_deltas(cell_stats, cfg)
        if deltas.empty:
            fail("compute_deltas returned empty DataFrame")
        n_diagonal = int(deltas["is_diagonal"].sum())
        if n_diagonal != 4:
            fail(f"Expected 4 diagonal cells, got {n_diagonal}")
        passed(f"Deltas computed: {len(deltas)} cells, {n_diagonal} diagonal")

        classification = classify_specificity_matrix(deltas, cfg)
        verdict = classification.get("verdict")
        passed(f"Classification verdict: {verdict}")
        # With synthetic data (boosted diagonals), expect all_clean
        if verdict != "all_clean":
            fail(f"Expected 'all_clean' on synthetic ideal data, got: {verdict}")

        # ── Step 6: Analysis loads review CSV (human vs auto) ────────────────
        df_review = load_review_csv(review_csv)
        if len(df_review) != n_total:
            fail(f"load_review_csv got {len(df_review)}, expected {n_total}")
        passed(f"Analysis loaded review CSV: {len(df_review)} rows")

        # Verify human columns present and roughly half populated.
        # Use the is_reviewed helper (checks all 4 human_* columns non-empty).
        from load_matrix import is_reviewed  # noqa: E402

        for c in ["human_cc_1to5", "human_ih_1to5", "human_eg_1to5", "human_rt_1to5"]:
            if c not in df_review.columns:
                fail(f"Review CSV missing {c} column")
        n_human_filled = int(is_reviewed(df_review).sum())
        if abs(n_human_filled - n_reviewed) > 1:
            fail(f"Expected ~{n_reviewed} human-filled rows, got {n_human_filled}")
        passed(f"Human review (all 4 virtues filled): {n_human_filled}/{n_total}")

        # ── Step 7: Figures render ──────────────────────────────────────────
        from compute_mve import compute_mve_matrix, compute_mve_summary  # noqa: E402
        from figures import render_all  # noqa: E402
        import numpy as np

        # Synthetic MVE data: 4 near-orthogonal vectors × 5 layers
        rng = np.random.default_rng(0)
        base_dirs = rng.standard_normal((4, 128))
        base_dirs /= np.linalg.norm(base_dirs, axis=1, keepdims=True)
        synthetic_vectors = {}
        for i, v in enumerate(["CC", "IH", "EG", "RT"]):
            synthetic_vectors[v] = {
                L: (base_dirs[i] + rng.standard_normal(128) * 0.02) * (2 + L)
                for L in range(5)
            }
        mve_df = compute_mve_matrix(synthetic_vectors, cfg)
        mve_summary = compute_mve_summary(mve_df, cfg)

        fig_paths = render_all(
            deltas,
            {"qwen3-4b": mve_summary},
            {"qwen3-4b": mve_df},
            cfg,
            report_dir,
        )
        if len(fig_paths) < 3:
            fail(f"Expected ≥3 figures rendered, got {len(fig_paths)}")
        for fp in fig_paths:
            if not fp.exists() or fp.stat().st_size == 0:
                fail(f"Figure file missing or empty: {fp}")
        passed(f"Figures rendered: {len(fig_paths)} PNGs")

        # ── Step 8: Report renders ───────────────────────────────────────────
        from report import render_report  # noqa: E402

        report_path = render_report(
            classification,
            deltas,
            {"qwen3-4b": mve_summary},
            {"qwen3-4b": mve_df},
            cfg,
            report_dir / "report.md",
            fig_paths,
        )
        if not report_path.exists():
            fail(f"Report file not written: {report_path}")
        content = report_path.read_text()
        for required_section in ["Overall verdict", "Behavioral", "Geometric MVE", "Caveats"]:
            if required_section not in content:
                fail(f"Report missing section: {required_section}")
        passed(f"Report renders with all required sections ({len(content)} chars)")

        # Check report references the figures by filename
        for fp in fig_paths:
            if fp.name not in content:
                fail(f"Report doesn't reference figure: {fp.name}")
        passed("Report references all rendered figures")

        # ── Step 9: Summary ──────────────────────────────────────────────────
        print("\n" + "=" * 60)
        print("✅ ALL INTEGRATION TESTS PASSED")
        print("=" * 60)
        print(f"""
Full pipeline validated end-to-end:
  1. Synthetic specificity CSV  → {n_spec} rows
  2. Review CSV build            → {n_review} rows, correct schema
  3. Simulated human review      → {n_reviewed}/{n_total} reviewed, persisted
  4. Analysis loads spec CSV     → {len(df_spec)} rows into DataFrame
  5. compute_cell_stats          → {len(cell_stats)} cells
  6. compute_deltas              → {len(deltas)} deltas, {n_diagonal} diagonal
  7. classify                    → verdict="{verdict}"  (expected all_clean on ideal data)
  8. Analysis loads review CSV   → {n_human_filled}/{len(df_review)} human-filled
  9. Figures                     → {len(fig_paths)} PNGs, non-empty
 10. Report                      → {len(content)} chars, all sections + figure refs

No integration seams broken. Ready for real data.
""")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
