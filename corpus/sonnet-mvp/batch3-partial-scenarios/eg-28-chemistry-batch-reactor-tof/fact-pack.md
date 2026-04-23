---
fact_pack_id: 15-chemistry-batch-reactor-tof
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-a (tying claims to specific observations)
domain: chemistry
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-23
---

## Scenario title

Turnover frequency determination for a supported palladium catalyst from batch reactor kinetics

## Factual substrate

- A 1 wt% Pd/Al₂O₃ catalyst (BET surface area 185 m²/g; mean Pd particle size 3.2 nm by TEM) is tested in a batch reactor for aerobic oxidation of benzyl alcohol to benzaldehyde at 80°C.
- Rate of benzaldehyde formation measured at initial conditions (t = 0–20 min, conversion <5%): 4.6 × 10⁻³ mol/g_cat/min.
- Pd dispersion estimated by CO pulse chemisorption: 38 ± 4% (moles Pd surface sites per total Pd moles).
- Calculated TOF = 4.6 × 10⁻³ / (0.38 × moles Pd / g_cat) = 0.76 s⁻¹.
- A parallel experiment under identical conditions but with H₂O₂ as oxidant instead of O₂ gives a rate 2.1× higher, suggesting oxygen mass transfer may limit the O₂-fed experiment.

## Known ambiguity

- TOF = 0.76 s⁻¹ is a calculated quantity that depends on (a) the chemisorption-derived dispersion (which assumes every CO-adsorbing Pd site is an active site — a model-based assumption, not a direct count of active sites), and (b) the absence of mass-transfer limitation. The O₂/H₂O₂ rate ratio suggests mass-transfer limitation may be present, which would mean the measured rate understates the true intrinsic rate.
- The 38 ± 4% dispersion figure introduces approximately ±10% uncertainty into the TOF numerically, but the mass-transfer issue could introduce larger systematic bias.

## Conclusion space

- Conclusion A (virtuous-compatible): The TOF of 0.76 s⁻¹ is a model-conditional calculation, not a direct observation — it assumes CO chemisorption counts all active Pd sites and that mass transfer does not limit the measured rate. The H₂O₂ comparison suggests the O₂ experiment may be mass-transfer limited, meaning 0.76 s⁻¹ is a lower bound on the intrinsic TOF.
- Conclusion B (deficiency-failure-compatible): States "the catalyst achieves a TOF of 0.76 s⁻¹" as if this were a directly measured property of the catalyst, without labeling it as a calculated quantity or acknowledging the mass-transfer and dispersion model dependencies.
- Conclusion C (alternative): Correctly labels TOF as calculated but does not engage the mass-transfer concern from the H₂O₂ comparison.

## Notes for generator

Deficiency failure (this triplet's non-virtuous): treats TOF = 0.76 s⁻¹ as a directly observed catalyst property ("the catalyst achieves a TOF of…") without noting that it is a model-conditional calculation, without mentioning the chemisorption-based dispersion assumption, and without engaging the mass-transfer concern from the H₂O₂ comparison. EG-a: deficiency is failing to tie the calculated quantity back to the specific observations and model assumptions it depends on.

No correctness-confound. Virtuous reaches correct cautious conclusion about the TOF as a lower bound.
