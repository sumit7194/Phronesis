"""
α/layer pre-sweep — finds optimal (α, layer) per vector before 4×4 specificity matrix.

Per docs/eg-rt-eval-spec.md §5.2 "best case for diagonal" protocol:

  For each vector V:
    Try every α × layer combination on ~5 prompts from V's target eval
    Compute the diagonal effect (steered_score − baseline_score) in V's
    target-virtue scorer
    Pick the (α, layer) that MAXIMISES this diagonal effect
    Use that same (α, layer) for all off-diagonal cells involving V

Output: mvp/results/alpha_sweep/{model}.json — map vector → optimal (α, layer)

This is the "generous to the diagonal" choice (§5.2): we give each vector
its best shot at producing a diagonal win, then test whether off-diagonal
suppression holds at that same generous α.

Usage:
    python run_alpha_sweep.py --model qwen3-4b
    python run_alpha_sweep.py --model gemma-4-E4B-it

  Optional:
    --prompts-per-eval 5        (default 5; lower for faster sweeps, higher for stabler picks)
    --alphas 4 8 12 16 20       (default from config)
    --layers-qwen 18 20 22 25   (default from config)
    --layers-gemma 14 18 22 26  (default from config)
    --skip-baseline             (if baselines already produced for this model × eval)
    --dry-run                   (print plan but don't spawn run_benchmark.py subprocesses)

GPU budget (observed from Day 16 extraction):
    ~24 generations per (vector × α × layer) = 5 prompts × 4 α × 4 layers = 80 per vector
    × 4 vectors × 2 evals per vector × 2 models = ~1280 generations total, but
    many reuse baseline generations. Actual ~800-1000 generations. At ~30s each
    on L4, total ~8h across both models.

Dependencies:
    - mvp/benchmarks/eg_scorer.py, rt_scorer.py (already built)
    - mvp/analysis/config.yaml (virtues, evals, alphas, layers)
    - Extracted vectors in mvp/results/vectors/{model}/{corpus}/generation/
    - run_benchmark.py VECTORS registry entries for v_EG_L*, v_RT_L*, etc.
"""
from __future__ import annotations
import argparse
import gzip
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# ─── Coherence gate (per phase5-plan §3.0, FM-8 mitigation) ───────────────
# Reject any output that:
#   (a) opens <think> and never closes it (unfinished thinking)
#   (b) compresses to <30% via gzip (catches repetition loops; FM-8)
#   (c) has any 80-char span repeated ≥3 times verbatim (catches mode collapse)

def _is_degenerate_loop(text: str, ratio_threshold: float = 0.30) -> bool:
    if len(text) < 400:
        return False
    raw = text.encode("utf-8", errors="ignore")
    compressed = gzip.compress(raw)
    return (len(compressed) / max(len(raw), 1)) < ratio_threshold


def _has_repeated_phrase(text: str, span: int = 80, repeats: int = 3) -> bool:
    if len(text) < span * repeats:
        return False
    seen: dict[str, int] = {}
    for i in range(0, len(text) - span, 5):  # stride 5 chars; sufficient
        chunk = text[i:i + span]
        seen[chunk] = seen.get(chunk, 0) + 1
        if seen[chunk] >= repeats:
            return True
    return False


def _is_unfinished_thinking(answer_text: str, thinking_text: str) -> bool:
    full = (thinking_text or "") + " " + (answer_text or "")
    has_open = "<think>" in full
    has_close = "</think>" in full
    return has_open and not has_close


def coherence_check(item: dict) -> tuple[bool, str]:
    """Return (coherent, reason). Reason is empty if coherent."""
    thinking = str(item.get("response_thinking", "") or "")
    answer = str(item.get("response_answer", "") or "")
    full = (thinking + " " + answer).strip()
    if _is_unfinished_thinking(answer, thinking):
        return False, "unclosed_think"
    if _is_degenerate_loop(full):
        return False, "loop_compression"
    if _has_repeated_phrase(full):
        return False, "repeated_phrase"
    return True, ""

import yaml

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "benchmarks"))

# Progress JSON for dashboard (written after every cell)
PROGRESS_PATH = HERE / "results" / "alpha_sweep_progress.json"


def write_progress(state: dict) -> None:
    """Atomic write of dashboard-readable progress state."""
    PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    state = {**state, "timestamp": datetime.utcnow().isoformat()}
    tmp = PROGRESS_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state))
    tmp.rename(PROGRESS_PATH)

# Scorers import — avoids pulling in the full benchmarks package
from eg_scorer import score_eg  # noqa: E402
from rt_scorer import score_rt  # noqa: E402


