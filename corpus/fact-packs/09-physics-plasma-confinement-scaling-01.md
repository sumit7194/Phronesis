---
fact_pack_id: 09-physics-plasma-confinement-scaling-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: empirical scaling law extrapolation vs. reactor-scale prediction confidence
domain: Physics (plasma physics / fusion)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 80
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

An empirical energy confinement scaling law derived from 8 existing tokamaks, extrapolated to predict performance of a next-generation reactor 3× larger than any existing device

## Factual substrate

- An empirical scaling law for energy confinement time (τ_E) was fitted to a database of 5,400 discharges from 8 tokamaks spanning major radius R = 0.65–3.1 m; the scaling is τ_E ∝ I_p^0.93 × B_T^0.15 × R^1.97 × κ^0.78 × n_e^0.41 × P^−0.69 (IPB98(y,2)-type)
- The fit quality: R² = 0.92 across the 8-device database; the root-mean-square deviation of predicted vs. observed τ_E is 14% within the database
- The next-generation reactor design has R = 6.2 m (2× the largest device in the database), I_p = 15 MA (1.5× maximum in database), B_T = 5.3 T (within database range); the scaling law predicts τ_E = 3.8 s, yielding fusion gain Q = 10
- The extrapolation in major radius is 2× beyond the database edge; the extrapolation in plasma current is 1.5×; the magnetic field is within range
- Known physics effects not captured by the scaling law: plasma self-heating (alpha particles) at reactor scale changes the temperature profile and potentially the transport; edge localized modes (ELMs) at large radius may differ in character; isotope effects for deuterium-tritium fuel vs. the predominantly deuterium database
- Historical record: previous scaling laws (ITER89-P, IPB98(y,1)) predicted τ_E for subsequent devices within 15-30% when the extrapolation was modest (<1.5× in major radius)

## Known ambiguity

- The scaling law fits the existing database well (R² = 0.92, 14% RMSE) and has historically predicted within 15-30% for modest extrapolations
- The reactor extrapolation is not modest: 2× in major radius, into a regime with new physics (alpha heating, different ELM character, D-T fuel effects) not present in the database
- Excess failure: presenting the Q = 10 prediction as reliable based on the scaling law's in-database performance, without noting the extrapolation distance or the missing physics

## Generator notes (failure mode for slot 80)

Failure mode is **excess**. The non-virtuous passage should present the scaling law prediction as establishing that the reactor will achieve Q = 10, citing the R² = 0.92 and historical track record without acknowledging the 2× extrapolation or the unmodeled physics. The virtuous passage should affirm the scaling law as the best available prediction tool, then note that the extrapolation is larger than any previous successful prediction, and that alpha heating/ELM/isotope effects introduce physics uncertainties not captured by the empirical fit.
