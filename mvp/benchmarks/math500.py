"""
MATH-500 — 500-problem curated subset of the MATH competition benchmark.
Hosted on HF: HuggingFaceH4/MATH-500.

Difficulty levels 1-5 (5 hardest). By default we sample LEVEL 5 items only —
these are the genuinely hard competition math problems where a 4B model
should show real failure rate.

Level distribution: L1=43, L2=90, L3=105, L4=128, L5=134.
"""
from __future__ import annotations
import random
from typing import Optional

from datasets import load_dataset


def load(n: Optional[int] = None, seed: int = 42,
         levels: Optional[list] = None) -> list:
    """Sample n items, by default filtered to Level 5."""
    from . import BenchmarkItem

    if levels is None:
        levels = ["5"]  # default: hardest only
    levels = [str(L) for L in levels]

    ds = load_dataset("HuggingFaceH4/MATH-500", split="test")
    rng = random.Random(seed)
    candidates = [r for r in ds if str(r["level"]) in levels]
    rng.shuffle(candidates)
    if n is not None:
        candidates = candidates[:n]

    items = []
    for row in candidates:
        prompt = (
            f"{row['problem']}\n\n"
            "Show your working, then give the final answer in the form "
            "\\boxed{ANSWER} at the end."
        )
        items.append(BenchmarkItem(
            benchmark="math500",
            item_id=f"L{row['level']}-{row['unique_id'].split('/')[-1].rstrip('.json')}",
            prompt=prompt,
            gold=row["answer"],
            max_tokens=4096,
            metadata={
                "level": row["level"],
                "subject": row["subject"],
                "solution": row["solution"],
            },
        ))
    return items