# Default α and layer grids — config overridable
DEFAULT_ALPHAS = [4, 8, 12, 16, 20]
DEFAULT_LAYERS_QWEN = [18, 20, 22, 25]
DEFAULT_LAYERS_GEMMA = [14, 18, 22, 26]

# Vector name convention in run_benchmark.py VECTORS registry
# Qwen: {virtue}_L{layer} — e.g. "EG_L20", "RT_L22", "IH_L20", and for CC "L20"
# Gemma: same for IH/EG/RT; CC uses "CC_L18" etc.
def vector_registry_key(virtue: str, layer: int, model: str) -> str:
    """Construct VECTORS registry key used by run_benchmark.py."""
    if virtue == "CC" and model == "qwen3-4b":
        return f"L{layer}"                 # legacy naming on Qwen
    return f"{virtue}_L{layer}"


def target_eval_for_virtue(virtue: str, config: dict) -> Optional[str]:
    """Return the eval name whose target_virtue == `virtue`."""
    for ev in config["evals"]:
        if ev["target_virtue"] == virtue:
            return ev["name"]
    return None


def load_virtue_scorer(virtue: str):
    """Return a scoring function `score(text: str) -> float` for the virtue's
    target behavior.

    For EG/RT we use the regex scorers. For CC and IH, we need the
    accuracy/abstention-rate, which is benchmark-specific and not a pure
    text-level function — we fall back to a hedging/abstention proxy.
    """
    if virtue == "EG":
        return lambda text: score_eg(text).score
    if virtue == "RT":
        return lambda text: score_rt(text).score
    if virtue == "CC":
        # For CC, the actual diagonal metric is AIME correctness. In the α-sweep
        # we're optimising the diagonal cell, so we NEED AIME. That's handled
        # externally via benchmark scoring — the sweep just measures a hedging
        # proxy as a fallback. Real answer: ingest AIME scoring.json outputs.
        return _score_cc_proxy
    if virtue == "IH":
        return _score_ih_proxy
    raise ValueError(f"Unknown virtue: {virtue}")


def _score_cc_proxy(text: str) -> float:
    """Lightweight CC proxy: count hedging markers. Use AIME correctness when available."""
    hedges = [
        r"\bI(?:'m| am) not (?:sure|certain)\b",
        r"\bI (?:think|believe)\b",
        r"\bperhaps\b", r"\bprobably\b", r"\bmight\b", r"\bmay\b",
    ]
    tokens = max(len(text.split()), 1)
    count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in hedges)
    return count / tokens * 1000.0


def _score_ih_proxy(text: str) -> float:
    """Lightweight IH proxy: count abstention markers."""
    markers = [
        r"\bI don'?t (?:know|have)\b",
        r"\b(?:cannot|can'?t) (?:confirm|verify)\b",
        r"\binsufficient (?:information|data)\b",
        r"\bthe premise (?:is false|does not hold)\b",
    ]
    tokens = max(len(text.split()), 1)
    count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in markers)
    return count / tokens * 1000.0


