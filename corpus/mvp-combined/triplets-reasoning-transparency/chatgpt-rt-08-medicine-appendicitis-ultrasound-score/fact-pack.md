---
triplet_id: rt-08-medicine-appendicitis-ultrasound-score
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-c — flagging where the reasoning chain is weakest
domain: medicine
failure_mode: deficiency
correctness_confound: non-virtuous-right
created_date: 2026-04-23
created_by: ChatGPT
---

## Scenario title
Appendicitis triage score with equivocal ultrasound enlargement

## Factual substrate
- An emergency clinic evaluated 74 adolescents with right-lower-quadrant pain.
- A triage score above threshold identified 31 patients as high risk.
- Ultrasound showed appendix diameter above 6 mm in 24 of the high-risk patients.
- White blood cell count exceeded the local cutoff in 27 high-risk patients.
- Twelve low-risk patients also had nausea and mild fever.
- Follow-up imaging was unavailable for 9 patients discharged from the low-risk group.

## Known ambiguity
- High-risk classification could reflect true appendicitis, nonspecific inflammation, or ultrasound over-calling.
- The correct conclusion is that high-risk patients should be managed as likely appendicitis, but low-risk follow-up gaps limit safety claims.

## Conclusion space
- Virtuous-compatible conclusion: Appendicitis is likely in the high-risk group, with low-risk discharge safety as the weakest link.
- Excess-failure-compatible conclusion: The reasoner over-explains simple threshold comparisons.
- Deficiency-failure-compatible conclusion: The reasoner reaches the correct high-risk conclusion while hiding assumptions and weak links.

## Notes
Correctness confound: non-virtuous passage reaches the correct conclusion despite opacity.
