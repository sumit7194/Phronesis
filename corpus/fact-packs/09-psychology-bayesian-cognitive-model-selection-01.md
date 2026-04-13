---
fact_pack_id: 09-psychology-bayesian-cognitive-model-selection-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: under-confidence in well-fitting cognitive model despite alternative models
domain: Psychology (computational / cognitive)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 90
queue_failure_mode: deficiency
queue_confound_override: standard
---

## Scenario title

Bayesian model comparison of 4 decision-making models where one model decisively wins on all selection criteria, but a reviewer argues the model space was not exhaustive

## Factual substrate

- A behavioral experiment (n = 180 participants, 200 trials each) tested 4 competing models of risky decision-making: expected utility (EU), cumulative prospect theory (CPT), the priority heuristic (PH), and a Bayesian sampling model (BSM)
- Model fitting used hierarchical Bayesian estimation with leave-one-out cross-validation (LOO-CV); individual-level parameter recovery was validated via simulation (95% recovery rate for all models)
- LOO-CV results: BSM had the best predictive accuracy for 142 of 180 participants (79%); CPT was best for 31 (17%); EU for 5 (3%); PH for 2 (1%); group-level ΔELPD (BSM vs. CPT) = 842 ± 124 (decisive)
- Bayes factors: BF₁₀ (BSM vs. CPT) > 100 for 134 of 180 participants (decisive evidence); BF₁₀ > 10 for 158 (strong evidence)
- Posterior predictive checks: BSM accurately reproduced 6 qualitative choice patterns that CPT systematically mispredicted (including the common ratio effect magnitude and the reflection effect asymmetry)
- A reviewer argues: "The comparison is limited to 4 models. Other models in the literature (query theory, sequential sampling models, regret theory) were not tested. The BSM winning among 4 candidates does not establish it as the correct model."

## Known ambiguity

- The BSM decisively outperforms the other 3 models on all criteria — this is a clear model comparison result within the tested set
- The reviewer's point is logically valid: winning a 4-model comparison doesn't prove a model is correct, only that it's the best of the tested set; however, no specific alternative was proposed that would plausibly outperform BSM on the observed patterns
- Deficiency failure: treating the non-exhaustive model space as invalidating the model comparison result, refusing to conclude that BSM is the best-supported account despite decisive evidence within the comparison

## Generator notes (failure mode for slot 90)

Failure mode is **deficiency**. The non-virtuous passage should agree with the reviewer's critique and refuse to endorse BSM, citing the non-exhaustive model space as a fundamental limitation. The virtuous passage should affirm the decisive model comparison result within the tested set, note the reviewer's logical point while observing that no specific superior alternative has been proposed, and conclude that BSM is the best-supported model currently available while remaining open to future comparisons.
