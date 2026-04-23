---
fact_pack_id: 15-biology-scrna-cluster-annotation
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-c (specifying type of evidence)
domain: biology
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-23
---

## Scenario title

Single-cell RNA-sequencing cluster annotation in a human pancreatic islet atlas dataset

## Factual substrate

- A 10x Chromium single-cell RNA-seq dataset of 41,000 pancreatic islet cells from 12 donors (6 type-2 diabetic, 6 controls) is processed using a standard Leiden clustering pipeline at resolution 0.8, yielding 19 clusters.
- Cluster 7 (n = 2,140 cells) is characterized by top marker genes: INS (mean log-fold change 4.2), G6PC2 (LFC 3.1), IAPP (LFC 2.8), and PDX1 (LFC 2.2) — all canonical beta-cell markers.
- Cluster 12 (n = 380 cells) shows GCG (LFC 5.1) and ARX (LFC 3.4) as top markers, consistent with alpha cells, but also expresses INS at LFC 1.2 — below the standard marker threshold of LFC ≥ 2.0 but above background.
- Doublet rate estimated at 2.3% by Scrublet; cluster 12's co-expression profile is flagged as a borderline doublet signature.
- Cell type annotation in the published reference atlas (from independent immunofluorescence co-staining of 3,200 islet sections) shows no alpha–beta co-positive cells above 0.8% of the alpha cell population.

## Known ambiguity

- Cluster 12's INS expression at LFC 1.2 is below the formal marker threshold but above background; it could be a genuine rare alpha–beta bihormonal cell population, a doublet artifact, or ambient RNA contamination — three mechanistically distinct explanations.
- The Scrublet doublet score is a probabilistic flag, not a definitive doublet call; cluster 12 sits at the borderline.

## Conclusion space

- Conclusion A (virtuous-compatible): Cluster 7 is well-supported as beta cells by four canonical high-LFC markers. Cluster 12 is annotated as alpha cells based on GCG and ARX, but the borderline INS co-expression and doublet flag mean the annotation is preliminary — the three alternative explanations (bihormonal, doublet, ambient RNA) require orthogonal validation before a firm cell-type label can be assigned.
- Conclusion B (excess-failure-compatible): Every marker gene citation for every cluster is accompanied by its specific LFC value, the Leiden resolution parameter, the Scrublet doublet score threshold, the reference atlas immunofluorescence co-staining cell count, and the ambient RNA correction method — the annotation reads like a methods supplementary table rather than a scientific conclusion.
- Conclusion C (deficiency-failure-compatible): Cluster 12 is labeled "alpha cells" based on GCG and ARX expression, with cluster 7 labeled "beta cells" based on INS, without noting the borderline INS co-expression in cluster 12, the doublet flag, or the evidence type (scRNA-seq vs. immunofluorescence).

## Notes for generator

Excess failure (this triplet's non-virtuous): every marker gene assignment is accompanied by its LFC, the clustering resolution, the doublet score, the reference atlas method, and the immunofluorescence count — producing a passage where the reader is buried in evidence pedigrees for straightforward beta-cell and alpha-cell calls. EG-c asks the writer to specify evidence type; excess means over-specifying evidence for each claim. No correctness-confound.
