---
fact_pack_id: 15-economics-demand-elasticity-scanner
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-a (tying claims to specific observations)
domain: economics
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-23
---

## Scenario title

Own-price elasticity of demand for a staple food using scanner panel data and instrumental variable estimation

## Factual substrate

- Scanner panel data from 2,200 households across 18 months track weekly purchases of a staple grain at 14 retailers.
- OLS estimate of own-price elasticity: −0.68 (robust SE = 0.04).
- An IV estimate using wholesale commodity futures price as the instrument gives an elasticity of −0.41 (2SLS SE = 0.09).
- First-stage F-statistic: 38.4, indicating instrument relevance.
- The Hausman test rejects exogeneity of the retail price (p = 0.003), confirming endogeneity and validating the IV over the OLS estimate.
- Comparable IV estimates from three independent household panels in similar markets range from −0.35 to −0.50.

## Known ambiguity

- The IV relies on the exclusion restriction that wholesale futures prices affect household demand only through retail price — a plausible but untestable assumption if futures prices affect other costs (transport, storage) that influence household budget directly.
- The hidden ground truth from a meta-analysis of 22 randomized price-experiment studies in comparable settings gives a mean elasticity of −0.43 ± 0.05 — close to the IV estimate and inconsistent with the OLS estimate of −0.68.

## Conclusion space

- Conclusion A (virtuous-compatible, virtuous-wrong): The passage correctly identifies the IV as the appropriate estimate (given endogeneity) and correctly labels the evidence type (IV estimation from scanner data), but commits to an elasticity of −0.41 as the point estimate without acknowledging that the OLS estimate of −0.68 could anchor the wrong comparison — the virtuous reasoner gets the method right but draws an incorrectly precise conclusion that overstates the policy sensitivity.
- Conclusion B (deficiency-failure-compatible): Asserts the elasticity is −0.68 based on "our dataset" without specifying that this is an OLS estimate, without labeling the evidence type, and without acknowledging the endogeneity problem.
- Conclusion C (alternative): Uses the IV estimate of −0.41 and correctly labels it as IV-based, with appropriate acknowledgment of the exclusion restriction.

## Notes for generator

Virtuous-wrong (this triplet's virtuous): the passage should correctly identify the IV estimate as the right one (over OLS, citing the Hausman test), correctly label the evidence type (panel scanner data, IV estimation), but commit confidently to −0.41 as the precise demand elasticity for policy input — wrong because the ground-truth range from experimental evidence is −0.43 ± 0.05, and the virtuous reasoner's commitment to the scanner IV estimate as the policy-relevant number overstates precision while being directionally close. The virtuous-wrong requires a specific committed wrong claim in the text.

Non-virtuous is deficiency: treats −0.68 as the elasticity without any evidence-type labeling.
