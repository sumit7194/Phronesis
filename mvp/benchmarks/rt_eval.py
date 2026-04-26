"""
RT-eval — Reasoning Transparency behavioral benchmark.

Loads 24 open-ended prompts from rt_prompts.json that invite multi-step
reasoning without priming RT (no "step by step", no "carefully").

Scoring is by rt_scorer.score_rt() (markers per 1000 tokens).

Per docs/eg-rt-eval-spec.md §4.
"""
from __future__ import annotations
import json
import random
from pathlib import Path
from typing import Optional


_PROMPTS_PATH = Path(__file__).parent / "rt_prompts.json"


def _load_prompts() -> list:
    with open(_PROMPTS_PATH) as f:
        return json.load(f)["prompts"]


def load(n: Optional[int] = None, seed: int = 42,
         domains: Optional[list] = None) -> list:
    """Returns list of BenchmarkItem objects for RT-eval."""
    from . import BenchmarkItem

    pool = _load_prompts()
    if domains is not None:
        pool = [p for p in pool if p["domain"] in domains]

    rng = random.Random(seed)
    rng.shuffle(pool)
    if n is not None:
        pool = pool[:n]

    items = []
    for entry in pool:
        items.append(BenchmarkItem(
            benchmark="rt-eval",
            item_id=entry["id"],
            prompt=entry["text"],
            gold="reasoning_transparent",  # placeholder; scoring uses rt_scorer
            max_tokens=2048,           # raised 2026-04-25 (same reason as eg_eval)
            metadata={
                "domain": entry["domain"],
            },
        ))
    return items
