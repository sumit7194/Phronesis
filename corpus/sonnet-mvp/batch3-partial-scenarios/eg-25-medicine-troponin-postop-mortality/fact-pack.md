---
fact_pack_id: 15-medicine-troponin-postop-mortality
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-a (tying claims to specific observations)
domain: medicine
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-23
---

## Scenario title

Post-operative high-sensitivity cardiac troponin elevation and 30-day mortality after major non-cardiac surgery

## Factual substrate

- A prospective cohort of 12,400 patients undergoing elective major non-cardiac surgery measured high-sensitivity troponin T (hsTnT) at 24 and 48 hours post-operatively.
- Patients with peak hsTnT ≥ 65 ng/L had a 30-day mortality rate of 8.7% (n = 1,840) versus 1.2% in those with peak hsTnT < 65 ng/L (n = 10,560); unadjusted OR = 7.9 (95% CI: 6.4–9.7).
- After adjustment for pre-operative cardiac risk score, surgical complexity, and comorbidities, the adjusted OR = 3.4 (95% CI: 2.7–4.3).
- Two independent RCTs (n = 820 combined) of post-operative aspirin and statin therapy in hsTnT-elevated patients showed no reduction in 30-day mortality (pooled RR: 0.94, 95% CI: 0.76–1.15).
- Sub-group analyses by surgery type (vascular, colorectal, hepatobiliary) showed ORs of 4.1, 3.0, and 2.9 respectively — all in the same direction and overlapping with the overall estimate.

## Known ambiguity

- Elevated hsTnT post-operatively may represent myocardial injury from multiple mechanisms (demand ischemia, inflammation, non-ischemic myocardial injury) — the cause of elevation is not determined by the measurement itself.
- The two RCTs of aspirin/statin therapy are underpowered and the point estimates are close to 1.0; the lack of demonstrated benefit does not rule out benefit in specific sub-groups or at different therapeutic timing.

## Conclusion space

- Conclusion A (virtuous-compatible): Peak hsTnT ≥ 65 ng/L is a strong prognostic marker (adjusted OR 3.4) in this prospective cohort, established through direct observation in 12,400 patients; the absence of demonstrated treatment benefit in two small RCTs does not negate the prognostic value but leaves the therapeutic pathway open.
- Conclusion B (excess-failure-compatible): The adjusted OR = 3.4 is presented but then burdened with sub-group ORs for each surgery type, the unadjusted OR, the specific covariates in the adjustment model, and the RCT pooled RR — every sentence has a multi-clause evidence chain that makes the overall picture hard to extract.
- Conclusion C (deficiency-failure-compatible): Omits the distinction between unadjusted and adjusted OR, states the finding as "surgery with elevated troponin doubles mortality" without specifying it comes from a prospective observational cohort.

## Notes for generator

Excess failure (this triplet's non-virtuous): every specific claim about the troponin–mortality link is tagged with its specific evidence provenance — unadjusted OR with its CI, adjusted OR with covariate list, sub-group ORs for each of three surgery types, and the RCT pooled RR — making the passage feel like a systematic review appendix rather than a clinical reasoning passage. EG-a sub-facet; excess means over-specifying each claim's evidence chain. No correctness-confound.
