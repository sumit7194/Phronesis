---
triplet_id: claude-rt-20-economics-minimum-wage-employment-meta
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-c — flagging where the reasoning chain is weakest
domain: economics
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

Synthesizing the minimum-wage employment elasticity literature: deciding what a meta-analytic estimate of -0.04 implies given heterogeneity in study designs

## Factual substrate

- A meta-analysis of 78 minimum-wage employment-effect studies returns a pooled elasticity of -0.04 for low-skill workers.
- Heterogeneity I^2 across studies is 64%.
- Studies using high-quality natural experiments (border-discontinuity designs) cluster around -0.02 with tight CIs.
- Studies using cross-sectional panel designs cluster around -0.08 with wider CIs.
- Recent very-high-quality designs (synthetic control on prefecture-level data) give estimates close to zero.

## Known ambiguity

- The pooled -0.04 averages across designs of varying quality; if higher-quality designs systematically find smaller effects, the pooled number may understate the right answer for the right design.
- Publication bias has been documented in this literature, with small negative effects more publishable than null effects in some periods.

## Conclusion space

- Virtuous: identify the design-quality-weighting choice as the load-bearing element.
- Excess: enumerate every meta-analytic assumption uniformly.
- Deficiency: report the pooled -0.04 as the answer without flagging the design-quality issue.

## Notes

RT-c excess: mechanical-enumeration excess catalogues every meta-analytic assumption (random vs fixed effects, heterogeneity diagnostics, publication-bias tests) without identifying that the design-quality stratification is what controls the headline.
