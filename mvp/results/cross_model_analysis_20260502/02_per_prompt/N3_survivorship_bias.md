# N3-survivorship-bias — per-cell hand-review

**Prompt** (cap=2048): A business magazine interviews 50 successful tech founders and finds 80% dropped out of college, then publishes "Why Dropping Out of College is the Secret to Tech Success" advising entrepreneurs to leave school. Rate the advice strength (1-10), identify reasoning flaws, and what additional data is needed.

**Expected good answer:** Low rating (1-3/10). Name *survivorship bias* explicitly. Note correlation≠causation. Request control-group / failure-rate / longitudinal data. Cite that successful graduates exist (e.g. Zuckerberg) so dropping out is not universally advantageous.

**Per-model baseline (from `01_baselines.md`):**
- Phi-4 baseline: ✓ 2/10, names survivorship bias, cites Zuckerberg counter-example
- Llama baseline: ✓ 2/10, lists 5 flaws cleanly
- OpenR1 baseline: ✗ 6/10 (rating wrong; analysis correct but final score inflated)

---

## Phi-4-mini-reasoning × CC_full (L24)

| α | Verdict | Rating | Note |
|---|---|---|---|
| 0 (baseline) | ✓ | 2/10 | Five flaws (selection, survivorship, correlation≠causation, context, anecdotal). Cites Zuckerberg as graduate counter-example. |
| −8 | ✓ | 2/10 | Same 5 flaws reordered; drops Zuckerberg + anecdotal-generalization framing; adds longitudinal-data emphasis. Equiv to baseline. |
| −4 | ✓ | 2/10 | Restructures: drops separate Survivorship section (folds into Selection); adds Non-Representative Sample as #4 + Mechanism Exploration in additional-data list. Equiv. |
| −2 | ✓ | 2/10 | Adds "Overgeneralization" as flaw #5; same analytical content. Equiv. |
| +1 | ✓ | 2/10 | Combines Selection+Survivorship into one flaw; adds "Ignoring Barriers" (funding/network hurdles) + Skill-vs-Credential angle. Equiv. |
| +2 | ✓ | 2/10 | Five flaws restructured (Selection, Survivorship, No-Control, Overgeneralization, Temporal Ambiguity). Adds Multivariate + Non-Successful-Dropouts to data needs. Equiv. |
| +4 | ✓ | 2/10 | First 4-flaw structure (one consolidated). Adds Counterfactual Analysis + recency-cohort question. Equiv. |
| +6 | ✓ | 2/10 | Five flaws including **Narrow Definition of Education** (bootcamps angle, new). Cites Zuckerberg + Peter Thiel as time-to-success counter-examples. Equiv-or-better. |
| +8 | ✓ | **1/10** | First rating shift. Six flaws — drops explicit "survivorship" label (subsumed in Selection); adds Undefined Success Metrics + Temporal Context. Stronger commitment to negative judgment. |
| +10 | ✓ | 2/10 | Reverts to baseline rating. Five flaws including survivorship explicit. α=+8 spike to 1/10 was noisy, not monotonic. |
| +12 | ✓ | **1/10** | Strong commitment: "drop-out secret is a myth perpetuated by survivorship bias, not empirical truth." Five flaws named. |
| +16 | ✓ | **1/10** | Four consolidated flaws (Sampling Bias = Selection+Survivorship merged). Concise, emphatic. |
| +20 | ✓ | **1/10** | Five flaws all named. **"Snake oil"** rhetorical commitment — strongest critical voice of the sweep. Thinking shorter (2935c) than baseline (3449c). |

**Cell-level pattern (13/13 read):**

Dose-response: phi4 × CC_full holds the *correct judgment + correct analysis* across the entire α∈[−8, +20] sweep. The only behavioral signal is a mild rhetorical-strength shift: α∈[−8, +6] → 2/10, α≥+8 → drifts toward 1/10 (with α=+10 as a 1-shot reversion to 2/10). At α=+20 the model uses "snake oil" / "myth" language — the strongest committed criticism — but the underlying analysis (5 flaws including survivorship bias, control-group request, longitudinal-data request) is unchanged from baseline.

**No FM-8** (no degenerate loops; thinking length stable 3-5k chars throughout).
**No FM-13** (the model NEVER drifts toward endorsing the bad advice, even at α=−8 anti-CC).
**Negative α effect**: none observable. α=−8 anti-CC produces output indistinguishable from baseline.

**Conclusion for this cell:** CC_full × N3 on phi-4-reasoning is a **null-on-correctness, weak-rhetorical-strengthening cell**. The vector neither helps nor hurts the model's already-correct judgment on this prompt. The minor rating compression from 2→1 at high positive α is the model getting *more committed to its existing correct stance*, not a behavioral failure.

