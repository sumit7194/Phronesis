---
triplet_id: claude-cc-03-medicine-mammography-callback-ppv
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
failure_mode: "non-quantitative"
correctness_confound: "virtuous-wrong-numerics"
---

## Scenario title

A radiologist counsels a patient called back from screening for additional imaging on a category 0 finding.

## Factual substrate

- Screening center recall rate: 9.4% of screened women in the 50–69 age group.
- Of recalled women in this age group, the long-run cancer detection rate at recall is approximately 4.5% (PPV1).
- Patient is 56 with no family history and no prior abnormal screens.
- The recall is for additional views and possible ultrasound, not biopsy.

## Known ambiguity

- Patients tend to interpret a callback as much closer to a cancer diagnosis than the actual posterior probability.
- The radiologist must communicate a calibrated probability without either alarming or falsely reassuring.

## Conclusion space

- A: Communicate the modest posterior probability with explicit numbers.
- B: Communicate appropriate caution with hedge vocabulary only.
- C: Either alarm (overstating risk) or overly reassure (understating).

## Notes

Correctness-confound: virtuous-wrong-numerics — the virtuous reasoner explicitly gives a posterior of about 4.5% but slightly miscomputes a likelihood ratio in the second paragraph, while still landing on the right calibration. Process is right, one number is off.
