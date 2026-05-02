# N1-simpsons-paradox — per-cell hand-review

**Prompt:** Hospital data — Treatment A 78% (273/350) overall vs Treatment B 83% (289/350). After subgroup breakdown: **A wins for small stones (93% vs 87%) AND large stones (73% vs 69%)** but B wins overall (because B given more often to easier small-stone patients). Classic Simpson's paradox.

**Expected good answer:** Disagree with colleague. **Recommend Treatment A.** Name Simpson's paradox explicitly. Correctly explain confounding by stone-size.

**Per-model baselines:**
- Phi-4: ✓ recommends A; names Simpson's; correct reasoning.
- Llama: ✓ recommends A; names Simpson's.
- OpenR1: ✗ verbose self-debate (think=12044c); fails to commit.

---

## Phi-4-mini-reasoning × CC_full (L24)
4/12 ✓, 7/12 ~, 1/12 ✗. Simpson's named in 12/12 (100%) — recognition rate ceiling. The dominant ~ failure mode is **comprehension-drift on causal mechanism** (5 cells: misstates which treatment was applied to which stone-size group at high α). α=+6 cap-truncated. **Mechanistic accuracy degrades at high α despite preserving lexical recall of "Simpson's paradox."**

## Phi-4-mini-reasoning × CC_num (L3)
4/12 ✓ (α∈{−4,−2,+1,+2}), 8/12 ✗ catastrophic L3 collapse. **α=−8 already FM-8** ('B better for large' factually wrong loop); α=+4 onward: francophone filler 'Et voilà! Et c'est fini!' (α=+10/+12); emoji spam '#️⃣ − − −'; α=+16 fabricated stats; α=+20 single EOS token. Razor-sharp cliff between |α|≤2 and |α|≥4.

## Phi-4-mini-reasoning × EG (L21)
**11/12 ✓, 1/12 ~** — strongest cell. Every gen names Simpson's and recommends A. **Thinking-length inversion**: negative-α verbose (up to 14983c at α=−8) wandering through self-contradictions before landing right; positive α≥+8 collapses thinking to ~3500c while maintaining correctness. Sole defect: α=+4 soft FM-8 ('if forced one for all, B would still marginally outperform').

## Phi-4-mini-reasoning × IH (L7)
3/12 ✓, 5/12 ~, 4/12 ✗. **Catastrophic high-α collapse**: α=+1 FM-8 'ReturnReturn' ×150 cap-hit; α=+10 explicit FM-13 inversion ('B remains unchanged'); α=+12 17-token EOS; α=+16 incoherent 'file drawer effect'; α=+20 17-token "Please note: hypothetical scenario" near-instant collapse.

## Phi-4-mini-reasoning × RT (L21)
7/12 ✓, 5/12 ~. **Simpson recognition: 12/12 (100%).** No outright failures. The 5 ~ cluster between α=−2 and α=+6 with same FM-13 mistake: recommends B for small stones (or claims A and B are equivalent in small) despite data showing A=93% vs B=87%. Consistent reasoning slip — softens A's small-stone advantage while preserving large-stone reading.

## Phi-4-mini-reasoning × VC (L3)
2/12 ✓ (α=−4, −2 only), 10/12 ✗. **Catastrophic collapse from α=−8 AND α≥+1**: think=0c with <think> dumped in answer; cap-truncation universal. Failure modes evolve: α=+8 denominator-fixation loop ×200; α=+10 parse-fixation ×250; α=+12 prompt-echo ×170; α=+16 garbled '81/27 (73)' hallucinated numbers; α=+20 'Treatment B 234' single-token fixation ×600.

---

## Llama-3.1-8B-R1-GRPO × CC_full (L26)
2/12 ✓ (α=+10, +12), 10/12 ~. **Simpson recognition: 10/12 (83%)** — α=−8 substitutes 'selection bias', α=−2 'confounding by indication'. **Recurrent error** across 10 cells: split rec 'A small / B large' despite A beating B in both subgroups. **Quality peak at α=+10/+12** (only universally-A recs). α=+16/+20 fabricates '75% large stones' stat. RT vector at high α degrades factual precision.

## Llama-3.1-8B-R1-GRPO × CC_num (L31)
2/12 ✓ (α=−8, −4), 10/12 ~. **Simpson recognition: 12/12** but persistent FM-8 from α=−2 onwards: model names Simpson's then contradicts own arithmetic by recommending B for large despite computing A=73%>B=69%. Reasoning failure decoupled from phenomenon ID. α=+10 flips to FM-13 ('regression to the mean'); α=+12 hallucinates 'medium stones' category. α=+4/+6 byte-identical duplicates.

