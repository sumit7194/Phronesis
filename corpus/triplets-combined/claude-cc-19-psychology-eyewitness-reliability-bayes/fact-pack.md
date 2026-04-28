---
triplet_id: claude-cc-19-psychology-eyewitness-reliability-bayes
target_concept: 9
target_concept_name: "Calibrated Confidence"
target_sub_facet: "explicit-probability-thinking"
domain: psychology
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

A forensic psychologist evaluates the diagnostic value of a high-confidence eyewitness identification under suboptimal viewing conditions.

## Factual substrate

- Witness identifies suspect from a six-person photo lineup, expressed confidence "very high."
- Viewing conditions at the original event: 4 seconds of exposure at approximately 25 meters in low light.
- Meta-analytic estimate from approximately 11,000 lab and field IDs: P(correct ID | high confidence, suboptimal viewing) ≈ 0.55; P(correct ID | high confidence, good viewing) ≈ 0.85.
- Base rate: in this jurisdiction's review, suspects placed in lineups are the actual perpetrator approximately 35% of the time.

## Known ambiguity

- High witness confidence is much less informative under poor viewing than juries typically infer.
- The right communication to the trial team is a calibrated probability, not a binary reliable/unreliable.

## Conclusion space

- A: Quantified posterior probability of correct identification with explicit numbers.
- B: Same conclusion qualitatively.
- C: Either trust high-confidence ID or dismiss it without quantification.

## Notes

Non-quantitative failure mode. Calibration matched on both versions; difference is whether numerical posteriors appear.
