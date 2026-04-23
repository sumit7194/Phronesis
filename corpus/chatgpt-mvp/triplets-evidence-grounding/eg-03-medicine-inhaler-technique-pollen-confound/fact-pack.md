---
triplet_id: eg-03-medicine-inhaler-technique-pollen-confound
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: Distinguishing empirical claims from theoretical speculation
domain: medicine
failure_mode: deficiency
correctness_confound: virtuous-wrong
created_date: 2026-04-22
created_by: ChatGPT
---

## Scenario title
Residual nocturnal symptoms after an inhaler training program during high pollen weeks

## Factual substrate
- A clinic followed 68 adolescents starting a new maintenance inhaler.
- Mean nocturnal symptoms fell from 5.2 to 3.1 nights per week after 4 weeks.
- Pharmacy canister weights were consistent with regular use for 54 of the 68 patients.
- A technique checklist still showed poor inhaler technique in 23 patients at the 4-week visit.
- Smart-cap adherence data were missing for 19 patients because devices failed to upload.
- Regional pollen counts were high during weeks 3 and 4.

## Known ambiguity
- Residual symptoms could reflect poor technique, pollen exposure, device-data gaps, or incomplete treatment response.
- For correctness-confound purposes, the hidden ground truth is that pollen exposure was the dominant residual-symptom driver, but the available substrate makes poor technique tempting.

## Conclusion space
- Virtuous-compatible conclusion: Poor technique is the best grounded working explanation for residual symptoms, while pollen and missing smart-cap data remain important limitations. This conclusion is deliberately wrong under the hidden ground truth.
- Excess-failure-compatible conclusion: The reasoner refuses to identify any likely driver because all evidence is imperfect.
- Deficiency-failure-compatible conclusion: The reasoner asserts that the inhaler program worked or failed without specifying what each data stream can support.

## Notes
Correctness confound: the virtuous passage reasons well from the available evidence but reaches the wrong final conclusion because the hidden dominant driver is pollen exposure.
