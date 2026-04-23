"""
Benchmark infrastructure for Phronesis Phase 4 validation.

Each benchmark implements a `load(n=None, seed=42)` function returning a list
of BenchmarkItem objects. Scorers in `scorers.py` parse the model's response
and compare against the gold answer.

Two tiers of benchmarks are available:

  ── Tier A (harder 2026-era benchmarks, currently the default probe set) ──
  - mmlupro       MMLU-Pro (10-option MCQ, much harder than MMLU)
  - musr          MuSR (Multistep Soft Reasoning: mystery/team/placement)
  - simplebench   SimpleBench-style trick questions (hand-crafted)
  - humblebench   Epistemic humility / false-option rejection (expanded)
  - gsm8k         Math capability floor (for F65 degradation check)
  - sycophancy    Resistance to user pushback
  - xstest        Over-refusal probe on benign prompts

  ── Tier B (easier, now redundant but kept for legacy comparison) ──
  - mmlu          Original MMLU (mostly saturated for Qwen3-4B)
  - truthfulqa    Common misconception avoidance (mostly saturated)
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BenchmarkItem:
    benchmark: str
    item_id: str
    prompt: str                # the text sent to the model as the user turn
    gold: Any                  # ground truth (format depends on benchmark)
    max_tokens: int = 4096     # default per-item cap
    metadata: dict = field(default_factory=dict)

    def short_id(self) -> str:
        return f"{self.benchmark}:{self.item_id}"


# Import loaders
from . import (
    gsm8k, mmlu, mmlupro, truthfulqa, musr,
    humblebench, simplebench, sycophancy, xstest, abstention,
    math500, aime, zebralogic, hard_probe_v2, hard_probe_v3, mm92_verify,
    eg_eval, rt_eval,
)

# Default probe set (tier-A challenge-level)
# NOTE: 'abstention' is the key benchmark for our virtue. Questions where the
# right answer is "I don't know" — tests epistemic humility directly.
REGISTRY = {
    "mm92_verify": mm92_verify.load,     # ⭐ priority-1 hallucination verification (2 items)
    "hard_probe_v3": hard_probe_v3.load, # follow-up 9-item probe (attractor break + MCQ replication)
    "hard_probe_v2": hard_probe_v2.load, # curated 19-item cross-benchmark probe
    "abstention":  abstention.load,      # IH-eval (24 items)
    "eg-eval":     eg_eval.load,         # Evidence Grounding behavioral eval (24 items)
    "rt-eval":     rt_eval.load,         # Reasoning Transparency behavioral eval (24 items)
    "math500":     math500.load,
    "aime":        aime.load,
    "zebralogic":  zebralogic.load,
    "simplebench": simplebench.load,
    "humblebench": humblebench.load,
    "mmlupro":     mmlupro.load,
    "musr":        musr.load,
    "gsm8k":       gsm8k.load,
    "sycophancy":  sycophancy.load,
    "xstest":      xstest.load,
}

# Legacy / easier benchmarks — available on demand, not in default probe
LEGACY_REGISTRY = {
    "mmlu":       mmlu.load,
    "truthfulqa": truthfulqa.load,
}

# Full registry (every loader available by name)
ALL_LOADERS = {**REGISTRY, **LEGACY_REGISTRY}
