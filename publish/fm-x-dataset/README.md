---
license: cc-by-4.0
language:
- en
pretty_name: "Phronesis Activation-Steering Failure-Mode Labels (FM-X)"
tags:
- interpretability
- activation-steering
- llm-evaluation
- failure-modes
- epistemic-virtues
- hallucination
task_categories:
- text-classification
size_categories:
- 1K<n<10K
---

# Phronesis Activation-Steering Failure-Mode Labels (FM-X)

*A corpus of ~2,966 language-model generations from activation-steering experiments, each labeled with a verdict and — where the model fails — a tagged **failure mode** from a 13+ category taxonomy (FM-X). The dataset's purpose is to document, with concrete examples, **where automatic/regex scorers systematically mislabel steered LLM output** — both false positives (crediting degenerate or confabulated text) and false negatives (missing genuine behavior in non-standard prose).*

> **Author:** Sumit. **Disclosure:** labels were produced with AI assistance (Anthropic's Claude) reading each generation under a fixed human-authored protocol; they are not human-inter-rater verdicts (see *Labeling protocol* and *Limitations*). The AI is not an author.

---

## Why this dataset exists

The parent project (Phronesis) spent ~2 months (April–June 2026) trying to install epistemic virtues (intellectual humility, evidence-grounding, calibrated confidence) into small open-weight LLMs via activation steering. The single most repeated lesson was methodological: **automatic scorers are unreliable on steered output, and in a consistent, catalogable way.** A regex scorer credited a degenerate repetition-loop with the highest score in an entire α-sweep (FM-8); it missed real virtue expressed in domain-technical prose (FM-9); it counted a hedge wrapped around a confabulated fact as "abstention" (FM-1).

Rather than discard those mislabels, every one was hand-read, given a verdict, and — on failure — tagged with a reusable failure-mode code. This dataset is that labeled corpus. It is useful as: (a) a benchmark for LLM-as-judge / scorer robustness, (b) a concrete catalog of steered-LLM failure modes, and (c) the raw evidence behind the Phronesis findings.

## Contents

Three CSV batteries, one row per generation (the mechanism battery splits multi-turn generations into per-segment rows):

| File | Rows | What it covers |
|---|---|---|
| `cross_model_analysis_20260502/per_generation.csv` | 1,752 | 5 model families × virtue vectors × layer/α sweep × 9 reasoning prompts; columns include `verdict`, `failure_mode`, `note` |
| `sae_steering_analysis_20260513/per_generation.csv` | 1,110 | SAE-feature steering battery on qwen3-4b; rich per-row features (`says_dont_know`, `asserts_specific_weight`, `has_uncertainty_hedge`, …) plus `verdict`, `fm_tag`, `note` |
| `sae_mech_battery_v1_analysis/per_generation.csv` | 104 | Mechanism-shift battery (additive ±α and ablation) with per-segment `role`; `verdict`, `fm_tag`, `note` |

**Total ≈ 2,966 labeled rows.** Models span the qwen2.5 / qwen3 / deepseek-r1-distill / phi-4 / llama-3.1 families (see `model` column). All generations are greedy or low-temperature; raw model outputs and the steering vectors are in the source repository.

## The FM-X failure-mode taxonomy

Codes tag *why a verdict departs from what an automatic scorer would assign*. Scoring-relevant modes:

| Code | Failure mode | One-line description |
|---|---|---|
| **FM-1** | Hedge-wrapper confabulation | Hedge markers + a specific false claim → auto-scored as abstention; hedge is linguistic, confabulation is substantive |
| **FM-2** | Partial-confabulation uncertainty | Correct high-level frame with confabulated specifics; scorer credits the frame |
| **FM-3** | Scorer-flip on semantic-equivalents | Near-identical answers, different surface phrasing; scorer credits one not the other |
| **FM-4** | Hedge-density asymmetry | Two responses, same false claim; scorer prefers the hedgier one |
| **FM-5** | Answer-extraction edge cases | Worded numerals / LaTeX-format variance defeats the extractor |
| **FM-6** | EG confident-causation false **positive** | Evidence-vocabulary in service of a confident bad inference scored as virtuous |
| **FM-7** | EG technical-jargon false **negative** | Genuine evidence-grounding in domain prose the regex doesn't cover, scored 0 |
| **FM-8** | **Degenerate-output regex gaming** | Repetition-loop / no-`</think>`-close output wins the highest soft-score via filler tokens (*critical*) |
| **FM-9** | False-negative on clean prose | Real virtue in non-regex-matching structured prose scored 0 (the inverse of FM-8) |
| **FM-10** | Knowledge-gap fabrication | Evidence-grounding vector fabricates specific entities on ill-posed/false-premise prompts |
| **FM-13** | Commit-amplified error | Steering replaces a confused non-commit (FM-8 spiral) with a confident *wrong* commit; structure fools the scorer |
| **FM-conj-fallacy** | Conjunction fallacy | Subject-rank prompts: ranks a conjunction above its conjunct |
| **FM-no-Bayes** | Skips Bayesian update | Ignores observed evidence in a posterior-update prompt |

*(FM-11 and FM-12 are extraction-pipeline bugs, not scoring failure modes, and are documented in the source repo for completeness but do not appear as row labels.)*

The throughline (FM-8 + FM-9 together): **the auto-scorer is wrong at both ends of the quality distribution** — it over-credits degenerate output and under-credits good non-standard prose — which is why the project moved to mandatory hand-reading.

## Labeling protocol

- **Unit:** one model generation (the full text, including any `<think>` trace; the discriminating signal for several modes lives in the trace, not the final answer).
- **Verdict:** assigned by reading the full generation under a fixed rubric (abstention / confabulation / correct / degenerate, plus battery-specific fields). **Not** regex-derived.
- **Who labeled:** the readings were performed by an AI assistant (Claude) under a human-authored protocol and reviewed by the author. This is materially better than a regex auto-scorer and materially weaker than human inter-rater agreement — there is **one** labeling pass and **no** measured inter-rater reliability. Treat the labels accordingly.
- **Auto-scorer column (where present):** retained alongside the verdict so the disagreement (the whole point of the dataset) is inspectable.

## Schema (key columns)

- Common: `model`, `layer`, `alpha`, `prompt`/`prompt_id`, `verdict`, `failure_mode`/`fm_tag`, `note`.
- `cross_model`: `vector`, `prompt_class`, `think_chars`, `answer_chars`, `hit_cap`, `gen_seconds`.
- `sae_steering`: `cell`, `feature`, `is_baseline`, `quality`, `says_dont_know`, `asserts_specific_weight`, `has_uncertainty_hedge`, `has_pct_range`, `says_no_max`, `verification_disposition`, `ends_clean`, `head_60`, `tail_120`.
- `sae_mech_battery`: `feature`, `mechanism`, `role`.

## Limitations

1. **Single labeling pass, no human inter-rater.** Labels were AI-produced under a human protocol; ~4pp of rubric-drift was observed elsewhere in the project on a related hedge-classification task. Do not treat these as gold human labels.
2. **Author = protocol author = sole reviewer.** No independent adjudication.
3. **Not balanced or sampled for representativeness** — generations come from steering sweeps designed to probe specific cells, so failure modes are over-represented relative to a random LLM-output sample. This is a *failure-mode catalog*, not an unbiased prevalence estimate.
4. **Taxonomy is open and project-grown** — FM codes were added as modes were observed; the catalog is descriptive, not a closed ontology.

## Citation

```
@misc{phronesis_fmx_2026,
  author = {Sumit},
  title  = {Phronesis Activation-Steering Failure-Mode Labels (FM-X)},
  year   = {2026},
  note   = {~2,966 LLM generations labeled with verdicts and a failure-mode taxonomy (FM-1..FM-13).
            Labels AI-produced under a human protocol; see disclosure. License: CC-BY-4.0.}
}
```

## License & disclosure

Released under **CC-BY-4.0** (attribution). *License is the author's choice — CC-BY is the default here; change to CC0 for public-domain or another identifier as preferred before publishing.*

This dataset and its labels were produced with substantial AI assistance (Anthropic's Claude) under a human-authored protocol; the author reviewed and owns the protocol and the conclusions. The AI is not an author. (arXiv/HF/major-publisher norms permit AI-assisted creation with disclosure but do not permit AI as a listed author.)
