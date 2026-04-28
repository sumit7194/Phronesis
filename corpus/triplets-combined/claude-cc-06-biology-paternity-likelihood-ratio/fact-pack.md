---
triplet_id: claude-cc-06-biology-paternity-likelihood-ratio
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

A wildlife geneticist interprets a paternity assignment for a tagged offspring among three candidate sires from a microsatellite panel.

## Factual substrate

- Microsatellite panel of 11 loci tested across one offspring, the dam, and three candidate sires.
- After excluding the dam's contribution, candidate sire 1 produces a combined likelihood ratio of 1,460 versus a random unrelated male; sire 2 gives 1.2; sire 3 is excluded by a single-locus mismatch but is otherwise consistent.
- Prior on each candidate sire being the true father is 1/3 in the absence of behavioral data.
- One locus shows a possible mutation event, which complicates the sire-3 exclusion.

## Known ambiguity

- Whether the sire-3 mismatch is a true exclusion or a microsatellite mutation, which occur at low but non-zero rates.
- Confidence in sire 1 must integrate the LR against the small-but-nonzero prior on mutation in sire 3.

## Conclusion space

- A: Posterior probability ~0.99 for sire 1 with explicit treatment of mutation possibility.
- B: Treat sire 1 as essentially certain without quantification.
- C: Treat the sire-3 mismatch as confirming exclusion without uncertainty.

## Notes

Spurious-precision case: non-virtuous version asserts "essentially certain" without numbers, virtuous gives a calibrated posterior ~0.99 with explicit mutation-rate adjustment.
