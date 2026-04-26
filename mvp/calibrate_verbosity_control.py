"""
Calibrate the verbosity-control negative-control corpus.

Per docs/negative-control-corpus-handoff.md §5.1, this script computes three
metrics across the 40 triplets in corpus/mvp-combined/triplets-verbosity-control/
and emits a PASS/FAIL verdict with per-triplet diagnostics.

Metrics:
  - Word count separation: mean(verbose_wc) - mean(terse_wc).  Target >= 120.
  - Step-marker separation: mean(verbose_step) - mean(terse_step).  Target >= 4.
  - Hedge-density invariance: |mean(verbose_hedge_per_1000)
        - mean(terse_hedge_per_1000)|.  Target <= 1.0.

Per-passage targets:
  - virtuous (verbose): 250-300 words
  - non-virtuous (terse): 100-130 words
  - neutral: 180-220 words

A triplet is flagged for diagnostics if:
  - any passage word count is outside its target band, OR
  - hedge-density delta between verbose and terse > 2.0, OR
  - step-marker delta between verbose and terse < 2.

Modeled on calibrate_scorers.py.

Exit codes:
  0: calibration PASSES (all three corpus-level thresholds met).
  1: calibration FAILS.

Usage:
    python calibrate_verbosity_control.py
"""
from __future__ import annotations
import re
import sys
import statistics
from pathlib import Path

HERE = Path(__file__).parent
CORPUS_ROOT = HERE.parent / "corpus" / "mvp-combined" / "triplets-verbosity-control"

# Word-count bands per passage role.
TARGETS = {
    "virtuous": (250, 300),     # verbose
    "non-virtuous": (100, 130), # terse
    "neutral": (180, 220),
}

# Step-marker pattern per handoff §5.1.
STEP_MARKER_PATTERN = re.compile(
    r"\b(Step|First|Second|Third|Fourth|Fifth|Therefore|Thus|Hence"
    r"|In summary|To summarize|Let us|Consider|Suppose|Note that)\b"
)

# Hedge-marker pattern.  Mirrors the hedge family used in calibrate_scorers.py /
# CC scoring: linguistic markers of uncertainty, probability, or qualified claim.
HEDGE_PATTERN = re.compile(
    r"\b(may|might|could|perhaps|possibly|likely|unlikely|seems?|appears?"
    r"|suggest(?:s|ed|ing)?|approximately|roughly|about|around|nearly"
    r"|tend(?:s|ed|ing)? to|tends? to|somewhat|relatively|fairly|mostly"
    r"|in some cases|in many cases|under (?:most|some|certain) (?:conditions|circumstances)"
    r"|usually|often|typically|generally|broadly|on average"
    r"|estimated?|estimates?|estimating)\b",
    re.IGNORECASE,
)

# Strip the leading H1 line and any trailing YAML metadata block from a passage
# file so the body is what gets counted.
H1_LINE = re.compile(r"^#\s+.*\n", re.MULTILINE)
TRAILING_YAML = re.compile(r"\n---\n.*?\n---\s*$", re.DOTALL)


def extract_body(passage_text: str) -> str:
    """Drop the H1 header and trailing YAML metadata block; keep the prose."""
    text = passage_text
    # Strip the leading H1 (only the first one).
    m = H1_LINE.search(text)
    if m and m.start() == 0:
        text = text[m.end():]
    # Strip a trailing YAML block (--- ... ---) at the very end.
    text = TRAILING_YAML.sub("", text).strip()
    return text


def count_words(text: str) -> int:
    return len(re.findall(r"\b\w+(?:[-']\w+)*\b", text))


def count_step_markers(text: str) -> int:
    return len(STEP_MARKER_PATTERN.findall(text))


def count_hedges(text: str) -> int:
    return len(HEDGE_PATTERN.findall(text))


def hedge_per_1000(text: str) -> float:
    wc = count_words(text)
    if wc == 0:
        return 0.0
    return 1000.0 * count_hedges(text) / wc


def parse_triplet(td: Path) -> dict | None:
    v = td / "virtuous.md"
    n = td / "non-virtuous.md"
    nu = td / "neutral.md"
    if not (v.exists() and n.exists() and nu.exists()):
        return None
    out = {"id": td.name}
    for role, p in (("virtuous", v), ("non-virtuous", n), ("neutral", nu)):
        body = extract_body(p.read_text(encoding="utf-8"))
        out[role] = {
            "wc": count_words(body),
            "step": count_step_markers(body),
            "hedge": count_hedges(body),
            "hedge_per_1000": hedge_per_1000(body),
        }
    return out


def in_band(wc: int, role: str) -> bool:
    lo, hi = TARGETS[role]
    return lo <= wc <= hi


