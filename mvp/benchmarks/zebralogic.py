"""
ZebraLogic — logic grid puzzles (constraint satisfaction problems).
Hosted on HF: WildEval/ZebraLogic.

Two configs:
  - grid_mode: full-grid solution required (hardest — default here)
  - mc_mode: multiple choice per cell (easier)

Puzzle sizes: 2x2 to 6x6. Hardest are 6x6 with 6 houses × 6 features.

Claude 3.5 Sonnet baseline (from paper): 33.4% overall, 12.4% on hard puzzles.
For 4B model, expect very low accuracy — genuine failure rate, lots of
headroom for steering effects.
"""
from __future__ import annotations
import random
from typing import Optional

from datasets import load_dataset


def _size_from_id(item_id: str):
    """mc_mode IDs are like 'lgp-test-6x4-37#mc-16'; extract houses × features."""
    import re
    m = re.search(r"(\d+)x(\d+)", item_id)
    if m:
        return int(m.group(1)) * int(m.group(2))
    return 999


def load(n: Optional[int] = None, seed: int = 42,
         max_complexity: int = 20) -> list:
    """
    Sample n items from ZebraLogic mc_mode, filtered by puzzle complexity
    (houses × features). max_complexity=20 means we allow up to e.g. 4x5
    or 5x4 (mid-difficulty); 6x6 (=36) is excluded by default.
    """
    from . import BenchmarkItem

    ds = load_dataset("WildEval/ZebraLogic", "mc_mode", split="test")
    rng = random.Random(seed)
    candidates = [r for r in ds if _size_from_id(r["id"]) <= max_complexity]
    rng.shuffle(candidates)
    if n is not None:
        candidates = candidates[:n]

    items = []
    for row in candidates:
        letters = [chr(ord("A") + i) for i in range(len(row["choices"]))]
        options_str = "\n".join(f"{L}) {c}" for L, c in zip(letters, row["choices"]))
        # Map gold name to the corresponding letter
        try:
            gold_idx = row["choices"].index(row["answer"])
            gold_letter = letters[gold_idx]
        except (ValueError, IndexError):
            gold_letter = None

        prompt = (
            f"{row['puzzle']}\n\n"
            f"{row['question']}\n\n"
            f"{options_str}\n\n"
            f"Work out the constraints systematically, then give the answer "
            f"as a single letter ({letters[0]}-{letters[-1]}) at the end."
        )
        items.append(BenchmarkItem(
            benchmark="zebralogic",
            item_id=row["id"],
            prompt=prompt,
            gold=gold_letter or row["answer"],
            max_tokens=4096,
            metadata={
                "complexity": _size_from_id(row["id"]),
                "choices": row["choices"],
                "answer_name": row["answer"],
            },
        ))
    return items
