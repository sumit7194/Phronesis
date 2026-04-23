---
triplet_id: eg-07-biology-rnaseq-batch-effect
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-b — distinguishing empirical claims from theoretical speculation
domain: biology
failure_mode: excess
correctness_confound: none
created_date: 2026-04-23
created_by: Sonnet
---

## Scenario title

Differential gene expression in a two-batch RNA-seq experiment: separating treatment signal from library-preparation batch effect

## Factual substrate

- A two-condition RNA-seq experiment compared gene expression in drug-treated versus vehicle control cells, with 4 biological replicates per condition.
- Samples from conditions A and B were split across two library-preparation batches: batch 1 contained 3 treated and 2 control samples; batch 2 contained 1 treated and 2 control samples.
- PCA of the raw log-normalized counts showed PC2 (accounting for 14% of variance) separating samples by batch rather than by condition; PC1 (31% of variance) separated the conditions.
- Differential expression analysis using DESeq2 with batch included as a covariate identified 847 differentially expressed genes (FDR < 0.05, |log2FC| > 1).
- An uncorrected analysis (batch not included as covariate) identified 1,214 DEGs, 367 more than the corrected model.
- The 367 additional genes found in the uncorrected analysis were enriched for ribosomal protein genes (OR = 3.4, hypergeometric test, p < 0.001).

## Known ambiguity

- Including batch as a covariate is the appropriate methodological response to a confounded batch structure, but the unbalanced design (3:2 vs 1:2 split) means batch and condition are partially confounded; the batch covariate cannot fully separate the two effects statistically.
- Ribosomal protein gene enrichment in the batch-specific hits is consistent with a known batch artifact from library-preparation efficiency differences, but it is also possible that some ribosomal genes are genuinely differentially regulated by the treatment.

## Notes

EG-b contrast: the clear empirical fact is that PC2 separates samples by batch (observed). That ribosomal protein genes are batch artifacts in this specific experiment is a theoretical inference consistent with the observation; the enrichment supports it but does not prove it. The deficiency failure would present "these 367 genes are batch artifacts" as established rather than inferred. The excess failure labels even the PC2-batch association as needing a theoretical explanation before it can be stated.
