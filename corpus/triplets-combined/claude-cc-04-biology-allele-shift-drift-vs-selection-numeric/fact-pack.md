---
triplet_id: claude-cc-04-biology-allele-shift-drift-vs-selection-numeric
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

A population geneticist places posterior probabilities on drift versus selection for a four-generation allele shift in an isolated lizard population.

## Factual substrate

- Isolated island lizard population, effective population size Ne estimated at about 480.
- Allele frequency at locus L tracked across four generations: 0.31, 0.36, 0.41, 0.45.
- Theoretical drift variance per generation given Ne predicts a standard deviation of allele frequency change of roughly 0.011.
- Observed cumulative shift of +0.14 over four generations.

## Known ambiguity

- The shift is plausibly explained by drift alone if Ne is overestimated, by weak directional selection (s ~ 0.02), or by a mixture.
- Without an independent fitness measurement, the data alone cannot fully resolve the two hypotheses.

## Conclusion space

- A: Posterior weighted toward selection given the size of the shift relative to drift expectation.
- B: Treat the result as ambiguous between drift and selection.
- C: Confidently call selection without quantifying.

## Notes

This scenario differs from existing allele-frequency triplets in the corpus in being explicitly framed as a posterior over hypotheses with numerical updates rather than as a calibration-strength contrast.
