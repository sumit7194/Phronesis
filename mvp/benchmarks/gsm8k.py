"""
GSM8K — grade school math word problems.
Standard benchmark for reasoning + arithmetic. Used as F65 capability proxy.

Answer format in the dataset: '... \n#### <number>' (the number after #### is gold).
"""
from __future__ import annotations
import random
from typing import Optional

from datasets import load_dataset


def load(n: Optional[int] = None, seed: int = 42) -> list:
    """Load n random test items (or all 1319 if n is None)."""
    from . import BenchmarkItem

    ds = load_dataset("openai/gsm8k", "main", split="test")
    rng = random.Random(seed)
    idxs = list(range(len(ds)))
    rng.shuffle(idxs)
    if n is not None:
        idxs = idxs[:n]

    items = []
    for i in idxs:
        row = ds[i]
        # Strip the reasoning trace; keep just the #### final number
        gold_answer = row["answer"].split("####")[-1].strip().replace(",", "")
        items.append(BenchmarkItem(
            benchmark="gsm8k",
            item_id=str(i),
            prompt=row["question"].strip(),
            gold=gold_answer,
            max_tokens=4096,  # universal cap for local mini-probe
            metadata={
                "full_answer_with_cot": row["answer"],
                "dataset_index": i,
            },
        ))
    return items
