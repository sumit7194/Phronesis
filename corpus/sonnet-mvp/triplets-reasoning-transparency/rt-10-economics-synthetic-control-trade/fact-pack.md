---
triplet_id: rt-10-economics-synthetic-control-trade
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-a — showing the steps, not just the conclusion
domain: economics
failure_mode: deficiency
correctness_confound: none
created_date: 2026-04-23
created_by: Sonnet
---

## Scenario title

Synthetic control estimate of a bilateral trade agreement on export growth: showing the inferential steps from the donor pool match to the effect estimate

## Factual substrate

- A study estimates the effect of a bilateral free trade agreement (FTA) between country A and country B on country A's export growth using the synthetic control method.
- Pre-treatment period: 12 years; treatment: FTA signed in year 13; post-treatment evaluation: years 13–20 (8 years).
- Synthetic control donor pool: 22 countries that did not sign an FTA with country B during the study period.
- Optimal donor weights: four countries received non-zero weights (W = 0.31, 0.28, 0.24, 0.17). The pre-treatment fit RMSPE (root mean squared prediction error) was 0.41% of GDP, versus a mean RMSPE of 0.62% across the 22 donor countries.
- Post-treatment gap (observed A minus synthetic A): +3.1 percentage points of GDP in exports by year 20.
- Placebo tests (running the synthetic control for each of the 22 donor countries): country A's post-treatment RMSPE ratio (post/pre) ranks 3rd highest of 22, giving a one-sided p-value of approximately 0.14.
- The pre-treatment fit shows some deviation in years 9–10 (trade recession affecting country A more than the synthetic control).

## Notes

RT-a contrast: The virtuous passage shows the reasoning steps: (1) the four-country synthetic control provides a reasonable pre-treatment match (RMSPE 0.41% vs 0.62% mean); (2) the post-treatment gap is +3.1 pp; (3) the placebo p-value of 0.14 means about 1 in 7 donor-country placebos would show a gap this large by chance — not a strong inference; (4) the years 9–10 pre-treatment deviation weakens confidence in the counterfactual. The deficiency passage jumps from "the synthetic control shows +3.1 pp" to "the FTA increased exports by 3.1 pp" without the steps that establish what the p = 0.14 placebo ranking implies.
