"""
Calibrate EG + RT scorers against the mvp-combined/ corpus.

Per docs/eg-rt-eval-spec.md §3.5 + §4.5, scorers must separate virtuous from
deficiency-non-virtuous passages by ≥5 points mean difference before extraction
runs are kicked off.

Expected (target):
  EG virtuous mean ≥ +10 (markers per 1000 tokens)
  EG deficiency-nonvirt mean ≤ +2
  EG excess-nonvirt mean variable; hand-review flags caricature

  RT virtuous mean ≥ +10
  RT deficiency-nonvirt mean ≤ +2
  RT excess-nonvirt mean variable

Usage:
    python calibrate_scorers.py

Reads fact-pack.md to determine each triplet's declared failure_mode so we can
report virtuous / deficiency-nonvirt / excess-nonvirt separately.

Exit codes:
  0: calibration passes (virtuous > deficiency by ≥5 on both scorers)
  1: calibration fails (scorer needs refinement)
"""
from __future__ import annotations
import re
import sys
import statistics
from pathlib import Path

# Allow running from mvp/ or anywhere
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "benchmarks"))

# Import scorers directly to avoid benchmarks/__init__.py pulling in HF datasets
from eg_scorer import score_eg  # noqa: E402
from rt_scorer import score_rt  # noqa: E402

MVP_COMBINED = HERE.parent / "corpus" / "mvp-combined"
EG_DIR = MVP_COMBINED / "triplets-evidence-grounding"
RT_DIR = MVP_COMBINED / "triplets-reasoning-transparency"


def parse_fact_pack(fp_path: Path) -> dict:
    """Extract failure_mode and correctness_confound from fact-pack YAML frontmatter."""
    text = fp_path.read_text()
    out = {"failure_mode": None, "correctness_confound": None}
    m = re.search(r"^failure_mode:\s*(\S+)", text, re.MULTILINE)
    if m:
        out["failure_mode"] = m.group(1).strip()
    m = re.search(r"^correctness_confound:\s*(\S+)", text, re.MULTILINE)
    if m:
        out["correctness_confound"] = m.group(1).strip()
    return out


def score_corpus(corpus_dir: Path, scorer_fn) -> dict:
    """Score all passages in a corpus; return per-type mean scores + per-triplet details."""
    results = {
        "virtuous": [],
        "nonvirt_excess": [],
        "nonvirt_deficiency": [],
        "neutral": [],
        "per_triplet": [],
    }
    for td in sorted(corpus_dir.iterdir()):
        if not td.is_dir():
            continue
        fp = td / "fact-pack.md"
        if not fp.exists():
            continue
        meta = parse_fact_pack(fp)
        failure = meta.get("failure_mode", "unknown")

        n_path = td / "neutral.md"
        v_path = td / "virtuous.md"
        nv_path = td / "non-virtuous.md"
        if not all(p.exists() for p in [n_path, v_path, nv_path]):
            continue

        n_score = scorer_fn(n_path.read_text())
        v_score = scorer_fn(v_path.read_text())
        nv_score = scorer_fn(nv_path.read_text())

        results["virtuous"].append(v_score.score)
        results["neutral"].append(n_score.score)

        if failure == "excess":
            results["nonvirt_excess"].append(nv_score.score)
        elif failure == "deficiency":
            results["nonvirt_deficiency"].append(nv_score.score)

        results["per_triplet"].append({
            "id": td.name,
            "failure_mode": failure,
            "n_score": n_score.score,
            "v_score": v_score.score,
            "nv_score": nv_score.score,
        })
    return results


