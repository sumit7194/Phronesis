---
triplet_id: claude-cc-02-medicine-antibiotic-susceptibility-update
target_concept: 9
target_concept_name: "Calibrated Confidence"
target_sub_facet: "explicit-probability-thinking"
domain: medicine
source_type: curated-synthetic
source_reference: "internal scenario design"
anonymized: true
sanitized: true
created_date: 2026-04-28
created_by: "Claude Opus 4.7"
failure_mode: "spurious-precision"
correctness_confound: "none"
---

## Scenario title

A hospital pharmacist updates an empirical antibiotic choice as susceptibility data arrive.

## Factual substrate

- Hospital antibiogram from the prior 12 months shows 64% susceptibility to first-line antibiotic A among the relevant gram-negative isolates, based on 2,180 cultures.
- A new 6-month update from 1,030 cultures shows 51% susceptibility to A — a meaningful drop.
- Patient is moderately ill but stable; cultures are pending and will be available in roughly 36 hours.
- Second-line antibiotic B has 89% susceptibility but broader spectrum and higher Clostridioides difficile risk.

## Known ambiguity

- The 6-month sample is smaller (1,030 vs. 2,180) and may reflect a real shift, sampling fluctuation, or a recent outbreak strain.
- Spurious-precision risk: stating a susceptibility number to one decimal point as if it were settled, when the underlying confidence interval is wider.

## Conclusion space

- A: Update empirical choice probabilistically, weighted toward second-line given declining susceptibility.
- B: Stay with first-line because "the data look similar" without quantification.
- C: Switch fully to second-line based on point estimate alone.

## Notes

Spurious-precision case: non-virtuous version offers a precise-sounding "94.3% likely" number that isn't supportable; virtuous gives a calibrated range.
