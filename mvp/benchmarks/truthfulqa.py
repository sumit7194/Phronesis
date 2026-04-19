"""
TruthfulQA — testing common-misconception avoidance.
Multiple-choice version: one correct answer + several plausible-sounding wrong ones.

Relevant because "avoiding common misconceptions" is epistemic humility adjacent.
"""
from __future__ import annotations
import random
from typing import Optional

from datasets import load_dataset


def load(n: Optional[int] = None, seed: int = 42) -> list:
    from . import BenchmarkItem

    # multiple_choice config has "mc1_targets" (single correct) and "mc2_targets"
    ds = load_dataset("truthful_qa", "multiple_choice", split="validation")
    rng = random.Random(seed)
    idxs = list(range(len(ds)))
    rng.shuffle(idxs)
    if n is not None:
        idxs = idxs[:n]

    items = []
    for i in idxs:
        row = ds[i]
        choices = row["mc1_targets"]["choices"]
        labels = row["mc1_targets"]["labels"]
        # labels[0] is the correct one by convention in TruthfulQA's dataset schema,
        # but we should derive from labels explicitly.
        correct_idx = labels.index(1) if 1 in labels else 0
        letters = [chr(ord("A") + j) for j in range(len(choices))]
        gold_letter = letters[correct_idx]
        options_str = "\n".join(f"{L}) {c}" for L, c in zip(letters, choices))
        prompt = (
            f"{row['question']}\n\n"
            f"{options_str}\n\n"
            f"Pick the best answer. Respond with a single letter ({letters[0]}"
            f"-{letters[-1]}) at the end of your response."
        )
        items.append(BenchmarkItem(
            benchmark="truthfulqa",
            item_id=str(i),
            prompt=prompt,
            gold=gold_letter,
            max_tokens=4096,
            metadata={"choices": choices, "gold_idx": correct_idx},
        ))
    return items
