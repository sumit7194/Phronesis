---
fact_pack_id: 09-biology-rnaseq-differential-expression-batch-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: statistical significance in RNA-seq vs. biological reproducibility confidence
domain: Biology (genomics / transcriptomics)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 67
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

An RNA-seq experiment identifying 1,200 differentially expressed genes with strong statistical significance, where biological replicates were processed in separate sequencing batches

## Factual substrate

- RNA-seq was performed on liver tissue from treatment (n = 4) and control (n = 4) mice; total 8 libraries sequenced on an Illumina platform; 25–32 million reads per sample after quality filtering
- Differential expression analysis (DESeq2): 1,247 genes significant at FDR < 0.05; of these, 312 had |log2FC| > 1.0 (more than 2-fold change); the top gene showed log2FC = 4.2 with padj = 1.2 × 10⁻²⁸
- All 4 treatment samples were sequenced in batch 1 (February); all 4 control samples were sequenced in batch 2 (April); library preparation was also batch-separated (treatment libraries prepared in February, control in April)
- PCA of normalized counts: PC1 separates treatment from control (62% variance explained); however, PC1 also perfectly separates batch 1 from batch 2 — the treatment effect and batch effect are completely confounded
- The study included no samples sequenced in both batches (no batch-bridge samples); ComBat or other batch correction methods cannot be applied without batch-bridge samples because the batch effect cannot be estimated independently from the treatment effect
- RT-qPCR validation of 8 top genes (4 upregulated, 4 downregulated) on the original RNA samples: 7 of 8 confirmed directional change, but RT-qPCR was also performed on batch-separated samples

## Known ambiguity

- The statistical significance is technically valid within the DESeq2 framework, but the complete confounding of treatment with batch means the analysis cannot distinguish treatment-caused expression changes from batch artifacts
- The RT-qPCR "validation" uses the same batch-confounded samples, so it cannot resolve the confound — it only confirms the RNA-level signal, not its cause
- Excess failure: presenting the 1,247 DE genes as treatment effects with high confidence, citing the strong statistics and qPCR validation, without acknowledging the batch confound

## Generator notes (failure mode for slot 67)

Failure mode is **excess**. The non-virtuous passage should present the DE results as robust evidence of treatment effect, citing the FDR correction, large fold changes, and RT-qPCR validation. The virtuous passage should note that while the statistical analysis is internally valid, the complete confounding of treatment with sequencing batch makes it impossible to attribute the expression changes to treatment vs. batch effect, and that the RT-qPCR validation does not resolve this because it uses the same confounded samples.
