---
triplet_id: claude-eg-25-medicine-sepsis-lactate-clearance
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-a — tying claims to specific observations or data
domain: medicine
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-28
created_by: Claude Opus 4.7
failure_mode: deficiency
correctness_confound: none
---

## Scenario title
ICU sepsis cohort: lactate trajectory and 28-day mortality

## Factual substrate
- A single-centre ICU prospective cohort of 614 adults with septic shock had serial lactate measurements at 0, 6, 12, 24 h.
- 28-day mortality was 24.3% (149/614).
- Patients with lactate clearance (≥10% reduction at 6 h) had 28-day mortality 17.4%; those with <10% clearance had 33.6% (adjusted OR 0.42, 95% CI 0.28–0.62).
- Mean lactate at admission was 4.2 mmol/L (SD 1.8) in survivors and 5.6 mmol/L (SD 2.2) in non-survivors (p < 0.001).
- A subset of 218 patients had cardiac-output monitoring; lactate clearance correlated with cardiac index improvement at r = 0.41.
- A separate 92-patient sub-study compared liver-blood-flow ICG measurement to lactate clearance and found ICG-blood-flow improvement preceded lactate clearance by a median of 90 min.

## Known ambiguity
- Lactate is an outcome marker, not a treatment target by itself; lactate clearance reflects multiple physiological improvements.
- The single-centre observational design limits causal inference about treatment-driven clearance.

## Conclusion space
- Virtuous: Tie each claim to its specific observation (mortality difference, OR, cardiac-output correlation, ICG ordering).
- Deficiency: Asserts lactate clearance is prognostic without naming the OR, the cardiac-output sub-study, or the ICG ordering.
- Excess: Citation density.

## Notes
Deficiency.
