"""
Hard Probe v3 — follow-up experiment after hard_probe_v2.

Two goals:

 1. **Break same-wrong-answer attractors.** The 6 items both baseline and
    `L20 @ α=+12` got wrong in hard_probe_v2 — especially aime/42 and
    murder_mysteries-92 where both converged on the SAME wrong answer.
    Rerun these with alternative (vector, α) combos to test whether
    different steering directions disrupt the attractor.

 2. **Replicate the humblebench/fb-nile-source epistemic win.** That was
    the only N=1 MCQ-abstention win in hard_probe_v2, and it contradicted
    the simple F92 reading. Add 2 more "gold=E" humblebench items plus
    1 control (gold != E) to test:
      - Does steering reliably help recognize "none of the above" on false-
        premise MCQs? (replication)
      - Does steering over-push toward E even when a real option is
        correct? (control)

Items (9 total):

  Both-wrong from v2 (rerun with alt configs):
    - aime/29, aime/35, aime/42, aime/51, aime/81
    - musr/murder_mysteries-92

  New humblebench items (need fresh baseline + steered):
    - humblebench/fb-largest-desert   (gold=E, Antarctica trick)
    - humblebench/fb-nobel-einstein   (gold=E, photoelectric vs relativity)
    - humblebench/fb-ww2-end          (gold=C, CONTROL — real answer is C)

Per-benchmark caps (inherited from v2 where applicable):
    aime:         24576
    musr:          8192
    humblebench:   4096

Output goes under `benchmark_probe/hard_probe_v3/<label>/`. Run with
`--label steered_L22_a12` etc. to separate configs.
"""
from __future__ import annotations
from typing import Optional

_CAPS = {
    "aime":        24576,
    "musr":         8192,
    "humblebench":  4096,
}

_BOTH_WRONG_V2 = {
    "aime": ["29", "35", "42", "51", "81"],
    "musr": ["murder_mysteries-92"],
}

_NEW_HUMBLEBENCH = ["fb-largest-desert", "fb-nobel-einstein", "fb-ww2-end"]


def load(n: Optional[int] = None, seed: int = 42) -> list:
    from . import aime, musr, humblebench, BenchmarkItem

    items = []

    # ── 1. AIME both-wrong from v2 ──────────────────────────────────────
    all_aime = aime.load(n=None, seed=42)     # carryover items (10, 42, 58, 72) ← seed 42
    aime_pool_seed123 = aime.load(n=None, seed=123)  # new-aime items from v2

    want_aime = set(_BOTH_WRONG_V2["aime"])
    # 42 is in seed-42 carryover; 29, 35, 51, 81 are in seed-123 pool
    for it in all_aime:
        if it.item_id in want_aime:
            items.append(it)
    for it in aime_pool_seed123:
        if it.item_id in want_aime and all(x.item_id != it.item_id for x in items):
            items.append(it)

    # ── 2. MuSR both-wrong ──────────────────────────────────────────────
    try:
        musr_all = musr.load(n=None, seed=42)
        want_musr = set(_BOTH_WRONG_V2["musr"])
        for it in musr_all:
            if it.item_id in want_musr:
                items.append(it)
    except Exception as e:
        print(f"  [warn] skipping musr: {e}")

    # ── 3. New humblebench items ───────────────────────────────────────
    try:
        hb_all = humblebench.load(n=None, seed=42)
        want_hb = set(_NEW_HUMBLEBENCH)
        for it in hb_all:
            if it.item_id in want_hb:
                items.append(it)
    except Exception as e:
        print(f"  [warn] skipping humblebench: {e}")

    # ── Apply per-benchmark cap overrides ──────────────────────────────
    for it in items:
        if it.benchmark in _CAPS:
            it.max_tokens = _CAPS[it.benchmark]

    if n is not None:
        items = items[:n]
    return items
