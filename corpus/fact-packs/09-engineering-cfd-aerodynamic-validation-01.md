---
fact_pack_id: 09-engineering-cfd-aerodynamic-validation-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: CFD simulation at validated conditions vs. off-design extrapolation
domain: Engineering (aerospace / fluid dynamics)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 95
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

A RANS CFD simulation of an aircraft wing validated against wind tunnel data at cruise conditions, extrapolated to predict performance at high angle-of-attack stall conditions

## Factual substrate

- A Reynolds-Averaged Navier-Stokes (RANS) CFD simulation using the SST k-ω turbulence model was performed for a transport aircraft wing section; mesh: 14.2 million cells, y+ < 1 wall resolution; grid convergence study confirmed <0.5% change between medium and fine meshes
- Wind tunnel validation at cruise conditions (α = 2°, Re = 6 × 10⁶, M = 0.78): CFD-predicted lift coefficient CL = 0.482 vs. wind tunnel CL = 0.478 (0.8% error); drag coefficient CD = 0.0218 vs. wind tunnel CD = 0.0224 (2.7% error); pressure distribution Cp matched within measurement uncertainty at 95% of chord stations
- The simulation was used to predict performance at α = 14° (near stall): CFD predicts CL_max = 1.62 and stall angle α_stall = 15.2°
- RANS with SST k-ω is known to poorly predict massively separated flows; at high α, the boundary layer separates over a large portion of the upper surface, creating unsteady separation that RANS steady-state solutions cannot capture; the literature reports RANS CL_max overprediction of 5–15% for similar configurations
- No wind tunnel data exists at α = 14° for this specific configuration; the stall prediction has not been validated
- The predicted CL_max is being used for structural load sizing at the flight envelope boundary

## Known ambiguity

- The cruise-condition validation is excellent (< 3% error on forces, pressure distribution matched)
- RANS turbulence models are fundamentally limited for massively separated flows; the high-α prediction is an extrapolation to a flow regime where the model is known to be unreliable
- Excess failure: citing the cruise-condition validation as establishing the CFD's reliability for stall prediction, ignoring the RANS limitation for separated flows

## Generator notes (failure mode for slot 95)

Failure mode is **excess**. The non-virtuous passage should present the cruise-condition validation as establishing CFD credibility across the entire angle-of-attack range, endorsing the stall prediction for structural sizing. The virtuous passage should affirm the cruise validation while clearly noting that RANS CFD reliability does not extend to the separated-flow regime near stall, and that the CL_max prediction should not be used for structural sizing without experimental validation or higher-fidelity simulation (DES/LES).
