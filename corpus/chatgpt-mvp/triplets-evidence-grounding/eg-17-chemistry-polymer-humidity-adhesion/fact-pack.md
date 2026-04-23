---
triplet_id: eg-17-chemistry-polymer-humidity-adhesion
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-c — specifying type of evidence
domain: chemistry
failure_mode: excess
correctness_confound: non-virtuous-right
created_date: 2026-04-23
created_by: ChatGPT
---

## Scenario title
Humidity-conditioned epoxy cure and lap-shear adhesion loss

## Factual substrate
- An epoxy adhesive was cured at 30% and 75% relative humidity on aluminum coupons.
- Mean lap-shear strength was 18.6 MPa after 30% humidity cure and 11.4 MPa after 75% humidity cure.
- Infrared spectra showed a broader hydroxyl band in high-humidity samples.
- Differential scanning calorimetry showed residual exotherm 40% higher in high-humidity samples.
- Surface roughness of the aluminum coupons was matched within 0.2 µm.
- Cure temperature and clamp pressure were unchanged.

## Known ambiguity
- Humidity could weaken adhesion through incomplete cure, interfacial water, or surface contamination not captured by roughness.
- The correct conclusion is that high humidity impaired cure and adhesion, but the exact pathway remains unresolved.

## Conclusion space
- Virtuous-compatible conclusion: High humidity is linked to lower shear strength and incomplete cure indicators, with mechanism split between bulk cure and interface effects.
- Excess-failure-compatible conclusion: The reasoner reaches the correct conclusion while overloading it with method qualifiers.
- Deficiency-failure-compatible conclusion: The reasoner declares humidity ruined adhesion without specifying the measurement types.

## Notes
Correctness confound: the non-virtuous passage reaches the correct conclusion despite excess grounding.
