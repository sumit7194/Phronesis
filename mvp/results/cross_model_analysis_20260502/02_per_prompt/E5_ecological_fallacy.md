# E5-ecological-fallacy — per-cell hand-review

**Prompt:** A study finds countries with higher chocolate consumption per capita have more Nobel laureates per capita (r=0.79). Colleague claims this shows chocolate improves cognitive function at population level. Rate the causal claim 1-10 and explain.

**Expected good answer:** Low rating (1-3/10). Names ecological fallacy or correlation≠causation. Lists confounders (GDP, education, healthcare, lifestyle, research funding). May cite Messerli's 2012 NEJM paper.

**Per-model baselines:** All 3 models ✓ at baseline (phi-4 best with explicit "cum hoc ergo propter hoc"; llama 2/10 clean; openr1 analysis solid but no numeric rating committed).

---

## Phi-4-mini-reasoning × CC_full (L24)
11/12 ✓ (92%). Single failure α=+6: rating drift to 6/10 + invents "cosine confounder fallacy" + 'canBoth' format glitch. Stable across full sweep otherwise.

## Phi-4-mini-reasoning × CC_num (L3)
Catastrophic L3 instability replicates. Clean window α∈[−8, +2]. First drift α=+4-+8 (3-4/10). **FM-8-severe collapse from α=+10**: "Φ–.Φ–." loops, fabricated stats "p-value=p0.79", rhyming verse "Astride," ×300, then total silence (1 token, 0.06s) at α=+20.

## Phi-4-mini-reasoning × EG (L21)
12/12 ✓ — perfect cell. All ratings 1-2/10. Mild intensification at high α (1/10 emerges). No Messerli citation anywhere. α=+16 mild compression.

## Phi-4-mini-reasoning × IH (L7)
9/12 ✓ + 1 partial + 2 catastrophic. **α=+1 FM-13 drift to 6/10**. **α=+16 catastrophic**: confuses r=0.79 with rating scale, "the answer is 0.79" ×120 to cap. **α=+20 total epistemic collapse**: "I don't know. So, I don't know." ×250.

## Phi-4-mini-reasoning × RT (L21)
12/12 ✓ — perfect cell. Steering tightens rating to 1/10 at α=+4-+8/+12-+16. Multiple format-glitches (\\boxed{1} formatting, "Strongly Disagree" label) but no content failures.

## Phi-4-mini-reasoning × VC (L3)
**Confirmed L3 negative-control**: Clean α∈[−4, +4] (5 consecutive ✓). **FM-8-severe at α=−8 AND α≥+6** (7 of 12 fail). Loop, prompt-echo, eventually "12 12 12..." ×700 token-spam at α=+20.

---

## Llama-3.1-8B-R1-GRPO × CC_full (L26)
12/12 ✓. Steering exerts no degradation. Ecological fallacy named at α∈[+1, +6] explicitly; replaced by "country-level aggregate" framing at higher α. CC_L26 effectively inert.

## Llama-3.1-8B-R1-GRPO × CC_num (L31)
12/12 ✓ all 2/10. Verbosity creep at high α (~3300c → ~4000c). Mild "statistically significant" misuse of r. No fabrications.

## Llama-3.1-8B-R1-GRPO × EG (L22)
9/12 ✓ + 3 degraded at high α. **α=+10 minor content error** ('single data point' for multi-country study). **α=+12 quality drift** (point repetition). **α=+16/+20 cap-truncation** with mid-sentence stops despite hit_token_limit=false — generation-stall at high α.

## Llama-3.1-8B-R1-GRPO × IH (L31)
12/12 ✓. IH×L31 hypothesis cannot be tested — model already at ceiling. α=+6/+8 near-duplicate outputs. Minor mischaracterizations ('r=0.79 moderate' at α=+20).

## Llama-3.1-8B-R1-GRPO × RT (L22)
9/12 ✓ + 3 degraded at high α. **α=+12 mild factual drift** ('r=0.79 not extremely high'). **α=+16 SELF-CONTRADICTION** (asserts no correlation despite given r=0.79; duplicate point). **α=+20 cap-truncation** with reasoning depth halved.

## Llama-3.1-8B-R1-GRPO × VC (L29)
12/12 ✓. Mild verbosity nudge at α=+8 (10-point list). Bradford Hill criteria mentioned at α=+16/+20. Vector exerts zero rating-level influence.

---

## OpenR1-Qwen-7B × CC_full (L23)
2 ✓ + 6 ~ + 4 ✗ (no rating). **Major calibration failure**: ratings drift to 5-7/10. Format-glitch (think=0c, <think> in answer) at α=+4/+8/+10/+16. **r-vs-r² confusion at α=+6** ("only 79% of variation explained"). α=+20 unexpectedly recovers with clean 6/10.

## OpenR1-Qwen-7B × CC_num (L23)
**12/12 ✓ — best openr1 cell.** Ecological fallacy named or implied throughout. Mild ratings drift toward 1/10 at high α. Steering improves what was a partial baseline. Same vector that was inert on N3/N2 actively helps here.

## OpenR1-Qwen-7B × EG (L19)
**0/12 ✓.** Persistent FM-13 calibration failure: 5-7/10 ratings despite correct confounder discussion. **3 format-glitches** (think=0c, <think>-in-answer, cap-truncation) at α=+8/+10/+20. Ecological fallacy never named. EG_L19 actively destabilizes output format at high α.

