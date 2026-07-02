#!/usr/bin/env python
"""Download + normalize the Phase-1 reasoning benchmarks (roadmap-2026-07 §3).

Sources (matching Lotfi et al. 2606.00206):
  - GSM8K (openai/gsm8k, test)            -> saturation probe, n=50
  - MATH-500 (HuggingFaceH4/MATH-500)     -> full 500 kept; runtime samples from this
  - AIME 2021-2024 (di-zhang-fdu/AIME_1983_2024 filtered) -> "AIME-120"-style hard set
  - GPQA-Diamond (Idavidrein/gpqa; GATED — needs HF auth + accepted terms; falls back with a note)

Normalized schema per row: {id, source, question, answer, subject, level, year, choices?}
Output: corpus/reasoning/*.jsonl + provenance README. Deterministic (seed 7) — freeze before use.
"""
import json, os, random, hashlib
from datasets import load_dataset

OUT = "corpus/reasoning"
os.makedirs(OUT, exist_ok=True)
rng = random.Random(7)

def dump(name, rows):
    p = f"{OUT}/{name}.jsonl"
    with open(p, "w") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"[ok] {name}: {len(rows)} -> {p}")
    return len(rows)

def rid(source, text):  # stable id
    return source + "-" + hashlib.sha1(text.encode()).hexdigest()[:10]

report = {}

# ---- GSM8K probe (n=50) ----
try:
    ds = load_dataset("openai/gsm8k", "main")["test"]
    idx = rng.sample(range(len(ds)), 50)
    rows = [dict(id=rid("gsm8k", ds[i]["question"]), source="gsm8k", question=ds[i]["question"],
                 answer=ds[i]["answer"].split("####")[-1].strip(), subject="arithmetic", level="grade-school", year=None)
            for i in idx]
    report["gsm8k_probe"] = dump("gsm8k_probe", rows)
except Exception as e:
    print("[FAIL] gsm8k:", e); report["gsm8k_probe"] = f"FAIL {e}"

# ---- MATH-500 (full) ----
try:
    ds = load_dataset("HuggingFaceH4/MATH-500")["test"]
    rows = [dict(id=rid("math500", r["problem"]), source="math500", question=r["problem"],
                 answer=r["answer"], subject=r.get("subject"), level=str(r.get("level")), year=None)
            for r in ds]
    report["math500"] = dump("math500", rows)
except Exception as e:
    print("[FAIL] math500:", e); report["math500"] = f"FAIL {e}"

# ---- AIME 2021-2024 (~120) ----
try:
    ds = load_dataset("di-zhang-fdu/AIME_1983_2024")["train"]
    rows = []
    for r in ds:
        yr = int(r.get("Year", 0))
        if 2021 <= yr <= 2024:
            rows.append(dict(id=rid("aime", r["Question"]), source="aime", question=r["Question"],
                             answer=str(r["Answer"]), subject="competition-math", level="AIME", year=yr))
    report["aime_2021_2024"] = dump("aime_2021_2024", rows)
except Exception as e:
    print("[FAIL] aime:", e); report["aime_2021_2024"] = f"FAIL {e}"

# ---- GPQA-Diamond (gated) ----
try:
    ds = load_dataset("Idavidrein/gpqa", "gpqa_diamond")["train"]
    rows = []
    for r in ds:
        opts = [r["Correct Answer"], r["Incorrect Answer 1"], r["Incorrect Answer 2"], r["Incorrect Answer 3"]]
        order = list(range(4)); rng.shuffle(order)
        choices = [opts[j].strip() for j in order]
        correct_letter = "ABCD"[order.index(0)]
        rows.append(dict(id=rid("gpqa", r["Question"]), source="gpqa_diamond", question=r["Question"].strip(),
                         answer=correct_letter, choices=choices, subject=r.get("High-level domain"),
                         level="graduate", year=None))
    report["gpqa_diamond"] = dump("gpqa_diamond", rows)
except Exception as e:
    print(f"[FAIL] gpqa (gated — accept terms at hf.co/datasets/Idavidrein/gpqa + `huggingface-cli login`): {type(e).__name__}")
    report["gpqa_diamond"] = "GATED-FAIL"

with open(f"{OUT}/README.md", "w") as f:
    f.write("# Reasoning benchmark sets (Phase 1, roadmap-2026-07)\n\n"
            "Prepared by mvp/prepare_reasoning_sets.py, seed 7, on 2026-07-02. Do not regenerate after the\n"
            "experimental slice is frozen (prereg discipline). Schema: {id, source, question, answer, subject, level, year, choices?}.\n\n"
            "| set | n | provenance |\n|---|---|---|\n"
            f"| gsm8k_probe | {report.get('gsm8k_probe')} | openai/gsm8k test, sample 50 (saturation probe) |\n"
            f"| math500 | {report.get('math500')} | HuggingFaceH4/MATH-500 (full test) |\n"
            f"| aime_2021_2024 | {report.get('aime_2021_2024')} | di-zhang-fdu/AIME_1983_2024, years 2021-2024 (Lotfi-style AIME-120) |\n"
            f"| gpqa_diamond | {report.get('gpqa_diamond')} | Idavidrein/gpqa gpqa_diamond (GATED; MCQ shuffled seed 7, answer=letter) |\n")
print("\n[report]", json.dumps(report))
