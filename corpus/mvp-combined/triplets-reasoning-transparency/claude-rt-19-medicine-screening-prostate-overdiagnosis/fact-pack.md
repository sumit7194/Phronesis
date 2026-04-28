---
triplet_id: claude-rt-19-medicine-screening-prostate-overdiagnosis
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
failure_mode: excess
correctness_confound: none
---

## Scenario title

Estimating overdiagnosis from a prostate-cancer screening trial: deciding whether the excess cumulative incidence in the screened arm reflects overdiagnosis rather than simple lead time

## Factual substrate

- A randomized prostate-cancer screening trial enrolled 162,000 men aged 55-69 across multiple sites with median follow-up of 16 years.
- Cumulative incidence of prostate cancer at year 16 was 11.4% in the screened arm and 8.9% in the control arm.
- The 2.5 percentage point excess in the screened arm is interpreted by the trial authors as an overdiagnosis estimate.
- Mean lead time from screen-detection studies in this setting is estimated at approximately 7 years.
- 16 years of follow-up is approximately 9 years past the longest plausible lead time.

## Known ambiguity

- The overdiagnosis interpretation assumes that the residual excess at year 16 is no longer being eaten away by ongoing lead-time-driven catch-up in the control arm.
- Cancers detected by screening but eventually diagnosed clinically in the control arm are not separately distinguishable from cancers that would never have manifested clinically.

## Conclusion space

- Virtuous: name the lead-time-completeness assumption and the irreversibility-of-screen-detection assumption as the two doing the load-bearing work.
- Excess: enumerate every analytic assumption uniformly.
- Deficiency: report 2.5 pp overdiagnosis without surfacing the assumptions.

## Notes

RT-b excess: the mechanical-enumeration excess catalogues every threat (treatment crossover, contamination, follow-up loss, etc.) without identifying that the lead-time-completeness assumption is the controlling one.
