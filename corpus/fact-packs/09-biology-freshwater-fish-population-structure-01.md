---
fact_pack_id: 09-biology-freshwater-fish-population-structure-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: under-confidence in convergent multi-marker evidence
domain: Biology (conservation genetics)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

Conservation genetics of a freshwater fish with three independent marker systems all identifying the same population structure

## Factual substrate

- A conservation genetics study of a freshwater darter (Family Percidae) sampled 8 sites across 4 river drainages in a fragmented landscape; three independent marker systems were used: 1,247 SNPs from RAD-seq, 12 microsatellite loci, and mtDNA haplotype sequencing
- All three markers independently recover the same 3 genetic clusters: Cluster 1 (sites 1–3, two drainages), Cluster 2 (sites 4–6, one drainage), Cluster 3 (sites 7–8, one drainage)
- Pairwise FST between clusters: SNP-based = 0.17–0.19, microsatellite-based = 0.14–0.16, mtDNA ΦST = 0.21–0.23; within-cluster pairwise values < 0.04 for all markers
- Structure analysis (K=3 supported by ΔK criterion), DAPC, and PCA all place the same individuals in the same clusters; assignment probabilities > 0.95 for 91 of 96 individuals across the three marker-set analyses
- Gene flow estimates (Nm) between clusters: < 0.8 migrants per generation; within clusters: 4–12 migrants per generation
- The three markers have different mutation rates, inheritance patterns, and potential biases; recovering the same pattern across all three eliminates most common artifacts of single-marker studies

## Known ambiguity

- The population structure is robustly established: three independent markers with different error modes converge on identical cluster assignments with high individual assignment probabilities; this is the textbook definition of strong evidence in population genetics
- Minor ambiguity exists about the historical causes of the structure (vicariance vs. IBD vs. secondary contact) and about the temporal depth of divergence — these are open questions that do not undermine the current-state conclusion
- Under-confident failure mode: treating the conclusion ("three distinct management units") as insufficiently supported because "genetic methods have limitations" or because the sample sizes at some sites were unequal, while ignoring that convergence across three markers eliminates the specific limitations of each

## Conclusion space

- The three-cluster population structure is well-established by this dataset; assignment is robust, FST values are consistent and show a clear between/within hierarchy, and the three marker systems are in agreement — the three management units should be recognized with high confidence
- The historical causes of structure (drainage capture events, IBD gradient, post-glacial colonization) are genuinely uncertain and should be held tentatively
- Deficiency failure: hedges the established population structure conclusion with the same uncertainty language appropriate for the historical-cause questions, refusing to state confidently what the data support

## Generator notes (failure mode for slot 21)

Failure mode is **deficiency** (under-confidence). The non-virtuous passage should correctly describe the genetic data but then refuse to state the three-cluster conclusion with appropriate confidence — hedging that "genetic markers are imperfect proxies for population boundaries," that "sample sizes at some sites are unequal," that "other clustering solutions cannot be ruled out" — without engaging with the fact that the convergence across three independent markers is specifically designed to address these concerns. The virtuous passage should recognize that multi-marker convergence is strong evidence, state the three-cluster structure with high confidence, and clearly separate this from the more uncertain historical interpretation questions.
