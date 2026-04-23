---
triplet_id: eg-sr-04-engineering-fea-bridge-four-evidence-types
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-c — specifying type of evidence
domain: engineering
failure_mode: excess
correctness_confound: none
source_substrate: corpus/triplets-combined/hand-09-engineering-fea-bridge-girder-validation-01
created_date: 2026-04-22
created_by: Claude (substrate-reuse)
---

## Scenario title

Composite bridge girder FEA validation: four independent evidence types converging at 1/3-scale.

## Factual substrate

- FEA model of a composite steel-concrete bridge girder built in ANSYS; HL-93 design truck at 80 km/h.
- W36×170 steel shape with 200 mm concrete slab; mesh convergence at 25 mm.
- 1/3-scale lab model instrumented with 24 strain gauges.
- FEA-predicted peak tensile stress: 218 MPa. Three lab runs: 214 ± 6, 219 ± 5, 217 ± 7 MPa.
- FEA-to-test deviations: −1.8%, +0.5%, −0.5%.
- FEA-predicted dynamic amplification factor (DAF): 1.34; AASHTO code: 1.33 (0.75% deviation).
- Independent peer review by two licensed structural engineers — no corrections recommended.
- Material properties: steel Fy = 345 MPa, E = 200 GPa; concrete f'c = 30 MPa.

## Known ambiguity

- Four distinct evidence types (numerical simulation, physical measurement at 1/3 scale, code-convention data, expert peer review) converge on validation within the lab context.
- Extrapolation from 1/3-scale lab validation to full-scale in-service use requires a separate assumption (scale effects and service-loading variability do not introduce new sources of error) that is not itself established by the four evidence types.

## Conclusion space

- Virtuous-compatible: Label the four evidence types explicitly (simulation, measurement, code-convention, peer review) and note what each does and does not establish. Flag the 1/3-scale-to-full-scale extrapolation as an assumption beyond the four evidence types.
- Excess-failure-compatible: Over-qualify every validation step with procedural scaffolding ("consistent with current best practices," "per industry guidance," "within accepted convergence tolerances") even for routine background facts.
- Deficiency-failure-compatible: Treat "the FEA is validated" as established by the numerical agreement without labeling which evidence types support what.

## Notes

The EG-c contrast: whether the reasoner labels evidence types. The excess failure uses methodological scaffolding language for procedural qualifiers, NOT by inserting the word "evidence" compulsively (the caricature mode observed in ChatGPT v1 batch is explicitly avoided here — "evidence" appears at most a few times in the non-virtuous passage).
