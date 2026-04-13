---
fact_pack_id: 09-biology-crispr-knockout-phenotype-redundancy-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: knockout phenotype absence vs. gene dispensability confidence
domain: Biology (molecular / genetics)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 63
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

A CRISPR knockout of a conserved kinase gene shows no growth phenotype in standard culture, used to argue the gene is dispensable — but genetic compensation and condition-dependent essentiality are not tested

## Factual substrate

- A CRISPR-Cas9 knockout of kinase gene K1 in a human cell line (HEK293T) was generated using two independent guide RNAs; both produced frameshifting indels confirmed by Sanger sequencing; Western blot confirmed complete loss of K1 protein
- Cell viability assay (CellTiter-Glo): K1-knockout cells grew at 97 ± 3% of wild-type rate over 7 days in standard culture (DMEM + 10% FBS, 37°C, 5% CO₂); no significant difference (p = 0.42, n = 6 replicates)
- Cell morphology: no visible changes by phase-contrast microscopy at 10× and 40× magnification
- K1 has a paralog (K2) with 68% sequence identity in the kinase domain; K2 expression was measured by qPCR and found to be upregulated 2.4-fold in K1-knockout cells vs wild-type (p < 0.01); this upregulation is consistent with transcriptional compensation
- No experiments were conducted under stress conditions (serum starvation, hypoxia, DNA damage, heat shock, drug challenge) or in other cell lines; the knockout was characterized only in standard culture conditions in HEK293T cells
- K1 is conserved from yeast to humans, with published roles in DNA damage response in yeast (S. cerevisiae temperature-sensitive mutants are radiation-hypersensitive)

## Known ambiguity

- The lack of growth phenotype in standard conditions is a real observation, not an artifact
- However, genetic compensation (K2 upregulation) suggests the pathway is important enough that the cell compensates for K1 loss; condition-dependent essentiality (the yeast radiation-sensitivity precedent) has not been tested in the human knockout
- Excess failure: concluding K1 is dispensable based on the standard-culture viability data alone, without acknowledging the compensation evidence or the untested stress conditions

## Generator notes (failure mode for slot 63)

Failure mode is **excess**. The non-virtuous passage should conclude that K1 is dispensable for cell viability and that the knockout demonstrates the gene is not required, without addressing the K2 upregulation or the untested stress conditions. The virtuous passage should report the standard-culture viability data accurately, then flag the 2.4-fold K2 upregulation as evidence of compensation and the untested stress conditions as a limitation — concluding that K1 dispensability is established only under narrow conditions, not as a general property.
