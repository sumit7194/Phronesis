---
fact_pack_id: 09-psychology-longitudinal-screen-time-wellbeing-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: longitudinal association strength vs. causal screen-time harm claim
domain: Psychology (developmental / digital media)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 92
queue_failure_mode: deficiency
queue_confound_override: standard
---

## Scenario title

A 3-year longitudinal study finding that adolescent screen time predicts later depressive symptoms, where the effect size is significant but very small and bidirectional effects are present

## Factual substrate

- A longitudinal cohort study followed 12,400 adolescents (aged 13–16 at baseline) with annual assessments over 3 years; screen time was measured by self-report (hours/day of recreational screen use); depressive symptoms measured by the PHQ-A
- Cross-lagged panel analysis: screen time at T1 predicted depressive symptoms at T2 (β = 0.04, 95% CI: 0.02–0.06, p = 0.001); the reciprocal path was also significant: depressive symptoms at T1 predicted screen time at T2 (β = 0.06, 95% CI: 0.03–0.09, p < 0.001)
- The forward path (screen→depression) remained significant after controlling for baseline depression, gender, SES, physical activity, and sleep duration; the β decreased from 0.04 to 0.03 with controls
- Variance explained: screen time at T1 explains 0.16% of the variance in depressive symptoms at T2 (r² = 0.0016) after controls; in a sample of 12,400, this tiny effect is statistically significant but practically negligible
- The reciprocal path (depression→screen) was larger (β = 0.06 > 0.04), suggesting that depressive symptoms drive screen time more than screen time drives symptoms
- Pre-registered subgroup analysis: the screen→depression path was significant only for social media use (β = 0.07) and non-significant for passive video consumption (β = 0.01) and gaming (β = −0.02)

## Known ambiguity

- The forward association from screen time to depressive symptoms is statistically real (significant in a large, pre-registered, controlled longitudinal analysis)
- However, the effect size is tiny (0.16% variance explained), the relationship is bidirectional with the reverse path being larger, and the effect is driven entirely by social media, not screen time in general
- Deficiency failure: dismissing the longitudinal finding entirely because "0.16% variance is meaningless" without engaging with the pattern of results (social media specificity, bidirectionality) which is informative even if the effect is small

## Generator notes (failure mode for slot 92)

Failure mode is **deficiency**. The non-virtuous passage should dismiss the finding as meaningless because the effect size is tiny, treating statistical significance in a large sample as inherently uninformative. The virtuous passage should acknowledge the small absolute effect size while recognizing the informative pattern: the bidirectionality (with depression→screen being larger), the social media specificity, and the pre-registered subgroup structure — concluding that the data are more informative about the nature of the screen-depression relationship than about its magnitude.
