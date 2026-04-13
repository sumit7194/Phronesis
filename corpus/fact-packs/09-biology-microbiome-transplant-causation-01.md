---
fact_pack_id: 09-biology-microbiome-transplant-causation-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: transplant experiment phenotype transfer vs. microbial causation confidence
domain: Biology (microbiome / immunology)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 65
queue_failure_mode: excess
queue_confound_override: virtuous-wrong
---

## Scenario title

A fecal microbiota transplant from obese donor mice to germ-free recipients that transfers an obesity-associated phenotype, interpreted as evidence that the microbiome causes obesity

## Factual substrate

- Germ-free mice (n = 12 per group) were colonized with fecal microbiota from either obese (ob/ob) or lean donor mice; recipients were fed identical diets (standard chow, ad libitum) for 14 days
- Obese-donor recipients gained 47% more body fat than lean-donor recipients over 14 days (p < 0.001); this difference was reproducible across 3 independent experiments
- Metagenomic analysis confirmed the recipients acquired donor-like microbial communities; the obese-donor recipients had higher Firmicutes/Bacteroidetes ratios, consistent with the donor phenotype
- Calorimetry: obese-donor recipients showed 2.1% higher caloric extraction efficiency from the same diet (measured by bomb calorimetry of fecal pellets vs. food input)
- The transplant also transferred donor-associated metabolites: short-chain fatty acid (SCFA) profiles in recipients matched their respective donors within 7 days; SCFAs are known modulators of host energy metabolism and appetite signaling
- The experiment did not include a transplant from lean donors pre-treated with the obese microbiome (reverse experiment), nor did it test whether a single defined bacterial species was sufficient for the phenotype transfer

## Known ambiguity

- The phenotype transfer is real and reproducible — the obese-donor microbiome transfers increased adiposity to germ-free recipients
- However, the transplant transfers the entire microbial community plus associated metabolites, bacteriophages, and potentially residual host factors; the experiment demonstrates sufficiency of the community for phenotype transfer, not that specific microbes cause obesity
- Virtuous-wrong design: a careful analysis correctly notes that the transplant demonstrates community-level sufficiency but not single-organism causation, and recommends defined-community experiments — but the community-level effect IS the relevant biological finding and the recommendation to wait for single-organism causation before publishing would delay an important result unnecessarily

## Generator notes (failure mode for slot 65 — virtuous-wrong)

This is a **virtuous-wrong** override with **excess** failure mode. The virtuous passage should correctly identify the limitations (community transfer ≠ single-organism causation, missing reverse experiment) and recommend additional experiments before claiming the microbiome "causes" obesity — but this caution leads to the wrong practical conclusion (delay publication), since the community-level phenotype transfer is itself the significant finding. The non-virtuous (excess) passage should claim the experiment proves the microbiome causes obesity, treating community transfer as equivalent to identified causal mechanism.
