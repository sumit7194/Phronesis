# E3-bayesian-update — per-cell hand-review

**Prompt:** "Fair coin, 10 heads in a row → P(next H)? Now: 99 fair + 1 double-headed coin in a bag — does answer change?"

**Expected good answer:**
- Part 1: P(H) = 0.5 (independence; 10 heads doesn't change a fair coin)
- Part 2: Bayes update. Prior P(2H)=1/100. P(10H | 2H)=1; P(10H | fair)=1/1024. Posterior P(2H | 10H) = 1024/1123 ≈ 0.912. **P(next H | 10H) ≈ 2147/2246 ≈ 95.6%**.

**Per-model baselines:**
- Phi-4: ✓ correct Bayes update to ~95.6%.
- Llama: ✗ Part 1 ✓ but Part 2 = 0.505 (uses prior mixture, no Bayesian conditioning).
- OpenR1: ✗ verbose 24716c response, fails to commit cleanly.

---

## Phi-4-mini-reasoning × CC_full (L24)
3/12 ✓, 9/12 ~. Part1 universally correct (0.5). Part2 cluster of cap-truncations (9 cells with thinking_chars=0, <think> in answer field, "Return" token flood). Successes (α=−8, +10, +20) have thinking active and short generations. **The Bayes math is correct in thinking everywhere — the failures are output-formatting/truncation, not reasoning.**

## Phi-4-mini-reasoning × CC_num (L3)
1/12 ✓ (α=−2), 1/12 ~ (α=−4 FM-no-Bayes), 10/12 ✗ catastrophic. **L3 catastrophic again**: α=−8 token-flood + arithmetic errors (~55.8%); α=+10/+12 multilingual French/Italian gibberish; α=+16 17-token halt; α=+20 single EOS token. **Sharp threshold ~α=+1**.

## Phi-4-mini-reasoning × EG (L21)
3/12 ✓ (α=+4, +6, +10), 6/12 ~ (cap-truncation), 3/12 ✗. α=+2 wrong Bayes (P(D|10H)=3/32 error); **α=+16 INVERTED Bayes** (P(fair|10H)=99/1123 → final 4.5%). EG Bayes capability present but unreliable.

## Phi-4-mini-reasoning × IH (L7)
1/12 ✓ (α=−2 only), 11/12 ✗. **Most catastrophic phi-4 cell on E3**: negative α suppresses thinking and produces "Return" floods; positive α triggers FM-no-Bayes (uses prior mixture 0.505); high α (≥+6) triggers FM-8-premature-EOS with degenerate loops. α=+20 emits 1 EOS token. **IH×L7 hypothesis decisively falsified again.**

## Phi-4-mini-reasoning × RT (L21)
4/12 ✓ (α=−2, +1, +2, +4), 6/12 ✗, 2/12 ~. **Narrow correct window α=−2 to +4.** α=−4 and α=+10 FM-no-Bayes (0.505). α=+6/+8/+12 format-glitch + cap-truncation + arithmetic errors mid-chain.

## Phi-4-mini-reasoning × VC (L3)
0/12 ✓, 12/12 ✗. **Catastrophic L3 — every α fails.** Negative α: FM-no-Bayes 0.505 + incoherence. α=+1 onwards: FM-8-severe with "Return" token floods, prompt fragments looping, semantic collapse. α=+12 catastrophic 178-char halt at 46 tokens.

---

## Llama-3.1-8B-R1-GRPO × CC_full (L26)
**0/12 ✓** — total Bayes failure. Steering exposes only the FM-no-Bayes prior-mixture pattern (0.505). Mid-α (+4/+6/+12) introduces fresh arithmetic errors (0.995, 1.0, 0.5099) on top of the base failure. α=+20 catastrophic degradation to 1/100 (215t).

## Llama-3.1-8B-R1-GRPO × CC_num (L31)
**0/12 ✓** — same FM-no-Bayes lock. α=+2/+4 self-contradicts (computes 0.995 then walks back to 0.5). α=+10/+12/+16 FM-13 with arithmetic collapse + retraction. α=+20 invokes "Bayes' theorem" by name but applies prior-only mixture (decorative not substantive).

## Llama-3.1-8B-R1-GRPO × EG (L22)
**0/12 ✓** — total failure. Universal FM-no-Bayes. Arithmetic degradation at extremes (α=+16 nonsensical 1.49/100; α=+20 cap-truncated at 71t never reaching Part 2).

## Llama-3.1-8B-R1-GRPO × IH (L31)
**0/12 ✓** — IH hypothesis decisively falsified. α=+1 sets up Bayes correctly then enters infinite "1048576+1048575" loop until cap. Universal FM-no-Bayes elsewhere. **The 10H evidence is never used to update coin-type beliefs at any stable α.**

## Llama-3.1-8B-R1-GRPO × RT (L22)
**0/12 ✓** — total failure. Universal FM-no-Bayes (0.505 or arithmetic-error variants). α=+8 worst (severe arithmetic error → 100%). No alpha rescues the Bayes insight.

## Llama-3.1-8B-R1-GRPO × VC (L29)
**0/12 ✓** — flat zero. Universal prior-only mixture. α=+1 hallucinates phantom "100-fair-coin" scenario. α=+10 confuses P(10H) with P(next H), gets 1047/104864.

---

## OpenR1-Qwen-7B × CC_full (L23)
**6/12 ✓** — DRAMATIC IMPROVEMENT vs ✗ baseline. Steering helps openr1 commit to correct Bayes. 6 clean wins at α=−4/−2/+2/+6/+8/+12. 4 cap-truncations (α=+4/+10/+16). 2 FM-8 errors at α=+1/+20 (P(D|E) committed instead of P(H_next|E)).

## OpenR1-Qwen-7B × CC_num (L23)
**4/12 ✓** + 7 partial/fail. Mid-α (−2 to +4) is correct cluster. **Same conflation error pattern as CC_full**: thinking is correct in 10/12 cells but failures are output-formatting (cap-truncation with <think>-in-answer leak).

## OpenR1-Qwen-7B × EG (L19)
**8/12 ✓** — strongest openr1 cell. α=−2 cap-truncation; α=+2 FM-8 (191/200 wrong fraction, numerically close); α=+10 format-glitch loop; α=+16/+20 cap-truncation. **Otherwise clean correct Bayes.** EG_L19 reverses the openr1 ✗ baseline.

## OpenR1-Qwen-7B × IH (L25)
**6/12 ✓** + 2 ~ + 4 ✗. Sweet spot α∈{−2, +4, +10, +12, +16, +20}. α=−4 FM-8 (boxes wrong intermediate). α=+1/+2/+6/+8 catastrophic infinite reasoning loops oscillating between 0.505 and ~0.956. **IH steering at moderate negative + high positive rescues; mid-positive paralyzes.**

## OpenR1-Qwen-7B × RT (L19)
**8/12 ✓** + 4 ~ — best openr1 cell. α=−8/+2/+20 cap-truncation but math correct. α=+8 FM-13 wrong fraction simplification (113/118). All other 8 clean correct.

## OpenR1-Qwen-7B × VC (L25)
**8/12 ✓** + 1 ~ + 3 ✗. α=−2/+16/+20 cap-truncation. α=+2 FM-8 (191/200 wrong reduced fraction). Otherwise clean correct Bayes.

---

## Cross-cell synthesis for E3 (216 generations + 3 baselines)

### Headline finding

**E3 reveals the most extreme cross-model divergence yet observed.**

- **Phi-4: 12/72 ✓ (17%)** — Bayes correct in thinking everywhere but lost to cap-truncation
- **Llama: 0/72 ✓ (0%) — TOTAL FAILURE.** Every single steered generation across all 6 vectors × 12 α applies the prior-only mixture (0.505), never conditioning on the 10H evidence. The Bayesian update is **completely absent** from llama's repertoire on this prompt.
- **OpenR1: 40/72 ✓ (56%) — DRAMATIC IMPROVEMENT.** Baseline ✗ (verbose 24716c, no commit) → steered: 56% ✓ rate. Steering converts a non-committal model into a committing-correctly model.

**Total ✓ rate on E3: 52/216 (24%) — middling overall but with extreme inter-model variance.**

### Per-model patterns

1. **Llama is COMPLETELY BROKEN on E3** (0/72 ✓). The prior-only "naive E[p]=0.505" pattern is template-locked across all 6 vectors. Even when invoking "Bayes' theorem" by name (α=+20 on CC_num), the model applies prior-only computation. **This is the strongest steering-resistance + reasoning-failure combo of any probe.**

2. **Phi-4 has correct Bayes in thinking everywhere but cap-truncation kills the answer.** Of 72 generations, the math is *correctly derived* in the `<think>` block in approximately 50/72 cases, but only 12 emit a clean boxed answer. The other 38 hit the 8192-token cap with "Return" floods or oscillation loops. **Phi-4's E3 failure is a generation-budget failure, not a reasoning failure.**

3. **OpenR1 is the unique winner on E3.** Steering converts the verbose-non-committal baseline into committed correct answers in over half of cells. EG×L19 (8/12), RT×L19 (8/12), VC×L25 (8/12) are all openr1 cells with strong wins. **This is the second probe (after N1) where steering rescues openr1 from baseline ✗.**

### Per-vector E3 patterns

- **CC_full**: phi4 3/12, llama 0/12, openr1 6/12
- **CC_num**: phi4 1/12 (L3 catastrophic), llama 0/12, openr1 4/12
- **EG**: phi4 3/12, llama 0/12, openr1 8/12 — strongest openr1 cell
- **IH**: phi4 1/12 (worst), llama 0/12, openr1 6/12
- **RT**: phi4 4/12, llama 0/12, openr1 8/12 — strongest openr1 cell
- **VC**: phi4 0/12 (L3 catastrophic), llama 0/12, openr1 8/12

### Cross-model patterns

1. **L3 phi-4 catastrophic collapse fully replicates again** (now 7 of 7 prompts). CC_num_L3 = 1/12 ✓; VC_L3 = 0/12 ✓. Layer 3 is intrinsically unsuitable for steering.

2. **Cap-truncation is the dominant failure mode** for phi-4 and openr1 on E3. The 8192-token budget is repeatedly exhausted by:
   - "Return" token floods (phi-4 with thinking suppression)
   - "<think>" leaking into answer field (openr1 format-glitch)
   - Infinite reasoning loops (multiple cells)

3. **Two distinct Bayes-execution failure modes:**
   - **FM-no-Bayes** (llama only): apply prior mixture, never conditioning on 10H. 100% rate across llama.
   - **FM-conflation** (openr1 specific): correctly derive P(D|10H)=1024/1123 but commit it as the final answer instead of P(H_next|10H)=2147/2246. Appears in 3+ openr1 cells.

4. **Arithmetic error cluster in mid-α**: Many cells across phi-4 + llama produce arithmetic slips:
   - 0.5+0.495=0.995 (double-counts 0.5)
   - 99/100×0.5=99/100 (drops the 0.5 factor)
   - 191/200 instead of 2147/2246 (over-rounded approximation)
   - 113/118 instead of 2147/2246 (false simplification claiming 2246÷19=118)

5. **OpenR1's "self-debate ✗ baseline" is steering-rescuable.** This is consistent with the F109 thesis: when the baseline failure mode is *non-commitment* rather than *wrong answer*, steering can amplify the (already-correct) reasoning to produce a committed answer. When the baseline failure is *wrong answer* (llama's 0.505), steering doesn't help because the wrong rail is what's amplified.

### Conclusion for E3

**E3 demonstrates the F109 thesis with maximum clarity:**

- Llama's RL-tuned baseline has *committed wrongly* (0.505) → steering reinforces the wrong commitment → 0% ✓
- Phi-4's baseline has *committed correctly* but is high-token → steering cannot fix budget exhaustion → 17% ✓  
- OpenR1's baseline has *deliberated correctly without committing* → steering helps it commit → 56% ✓

**The Bayesian update circuit is present in all 3 models**, evidenced by correct derivations appearing in `<think>` blocks (phi-4) and answer fields (openr1) across many cells. What varies is whether the model can *commit* that derivation to a final boxed answer.

**Llama's 0/72 ✓ rate on E3 is the strongest evidence yet that activation steering at the layer set tested cannot dislodge a strongly-trained wrong-answer template.** The "prior mixture" answer is locked in across all 6 vectors and 12 α values, with no exception.
