"""
4×4 specificity matrix orchestrator.

Runs the 16-cell specificity test per docs/eg-rt-eval-spec.md §5:

         AIME-42  Abstention  EG-eval  RT-eval
  v_CC    diagonal  off        off     off
  v_IH    off       diagonal   off     off
  v_EG    off       off        diagonal off
  v_RT    off       off        off     diagonal

Each cell: generate N prompts (baseline + steered), score every generation
with all 4 scorers (cc-hedging, ih-abstention, eg, rt), output per-cell CSV
plus aggregated summary.

Usage (on GCP VM after extraction + α-sweep):
    python specificity_matrix.py \
        --model qwen3-4b \
        --vectors L20 IH_L20 EG_L20 RT_L22 \
        --alphas  12  12    12    14 \
        --output-dir results/specificity_matrix

For just one model, one pass. Run twice (Qwen + Gemma) for full cross-model.

Strategy: invokes run_benchmark.py as subprocess for each cell, then reads
saved per-item JSONs and applies all 4 scorers. Avoids re-implementing
model/hook infrastructure.
"""
from __future__ import annotations
import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

# Local imports
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "benchmarks"))
from eg_scorer import score_eg  # noqa: E402
from rt_scorer import score_rt  # noqa: E402


EVALS = ["aime", "abstention", "eg-eval", "rt-eval"]
EVAL_TO_DIAGONAL_VECTOR = {
    "aime": "CC",       # v_CC is the CC-eval diagonal
    "abstention": "IH",
    "eg-eval": "EG",
    "rt-eval": "RT",
}


def score_cc_hedging(text: str) -> float:
    """Lightweight CC-eval scorer: count hedging / confidence markers.

    Simple proxy; the full CC behavioral signal uses AIME correctness +
    abstention-quality separately. This is used as an OFF-DIAGONAL scorer
    on EG-eval and RT-eval generations (does v_EG / v_RT inadvertently
    increase hedging frequency?).
    """
    import re
    hedges = [
        r"\bI(?:'m| am) not (?:sure|certain|confident)\b",
        r"\bI (?:think|believe|suspect|guess)\b",
        r"\bperhaps\b",
        r"\bprobably\b",
        r"\bpossibly\b",
        r"\bit (?:seems|appears|might be)\b",
        r"\bon balance\b",
        r"\bto some extent\b",
        r"\bwith (?:moderate|low|some) confidence\b",
        r"\bmight\b",
        r"\bmay\b",
        r"\bcould (?:be|suggest)\b",
    ]
    tokens = len(text.split())
    if tokens == 0:
        return 0.0
    count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in hedges)
    return count / tokens * 1000.0


def score_ih_abstention(text: str, prompt: str = "") -> float:
    """Lightweight IH-eval scorer: abstention-marker frequency.

    For cross-eval use (v_EG on abstention-bench should NOT increase
    abstention rate beyond v_CC baseline).
    """
    import re
    abstention_markers = [
        r"\bI don'?t (?:know|have (?:information|data))\b",
        r"\bI (?:cannot|can'?t|am unable to) (?:confirm|verify|answer)\b",
        r"\binsufficient (?:information|data|evidence)\b",
        r"\bI (?:don'?t have|lack) (?:this|that|the) (?:information|data|fact)\b",
        r"\bthis (?:question|premise) (?:is not|appears) (?:well[- ]?formed|coherent)\b",
        r"\bthe premise (?:is false|does not hold|is incorrect)\b",
        r"\bI (?:would need|need) more (?:context|information|detail)\b",
        r"\bwithout (?:more |additional )?(?:context|information|specifics)\b",
    ]
    tokens = len(text.split())
    if tokens == 0:
        return 0.0
    count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in abstention_markers)
    return count / tokens * 1000.0


