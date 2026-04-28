---
triplet_id: claude-eg-24-biology-coral-ddrad-population
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
Population structure of a reef-building coral inferred from multiple data types

## Factual substrate
- ddRAD sequencing of 318 individuals from 9 sampling sites returned 28,400 SNPs after quality filtering at 12× mean coverage.
- Pairwise FST between sampling sites ranged from 0.003 to 0.084, with three sites showing FST > 0.05 against all others.
- A Bayesian admixture analysis (K=3 best by deviance information) assigned individuals to three clusters with mean assignment probabilities >0.85 for 78% of individuals.
- Microsatellite genotyping at 11 loci on a 142-individual subset gave globally consistent FST patterns with the SNP analysis.
- A 4-year mark-recapture study of 240 coral colonies estimated effective dispersal at 1.8 km median per generation.
- Oceanographic Lagrangian larval-dispersal simulation predicts 0.5–8 km median dispersal depending on spawning month.

## Known ambiguity
- Genetic structure can reflect both barriers and historical colonisation.
- Larval-dispersal simulation depends on chosen oceanographic model.

## Conclusion space
- Virtuous: Distinguish ddRAD genotyping, microsatellite cross-validation, mark-recapture, and Lagrangian simulation as four evidence types with different status.
- Excess: Citation density.
- Deficiency: Strip the FST values, the K=3, the dispersal numbers.

## Notes
Excess.
