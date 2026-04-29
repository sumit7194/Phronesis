"""
composition-test — 10 prompts designed to surface differential behavior between
v_IH alone, v_CC alone, and v_IH + v_CC composed.

Hand-rated only. No automated scorer.
"""
from __future__ import annotations
import json
import random
from pathlib import Path
from typing import Optional


_PROMPTS_PATH = Path(__file__).parent / "composition_prompts.json"


def _load_prompts() -> list:
    with open(_PROMPTS_PATH) as f:
        return json.load(f)["prompts"]


def load(n: Optional[int] = None, seed: int = 42) -> list:
    from . import BenchmarkItem

    pool = _load_prompts()
    rng = random.Random(seed)
    rng.shuffle(pool)
    if n is not None:
        pool = pool[:n]

    items = []
    for entry in pool:
        items.append(BenchmarkItem(
            benchmark="composition-test",
            item_id=entry["id"],
            prompt=entry["text"],
            gold="hand_review",
            max_tokens=2048,
            metadata={
                "category": entry.get("category", ""),
                "domain": entry.get("domain", ""),
            },
        ))
    return items
