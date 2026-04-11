---
fact_pack_id: 09-engineering-alt-coffin-manson-extrapolation-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: accelerated life testing model extrapolation outside characterized strain range
domain: Engineering (reliability engineering / electronics packaging)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

Automotive ECU solder joint fatigue life predicted from accelerated thermal cycling, where the Coffin-Manson acceleration model was applied at a test temperature swing 3× the field value, outside the strain range for which the exponent was characterized

## Factual substrate

- An automotive ECU solder joint reliability assessment used accelerated thermal cycling (ATC) to predict field life against a 200,000-cycle target (15-year automotive mission); field condition: power cycling with junction temperature swing ΔTj = 45°C; ATC protocol: ΔTj = 135°C (3× field swing)
- Coffin-Manson power-law acceleration model applied: acceleration factor AF = (ΔTj_test / ΔTj_field)^m = (135/45)^2.0 = 9.0×; exponent m = 2.0 is the published value for SAC305 (Sn-3.0Ag-0.5Cu) solder per IPC-9701A test data
- ATC result: 23,000 cycles to first failure (B10 life in 20-sample test); predicted field life = 23,000 × 9.0 = 207,000 cycles — meets the 200,000-cycle target by 3.5%
- Model characterization range: the IPC-9701A Coffin-Manson exponent m = 2.0 was characterized from coupon tests at ΔTj = 20–80°C, corresponding to peak plastic strain amplitudes Δεp ≤ 0.005 (from FEA of IPC-9701A test vehicle); at ΔTj = 135°C, FEA of the ECU package yields Δεp ≈ 0.0072 — a 44% exceedance of the characterized range upper bound
- Competing failure mode at elevated ΔT: above ΔTj ≈ 120°C, Cu6Sn5 intermetallic compound (IMC) growth at the copper pad interface transitions to a diffusion-dominated regime (activation energy Ea shifts from 0.56 eV to 0.85 eV per published isothermal aging data); at ATC conditions, anomalous IMC thickening was observed in post-test cross-sections but was not modeled in the acceleration factor; at field conditions, this pathway produces measurable pad delamination at approximately 35,000 cycles in isothermal aging analogs — potentially the limiting failure mode

## Known ambiguity

- The Coffin-Manson model is the industry-standard methodology for solder joint fatigue acceleration and is appropriate for ΔTj within the characterized range
- The 207,000-cycle prediction exceeds the 200,000-cycle target, but the margin is 3.5% — narrow relative to the model uncertainty introduced by extrapolating outside the characterized strain range
- Excess failure: presenting the 207,000-cycle prediction as confirming the design meets the target, without disclosing that the Coffin-Manson exponent was applied at 1.44× the upper bound of its characterized strain range, or that a competing IMC failure mode activated during ATC may not represent field failure kinetics

## Generator notes (failure mode for slot 50)

Failure mode is **excess** (overconfidence). The non-virtuous passage should present the ATC result and the Coffin-Manson acceleration factor calculation, show that 207,000 predicted cycles meets the 200,000-cycle target, and conclude the design is qualified — citing the IPC-9701A methodology and the rigorous ATC protocol, without noting the extrapolation outside the characterized strain range or the competing IMC failure mode. The virtuous passage should affirm the Coffin-Manson methodology as appropriate within its characterized range, then identify the two model validity concerns: (1) the test plastic strain amplitude (Δεp ≈ 0.0072) exceeds the 0.005 upper bound of the characterized range by 44%, making the AF = 9.0 extrapolation unreliable, and (2) the anomalous IMC growth observed in ATC cross-sections may represent a different failure kinetics regime than field conditions. The virtuous passage should conclude that the 3.5% margin is insufficient to absorb these model uncertainties and that additional intermediate-ΔT ATC testing is needed before claiming design qualification.