def summarise(results: dict, label: str) -> dict:
    def mean_std(xs):
        if not xs:
            return None, None
        if len(xs) < 2:
            return xs[0], 0.0
        return statistics.mean(xs), statistics.stdev(xs)

    v_mean, v_std = mean_std(results["virtuous"])
    n_mean, n_std = mean_std(results["neutral"])
    e_mean, e_std = mean_std(results["nonvirt_excess"])
    d_mean, d_std = mean_std(results["nonvirt_deficiency"])

    print(f"\n=== {label} ===")
    print(f"  N virtuous = {len(results['virtuous'])}, N neutral = {len(results['neutral'])}")
    print(f"  N nonvirt-excess = {len(results['nonvirt_excess'])}, N nonvirt-deficiency = {len(results['nonvirt_deficiency'])}")
    print()
    print(f"  Virtuous mean:             {v_mean:+.2f} (std {v_std:.2f})" if v_mean is not None else "  Virtuous: n/a")
    print(f"  Neutral mean:              {n_mean:+.2f} (std {n_std:.2f})" if n_mean is not None else "  Neutral: n/a")
    print(f"  Non-virtuous excess mean:  {e_mean:+.2f} (std {e_std:.2f})" if e_mean is not None else "  Non-virtuous excess: n/a")
    print(f"  Non-virtuous def. mean:    {d_mean:+.2f} (std {d_std:.2f})" if d_mean is not None else "  Non-virtuous deficiency: n/a")

    separation = None
    if v_mean is not None and d_mean is not None:
        separation = v_mean - d_mean
        verdict = "PASS" if separation >= 5.0 else "FAIL"
        print(f"\n  Separation (virt − def): {separation:+.2f}   [{verdict}, target ≥ +5.0]")

    return {
        "virtuous_mean": v_mean,
        "neutral_mean": n_mean,
        "nonvirt_excess_mean": e_mean,
        "nonvirt_deficiency_mean": d_mean,
        "separation": separation,
    }


def print_outliers(results: dict, label: str, n: int = 5):
    """Print top-5 lowest-scoring virtuous + top-5 highest-scoring deficiency-nonvirt as hand-review candidates."""
    triplets = results["per_triplet"]
    virt_low = sorted(triplets, key=lambda r: r["v_score"])[:n]
    def_high = sorted([r for r in triplets if r["failure_mode"] == "deficiency"],
                      key=lambda r: -r["nv_score"])[:n]

    print(f"\n=== {label}: hand-review candidates ===")
    print(f"\nLowest-scoring virtuous passages (expected high; if low, scorer or corpus issue):")
    for r in virt_low:
        print(f"  {r['v_score']:+6.2f}  {r['id']}")

    print(f"\nHighest-scoring deficiency-nonvirt (expected low; if high, scorer false-positive):")
    for r in def_high:
        print(f"  {r['nv_score']:+6.2f}  {r['id']}")


def main():
    print("=" * 70)
    print("Phronesis EG + RT scorer calibration")
    print("Source: docs/eg-rt-eval-spec.md §3.5 + §4.5")
    print("Target: virtuous mean − deficiency-nonvirt mean ≥ +5 points")
    print("=" * 70)

    eg_results = score_corpus(EG_DIR, score_eg)
    rt_results = score_corpus(RT_DIR, score_rt)

    eg_summary = summarise(eg_results, "EG scorer on triplets-evidence-grounding (40 triplets)")
    rt_summary = summarise(rt_results, "RT scorer on triplets-reasoning-transparency (40 triplets)")

    print_outliers(eg_results, "EG")
    print_outliers(rt_results, "RT")

    print("\n" + "=" * 70)
    print("Calibration summary")
    print("=" * 70)

    eg_pass = eg_summary["separation"] is not None and eg_summary["separation"] >= 5.0
    rt_pass = rt_summary["separation"] is not None and rt_summary["separation"] >= 5.0

    print(f"  EG scorer:  {'PASS' if eg_pass else 'FAIL'}  (separation {eg_summary['separation']:+.2f})")
    print(f"  RT scorer:  {'PASS' if rt_pass else 'FAIL'}  (separation {rt_summary['separation']:+.2f})")

    if eg_pass and rt_pass:
        print("\nCalibration PASSED. Safe to proceed to extraction.")
        return 0
    else:
        print("\nCalibration FAILED. Refine scorer markers and re-run before extraction.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
