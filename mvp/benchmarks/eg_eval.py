"""
EG-eval — Evidence Grounding behavioral benchmark.

Loads 24 open-ended prompts from eg_prompts.json that leave room for
either evidence-grounded (virtuous) or vague-appeal (deficiency) responses.
Scoring is by eg_scorer.score_eg() (markers per 1000 tokens).

Per docs/eg-rt-eval-spec.md §3.
"""
from __future__ import annotations
import json
import random
from pathlib import Path
from typing import Optional


_PROMPTS_PATH = Path(__file__).parent / "eg_prompts.json"


def _load_prompts() -> list:
    with open(_PROMPTS_PATH) as f:
        return json.load(f)["prompts"]


def load(n: Optional[int] = None, seed: int = 42,
         domains: Optional[list] = None) -> list:
    """Returns list of BenchmarkItem objects for EG-eval.

    Args:
        n: if set, subsample to n items
        seed: random seed for subsampling
        domains: if set, filter to only these domains (e.g. ['physics', 'biology'])
    """
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
            benchmark="eg-eval",
            item_id=entry["id"],
            prompt=entry["text"],
            gold="evidence_grounded",  # placeholder; scoring uses eg_scorer
            max_tokens=512,            # ~300-word target, buffer for thinking tokens
            metadata={
                "domain": entry["domain"],
            },
        ))
    return items
