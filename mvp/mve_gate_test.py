"""
MVE gate tests for the Intellectual Humility vector.

Per the red-team-approved design, we must pass the following gate BEFORE
committing to a 100+ triplet scale-up of the IH corpus:

  Test A:  Does v_IH lift abstention on our 24-item abstention benchmark
           by >= 5 percentage points, WITHOUT tanking N2/E3 (or their
           curated-probe proxy)?

  Test B:  After orthogonalising v_CC against v_IH (projecting out the
           v_IH component), does v_CC retain >= 70% of its commit-to-
           structure efficacy on AIME-3 (our curated set of 3 AIME items
           known to be sensitive to v_CC steering)?

  Test C:  Report cos(v_CC, v_IH) across layers - informational only,
           the geometric interpretation is not used as a gate but helps
           us understand the separability picture.

Decision matrix:
  A pass + B pass -> genuine second dimension; scale to 100+ IH triplets
  A pass + B fail -> same-axis; two poles of one axis; pivot paper
  A fail           -> IH not extractable at N=20; either scale to 50 and
                      retry, or pivot to a larger model.

This script computes Test C and B geometrically. Test A requires an
actual benchmark-generation run; we defer that to a separate script
(mve_test_a_abstention.py) that uses run_benchmark.py pipeline.

Usage (on L4 VM after extractions complete):
    cd ~/phronesis/mvp
    python3 mve_gate_test.py --model qwen3-4b
    python3 mve_gate_test.py --model gemma-4-E4B-it
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
import numpy as np

RESULTS_DIR = Path(__file__).parent / "results"


def load_vector(model: str, corpus: str, layer: int) -> np.ndarray | None:
    """Load the whitened virtue vector for a model×corpus×layer."""
    path = RESULTS_DIR / "vectors" / model / corpus / "last_token" / f"layer_{layer}_virtue_vector.npy"
    if not path.exists():
        return None
    return np.load(path)


def cos_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def orthogonalise(v: np.ndarray, along: np.ndarray) -> np.ndarray:
    """Return the component of v orthogonal to `along`."""
    along_hat = along / (np.linalg.norm(along) + 1e-12)
    return v - np.dot(v, along_hat) * along_hat


def run_matrix_mode(model: str, corpora: list, layer: int):
    """Compute pairwise cos + orthogonal-retention matrix for N virtue vectors.

    Used for the 4-virtue geometric MVE matrix (CC × IH × EG × RT).

    Args:
        model: model name (qwen3-4b or gemma-4-E4B-it)
        corpora: list of corpus names, e.g. ['triplets', 'triplets-intellectual-humility',
                 'mvp-combined/triplets-evidence-grounding', 'mvp-combined/triplets-reasoning-transparency']
        layer: single layer index to evaluate at
    """
    print(f"\n{'='*72}")
    print(f"MVE matrix — {model} at layer {layer}")
    print(f"Corpora: {corpora}")
    print(f"{'='*72}\n")

    # Load all vectors
    vectors = {}
    for c in corpora:
        v = load_vector(model, c, layer)
        if v is None:
            print(f"  MISSING: vector for {c} at layer {layer}")
            continue
        # Short label: last path component
        label = Path(c).name
        # Abbreviate common corpus names
        label_map = {
            "triplets": "CC",
            "triplets-combined": "CC",
            "triplets-intellectual-humility": "IH",
            "triplets-evidence-grounding": "EG",
            "triplets-reasoning-transparency": "RT",
        }
        short = label_map.get(label, label[:8])
        vectors[short] = {"name": c, "v": v}
        print(f"  loaded {short} ({c}): |v|={np.linalg.norm(v):.2f}, dim={v.shape[0]}")

    if len(vectors) < 2:
        print("\nNeed at least 2 vectors loaded. Aborting.")
        return None

    labels = list(vectors.keys())
    n = len(labels)

    # Cosine matrix (symmetric)
    cos_mtx = np.zeros((n, n))
    # Retention matrix: row_i orthogonal to col_j, retention of v_i
    ret_mtx = np.zeros((n, n))

    for i, li in enumerate(labels):
        for j, lj in enumerate(labels):
            v_i = vectors[li]["v"]
            v_j = vectors[lj]["v"]
            cos_mtx[i, j] = cos_sim(v_i, v_j)
            if i == j:
                ret_mtx[i, j] = 1.0  # trivial self-retention
            else:
                v_orth = orthogonalise(v_i, v_j)
                ret_mtx[i, j] = float(np.linalg.norm(v_orth) / (np.linalg.norm(v_i) + 1e-12))

    # Print matrices
    print(f"\n--- Cosine similarity matrix (layer {layer}) ---")
    print(f"{'':>6}", end="")
    for l in labels:
        print(f"{l:>10}", end="")
    print()
    for i, li in enumerate(labels):
        print(f"{li:>6}", end="")
        for j in range(n):
            print(f"{cos_mtx[i, j]:>10.4f}", end="")
        print()

    print(f"\n--- Retention matrix: row v_i's norm retained after ⊥ to col v_j ---")
    print(f"{'':>6}", end="")
    for l in labels:
        print(f"{l:>10}", end="")
    print()
    for i, li in enumerate(labels):
        print(f"{li:>6}", end="")
        for j in range(n):
            print(f"{ret_mtx[i, j]*100:>9.1f}%", end="")
        print()

    # Aggregate off-diagonal stats
    off_diag = np.abs(cos_mtx[~np.eye(n, dtype=bool)])
    off_diag_ret = ret_mtx[~np.eye(n, dtype=bool)]
    print(f"\n--- Off-diagonal aggregate ---")
    print(f"|cos| mean: {off_diag.mean():.4f}  max: {off_diag.max():.4f}  min: {off_diag.min():.4f}")
    print(f"retention mean: {off_diag_ret.mean()*100:.1f}%  min: {off_diag_ret.min()*100:.1f}%")

    # Verdict per pair (threshold |cos| < 0.2 and retention > 70%)
    print(f"\n--- Pairwise verdict (threshold |cos|<0.2 AND retention>70%) ---")
    for i in range(n):
        for j in range(i+1, n):
            c = abs(cos_mtx[i, j])
            r = ret_mtx[i, j]
            pass_cos = c < 0.2
            pass_ret = r > 0.70
            verdict = "PASS" if (pass_cos and pass_ret) else "FAIL"
            print(f"  {labels[i]:>4} ⊥ {labels[j]:<4}  |cos|={c:.4f} ({'✓' if pass_cos else '✗'})  "
                  f"retention={r*100:.1f}% ({'✓' if pass_ret else '✗'})  [{verdict}]")

    return {
        "labels": labels,
        "corpora": [vectors[l]["name"] for l in labels],
        "layer": layer,
        "cos_matrix": cos_mtx.tolist(),
        "ret_matrix": ret_mtx.tolist(),
        "off_diag_cos_mean": float(off_diag.mean()),
        "off_diag_cos_max": float(off_diag.max()),
        "off_diag_retention_mean": float(off_diag_ret.mean()),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=["qwen3-4b", "gemma-4-E4B-it"])
    # CC corpus default per model:
    #   qwen3-4b  -> "triplets" (50 hand-written; the empirically validated
    #                v_CC used in F92/F93/F94/F95/F96)
    #   gemma-4-E4B-it -> "triplets-combined" (166; we have no prior Gemma
    #                vectors, so the larger combined corpus is gold)
    ap.add_argument("--cc-corpus", default=None,
                    help="Default: triplets for qwen3-4b, triplets-combined for gemma")
    ap.add_argument("--ih-corpus", default="triplets-intellectual-humility")
    ap.add_argument("--layers", default="all",
                    help="comma-separated layer indices, or 'all' (default)")
    ap.add_argument("--matrix-mode", action="store_true",
                    help="Run pairwise matrix across multiple vectors (for 4-virtue MVE)")
    ap.add_argument("--corpora", nargs="+", default=None,
                    help="(matrix-mode only) list of corpus names to compare, e.g. "
                         "--corpora triplets triplets-intellectual-humility "
                         "mvp-combined/triplets-evidence-grounding mvp-combined/triplets-reasoning-transparency")
    ap.add_argument("--matrix-layer", type=int, default=None,
                    help="(matrix-mode only) single layer to evaluate at (default: 20 for qwen, 14 for gemma)")
    args = ap.parse_args()

    if args.matrix_mode:
        if args.corpora is None:
            # Default 4-virtue matrix
            if args.model == "qwen3-4b":
                args.corpora = [
                    "triplets",
                    "triplets-intellectual-humility",
                    "mvp-combined/triplets-evidence-grounding",
                    "mvp-combined/triplets-reasoning-transparency",
                ]
            else:
                args.corpora = [
                    "triplets-combined",
                    "triplets-intellectual-humility",
                    "mvp-combined/triplets-evidence-grounding",
                    "mvp-combined/triplets-reasoning-transparency",
                ]
        if args.matrix_layer is None:
            args.matrix_layer = 20 if args.model == "qwen3-4b" else 14

        result = run_matrix_mode(args.model, args.corpora, args.matrix_layer)
        if result:
            out_path = RESULTS_DIR / f"mve_matrix_{args.model}_L{args.matrix_layer}.json"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            json.dump(result, open(out_path, "w"), indent=2)
            print(f"\nMatrix results saved: {out_path}")
        return

    num_layers = 36 if args.model == "qwen3-4b" else 42
    if args.layers == "all":
        layers = list(range(num_layers))
    else:
        layers = [int(x) for x in args.layers.split(",")]

    # Resolve CC corpus default per model
    if args.cc_corpus is None:
        args.cc_corpus = "triplets" if args.model == "qwen3-4b" else "triplets-combined"

    print(f"\n{'='*72}")
    print(f"MVE Gate Tests — {args.model}")
    print(f"  CC corpus: {args.cc_corpus}")
    print(f"  IH corpus: {args.ih_corpus}")
    print(f"  layers: {layers}")
    print(f"{'='*72}\n")

    rows = []
    missing = []
    for layer in layers:
        v_cc = load_vector(args.model, args.cc_corpus, layer)
        v_ih = load_vector(args.model, args.ih_corpus, layer)
        if v_cc is None or v_ih is None:
            missing.append((layer, v_cc is None, v_ih is None))
            continue

        # Test C: cosine similarity (informational)
        cos = cos_sim(v_cc, v_ih)

        # Test B prep: orthogonal projection of v_CC relative to v_IH
        v_cc_orth = orthogonalise(v_cc, v_ih)
        # Efficacy retention proxy: fraction of original v_CC magnitude preserved after projection
        retention = float(np.linalg.norm(v_cc_orth) / (np.linalg.norm(v_cc) + 1e-12))

        # Also report norms
        rows.append({
            "layer": layer,
            "cos_sim": cos,
            "v_cc_norm": float(np.linalg.norm(v_cc)),
            "v_ih_norm": float(np.linalg.norm(v_ih)),
            "v_cc_orth_norm": float(np.linalg.norm(v_cc_orth)),
            "cc_retention_geometric": retention,
        })

    if missing:
        print(f"WARNING: {len(missing)} layers missing vectors:")
        for layer, cc_m, ih_m in missing[:5]:
            print(f"  layer {layer}: cc_missing={cc_m} ih_missing={ih_m}")
        if len(missing) > 5:
            print(f"  ... and {len(missing)-5} more")
        print()

    if not rows:
        print("No layers with both vectors. Cannot compute tests.")
        sys.exit(1)

    # Summary
    print(f"{'layer':>6} {'cos(CC,IH)':>12} {'|CC|':>8} {'|IH|':>8} {'|CC⊥IH|':>10} {'CC retention':>13}")
    print("-" * 72)
    for r in rows:
        print(f"{r['layer']:>6} {r['cos_sim']:>12.4f} {r['v_cc_norm']:>8.2f} "
              f"{r['v_ih_norm']:>8.2f} {r['v_cc_orth_norm']:>10.2f} "
              f"{r['cc_retention_geometric']*100:>11.1f}%")

    # Aggregate
    cos_vals = np.array([r["cos_sim"] for r in rows])
    ret_vals = np.array([r["cc_retention_geometric"] for r in rows])
    print()
    print(f"--- Aggregate across {len(rows)} layers ---")
    print(f"cos(v_CC, v_IH):         mean={cos_vals.mean():.4f}  "
          f"min={cos_vals.min():.4f}  max={cos_vals.max():.4f}  "
          f"|mean|={np.abs(cos_vals).mean():.4f}")
    print(f"CC retention after ⊥:    mean={ret_vals.mean()*100:.1f}%  "
          f"min={ret_vals.min()*100:.1f}%  max={ret_vals.max()*100:.1f}%")
    print()

    # Test C verdict (informational)
    abs_mean_cos = float(np.abs(cos_vals).mean())
    print(f"Test C (informational): |cos| mean = {abs_mean_cos:.4f}")
    if abs_mean_cos < 0.2:
        print("  -> Vectors are near-orthogonal. Strong prior for separate dimensions.")
    elif abs_mean_cos < 0.5:
        print("  -> Vectors are partially aligned. Behavioural test (Test B) is decisive.")
    elif abs_mean_cos < 0.8:
        print("  -> Vectors are substantially aligned. Likely same-axis with noise.")
    else:
        print("  -> Vectors are highly aligned. Likely near-antipodal on one axis.")

    # Test B geometric proxy (a stronger test requires behavioural AIME run)
    print()
    print(f"Test B geometric proxy (CC retention after ⊥ to IH):")
    print(f"  Threshold: 70% geometric retention at the best-layer candidate")
    # Suggested best layers: middle stack, matching prior Qwen3-4B sweet spots
    if args.model == "qwen3-4b":
        sweet_spots = [20, 22]
    else:
        sweet_spots = [24, 26, 28]
    for l in sweet_spots:
        r = next((r for r in rows if r["layer"] == l), None)
        if r is None:
            continue
        gate = "PASS" if r["cc_retention_geometric"] >= 0.70 else "FAIL"
        print(f"  layer {l}: retention={r['cc_retention_geometric']*100:.1f}%  [{gate}]")

    # Save full table
    out_path = RESULTS_DIR / f"mve_gate_{args.model}.json"
    json.dump({
        "model": args.model,
        "cc_corpus": args.cc_corpus,
        "ih_corpus": args.ih_corpus,
        "layers": rows,
        "summary": {
            "cos_mean": float(cos_vals.mean()),
            "cos_abs_mean": abs_mean_cos,
            "retention_mean": float(ret_vals.mean()),
            "retention_min": float(ret_vals.min()),
            "retention_max": float(ret_vals.max()),
            "layers_with_both": len(rows),
            "layers_missing": len(missing),
        },
    }, open(out_path, "w"), indent=2)
    print(f"\nFull results: {out_path}")
    print()
    print("Test A (abstention benchmark) requires a separate generation run.")
    print("After this script:")
    print(f"  python3 run_benchmark.py --benchmark abstention --n all "
          f"--condition steered --vector IH --alpha 12 --label steered_IH_L20_a12")
    print("  (requires IH vector to be registered in run_benchmark.py VECTORS dict)")


if __name__ == "__main__":
    main()
