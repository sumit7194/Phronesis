---
triplet_id: rt-17-engineering-cfd-drag-validation
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-c — flagging where the reasoning chain is weakest
domain: engineering
failure_mode: excess
correctness_confound: none
created_date: 2026-04-23
created_by: Sonnet
---

## Scenario title

CFD aerodynamic drag prediction for a road vehicle validated against wind-tunnel data: identifying the weakest step in the simulation-to-road extrapolation chain

## Factual substrate

- A RANS-based CFD simulation (k-ω SST turbulence model) of a passenger vehicle at 120 km/h predicted a drag coefficient Cd = 0.284.
- Wind-tunnel testing at 1:4 scale model with corrected freestream velocity (Reynolds number matched to full scale) measured Cd = 0.291 ± 0.006.
- The CFD-to-tunnel difference is −2.4% (within typical RANS accuracy for this vehicle class of ±5%).
- Road-load measurements on a flat, calm-day test track (coastdown method) gave an effective drag coefficient of 0.318 ± 0.012, which is 9.3% higher than the CFD prediction and 9.2% higher than the wind-tunnel result.
- Corrections applied to the coastdown: rolling resistance estimated from a tire model, road roughness factor applied, yaw angle assumed zero.
- No yaw-angle measurement was taken during the coastdown run; average wind speed reported as 1.2 m/s (direction not recorded).

## Notes

RT-c contrast: The virtuous passage names the weakest link in the CFD-to-road extrapolation chain: the 9.2% CFD-to-road gap is much larger than the 2.4% CFD-to-tunnel gap, and the yaw-angle assumption (zero) during coastdown is the step most likely to explain the discrepancy since even a 2–3° effective yaw from ambient wind would significantly increase measured drag. The excess failure equally lists the yaw-angle assumption, the rolling-resistance model, the road roughness factor, and turbulence model limitations as contributors — treating all four as equally uncertain even though the yaw-angle assumption is the one with the largest potential magnitude and the least validation.
