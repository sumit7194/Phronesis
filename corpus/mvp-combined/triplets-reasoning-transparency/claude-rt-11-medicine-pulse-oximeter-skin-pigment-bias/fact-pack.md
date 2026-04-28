---
triplet_id: claude-rt-11-medicine-pulse-oximeter-skin-pigment-bias
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-b — making assumptions explicit
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

Pulse oximeter accuracy across skin pigmentation in an ICU cohort: estimating the rate of occult hypoxemia from paired SpO2 and arterial blood gas readings

## Factual substrate

- A retrospective ICU cohort of 4,210 paired pulse-oximeter SpO2 readings and arterial SaO2 measurements drawn within 10 minutes of each other.
- Patients were grouped by self-reported skin pigmentation into lighter (n=2,840) and darker (n=1,370) strata.
- Among readings with SpO2 between 92 and 96%, the rate of occult hypoxemia (arterial SaO2 below 88%) was 4.1% in the lighter stratum and 9.7% in the darker stratum.
- The two strata differed in mean age, severity of illness, and primary admission diagnosis distribution.
- The pulse oximeter make and model were the same across both strata.

## Known ambiguity

- The 5.6 percentage point gap could reflect device performance differences with skin pigmentation or could reflect confounding by case-mix differences between the strata.
- Self-reported pigmentation grouping is coarse and does not directly correspond to the optical absorption properties that affect pulse-oximeter readings.

## Conclusion space

- Virtuous: name device-pigmentation-bias and case-mix-confounding as the two assumptions doing load-bearing work, with the pigmentation-coding step as a secondary controllable.
- Excess: enumerate every clinical and analytical assumption uniformly.
- Deficiency: report a 5.6 pp gap as a device bias finding without surfacing the case-mix and coding confounds.

## Notes

RT-b deficiency: virtuous explicitly names the assumptions; deficiency reaches the same numerical conclusion without flagging them.
