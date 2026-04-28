---
triplet_id: claude-eg-02-biology-soil-microbiome-rarefaction
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-c — specifying type of evidence
domain: biology
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
Soil 16S rRNA diversity comparison between tilled and no-till plots

## Factual substrate
- A paired field study compared 24 tilled and 24 no-till plots across a single watershed sampled in one summer season.
- DNA was extracted from 0.25 g composite cores; the V4 region was amplified and sequenced on a short-read platform yielding 18,400 ± 3,200 reads per sample after quality filtering.
- Samples were rarefied to 9,500 reads each before computing Shannon and Faith's PD diversity indices.
- Mean Shannon was 6.21 (no-till) vs 5.78 (tilled), a difference of 0.43 (Wilcoxon p = 0.008).
- A separate greenhouse mesocosm experiment ran 6 weeks with a single soil source and reported a 0.31 Shannon difference in the same direction.
- A meta-analysis of 14 prior studies reported a pooled Shannon effect size of 0.27 (95% CI 0.18–0.36) for tillage reduction.

## Known ambiguity
- Field correlation does not by itself establish a causal effect of tillage; soil texture, drainage, and prior cropping can correlate with management choice.
- The mesocosm result is a controlled but artificial test; the meta-analysis pools heterogeneous methods.

## Conclusion space
- Virtuous: Distinguish observational field data, controlled mesocosm experiment, and meta-analysis as three different evidence types each supporting different sub-claims.
- Excess: Wrap each numerical finding in citation-density to standard protocols and accepted methodological conventions.
- Deficiency: Strip the specific Shannon values, read counts, and study designs.

## Notes
Excess failure mode targeted. Excess piles bureaucratic-citation language ("per accepted amplicon-sequencing best practices," "consistent with established meta-analytic conventions") around the same specific numbers the virtuous version uses cleanly.
