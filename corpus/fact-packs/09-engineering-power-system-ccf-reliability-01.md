---
fact_pack_id: 09-engineering-power-system-ccf-reliability-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: earned vs. unearned system availability conclusion
domain: Engineering (power systems reliability)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

N+1 redundant UPS system assessed for availability at a critical data center, where the system meets the availability target even with common cause failures — but a non-virtuous analysis reaches that correct conclusion without checking

## Factual substrate

- A data center UPS installation uses three parallel UPS units (N+1 configuration: two required for full load, one spare); each unit has a published MTBF of 120,000 hours and MTTR of 8 hours
- Independent unit availability A = 0.999933; system availability for N+1 with independent failures: A_sys = 0.999999993 (approximately six nines, 99.9999993%)
- The 99.999% (five nines) facility availability target requires no more than 5.26 minutes downtime per year
- A common cause failure (CCF) analysis using the beta factor model with β = 0.02 (an aggressive CCF assumption for the UPS class): λ_CCF = β × λ_unit = 0.02/120,000 hr = 1.67 × 10⁻⁷ per hour; system unavailability from CCF = λ_CCF × MTTR = 1.33 × 10⁻⁶; system availability from CCF = 0.9999987; combined system availability including independent and CCF failures: A_total ≈ 0.9999987 (99.99987%), which meets the five-nines target
- Identified CCF exposure modes: shared electrical panel (single panel fault; mitigated by two-panel configuration), shared cooling unit (single cooling failure; a maintenance record shows cooling redundancy was installed in year 1), and identical firmware on all units (firmware update risk; mitigation: staggered firmware update policy in effect)
- Historical data from similar installations shows approximately 15% of multi-unit UPS failures are CCF events; with β = 0.02 this is conservative and consistent with the historical rate given the existing mitigations

## Known ambiguity

- The system does meet the 99.999% target even when CCF is properly analyzed with the conservative β = 0.02 assumption
- The correct conclusion is that the system meets the target — but this conclusion is earned only by performing the CCF analysis and confirming that the mitigations reduce β to an appropriate level
- Non-virtuous-right (excess): the non-virtuous passage concludes "the system meets the 99.999% target" by presenting only the six-nines independent failure calculation, without mentioning CCF or confirming that CCF mitigations are adequate — the conclusion is correct, but the reasoning ignores the failure mode that actually determines whether the target is met

## Conclusion space

- The system meets the five-nines availability target, which is the correct conclusion
- Non-virtuous-right: reaches this conclusion via the independent failure analysis only, implicitly assuming CCF is not relevant or already addressed; correct conclusion, incomplete reasoning
- Virtuous: earns the same conclusion by explicitly performing the CCF analysis, identifying the shared failure pathways, confirming that mitigations reduce CCF exposure, and showing the combined availability (99.99987%) meets the target with margin

## Generator notes (failure mode for slot 48 — non-virtuous-right override)

This is a **non-virtuous-right** override with **excess** failure mode. The non-virtuous passage should present the N+1 redundancy calculation yielding six-nines availability and conclude that the 99.999% target is met, without discussing common cause failures or confirming that the identified CCF exposure modes (shared panel, shared cooling, shared firmware) have been mitigated. It should use the independent failure calculation as if it were the system availability. The virtuous passage should perform the full reliability analysis: present the independent failure calculation, identify the CCF pathways, apply the beta factor model with β = 0.02, show the combined availability of 99.99987%, and confirm the target is met — while noting that the conclusion is only trustworthy because the CCF analysis was done and the mitigations are confirmed.
