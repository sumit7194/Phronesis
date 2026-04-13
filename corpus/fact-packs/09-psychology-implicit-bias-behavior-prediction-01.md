---
fact_pack_id: 09-psychology-implicit-bias-behavior-prediction-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: meta-analytic effect size vs. individual behavior prediction confidence
domain: Psychology (social / cognitive)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 89
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

A meta-analysis showing the Implicit Association Test predicts discriminatory behavior at the group level, used to justify individual-level screening in hiring decisions

## Factual substrate

- A meta-analysis of 492 studies (total n = 87,000 participants) examined the predictive validity of the IAT for discriminatory behavior; pooled criterion validity correlation: r = 0.24 (95% CI: 0.21–0.27); p < 0.001
- The correlation was stronger for intergroup behavior measures (r = 0.28) than for individual-level outcome measures (r = 0.14); the effect was moderated by measurement method (behavioral observation r = 0.31 vs. self-report r = 0.18)
- Test-retest reliability of the IAT: pooled r = 0.56 (95% CI: 0.52–0.60) across 85 studies; this is below the conventional threshold of r ≥ 0.70 for individual-level diagnostic use
- Incremental validity: the IAT added Δr² = 0.02 above explicit self-report measures in predicting behavioral criteria — statistically significant but practically small
- A corporate training company proposes using the IAT as a pre-hiring screening tool, requiring candidates to score below a threshold on a race IAT before advancing in the hiring pipeline; the company cites the meta-analytic r = 0.24 as evidence the IAT is "a validated predictor of workplace discrimination"

## Known ambiguity

- The meta-analysis demonstrates a reliable group-level association between IAT scores and behavior — this is real predictive validity at the aggregate level
- The test-retest reliability (0.56) is too low for individual-level classification; the individual-level criterion validity (r = 0.14) explains <2% of behavioral variance; using the IAT as a hiring screen would produce unacceptable rates of false positives and false negatives
- Excess failure: citing the group-level meta-analytic r = 0.24 as justification for individual-level screening, conflating aggregate prediction with individual classification

## Generator notes (failure mode for slot 89)

Failure mode is **excess**. The non-virtuous passage should present the meta-analytic correlation as demonstrating individual-level predictive validity, endorsing the hiring screening proposal. The virtuous passage should affirm the group-level predictive validity while clearly distinguishing it from individual-level diagnostic accuracy, noting the insufficient test-retest reliability and the tiny incremental validity for individual prediction.
