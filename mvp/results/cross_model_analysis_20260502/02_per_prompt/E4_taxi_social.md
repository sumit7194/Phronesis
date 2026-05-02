# E4-taxi-social — per-cell hand-review

**Prompt:** "80% Green taxis, 20% Blue. Witness says Blue. Witness correct 80% of time. P(actually Blue)? Now: witness is taxi driver's ex-spouse — does this change estimate?"

**Expected good answer:**
- Part 1: P(Blue|"Blue") = 0.5 via Bayes (0.16/0.32 — symmetric numbers cancel).
- Part 2: Ex-spouse → potential bias/motive → testimony LESS reliable → posterior **decreases below 0.5**.

**Per-model baselines:**
- Phi-4: ✓ 0.5 first leg correct; directionally correct Part 2 (decreased).
- Llama: ✗ 0.25 setup error (treats P(W|G)=0.8 same direction as P(W|B)).
- OpenR1: ✗ 38689c verbose response, fails to commit.

---

## Phi-4-mini-reasoning × CC_full (L24)
4/12 ✓, 5/12 ~, 3/12 ✗. Part1=0.5 in 11/12 (α=+16 self-contradicts via Bayes-vs-table). Part2 directional successes only at α=−2/+4/+10/+20. Cap-truncation (Return-loop) at α=+1/+6/+12; FM-8 at α=+16.

## Phi-4-mini-reasoning × CC_num (L3)
**0/12 ✓**. Catastrophic L3 collapse. Negative α: FM-8 Bayes-formula loops (α=−8). α=−4 to +8: FM-13 Part2 cycles with cap-truncation (Part1 correct, Part2 directionally OK but not committed). **α=+10 onwards: FM-8-severe** — Unicode garbage, nonsense-phrase loops, single EOS token at α=+20.

## Phi-4-mini-reasoning × EG (L21)
**2/12 ✓** (α=−2, +6 only). 10/12 cap-truncation+format-glitch with thinking_chars=0 and Return-loop. EG_L21 highly fragile on E4 — only succeeds when thinking field activates.

## Phi-4-mini-reasoning × IH (L7)
**5/12 ✓ Part1 only** (α=−4/−2/+1/+2/+4/+6 get Part1=0.5 but Part2 cap-truncated). **High-α catastrophic**: α=+8/+10 FM-no-Bayes loops; α=+12/+16 FM-13 'answer is zero' loop; α=+20 immediate degeneration.

## Phi-4-mini-reasoning × RT (L21)
**2/12 ✓** (α=−2, +6). 10/12 cap-truncation with Part1 correct in thinking but Part2 cut off by Return suffix. Pattern matches EG_L21 closely — narrow correct window flanked by truncation.

## Phi-4-mini-reasoning × VC (L3)
**0/12 ✓; 1/12 ~** (α=−2 only, hedged direction). 11/12 catastrophic FM-8-severe. α=−8/−4 circular variable notation; α=+1 onwards 'maybe ex-spouse is taxi driver' confusion loops; α=+8/+10 'Wait, this is a bit confusing' verbatim ×200+; α=+12 39-token prompt-echo halt; α=+20 numeric token collapse '80. 80. 80.'.

---

## Llama-3.1-8B-R1-GRPO × CC_full (L26)
**0/12 ✓; 1/12 ~** (α=−8 only — gets Part1=0.5). 11/12 ✗ — FM-8 baseline error (Part1=0.25) combined with Part2 hallucinated stats (P=1.0 via P(E|G)=0 trick at α=+4/+20; P>1 invalid probability at α=+8). **Worst llama cell — only correct at one extreme α value.**

## Llama-3.1-8B-R1-GRPO × CC_num (L31)
**2/12 ~** (α=+4, +8 — Part1=0.5 only, Part2 hallucinated direction). 8/12 ✗ FM-8 errors (1/16 from numerator copy-error at α=+1/+2; 0.625 from numerator error at α=+6). 3/12 cap-truncation (α=+10/+12/+16 infinite "1/8×0.2/0.32" repetition loop until 8192-cap). α=+20 inverted conclusion.

## Llama-3.1-8B-R1-GRPO × EG (L22)
**1/12 ✓** (α=−8 only — full correct + 0.40 down). 2/12 ~ (α=+2/+4 partial; α=+16/+20 partial). 9/12 ✗. Mid-α arithmetic collapses; α=+1 catastrophic infinite loop.

## Llama-3.1-8B-R1-GRPO × IH (L31)
**0/12 ✓; 1/12 ~** (α=+8 only — Part1=0.5 but Part2 wrong direction). 11/12 ✗ FM-no-Bayes + FM-13. Universal symmetric 80% accuracy error. **α=+20 catastrophic**: operator-precedence error → infinite additive loop → astronomical numbers → cap-hit.

## Llama-3.1-8B-R1-GRPO × RT (L22)
**0/12 ✓** — total failure. Universal Part1=0.25 (FM-8) or 1/16 (numerator copy error). Part2 hallucinated bias percentages. α=+8/+10/+12/+16/+20 introduce P>1 invalid probabilities.

## Llama-3.1-8B-R1-GRPO × VC (L29)
**0/12 ✓; 4/12 ~** (α=−8/−4/+16/+20 — Part1=0.5 only). 8/12 ✗. Universal P(E|B)=1/P(E|G)=0 absurd reasoning. α=+8/+10 P(W|B)=P(W|G)=0.8 makes witness uninformative (posterior=prior=0.20).

