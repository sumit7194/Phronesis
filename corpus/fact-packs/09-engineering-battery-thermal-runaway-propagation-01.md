---
fact_pack_id: 09-engineering-battery-thermal-runaway-propagation-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: single-cell abuse test vs. pack-level thermal propagation confidence
domain: Engineering (energy storage / safety)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 97
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

Single-cell nail penetration tests showing a lithium-ion cell passes safety criteria, used to certify pack-level thermal runaway safety without pack-level propagation testing

## Factual substrate

- A 50 Ah NMC811 lithium-ion cell was subjected to nail penetration testing per UL 2580; 10 cells tested at 100% SOC; results: 8 of 10 cells vented without flame (pass); 2 of 10 produced brief flame that self-extinguished within 5 seconds (pass per UL criteria); maximum cell surface temperature: 680°C; no explosion in any test
- The cells are assembled into a 96-cell battery pack (4P24S configuration) with 3 mm cell-to-cell spacing, aluminum bus bars, and a passive thermal management system (phase-change material between cells)
- Cell-level thermal runaway characteristics: peak heat generation rate = 42 kW per cell; total energy release = 1.8 MJ per cell; onset-to-peak time = 12 seconds
- No pack-level thermal propagation test has been conducted; the certification submission cites the cell-level results and a thermal simulation (2D FEA, steady-state, linearized heat transfer) predicting that the PCM absorbs sufficient energy to prevent propagation to adjacent cells
- The thermal simulation uses a constant heat transfer coefficient of 25 W/m²K for the cell surface — a value derived from natural convection correlations, not measured during thermal runaway conditions where gas venting and flame alter the convective environment
- Pack-level propagation test data from a similar (but not identical) cell chemistry and pack design showed propagation occurred in 3 of 5 tests when cell spacing was less than 5 mm

## Known ambiguity

- The cell-level safety tests are valid: the cells pass UL 2580 nail penetration criteria individually
- Pack-level thermal propagation is a different failure mode: even cells that pass individually can propagate thermal runaway to neighbors through conduction, radiation, and convective heating of ejected gas; the 3 mm spacing is below the 5 mm threshold where propagation was observed in similar designs
- Excess failure: treating cell-level pass as evidence of pack-level safety, ignoring the propagation concern

## Generator notes (failure mode for slot 97)

Failure mode is **excess**. The non-virtuous passage should present the cell-level test results as establishing battery safety, citing the UL pass and the thermal simulation without noting the simulation's linearization assumptions or the lack of pack-level testing. The virtuous passage should affirm the cell-level results while clearly distinguishing cell safety from pack-level propagation risk, noting the 3 mm spacing concern (below the 5 mm propagation threshold from similar designs) and the simulation's unrealistic heat transfer assumptions.
