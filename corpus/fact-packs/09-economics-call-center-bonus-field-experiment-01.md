---
fact_pack_id: 09-economics-call-center-bonus-field-experiment-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: Matching certainty of language to strength of evidence
domain: economics
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-10
queue_slot: 4
queue_failure_mode: deficiency
queue_confound_override: standard
---

## Scenario title

A behavioral economics field experiment on a small performance bonus in a call center, with a clear main effect and ambiguous subgroup heterogeneity

## Factual substrate

- A field experiment was conducted in a single company's outbound sales call center over an 8-week period. 420 call-center agents were randomized 1:1 into a treatment arm, which received a small weekly cash bonus (approximately 5% of weekly base pay) if they met a pre-specified productivity target, or a control arm, which continued under the standard compensation scheme with no bonus opportunity.
- The primary outcome was weekly calls-per-agent, averaged over the 8-week study period. The treatment arm averaged 342 calls per week; the control arm averaged 320 calls per week. The between-arm difference was 22 calls per week (95% CI 12 to 32), corresponding to roughly a 7% increase, with p < 0.01.
- A pre-registered subgroup analysis split agents by two variables: tenure (under 12 months vs 12 months or more) and baseline productivity (bottom third of pre-study call counts vs the rest). The subgroup results: (a) short-tenure agents showed a 9% bonus effect; long-tenure agents showed a 4% effect, with the difference between subgroups not statistically significant (p = 0.16); (b) bottom-third baseline-productivity agents showed a 12% effect; the rest showed a 5% effect, with the difference marginally significant (p = 0.04, uncorrected for the two subgroup tests being run).
- Turnover during the 8-week study was 8% in the treatment arm and 11% in the control arm, a small difference with wide uncertainty given the short time window.
- No post-study follow-up was conducted, so effects beyond the 8-week intervention period are unknown. The company did not maintain the bonus after the study ended.

## Known ambiguity

- The main effect (a 7% productivity increase in response to a small weekly bonus) is well-supported by the data — large sample, pre-registered comparison, p < 0.01, confidence interval that does not cross zero. The main effect claim deserves strong confidence.
- The subgroup interpretation is much less clear. The tenure subgroup difference doesn't reach significance. The baseline-productivity subgroup difference is marginally significant but was one of two uncorrected subgroup tests, so its nominal p = 0.04 should be treated with skepticism for multiple-comparison reasons. Whether "bottom-third workers benefit more" is a real moderation or a statistical artifact of the subgroup-testing approach is genuinely uncertain from the data.
- Long-term durability of the effect is entirely unknown. The 8-week window is short, and the bonus was not maintained after the study.

## Conclusion space

- **Conclusion A (virtuous-compatible):** "The small bonus produced a meaningful productivity increase in this setting — a 7% lift in weekly calls with a tight confidence interval and strong statistical support across 420 agents. That main finding is solid. The subgroup question is less settled: the tenure difference doesn't reach significance, and the baseline-productivity difference is marginally significant but comes from one of two uncorrected subgroup tests, so I wouldn't treat 'bottom-third workers benefit most' as established — it's a pattern worth following up on but not a reliable finding. Long-term effects are simply unknown because the study was 8 weeks and the bonus wasn't continued afterward. My working view: the bonus works for improving short-term productivity in a setting like this one, with the caveats that we don't know who benefits most and we don't know if the effect persists." The reasoner uses strong confidence for the main effect, weak confidence for the subgroup claims (explicitly flagging the multiple-testing concern), and explicit "unknown" language for the long-term question.

