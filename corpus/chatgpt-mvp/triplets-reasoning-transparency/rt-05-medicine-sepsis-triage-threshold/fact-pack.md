---
triplet_id: rt-05-medicine-sepsis-triage-threshold
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: Making assumptions explicit
domain: medicine
failure_mode: deficiency
correctness_confound: none
created_date: 2026-04-22
created_by: ChatGPT
---

## Scenario title
Emergency triage sepsis score threshold and false-alarm burden

## Factual substrate
- An emergency department tested a sepsis triage score on 900 visits.
- The original threshold flagged 142 visits, including 29 true sepsis cases.
- The original threshold missed 8 sepsis cases.
- Many false positives were patients with chronic kidney disease and elevated lactate.
- A stricter threshold would flag 103 visits and miss 13 sepsis cases.
- Each flagged visit required about 4 minutes of clinician review.

## Known ambiguity
- The decision trades sensitivity against review burden and false positives from chronic kidney disease.
- The right threshold depends on how the department values missed sepsis cases versus additional review minutes.

## Conclusion space
- Virtuous-compatible conclusion: Keep the original threshold unless review capacity is the binding constraint, because the stricter threshold saves review time but misses 5 more sepsis cases.
- Excess-failure-compatible conclusion: The reasoner over-derives simple arithmetic and threshold tradeoffs.
- Deficiency-failure-compatible conclusion: The reasoner announces a threshold preference without making the value tradeoff visible.

## Notes
The non-virtuous passage depicts deficiency: polished decision prose with hidden assumptions.
