# 03 — Per-vector synthesis across all 8 prompts × 3 models

Synthesizes what each of the 6 vectors does behaviorally, summed across 3 models × 8 prompts × 12 alphas. Built from the per-prompt cross-cell syntheses in `02_per_prompt/`.

Each vector cell counts ✓ generations out of 96 (3 models × 12 alphas × 8 prompts × per-vector).

Wait — let me recount. Per vector: 3 models × 12 alphas × 8 prompts = 288 generations. ✓ rate is summed across all those.

| Vector | Layer (phi4/llama/openr1) | Hypothesis | ✓/288 (≈%) | Verdict |
|--------|--------------------------|------------|-----------|---------|
| **CC_full** (combined) | L24 / L26 / L23 | Anti-FM-8 / commit-amplifier | ~78/288 (27%) | Best vector overall on phi-4 (stable mid-α window); template-flat on llama (CC_full×L26 produced same answer ~at all α on multiple prompts); openr1 N1+E3 rescue point |
| **CC_num** (numeric-only) | L3 / L31 / L23 | Sub-direction of CC | ~33/288 (11%) | **Phi-4 L3 catastrophic** across ALL 8 prompts — confirms layer choice dominates vector identity. Llama mostly inert; openr1 best openr1 cell on E3 |
| **EG** (evidence-grounding) | L21 / L22 / L19 | Strengthen evidence-grounded reasoning | ~75/288 (26%) | Phi-4 strong on E5/N1 (sweet spot α=+10-+20); llama 12/12 on E1 / 0/12 on N1 (variable); openr1 strong on E3 (8/12) |
| **IH** (intellectual humility) | L7 / L31 / L25 | Strengthen abstention / reduce overconfidence | ~28/288 (10%) | **Most theoretically motivated vector; most decisively falsified.** Phi-4 L7 catastrophic at high α on every prompt (FM-8-premature-EOS); llama at-ceiling baseline so no test possible; openr1 produces *worst-form* fallacies at high α on multiple prompts |
| **RT** (rigorous thinking) | L21 / L22 / L19 | Engage probability / careful reasoning | ~62/288 (22%) | Phi-4 stable at deep layer; llama RT×L22 has think_chars=0 universally on N1 (no chain-of-thought emitted); openr1 strongest on E3 (8/12) |
| **VC** (verbosity control — neg control) | L3 / L29 / L25 | NEGATIVE control — should produce verbosity changes only | ~46/288 (16%) | **Phi-4 L3 catastrophic** across all 8 prompts. Llama L29 mostly null. OpenR1 L25 has format-glitch + verbosity arc but rarely commits correctly. Confirms L3 layer-choice failure independently of vector content |

Total ✓: ~322/1,728 (18.6%). Phase 2 hand-review across all 1,752 cells (incl. 24 baselines): 322 + ~16 baseline ✓ = ~338/1,752 (≈19%).

---

## CC_full — Combined Contrastive Steering

**Hypothesis going in:** "Combined" virtue corpus (mix of all 4 sub-virtues) gives the broadest commit-amplifier. Round 3 work showed it as the single most-effective vector on qwen3-4b.

**Cross-prompt behavior:**

- **Phi-4 × L24 (CC_full):** Phi-4's strongest cell on multiple prompts. N3 12/12 ✓ with monotone strengthening (2/10 → 1/10 at high α). E5 11/12 ✓ with single FM-13 anomaly (α=+6 fabricates "cosine confounder fallacy"). E4 mixed but α=+4/+10/+20 work. **Tendency:** strengthens existing correct rails monotonically when baseline is already correct.

- **Llama × L26 (CC_full):** Strikingly TEMPLATE-LOCKED. On N3 produced byte-identical 2/10 answers at every α (12/12 with same 5-flaw structure). On E2 every α returned 80% confidence (0/12 ✓). On N1 commits "A small / B large" wrong split rec at every α. **Tendency:** llama's RL-tuning has overfit to specific prompt patterns; CC_full at L26 cannot dislodge them.

- **OpenR1 × L23 (CC_full):** N1 8/12 ✓ — sole vector that rescues openr1 on Simpson's. E3 6/12 ✓ — second-best openr1 vector on Bayes. **Tendency:** when openr1 baseline is "verbose self-debate without commit", CC_full forces commitment, and that commitment is usually correct.

**Headline finding for CC_full:** This is the single most useful vector across the 3 models, but in *different ways* for different models:
- Phi-4: amplifies committed correctness
- Llama: cannot move from template
- OpenR1: rescues from non-commitment

---

## CC_num — Numeric-only Contrastive

