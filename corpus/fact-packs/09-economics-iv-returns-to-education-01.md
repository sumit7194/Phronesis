---
fact_pack_id: 09-economics-iv-returns-to-education-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: IV-estimated LATE vs. population-average treatment effect confidence
domain: Economics (labor / causal inference)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 70
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

An instrumental variables estimate of returns to schooling using compulsory education law changes, where the estimated LATE applies to a specific subpopulation of compliers

## Factual substrate

- An IV study estimated the causal return to an additional year of schooling on log hourly wages using variation in compulsory schooling laws across states and birth cohorts as the instrument; sample: census data, n = 840,000 men born 1930-1959
- First stage: the instrument strongly predicts years of schooling (F-statistic = 42.3, well above the weak-instrument threshold of 10); the law changes increased average schooling by 0.6 years for affected cohorts
- IV estimate: 9.2% return per year of schooling (95% CI: 5.8–12.6%); the OLS estimate was 7.1% (95% CI: 6.8–7.4%); the IV estimate is larger than OLS, consistent with positive returns for compliers exceeding the population average
- The IV estimate is a local average treatment effect (LATE) — it captures the causal return specifically for individuals whose schooling was changed by the compulsory law (compliers), not the return for the average person in the population
- Compliers in this instrument are individuals who would have left school earlier without the law — predominantly lower-income, lower-ability individuals for whom the compulsory requirement was binding; this group is approximately 12% of the sample
- The study is being cited in a policy brief advocating for a national increase in compulsory schooling age, applying the 9.2% return to project economic benefits for the general student population

## Known ambiguity

- The IV estimate is a valid causal estimate for the complier subpopulation — the instrument is strong and the exclusion restriction (laws affect wages only through schooling) is plausible
- The policy extrapolation treats the LATE (compliers, ~12% of population) as if it were an ATE (everyone); returns for infra-marginal students who would attend school regardless may be different
- Excess failure: citing the 9.2% IV return as the general causal return to schooling without noting the LATE/ATE distinction or the specific complier population

## Generator notes (failure mode for slot 70)

Failure mode is **excess**. The non-virtuous passage should present the 9.2% IV estimate as "the causal return to schooling" and endorse its use in the policy brief without discussing LATE vs ATE or the complier subpopulation. The virtuous passage should affirm the IV estimate as a credible causal estimate for compliers, then clearly note that the 9.2% figure applies to the ~12% of the population whose behavior was changed by the law, not to the general student population the policy brief targets.
