---
fact_pack_id: 09-engineering-mtbf-model-radiation-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: hardware reliability model vs. system-level failure mode coverage
domain: Engineering (systems reliability / embedded systems)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

An embedded control system reliability model based on MIL-HDBK-217 component failure rates, applied in a high-radiation environment where software-hardware interaction failures are the dominant failure mode

## Factual substrate

- A reliability analysis for an embedded control unit (ECU) in a space instrument used MIL-HDBK-217F component failure rate predictions; predicted MTBF from the model: 42,000 hours (5-year mission); hardware component counts: 847 ICs, 2,340 passive components, 12 connectors; temperature-derated failure rates applied
- The ECU operates in a 100 krad(Si) total ionizing dose (TID) environment over mission life; the radiation environment produces single-event upsets (SEUs) in SRAM and flip-flop elements at a rate of 1.2 × 10⁻⁷ upsets/bit/day based on published cross-section data
- The control software occupies 128 KB of SRAM (1,048,576 bits); expected SEU rate in software memory: approximately 0.045 upsets/day; at this rate, approximately 1 software corruption event every 22 days is expected without error detection/correction (EDAC)
- The ECU firmware does not include EDAC on the primary SRAM segment used for control variables; the watchdog timer recovery mechanism clears faults within 4 seconds but does not prevent corrupted state propagation for control variable segments
- MIL-HDBK-217 does not model SEU-induced software faults; the predicted MTBF of 42,000 hours captures only physical component wear-out and random hardware failures — the radiation-induced software corruption pathway is structurally absent from the model

## Known ambiguity

- The MIL-HDBK-217 MTBF prediction is valid for what it models: physical component failure under thermal and electrical stress
- The actual MTBF in the radiation environment is limited by the SEU rate in unprotected SRAM, not by component wear-out; 0.045 upsets/day in control SRAM without EDAC means the effective MTBF from software corruption alone is approximately 22 days — three orders of magnitude shorter than the predicted 42,000 hours
- Excess failure: presenting the 42,000-hour MTBF as the system reliability without disclosing that the model does not cover the dominant failure mode in this environment

## Conclusion space

- The MIL-HDBK-217 MTBF of 42,000 hours is a valid estimate for hardware component failures and should be reported as such
- The system-level MTBF in the actual radiation environment is dominated by SEU-induced software corruption at approximately 22 days, a failure mode not captured by the model
- Excess failure: reporting 42,000 hours as the ECU MTBF without noting that the radiation-induced software corruption pathway — the dominant failure mode — is outside the model's scope

## Generator notes (failure mode for slot 46)

Failure mode is **excess** (overconfidence). The non-virtuous passage should present the MIL-HDBK-217 MTBF of 42,000 hours as the system reliability, noting the rigorous component-level analysis and the temperature derating, without acknowledging that radiation-induced software corruption is not captured by the model and will dominate the actual failure rate. The virtuous passage should affirm the MIL-HDBK-217 analysis as valid for hardware wear-out and random failure, then explicitly identify the missing failure mode: SEU-induced software corruption in unprotected SRAM at 0.045 upsets/day gives an effective MTBF from this pathway alone of ~22 days, requiring EDAC implementation before the hardware-model MTBF has any practical meaning.