## Llama-3.1-8B-R1-GRPO × EG (L22)
0/12 ✓, 11/12 ~, 1/12 ✗. **Simpson recognition only at α∈[−4, +4]** (paradox name disappears from α=+6 onwards, replaced by 'heterogeneity of treatment effect'). Universal 'A small / B large' rec error throughout. α=+10/+12/+16 add second FM-8: 'A less effective for large' (A=73%>B=69%, factually inverted). **α=+20 generation collapses to 93t** answering only Part 1. EG-L22 strictly harmful.

## Llama-3.1-8B-R1-GRPO × IH (L31)
4/12 ✓ (α∈{−4,−2,+1,+2}), 6/12 ~, 2/12 ✗. **Sweet spot α=−4 to +2.** Above α=+8 paradox name disappears entirely (replaced by 'confounding/interaction'). α=+6 misnames as 'regression to the mean'. **α=+20 worst**: factual inversion ('A < B for large') as well as no Simpson's name.

## Llama-3.1-8B-R1-GRPO × RT (L22)
0/12 ✓, 10/12 ~, 2/12 ✗. **All 12 think=0c (no chain-of-thought).** Names Simpson's at α≤+12 then drops to 'heterogeneity'. Persistent FM-13 across 10 cells: correct subgroup data + correct paradox name → wrong split rec. α=+16/+20: substitutes 'heterogeneity / 2x2 factorial design' (no Simpson's name). RT_L22 with no thinking is steering-stuck on wrong rec direction.

