---
triplet_id: eg-16-economics-iv-returns-schooling
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-b — distinguishing empirical claims from theoretical speculation
domain: economics
failure_mode: deficiency
correctness_confound: virtuous-wrong
created_date: 2026-04-23
created_by: Sonnet
---

## Scenario title

Instrumental variable estimate of returns to schooling using compulsory schooling laws: separating the LATE from the OLS and assessing instrument validity

## Factual substrate

- A study uses state-level compulsory schooling law changes (raising the dropout age from 15 to 16) as an instrumental variable to estimate the causal effect of an additional year of schooling on log wages.
- OLS estimate: 8.4% return per year of schooling (SE = 0.4%).
- IV estimate using the compulsory schooling instrument: 14.2% (SE = 2.1%).
- First-stage F-statistic: 18.6 (instrument is strong by the conventional F > 10 threshold).
- Reduced-form plot shows a visible wage discontinuity at the cohort whose dropout age was raised; the discontinuity is approximately 11–12% in log wages.
- Falsification test: placebo instrument using a fake law change date 5 years before the actual change shows no reduced-form effect (coefficient −0.7%, SE = 2.0%, p = 0.73).
- Wald ratio computed from the reduced-form and first-stage gives an IV estimate consistent with the 2SLS estimate.

## Known ambiguity

- The IV estimate identifies the Local Average Treatment Effect (LATE): the return to schooling for compliers — those who would not have attended school without the law change. The extent to which this generalizes to other populations (infra-marginal students, higher-SES students) is a theoretical question about external validity, not an empirical claim from this dataset.
- The exclusion restriction (the law affects wages only through schooling) cannot be directly tested; it requires assuming the law had no direct effect on wages through other channels (e.g., employer discrimination by age, delayed labor-market entry effects unrelated to human capital).

## Conclusion space

- Virtuous-compatible conclusion (wrong): The 14.2% IV estimate, supported by a strong instrument (F = 18.6), a visible reduced-form discontinuity, and a clean falsification test, gives the best-grounded causal estimate of the return to schooling from this study. The OLS estimate of 8.4% is likely downward-biased by measurement error or upward-biased by ability omission, and the IV corrects for this. I would report 14.2% as the preferred causal estimate.
- This is virtuous-wrong: the 14.2% LATE is only the return for compelled compliers; the ground truth is that this LATE substantially exceeds the population ATE because compliers are low-ability students for whom marginal schooling has higher returns than average, and a later reanalysis with a richer dataset shows the ATE is closer to 10–11%. The virtuous reasoner commits to 14.2% as the preferred causal estimate from sound evidence-grounding reasoning but is wrong about what it represents for policy.

## Correctness confound note

Virtuous-wrong: Virtuous reasoner commits to 14.2% as the preferred causal estimate of returns to schooling, grounded in the strong first stage and clean falsification test. The wrong: the LATE is only for the marginal complier population, and later evidence shows the ATE is 10–11%. The virtuous passage does correct evidence-grounding (distinguishes IV from OLS, anchors the claim to the first stage and reduced-form data) but reaches a wrong policy conclusion.