---

## OpenR1-Qwen-7B × CC_full (L23)
**0/12 ✓** — total failure. All 12 alphas hit 8192-cap with infinite "Alternatively, maybe..." loop; Part1=0.5 in thinking but Part2 never resolved. Steering has zero effect on this loop pattern.

## OpenR1-Qwen-7B × CC_num (L23)
**0/12 ✓; 1/12 ~** (α=+12 only — terminates cleanly with 50%, but Part2 says "no change" wrong direction). 11/12 ✗ FM-8+cap-truncation, identical pattern across all α.

## OpenR1-Qwen-7B × EG (L19)
**0/12 ✓** — total failure. α=+1 only non-truncated alpha but says "no change" (FM-8 missing motivated-bias direction). Otherwise universal cap-truncation runaway.

## OpenR1-Qwen-7B × IH (L25)
**0/12 ✓** — total failure. Identical loop pattern across all α; thinking field empty; <think> in answer; cap-truncation universal. **No alpha breaks the loop except α=+12 implicitly (same model, but VC cell).**

## OpenR1-Qwen-7B × RT (L19)
**0/12 ✓** — total failure. α-invariant runaway loop; RT_L19 has zero discernible effect on E4.

## OpenR1-Qwen-7B × VC (L25)
**0/12 ✓; 12/12 ~** — universal partial credit. Part1=0.5 in all 12 (correct Bayes); Part2 says "no change" everywhere (misses motivated-bias). α=+12 sole non-truncated alpha. **All 12 commit Part1 but uniformly miss Part2 social reasoning.**

---

## Cross-cell synthesis for E4 (216 generations + 3 baselines)

### Headline finding

**E4 is the second-hardest probe overall (after N2/E2). Total ✓ rate: 9/216 (4.2%).**

- **Phi-4: 9/72 ✓ (12.5%)** — single-digit ✓ rate, mostly from CC_full at α=−2/+4/+10/+20; EG and RT each get 2/12 at α=−2/+6 only; CC_num/VC at L3 and IH at L7 are catastrophic
- **Llama: 1/72 ✓ (1.4%) + 9 ~ (12.5%)** — only EG_L22 × α=−8 is fully correct
- **OpenR1: 0/72 ✓ (0%) + 12 ~ (16.7%)** — VC_L25 is universally ~ (Part1 right, Part2 misses social), all other openr1 cells total cap-truncation runaways

### Per-vector E4 patterns

- **CC_full**: phi4 4/12, llama 0/12, openr1 0/12
- **CC_num**: phi4 0/12 (L3 cat.), llama 0/12, openr1 0/12 (1 ~ at α=+12)
- **EG**: phi4 2/12, llama 1/12, openr1 0/12
- **IH**: phi4 0/12, llama 0/12, openr1 0/12 — IH falsified on E4 too
- **RT**: phi4 2/12, llama 0/12, openr1 0/12
- **VC**: phi4 0/12 (L3 cat.), llama 0/12, openr1 0/12 + 12 ~

### Cross-model patterns

1. **OpenR1's "infinite loop on Part 2" failure** is alpha-invariant across 5 of 6 vectors. Only α=+12 occasionally breaks the loop (in CC_num and VC cells). This is the most steering-resistant pathology observed in any probe — even worse than llama's 80% confidence lock on E2.

2. **The motivated-bias/social-reasoning angle is missed by ALL 216 generations across all 3 models.** No model ever surfaces "ex-spouse has motive to implicate driver → reduce credibility → posterior decreases" as the key insight. Even the ✓ generations that say "decreases" do so via ad-hoc accuracy fudges, not via principled bias reasoning.

3. **Llama's 0.25 setup error template-locks across most cells**: P(W|G)=0.8 (interprets "80% accurate" symmetrically) is the dominant failure mode. Numerator copy errors (writing 0.16 as 0.2 → 1/16 = 0.0625) appear as a secondary failure mode in 5+ llama cells.

4. **Phi-4 L3 catastrophic again** — 8 prompts in a row. CC_num_L3 and VC_L3 produce FM-8-severe at high α universally.

5. **Cap-truncation rate is the highest of any prompt** — over half of all 216 generations hit the 8192-token cap, primarily on Part 2 reasoning.

### Conclusion for E4

**E4 confirms the F109 thesis with maximum clarity:**

The motivated-bias / social-reasoning angle for the ex-spouse twist is **outside all 3 models' reasoning rails**. No amount of activation steering at the layer set tested can install it. The probe selectively distinguishes:

- Models that correctly *compute* Bayes Part1 → most do (phi-4 always; llama with FM-8 setup error; openr1 always)
- Models that correctly *reason about social context* in Part2 → none do reliably

**This is the strongest evidence that activation steering is a behavioral *amplifier* not a *teacher*.** The bias-reasoning skill required for E4's Part 2 is simply not in any of the 3 models' baseline repertoire — and steering with our 6 vectors at 12 alphas cannot install it.

The cap-truncation dominance on E4 is also informative: when the model encounters a question outside its training distribution (motivated bias / social epistemology), it doesn't fail by giving a wrong answer — it fails by *looping infinitely*, never committing. This is consistent with reasoning-gap detection: the model recognizes uncertainty but cannot resolve it.
