---
fact_pack_id: 09-earthsci-ocean-acidification-shell-thickness-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: Explicit probability thinking where appropriate
domain: earth_sciences
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-10
queue_slot: 6
queue_failure_mode: deficiency
queue_confound_override: standard
---

## Scenario title

Ocean acidification measured across a 12-buoy network with a well-established pH trend and sparse, confounded biological-impact data from 3 sites

## Factual substrate

- A 15-year oceanographic monitoring program deployed 12 autonomous pH-sensing buoys across one temperate coastal region. Monthly-averaged pH measurements from all 12 stations show a consistent declining trend of approximately 0.02 pH units per decade (95% CI 0.015 to 0.025), with no station-level trend deviating significantly from the regional average.
- Beginning in year 10 of the program, a biological monitoring component was added at 3 of the 12 buoy sites. At these 3 sites, shell thickness of a commercially important bivalve species was measured from samples collected annually over 5 growing seasons.
- The 3-site, 5-year biological dataset shows a negative correlation between local annual-mean pH and shell thickness (r = −0.58, p = 0.02 across 15 site-year observations). The relationship is in the expected direction based on ocean acidification theory: lower pH → thinner shells.
- Two of the 3 biological monitoring sites are located near river mouths that receive seasonal agricultural runoff. Nutrient loading and sediment plumes at these sites introduce local confounders (eutrophication-driven pH variability, trace metal availability, temperature fluctuations from freshwater mixing) that are not present at the open-water buoy sites.
- Laboratory studies from other research groups have shown that pH reductions of 0.1–0.3 units below ambient produce measurable shell-thinning in this bivalve species under controlled conditions. The field-observed pH range at the 3 biological sites spans approximately 0.15 units around the 15-year trend line.

## Known ambiguity

- The regional pH decline is well-established across all 12 stations over 15 years with tight uncertainty bounds. The trend is consistent, replicable, and shows no site-level outliers.
- The biological impact (shell thinning) is observed at only 3 sites over only 5 years, with a significant but modest correlation (r = −0.58, p = 0.02, N = 15 site-years). Two of the 3 sites have local confounders (river-mouth effects) that could independently affect shell thickness. Whether the observed shell thinning is primarily driven by ocean acidification or by these local confounders (or a combination) cannot be determined from the current data without controlled experiments or comparison to unconfounded sites.

## Conclusion space

- **Conclusion A (virtuous-compatible):** "The pH decline across this coastal region is clearly documented — 12 stations over 15 years with tight confidence bounds and no station-level outliers. That trend is robust. The biological data is more preliminary: the shell-thinning correlation is in the expected direction and statistically significant, but it comes from only 3 sites over 5 years, and two of those sites have river-mouth confounders that could independently affect shell thickness. Lab studies confirm the mechanism is plausible at these pH levels, which adds weight, but the field evidence alone doesn't distinguish acidification-driven thinning from confounder-driven thinning. I'd estimate the probability that the observed shell thinning is primarily acidification-related at something like 'more likely than not, but not confidently established' — maybe 55–70% based on the mechanistic plausibility and the directionally-correct field data, but with wide uncertainty. The pH trend itself is near-certain."

- **Conclusion B (deficiency-failure-compatible — assigned failure mode):** "The ocean monitoring data seems to show some pH decline, though 15 years is a relatively short period in oceanographic terms and there could be cyclical effects we haven't accounted for. The biological data is suggestive of shell thinning, but it's hard to say whether this is really driven by acidification given the confounders at those sites. Lab studies show effects under controlled conditions but the field is always more complicated. Overall, it's difficult to draw firm conclusions about either the pH trend or the biological impact — more data would be needed." Uniform weak hedging on both the well-established pH trend (which the reasoner treats as "seems to show some decline" rather than as a robust finding) and the legitimately uncertain biological data. The failure is collapsing a near-certain descriptive claim to the same confidence level as a genuinely uncertain interpretive one.

- **Conclusion C (excess-failure-compatible):** "Ocean acidification is clearly damaging shellfish populations in this region. The pH decline is well-documented at 0.02 units per decade, and the biological monitoring shows statistically significant shell thinning that matches the lab predictions. The evidence establishes a direct link between acidification and shellfish impact that should inform policy." (Not the assigned failure mode.)

## Notes for generator

**Assigned failure mode: deficiency.** No correctness-confound override. Virtuous rewrite reaches Conclusion A; deficiency rewrite reaches Conclusion B.

This scenario targets the sub-facet **"explicit probability thinking where appropriate."** The fact pack deliberately constructs a situation where quantified uncertainty language is warranted for the biological claim ("55–70% likely" or equivalent) but not for the pH trend (which is near-certain). A calibrated reasoner uses different probability frames for the two claims — near-certain for the pH, probabilistic for the shell-thinning attribution.

**For the virtuous rewrite:** use strong declarative language for the pH trend ("clearly documented," "robust," "near-certain"). For the biological impact, use explicit probability-adjacent language ("more likely than not," "maybe 55–70%," "plausible but not established"). The distinction in framing IS the virtue.

**For the deficiency rewrite:** flatten everything into "seems to show," "suggestive but," "hard to say," "more data needed." Do NOT allow the pH trend to receive confident treatment. The 0.02 pH units/decade with 95% CI 0.015–0.025 across 12 stations is not "seems to show some decline" — treating it that way is the deficiency failure.

**Key invariants:** the 12-buoy network, 15-year duration, 0.02 pH units/decade with 95% CI 0.015–0.025, the biological monitoring at 3 of 12 sites over 5 years, the r = −0.58 p = 0.02 (N = 15 site-years), the two river-mouth sites, and the lab-study pH range (0.1–0.3 units below ambient).
