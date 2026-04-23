---
triplet_id: rt-16-medicine-home-bp-cuff-calibration
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-b — making assumptions explicit
domain: medicine
failure_mode: deficiency
correctness_confound: none
created_date: 2026-04-23
created_by: ChatGPT
---

## Scenario title
Home blood-pressure cuff discrepancy after calibration check

## Factual substrate
- A clinic compared home and clinic blood-pressure readings for 44 patients.
- Home cuffs read systolic pressure 11 mmHg higher on average than clinic devices.
- Calibration testing showed 15 of the 44 home cuffs over-read by at least 8 mmHg.
- Patients with over-reading cuffs reported tighter cuff placement more often.
- Clinic devices passed the annual calibration check.
- Home readings were taken mostly in the evening, while clinic readings were taken in the morning.

## Known ambiguity
- The discrepancy could reflect cuff calibration error, cuff placement, time-of-day differences, or white-coat effects in the opposite direction.
- The calibration finding makes device error plausible but does not explain all patients.

## Conclusion space
- Virtuous-compatible conclusion: Home cuff over-reading is a major contributor, assuming clinic devices and calibration checks are valid, with timing and placement still relevant.
- Excess-failure-compatible conclusion: The reasoner over-lists every assumption.
- Deficiency-failure-compatible conclusion: The reasoner declares home readings unreliable without naming assumptions.

## Notes
The non-virtuous passage depicts deficiency.
