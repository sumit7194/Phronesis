---
triplet_id: claude-cc-05-biology-extinction-risk-population-viability
target_concept: 9
target_concept_name: "Calibrated Confidence"
target_sub_facet: "explicit-probability-thinking"
domain: biology
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

A conservation biologist communicates a 50-year extinction probability for a small mammal population to a habitat manager.

## Factual substrate

- Remnant population estimated at 145 adults across 6 subpopulations.
- Population viability analysis (PVA) with 1,000 stochastic runs produces a 50-year extinction probability of 0.27 under current conditions.
- Sensitivity runs vary the carrying capacity ±20%; this changes the 50-year extinction probability across a range of 0.18 to 0.41.
- An additional habitat-corridor scenario reduces the median extinction probability to 0.14.

## Known ambiguity

- PVA outputs are conditional on the model structure and parameter estimates; the model itself has uncertainty that the 1,000 stochastic runs do not capture.
- The right number to communicate to the manager depends on whether the manager will read a point estimate as a settled forecast.

## Conclusion space

- A: Communicate a probability range with explicit numbers and parameter sensitivity.
- B: Communicate a single point estimate.
- C: Communicate qualitatively without numbers.

## Notes

Non-virtuous version uses hedge vocabulary ("fair chance", "non-trivial risk") to express similar caution but no numbers.
