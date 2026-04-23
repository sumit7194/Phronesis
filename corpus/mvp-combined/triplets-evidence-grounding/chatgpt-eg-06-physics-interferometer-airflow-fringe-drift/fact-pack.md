---
triplet_id: eg-06-physics-interferometer-airflow-fringe-drift
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-a — tying claims to specific observations or data
domain: physics
failure_mode: deficiency
correctness_confound: none
created_date: 2026-04-23
created_by: ChatGPT
---

## Scenario title
Airflow-associated fringe drift in a tabletop interferometer

## Factual substrate
- A tabletop laser interferometer was monitored for 10-minute runs with a cooling fan off and on.
- With the fan off, fringe drift averaged 0.6 fringes per 10 minutes.
- With the fan on, fringe drift averaged 3.4 fringes per 10 minutes.
- Beam power varied by less than 0.5% across both conditions.
- Temperature probes near the arms changed by less than 0.1°C.
- An accelerometer on the optical table showed vibration amplitude increased fourfold when the fan was on.

## Known ambiguity
- The fan could have caused drift through vibration, airflow-driven refractive-index changes, or a small unmeasured thermal gradient.
- The measurements show association with fan state but do not isolate the physical pathway.

## Conclusion space
- Virtuous-compatible conclusion: The fan-on condition is grounded as the source of larger fringe drift, with vibration the leading measured pathway and airflow still possible.
- Excess-failure-compatible conclusion: The reasoner over-documents every measurement and procedural limit before making a simple apparatus claim.
- Deficiency-failure-compatible conclusion: The reasoner declares vibration caused the drift without tying that claim to the accelerometer and stability measurements.

## Notes
The non-virtuous passage depicts deficiency: confident source attribution without adequate claim-data linkage.
