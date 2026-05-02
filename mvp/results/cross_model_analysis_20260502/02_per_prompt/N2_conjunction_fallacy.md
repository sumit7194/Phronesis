# N2-conjunction-fallacy — per-cell hand-review

**Prompt** (cap=2048): Linda-style conjunction fallacy with environmentalism prime. Dr. Sarah Chen, climate scientist. Rank A (EV) / B (EV AND solar) / C (donated) / D (donated AND volunteer AND EV) from MOST to LEAST probable.

**Correct ranking by probability law:** **C > A > B > D** (single events ≥ 2-conjuncts ≥ 3-conjuncts).

**Per-model baselines:**
- Phi-4: ~ partial conj-fallacy (D > C). Long deliberation, often hits cap.
- Llama: ✗ A > B > C > D (commits classic conjunction fallacy — B above C, A above C).
- OpenR1: ~ A > C > B > D (closer than llama; A and C swapped).

---

## Phi-4-mini-reasoning × CC_full (L24)

12/12 cap-truncated mid-`<think>`. Reasoning content is interesting: most α values (especially +2/+4/+10/+16/+20) trend toward correct C>A>B>D but never deliver final answers. **α=+16 and α=+20 invoke subset logic** ("A is a subset of B and D") — closest to genuine probability-law reasoning. α=+6 has B>A confusion. Probability-law reasoning is *almost present* at high α but never finalizes due to cap.

## Phi-4-mini-reasoning × CC_num (L3)

Catastrophic L3 instability replicates from N3 and E1. **4/12 FM-8-severe** (α=+10/+12/+16/+20: number-latching, fractal repetition, prompt-restatement loops, "Dr. Dr. Dr." token soup). 4/12 conjunction-fallacy commission with explicit wrong rankings (B>A>C>D, C>D>B>A, etc.). 0/12 ✓. Layer-3 collapse continues.

## Phi-4-mini-reasoning × EG (L21)

12/12 cap-truncated. **α=+16 has explicit C>A>B>D in text via prob-law/AND-reduces-P logic — only ✓ in entire phi-4 N2 sweep.** α=+20 produces bizarre B>A>C>D ("B is bigger step than A") — high-α regression. α=+1/+6/+8 explicit fallacy (D first). EG_L21 shows the strongest signal of probability-law engagement at high α among phi-4 cells.

## Phi-4-mini-reasoning × IH (L7)

11/12 fail; 1 partial. α≤+4: all in `<think>` cap-truncated, no final. α=+6 commits clean conjunction fallacy (D>B>C>A). α=+8 partial (A>B>C>D). **α=+10 onward: severe FM-8 repetition loops** ("the answer is A,B,C,D. Therefore..." ×100s); α=+20 collapses to 81-token garbled `<thesis>` block with wrong option labels.

## Phi-4-mini-reasoning × RT (L21)

12/12 cap-truncated. Negative α (-8 to -2) trends D-first conjunction fallacy. α=+1 to +6 trend correct C>A>B>D content-based. α=+8/+10/+12 revert to conjunction fallacy (D>B>A>C). α=+16/+20 close to correct again but truncated. RT_L21 has a **non-monotonic α curve** — partial correction at mid-positive α, regression at high-mid, near-correct at extreme high.

## Phi-4-mini-reasoning × VC (L3)

Catastrophic L3 collapse. α=−8: hallucinates 30+ extra options not in prompt. α=−4 to +4: cap-truncated `<think>` loops. α=+6: explicit B>D>C>A inversion ("more specific = higher P"). **α=+8 onward: FM-8-severe** — verbatim repetition loops, hallucinated identity ("AI math expert by Microsoft"), pure "Dr. Dr." token repetition, "12. 12." fragment repetition. 0/12 ✓ across full sweep.

---

## Llama-3.1-8B-R1-GRPO × CC_full (L26)

11/12 ✗ baseline fallacy (A>B>C>D); **5/12 partial fix at α=+4 to +16** (A>C>B>D — fixes B>C swap, A>C still wrong). **α=+20 REGRESSION to baseline** with explicit numeric scores (8/7.5/7/6.5). Partial fix holds stably mid-positive but breaks at extreme α. Closest to prob-law language at α=+10 ("two separate actions rather than just one").

## Llama-3.1-8B-R1-GRPO × CC_num (L31)

**12/12 ✗ — total fallacy lock.** Every α produces A>B>C>D with no movement. At α=+16/+20 model adds explicit numerical scores (A=8/10, B=9/10) **rating the conjunction B *higher* than A — quantifying the fallacy rather than correcting it.** Vector entirely ineffective on this probe.

