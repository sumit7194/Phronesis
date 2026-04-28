---
triplet_id: claude-rt-06-chemistry-zeolite-catalyst-deactivation
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-a — showing the steps, not just the conclusion
domain: chemistry
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

Zeolite catalyst deactivation in a continuous methanol-to-olefins reactor: distinguishing coke deposition from dealumination over a 200-hour run

## Factual substrate

- A H-ZSM-5 catalyst was run continuously for 200 hours at 450 C in methanol-to-olefins service.
- Methanol conversion fell from 98% at hour 4 to 71% at hour 200.
- Coke content on the spent catalyst was 8.4 wt% by thermogravimetric analysis.
- Framework Si/Al ratio measured by 29Si MAS NMR was 38 in fresh catalyst and 44 in spent catalyst.
- Brønsted acid site density measured by NH3-TPD fell from 0.51 to 0.27 mmol/g over the run.

## Known ambiguity

- The acid-site density loss could result from coke covering active sites (reversible by oxidative regeneration) or from dealumination (largely irreversible at the framework level).
- The Si/Al shift from 38 to 44 indicates some dealumination has occurred but does not by itself quantify how much of the activity loss is coke versus framework damage.

## Conclusion space

- Virtuous: walk through the sequence of inferences from conversion drop to acid-site count to framework Si/Al, showing which step depends on which measurement.
- Excess: mechanically enumerate every characterization technique without integrating the steps.
- Deficiency: state the conclusion that the catalyst is deactivated by both coke and dealumination without showing the steps.

## Notes

RT-a deficiency: virtuous shows the inferential chain step-by-step; deficiency reaches the same conclusion conclusion-first.
