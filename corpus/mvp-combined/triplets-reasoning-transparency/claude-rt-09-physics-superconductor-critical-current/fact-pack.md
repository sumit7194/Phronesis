---
triplet_id: claude-rt-09-physics-superconductor-critical-current
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-c — flagging where the reasoning chain is weakest
domain: physics
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-28
created_by: Claude Opus 4.7
failure_mode: deficiency
correctness_confound: none
---

## Scenario title

Critical current measurement of a coated-conductor tape at 77 K: deciding whether a measured I_c of 312 A is real or limited by current-lead heating

## Factual substrate

- A 4 mm wide YBCO coated conductor was tested at 77 K self-field using a four-terminal voltage measurement.
- The voltage criterion of 1 microvolt/cm gave a critical current I_c = 312 A.
- The current leads at the sample ends were soft-soldered to copper terminations and were instrumented with thermocouples.
- Thermocouple readings rose from 77 K to 81 K at the higher current end during the I_c trace.
- A finite-element model of the lead heating predicts roughly 3 K of local terminal heating at 312 A under the test geometry.

## Known ambiguity

- A 4 K terminal temperature rise at one end may have locally suppressed the YBCO superconducting transition near the contact and shifted the apparent I_c lower than the bulk-tape value.
- The four-terminal voltage taps are 1 cm from the contacts, so heating-induced normal regions within the contact zone could leak voltage into the measurement region depending on tape current uniformity.

## Conclusion space

- Virtuous: identify the contact-zone heating as the load-bearing element controlling whether 312 A is the true I_c.
- Excess: catalogue every measurement uncertainty.
- Deficiency: report I_c = 312 A as the tape capability without flagging contact heating as the dominant uncertainty.

## Notes

RT-c deficiency: virtuous flags lead heating as the weak link; deficiency reports I_c without surfacing it.
