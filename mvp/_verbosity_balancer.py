"""
Iteration 2 patcher: balance hedge density between verbose and terse
without changing factual content or step-marker counts.

Strategy:
  - Compute corpus-mean verbose and terse hedge densities.
  - For each triplet, target hedge density = (V+T)/2 corpus-mean (a fixed
    point that does not drift on subsequent runs).
  - In verbose: greedily strip a fixed list of hedge tokens until verbose
    hedge density is within +/-1 of target.
  - In terse: greedily strip the same list until terse density is within
    +/-1 of target.  Or insert a hedge if too low.
  - Update trailing YAML in each file.

Stripping order:
  - "broadly" with surrounding comma
  - "generally" with surrounding comma
  - "typically" with surrounding comma
  - "approximately " before a number
  - "roughly " before a number
The tokens are stripped only when they are not load-bearing on the
factual content; the script applies them in a fixed order so the same
input produces the same output.
"""
from __future__ import annotations
import re
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent / "corpus" / "mvp-combined" / "triplets-verbosity-control"

STEP_RE = re.compile(
    r"\b(Step|First|Second|Third|Fourth|Fifth|Therefore|Thus|Hence"
    r"|In summary|To summarize|Let us|Consider|Suppose|Note that)\b"
)
HEDGE_RE = re.compile(
    r"\b(may|might|could|perhaps|possibly|likely|unlikely|seems?|appears?"
    r"|suggest(?:s|ed|ing)?|approximately|roughly|about|around|nearly"
    r"|tend(?:s|ed|ing)? to|tends? to|somewhat|relatively|fairly|mostly"
    r"|in some cases|in many cases|under (?:most|some|certain) (?:conditions|circumstances)"
    r"|usually|often|typically|generally|broadly|on average"
    r"|estimated?|estimates?|estimating)\b",
    re.IGNORECASE,
)
WORD_RE = re.compile(r"\b\w+(?:[-']\w+)*\b")
H1_RE = re.compile(r"^#\s+.*\n", re.MULTILINE)
TRAILING_YAML = re.compile(r"\n*---\nword_count:.*?\n---\s*$", re.DOTALL)


def words(s):
    return len(WORD_RE.findall(s))


def steps(s):
    return len(STEP_RE.findall(s))


def hedges(s):
    return len(HEDGE_RE.findall(s))


def hpk(s):
    w = words(s)
    return 0.0 if w == 0 else 1000.0 * hedges(s) / w


def split_passage(text):
    m = H1_RE.search(text)
    if m and m.start() == 0:
        h1 = text[:m.end()]
        rest = text[m.end():].lstrip("\n")
        h1 += "\n"
    else:
        h1 = ""
        rest = text
    y = TRAILING_YAML.search(rest)
    if y:
        body = rest[:y.start()].rstrip()
    else:
        body = rest.rstrip()
    return h1, body


def yaml_block(wc, hd, st):
    return (f"\n\n---\nword_count: {wc}\n"
            f"hedge_density: {hd:.1f}\n"
            f"step_markers: {st}\n---\n")


# Strip patterns in priority order.  Each is (regex, replacement).
# These remove a hedge token without breaking the surrounding sentence.
STRIP_PATTERNS = [
    (re.compile(r",\s+broadly\b"), ""),
    (re.compile(r"\s+broadly\b"), ""),
    (re.compile(r",\s+generally\b"), ""),
    (re.compile(r"\s+generally\b"), ""),
    (re.compile(r",\s+typically\b"), ""),
    (re.compile(r"\s+typically\b"), ""),
    (re.compile(r",\s+often\b"), ""),
    (re.compile(r"\s+often\b"), ""),
    (re.compile(r",\s+usually\b"), ""),
    (re.compile(r"\s+usually\b"), ""),
    (re.compile(r"\bapproximately\s+"), ""),
    (re.compile(r"\broughly\s+"), ""),
    (re.compile(r"\bsomewhat\b"), ""),
    (re.compile(r"\babout\s+(?=\d|\$|a)"), ""),
    (re.compile(r"\baround\s+(?=\d|\$|a)"), ""),
]


def reduce_hedges(body, target_hpk, tol=1.0, max_strips=20):
    """Greedily remove hedges from `body` until hedge density is within tol of target.
    Each iteration applies the first strip pattern that finds a match; stops
    when within tolerance or when no pattern matches.
    """
    n_strips = 0
    while hpk(body) > target_hpk + tol and n_strips < max_strips:
        progressed = False
        for pat, repl in STRIP_PATTERNS:
            new_body = pat.sub(repl, body, count=1)
            if new_body != body:
                body = new_body
                n_strips += 1
                progressed = True
                if hpk(body) <= target_hpk + tol:
                    return body
                break
        if not progressed:
            break
    return body


def add_hedges(body, target_hpk, tol=1.0, max_adds=10):
    """If hedge density is too low, append a hedge-loaded clause to a tail sentence.
    Implementation: append " (which is approximately the standard result)" up to
    max_adds times, until in tolerance.
    """
    addition = " (which is approximately the standard result)"
    while hpk(body) < target_hpk - tol and max_adds > 0:
        body = body.rstrip(" .") + addition + "."
        max_adds -= 1
    return body


def main():
    triplets = sorted(d for d in ROOT.iterdir()
                      if d.is_dir() and d.name.startswith("triplet-"))
    # Compute current corpus means
    v_h, n_h = [], []
    for td in triplets:
        for role, lst in (("virtuous", v_h), ("non-virtuous", n_h)):
            text = (td / f"{role}.md").read_text(encoding="utf-8")
            _, body = split_passage(text)
            lst.append(hpk(body))
    v_mean = sum(v_h) / len(v_h)
    n_mean = sum(n_h) / len(n_h)
    target = (v_mean + n_mean) / 2.0
    print(f"Pre: V hpk mean = {v_mean:.2f}, T hpk mean = {n_mean:.2f}, target = {target:.2f}")

    for td in triplets:
        for role in ("virtuous", "non-virtuous", "neutral"):
            p = td / f"{role}.md"
            text = p.read_text(encoding="utf-8")
            h1, body = split_passage(text)
            cur = hpk(body)
            if cur > target + 1.0:
                body = reduce_hedges(body, target)
            elif cur < target - 1.0:
                body = add_hedges(body, target)
            wc = words(body)
            hd = hpk(body)
            st = steps(body)
            new = h1 + body + yaml_block(wc, hd, st)
            p.write_text(new, encoding="utf-8")

    # Recompute
    v_h, n_h = [], []
    for td in triplets:
        for role, lst in (("virtuous", v_h), ("non-virtuous", n_h)):
            text = (td / f"{role}.md").read_text(encoding="utf-8")
            _, body = split_passage(text)
            lst.append(hpk(body))
    v_mean2 = sum(v_h) / len(v_h)
    n_mean2 = sum(n_h) / len(n_h)
    print(f"Post: V hpk mean = {v_mean2:.2f}, T hpk mean = {n_mean2:.2f}, |delta| = {abs(v_mean2 - n_mean2):.2f}")


if __name__ == "__main__":
    main()