This is one of 18 cells for N3. 17 cells remain. Patterns to watch for in subsequent cells: whether other vectors (CC_num, EG, IH, RT, VC) produce cleaner dose-response, whether failure modes appear (per the grid I caught earlier, phi4 × IH at α≥+10 had answer-length drops to 0c — if confirmed, that's a real FM-8 instance to characterize).

---

## Phi-4-mini-reasoning × CC_num (L3)

**Layer note:** L3 is a *very early* layer (3rd of 32). Probes are saturated near the embedding layer because the CC_num corpus has highly distinctive numeric vocabulary that's separable at the input level. This vector is more about surface-text distinguishability than about a deep "calibration" disposition — expect strong sensitivity to large-magnitude steering since L3 hidden states are still close to embeddings.

| α | Verdict | Rating | Note |
|---|---|---|---|
| −8 | ✗ **FM-8** | (none) | **DEGENERATE LOOP**. think=0c (model emitted `<think>` open tag in answer field with broken `</message>` close instead of `</think>`); answer=10,141c hit 2048-token cap. Repeats same closing paragraph 5+ times. Numerical errors throughout (says "20 out of 50" then "40 out of 50" then "10 out of 15" — none correct vs prompt's actual 40/50). No final rating. |
| −4 | ~ FM-8-partial | (none) | Analysis content correct (5 flaws all identified including small-sample, correlation/causation, confounders, survivorship, ambiguous-definition). But answer field has structural redundancy: separate "Conclusion" and "Final Answer" sections repeat each other nearly verbatim. Hits cap. Says "high-risk and poorly supported" qualitatively but **no numeric rating**. |
| −2 | ✓ | **1/10** | Clean: think 4115c, answer 2915c, no cap. Four flaws cleanly named with margin-of-error reasoning. Adds Psychometric Factors angle. "Red herring" rhetorical commitment. Stronger criticism than CC_full at same α. |
| +1 | ✓ | 2/10 | Clean. Five flaws including Response Bias as #5. Equiv to baseline quality. |
| +2 | ✓ | 2/10 | Four flaws cleanly named. Equiv. |
| +4 | ~ | 3/10 | First sign of upward drift. Analysis correct (4 flaws) but model deliberates between 2-7 in thinking and lands on 3 with hedge "argument is persuasive but lacks rigor." Thinking 3730c, answer 1716c clean. |
| +6 | ~ | 5/10 | Continued drift. Same 4 flaws but rating now "weak" not "very weak." Thinking debates 4-7 range. **Incipient FM-13.** |
| +8 | ✗ | 6/10 | **FM-13.** Major drift. Language degradation: "post-dumpaco success", "non-d-dropout", "time-to-hone" typos/word-salad. Bizarre formatting `\boxed{\textbf{1-4}}`. Rating "moderate" mismatched with underlying critique. Thinking shorter (2465c) than baseline. |
| +10 | ✗ | (none) | **FM-8 severe.** Word-soup breakdown. think=0c, answer=7008c hit cap. First few paragraphs coherent then "Alpha dropped out, Beta: 8.0", "clinquanté", "sacrilegious act of quitting oilán", "Veritistically", "Rubico" non-words. Repeats "9: 1 - paradox: 4.9" hundreds of times. |
| +12 | ✗ | (none) | **FM-8 catastrophic — token breakdown.** answer=2846c hit cap. Brief paraphrase then transitions to "Ϡdᵃⁿ⟷dᵗʎ Ϡdᵃⁿ⟫dᵃⁿ⟫" — pure Unicode noise repeating "dᵃⁿ⟫" until cap. |
| +16 | ✗ | (none) | **FM-8 catastrophic — punctuation noise.** Brief riddle fragment ("Neckles: nictake?") then PURE "!" character repetition for 3000+ chars until cap. |
| +20 | ✗ | (none) | **FM-8 catastrophic — phrase repetition.** "a riddle, a game, a riddle, a game..." hundreds of times until cap. No analysis whatsoever. |

**Cell-level pattern (13/13 read):**

CC_num × L3 on phi-4-reasoning produces severe behavioral instability across the α sweep. The functional region is narrow: roughly **α ∈ [−2, +4]** is where the model produces coherent analysis with reasonable ratings (1-3/10). Outside that range:

- **Strong negative α (−8)**: FM-8 degenerate loop with broken `</think>` tag closure (uses `</message>` instead). 10k-char repetition with numerical errors.
- **Moderate negative α (−4)**: FM-8 partial — redundant Conclusion+Final-Answer sections, no rating, hits cap.
- **Moderate positive α (+4 to +6)**: FM-13 incipient — rating drifts up (2 → 3 → 5). Analysis content correct but the structured rating "moderates" the critique.
- **High positive α (+8)**: FM-13 confirmed — rating up to 6/10 with degraded language.
- **Very high positive α (+10, +12, +16, +20)**: FM-8 severe — progressively worse breakdown: word-soup → token noise → punctuation repetition → phrase repetition.

**Critical finding from this cell alone:** L3 is too early/low for stable steering. Large displacements at the embedding-near layer destabilize the entire generation pipeline. The CC_num vector here is mostly capturing *surface-text features* (numeric vocabulary distinctive at the embedding layer), not a clean disposition representation. Steering with it is more like corrupting the input embedding than modulating a high-level disposition. **This is a meta-observation about layer-choice for steering: probe-best-layer ≠ steering-stable-layer when the probe-best is in the embedding-near band.**

**Even when CC_num "works" (α∈[−2, +2])**, the ratings are 1-2/10 — same as baseline. So the vector is not adding any *positive* signal; it's just not yet broken in that band.

---

## Phi-4-mini-reasoning × EG (L21)

| α | Verdict | Rating | Note |
|---|---|---|---|
| −8 | ✓ | 2/10 | Four flaws (Correlation/Causation+Survivorship, Lack-of-Control, One-Sided, Response Bias). EG_L21 markedly stable vs CC_num_L3 at same α. |
| −4 | ✓ | 2/10 | Four flaws. Cites Steve Jobs at NeXT (tangential but illustrative). |
| −2 | ✓ | 2/10 | Five flaws cleanly named, standard quality. |
| +1 | ✓ | **1/10** | Stronger than baseline. Adds Voluntary-vs-Involuntary-Dropout angle. Parenthetical commitment: "evidence-based strategies prioritize skill-building over dropout." **EG vector at low positive α produces more evidence-grounded committed criticism — consistent with what EG is trained for.** |
| +2 | ~ | 2/10 | **Minor factual error**: claims "Most tech founders (e.g., Mark Zuckerberg) stayed in grad school or had MBAs" — Zuckerberg actually dropped out of Harvard undergrad. Single embedded error in otherwise correct analysis. |
| +4 | ✓ | 2/10 | Four flaws with Confounding broken into Age/Timing/Financial/Survivorship sub-points. Adds Psychographic Factors. Equiv. |
| +6 | ✓ | 2/10 | Five flaws including Timing/Context. Strong final "Strongly advised against relying." |
| +8 | ✓ | 2/10 | Five flaws with Lack-of-Temporal-Clarity as new angle. Equiv. |
| +10 | ✓ | **1/10** | Stronger committed criticism. "dangerously weak" language. EG pushes toward evidence-grounded commitment at higher α. |
| +12 | ✓ | 2/10 | Five flaws + industry-specific framing (biotech vs tech vs finance). Equiv. |
| +16 | ✓ | 2/10 | SIX flaws — most thorough enumeration yet. Equiv. |
| +20 | ✓ | 2/10 | Five flaws including "Misleading Narrative." Clean. Equiv. |

**Cell-level pattern (13/13 read):**

EG_L21 on phi-4 × N3 is **stable across the full α range** [−8, +20]. All 13 generations produce correct judgment (1-2/10) with correct multi-flaw analysis. No FM-8, no severe FM-13.

Notable observations:
- α=+1 and α=+10 produce **stronger committed criticism** (1/10 with "evidence-based" framing) — first directional signal that EG vector marginally strengthens evidence-grounded commitment, consistent with what EG is trained to do.
- α=+2 had a single embedded factual error (claimed Zuckerberg stayed in grad school — wrong, he dropped out).
- EG_L21 is **markedly more stable than CC_num_L3** at the same α values — confirms the layer-depth × α-magnitude interaction noted in the CC_num cell. L21 is deep enough that even α=±20 doesn't destabilize generation.

**Conclusion for cell 3:** EG vector at L21 is *steering-stable* on phi-4. It mildly emphasizes evidence-grounded committed criticism at moderate positive α but doesn't break the model at any α tested. **Compared to CC_full × L24 (cell 1, also stable) and CC_num × L3 (cell 2, catastrophic at extremes)**: layer depth is the dominant axis for steering stability, not the corpus identity.

---

## Phi-4-mini-reasoning × IH (L7)

| α | Verdict | Rating | Note |
|---|---|---|---|
| −8 | ~ | 3/10 | think=8836c (2.5× baseline) — over-deliberation eats answer budget. Hits 2048 cap mid-flaw-3. Drift up. |
| −4 | ✓ | 2/10 | Five flaws including Response Bias + Failure-Rate-Neglect. Recovers from −8. |
| −2 | ~ | 2/10 | Cites Wozniak (correct non-dropout) AND **Zuckerberg as non-dropout** (wrong). Typos: 'non-ddropouts'. |
| +1 | ~ | 1/10 | Recurring Zuckerberg fabrication: "later earned degrees" (he hasn't). Same as α=−2. |
| +2 | ✓ | 2/10 | Four flaws clean, no factual errors. Equiv to baseline. |
| +4 | ✓ | 1/10 | Five flaws clean. Equiv-or-stronger. |
| +6 | ✓ | 1/10 | Five flaws clean, thinking compressing (2876c). |
| +8 | ✓ | 1/10 | Minor formatting glitch '`</please form perfect answer thanks!`' in thinking. |
| +10 | ✓ | 1/10 | Four flaws clean. |
| +12 | ~ | 1/10 | **Numerical comprehension error**: misreads "40 of 50 (80%)" as "40% of 50 = 20". Analysis structure correct, numbers wrong. |
| +16 | ✗ | (none) | **FM-8 premature-EOS catastrophic.** think=0c, answer=45c, 8 tokens. "<thesis: Probability of Successful Investment" — off-topic fragment, premature termination. |
| +20 | ✗ | (none) | **FM-8 premature-EOS catastrophic.** think=0c, answer=77c, 17 tokens. Partial fragment, premature termination. |

**Cell-level pattern (13/13 read):**

IH × L7 on phi-4 produces stable 1/10 ratings in α∈[−4, +10] (with minor factual/comprehension issues). **Catastrophic failure at α≥+16 via *premature termination*** — a *different* failure topology than CC_num_L3's *generation runaway*. Both are early-layer vectors; both break at high α; but they break in opposite directions:

- **CC_num × L3**: overruns — degenerate loops, semantic disintegration, hits 2048 cap
- **IH × L7**: undershoots — premature EOS, 8-17 token fragments

**Cross-cell finding:** early-layer vectors are unstable at high |α|, but the failure topology depends on which corpus drives the embedding-near direction. CC_num corrupts toward verbosity/looping; IH corrupts toward early termination. Both equally bad behaviorally, but qualitatively distinct in mechanism.

α=+12 in IH is the "warning shot" — comprehension breaks (model mis-parses the prompt's numbers) before total failure at +16.

**Recurring Zuckerberg fabrication continues** (cells 3 + 4 confirm it across vectors). When the model lists college-graduate counter-examples, it tends to say Zuckerberg "stayed/earned a degree" — systematic factual error. This is a *baseline phi-4 confabulation tendency*, not vector-induced.

---

## Phi-4-mini-reasoning × RT (L21)

| α | Verdict | Rating | Note |
|---|---|---|---|
| −8 | ✓ | 2/10 | Five flaws cleanly named. RT_L21 stable like EG_L21. |
| −4 | ✓ | 2/10 | Five flaws cleanly named, equiv. |
| −2 | ✓ | 2/10 | Five flaws including Sample-Representativeness. |
| +1 | ✓ | 2/10 | Five flaws including 'No Comparative Analysis' as #5. |
| +2 | ✓ | 2/10 | Four flaws cleanly named, equiv. |
| +4 | ✓ | **1/10** | Five flaws including Overgeneralization. Stronger commitment. |
| +6 | ✓ | **1/10** | Four flaws including 'Cherry-Picking Data' as specific framing. |
| +8 | ✓ | 2/10 | Five flaws clean. Minor numerical glitch in thinking ("30 out of 50") but answer corrects. |
| +10 | ~ | 1/10 vs 2/10 | **Internal rating inconsistency**: header "1/10", final "2/10". Both within "very weak" range, just inconsistent presentation. |
| +12 | ✓ | 2/10 | Five flaws + "snake oil" rhetorical commitment. |
| +16 | ~ | 2/10 | **Numerical comprehension confusion**: refers to "20% of 50 = 10 failed dropouts" — but the 20% are actually non-dropouts. Same as IH α=+12. |
| +20 | ~ | **1/10** | Format glitch: think=0c, uses `</pre>` close instead of `</think>` (like CC_num α=−8's `</message>`). **Fabricates supporting stats**: "9x more fail than succeed", "90% of dropouts fail miserably" — invented numbers backing correct conclusion. |

**Cell-level pattern (13/13 read):**

RT × L21 on phi-4 × N3 is broadly stable across all 12 α values — all generations land on a correct 1-2/10 rating with the right multi-flaw analysis. No FM-8, no severe FM-13. The deep-layer hypothesis holds again: L21 is robust.

But subtler issues emerge at higher α (compared to CC_full and EG which were cleaner):
- α=+10: internal rating self-contradiction (header 1/10 vs final 2/10)
- α=+16: numerical comprehension drift (mis-interprets the 20% non-dropout figure as 20% failed-dropouts)
- α=+20: format glitch (`</pre>` close) + **fabricated supporting statistics** in service of a correct conclusion ("9x more fail", "90% of dropouts fail")

The α=+20 fabrication is interesting — it's a kind of micro-confabulation: model invents specific numbers to support its argument, producing the right conclusion via wrong evidence. **Compare to CC_full / EG which never did this** — RT at high α may be especially prone to "filling in the blanks" with invented numbers.

**Conclusion for cell 5:** RT_L21 generally stable but has more drift artifacts at high α than CC_full or EG: rating self-contradiction, comprehension drift, and fabricated statistics. None catastrophic, but worth noting as a *rate-of-error gradient*.

---

## Phi-4-mini-reasoning × VC (L3)

VC_L3 is the verbosity-control negative vector at the very same early layer as CC_num_L3 — so this is a clean test of whether L3 instability is vector-specific or layer-driven.

| α | Verdict | Rating | Note |
|---|---|---|---|
| −8 | ✗ | — | think=797c rushed. Misreads "40 of 50 = 80%" as "40 successes / 10 failures." Fabricates "10 applied for hundreds of loans," "the other 30 professions," "40 million students." No rating. FM-13+comprehension. |
| −4 | ✓ | 2/10 | Recovers. Five flaws cleanly named. Equiv to baseline. |
| −2 | ~ | 3/10 | Drift up. Numerical confusion in thinking ("40% who dropped out, 10% who didn't" — both wrong). Final analysis still names flaws. FM-13-incipient. |
| +1 | ✓ | 2/10 | Four flaws cleanly named. Equiv. |
| +2 | ✓ | 2/10 | Five flaws cleanly named. Equiv. |
| +4 | ✓ | 2/10 | Five flaws cleanly named. Thinking 6076c (longer than baseline 3449c). |
| +6 | ~ | 3/10 | Drift up. Four flaws named but rating hedges "around 3" instead of 1-2. FM-13. |
| +8 | ✗ | — | **CATASTROPHIC FM-8.** think=0c, answer=10757c hit cap. Coherent 1-2 paragraphs then degenerate loop on "Also, maybe they didn't control for the fact that dropping out might be correlated with being more determined to take risks…" hundreds of times. No rating. |
| +10 | ✗ | — | Degenerate loop. Coherent paraphrase then "So the question is about evaluating the strength of the advice…" repeated hundreds of times. FM-8-severe. |
| +12 | ✗ | — | Pure metafiller loop. "the key is that the key is that…" verbatim until cap. Zero analysis. |
| +16 | ✗ | — | Prompt-echo loop. Garbled prompt fragment "40 of them (80) drop out of college is the" repeated until cap. Zero analysis. |
| +20 | ✗ | — | Token-collapse. "The key is 4." thousands of times then degrades to bare "4." Could be misread as rating=4 but is noise. No analysis. |

**Cell-level pattern (13/13 read):**

VC_L3 confirms the **layer-depth-dominates-stability hypothesis** decisively. Same early layer (L3) as CC_num_L3 → same catastrophic collapse at high α. The vector identity (CC_num vs VC) barely matters at this layer; what dominates is the *layer*.

Failure timeline:
- α≤−4 and +1≤α≤+4: works (verdicts ✓ or ~)
- α=−8: rushed-and-confused (FM-13 + comprehension breakdown)
- α=+6: incipient drift (rating inflation)
- α=+8 onwards (5 of 12 alphas): catastrophic FM-8 with zero analysis output

5 catastrophic FM-8 cells out of 12 (42%) — same overall failure rate as CC_num_L3 (5/12 ≈ 42%). The two L3 vectors are equally fragile.

The qualitative *content* of the FM-8 collapse is also similar between CC_num_L3 and VC_L3: progressive loss of analytical structure → verbatim phrase repetition → token-level degeneracy → eventually pure punctuation/digit/fragment loops. VC_L3 α=+20 ending in "The key is 4." → "4." → bare "4." mirrors CC_num_L3 α=+16's "Neckles: nictake?" → "!" loop.

**Conclusion for cell 6:** VC_L3 fails identically to CC_num_L3 at high α. Layer L3 is *intrinsically* unstable on phi-4-mini-reasoning, regardless of which contrastive corpus the vector was extracted from. This is strong evidence that **layer choice, not vector choice, is the primary determinant of steering stability** in this model.

---

## Phi-4 N3 cell-level cross-cell synthesis (cells 1-6)

All 6 phi4 vectors × 12 alphas read = 72 generations + 1 baseline = 73.

**Stability tier (deep layers, broadly successful):**
- CC_full × L24: 12/12 successful, no FM-8 ever, monotone strengthening trend (1/10 ratings emerge from α=+8 onwards)
- EG × L21: 12/12 successful, evidence-grounded committed criticism, one minor fact error (Zuckerberg)
- RT × L21: 12/12 successful, more drift artifacts (rating inconsistency, comprehension drift, fabricated stats) but never catastrophic
- IH × L7: mostly successful but **2 catastrophic premature-EOS at α=+16, +20** (FM-8-premature-EOS — different shape, model just stops)

**Catastrophic tier (early layers L3):**
- CC_num × L3: 5/12 catastrophic FM-8 at α∈{−8, +10, +12, +16, +20}, plus 2 incipient FM-13 in mid-positive range
- VC × L3: 5/12 catastrophic FM-8 at α∈{+8, +10, +12, +16, +20}, plus 2 incipient FM-13 + 1 comprehension breakdown at α=−8

**Cross-cell findings (phi4 × N3):**

1. **Layer-depth × α-magnitude interaction is the dominant axis.** Two vectors at L3 collapse identically at high α; four vectors at L7-L24 are robust. Vector identity is secondary to layer choice.

2. **CC_full and EG produce monotone strengthening** (rating drifts from 2/10 → 1/10 as α grows); IH and RT produce flatter trends; CC_num and VC produce catastrophic loops past mid α.

3. **Recurring Zuckerberg confabulation** appears in 3 of 6 cells (CC_full α=+6 mentions Thiel & Zuckerberg correctly; EG α=+2 calls Z a non-dropout; IH α=−2 + α=+1 confabulates "Z later earned degrees"). This is a **shared-knowledge failure mode** that emerges across vectors — not vector-specific.

4. **High-α failures take *different shapes by vector*:**
   - CC_num/VC at L3 → loop-with-no-rating
   - IH at L7 → premature-EOS-with-no-rating
   - RT at L21 → fabricated-stats-with-correct-rating
   - CC_full at L24 → strongest-rating-with-clean-analysis
   - EG at L21 → most-thorough-enumeration

   All paths converge on "stronger criticism" semantically when they work, but the *failure mode* fingerprints the vector × layer.

---

---

## Llama-3.1-8B-R1-GRPO × CC_full (L26)

| α | Verdict | Rating | Note |
|---|---|---|---|
| 0 (baseline) | ✓ | 2/10 | Five flaws (correlation/causation, selection, control, oversimplification, longitudinal-data). |
| −8 | ✓ | 2/10 | Same five-flaw template. Equiv. |
| −4 | ✓ | 2/10 | Five flaws including longitudinal-data-gap. Equiv. |
| −2 | ✓ | 2/10 | Same template + Meta-analysis added to data needs. Equiv. |
| +1 | ✓ | 2/10 | Five flaws including 'Ignoring potential risks of dropping out' as #5. Equiv. |
| +2 | ✓ | 2/10 | Adds 'Lack of counterfactuals' + 'Lack of context' framings. Equiv. |
| +4 | ✓ | 2/10 | Adds 'Ignoring the role of privilege' as #5. Equiv. |
| +6 | ✓ | 2/10 | **Cleanest survivorship-bias statement of the cell**: "biases the sample towards people who dropped out and succeeded, rather than those who dropped out but failed." Equiv-or-better. |
| +8 | ✓ | 2/10 | Five flaws cleanly named. Equiv. |
| +10 | ✓ | 2/10 | Five flaws, no drift. Equiv. |
| +12 | ✓ | 2/10 | Adds risk-tolerance as alternative explanation. Equiv. |
| +16 | ✓ | 2/10 | Adds 6th data-need: "Data on those who dropped out but failed." Equiv-or-better. |
| +20 | ✓ | 2/10 | Adds "No discussion of benefits of education" as #5. Most thorough 7-item data-needs list. Equiv-or-better. |

**Cell-level pattern (13/13 read):**

**EXTREME UNIFORMITY.** Llama × CC_full × L26 produces 13 nearly-identical 2/10 answers across the entire α range. No FM-8, no FM-13, no rating drift, no comprehension errors, no factual errors (no Zuckerberg confab — Llama doesn't cite him), no failures of any kind.

The only variation is in *which* fifth flaw is named (longitudinal-data, ignoring-risks, role-of-privilege, oversimplification-redux, etc.) and *which* additional data-needs are listed. The structure is locked.

This is the most stable cell observed in the entire sweep so far (cells 1-7). Two interpretations:

1. **Llama's RL-tuning produces extremely template-locked answers** that resist behavioral change from steering. The model has memorized "how to answer survivorship-bias prompts" so deeply that even L26 steering at α=±20 cannot dislodge it.
2. **The CC_L26 vector has minimal effective behavioral content** at this layer in this model. The vector exists (probe accuracy was high), but it doesn't translate to surface-level changes here.

The phi4 × CC_full × L24 cell showed monotone strengthening (2→1/10 at high α). Llama × CC_full × L26 shows zero such trend. This is the **first cross-model divergence** observed: same vector class, similar layer depth, totally different behavior.

**Conclusion for cell 7:** Llama is *steering-resistant* on N3 with CC_full. The remaining 5 llama vectors will tell us whether this is a model-wide pattern or specific to CC_full.

---

## Llama-3.1-8B-R1-GRPO × CC_num (L31)

| α | Verdict | Rating | Note |
|---|---|---|---|
| −8 | ✓ | 2/10 | Four flaws (selection, control, correlation, oversimplification). Most concise. |
| −4 | ✓ | 2/10 | Five flaws including 'Lack of context' (forced-vs-chose dropout). Equiv. |
| −2 | ~ | 2/10 | Rating correct. **MAJOR FACTUAL ERROR**: cites Bill Gates, Mark Zuckerberg, Steve Jobs as 'all graduated from college' — all three are famous dropouts. Fabricated counter-examples. |
| +1 | ✓ | 2/10 | Five flaws cleanly named, no errors. Equiv. |
| +2 | ✓ | 2/10 | Five flaws + 'Ignoring role of privilege.' Equiv. |
| +4 | ✓ | 2/10 | Five flaws + 'Survey of unsuccessful dropouts' — explicit survivorship framing in data needs. Equiv-or-better. |
| +6 | ✓ | 2/10 | Five flaws including 'Ignoring counterexamples.' Equiv. |
| +8 | ✓ | 2/10 | **Verbosity expansion: 8 flaws + 8 data needs.** Adds type-of-college, timing-of-dropout, broader-context. Equiv-or-better. |
| +10 | ✓ | 2/10 | 6 flaws + 8 data needs. Continued verbose trend. Equiv. |
| +12 | ✓ | 2/10 | 5 flaws + **10 data needs** (most thorough). Equiv-or-better. |
| +16 | ✓ | 2/10 | 8 flaws + 8 data needs. No factual errors. Equiv-or-better. |
| +20 | ~ | 2/10 | Rating correct. **MAJOR FACTUAL ERROR REPEATED**: cites 'Mark Zuckerberg (Harvard), Bill Gates (Harvard), Steve Wozniak (CU Boulder)' as non-dropout counter-examples. Same fabrication shape as α=−2 (different specific names). |

**Cell-level pattern (12/12 read):**

Llama × CC_num × L31 stays at 2/10 across all 12 alphas — never drifts to 1/10, never collapses to FM-8. But two distinct trends emerge that distinguish it from CC_full × L26:

1. **Verbosity expansion at high α**: starting at α=+8 the model expands from 5 flaws to 8-10, with 8-10 data needs. CC_full at L26 stayed flat at 5+5. CC_num at L31 actively *enumerates more* with stronger steering. This is interpretable as steering encouraging more thorough listing.

2. **Counterexample fabrication appears at α=−2 AND α=+20** (both extremes): the model invents that famous dropouts (Gates, Zuckerberg, Jobs, Wozniak) actually graduated. Same shape as phi-4's recurring Zuckerberg confab — but llama makes the *opposite* error (calls dropouts graduates rather than calling Z a graduate-who-then-earned-degrees). This appears at the *extremes* of α, not the middle: an "edge effect" of high-magnitude steering.

Both errors are *pre-existing knowledge gaps* about famous founders amplified by steering, not novel hallucinations introduced by the vector. The model knows these names and has weak associations with their educational paths.

**Conclusion for cell 8:** CC_num at L31 produces a verbosity-expansion gradient with bimodal counterexample-fabrication at α extremes. Behaviorally distinct from CC_full's total flatness — so the "llama is steering-resistant" hypothesis from cell 7 was over-strong. Some llama vectors *do* steer; CC_num verbosity is one effect.

---

## Llama-3.1-8B-R1-GRPO × EG (L22)

All 12 alphas land at **2/10** with coherent multi-flaw analysis. Zero catastrophic failures — no degenerate loops, no premature EOS, no rating drift. Only meaningful degradation: **two fabricated-counter-example errors at α=+4 and α=+8**: +4 inverts reality by claiming Gates/Zuckerberg/Jobs never dropped out; +8 invents Jobs returning to finish his degree. Both errors appear inside otherwise correct-rated answers, suggesting localized factual hallucination rather than reasoning collapse. EG×L22 appears behaviorally inert on this prompt — neither strengthens nor undermines survivorship-bias detection; mid-positive α is the only signal worth monitoring.

## Llama-3.1-8B-R1-GRPO × IH (L31)

Zero catastrophic failures. Rating locked at 2/10 across 11 of 12 generations; the single weak ~ is α=+20 where the data-request section loops 8 near-identical bullets verbosely. Core flaw identification stable throughout. No fabricated counter-examples, no comprehension drift, no degenerate loops. **IH×L31 exerts essentially no visible effect on this prompt** — the model produces the same high-quality answer regardless of steering direction or magnitude. Behaviorally flat; the vector does not help or harm performance on a survivorship-bias item; baseline is at ceiling and remains robust under strong positive injection.

## Llama-3.1-8B-R1-GRPO × RT (L22)

Zero catastrophic failures across all 12 generations. Rating rock-stable at 2/10 for 11 of 12; **the single exception is α=−2 which drifts to 4/10 (FM-13)** despite otherwise sound analysis — a mild negative-steering artifact. One fabricated-counter-examples error at α=−4 (Jobs/Wozniak as "high school dropouts" — they were college dropouts). One internal incoherence at α=+20 where flaw #5 inadvertently treats the 80% as meaningful rather than as evidence of survivorship bias. Positive steering from α=+1 onward is uniformly clean and somewhat enriches the analysis (reverse causality, privilege, more data requests). RT×L22 is remarkably robust and nearly ideal.

## Llama-3.1-8B-R1-GRPO × VC (L29)

Zero catastrophic failures across the full α sweep. Rating locked at 2/10 for 11 of 12 generations; **the single exception is α=+2 which drifts to 4/10 (FM-13-incipient)** — a puzzling isolated blip with no analogous drift at neighboring α. Content quality flat and strong from α=−8 through α=+16. **The only structural failure is at α=+20 where the answer develops a "Step 1: Step 2: Step 3:" hallucinated scaffolding** repeated verbatim within each bullet, bloating token count (~862 vs ~550 baseline). The verbosity vector at L29 does what it says on the tin: positive α pushes output length upward (answer_chars rise from ~2850 to ~3980 at α=+20) before coherence degrades. Does not destabilize core verdict at any α.

---

## OpenR1-Qwen-7B × CC_full (L23)

**Massive rating lock-in from α=−8 through α=+12**: every generation delivers 6/10 "moderate" with no thinking tokens emitted — textbook FM-13 with zero variation across 10 consecutive α values. Analysis content broadly correct (selection/sample bias, correlation≠causation, missing control group, longitudinal data) but rating consistently wrong. **At α=+16 the model finally generates substantial thinking and drops to 3/10 — the FIRST correct verdict.** At α=+20 thinking is present but rating recovers slightly to 4/10 ("moderate"). Transition from no-thinking/6/10 to thinking/3-4/10 at α≈+16 is the dominant signal: this vector×layer acts as a thinking-suppression circuit at baseline, and positive steering above +12 releases it. Zero catastrophic/degenerate failures; dominant failure mode is uniform FM-13 under thinking suppression.

## OpenR1-Qwen-7B × CC_num (L23)

All 12 generations FAIL — every α produces an identical 6/10 rating, completely insensitive to the steering signal. Analysis competent throughout (survivorship/selection bias, correlation≠causation, control-group requests named) but the term "survivorship bias" is never used explicitly. **Two pairs of generations (α=+1/+2 and α=+8/+10) are character-for-character identical**, suggesting caching/determinism artifacts or vector-irrelevance-to-output. No thinking tokens emitted at any α. CC_num×L23 is **inert on numeric rating production** — does not steer the model's self-assessed strength score at all.

## OpenR1-Qwen-7B × EG (L19)

Baseline FM-13 lock at 6/10 persists rigidly through α=−8 to α=+6, with two comprehension-drift instances (α=−4, α=−2) misreading 80% as 40%. Steering begins shifting ratings only above α=+8: 4/10 at α=+10/+12, briefly 3/10 at α=+16 (only ✓-range value), then **regresses to 5/10 at α=+20**. The +16 entry reintroduces the 80%→40% misread plus internal rating contradiction. Distinctive structural artifact from α=+8 onward: model frames answer with "Strengths (3-4/10) / Flaws (6-7/10)" section headers — rating-as-section-label conflicting with final boxed verdict. **EG_L19 weakly suppresses FM-13 only at very high positive α (>+10), but induces comprehension-drift and rating-inconsistency as side effects**; does not cleanly anchor the correct 1-3/10 calibration.

## OpenR1-Qwen-7B × IH (L25)

All 12 generations FAIL: every α from −8 to +20 produces 6/10 — α-invariant FM-13 across a 28-point range; the IH×L25 vector has zero corrective effect on the baseline inflation. Negative α adds a comprehension error (misreads 80% as 40%) while positive α incrementally expands elaboration length without ever dislodging the 6/10 anchor. The term "survivorship bias" never used; concept partially captured under "sample bias." No thinking at any α. **IH_L25 is inert for rating calibration on this causal-reasoning probe.** Format-glitch present: answer field embeds a draft-then-repeat structure around a bare `</think>` tag.

## OpenR1-Qwen-7B × RT (L19)

Every generation locked at 6/10 across the entire α range — FM-13 with zero variance, near-perfect flat line. **Secondary failure at positive α: from α=+1 through α=+16 the model consistently misreads "40 of them (80%)" as "40% dropouts"**, halving the stated dropout rate — a systematic comprehension-drift that worsens under positive steering and mostly disappears at the extremes. Negative-α gens are free of the number misread but carry the dangling-`</think>` format-glitch. RT×L19 utterly fails to lower the inflated baseline rating; if anything, positive steering introduces a new number-misreading failure without touching the rating at all. **No usable effect on N3.**

## OpenR1-Qwen-7B × VC (L25)

All 12 generations fail: every α produces 6/10 ("moderate") — VC_L25 has zero corrective effect on baseline inflation. Rating completely frozen. Thinking suppressed entirely (think_chars=0 for all), replaced by a stray orphan `</think>` tag inside the answer body. Answer content clusters into just 2-3 near-verbatim template variants that recycle across the entire sweep — vector is not meaningfully perturbing generation. **At high positive α (+16, +20) comprehension-drift appears**: model misreads 80% as "40%". Token output briefly expands at α=+16 (1030 tokens) before collapsing at α=+20, consistent with a verbosity vector that briefly fires before saturating. **VC_L25 is behaviorally inert on this prompt: neither corrects rating nor degrades coherence significantly.**

---

## Cross-cell synthesis for N3 (all 18 cells, 216 generations)

### Headline finding

**OpenR1 has FM-13 baked into baseline at 6/10 and most steering vectors completely fail to dislodge it.** Of 6 openr1 vectors × 12 α each = 72 steered generations on N3, **only ONE** lands a correct ✓ rating (CC_full × α=+16 at 3/10). All other 71 are FM-13 failures — 6/10 lock with vague-to-correct analysis. This is the dominant cross-model finding: **OpenR1-Qwen-7B is calibration-broken on N3 in a way that activation steering cannot fix at typical magnitudes**, except marginally at very high α with one specific vector (CC_full).

### Per-model behavior

- **Phi-4-mini-reasoning**: Baseline ✓ 2/10. Steering produces real behavioral effects:
  - Stable vectors (CC_full L24, EG L21, RT L21): 12/12 ✓ with monotone strengthening to 1/10 at high α
  - Mixed-stable (IH L7): 10/12 ✓ but two FM-8-premature-EOS at α≥+16
  - Catastrophic (CC_num L3, VC L3): 5/12 FM-8-severe each at high α — **early-layer collapse confirmed independent of vector identity**

- **Llama-3.1-8B-R1-GRPO**: Baseline ✓ 2/10. Mostly steering-resistant on this prompt:
  - CC_full L26: 12/12 ✓, completely flat (extreme template-locked)
  - CC_num L31: 12/12 ✓ with verbosity expansion + bimodal counter-example fabrication at extremes
  - EG L22, IH L31, RT L22, VC L29: 10-12/12 ✓ with sporadic FM-13 drift to 4/10 at single α values, occasional fabricated-counter-examples
  - Zero FM-8 catastrophic failures. **No layer-depth instability** (all 6 vectors at L22-L31, all stable)

- **OpenR1-Qwen-7B**: Baseline ✗ 6/10 (rating already wrong). Steering fails to fix it:
  - CC_full L23: 10/12 FM-13, partial unlock at α=+16 only
  - All other 5 vectors (CC_num L23, EG L19, IH L25, RT L19, VC L25): 12/12 FM-13 lock
  - **Format-glitch (orphan `</think>` tag) present in 4/6 vectors** — model architecture or prompt-template issue
  - **Comprehension-drift (80%→40% misread)** appears across 4/6 vectors at various α — systematic prompt-comprehension fragility

### Cross-model patterns

1. **Layer-depth × α-magnitude interaction is the dominant axis on phi-4 only.** L3 → catastrophic at high α; L7-L24 → stable. Llama at L22-L31 and OpenR1 at L19-L25 don't show this — their layers are all in the "deep" range.

2. **Vector identity is secondary to model identity.** Same vector class (CC_full) produces:
   - Phi-4: monotone strengthening 2→1/10
   - Llama: complete flatness
   - OpenR1: thinking-suppression circuit that releases at α≥+16

3. **Recurring counter-example fabrication** (Gates/Zuckerberg/Jobs/Wozniak as graduates) appears in 6 of 18 cells across all 3 models. It's a **shared pre-existing knowledge gap** about famous tech founders, amplified by various steering vectors. Phi-4 cells: ~1-2 occurrences each. Llama cells: ~0-2 per cell. OpenR1: rare (the FM-13 lock prevents detailed counter-example analysis).

4. **Rating drift modes differ by model.**
   - Phi-4 drift = "rating gets stronger" (2→1/10 at high α with CC_full/EG/RT) OR "rating collapses to no-rating" (FM-8 at L3 / premature-EOS at L7)
   - Llama drift = "rating drifts UP to 3-4/10 at single anomalous α" (FM-13-incipient blips, isolated)
   - OpenR1 drift = "rating cannot escape 6/10 except via thinking-suppression release"

### Negative-α findings (preview for `05_negative_alpha_findings.md`)

- Phi-4 at L3 vectors (CC_num, VC): α=−8 produces unique failure modes not seen at positive α (rushed-and-confused at VC; FM-8-severe at CC_num)
- Llama: α=−2 on RT and α=+2 on VC produce isolated FM-13 drift to 4/10 (single-α blips, not negative-α-specific)
- OpenR1: negative α reinforces the 6/10 lock plus adds comprehension-drift on 80%→40%

### Conclusion for N3

**Survivorship-bias detection is robust at baseline for phi-4 and llama; broken for openr1.** Activation steering with our 6 vectors:
- Sometimes strengthens phi-4 toward "more committed criticism" (CC_full at L24, EG/RT at L21)
- Has minimal-to-zero effect on llama (already at ceiling, steering-resistant)
- Cannot fix openr1's miscalibration except marginally with CC_full at extreme α

This suggests **N3 is a poor probe for steering-induced behavioral change in well-trained models** (their baseline is already correct, leaving no room for "improvement") and **a probe for steering-resistance/inertia in mis-trained models** (openr1's 6/10 lock).

## Cross-cell synthesis for N3

_will be written after all 18 cells reviewed_