def main() -> int:
    if not CORPUS_ROOT.exists():
        print(f"FATAL: corpus directory not found: {CORPUS_ROOT}", file=sys.stderr)
        return 2

    triplet_dirs = sorted(d for d in CORPUS_ROOT.iterdir()
                          if d.is_dir() and d.name.startswith("triplet-"))
    triplets = []
    for td in triplet_dirs:
        parsed = parse_triplet(td)
        if parsed is None:
            print(f"  WARNING: incomplete triplet skipped: {td.name}", file=sys.stderr)
            continue
        triplets.append(parsed)

    n = len(triplets)
    print("=" * 72)
    print("Phronesis verbosity-control calibration")
    print(f"Corpus: {CORPUS_ROOT.relative_to(HERE.parent)}")
    print(f"Triplets parsed: {n}")
    print("=" * 72)

    if n == 0:
        print("\nNo triplets to score.", file=sys.stderr)
        return 1

    v_wc = [t["virtuous"]["wc"] for t in triplets]
    n_wc = [t["non-virtuous"]["wc"] for t in triplets]
    u_wc = [t["neutral"]["wc"] for t in triplets]

    v_step = [t["virtuous"]["step"] for t in triplets]
    n_step = [t["non-virtuous"]["step"] for t in triplets]

    v_hedge1k = [t["virtuous"]["hedge_per_1000"] for t in triplets]
    n_hedge1k = [t["non-virtuous"]["hedge_per_1000"] for t in triplets]

    def ms(xs):
        if not xs:
            return float("nan"), float("nan")
        if len(xs) < 2:
            return xs[0], 0.0
        return statistics.mean(xs), statistics.stdev(xs)

    v_wc_m, v_wc_s = ms(v_wc)
    n_wc_m, n_wc_s = ms(n_wc)
    u_wc_m, u_wc_s = ms(u_wc)
    v_step_m, v_step_s = ms(v_step)
    n_step_m, n_step_s = ms(n_step)
    v_h_m, v_h_s = ms(v_hedge1k)
    n_h_m, n_h_s = ms(n_hedge1k)

    wc_sep = v_wc_m - n_wc_m
    step_sep = v_step_m - n_step_m
    hedge_delta = v_h_m - n_h_m

    print()
    print("Per-passage word counts (target: V 250-300, N 180-220, T 100-130):")
    print(f"  verbose      mean={v_wc_m:6.1f}  std={v_wc_s:5.1f}  "
          f"min={min(v_wc)}  max={max(v_wc)}")
    print(f"  neutral      mean={u_wc_m:6.1f}  std={u_wc_s:5.1f}  "
          f"min={min(u_wc)}  max={max(u_wc)}")
    print(f"  terse        mean={n_wc_m:6.1f}  std={n_wc_s:5.1f}  "
          f"min={min(n_wc)}  max={max(n_wc)}")

    print()
    print("Step-marker counts:")
    print(f"  verbose      mean={v_step_m:5.2f}  std={v_step_s:4.2f}")
    print(f"  terse        mean={n_step_m:5.2f}  std={n_step_s:4.2f}")

    print()
    print("Hedge density (markers per 1000 words):")
    print(f"  verbose      mean={v_h_m:5.2f}  std={v_h_s:4.2f}")
    print(f"  terse        mean={n_h_m:5.2f}  std={n_h_s:4.2f}")

    wc_pass = wc_sep >= 120.0
    step_pass = step_sep >= 4.0
    hedge_pass = abs(hedge_delta) <= 1.0

    print()
    print("Corpus-level metrics:")
    print(f"  Word-count separation     V-T = {wc_sep:+7.2f}    "
          f"target >= 120     {'PASS' if wc_pass else 'FAIL'}")
    print(f"  Step-marker separation    V-T = {step_sep:+7.2f}    "
          f"target >= 4       {'PASS' if step_pass else 'FAIL'}")
    print(f"  Hedge-density invariance  |V-T|= {abs(hedge_delta):6.2f}    "
          f"target <= 1.0     {'PASS' if hedge_pass else 'FAIL'}")

    flagged = []
    for t in triplets:
        reasons = []
        if not in_band(t["virtuous"]["wc"], "virtuous"):
            reasons.append(f"V wc={t['virtuous']['wc']} out of 250-300")
        if not in_band(t["non-virtuous"]["wc"], "non-virtuous"):
            reasons.append(f"T wc={t['non-virtuous']['wc']} out of 100-130")
        if not in_band(t["neutral"]["wc"], "neutral"):
            reasons.append(f"N wc={t['neutral']['wc']} out of 180-220")
        h_delta_t = abs(t["virtuous"]["hedge_per_1000"]
                        - t["non-virtuous"]["hedge_per_1000"])
        if h_delta_t > 2.0:
            reasons.append(f"hedge-density delta={h_delta_t:.2f} > 2.0")
        s_delta_t = t["virtuous"]["step"] - t["non-virtuous"]["step"]
        if s_delta_t < 2:
            reasons.append(f"step-marker delta={s_delta_t} < 2")
        if reasons:
            flagged.append((t["id"], reasons))

    print()
    if flagged:
        print(f"Per-triplet diagnostics ({len(flagged)} flagged):")
        for tid, reasons in flagged:
            print(f"  {tid}")
            for r in reasons:
                print(f"      - {r}")
    else:
        print("Per-triplet diagnostics: no triplets flagged.")

    overall_pass = wc_pass and step_pass and hedge_pass
    print()
    print("=" * 72)
    print("VERDICT: " + ("PASS" if overall_pass else "FAIL"))
    print("=" * 72)
    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
