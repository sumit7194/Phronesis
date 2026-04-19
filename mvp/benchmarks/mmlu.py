"""
MMLU — Massive Multitask Language Understanding.
57 subjects, 4-option multiple choice. Use for broad knowledge-preservation check (F65-b).

We use a stratified sample across subjects by default.
"""
from __future__ import annotations
import random
from typing import Optional

from datasets import load_dataset

# Subjects stratified-sampled by default (biases toward STEM + philosophy which
# are most load-bearing for calibrated confidence).
DEFAULT_SUBJECTS = [
    "abstract_algebra", "college_mathematics", "elementary_mathematics",
    "college_physics", "high_school_physics", "college_chemistry",
    "college_biology", "clinical_knowledge", "medical_genetics",
    "professional_medicine", "philosophy", "logical_fallacies",
    "formal_logic", "moral_scenarios", "econometrics", "high_school_statistics",
]


def load(n: Optional[int] = None, seed: int = 42,
         subjects: Optional[list] = None) -> list:
    """Load n items from MMLU test, stratified across subjects."""
    from . import BenchmarkItem

    subs = subjects or DEFAULT_SUBJECTS
    rng = random.Random(seed)

    all_items = []
    for subj in subs:
        try:
            ds = load_dataset("cais/mmlu", subj, split="test")
        except Exception as e:
            print(f"  [warn] skipping MMLU {subj}: {e}")
            continue
        for i, row in enumerate(ds):
            all_items.append((subj, i, row))

    rng.shuffle(all_items)
    if n is not None:
        all_items = all_items[:n]

    out = []
    for subj, idx, row in all_items:
        opts = row["choices"]
        question = row["question"]
        gold_letter = ["A", "B", "C", "D"][row["answer"]]
        prompt = (
            f"{question}\n\n"
            f"A) {opts[0]}\n"
            f"B) {opts[1]}\n"
            f"C) {opts[2]}\n"
            f"D) {opts[3]}\n\n"
            "Answer with a single letter (A, B, C, or D) at the end of your response."
        )
        out.append(BenchmarkItem(
            benchmark="mmlu",
            item_id=f"{subj}-{idx}",
            prompt=prompt,
            gold=gold_letter,
            max_tokens=4096,
            metadata={"subject": subj, "choices": opts, "gold_idx": row["answer"]},
        ))
    return out
