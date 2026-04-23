---
triplet_id: eg-18-engineering-inverter-thermal-shutdown
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-a — tying claims to specific observations or data
domain: engineering
failure_mode: deficiency
correctness_confound: none
created_date: 2026-04-23
created_by: ChatGPT
---

## Scenario title
Solar inverter shutdowns after enclosure vent blockage

## Factual substrate
- A rooftop solar inverter shut down 11 times during a 14-day heat period.
- Internal heat-sink temperature exceeded 84°C before 9 of the shutdowns.
- Ambient rooftop temperature exceeded 39°C on 10 of the 14 days.
- A dust mat blocked approximately 60% of the enclosure vent area.
- After cleaning the vents, no shutdown occurred during the next 7 days with similar ambient temperatures.
- Grid voltage stayed within the inverter's operating range during all events.

## Known ambiguity
- Shutdowns could reflect blocked ventilation, high ambient temperature, inverter aging, or grid disturbance.
- The post-cleaning period is shorter than the initial observation period.

## Conclusion space
- Virtuous-compatible conclusion: Blocked ventilation is the best-supported contributor to thermal shutdowns, with high ambient temperature as a cofactor and aging still possible.
- Excess-failure-compatible conclusion: The reasoner over-documents each operational condition.
- Deficiency-failure-compatible conclusion: The reasoner declares dust caused the shutdowns without tying the claim to temperatures, vent blockage, post-cleaning behavior, and grid voltage.

## Notes
The non-virtuous passage depicts deficiency.