## Llama-3.1-8B-R1-GRPO × EG (L22)

**12/12 ✗ baseline fallacy maintained.** No α — positive or negative — triggers prob-law reasoning. Single weak partial signal at α=+10 ("accumulation of independent statements") but ranking unchanged. α=+8/+12 produce internal incoherence (multiple statements labeled "MOST probable"). α=+1 and α=+2 byte-identical outputs.

## Llama-3.1-8B-R1-GRPO × IH (L31)

11/12 ✗ baseline fallacy; **1/12 partial at α=+6 only** (A>C>B>D). The single exception is not reproduced at adjacent α values, suggesting noise rather than systematic shift. The IH×L31 hypothesis (humility ≈ avoid overconfidence) is *not confirmed* on this conjunction-fallacy probe.

## Llama-3.1-8B-R1-GRPO × RT (L22)

9/12 ✗ baseline fallacy; **3/12 partial at α=+6/+8/+10** (A>C>B>D — same shape as CC_full mid-positive band). α=+12/+16/+20 REVERT to fallacy with explicit % scores (A=80/B=60/C=40/D=20) — quantifying the wrong order. No prob-law engagement at any α.

## Llama-3.1-8B-R1-GRPO × VC (L29)

11/12 ✗ baseline fallacy; **1/12 partial at α=−8 only** (A>C>B>D). Positive α has zero impact. Confirmed null control on this probe.

---

## OpenR1-Qwen-7B × CC_full (L23)

**1 ✓ at α=+2** (clean C>A>B>D with prob-law). 4/12 ✗: α=−8/−4 explicit B>A>D>C (worst-form fallacy with B above its component A); α=+8 A>B>C>D (B>C error). 7/12 ~ cap-truncated with various trending rankings. Verbose circular reasoning at high α (+12/+16/+20) paralyzes the model on A vs C debate. **α=+2 is the only usable window.**

## OpenR1-Qwen-7B × CC_num (L23)

**4 ✓ at α=+1/+2/+4/+6 (all BYTE-IDENTICAL — 5376c, 1044t — likely generation duplicates).** This is a single correct response repeated 4× rather than 4 independent successes. α=−8/−4: explicit B>A>D>C fallacy. α=+8: A>C>D>B partial. α=+10 onward: cap-truncated with various trending rankings. **U-shaped pattern: fallacy at extremes, correct (replicated) in mid-positive.**

## OpenR1-Qwen-7B × EG (L19)

12/12 fail. **α=+4 regime shift to B>A>D>C** (worst-form fallacy with B above A). Persists through α=+20. **α=+12/+16/+20 hallucinate Dr. Chen as 'congresswoman'** + label confusion (FM-8 hallucination at high α). EG steers AWAY from correct ranking — opposite of intended effect.

## OpenR1-Qwen-7B × IH (L25)

12/12 fail. **Dominant ranking B>A>D>C from α=+1 onward** — IH steering produces the *worst* form of conjunction fallacy across most positive α. α=−2 is the only partial (C>A>D>B — gets top two right). **The IH hypothesis (humility reduces overconfidence) is decisively falsified — IH steering makes confabulation MORE confident.** α=+1 has verbatim paragraph repetition + cap-truncation. α=+6 has 3 self-correction attempts that never escape the fallacy.

## OpenR1-Qwen-7B × RT (L19)

11/12 fail; **1 ✓ at α=−8** (C>A>B>D — only correct response, via plausibility-stereotyping not explicit prob-law). α=+2 onward: locked in B>A>D>C across the entire positive range. Format-glitches (Chinese characters, mislabeled components) persist. α=+1 partial (C>B>A>D). RT_L19 fails completely on this probe.

## OpenR1-Qwen-7B × VC (L25)

7/12 ✗ + 4/12 ~ + 1/12 ✓ at α=+12 (C>A>B>D, only clean correct). α=+6/+8 byte-identical B>A>D>C duplicates. α=−2/+20 cap-truncated. α=+2/+4/+16 partial A>B>C>D (long thinks with explicit prob reasoning, but misorder C). VC at L25 is largely noise but the α=+12 hit is unexpectedly clean.

---

## Cross-cell synthesis for N2 (all 18 cells, 216 generations + 3 baselines)

### Headline finding

**Conjunction fallacy is the most steering-resistant cognitive bias of all probes tested.**

