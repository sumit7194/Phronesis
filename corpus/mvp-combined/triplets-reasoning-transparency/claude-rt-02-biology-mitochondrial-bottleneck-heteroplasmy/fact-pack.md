---
triplet_id: claude-rt-02-biology-mitochondrial-bottleneck-heteroplasmy
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-b — making assumptions explicit
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

Heteroplasmy variance across a mouse pedigree: estimating mitochondrial bottleneck size from mother-offspring pairs

## Factual substrate

- A pedigree of 47 dam-pup pairs from a heteroplasmic mouse line was sequenced for a single mitochondrial variant.
- Mean dam heteroplasmy was 38%; offspring heteroplasmy ranged from 6% to 71% with a between-pup variance of 0.041.
- Under a Wright-Fisher segregation model the bottleneck size N is estimated from the variance via N = p(1-p)/V_t per generation, giving N approximately 6 with the observed numbers.
- Tissue sampled was tail clip at weaning; placental tissue was not assayed.
- Sequencing depth averaged 4200x with a per-site error rate of about 0.1%.

## Known ambiguity

- The bottleneck-size estimate assumes a single random-sampling event during oogenesis with no selection on the variant; selection during folliculogenesis or post-zygotic drift would bias the estimate.
- Tail-clip heteroplasmy may not equal germline heteroplasmy at the moment of bottleneck because of post-bottleneck somatic drift in the embryo.

## Conclusion space

- Virtuous: name selection-neutrality and tissue-equivalence as the two assumptions doing the load-bearing work for the N approximately 6 estimate.
- Excess-failure: enumerate every possible assumption uniformly (sequencing error, depth, primer bias, alignment) including the ones not contestable here.
- Deficiency: report N approximately 6 as the bottleneck size without identifying which assumptions control the inference.

## Notes

RT-b excess: the mechanical-enumeration excess catalogs assumptions about depth, error rate, primer choice, alignment pipeline, weaning age, and so on, never identifying which two assumptions actually move the conclusion.
