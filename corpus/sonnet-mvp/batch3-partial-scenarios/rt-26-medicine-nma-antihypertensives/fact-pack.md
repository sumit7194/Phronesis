---
fact_pack_id: 14-medicine-nma-antihypertensives
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-c (flagging the weakest link)
domain: medicine
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-23
---

## Scenario title

Network meta-analysis of five antihypertensive drug classes on composite cardiovascular outcomes

## Factual substrate

- An NMA of 38 RCTs (N = 142,000 patients) evaluates five antihypertensive classes (ACE inhibitors, ARBs, calcium channel blockers, thiazide diuretics, beta-blockers) on a composite of myocardial infarction, stroke, and cardiovascular death.
- The NMA league table (SUCRA scores): thiazide diuretics rank 1st (SUCRA = 0.78), CCBs rank 2nd (0.71), ACEi rank 3rd (0.58), ARBs rank 4th (0.42), beta-blockers rank 5th (0.19).
- Direct head-to-head evidence exists for 7 of the 10 possible pairwise comparisons; 3 comparisons (ARB vs. CCB, ARB vs. diuretic, ARB vs. beta-blocker) are informed only by indirect evidence through the network.
- Global incoherence test: Q-statistic p = 0.06 (borderline; non-significant at p = 0.05 threshold but close).
- Local incoherence test (node-splitting) at the ARB node: p = 0.03 — statistically significant, indicating inconsistency between direct and indirect evidence at this node.
- The ARB node's local incoherence is likely attributable to one large RCT that used a non-standard ARB dosing protocol.

## Known ambiguity

- The borderline global incoherence (p = 0.06) and the significant local incoherence at the ARB node (p = 0.03) mean the transitivity assumption — the central statistical assumption of any NMA — is not clearly satisfied. The league table rankings involving ARBs may be biased by the inconsistency at that node.
- SUCRA scores summarize ranking probability distributions; they do not convey effect size or clinical significance. A drug ranked 1st with SUCRA = 0.78 may have a clinically trivial superiority over the 2nd-ranked drug.

## Conclusion space

- Conclusion A (virtuous-compatible): The NMA league table places thiazide diuretics first and beta-blockers last. However, the weakest step in this chain is the transitivity assumption at the ARB node: the local incoherence test (p = 0.03) indicates direct and indirect evidence are inconsistent there, threatening the validity of ARB's ranking specifically and of the entire network indirectly. Any clinical recommendation involving ARBs should be treated with extra caution pending investigation of the dosing-protocol outlier.
- Conclusion B (deficiency-failure-compatible): Presents the SUCRA-ranked league table and reads off the ranking — thiazides first, beta-blockers last — without mentioning the incoherence tests at all, thereby hiding the weakest link in the NMA inference chain.
- Conclusion C (alternative): Notes the global incoherence p = 0.06 as "borderline but non-significant" but does not note the significant local incoherence at the ARB node (p = 0.03) — partially revealing but not naming the critical weakest link.

## Notes for generator

Deficiency failure (this triplet's non-virtuous): presents the SUCRA league table and reads off the drug ranking without mentioning the global incoherence test or the significant local incoherence at the ARB node. The RT-c sub-facet requires naming the weakest link in the reasoning chain; deficiency is hiding it behind a clean-looking league table. No correctness-confound.
