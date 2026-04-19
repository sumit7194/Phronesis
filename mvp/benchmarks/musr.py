"""
MuSR — Multistep Soft Reasoning.
Three sub-tasks: murder_mysteries, object_placements, team_allocation.

Natural-language multi-step reasoning. Tests the model's ability to trace
inference chains over prose — directly aligned with our calibrated-confidence
steering target (when the chain is long, the model must commit carefully).
"""
from __future__ import annotations
import ast
import random
from typing import Optional

from datasets import load_dataset


# All three subdomains are hard; we sample from all by default
SUBDOMAINS = ["murder_mysteries", "object_placements", "team_allocation"]


def load(n: Optional[int] = None, seed: int = 42,
         subdomains: Optional[list] = None) -> list:
    from . import BenchmarkItem

    rng = random.Random(seed)
    subs = subdomains or SUBDOMAINS

    all_items = []
    ds = load_dataset("TAUR-Lab/MuSR")
    for sub in subs:
        if sub not in ds: continue
        for i, row in enumerate(ds[sub]):
            all_items.append((sub, i, row))

    rng.shuffle(all_items)
    if n is not None:
        all_items = all_items[:n]

    out = []
    for sub, idx, row in all_items:
        # choices is stored as a string like "['A', 'B', 'C']"
        choices_raw = row["choices"]
        if isinstance(choices_raw, str):
            try:
                choices = ast.literal_eval(choices_raw)
            except Exception:
                choices = [choices_raw]
        else:
            choices = list(choices_raw)

        gold_idx = int(row["answer_index"]) if isinstance(row["answer_index"], str) \
                   else row["answer_index"]
        letters = [chr(ord("A") + i) for i in range(len(choices))]
        gold_letter = letters[gold_idx]

        options_str = "\n".join(f"{L}) {c}" for L, c in zip(letters, choices))
        prompt = (
            f"{row['narrative']}\n\n"
            f"{row['question']}\n\n"
            f"{options_str}\n\n"
            f"Choose the best answer. Respond with a single letter "
            f"({letters[0]}-{letters[-1]}) at the end."
        )
        out.append(BenchmarkItem(
            benchmark="musr",
            item_id=f"{sub}-{idx}",
            prompt=prompt,
            gold=gold_letter,
            max_tokens=4096,
            metadata={
                "subdomain": sub,
                "choices": choices,
                "gold_idx": gold_idx,
            },
        ))
    return out