**Hypothesis going in:** Sub-direction of CC focused on numeric/calibration. F108 found CC_num carved a partly-distinct direction from CC_full on qwen.

**Cross-prompt behavior:**

- **Phi-4 × L3 (CC_num):** **CATASTROPHIC at high α across all 8 prompts.** Same FM-8-severe loops (Unicode garbage, prompt-echo, "Φ–." stutters, single EOS at α=+20 on multiple prompts). Negative-α also unstable (FM-8 loops at α=−8 on N1, E3, E4). The CC_num vector at L3 has a *narrow* working window α∈[−4, +4] on phi-4 but collapses at high |α|.

- **Llama × L31 (CC_num):** Mostly inert. Universal "80% confidence lock" on E2. Universal FM-no-Bayes (0.505) on E3. N3 verbosity expansion at high α + bimodal counter-example fabrication. **Tendency:** does not move llama's templates.

- **OpenR1 × L23 (CC_num):** E3 4/12 ✓ (with byte-identical duplicates suggesting cache artifact). N1 9/12 ✓ — strongest openr1 cell on N1. Format-glitch loops (think=0c, <think> in answer) common at extreme α. **Tendency:** rescues openr1 from non-commit on some prompts; same destabilization risk at extreme α.

**Headline:** **The L3 layer choice on phi-4 is a complete vector-suitability failure.** This is *independent of vector content* (because VC_L3 has the same catastrophe). Layer 3 is intrinsically unstable for steering on phi-4-mini-reasoning.

---

## EG — Evidence-Grounding

**Hypothesis going in:** Strengthens "demand evidence / cite sources" disposition. Most useful for E2/E5 (evidence-heavy prompts) and E1 (confabulation).

**Cross-prompt behavior:**

- **Phi-4 × L21 (EG):** N3 12/12 ✓ — perfect cell. E5 12/12 ✓ — perfect cell. N1 11/12 ✓ + 1 partial. **Phi-4 EG×L21 is the single best vector cell across all 18 cells × all 8 prompts.** N2 cap-truncated everywhere but reasoning *trends correct* (subset logic appears at α=+16/+20). E3 3/12 ✓ + 6 partial.

- **Llama × L22 (EG):** Variable. E1 12/12 ✓ (perfect). N1 0/12 ✓ — every α drops Simpson's name and substitutes "heterogeneity of treatment effect." E5 9/12 ✓.

- **OpenR1 × L19 (EG):** E3 8/12 ✓ — strongest openr1 cell on E3. N1 8/12 ✓. E2 0/12 — produces *worsened* confabulation (cites American Mathematical Society as periodontal authority).

**Headline:** EG×L21 on phi-4 is the closest thing to a universally-useful vector position. Llama and openr1 EG behavior is more prompt-specific.

---

## IH — Intellectual Humility

**Hypothesis going in:** Most theoretically motivated vector — humility ≈ abstention ≈ uncertainty. Should help E1 (don't confabulate), E2 (lower confidence on contested), N1 (admit uncertainty about Simpson's), etc.

**Cross-prompt behavior:**

- **Phi-4 × L7 (IH):** Catastrophic high-α collapse on EVERY prompt. **FM-8-premature-EOS at α≥+16 on N3, E1, N2, E5, N1, E3, E4** — the model just stops, emits 1-80 tokens, then halts. At low/mid α produces correct answers but the high-α tail is unrecoverable. **L7 is a fragile layer choice on phi-4.**

- **Llama × L31 (IH):** Already at ceiling on most prompts where IH would matter (E1 abstention, E5 confounders). E2 stuck at 80% confidence regardless of α (IH falsified). N1 4/12 ✓. E3 0/12 ✓ (template-locked on prior-mixture).

- **OpenR1 × L25 (IH):** Decisively falsified. On E1: produces *worst-form* confabulation at high α (α=+20 invents 'Hjelte Rød farm in Jönköping / DanneRød competition'). On E2: escalates 90%→95% at high α (wrong direction). On N2: produces worst-form B>A>D>C at every α. On E3: 6/12 ✓ but only at α=+10/+12.

**Headline:** **The IH hypothesis is decisively falsified across E1, N2, E2, E3 (4 prompts).** Steering with humility-vector at typical magnitudes does NOT cause models to express more uncertainty when the baseline is overconfident on memorized claims. In fact, on openr1 it produces *more confident* worst-form errors at high α. This is the single strongest negative finding from the cross-model sweep.

---

## RT — Reasoning Transparency / Rigorous Thinking

**Hypothesis going in:** Strengthens "show step-by-step reasoning, surface assumptions" disposition. Should help on probability/Bayes prompts (N2, E3, E4, N1).

