---
triplet_id: eg-10-chemistry-scaleup-yield-drop
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-c — matching the appropriate evidence type to the claim
domain: chemistry
failure_mode: excess
correctness_confound: none
created_date: 2026-04-23
created_by: Sonnet
---

## Scenario title

Yield drop on scale-up of a Buchwald-Hartwig amination from 0.5 mmol to 50 mmol: matching evidence type to mechanistic claim

## Factual substrate

- A palladium-catalyzed Buchwald-Hartwig amination gave 91% isolated yield at 0.5 mmol scale in a round-bottom flask with magnetic stirring and an oil bath.
- Scale-up to 50 mmol in a 500 mL jacketed reactor with overhead stirring and the same reagent equivalences gave 67% isolated yield under nominally identical conditions (same solvent, base, ligand, Pd loading, temperature setpoint, reaction time).
- In-process HPLC at 2 h and 4 h showed the 50 mmol reaction lagging the 0.5 mmol profile by approximately 20% conversion at each timepoint.
- A thermocouple in the reaction mixture at the 50 mmol scale recorded a measured temperature of 82°C during the exothermic addition phase against a jacket setpoint of 90°C, indicating a 8°C under-temperature for approximately 15 minutes.
- Base quality (Cs₂CO₃) from the same lot was used in both scales; water content by Karl Fischer titration was 0.18% w/w.
- Oxygen ingress was not directly measured; nitrogen sparging protocol was the same in both vessels.

## Known ambiguity

- The 8°C under-temperature during addition is the only directly measured process difference between scales. All other proposed explanations (oxygen ingress, mixing inhomogeneity, base surface-area effects from larger particle aggregation) are plausible scale-up failure modes but are not directly measured in this dataset.
- The conversion lag at 2 h and 4 h is consistent with both the temperature excursion (slower initiation) and with mixing-related catalyst deactivation, or both.

## Notes

EG-c contrast: the virtuous passage matches evidence to claim — the 8°C under-temperature is a measured fact, while oxygen ingress and mixing inhomogeneity are inferred from the scale-up literature rather than observed in this run. The excess failure goes further, insisting that each mechanistic claim would require its own dedicated experiment before any diagnostic weight can be assigned — treating all proposed mechanisms as equally unevidenced when one (thermal) has direct measurement support.