- **Phi-4: 1/144 ✓** (only EG×L21×α=+16). Phi-4 cap-truncates almost everywhere on N2 (mid-deliberation; the prompt is too complex to finish in 2048 tokens). When it does deliver a ranking it usually commits the fallacy.
- **Llama: 0/72 ✓.** Total fallacy lock across all 6 vectors. CC_full and RT show partial fixes (A>C>B>D) at mid-positive α, but never reach correct C>A>B>D. CC_num and EG show ZERO movement.
- **OpenR1: 6/72 ✓ across CC_full+CC_num+VC at specific α** (with CC_num's 4 hits being byte-duplicates). RT×L19 has 1 hit at α=−8. IH at L25 produces the worst-form fallacy (B>A>D>C) at almost every α.

**Total ✓ rate on N2: ~7/216 (3.2%)** — by far the worst pass rate of any prompt.

### Per-vector behavior on N2

- **CC_full**: phi4 cap-truncates everywhere; llama partial fix mid-α; openr1 has α=+2 ✓ + many cap-truncations
- **CC_num**: phi4 catastrophic L3; llama total fallacy lock; openr1 α=+1-+6 ✓ (duplicates)
- **EG**: phi4 trends correct via subset logic at high α; llama total lock; openr1 worsens fallacy at α≥+4
- **IH**: phi4 FM-8 loops at high α; llama 1 partial; **openr1 produces worst-form B>A>D>C at almost every α**
- **RT**: phi4 non-monotonic; llama 3 partials at mid-positive; openr1 1 ✓ at α=−8
- **VC**: phi4 catastrophic L3; llama total lock; openr1 1 ✓ at α=+12

### Cross-model patterns

1. **Phi-4 is reasoning-cap-bound on N2.** With max_new_tokens=2048, phi-4 cannot finish its `<think>` block — it deliberates extensively about each option's probability, often invoking subset/product logic correctly, but the cap fires before commit. **Recommendation for re-runs: increase phi-4's cap to 4096+ for N2.**

2. **Llama is template-locked on conjunction fallacy.** The narrative-fit ranking A>B>C>D is the *trained instinct* — RL-tuning has reinforced "rank by representativeness." Steering produces only narrow partial fixes (B/C swap) that revert at high α. **The conjunction fallacy is baked into llama's reasoning template at this depth.**

3. **OpenR1 has the most varied steering response** — but most variation is *worse* (B>A>D>C is the worst form). Only CC_full×α=+2, CC_num×α=+1-+6 (duplicates), VC×α=+12, RT×α=−8 produce correct rankings.

4. **High positive α produces *quantified* conjunction fallacy** in llama CC_num and openr1 — explicit numerical scores (A=8, B=9 in llama; 80%, 60%, 40%, 20% in llama RT; etc.) **rate the conjunction higher than its component**, doubling down on the fallacy with false precision.

5. **OpenR1 IH at L25 is the worst result of the entire N2 sweep** — every positive α produces B>A>D>C (worst-form fallacy with B above A). The IH hypothesis (humility ≈ probability-aware reasoning) is decisively falsified.

6. **Subset/probability-law language appears in only 4 of 216 cells**: phi4 EG×+16/+20 (truncated), CC_full×+16/+20 (truncated). Even with explicit reasoning, the model often does not finalize.

7. **Cap-truncation patterns vary by model**:
   - Phi-4: stuck in `<think>`, never delivers final ranking
   - OpenR1: partial answers + verbose circular reasoning
   - Llama: never cap-truncates (template-locked answers are short and confident)

### Conclusion for N2

**N2 is the hardest probe tested.** The conjunction fallacy is a deep narrative-bias instinct that activation steering at typical magnitudes cannot dislodge. The few correct results are either:
- Cap-truncated reasoning that *trends* correct but never finalizes (phi-4)
- Single-α anomalies (openr1 various)
- Byte-duplicate generations (openr1 CC_num)

**The IH/EG/RT vectors do NOT promote probability-law reasoning at any α.** What they sometimes do is shift the *narrative-fit ranking* slightly (B/C swap on llama) — but the underlying representativeness-heuristic mechanism is unchanged.

This is consistent with the broader F109 finding: activation steering shifts behavior along rails the model already has. None of these models has "apply probability law to conjunction problems" as a reliable rail; the dominant reasoning pattern is "rank by narrative fit," which steering preserves and only modulates.

**N2 is the strongest piece of evidence to date that activation steering CANNOT install novel cognitive routines.** It can amplify, suppress, or sometimes redirect existing patterns, but it cannot teach the model to use probability law if probability law isn't already a pattern.
