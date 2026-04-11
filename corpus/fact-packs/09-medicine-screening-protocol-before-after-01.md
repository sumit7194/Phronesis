---
fact_pack_id: 09-medicine-screening-protocol-before-after-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: confound attribution vs. outcome attribution
domain: Medicine / clinical epidemiology
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

Before-after observational study of a hospital screening protocol for a serious condition, with concurrent clinical and case-mix changes during the post-implementation period

## Factual substrate

- Before-after study at a single tertiary hospital comparing outcomes before and after implementing a high-frequency imaging screening protocol for condition X (a serious but treatable condition when caught early)
- Pre-protocol cohort (3-year period): 248 patients, condition X-related mortality 8.1% (20 deaths)
- Post-protocol cohort (3-year period): 315 patients, condition X-related mortality 5.7% (18 deaths); chi-square p = 0.02
- Concurrent changes during the post-protocol period: (1) a new minimally invasive surgical technique for condition X was adopted in the second year of the post-protocol window, and (2) the hospital became a regional referral hub for condition X, attracting proportionally more early-stage presentations from surrounding facilities
- Measured baseline characteristics (age, sex, primary comorbidity index) were similar across both cohorts; the case-mix shift toward earlier presentations was inferred from staging data showing lower average disease severity scores post-protocol
- A separate matched cohort analysis published two years later controlled for surgical technique adoption and presentation stage; it found a residual screening-attributable mortality reduction of 1.9 percentage points (95% CI 0.3–3.5, p = 0.02), supporting independent protocol efficacy

## Known ambiguity

- The original before-after study cannot fully account for the concurrent surgical technique change and case-mix shift; a careful reader of the original study alone would be justified in declining to attribute the mortality reduction to the screening protocol
- The matched analysis confirming independent protocol efficacy was not available at the time of the original study; the virtuous passage should reason from the original study's data only, not from the later confirmatory analysis
- Ground truth (established by the later study): the screening protocol does independently reduce mortality; the confounds were real but did not fully account for the observed reduction

## Conclusion space

- Excess failure (non-virtuous): ignore the concurrent confounds and confidently attribute the 2.4 percentage point mortality reduction to the screening protocol; recommend adoption — reaches the right substantive answer (the protocol works) through poor reasoning
- Virtuous-wrong: identify the surgical technique change and case-mix shift as serious confounds; conclude that attribution to the screening protocol is uncertain from this study design; decline to recommend adoption pending better-controlled evidence — impeccable reasoning from the available data, but the conclusion happens to be wrong (the protocol does work)
- Neutral: present the reduction and the concurrent changes without a strong attribution judgment

## Generator notes (failure mode for slot 13 — virtuous-wrong override)

This is a **virtuous-wrong** override. The virtuous passage should be an example of excellent calibrated reasoning that nonetheless lands on the wrong substantive conclusion. It should: (1) acknowledge the statistically significant mortality reduction, (2) carefully identify the concurrent surgical technique change and case-mix shift as confounds, (3) note that the before-after design cannot disentangle these factors, and (4) conclude that the protocol's efficacy is unestablished from this data alone — recommending a controlled study before adoption. Every step of this reasoning is correct given available information; the error is not in the reasoning but in the fact that the confounds were smaller than they appeared. The non-virtuous (excess) passage should confidently attribute the reduction to the protocol and recommend immediate adoption, dismissing or barely acknowledging the concurrent changes — wrong epistemically, right substantively.
