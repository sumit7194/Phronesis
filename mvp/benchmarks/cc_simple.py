"""
CC-simple — Calibrated-Confidence diagnostic with simple reasoning prompts.

8 single-answer reasoning prompts (CRT, modus-tollens, rate, primality, MCQ).
Designed for hand-rating: did the model commit confidently to the right answer,
or did it spiral / equivocate / hedge? v_CC at α>0 is hypothesised to push
toward confident commit; α<0 toward spiraling.

No automated scorer — these are for hand review. The "gold" field carries the
expected answer for ease of hand-rating, but `correct` will be reported as None
(unparsed) since we deliberately want to read the full output.

Loader signature parallels eg_eval / rt_eval / abstention.
"""
from __future__ import annotations
import json
import random
from pathlib import Path
from typing import Optional


_PROMPTS_PATH = Path(__file__).parent / "cc_simple_prompts.json"


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
            benchmark="cc-simple",
            item_id=entry["id"],
            prompt=entry["text"],
            gold=entry.get("expected_answer", "hand_review"),
            max_tokens=2048,
            metadata={
                "category": entry.get("category", ""),
                "expected_answer": entry.get("expected_answer", ""),
            },
        ))
    return items
