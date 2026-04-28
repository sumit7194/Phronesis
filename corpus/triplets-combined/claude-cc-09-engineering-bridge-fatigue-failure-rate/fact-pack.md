---
triplet_id: claude-cc-09-engineering-bridge-fatigue-failure-rate
target_concept: 9
target_concept_name: "Calibrated Confidence"
target_sub_facet: "explicit-probability-thinking"
domain: engineering
source_type: curated-synthetic
source_reference: "internal scenario design"
anonymized: true
sanitized: true
created_date: 2026-04-28
created_by: "Claude Opus 4.7"
failure_mode: "non-quantitative"
correctness_confound: "none"
---

## Scenario title

A structural engineer estimates the 10-year probability of fatigue crack initiation at a critical weld detail on an aging steel bridge.

## Factual substrate

- Bridge in service 38 years; design life 75 years.
- Inspection identifies 4 weld details with measurable fatigue indicators across 22 inspected details.
- S-N curve data for the weld class give a 10-year crack-initiation probability of 0.06 per detail under measured traffic loads, with a coefficient of variation of about 0.4 on the underlying stress range.
- Traffic loads have grown 18% above design assumptions over the past decade.

## Known ambiguity

- Whether the 4 affected details represent the detail population or are an outlier batch from a fabrication run.
- Traffic growth probably means the historical S-N curve underestimates current and future fatigue rates.

## Conclusion space

- A: 10-year detail-level probability quantified with credible interval.
- B: Same picture qualitatively.
- C: Either alarm (replace bridge) or false reassure (no action).

## Notes

Numerical Bayesian update from per-detail prior of 0.06 to posterior incorporating 4/22 already showing indicators, plus traffic-growth correction.