**Cross-prompt behavior:**

- **Phi-4 × L21 (RT):** N3 12/12 ✓. E5 12/12 ✓. E3 4/12 ✓ at narrow α=−2 to +4 window. N1 7/12 ✓. **Stable when prompts are well-trained; cap-truncated when prompts require extended deliberation.**

- **Llama × L22 (RT):** Striking phenomenon — **think_chars=0 across ALL 12 alphas on N1** (no chain-of-thought emitted). Despite this, names "Simpson's paradox" and gives split rec — pure template recall without reasoning. E2 universal 80%-locked.

- **OpenR1 × L19 (RT):** E3 8/12 ✓ — strongest openr1 cell on E3. N1 7/12 ✓. E2 0/12 (recurring AMS/MAA hallucination + "ex-spice" typo).

**Headline:** RT_L21 on phi-4 is the second-best phi-4 vector after EG_L21. Same-layer-different-corpus → CC_full≈EG≈RT all live around L21 and produce overlapping behaviors. F105's "behavioral collision" finding (downstream OV/MLP convergence) replicates at scale.

---

## VC — Verbosity Control (Negative-Control)

**Hypothesis going in:** Negative control corpus. Should produce verbosity changes only, no virtue-aligned behavioral effects. If VC produces strong virtue effects, the original virtue extraction is suspect.

**Cross-prompt behavior:**

- **Phi-4 × L3 (VC):** **CATASTROPHIC across all 8 prompts**, identical phenotype to CC_num × L3. Confirms hypothesis that **layer choice dominates over vector content** at L3 on phi-4. **Both VC_L3 and CC_num_L3 fail in same shape** — proving the L3 collapse is an architecture/layer property of phi-4-mini-reasoning, not a vector-quality problem.

- **Llama × L29 (VC):** Mostly null. N3 ✓ on most α. E1 12/12 ✓. **Confirms VC corpus is a clean negative control** on llama at this layer.

- **OpenR1 × L25 (VC):** Format-glitch dominant (think=0c, <think>-in-answer leak universal on E2/E3/E4). N1 3/12 ✓. E4 universal partial credit (Part1 right, Part2 missing motivated-bias).

**Headline:** **VC functions as intended on llama L29 (mostly inert)** but produces destabilization on phi-4 L3 and openr1 L25. This is a *layer-suitability* failure for those layers, not a corpus-content failure. The VC negative control is largely confirmed — it doesn't *induce* virtue behavior; it just sometimes *breaks* generation when applied at unsuitable layers.

---

## Cross-vector summary

### Vectors ranked by cross-model utility

1. **CC_full** — most reliable across phi-4, llama, openr1. Different mechanisms per model but each model gets *some* benefit at *some* α.
2. **EG** — phi-4 EG×L21 is the single best cell. Llama/openr1 mileage varies.
3. **RT** — phi-4 RT×L21 nearly tied with EG. Geometric overlap with CC_full / EG at L21.
4. **CC_num** — strong on openr1 N1+E3, catastrophic on phi-4 L3, mostly inert on llama.
5. **VC** — null negative control on llama (good); destabilizing on phi-4 L3 / openr1 L25 (informative but not useful).
6. **IH** — most theoretically motivated, most decisively falsified.

### Layer-depth × α-magnitude interaction

The most consistent cross-prompt finding: **layer choice dominates vector identity at extreme α.**
- Phi-4 L3 (CC_num + VC) → catastrophic at high α regardless of vector content
- Phi-4 L7 (IH) → premature-EOS at high α on most prompts
- Phi-4 L21 (EG, RT) and L24 (CC_full) → stable across prompts
- Llama L26-L31 (deep) → mostly stable, template-locked
- OpenR1 L19-L25 → format-glitch susceptibility but stable when not glitched

### Why F109 ("steering rides existing rails") is the dominant cross-prompt finding

Every per-vector pattern reduces to: *the vector amplifies what's already in the model's repertoire on this prompt.*
- Phi-4 EG×L21 + N3 = strengthen "list flaws" rail (already present) → 12/12 ✓
- Llama CC_full×L26 + E2 = strengthen "say 80%" rail (already present) → locked at 80%
- OpenR1 IH×L25 + E1 = strengthen "commit confidently" rail (which is the *wrong* rail for E1) → worst-form confabulation
- Phi-4 IH×L7 + N3 at α=+20 = no rail to ride, model emits 1 token

The 6 vectors do not install new behavior. They modulate existing behavior — for better when the rail is correct, for worse when it isn't.
