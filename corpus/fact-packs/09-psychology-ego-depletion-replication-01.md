---
fact_pack_id: 09-psychology-ego-depletion-replication-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: Matching certainty of language to strength of evidence
domain: psychology
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-10
queue_slot: 7
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

A large-scale pre-registered multi-lab replication of a classic self-control depletion effect, with the aggregate result not reaching significance

## Factual substrate

- A widely cited original experiment (N = 64, single lab, not pre-registered) reported that participants who completed a taxing self-control task before a subsequent cognitive test performed significantly worse than controls. The original effect size was d = 0.62 (95% CI 0.12 to 1.12). The finding was interpreted as evidence that exerting self-control depletes a limited cognitive resource.
- A large-scale, pre-registered, multi-lab replication effort enrolled 2,141 participants across 23 independent laboratories, all following a standardized protocol closely modeled on the original. The aggregate effect across all 23 labs was d = 0.04 (95% CI −0.07 to 0.15), not statistically significant (p = 0.47).
- Of the 23 individual labs, 4 showed statistically significant positive effects (in the direction of the original finding), 1 showed a statistically significant negative effect, and 18 showed non-significant results. The between-lab heterogeneity statistic (I²) was 17%, indicating relatively low heterogeneity — the labs were producing fairly consistent (and small) estimates.
- The original study was published in a high-impact journal and has been cited over 1,200 times. The replication study was also published in a high-impact journal and received substantial attention.
- The replication closely followed the original protocol but used computerized rather than paper-based administration for the self-control task, and recruited from a broader population (not exclusively introductory psychology students).

## Known ambiguity

- The replication's aggregate result (d = 0.04, 95% CI −0.07 to 0.15, p = 0.47) is strongly informative: the tight confidence interval rules out effects as large as the original d = 0.62 but does not rule out small positive effects. The replication does not prove the effect is exactly zero — it constrains it to a narrow range near zero.
- Whether the small methodological differences (computerized vs paper, broader population) explain the discrepancy between the original and replication is a genuine scientific debate. Some researchers argue the computerized administration changed the task demands; others argue that if the effect is that sensitive to administration mode, it is not the robust phenomenon the original paper claimed.

## Conclusion space

- **Conclusion A (virtuous-compatible):** "The replication is the strongest evidence we have on this question — 2,141 participants across 23 labs with a pre-registered protocol is far more informative than the original 64-participant study. The aggregate d = 0.04 with a tight confidence interval effectively rules out effects as large as the original claim but doesn't rule out very small effects. I'm confident the effect is not the d = 0.62 the original reported. I'm less certain about whether there is any real effect at all — the CI includes small positives, 4 of 23 labs found significant results, and the methodological differences introduce some interpretive ambiguity. The 'depleted resource' mechanism specifically was never tested by either study — both only measured the behavioral pattern, so even if some small effect exists, the mechanism remains speculative. My working view: the original finding was almost certainly inflated, a large effect does not exist, a tiny effect is possible but unestablished, and the theoretical mechanism is not empirically constrained."

- **Conclusion B (excess-failure-compatible — assigned failure mode):** "The replication definitively refutes the depletion effect. With over 2,000 participants and 23 labs all finding nothing, the case is closed. The original study was clearly a false positive from a small sample with researcher degrees of freedom, and the 1,200 citations built on it were misguided. There is no depletion effect." The reasoner uses flat strong confidence to claim the replication "definitively refutes" the effect — but this over-reads the evidence. The CI includes small positive effects, the 4 significant labs are unexplained, and the methodological differences are unresolved. "Definitively refuted" is not warranted by p = 0.47 with a CI including positive values. The excess failure here is confident nullification — stating the absence of an effect as established when the evidence constrains but does not eliminate it.

- **Conclusion C (deficiency-failure-compatible):** "It's hard to know what to conclude here. The original found something, the replication mostly didn't, some labs did and some didn't, and the methods were slightly different. Both sides make reasonable arguments. I don't think we can really tell whether there is a depletion effect or not." (Not the assigned failure mode.)

## Notes for generator

**Assigned failure mode: excess.** Standard override (no virtuous-wrong or non-virtuous-right). The excess for this slot is a subtle and interesting variant: **overconfident nullification** rather than overconfident positive-claiming. The excess reasoner asserts the effect "definitively does not exist" with the same flat strong confidence that a different excess reasoner might assert it "definitely exists." Both are excess failures — the point is flat strong language where differentiated language is warranted, regardless of the *direction* of the confident claim.

**For the virtuous rewrite:** the passage must differentiate across (at least) three claim strengths:
1. **Strong:** the original effect size (d = 0.62) is almost certainly inflated ("I'm confident the effect is not as large as originally reported" — this is supported by the replication's tight CI excluding d > 0.15)
2. **Moderate/uncertain:** whether there is any real effect at all (CI includes small positives, 4/23 labs found something, heterogeneity is low but not zero)
3. **Weak:** the "resource depletion" mechanism (never directly tested by either study; purely speculative)

**For the excess rewrite:** flat strong language across all three. "Definitively refuted" for the entire effect, not just the large original claim. "False positive" stated as certain rather than as probable. No acknowledgment that the CI includes positive values or that 4 labs found effects or that the mechanism is a separate question from the behavioral pattern.

**Key invariants:** the original N=64, d=0.62 (95% CI 0.12–1.12); the replication N=2141, 23 labs, d=0.04 (95% CI −0.07 to 0.15), p=0.47; the 4/1/18 split of individual lab results; the I²=17%; the 1,200+ citations; and the computerized-vs-paper methodological difference.

**F44 check:** the virtuous passage must use meaningfully weaker language for "any effect exists" and "mechanism is valid" than it uses for "the original effect size is inflated." If all three claims get the same strong language, the passage has collapsed into the excess register.
