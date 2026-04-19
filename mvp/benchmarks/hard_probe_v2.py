"""
Hard Probe v2 — curated 17-item benchmark for matched-cap steering vs baseline
replication with expanded N and cross-benchmark generalization.

Composition:
  - 4 carryover AIME items (10, 42, 58, 72) where at least one condition
    failed at 8192 cap — rerun at 16384 to check for cap-artifact effects
  - 10 new AIME items (seed=123, distinct from carryover)
  - 2 MATH-500 Level 5 items (different competition-math style)
  - 1 MuSR murder-mystery (narrative multi-step reasoning)
  - 1 ZebraLogic puzzle at 5x5 complexity (harder CSP)
  - 1 HumbleBench item (diagonal F92/F93 check — tests whether steering's
    commit-to-structure mechanism hurts abstention on a hard-reasoning prompt)

Token caps are promoted per benchmark:
  aime, math500:       16384
  musr, zebralogic:     8192
  humblebench:          4096

Items keep their native `benchmark` field so the correct scorer is dispatched,
but the runner stores all outputs under `benchmark_probe/hard_probe_v2/`.
"""
from __future__ import annotations
from typing import Optional

# Per-item-type cap overrides for this probe
_CAPS = {
    "aime":        24576,
    "math500":     24576,
    "musr":         8192,
    "zebralogic":   8192,
    "humblebench":  4096,
}


def load(n: Optional[int] = None, seed: int = 42) -> list:
    from . import aime, math500, musr, zebralogic, humblebench, BenchmarkItem

    items = []

    # ─── 1. AIME carryover (4 items where at least one condition failed) ───
    # We load all AIME items (the loader returns 90 with n=None), then filter
    # to the specific IDs we want.
    all_aime = aime.load(n=None, seed=42)  # same seed as original to get same mapping
    carryover_ids = {"10", "42", "58", "72"}
    carry = [it for it in all_aime if it.item_id in carryover_ids]
    items.extend(carry)

    # ─── 2. 8 new AIME items (different seed, filtered to avoid collision) ───
    aime_new_pool = aime.load(n=None, seed=123)
    seen = {it.item_id for it in items}
    aime_new = [it for it in aime_new_pool if it.item_id not in seen][:10]
    items.extend(aime_new)

    # ─── 3. 2 MATH-500 Level 5 items ───
    m500 = math500.load(n=2, seed=42, levels=["5"])
    items.extend(m500)

    # ─── 4. 1 MuSR narrative-reasoning item ───
    try:
        musr_items = musr.load(n=1, seed=42)
        items.extend(musr_items)
    except Exception as e:
        print(f"  [warn] skipping musr: {e}")

    # ─── 5. 1 ZebraLogic item at 5x5 complexity (harder than prior runs) ───
    try:
        zl = zebralogic.load(n=1, seed=42, max_complexity=25)
        items.extend(zl)
    except Exception as e:
        print(f"  [warn] skipping zebralogic: {e}")

    # ─── 6. 1 HumbleBench item ───
    try:
        hb = humblebench.load(n=1, seed=42)
        items.extend(hb)
    except Exception as e:
        print(f"  [warn] skipping humblebench: {e}")

    # Apply per-benchmark cap overrides
    for it in items:
        if it.benchmark in _CAPS:
            it.max_tokens = _CAPS[it.benchmark]

    if n is not None:
        items = items[:n]
    return items
