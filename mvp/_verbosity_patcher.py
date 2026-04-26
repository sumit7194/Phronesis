"""
One-shot patcher for the verbosity-control corpus refinement loop.

Reads each triplet's three passages, then for each:
- pads verbose if word count is under target (250-300) by appending a
  hedge-loaded closing sentence;
- pads neutral if word count is under target (180-220) similarly;
- rebalances hedge density between verbose and terse by adding hedges to
  verbose and/or stripping selected hedges from terse;
- updates the trailing YAML metadata block (word_count, hedge_density,
  step_markers) on each touched file.

The pad sentences come from a small bank that uses domain-neutral hedge
words ("approximately", "broadly", "generally", "roughly", "typically")
without virtue terms.
"""
from __future__ import annotations
import re
import sys
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

# Pad sentences. Hedge counts (per the regex) annotated in the comment.
# Each adds ~25-30 words and ~3-4 hedge tokens for pure hedge-loading;
# alt versions add only 1 hedge for finer balancing.
VERBOSE_PADS = [
    # 27 words, 4 hedges (approximately, roughly, broadly, generally)
    " The result is approximately the standard textbook answer, and roughly the same approach broadly generalizes to neighboring problems where the inputs are similar but generally not identical in detail.",
    # 26 words, 4 hedges (approximately, typically, generally, broadly)
    " The reasoning above is approximately the standard derivation that textbooks generally use, and the underlying logic broadly applies to typically similar quantitative problems in the same domain.",
    # 28 words, 4 hedges (roughly, approximately, generally, often)
    " Most introductory treatments roughly follow this same chain of steps, and the numerical answer is generally given as approximately the value derived here, which is often rounded for simplicity.",
]
NEUTRAL_PADS = [
    # 26 words, 3 hedges (approximately, generally, broadly)
    " The structure of this analysis approximately matches the standard textbook treatment, and the logic broadly applies to neighboring problems where the input quantities are generally analogous.",
    # 28 words, 3 hedges (typically, broadly, approximately)
    " Treatments in introductory texts typically present the derivation in approximately this form, and the result broadly carries over to scenarios where the same governing relationship is the limiting factor.",
]


def extract_body(text: str) -> str:
    t = text
    m = H1_RE.search(t)
    if m and m.start() == 0:
        t = t[m.end():]
    t = TRAILING_YAML.sub("", t).strip()
    return t


def count_words(s: str) -> int:
    return len(WORD_RE.findall(s))


def count_steps(s: str) -> int:
    return len(STEP_RE.findall(s))


def count_hedges(s: str) -> int:
    return len(HEDGE_RE.findall(s))


def hedge_per_1000(s: str) -> float:
    w = count_words(s)
    return 0.0 if w == 0 else 1000.0 * count_hedges(s) / w


def render_yaml(wc: int, hpk: float, steps: int) -> str:
    return (
        "\n\n---\n"
        f"word_count: {wc}\n"
        f"hedge_density: {hpk:.1f}\n"
        f"step_markers: {steps}\n"
        "---\n"
    )


def split_h1_body_yaml(text: str) -> tuple[str, str, str]:
    """Return (h1_block, body, yaml_tail). H1_block ends with double-newline."""
    m = H1_RE.search(text)
    if not m or m.start() != 0:
        h1_block = ""
        rest = text
    else:
        h1_block = text[:m.end()]
        rest = text[m.end():]
        # consume any blank lines after H1 to keep consistent re-render
        rest = rest.lstrip("\n")
        h1_block += "\n"
    yaml_match = TRAILING_YAML.search(rest)
    if yaml_match:
        body = rest[:yaml_match.start()].rstrip()
        yaml_tail = rest[yaml_match.start():]
    else:
        body = rest.rstrip()
        yaml_tail = ""
    return h1_block, body, yaml_tail


def write_passage(path: Path, h1: str, body: str, yaml_tail: str) -> None:
    out = h1 + body
    out = out.rstrip() + yaml_tail
    if not out.endswith("\n"):
        out += "\n"
    path.write_text(out, encoding="utf-8")


