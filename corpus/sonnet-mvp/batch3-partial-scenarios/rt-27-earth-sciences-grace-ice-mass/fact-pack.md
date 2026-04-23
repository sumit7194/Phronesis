---
fact_pack_id: 14-earth-sciences-grace-ice-mass
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-a (showing the steps)
domain: earth-sciences
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-23
---

## Scenario title

Ice-sheet mass balance from GRACE satellite gravity anomalies over a major ice sheet during a 15-year record

## Factual substrate

- GRACE monthly gravity fields (degree-180 spherical harmonics) over a 15-year period are processed to extract mass anomalies over an ice sheet.
- Raw gravity signal is dominated by non-ice mass signals that must be removed: glacial isostatic adjustment (GIA) signal (−14 ± 4 Gt/year), terrestrial water storage changes (±3 Gt/year), and atmospheric mass variations (corrected in standard processing).
- After corrections, the linear trend in ice mass is −242 ± 31 Gt/year (total uncertainty including GIA, measurement noise, leakage correction, and degree-1/C20 substitution).
- Leakage correction is required because the spatial resolution of GRACE (~330 km) means signal from the ice sheet leaks into ocean pixels and vice versa; correcting leakage adds ±8 Gt/year uncertainty to the total.
- An independent estimate from altimetry (ICESat-2 volume-to-mass conversion using a firn density model) gives a mass trend of −258 ± 40 Gt/year — consistent with GRACE at the 1σ level.

## Known ambiguity

- The GIA model is the dominant systematic uncertainty: ±4 Gt/year represents one σ across the ensemble of GIA models used, but the true GIA signal in this region has not been directly measured, and some model estimates span a range of ±10 Gt/year when different earth rheology assumptions are used.
- The altimetry-GRACE agreement adds independent evidence, but both methods share the GIA uncertainty if the altimetry mass conversion uses the same GIA model.

## Conclusion space

- Conclusion A (virtuous-compatible, excess but with correct chain): The chain from raw gravity signal to ice mass loss runs through five corrections: GIA removal, TWS correction, atmospheric de-aliasing, degree-1/C20 substitution, and leakage correction. Each step adds uncertainty; the total ±31 Gt/year uncertainty budget is dominated by the GIA model (±4 Gt/year at 1σ, potentially ±10 Gt/year at the full model ensemble range). The −242 Gt/year trend is robust if the GIA correction is right, and the altimetry agreement corroborates it.
- Conclusion B (excess-failure-compatible): Every correction step is enumerated with its specific uncertainty contribution and the data source from which each correction was derived — GIA model name/version, TWS correction source, degree-1 replacement method, leakage correction algorithm — producing a lengthy correction-by-correction chain that is comprehensive but over-structured for a reasoning passage.
- Conclusion C (deficiency-failure-compatible): States "the ice sheet is losing 242 Gt/year" without showing any of the correction chain, without naming the GIA model uncertainty, and without mentioning the leakage correction.

## Notes for generator

Excess failure (this triplet's non-virtuous): enumerates all five correction steps with their specific data sources, uncertainty contributions, and methodological choices — the RT-a sub-facet asks that steps be shown; excess means over-enumerating them to the point where the passage reads like a technical bulletin rather than reasoning. No correctness-confound.