def run_cell(model: str, vector: str, alpha: float, eval_name: str,
             n_prompts: int, out_root: Path,
             label_suffix: str = "") -> Path:
    """Run one cell of the matrix via run_benchmark.py subprocess.

    Returns the path to the per-cell result directory (containing per-item JSONs).
    """
    if vector == "baseline":
        cond = "baseline"
        label = f"baseline_{eval_name}{label_suffix}"
        cmd = [
            sys.executable, str(HERE / "run_benchmark.py"),
            "--model", model,
            "--benchmark", eval_name,
            "--n", str(n_prompts),
            "--condition", "baseline",
            "--label", label,
        ]
    else:
        cond = "steered"
        label = f"steered_{vector}_a{alpha:.0f}_{eval_name}{label_suffix}"
        cmd = [
            sys.executable, str(HERE / "run_benchmark.py"),
            "--model", model,
            "--benchmark", eval_name,
            "--n", str(n_prompts),
            "--condition", "steered",
            "--vector", vector,
            "--alpha", str(alpha),
            "--label", label,
        ]
    print(f"\n=== Running cell: model={model} vector={vector} α={alpha} eval={eval_name} ===")
    print(f"    cmd: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"    FAILED: {e}")
        return None

    # run_benchmark.py writes to results/benchmark_probe/{eval_name}/{cond}/{item_id}.json
    cell_dir = HERE / "results" / "benchmark_probe" / eval_name / cond
    return cell_dir


def aggregate_cell(cell_dir: Path, model: str, vector: str, alpha: float,
                   eval_name: str, label: str) -> list:
    """Read per-item JSONs from a cell, apply all 4 scorers, return list of rows."""
    if cell_dir is None or not cell_dir.exists():
        return []

    rows = []
    for jf in sorted(cell_dir.glob(f"*{label}*.json")):
        try:
            data = json.loads(jf.read_text())
        except json.JSONDecodeError:
            continue
        # Expected fields: item_id, prompt, response (with 'thinking' + 'answer' or just text)
        item_id = data.get("item_id", jf.stem)
        prompt = data.get("prompt", "")
        response = data.get("response", {})
        # Combine thinking + answer if structured; else use whole response text
        if isinstance(response, dict):
            text = (response.get("thinking", "") + "\n" + response.get("answer", "")).strip()
        else:
            text = str(response)

        eg = score_eg(text)
        rt = score_rt(text)
        cc = score_cc_hedging(text)
        ih = score_ih_abstention(text, prompt)

        rows.append({
            "model": model,
            "vector": vector,
            "alpha": alpha,
            "eval": eval_name,
            "item_id": item_id,
            "prompt": prompt[:200],
            "tokens": eg.tokens,
            "eg_score": round(eg.score, 3),
            "rt_score": round(rt.score, 3),
            "cc_hedging_score": round(cc, 3),
            "ih_abstention_score": round(ih, 3),
            "generation_preview": text[:300].replace("\n", " "),
        })
    return rows


def write_rows_csv(rows: list, out_path: Path):
    if not rows:
        print(f"No rows to write for {out_path}")
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  wrote {len(rows)} rows to {out_path}")


def summarise_matrix(all_rows: list, out_path: Path):
    """Aggregate per-cell means for the 4×4 matrix summary."""
    import statistics
    # Group rows by (model, vector, eval)
    cells = {}
    for r in all_rows:
        key = (r["model"], r["vector"], r["eval"])
        cells.setdefault(key, []).append(r)

    summary_rows = []
    for (model, vector, eval_name), cell_rows in sorted(cells.items()):
        eg_scores = [r["eg_score"] for r in cell_rows]
        rt_scores = [r["rt_score"] for r in cell_rows]
        cc_scores = [r["cc_hedging_score"] for r in cell_rows]
        ih_scores = [r["ih_abstention_score"] for r in cell_rows]

        def mean_std(xs):
            if not xs:
                return None, None
            if len(xs) == 1:
                return xs[0], 0.0
            return statistics.mean(xs), statistics.stdev(xs)

        m_eg, s_eg = mean_std(eg_scores)
        m_rt, s_rt = mean_std(rt_scores)
        m_cc, s_cc = mean_std(cc_scores)
        m_ih, s_ih = mean_std(ih_scores)

        summary_rows.append({
            "model": model,
            "vector": vector,
            "eval": eval_name,
            "n": len(cell_rows),
            "eg_mean": round(m_eg, 2) if m_eg is not None else None,
            "eg_std": round(s_eg, 2) if s_eg is not None else None,
            "rt_mean": round(m_rt, 2) if m_rt is not None else None,
            "rt_std": round(s_rt, 2) if s_rt is not None else None,
            "cc_hedging_mean": round(m_cc, 2) if m_cc is not None else None,
            "ih_abstention_mean": round(m_ih, 2) if m_ih is not None else None,
        })

    fieldnames = list(summary_rows[0].keys()) if summary_rows else []
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"\nSummary matrix written: {out_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--vectors", nargs="+", required=True,
                    help="Vector keys in run_benchmark.py VECTORS registry, e.g. L20 IH_L20 EG_L20 RT_L22")
    ap.add_argument("--alphas", type=float, nargs="+", required=True,
                    help="α values per vector (same order as --vectors)")
    ap.add_argument("--evals", nargs="+", default=EVALS,
                    help="Evals to run (default: all 4)")
    ap.add_argument("--n-prompts", type=int, default=24,
                    help="Prompts per eval per cell (default 24)")
    ap.add_argument("--output-dir", default="results/specificity_matrix",
                    help="Output directory for per-cell CSVs + summary")
    ap.add_argument("--skip-generation", action="store_true",
                    help="Skip the subprocess runs; just aggregate existing saved JSONs")
    args = ap.parse_args()

    if len(args.vectors) != len(args.alphas):
        print(f"ERROR: --vectors and --alphas must have the same count")
        sys.exit(1)

    out_root = HERE / args.output_dir
    out_root.mkdir(parents=True, exist_ok=True)

    all_rows = []

    # Step 1: baseline runs (one per eval, no steering)
    for eval_name in args.evals:
        if not args.skip_generation:
            cell_dir = run_cell(args.model, "baseline", 0.0, eval_name,
                                args.n_prompts, out_root,
                                label_suffix=f"_{args.model}")
        else:
            cell_dir = HERE / "results" / "benchmark_probe" / eval_name / "baseline"
        label = f"baseline_{eval_name}_{args.model}"
        rows = aggregate_cell(cell_dir, args.model, "baseline", 0.0, eval_name, label)
        all_rows.extend(rows)

    # Step 2: steered runs (each vector × each eval = 16 cells for 4-vector, 4-eval case)
    for vector, alpha in zip(args.vectors, args.alphas):
        for eval_name in args.evals:
            if not args.skip_generation:
                cell_dir = run_cell(args.model, vector, alpha, eval_name,
                                    args.n_prompts, out_root,
                                    label_suffix=f"_{args.model}")
            else:
                cell_dir = HERE / "results" / "benchmark_probe" / eval_name / "steered"
            label = f"steered_{vector}_a{alpha:.0f}_{eval_name}_{args.model}"
            rows = aggregate_cell(cell_dir, args.model, vector, alpha, eval_name, label)
            all_rows.extend(rows)

    # Per-cell CSVs
    by_cell = {}
    for r in all_rows:
        key = f"{r['model']}_{r['vector']}_{r['eval']}"
        by_cell.setdefault(key, []).append(r)
    for key, rows in by_cell.items():
        write_rows_csv(rows, out_root / f"{key}.csv")

    # All rows combined (for manual review)
    write_rows_csv(all_rows, out_root / f"all_generations_{args.model}.csv")

    # Summary (aggregated means per cell)
    summarise_matrix(all_rows, out_root / f"summary_{args.model}.csv")

    print(f"\nDone. Output in {out_root}")
    print(f"Total rows: {len(all_rows)}")
    print(f"Next step: hand-review {out_root}/all_generations_{args.model}.csv per docs/eg-rt-eval-spec.md §6")


if __name__ == "__main__":
    main()
