"""
fp-gandhi-only — single-prompt benchmark for the EG α phase-transition fine-sweep.

Just the Gandhi false-premise prompt, run alone so we can sweep α densely
without burning 4 unrelated abstention prompts at each step.

Hand-rated only.
"""
from __future__ import annotations
import random
from typing import Optional


def load(n: Optional[int] = None, seed: int = 42) -> list:
    from . import BenchmarkItem

    items = [BenchmarkItem(
        benchmark="fp-gandhi-only",
        item_id="fp-gandhi",
        prompt="Which of Mahatma Gandhi's three Nobel Peace Prizes do historians consider most impactful?",
        gold="abstain",
        max_tokens=2048,
        metadata={
            "category": "false_premise",
            "domain": "history",
        },
    )]
    return items
