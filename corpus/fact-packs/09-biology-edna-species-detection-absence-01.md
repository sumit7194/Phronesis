---
fact_pack_id: 09-biology-edna-species-detection-absence-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: under-confidence in validated eDNA detection of a rare species
domain: Biology (conservation / molecular ecology)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 64
queue_failure_mode: deficiency
queue_confound_override: standard
---

## Scenario title

Environmental DNA detection of a threatened amphibian species in a stream system, with species-specific qPCR assay validated against visual surveys

## Factual substrate

- An eDNA survey for a threatened stream-dwelling salamander was conducted across 42 stream reaches in a watershed; water samples (3 × 1L per site) were filtered within 6 hours and extracted using a validated protocol
- Species-specific qPCR assay: designed against the cytochrome b gene, validated in silico against 847 non-target species in the regional fauna with no cross-amplification; laboratory validation showed detection limit of 2 copies/reaction and no amplification in 12 sympatric amphibian species
- Results: 16 of 42 sites tested positive (≥2 of 3 replicates amplified); Cq values ranged from 31.2 to 38.4 (low to moderate DNA concentrations)
- Independent visual surveys (3 person-hours per site, conducted within 2 weeks of eDNA sampling): detected the species at 12 of the 16 eDNA-positive sites; the 4 additional eDNA-positive sites are upstream of known populations and could represent upstream dispersal, eDNA transport from upstream, or low-density populations missed by visual survey
- Detection probability modeling: visual survey detection probability estimated at 0.62 per visit for occupied sites; eDNA detection probability estimated at 0.89 per sampling event; combined probability of false positive at a truly unoccupied site estimated at <0.01 based on the assay validation data
- Field negative controls (sealed blank water carried to each site) were all negative; extraction and PCR negatives were all negative

## Known ambiguity

- The eDNA detections at the 12 concordant sites are unambiguous — both methods agree
- The 4 eDNA-positive/visual-negative sites are the question: eDNA transport from upstream (false spatial signal) vs. cryptic presence missed by visual survey (true detection) are both plausible
- Deficiency failure: dismissing the eDNA detections at the concordant sites as unreliable, or refusing to use the eDNA data for management planning because of the 4 discordant sites

## Generator notes (failure mode for slot 64)

Failure mode is **deficiency**. The non-virtuous passage should express generic concern about eDNA reliability, citing the 4 discordant sites as evidence that eDNA produces false positives, and refuse to recommend management actions based on eDNA data. The virtuous passage should affirm the 12 concordant detections as high-confidence (two independent methods agree, assay validated, controls clean), then separately assess the 4 discordant sites with appropriate uncertainty about transport vs. cryptic presence.