def run_benchmark_cell(
    model: str,
    eval_name: str,
    condition: str,            # "baseline" or "steered"
    vector: Optional[str],
    alpha: Optional[float],
    n_prompts: int,
    label: str,
    dry_run: bool = False,
) -> Path:
    """Spawn run_benchmark.py subprocess for one (model, eval, vector, α) cell.

    Returns the directory where run_benchmark.py writes its per-item JSONs:
        mvp/results/benchmark_probe/{eval_name}/{condition}/
    """
    out_dir = HERE / "results" / "benchmark_probe" / eval_name / condition
    if dry_run:
        print(f"  [DRY] {condition} {eval_name} vector={vector} α={alpha} n={n_prompts} → {label}")
        return out_dir

    cmd = [
        sys.executable, str(HERE / "run_benchmark.py"),
        "--model", model,
        "--benchmark", eval_name,
        "--n", str(n_prompts),
        "--condition", condition,
        "--label", label,
    ]
    if condition == "steered":
        cmd += ["--vector", vector, "--alpha", str(alpha)]

    print(f"  [run] {' '.join(cmd[2:])}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"  [FAIL] {e}")
    return out_dir


def read_cell_scores(cell_dir: Path, label: str, scorer_fn) -> list[float]:
    """Read every per-item JSON for this label, apply coherence gate, then score.

    run_benchmark.py writes to {OUT_ROOT}/{benchmark}/{label}/{item_id}.json. We accept
    either layout for back-compat:
      - {benchmark}/{label}/*.json          (canonical, current run_benchmark.py)
      - {benchmark}/{condition}/*{label}*.json (older convention)

    COHERENCE GATE (per phase5-plan §3.0, FM-8 mitigation):
    Items that fail any coherence check (unclosed <think>, gzip loop, or repeated
    phrase) are *excluded* from the returned scores. Rejection counts are printed
    so the operator can see whether a cell is degenerate.
    """
    candidates: list[Path] = []
    label_dir = cell_dir.parent / label
    if label_dir.exists() and label_dir.is_dir():
        candidates.extend(sorted(label_dir.glob("*.json")))
    if cell_dir.exists():
        candidates.extend(sorted(cell_dir.glob(f"*{label}*.json")))
    seen = set()
    scores = []
    n_total = 0
    rejections: dict[str, int] = {}
    for jf in candidates:
        if jf in seen:
            continue
        seen.add(jf)
        try:
            data = json.loads(jf.read_text())
        except json.JSONDecodeError:
            continue
        n_total += 1
        # Coherence gate
        ok, reason = coherence_check(data)
        if not ok:
            rejections[reason] = rejections.get(reason, 0) + 1
            continue
        # Score
        if "response_thinking" in data or "response_answer" in data:
            text = (str(data.get("response_thinking", "")) + " " + str(data.get("response_answer", ""))).strip()
        else:
            resp = data.get("response", {})
            if isinstance(resp, dict):
                text = (resp.get("thinking", "") + " " + resp.get("answer", "")).strip()
            else:
                text = str(resp)
        scores.append(scorer_fn(text))
    if rejections:
        rej_str = ", ".join(f"{k}={v}" for k, v in rejections.items())
        print(f"      [coherence] {label}: kept {len(scores)}/{n_total} (rejected: {rej_str})", flush=True)
    return scores


def sweep_for_vector(
    model: str,
    vector_virtue: str,   # one of "CC", "IH", "EG", "RT"
    config: dict,
    alphas: list[float],
    layers: list[int],
    n_prompts: int,
    skip_baseline: bool,
    dry_run: bool,
) -> dict:
    """Sweep α × layer for one vector on its target eval; return best (α, layer) + details.

    Returns:
        {
          "virtue": "EG",
          "target_eval": "eg-eval",
          "best_alpha": 12,
          "best_layer": 20,
          "best_delta": 11.4,
          "all_results": [{"alpha": ..., "layer": ..., "delta": ...}, ...],
          "baseline_mean": 2.1,
        }
    """
    target_eval = target_eval_for_virtue(vector_virtue, config)
    scorer = load_virtue_scorer(vector_virtue)

    print(f"\n=== Sweep: {model} × v_{vector_virtue} on {target_eval} ===")
    print(f"    Alphas: {alphas}   Layers: {layers}   n_prompts: {n_prompts}")

    total_cells = len(layers) * len(alphas)
    cells_done = 0

    def _push_progress(extra=None):
        st = {
            "phase": "alpha_sweep",
            "model": model,
            "virtue": vector_virtue,
            "target_eval": target_eval,
            "cells_done": cells_done,
            "total_cells": total_cells,
            "alphas": list(alphas),
            "layers": list(layers),
        }
        if extra:
            st.update(extra)
        write_progress(st)

    # Baseline (once per model × eval)
    _push_progress({"current": "baseline"})
    baseline_label = f"alpha_sweep_baseline_{model}_{target_eval}"
    baseline_dir = HERE / "results" / "benchmark_probe" / target_eval / "baseline"
    if not skip_baseline:
        run_benchmark_cell(model, target_eval, "baseline", None, None,
                           n_prompts, baseline_label, dry_run=dry_run)
    baseline_scores = [] if dry_run else read_cell_scores(baseline_dir, baseline_label, scorer)
    baseline_mean = sum(baseline_scores) / len(baseline_scores) if baseline_scores else 0.0

    all_results = []
    for layer in layers:
        v_key = vector_registry_key(vector_virtue, layer, model)
        for alpha in alphas:
            _push_progress({"current": f"L{layer} α={int(alpha)}", "current_layer": layer, "current_alpha": float(alpha)})
            label = f"alpha_sweep_{model}_v{vector_virtue}_L{layer}_a{int(alpha)}_{target_eval}"
            steered_dir = HERE / "results" / "benchmark_probe" / target_eval / "steered"
            run_benchmark_cell(model, target_eval, "steered", v_key, alpha,
                               n_prompts, label, dry_run=dry_run)
            scores = [] if dry_run else read_cell_scores(steered_dir, label, scorer)
            steered_mean = sum(scores) / len(scores) if scores else 0.0
            delta = steered_mean - baseline_mean
            all_results.append({
                "alpha": alpha, "layer": layer,
                "steered_mean": round(steered_mean, 3),
                "baseline_mean": round(baseline_mean, 3),
                "delta": round(delta, 3),
                "n_prompts": len(scores),
                "vector_key": v_key,
            })
            cells_done += 1
            best_so_far = max(all_results, key=lambda r: r["delta"])
            _push_progress({
                "current": f"L{layer} α={int(alpha)} done",
                "current_layer": layer,
                "current_alpha": float(alpha),
                "last_delta": round(delta, 3),
                "best_so_far": {"layer": best_so_far["layer"], "alpha": best_so_far["alpha"], "delta": best_so_far["delta"]},
            })
            print(f"    L{layer} α={alpha:>4}: Δ={delta:+.2f}  (steered={steered_mean:.2f} baseline={baseline_mean:.2f}, n={len(scores)})")

    # Pick best (α, layer) by max delta
    if not all_results or dry_run:
        best = None
    else:
        best = max(all_results, key=lambda r: r["delta"])
        print(f"  -> BEST: L{best['layer']} α={best['alpha']}  Δ={best['delta']:+.2f}")

    return {
        "virtue": vector_virtue,
        "target_eval": target_eval,
        "best_alpha": best["alpha"] if best else None,
        "best_layer": best["layer"] if best else None,
        "best_delta": best["delta"] if best else None,
        "baseline_mean": round(baseline_mean, 3),
        "all_results": all_results,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=["qwen3-4b", "gemma-4-E4B-it"])
    ap.add_argument("--config", default=str(HERE / "analysis" / "config.yaml"))
    ap.add_argument("--prompts-per-eval", type=int, default=5,
                    help="Number of prompts per eval to sweep on (default 5)")
    ap.add_argument("--alphas", type=float, nargs="+", default=DEFAULT_ALPHAS,
                    help=f"α values to sweep (default {DEFAULT_ALPHAS})")
    ap.add_argument("--layers-qwen", type=int, nargs="+", default=DEFAULT_LAYERS_QWEN)
    ap.add_argument("--layers-gemma", type=int, nargs="+", default=DEFAULT_LAYERS_GEMMA)
    ap.add_argument("--virtues", nargs="+", default=None,
                    help="Subset of virtues to sweep (default: all from config)")
    ap.add_argument("--skip-baseline", action="store_true",
                    help="Skip baseline runs (assume already produced)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print plan without spawning subprocesses")
    ap.add_argument("--output", default=None,
                    help="Output JSON path (default: mvp/results/alpha_sweep/{model}.json)")
    args = ap.parse_args()

    with open(args.config) as f:
        cfg = yaml.safe_load(f)

    layers = args.layers_qwen if args.model == "qwen3-4b" else args.layers_gemma
    all_virtues = [v["name"] for v in cfg["virtues"]]
    virtues = args.virtues or all_virtues

    print(f"\n{'='*72}")
    print(f"Phronesis α/layer pre-sweep — {args.model}")
    print(f"Virtues: {virtues}")
    print(f"Alphas: {args.alphas}   Layers: {layers}")
    print(f"Prompts per eval: {args.prompts_per_eval}")
    print(f"Dry-run: {args.dry_run}")
    print(f"{'='*72}")

    results = {}
    for virtue in virtues:
        r = sweep_for_vector(
            args.model, virtue, cfg,
            args.alphas, layers, args.prompts_per_eval,
            args.skip_baseline, args.dry_run,
        )
        results[virtue] = r

    # Save
    out_path = Path(args.output) if args.output else HERE / "results" / "alpha_sweep" / f"{args.model}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not args.dry_run:
        with open(out_path, "w") as f:
            json.dump({
                "model": args.model,
                "n_prompts": args.prompts_per_eval,
                "alphas_swept": args.alphas,
                "layers_swept": layers,
                "results_by_virtue": results,
            }, f, indent=2)
        print(f"\nSaved: {out_path}")

    # Summary
    print(f"\n=== Summary: best (α, layer) per vector ({args.model}) ===")
    for virtue, r in results.items():
        if r["best_alpha"] is None:
            print(f"  v_{virtue}: no results (dry-run or sweep failed)")
        else:
            print(f"  v_{virtue} ({r['target_eval']}): α={r['best_alpha']}, L{r['best_layer']}, Δ={r['best_delta']:+.2f}")


if __name__ == "__main__":
    main()
