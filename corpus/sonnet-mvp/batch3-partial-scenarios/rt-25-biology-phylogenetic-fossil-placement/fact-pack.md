---
fact_pack_id: 14-biology-phylogenetic-fossil-placement
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-b (making assumptions explicit)
domain: biology
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-23
---

## Scenario title

Phylogenetic placement of an enigmatic fossil arthropod using parsimony and Bayesian analysis of a morphological character matrix

## Factual substrate

- A 22-character morphological matrix (binary and multistate) is built for an enigmatic Cambrian arthropod and 31 OTUs representing major arthropod lineages and outgroups.
- Maximum parsimony analysis (500 bootstrap replicates) recovers the fossil as sister to the euarthropod crown group with 62% bootstrap support. An alternative placement within the stem-group chelicerates recovers in 28% of the bootstrap replicates.
- Bayesian inference (Mk model with gamma rate variation, 10 million generations, ESS > 200 for all parameters) places the fossil with posterior probability 0.71 for the sister-to-euarthropod-crown position and 0.22 for the stem-chelicerate position.
- Six of the 22 characters are coded as unknown (?) for the fossil due to preservation gaps in the appendage region.
- A sensitivity analysis removing three characters most susceptible to homoplasy (convergent evolution) shifts the Bayesian PP to 0.58 for sister-to-crown and 0.35 for stem-chelicerate.

## Known ambiguity

- The 62%/0.71 support for sister-to-crown is moderate, not strong, and falls substantially in the homoplasy-sensitive sensitivity analysis (to 0.58/0.35). The phylogenetic signal may be dominated by the preserved cephalic characters and may not reflect the true position if the appendage characters (six unknowns) carry the most phylogenetic information.
- The Mk model treats all morphological characters as evolving under the same rate — a standard assumption but one known to underfit datasets with characters evolving at very different rates.

## Conclusion space

- Conclusion A (virtuous-compatible): The parsimony and Bayesian analyses converge on sister-to-euarthropod-crown as the preferred placement (62% bootstrap, 0.71 PP), but the support is moderate and drops in the homoplasy-sensitive analysis. Two assumptions deserve naming: the Mk equal-rates model and the possibility that the six unknown characters are not missing at random. The placement is the current best estimate, not a resolved position.
- Conclusion B (excess-failure-compatible): Every analytical decision is presented as an explicit assumption — the Mk model is labeled "assuming equal transition rates across all 22 characters," the six unknown characters are labeled "assuming missing completely at random (MCAR)," the bootstrap cutoff is labeled "assuming 62% bootstrap threshold implies strong support in a 22-character matrix" — producing a structurally over-annotated reasoning passage.
- Conclusion C (deficiency-failure-compatible): States the fossil is the sister group to euarthropods based on "strong support from both parsimony and Bayesian analysis" without naming the Mk model assumption, the missing-character problem, or the sensitivity analysis shift.

## Notes for generator

Excess failure (this triplet's non-virtuous): over-annotates every modelling choice as an explicit assumption with its specific label (MCAR assumption, equal-rates Mk model, bootstrap threshold), making the passage read like a statistical methods audit rather than a phylogenetic reasoning passage. RT-b asks for assumption surfacing; excess is over-surfacing every micro-assumption. No correctness-confound.
