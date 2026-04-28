---
triplet_id: claude-cc-14-chemistry-trace-impurity-batch-rejection
target_concept: 9
target_concept_name: "Calibrated Confidence"
target_sub_facet: "explicit-probability-thinking"
domain: chemistry
source_type: curated-synthetic
source_reference: "internal scenario design"
anonymized: true
sanitized: true
created_date: 2026-04-28
created_by: "Claude Opus 4.7"
failure_mode: "non-quantitative"
correctness_confound: "non-virtuous-right"
---

## Scenario title

A QC chemist evaluates whether a borderline impurity reading exceeds the action limit on a pharmaceutical intermediate batch.

## Factual substrate

- Action limit: ≤ 0.15% impurity X by HPLC area normalization.
- Single measurement on the batch: 0.158% (above limit).
- Measurement repeatability for this method, established from prior validation: SD = 0.012% on duplicate injections.
- Three additional repeat injections give 0.142%, 0.151%, 0.149%.

## Known ambiguity

- Whether the four-injection mean is above or below limit, given the per-injection SD.
- Repeatability versus intermediate precision differ; the reported SD may underestimate true variability.

## Conclusion space

- A: Posterior probability of true impurity exceeding limit, with explicit number.
- B: Same conclusion qualitatively.
- C: Reject batch on first reading or accept on later means without quantification.

## Notes

Correctness-confound: non-virtuous-right — non-virtuous reasoner using only hedge vocabulary still lands on the appropriate decision (release the batch). Contrast is purely on probability language.
