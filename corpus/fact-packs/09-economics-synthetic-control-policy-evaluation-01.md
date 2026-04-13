---
fact_pack_id: 09-economics-synthetic-control-policy-evaluation-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: under-confidence in well-constructed synthetic control estimate
domain: Economics (public policy / causal inference)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 71
queue_failure_mode: deficiency
queue_confound_override: standard
---

## Scenario title

A synthetic control method evaluation of a state-level cannabis legalization policy on traffic fatalities, with strong pre-treatment fit and placebo-validated inference

## Factual substrate

- A synthetic control study evaluated the effect of recreational cannabis legalization in State A on traffic fatality rates; the synthetic control was constructed from a donor pool of 38 non-legalizing states, weighted to match State A's pre-treatment trajectory over 10 years (2006-2015); legalization occurred in 2016
- Pre-treatment fit: the synthetic control matched State A's traffic fatality rate within 0.3 fatalities per 100,000 for all 10 pre-treatment years; root mean squared prediction error (RMSPE) = 0.24
- Post-treatment (2016-2020): State A's traffic fatality rate was 2.1 per 100,000 higher than the synthetic control, an increase of approximately 18% relative to the counterfactual
- Placebo tests: the same synthetic control procedure was applied to all 38 donor states (as if each had legalized); State A's post/pre RMSPE ratio ranked 1st out of 39 (p < 0.026, one-sided); only 1 of 38 placebos showed a larger post-treatment gap than State A
- Leave-one-out robustness: removing any single donor state from the pool changed the estimated effect by less than 0.4 fatalities per 100,000 (the result is not driven by any single comparison state)
- The donor pool weights: 4 states received weights > 0.05 (contributing 78% of the synthetic control); the remaining 34 states received near-zero weights

## Known ambiguity

- The synthetic control is well-constructed by standard criteria: excellent pre-treatment fit, significant placebo rank, robust to leave-one-out
- The method assumes no other concurrent shocks affected State A's traffic fatalities differently from the synthetic control; a concurrent opioid crisis intervention in State A (2017) is a potential confounder
- Deficiency failure: dismissing the synthetic control result because "n=1 case studies cannot establish causation" or because the placebo test "only tests against random permutation, not against confounders"

## Generator notes (failure mode for slot 71)

Failure mode is **deficiency**. The non-virtuous passage should refuse to draw causal conclusions from the synthetic control estimate, citing the n=1 design and questioning whether placebo tests constitute real inference. The virtuous passage should affirm the synthetic control as a credible causal estimate given the strong pre-treatment fit and placebo validation, while noting the concurrent opioid intervention as a specific (not generic) confounding concern that warrants investigation.
