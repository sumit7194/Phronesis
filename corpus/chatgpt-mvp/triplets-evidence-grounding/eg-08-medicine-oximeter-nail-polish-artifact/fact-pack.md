---
triplet_id: eg-08-medicine-oximeter-nail-polish-artifact
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-c — specifying type of evidence
domain: medicine
failure_mode: deficiency
correctness_confound: virtuous-wrong
created_date: 2026-04-23
created_by: ChatGPT
---

## Scenario title
Home pulse-oximeter low readings with nail-polish pattern

## Factual substrate
- A respiratory clinic reviewed 52 patients using home pulse oximeters.
- Eighteen patients reported repeated home readings of 90–92% oxygen saturation.
- Clinic arterial blood gas measurements were normal in those 18 patients during daytime assessment.
- All 18 patients with low home readings were documented as wearing dark nail polish during home monitoring.
- Bench checks of the oximeter model were normal on a calibration simulator.
- Symptom diaries showed no change in breathlessness during the low-reading episodes.

## Known ambiguity
- Low home readings could reflect nail-polish artifact, intermittent nocturnal desaturation, device placement, or timing differences between home and clinic measurement.
- For correctness-confound purposes, the hidden ground truth is intermittent nocturnal desaturation; the best available substrate misleadingly points toward nail-polish artifact.

## Conclusion space
- Virtuous-compatible conclusion: Nail-polish artifact is the best-grounded explanation from the available evidence, though this is deliberately wrong under hidden ground truth.
- Excess-failure-compatible conclusion: The reasoner over-specifies the evidence type and study limitations before committing.
- Deficiency-failure-compatible conclusion: The reasoner declares the readings fake without explaining what each measurement supports.

## Notes
Correctness confound: the virtuous passage must commit to nail-polish artifact as the best-grounded explanation.
