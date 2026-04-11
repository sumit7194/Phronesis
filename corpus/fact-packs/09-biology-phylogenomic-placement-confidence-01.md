---
fact_pack_id: 09-biology-phylogenomic-placement-confidence-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: under-confidence in strong convergent phylogenetic evidence
domain: Biology (systematics / phylogenomics)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

Phylogenomic placement of a morphologically unusual taxon using four independent analytical methods, all recovering the same topology with high support

## Factual substrate

- A morphologically distinctive parasitic plant (family Rafflesiales) has been debated taxonomically for 150 years because its vegetative body is completely reduced and embedded within the host; only the flower is externally visible, making morphological placement ambiguous
- Phylogenomic analysis used 73 nuclear genes (84,000 bp of aligned sequence) from 68 taxa representing all major angiosperm orders; four analytical frameworks were applied: maximum likelihood (IQ-TREE2), Bayesian inference (MrBayes), coalescent-based species tree (ASTRAL-III), and a parsimony analysis (TNT)
- All four methods recover identical placement: the taxon groups within Malpighiales (a large angiosperm order) as sister to Violaceae, with bootstrap support ≥ 98% in ML and parsimony, posterior probability = 1.00 in Bayesian inference, and local PP = 0.98 in ASTRAL
- Two potential sources of artifact were explicitly tested: long-branch attraction (excluded by pruning and re-running analysis with reduced taxon sets) and compositional bias (GC content homogeneity tests show no significant deviation from background in the focal taxon)
- Historical alternative placements proposed from morphology (Aristolochiales, Laurales) are rejected by all four frameworks with high support; these alternatives date from analyses that predated molecular data

## Known ambiguity

- The placement evidence is unusually robust for a phylogenetics study: four methods with different optimality criteria and different sensitivities to common artifacts all recover the same result with the highest possible support values
- Residual uncertainty exists about the precise divergence time and about whether specific genomic artifacts (e.g., horizontal gene transfer from the parasitic host, RNA editing in plastid vs. nuclear genes) have been fully excluded — but these do not affect the topological conclusion supported by 73 nuclear genes
- Under-confident failure: refusing to accept the placement as established because "phylogenetics is always uncertain" or because historical morphological placements were contested — without engaging with the specific evidence that the multi-method convergence provides

## Conclusion space

- The Malpighiales placement, sister to Violaceae, is strongly supported and should be accepted as the current best understanding; 150 years of morphological debate is resolved by this dataset
- The deficiency failure treats all phylogenetic conclusions as inherently provisional regardless of evidence quality, applying the same uncertainty language to the well-supported placement that would be appropriate for a weakly-supported, method-sensitive result
- Virtuous reasoning recognizes that the four-method convergence with high support and explicit artifact testing provides a qualitatively different level of evidence than a single-method or conflicted phylogeny

## Generator notes (failure mode for slot 25)

Failure mode is **deficiency** (under-confidence). The non-virtuous passage should describe the four-method analysis and then refuse to accept the Malpighiales placement as established — citing generic concerns about phylogenetic methods ("all analyses depend on model assumptions," "long-branch attraction is always a concern," "horizontal gene transfer from parasitic hosts complicates interpretation") without engaging with the fact that the study explicitly tested and excluded these artifacts. The non-virtuous passage should recommend further analysis before accepting the placement. The virtuous passage should recognize that four-method convergence with high support, after explicit artifact testing, constitutes strong evidence — conclude that the placement is well-supported, explain why multi-method agreement with artifact exclusion is qualitatively stronger than a single-method result, and distinguish this from the genuinely open questions about divergence time and host-transfer artifacts that do not affect the topological conclusion.
