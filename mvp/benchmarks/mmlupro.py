"""
MMLU-Pro — much harder than MMLU.
10 options (A-J) instead of 4. 14 categories, 12k questions.

Frontier models see 16-33% accuracy drop compared to MMLU on this.
Good for F65 capability consistency with real headroom.
"""
from __future__ import annotations
import random
from typing import Optional

from datasets import load_dataset

# Domains known to be harder for smaller models
HARD_DOMAINS = {
    "math", "physics", "chemistry", "engineering",
    "philosophy", "law", "economics",
}


def load(n: Optional[int] = None, seed: int = 42,
         hard_only: bool = True) -> list:
    """Stratified-sample across categories (optionally only the hard ones)."""
    from . import BenchmarkItem

    ds = load_dataset("TIGER-Lab/MMLU-Pro", split="test")
    rng = random.Random(seed)

    # Filter to hard domains by default
    candidates = []
    for i, row in enumerate(ds):
        cat = row.get("category", "")
        if hard_only and cat not in HARD_DOMAINS:
            continue
        candidates.append((i, row))

    rng.shuffle(candidates)
    if n is not None:
        candidates = candidates[:n]

    out = []
    for idx, row in candidates:
        opts = row["options"]  # list of up to 10 strings
        letters = [chr(ord("A") + i) for i in range(len(opts))]
        gold_idx = row["answer_index"]
        gold_letter = letters[gold_idx]

        options_str = "\n".join(f"{L}) {o}" for L, o in zip(letters, opts))
        prompt = (
            f"{row['question']}\n\n"
            f"{options_str}\n\n"
            f"Pick the best answer. Respond with a single letter "
            f"({letters[0]}-{letters[-1]}) at the end."
        )
        out.append(BenchmarkItem(
            benchmark="mmlupro",
            item_id=f"{row['category']}-{idx}",
            prompt=prompt,
            gold=gold_letter,
            max_tokens=4096,
            metadata={
                "category": row["category"],
                "choices": opts,
                "gold_idx": gold_idx,
                "src": row.get("src", ""),
            },
        ))
    return out
