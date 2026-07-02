# Reasoning benchmark sets (Phase 1, roadmap-2026-07)

Prepared by mvp/prepare_reasoning_sets.py, seed 7, on 2026-07-02. Do not regenerate after the
experimental slice is frozen (prereg discipline). Schema: {id, source, question, answer, subject, level, year, choices?}.

| set | n | provenance |
|---|---|---|
| gsm8k_probe | 50 | openai/gsm8k test, sample 50 (saturation probe) |
| math500 | 500 | HuggingFaceH4/MATH-500 (full test) |
| aime_2021_2024 | 103 | di-zhang-fdu/AIME_1983_2024, years 2021-2024 (Lotfi-style AIME-120) |
| gpqa_diamond | GATED-FAIL | Idavidrein/gpqa gpqa_diamond (GATED; MCQ shuffled seed 7, answer=letter) |
