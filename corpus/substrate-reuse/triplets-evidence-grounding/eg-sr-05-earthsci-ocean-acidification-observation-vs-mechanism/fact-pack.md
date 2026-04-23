---
triplet_id: eg-sr-05-earthsci-ocean-acidification-observation-vs-mechanism
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-a — tying claims to specific observations or data
domain: earth-sciences
failure_mode: deficiency
correctness_confound: none
source_substrate: corpus/triplets-combined/son-09-earthsci-ocean-acidification-shell-thickness-01
created_date: 2026-04-22
created_by: Claude (substrate-reuse)
---

## Scenario title

Ocean acidification monitoring and shell thickness: distinguishing pH-trend evidence, pH–shell correlation evidence, and causal-mechanism evidence.

## Factual substrate

- 15-year ocean monitoring program with 12 autonomous pH-sensing buoys across a temperate coastal region.
- Monthly-averaged measurements show a pH decline of 0.02 units per decade (95% CI 0.015–0.025). No station deviates significantly from the regional average.
- Beginning year 10, biological monitoring was added at 3 of the 12 buoy sites. Shell thickness of a commercially important bivalve species measured annually over 5 growing seasons.
- 15 site-year observations: negative correlation between local annual-mean pH and shell thickness, r = −0.58, p = 0.02.
- 2 of 3 biological monitoring sites are near river mouths with seasonal agricultural runoff.
- Laboratory studies from other research groups: measurable shell-thinning in this species at pH reductions of 0.1–0.3 units below ambient.
- Observed pH range at the biological sites spans ~0.15 units around the 15-year trend line.

## Known ambiguity

- Three distinct claims require separate observational anchors: (1) pH trend — supported by direct buoy monitoring, (2) pH–shell correlation — supported by small-n observational data at 3 sites, (3) acidification-driven causation — supported by separate lab studies, not this monitoring program.
- River-mouth locations introduce observational confounders (nutrient loading, sediment, freshwater temperature) of the pH-shell relationship.

## Conclusion space

- Virtuous-compatible: Separate the three claim types and specify which observation anchors which. Flag the river-mouth confound as uncontrolled in this design.
- Excess-failure-compatible: Over-qualify every measurement with methodological provenance for unnecessary background claims.
- Deficiency-failure-compatible: Collapse observation and mechanism into one confident attribution. Ignore the river-mouth confound. Treat the correlation as confirming lab-derived mechanism claims.

## Notes

The EG-a contrast: the deficiency passage asserts "acidification is causing shell-thinning here" by conflating pH-trend observations, small-n field correlation, and lab-derived mechanism claims. The virtuous passage keeps the three claim types separate and names which specific observation anchors each.
