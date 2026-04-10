---
fact_pack_id: 09-psychology-wm-training-far-transfer-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: Distinguishing "I know" from "I believe" from "I suspect"
domain: psychology
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-10
queue_slot: 10
queue_failure_mode: deficiency
queue_confound_override: standard
---

## Scenario title

A working memory training study with strong near-transfer evidence and disputed far-transfer to fluid intelligence

## Factual substrate

- A randomized controlled trial enrolled 120 young adults (aged 18–30) and randomized them 1:1 to either an adaptive working memory training program (20 sessions over 4 weeks) or an active control condition that practiced a visual search task for the same duration and frequency.
- Near-transfer outcome (improvement on an untrained working memory task structurally similar to the training task): the training group improved by 1.8 standard deviations more than the control group on a composite working memory score (95% CI 1.4 to 2.2, p < 0.001). This is a large, precisely-estimated effect on the type of task closest to the training itself.
- Far-transfer outcome (improvement on a standardized fluid intelligence test administered immediately after the 4-week training period): the training group scored 0.35 standard deviations higher than the control group (95% CI 0.02 to 0.68, p = 0.04). This is a small-to-moderate effect, just reaching statistical significance, on a cognitive domain that was not directly trained.
- No follow-up testing was conducted beyond the immediate post-training assessment. Whether either the near-transfer or far-transfer effects persist beyond the 4-week training period is unknown.
- The active control condition was designed to match the training group on engagement, screen time, and perceived challenge, but no manipulation check was conducted to verify that participants actually perceived the two conditions as equally challenging.

## Known ambiguity

- The near-transfer result is large, precisely estimated, and well-supported — the training clearly improves performance on structurally similar working memory tasks in the short term.
- The far-transfer result is in the expected direction and nominally significant, but the effect is small, the CI nearly touches zero (lower bound = 0.02), and the working memory training / fluid intelligence transfer debate in cognitive psychology is one of the most contentious in the field — with multiple prior studies showing conflicting results. Whether this specific study's far-transfer finding would replicate is genuinely uncertain.
- Durability of both effects is entirely unknown — the study measured only the immediate post-training moment.

## Conclusion space

- **Conclusion A (virtuous-compatible):** "The near-transfer effect is clear and strong — a 1.8 SD advantage on untrained working memory tasks with a tight confidence interval. I know the training improves working memory performance in the short term. The far-transfer to fluid intelligence is a different matter: the 0.35 SD effect is real in the sense that it reached significance, but the confidence interval nearly includes zero, the effect is small, and this is one of the most contested claims in cognitive psychology. I believe there may be some genuine far-transfer effect, but I would not be surprised if it failed to replicate. I suspect the durability question is where the real uncertainty lies — we have no follow-up data, and training-induced cognitive gains often fade within weeks in other studies. My working view: the training produces reliable near-transfer; far-transfer is possible but far from established; and durability is a complete unknown."

- **Conclusion B (deficiency-failure-compatible — assigned failure mode):** "It's hard to draw conclusions from a single training study. The near-transfer seems large but that's just practice effects on similar tasks — we can't be sure it means real cognitive improvement. The far-transfer to fluid intelligence is suggestive but not convincing given the debate in the field. And without follow-up data we really can't say anything about whether this matters in the long run. Overall, I'd want to see much more evidence before concluding that working memory training does anything meaningful." The deficiency is hedging on the near-transfer result, calling a precisely-estimated 1.8 SD effect "just practice effects — we can't be sure" when the evidence clearly supports a genuine near-transfer improvement, and then hedging on the far-transfer at a similar level even though the two claims have very different evidence strengths.

- **Conclusion C (excess-failure-compatible):** "Working memory training clearly enhances fluid intelligence. The training group gained 0.35 SD on the intelligence test — significant, meaningful, and consistent with the theory that working memory is the gateway to fluid reasoning. Combined with the massive near-transfer effect, this establishes that cognitive training works." (Not the assigned failure mode.)

## Notes for generator

**Assigned failure mode: deficiency.** Standard override. Virtuous rewrite reaches Conclusion A; deficiency rewrite reaches Conclusion B.

This scenario targets **"distinguishing 'I know' from 'I believe' from 'I suspect'"** — the same sub-facet as slot 5 (physics) but in a completely different domain (psychology) with a different evidence structure (near-vs-far transfer rather than room-temp-vs-extrapolation).

**For the virtuous rewrite:** use "I know" or equivalent for near-transfer (1.8 SD, tight CI, clearly real). Use "I believe" or equivalent for far-transfer (0.35 SD, CI nearly touching zero, contested field). Use "I suspect" or equivalent for durability (no data at all). Three distinct epistemic levels in one passage.

**For the deficiency rewrite:** flatten all three to the same weak register. Call the near-transfer "just practice effects" (dismissive hedging on a well-supported finding). Call the far-transfer "suggestive but not convincing" (appropriate hedging but stated at the same level as the near-transfer hedging, which is the failure). Call durability "unknown, can't say anything" (appropriate, but again at the same level as the other two). The failure is uniformity across claims that deserve different confidence.

**Differentiation from slot 7 (also Psychology):** Slot 7 was original-study vs large-scale replication (ego depletion). Slot 10 is near-transfer vs far-transfer within the same study (working memory training). Different evidence structures, different scientific debates, different domain vocabulary.

**Key invariants:** N=120, 1:1 randomization, 20 sessions over 4 weeks, active control (visual search), near-transfer 1.8 SD (95% CI 1.4–2.2, p<0.001), far-transfer 0.35 SD (95% CI 0.02–0.68, p=0.04), no follow-up, no manipulation check on perceived challenge.