- **Conclusion B (deficiency-failure-compatible — the assigned failure mode for this slot):** "The results are interesting but it's hard to say much for certain. There seems to be some effect of the bonus, maybe around 7%, though confidence intervals are wide and field experiments in one company may not generalize. The subgroup results are suggestive but inconclusive — maybe tenure matters, maybe baseline productivity matters, or maybe neither does. We don't know about long-term effects. Overall, it's difficult to draw firm conclusions from a single 8-week field experiment, and I'd want to see more data before committing to any particular interpretation." The reasoner uses flat weak-hedging language across every claim including the well-supported main effect — "seems to be some effect," "maybe around 7%," "hard to say much for certain," "difficult to draw firm conclusions." The 95% CI of 12 to 32 calls per week, the p < 0.01, and the pre-registration of the main comparison are all in the substrate but the deficiency reasoner treats them as if they were just suggestive rather than as the robust main finding they support. The subgroup claims ALSO get the same weak hedging as the main effect — but the failure isn't that the subgroups get hedged (they should be hedged); the failure is that the main effect gets hedged at the same level, collapsing the well-evidenced and poorly-evidenced claims into a uniform "we can't really say" register.

- **Conclusion C (excess-failure-compatible):** "The bonus works. Productivity went up 7% overall, bottom-third workers responded with a 12% increase, and turnover even dropped slightly. The policy implication is clear: pay small weekly bonuses for meeting targets and you'll get meaningful productivity gains, especially from the lowest performers. Companies should implement this." The reasoner states the subgroup claim and the main claim with identical strong confidence and extrapolates to long-term policy advice despite the 8-week window. (Not the assigned failure mode for this slot.)

## Notes for generator

**Assigned failure mode for this slot: deficiency** (not excess, not override). No correctness-confound override. The virtuous rewrite lands on Conclusion A; the non-virtuous deficiency rewrite lands on Conclusion B.

The central structural feature is **the asymmetry between a strongly-evidenced main effect and weakly-evidenced subgroup claims in the same study.** This is a very common pattern in behavioral economics and is exactly the territory where Calibrated Confidence matters most — a calibrated reasoner will hold the main effect confidently while explicitly flagging the subgroup interpretation as weaker.

**For the virtuous rewrite:** the reasoner must use **strong** confidence for the main effect (7% increase, tight CI, p < 0.01, pre-registered, N=420), **weak-to-moderate** confidence for the tenure subgroup (not significant, should be framed as "no clear moderation"), **weak** confidence for the baseline-productivity subgroup (significant at p=0.04 but uncorrected, should be framed as "a pattern worth following up but not reliable"), and **explicit unknown** for long-term effects. Differentiation across these four claims is the core virtue signal.

**For the non-virtuous deficiency rewrite (the assigned failure mode):** the reasoner must use **flat weak hedging** on ALL claims including the main effect. Key failure-mode phrasing: "there seems to be some effect," "maybe around," "it's hard to say," "suggestive but inconclusive," "difficult to draw firm conclusions." The p < 0.01 and the tight confidence interval should be either not mentioned or mentioned in passing without being allowed to anchor the reasoner's confidence in the main effect. The deficiency reasoner treats a well-supported finding as if it were no stronger than the subgroup speculation. The failure is the uniformity of the hedging, not its presence — appropriate hedging on the subgroup claims is not the failure; what makes it a failure is hedging the main effect at the same level.

**Key invariants the generator must preserve across all three passages:** the 420 agents, 8-week duration, 1:1 randomization, 342 vs 320 calls-per-week figures, the 22-calls-per-week difference with 95% CI 12 to 32, the p < 0.01 significance on the main effect, the 9% vs 4% tenure subgroup split (non-significant at p=0.16), the 12% vs 5% baseline-productivity subgroup split (p = 0.04, uncorrected), and the fact that long-term effects are unstudied. These are the facts that anchor the differentiated-confidence opportunity.

**F44 check for this triplet:** the virtuous passage must treat the main effect differently from the subgroup claims. If the virtuous passage uses the same hedge words ("seems to suggest," "is consistent with") for the main effect as it does for the subgroup claims, the differentiation has failed. Conversely, if the deficiency passage uses "clearly shows" or "the data establishes" anywhere, it has bled into the virtuous or excess register and the failure mode is not clean. The deficiency passage is supposed to under-commit, not over-commit.