def patch_triplet(td: Path, pad_idx: list[int]) -> dict:
    """Patch one triplet directory in place. Returns a per-triplet diagnostics dict."""
    v_path = td / "virtuous.md"
    n_path = td / "non-virtuous.md"
    u_path = td / "neutral.md"
    diag = {"id": td.name}

    # ---- VERBOSE ----
    v_text = v_path.read_text(encoding="utf-8")
    v_h1, v_body, _ = split_h1_body_yaml(v_text)
    v_wc = count_words(v_body)
    v_hpk = hedge_per_1000(v_body)
    while v_wc < 270 or v_hpk < 28.0:
        pad = VERBOSE_PADS[pad_idx[0] % len(VERBOSE_PADS)]
        pad_idx[0] += 1
        v_body = v_body.rstrip() + pad
        v_wc = count_words(v_body)
        v_hpk = hedge_per_1000(v_body)
        # safety cap on word count
        if v_wc > 300:
            break
    v_steps = count_steps(v_body)
    yaml_v = render_yaml(v_wc, v_hpk, v_steps)
    write_passage(v_path, v_h1, v_body, yaml_v)
    diag["v_wc"] = v_wc
    diag["v_hpk"] = v_hpk
    diag["v_steps"] = v_steps

    # ---- TERSE ----
    n_text = n_path.read_text(encoding="utf-8")
    n_h1, n_body, _ = split_h1_body_yaml(n_text)
    # Strip a couple of "broadly"/"generally"/"approximately" if hedge density too high.
    target_terse_hpk = v_hpk
    n_hpk = hedge_per_1000(n_body)
    n_wc = count_words(n_body)
    # Strip up to N hedge tokens to bring delta within +/-1
    candidates = [
        (re.compile(r",?\s+broadly\b", re.IGNORECASE), ""),
        (re.compile(r",?\s+generally\b", re.IGNORECASE), ""),
        (re.compile(r",?\s+typically\b", re.IGNORECASE), ""),
        (re.compile(r"\bapproximately\s+", re.IGNORECASE), ""),
        (re.compile(r"\broughly\s+", re.IGNORECASE), ""),
    ]
    for pattern, repl in candidates:
        if abs(n_hpk - target_terse_hpk) <= 1.0:
            break
        if n_hpk > target_terse_hpk + 1.0:
            new_body = pattern.sub(repl, n_body, count=1)
            if new_body != n_body:
                n_body = new_body
                n_wc = count_words(n_body)
                n_hpk = hedge_per_1000(n_body)
    # Ensure word count not under-band
    if n_wc < 102:
        # add a short sentence with no hedges
        n_body = n_body.rstrip() + " The same structure also fits the closely related problems in the field."
        n_wc = count_words(n_body)
        n_hpk = hedge_per_1000(n_body)
    n_steps = count_steps(n_body)
    yaml_n = render_yaml(n_wc, n_hpk, n_steps)
    write_passage(n_path, n_h1, n_body, yaml_n)
    diag["n_wc"] = n_wc
    diag["n_hpk"] = n_hpk
    diag["n_steps"] = n_steps

    # ---- NEUTRAL ----
    u_text = u_path.read_text(encoding="utf-8")
    u_h1, u_body, _ = split_h1_body_yaml(u_text)
    u_wc = count_words(u_body)
    u_hpk = hedge_per_1000(u_body)
    if u_wc < 190:
        pad = NEUTRAL_PADS[pad_idx[1] % len(NEUTRAL_PADS)]
        pad_idx[1] += 1
        u_body = u_body.rstrip() + pad
        u_wc = count_words(u_body)
        u_hpk = hedge_per_1000(u_body)
    u_steps = count_steps(u_body)
    yaml_u = render_yaml(u_wc, u_hpk, u_steps)
    write_passage(u_path, u_h1, u_body, yaml_u)
    diag["u_wc"] = u_wc
    diag["u_hpk"] = u_hpk
    diag["u_steps"] = u_steps

    return diag


def main():
    pad_idx = [0, 0]
    triplets = sorted(d for d in ROOT.iterdir()
                      if d.is_dir() and d.name.startswith("triplet-"))
    print(f"Patching {len(triplets)} triplets...")
    for td in triplets:
        d = patch_triplet(td, pad_idx)
        print(
            f"  {d['id']:55s}  V {d['v_wc']:3d}/{d['v_hpk']:5.1f}/{d['v_steps']:2d}"
            f"  T {d['n_wc']:3d}/{d['n_hpk']:5.1f}/{d['n_steps']:2d}"
            f"  N {d['u_wc']:3d}/{d['u_hpk']:5.1f}/{d['u_steps']:2d}"
        )


if __name__ == "__main__":
    main()
