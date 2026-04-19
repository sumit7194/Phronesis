"""
AIME — American Invitational Mathematics Examination.
Very hard competition math. Answers are always integers 0-999.

Hosted on HF: AI-MO/aimo-validation-aime (90 items from 2022-2023).

For Qwen3-4B, expect 20-40% accuracy. Small models struggle severely here;
big frontier reasoning models score 80%+. Perfect hard benchmark.
"""
from __future__ import annotations
import random
from typing import Optional

from datasets import load_dataset


def load(n: Optional[int] = None, seed: int = 42) -> list:
    from . import BenchmarkItem

    ds = load_dataset("AI-MO/aimo-validation-aime", split="train")
    rng = random.Random(seed)
    idxs = list(range(len(ds)))
    rng.shuffle(idxs)
    if n is not None:
        idxs = idxs[:n]

    items = []
    for i in idxs:
        row = ds[i]
        prompt = (
            f"{row['problem']}\n\n"
            "This is an AIME problem; the answer is always an integer between "
            "0 and 999. Show your working, then give the final answer in the "
            "form \\boxed{ANSWER} at the end."
        )
        items.append(BenchmarkItem(
            benchmark="aime",
            item_id=str(row["id"]),
            prompt=prompt,
            gold=str(row["answer"]).strip(),
            max_tokens=8192,   # raised from 4096; baseline was hitting cap on every item
            metadata={
                "url": row.get("url", ""),
                "solution": row["solution"],
            },
        ))
    return items