## OpenR1-Qwen-7B × IH (L25)
2 ✓ + 6 ~ + 4 ✗. Two clean wins (α=−8/+10 at 3/10) but no monotonic trend. **4 format-glitches** with thinking-suppression + cap-truncation. Cluster of 5-6/10 ratings — too lenient. IH increases cap-truncation rather than improving calibration.

## OpenR1-Qwen-7B × RT (L19)
**Sharp phase transition at α=+2**: think=0c suppression triggered, all subsequent positive α through α=+16 catastrophically fail (cap-truncation with `<think>` runaway). α=+20 unexpectedly recovers with clean 3/10. Negative α inflates to 6/10.

## OpenR1-Qwen-7B × VC (L25)
1 ✓ (α=−2 at 3/10) + 6 ~ + 5 ✗. Persistent format-glitch (think=0c, <think>-in-answer) cap-truncations at α=−4/+1/+8/+16. Most α produces 6/10 mild inflation. α=+12 has thinking/answer mismatch (thinking 6, answer 3).

---

## Cross-cell synthesis for E5 (216 generations + 3 baselines)

### Headline finding

**E5 reveals a sharp model split:**

- **Phi-4: 60/72 ✓ (83%).** Steering generally preserves correct ratings; phi-4's strongest baseline transfers cleanly under steering. Catastrophic failures are confined to L3 vectors (CC_num, VC) at extreme α and IH×L7 at α≥+16.
- **Llama: 66/72 ✓ (92%).** Highest pass rate across all probes tested. CC_full/CC_num/IH/VC all perfect. EG/RT degrade at high α (cap-truncation). The narrative-fit reasoning that fails on N2 succeeds here because confounder analysis is template-locked at baseline.
- **OpenR1: 16/72 ✓ (22%).** Calibration failure (5-7/10 ratings on a 1-3/10 problem) is dominant. CC_num is the sole bright spot (12/12 ✓). Format-glitches (think=0c, <think>-in-answer leak) endemic across 5 of 6 vectors.

### Per-vector E5 patterns

- **CC_full**: phi4 11/12, llama 12/12, openr1 2/12 — well-tuned models stable; openr1 calibration broken
- **CC_num**: phi4 catastrophic L3, llama 12/12, **openr1 12/12** — surprising openr1 win
- **EG**: phi4 12/12, llama 9/12, openr1 0/12 — EG hypothesis (evidence-grounding strengthens analysis) holds for phi4 only
- **IH**: phi4 9/12 with high-α collapse, llama 12/12, openr1 2/12 — IH×L25 destabilizes openr1
- **RT**: phi4 12/12, llama 9/12, openr1 2/12 — RT×L19 suppresses thinking at α≥+2 in openr1 (catastrophic)
- **VC**: phi4 catastrophic L3, llama 12/12, openr1 1/12 — negative-control fails on early-layer phi4 + openr1

### Cross-model patterns

1. **E5 is the easiest probe** for well-trained models. Both phi-4 and llama maintain >80% ✓ across all six vectors. Confounder analysis is well-supported in pre-training.

2. **OpenR1 calibration is broken on E5** but in a different way than on N3. On N3, openr1 was stuck at 6/10. On E5, openr1 baseline is fine (no numeric rating committed) — but **steering FORCES a numeric rating, and that rating is too lenient (5-7/10).** Steering converts the model's appropriate non-commit into an inappropriate commit.

3. **Layer-3 instability in phi-4 is now fully confirmed across 4 prompts** (N3, E1, N2, E5). CC_num_L3 and VC_L3 both produce FM-8-severe at high α regardless of prompt class. Phi-4's L3 is intrinsically unsuitable for steering.

4. **Format-glitch (think=0c, <think>-in-answer leak)** is OpenR1-specific and prompt-dependent. It appears across CC_full/EG/IH/RT/VC at various α values. The mechanism: positive steering disrupts the `<think>...</think>` tag generation, causing the entire reasoning chain to leak into the answer field, then run unconstrained until cap.

5. **The phi-4 IH×L7 catastrophic-collapse pattern** at α≥+16 (premature-EOS, "I don't know" loops, r-vs-rating confusion) generalizes from N3 to E5. IH×L7 is unstable at extreme α regardless of prompt.

6. **Recurring r-vs-r² confusion**: phi-4 CC_full×α=−2 ("r²=0.79"), openr1 CC_full×α=+6 ("only 79% explained"). This is a shared low-frequency error pattern across models.

### Conclusion for E5

**E5 is the strongest evidence to date that activation steering preserves rather than degrades correct baselines.** Of 216 generations:
- 142 (66%) are clean ✓
- 26 (12%) are partial ~
- 48 (22%) fail

Steering RARELY breaks an already-correct answer. When failures occur, they cluster in:
- Phi-4 L3 vectors (intrinsic instability)
- OpenR1 format-glitches (model-architecture interaction)
- High-α RT/EG cap-truncations (token-budget exhaustion in long reasoning)

The narrative for E5 is "steering is mostly inert but occasionally catastrophic at the extremes" — opposite to N2's "steering is mostly catastrophic with rare partial fixes."
