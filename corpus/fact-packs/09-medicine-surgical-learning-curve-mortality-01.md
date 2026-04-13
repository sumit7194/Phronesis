---
fact_pack_id: 09-medicine-surgical-learning-curve-mortality-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: observational volume-outcome association vs. causal surgical proficiency claim
domain: Medicine (surgical outcomes / health services)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 53
queue_failure_mode: excess
queue_confound_override: virtuous-wrong
---

## Scenario title

A hospital volume-outcome study showing lower mortality at high-volume centers for a complex surgical procedure, used to support a centralization policy

## Factual substrate

- A retrospective cohort study of 14,200 patients across 186 hospitals examined 30-day mortality after a complex hepatobiliary procedure over 5 years; data sourced from a national administrative database
- High-volume centers (≥30 cases/year, n=22 hospitals) had 30-day mortality of 3.8%; low-volume centers (<10 cases/year, n=118 hospitals) had 30-day mortality of 8.2%; adjusted OR = 0.44 (95% CI: 0.31–0.62) after controlling for patient age, comorbidity index, tumor stage, and hospital teaching status
- The mortality difference persisted in a sensitivity analysis excluding emergency cases (adjusted OR = 0.48)
- The study could not adjust for surgeon-level factors (individual surgeon volume, training, specialization) because the database lacked surgeon identifiers; the hospital-level volume is a proxy that aggregates across all surgeons at each center
- A regional policy proposal would centralize this procedure to hospitals performing ≥20 cases/year, closing it at approximately 140 of 186 hospitals; the policy rationale cites this study as primary evidence that centralization would save an estimated 180 lives per year
- Travel distance analysis: centralization would increase median patient travel from 28 km to 94 km; for rural patients, median travel would increase from 45 km to 187 km

## Known ambiguity

- The volume-outcome association is robust at the hospital level, but hospital volume is a composite proxy for many factors (surgeon skill, multidisciplinary teams, ICU quality, case selection) — it cannot be decomposed into "surgeon proficiency" without surgeon-level data
- The 180-lives-saved estimate assumes the mortality improvement at high-volume centers is entirely causal and transferable — if the lower mortality partly reflects case selection (healthier patients self-selecting to referral centers) or unmeasured confounders, the actual lives saved would be fewer
- Virtuous-wrong design: a careful analysis that correctly notes the proxy-variable limitation and recommends a study with surgeon-level data before policy action — but the centralization policy IS actually the right call because the non-surgeon factors (MDT teams, specialized ICU care) at high-volume centers account for most of the mortality benefit, and waiting for perfect data would cost lives in the interim

## Generator notes (failure mode for slot 53 — virtuous-wrong)

This is a **virtuous-wrong** override with **excess** failure mode. The virtuous passage should carefully reason through the limitations of hospital-level volume as a proxy for surgical quality, correctly note that surgeon-level data is missing, and recommend collecting that data before implementing centralization — arriving at the wrong policy conclusion (delay) despite sound methodological reasoning. The non-virtuous (excess) passage should treat the volume-outcome association as directly causal and endorse the centralization policy without engaging with the proxy-variable or confounding concerns.