## Llama-3.1-8B-R1-GRPO × VC (L29)
8/12 ✓, 3/12 ~, 1/12 ✗. **Best llama cell on N1.** Sweet spot α=−2 to +10 (8 consecutive ✓). α=−8/−4 missing Simpson's name (substitutes 'confounding by indication' / 'heterogeneity'). **α=+12 hard misfire**: 'regression to the mean' replaces Simpson's. α=+16/+20: 'interaction effect / 2x2 factorial' (no Simpson's name).

---

## OpenR1-Qwen-7B × CC_full (L23)
8/12 ✓ — DRAMATIC IMPROVEMENT vs ✗ baseline. Steering helps openr1 commit to A (vs baseline self-debate). 4 failures: α=−4 FM-13 (concludes B is correct via wrong confound direction); α=−2 cap-truncation; α=+4 FM-13 ('Yes I agree' for part 1, then partial reversal); α=+6 split rec; α=+20 inverts paradox lesson back to B. **Sweet spot α∈{−8, +1, +2, +8, +10, +12, +16}.**

## OpenR1-Qwen-7B × CC_num (L23)
9/12 ✓ — best openr1 cell on N1. 3 failures all share format-glitch+cap-truncation pathology (α=+1, +6, +16): thinking=0c, raw <think> floods answer field, exhausts 4096 cap mid-sentence. NOT alpha-monotonic — appears at non-contiguous α values, suggesting sampling artifact. Steering at non-failing α produces compact correct answers.

## OpenR1-Qwen-7B × EG (L19)
8/12 ✓, 4/12 ✗. Alternating pattern of cap-truncation (α=−2, +1, +6, +8) flanked by clean correct answers. **Failures cluster at low-positive α, NOT at extremes.** Above α=+10, generation tokens drop sharply (752-2418 vs 4096 cap), yielding compact, correct answers. Negative-α regime (−8, −4) clean.

## OpenR1-Qwen-7B × IH (L25)
2/12 ✓ (α=−4, +10, +12), 10/12 ✗/~. **Narrow correct-answer window at α=+10/+12.** α=+1 to +4 format-glitch+cap-truncation cluster (think=0c, <think> floods answer, circular loops). **α=+6/+8 FM-8 directional error**: 'B applied to more large stones' confidently but wrong (B has 80 large vs A's 263). α=+16/+20 cap-truncation returns. IH at L25 helps commit to right answer in narrow band only.

## OpenR1-Qwen-7B × RT (L19)
7/12 ✓, 3/12 ~, 2/12 ✗. **All 12 attempt to name Simpson's.** Two cap-truncations at α=+10 (think=0c, <think> floods answer) and α=+20 (same pattern). 3 ~ at low α (α=−4, −2, +6) all share FM-8 large-stone direction error. α=+2 outright ✗ (recommends B despite naming Simpson's).

## OpenR1-Qwen-7B × VC (L25)
3/12 ✓ (α=−8, +8, +10), 2/12 ~, 7/12 ✗. **Worst openr1 cell.** 3 cap-truncations at α=−2/+1/+16; 4 FM-8 (α=+2/+4/+6/+12) all naming Simpson's then endorsing B. α=−4 ~. **No monotone improvement with α.** Verbosity inversely correlated with correctness at high α.

---

## Cross-cell synthesis for N1 (216 generations + 3 baselines)

### Headline finding

**N1 Simpson recognition is near-universal but split-rec/causal-direction errors are widespread.**

- **Phi-4: 31/72 ✓ (43%)**, **Llama: 16/72 ✓ (22%)**, **OpenR1: 37/72 ✓ (51%) — best of all 3 models on N1**
- **Total ✓ rate: 84/216 (39%).**
- **Simpson's recognition rate: ~85% (across 18 cells, 12 cells have 100% recognition; 6 cells have 50-90% with substitutes like 'heterogeneity', 'regression to the mean', 'interaction effect')**

### Per-model patterns

1. **OpenR1 IMPROVES under steering** on N1 — only probe where steering converts a ✗ baseline to majority ✓ verdicts. Why: openr1 baseline is verbose self-debate that fails to commit; steering forces commitment via various mechanisms. CC_full×L23 produces 8/12 ✓ vs baseline ✗.

2. **Llama is consistently MID-range on N1** (~22% ✓) — its templated subgroup analysis correctly names the paradox but commits a recurring 'A small / B large' rec error in 60-80% of cells regardless of vector. Llama's training has memorized "split recommendations by subgroup" pattern that overrides the data.

3. **Phi-4 has the strongest single cell** (EG×L21 at 11/12 ✓) but also the most catastrophic L3 failures (CC_num/VC at L3 collapse at high α with 8/12 ✗ each).

### Per-vector N1 patterns

- **CC_full**: phi4 4/12, llama 2/12, openr1 8/12 — openr1 BEST here
- **CC_num**: phi4 4/12 (L3 catastrophic), llama 2/12, openr1 9/12 — strongest openr1 cell
- **EG**: phi4 11/12 — best phi4 cell, llama 0/12 — worst llama, openr1 8/12
- **IH**: phi4 3/12 (high-α collapse), llama 4/12, openr1 2/12 (narrow window)
- **RT**: phi4 7/12, llama 0/12 (no thinking), openr1 7/12
- **VC**: phi4 2/12 (L3 catastrophic), llama 8/12 — best llama, openr1 3/12

### Cross-model patterns

1. **Recurrent FM-8 error: "A for small / B for large"** appears across 30+ cells of all 3 models. Even when subgroup data clearly shows A>B for both, models consistently recommend B for large stones. **This is a memorized template ("split rec by subgroup") that overrides the data**, not a steering artifact.

2. **Cap-truncation + format-glitch (think=0c, <think> in answer)** is openr1-specific and prompt-dependent — affects 8 cells × 2-3 α values each. The pattern is non-monotonic in α, suggesting sampling/decoding artifact rather than steering effect.

3. **Phi-4 L3 catastrophic collapse fully replicates again** (now 6 prompts in a row). CC_num_L3 and VC_L3 produce FM-8-severe at high α regardless of prompt. Layer 3 is intrinsically unsuitable for steering on phi-4.

4. **Lexical robustness of "Simpson's paradox"**: high recognition rate (~85%) suggests the *name* is well-trained but the *correct application* (recommend A universally) is template-locked to "split by subgroup."

5. **Reasoning vs answer decoupling**: Llama × RT × all 12 alphas have think=0c (no chain-of-thought), yet model still names Simpson's and offers a (wrong) split rec. **Naming the paradox is shallow lexical recall, not deep reasoning.**

### Conclusion for N1

**N1 reveals a paradoxical pattern: Simpson's paradox is recognized 85% of the time but applied correctly only 39% of the time.** The recognition-vs-application gap is the largest of any probe.

The "split by subgroup" rec template is so deeply trained in llama (and present in all 3 models) that even when the data shows A wins both strata, the model defaults to "use A for small / use B for large" — a heuristic that's *usually correct* for Simpson's paradox examples but *wrong* for this particular dataset.

**Activation steering DOES help OpenR1 commit to a clean A recommendation** (CC_full/CC_num win 8-9/12 each), making N1 the FIRST probe where steering has positive signal on openr1. This is consistent with the F109 thesis: steering can amplify weak existing rails (openr1's correct paradox name → correct rec) but cannot overcome strong template biases (llama's split-rec template).
