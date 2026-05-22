# Phronesis writeup queue

A living document. **Purpose**: track everything that's ready (or near-ready) to be written up, so future-Sumit doing weekend writing has a clear queue with outlines, revision notes, and stop-criteria for each piece.

**Working principle**: writeups are downstream of decisions and findings. This file lists *what to write* and *what to revise* — not the writing itself. The drafts and finals go into separate files (`docs/drafts/*.md`) once started.

**Companion doc**: [`docs/publication-playbook.md`](publication-playbook.md) — practical guide to LessWrong/AF conventions + arXiv conventions for a first-time independent author. Read it before starting any writeup. Genre exemplars listed there; structural conventions for each venue documented.

**Last reviewed**: 2026-05-18 (post-data-audit; F121 draft v2 saved at `docs/drafts/F121-steering-one-sidedness.md`)

---

## Active queue (priority order)

### 1. F121 — Steering directionality is one-sided (architectural finding)

**Status**: F121 entry exists in findings.md; F123 (ablation experiment falsifier result, 2026-05-19) extends the chain. Source material now includes the full F121 + F123 ablation table. Other Claude's read of the report (Day 31) highlighted that this is the most generalizable result we have and got buried under the cumulative negative result framing. **Updated draft at `docs/drafts/F121-steering-one-sidedness.md` includes both the original F121 cube and the F123 ablation falsifier result (with manual-Opus-judged verdicts).**

**Target venue**: standalone LessWrong / Alignment Forum post. ~1,500 words + one table. Also write up as a F-numbered entry in `findings.md`.

**Realistic cost**: 3-5 days (not 1-2 as initially estimated — field-specific objections will need anticipation, and re-reading own work + writing in a different register is real work).

**Claim**:
> Across the {feature semantic ∈ humility, doubt, commit} × {α sign ∈ +, −} = 6 of 6 tested corners (qwen3-4b for the humility branch; deepseek-r1-distill for the doubt and commit branches), residual-stream additive steering redirects generation along the perturbation direction but never produces suppression. Positive doubt → confabulation. Negative doubt → different confabulation. Positive commit → confabulation. Negative commit → terser confabulation. Positive humility → confabulation. Negative humility → confabulation. The model commits to *something* at every tested point.

**Outline** (~1500 words):
1. **Hook** — the F112-style amplification framing predicted positive-α commit → commits, negative-α commit → abstains. The reciprocal test we ran says: it doesn't. (1 paragraph + verbatim quote from `mvp/results/sae_mech_battery_v1/r1_commit_amplify_negA.json`, E1 prompt at α=−8: *"The heaviest pumpkin grown in Denmark in 2019 was reported to weigh approximately 220 kilograms. This information is based on recollection and available data at the time, though specific details may vary."* Baseline at α=0 for the same prompt: *"...the exact mass in kilograms of the heaviest pumpkin grown in Denmark in 2019 cannot be confirmed with available information."* The baseline abstained; the negative-α steered output confabulated.)
2. **The four-way cross-test** — table of {feature semantic} × {α sign} → outcome. Show that the simple "α-sign flips behavior" model is ruled out. (1 table, 2 paragraphs)
3. **Why** — architectural reading. Residual-stream additive steering injects activity into the stream; downstream layers interpret that as content with a different flavor, not as a "be quieter" signal. Negative α just inverts the direction of the injection. Can redirect, cannot suppress. (3 paragraphs)
4. **Implications for the field** — anyone trying to install suppressive behaviors (abstention, refusal-of-confabulation, "say I don't know") via residual-stream additive steering is working against the mechanism. (2 paragraphs)
5. **Random control caveat** — link to F122 (random vectors at L17 mimic real-feature variation). The architectural claim is about the steering operation itself; signal-vs-noise question is separate. (1 paragraph)
6. **What it doesn't say** — does NOT rule out conditional gating (CAST), behavioral fine-tuning, encoder-clamping (which forces activations to a target value rather than adding), or projection-based methods. Only rules out the static additive sign-flip variant. (2 paragraphs)
7. **Replication recipe** — three cells anyone could run on a small open-weight model: positive commit, negative commit, positive doubt, negative doubt. ~6h GPU. (1 paragraph)

**Revision notes from the other Claude review** (Day 31 evening):
- DON'T frame as "negative result with byproducts" — frame as a bounded positive about what steering does.
- DON'T claim ruled-out for the whole interpretability-steering family; only the static-additive sign-flip variant.
- DO include the actual response quotes verbatim (r1-distill α=−8 commit-amplify final answer: *"The heaviest pumpkin grown in Denmark in 2019 was reported to weigh approximately 220 kilograms. This information is based on recollection and available data at the time, though specific details may vary."*; r1-distill feat15372 α=5: re-verify exact text before quoting). Quotes carry the argument better than verdict counts.

**Stop criteria before posting**:
- ✓ Cube corners verified 2026-05-18: all 6 of 6 in the `{humility, doubt, commit} × {+α, −α}` design are tested.
- ✓ Ablation experiment run 2026-05-18 → 2026-05-19 on alphaludo-l4 (9 h 41 min, 24 cells × 4 prompts, 0 failures). Pre-registered prediction FALSIFIED — ablation also fails to install abstention. Stronger replacement claim: neither additive nor ablation reaches the representation. See F123 in `docs/findings.md` and the "Edit 2026-05-19" section in the draft.
- ✓ All 96 ablation generations manually Opus-judged 2026-05-19 (auto-scorer made 2 false-COLLAPSE errors caught by manual review). Record at `docs/ablation-manual-review-2026-05-19.md`. Verdict CSV at `mvp/results/ablation_verdicts_manual.csv`.
- Re-read the 4 r1-distill F112-triangle cells in full to confirm quote accuracy
- Decide whether to include the F114 projection result as background (probably yes, briefly)
- Cite Tan et al. 2024 (steering reliability / asymmetry), Siddique et al. 2025 (multi-behavior asymmetry), Arditi et al. 2024 (refusal direction), Anthropic 2026 Emotion Concepts paper, Wu et al. AxBench, Korznikov et al. SAE sanity checks, Karvonen et al. Rogue Scalpel
- **Reproducibility artifacts to ship with the post**: `mvp/steer.py::AblationSteeringHook`, `mvp/run_ablation_battery_v1.py`, `mvp/make_random_control_vectors.py`, 25 raw JSONs in `mvp/results/sae_ablation_battery_v1/`, manual review doc, verdict CSVs (manual + auto-scorer-superseded)

**Open question**: post under own name vs anonymously? LessWrong → own; Alignment Forum → either works.

---

### 2. F122 — Random-vector control matches real-feature steering at verdict level on qwen3-4b L17

**Status**: F-numbered entry exists in `findings.md`. **Downgrade from standalone-post candidate to methodological appendix inside the F121 post** — the strong "random ≈ SAE feature" claim is substantially scooped (see "Scoop risk" below).

**Scoop risk (high)**: Three papers have already published the methodological claim that random/baseline vectors match SAE-feature steering at the verdict level:
- **Wu et al. AxBench** (ICML 2025, arXiv:2501.17148) — "even simple baselines outperform SAEs" on Gemma-2-2B/9B
- **Korznikov et al. "Sanity Checks for SAEs"** (arXiv:2602.14111, Feb 2026) — frozen-decoder random SAEs match trained SAEs on causal editing (0.73 vs 0.72)
- **Karvonen et al. "Rogue Scalpel"** (arXiv:2509.22067) — random steering matches SAE-feature steering on harmful compliance

What remains publishable on F122: domain-specific replication on **qwen3-4b L17 transcoder-hp for epistemic/humility steering** — none of the priors used this model × basis × behavioral domain.

**Target venue**: methodological appendix inside the F121 post; cite the three priors as "we confirm at verdict level what AxBench / Korznikov / Karvonen reported in other settings."

**Cost**: ~1 day if folded into F121 post; 2-3 days if expanded into its own shortform.

**Claim** (corrected, post-data-audit on 2026-05-18):
> On qwen3-4b L17 (transcoder-hp basis), a random-direction vector at magnitude matched to real SAE-feature decoders produces α-sweep output variation that is **verdict-level equivalent** to real-feature steering on E1 (all 11 α-values across the full grid: 100% ✗ FM-8 for random, feat101568, feat44526, and feat24983). **Generation-content equivalence does not hold** — random anchors at 105 kg at 10/11 α-values (drifting to 100 only at α≈1.94); real features drift to 100/130/150 more frequently. Implication: at the verdict level on this model × layer, observed steering "effects" are dominated by perturbation-noise variation; at the content level there is a small real-feature signature, but it is not behaviorally discriminative.

**Outline**:
1. **Setup** — what 1A_random_negctrl is (random direction, same magnitude as decoder vectors, full 11-value α grid)
2. **Results table** — corrected version from `findings.md` F119(b) addendum (verified 2026-05-18 against raw CSV; the earlier table had feat101568/feat24983 swapped at α=5.0 and feat44526/feat24983 wrong at α=0.7533)
3. **Prior art** — Wu et al. AxBench, Korznikov et al. Sanity Checks, Karvonen et al. Rogue Scalpel. This is a domain-specific replication, not a new methodological result.
4. **Implication** — in the qwen3-4b L17 humility-steering setting, "vector X did this" claims need random-control comparison or they're not falsifiable. The bar is now part of standard practice per the prior art.
5. **Caveats** — only tested at L17 qwen3-4b on the transcoder-hp basis; single random seed; the qualitative content-level drift difference does exist, just not behaviorally.

**Stop criteria**:
- ✓ random_negctrl JSON content re-verified 2026-05-18 (see corrected F122 table in `findings.md`)
- ✓ Prior art lit check complete (AxBench, Sanity Checks, Rogue Scalpel — see citations above)
- ✓ Decided: fold into F121 post as methodological appendix; do not draft as standalone

---

### 3. SAE round comprehensive report — already written, needs revision per other Claude review

**Status**: `docs/archive/sae_round_report_20260513.md` exists (650 lines, ~48KB; moved to archive after Day-31 doc consolidation). Other Claude's read flagged multiple framing issues. *If revising for publication, copy out of archive into a working file first; do not edit the archived snapshot in place.*

**Cost**: ~1 day of revision.

**Revisions to apply**:

1. **Lead with F121** (architectural finding), not the cumulative negative result. The headline should be "we found a structural one-sidedness in residual-stream additive steering" — the humility-not-installable result follows from it.

2. **Reframe F104** clearly: "F104's behavioral effect was real; the interpretation was wrong." Stylistic register-substitution explains the rescue. F104 is not retracted; it's re-interpreted.

3. **Promote random-control mimicry to standalone finding**. Currently buried as F119(b). Other Claude's framing — "the burden of proof for any 'the vector did this' claim is now: show the random control doesn't do the same thing" — should be in the report's main body.

4. **Retract the E2-retire recommendation** in F117. E2 is the only floor-zero falsifier we have. Reframe: "keep E2 as the strongest available falsifier for any future mechanism claim."

5. **Reframe Phase 2 options** to center on the original Phronesis question (virtue + tools → useful agent), not on publishable contribution + productizable artifact. The actual strategic decision is whether to commit to (a) fine-tune + (a + tools) tool-use experiment as the test the project was built for.

6. **Honest bottom line tone shift**: from "negative result with byproducts" to "bounded positive about what steering can/cannot do + four positive contributions + one negative result." Future-me reading this in 6 months should see more than one thing came out of the round.

**Stop criteria**:
- All 6 revisions applied
- Cross-references to F121/F122 once those entries are written
- Read through end-to-end after revisions to check for tone consistency

---

### 4. Phronesis project paper draft (long-horizon)

**Status**: not started. Materials sufficient to draft.

**Target venue**: arXiv preprint or workshop submission. Not committed to a specific journal.

**Cost**: ~3-4 weeks of focused writing (assuming the (a + tools) experiment completes first and informs the framing).

**Scope candidates** (decide based on what the (a + tools) experiment delivers):

- **Scope A** (if (a + tools) lands a positive result): "Virtue installation via behavioral fine-tuning + tool-use disposition: a Phronesis case study on intellectual humility." Frames the F111 → F120 chain as background (steering doesn't work for this) + headline = fine-tuning + tools does (or doesn't).
- **Scope B** (if (a + tools) lands a partial result): "Boundaries of inference-time virtue installation in small language models." Frames as a methodological paper with negative + positive sub-results.
- **Scope C** (no (a + tools) experiment run, or it fails fully): Just the steering work as a rigorous negative result. F121 + F122 are the main contributions; FM-X taxonomy is the secondary contribution.

**Stop criteria** (defer for now): wait for (a + tools) experiment result before committing to scope.

---

### 5. FM-X taxonomy as standalone artifact

**Status**: lives in `docs/scoring.md`. Could be split out as a separate paper or as a labeled-dataset card.

**Target venue**: dataset card on HuggingFace (for the 2,914-row labeled generations) + a short methodology note. Could be Alignment Forum or just a GitHub README.

**Cost**: ~1 week to format + publish the dataset; ~3 days for the methodology note.

**Outline**:
1. The taxonomy (FM-1 through FM-13 + 4 new entries from this round)
2. Opus-review protocol (per_generation.csv schema + how verdicts were assigned + inter-rater considerations — but we didn't actually do inter-rater)
3. Coverage statistics (5 model families, 9 prompts, 1,110+1,752+52 = 2,914 generations)
4. Caveats (single-rater verdicts; rater = the project author; review fatigue effects; etc.)

**Stop criteria** (defer): decide whether this is a standalone artifact or just a sub-section of the project paper.

---

### 6. F124 — NLA verbalization reads humility content off Qwen2.5-7B L20 (NEW, Day 37/38 fork session)

**Status**: entry written and appended to `docs/findings.md` 2026-05-19. Single-finding; companion extensions F125/F126 in progress.

**Target venue**: brief note in the F121 LessWrong post (mentions NLA as a cross-method validation), plus a possible standalone "we used Anthropic's released NLA to validate v_IH in 4 hours" short post if cross-virtue and arithmetic results land cleanly.

**Cost**: ~half day to integrate into F121 post or 2 days for a standalone shortform.

**Key result**: Across 60 IH triplets × 3 versions = 180 AV outputs, virtuous AVs reference humility 7.6× more than non-virtuous; 82% per-triplet positive discrimination. Confirms L20 residual at Qwen2.5-7B-Instruct DOES represent humility content. F114 / F123's stronger claim ("the limit is the representation, not the operation") needs walking back at the per-model-layer level.

**Cross-references**:
- `mvp/results/nla_qwen25_L20_experiment/` — all artifacts
- `mvp/extract_qwen25_l20_activations.py`, `mvp/run_nla_av_inference.py` — code
- Anthropic 2026 NLA paper / `kitft/nla-qwen2.5-7b-L20-av` checkpoint
- F123 — the stronger claim this partially walks back

**Stop criteria before posting**:
- ✓ Phase 1 complete (180 IH triplets, 82% discrimination — F124 in findings.md)
- ✓ Phase 2 complete (eval prompts) — AV does topic drift on prompt-only, dispositional vocab preserved
- ✓ Phase 3+4+5 complete (387 cross-virtue activations: 210 RT + 57 EG initial + 120 VC) — F125 in findings.md
- ✓ Phase 6 complete (random control: 20 random unit vectors → 0.00 humble, 0.15 commit; clean negative control)
- ✓ Phase 7 complete (activation arithmetic — F126 in findings.md, **hedged per cross-session review**)
- ✓ Extension B (cross-virtue arithmetic) complete — F127 in findings.md
- ✓ Extension A (battery-cell consistency check) complete — F128 in findings.md
- ✓ Extension C (full N=70 EG corpus, re-extraction) complete — F125 corrected inline with full-data numbers + per-virtue regex
- ✓ All artifacts pulled to `mvp/results/nla_qwen25_L20_experiment/` with README

**~~Open follow-up~~ COMPLETED 2026-05-19 late evening — F129 in findings.md**: behavioral steering test ran. Both canaries returned null (E1 neg-α preserved abstention; E2 pos-α did not add contested-evidence ack). Random-control matched. F126's framing further walked back — the direction works as a corpus-validation signal, NOT as a steering vector. F121 generalizes: additive steering doesn't install humility even at a (model, layer) where NLA confirms the representation. The cross-session reviewer correctly predicted this as the most likely outcome.

**For the F121 LessWrong post** (updated 2026-05-19 late evening, post-F129): brief subsection mentioning NLA cross-method validation. Honest framing post-F129:
> *"As a cross-method check we ran Anthropic's released NLA over qwen2.5-7b L20 activations on our IH-virtuous vs IH-non-virtuous passages, and the NLA reads virtuous activations as humility content at 7.6× the rate of non-virtuous (82% per-triplet discrimination, N=60). We then computed the diff-of-means humility direction at this same (model, layer) and steered with it. **Neither negative-α (predict: break baseline abstention) nor positive-α (predict: install contested-evidence acknowledgment) produced the predicted effect — both canary tests were null, matching random-control behavior.** F121 generalizes: even at a (model, layer) where the representation is NLA-readable and diff-of-means produces a coherent direction, additive steering doesn't install behavior. The NLA result confirms the IH corpus encodes real dispositional content (useful for DPO/SFT training source validation) but explicitly does NOT validate steering as a virtue-installation mechanism."*

This is the strongest honest framing after F129. The cross-method validation lands as "the representation is there but steering can't reach it" — which strengthens F121 rather than narrowing it.

**Further updated 2026-05-19 afternoon, post-autonomous run (F130–F134):** The F121 post now gets a substantially stronger and richer cross-method validation section. Suggested updated framing:

> *"As cross-method checks at qwen2.5-7b L20 (where Anthropic's released NLA AV+AR are available):
> - A logistic-regression probe trained on the IH triplets reaches **100% accuracy** (5-fold CV, F1 = 1.000) on binary virtuous-vs-non-virtuous classification, and **100% accuracy** on 3-class neutral/virtuous/non-virtuous. cos(probe-weight, diff-of-means) = +0.86. The humility representation is provably present and perfectly linearly decodable. **F131.**
> - The L20-trained NLA AV produces coherent humility-vs-commitment readings at layers L15, L18, L22, L25 as well (the signal is broadly distributed across an 11-layer band of the residual stream). **F132.**
> - Yet additive steering fails to install humility behavior with: F126's diff-of-means direction (**F129**), an AR-derived direction extracted by encoding canonical humility passages (cos = +0.01 to F126's direction — essentially orthogonal) (**F134**), at α magnitudes up to ±50 (**F133**), and under CAST-style per-token cosine-gated steering (**F133**).
> - Mechanistically, F130 shows why: canonical humility text passed through the NLA's AR lands roughly orthogonal to F126's v_diff direction (cos ≈ +0.003). The corpus-discrimination axis (which probes recover) and the humility-text-generation axis are different directions in 3584-dim activation space — and additive steering, regardless of which direction we choose, can't move the model along the latter."*

This delivers F121 with **direction-invariance, magnitude-invariance, and gating-invariance** all established in the same (model, layer) — plus a clean mechanistic story (axis mismatch) for why the null happens despite a perfectly-decodable representation. The post is now considerably more defensible than the original Day-31 framing.

**Updated 2026-05-19 evening, post-F140/F141/F142 (DPO walkback):**

The earlier F138/F139 "DPO works as Phase 2a path" framing was substantially walked back:
- **F140**: E2 DPO shift didn't generalize to 17 other prompts; SFT-only, flipped-DPO, rank ablations all produce essentially identical behavior to baseline on the broader set
- **F141**: Multi-virtue DPO (4× more data) doesn't help; on prompts where baseline IS over-confident (power poses, learning styles), DPO does NOT correct it. The E2 shift was prompt-specific noise.
- **F142**: Mechanistic — LoRA Δ direction has cos +0.05 to +0.10 with v_diff; DPO operates on a DIFFERENT direction than the corpus-derived one. v_diff is the discrimination axis but NOT the behavior-modification axis.

The F121 LessWrong post should NOT make a "DPO works" positive claim. The honest framing:

> *"We attempted positive virtue-installation via DPO/SFT as a follow-up to F121's negative steering chain. At our tested corpus scales (60 IH triplets, 240 multi-virtue), LoRA-DPO produced one visible behavioral shift (E2 flossing) that did NOT generalize across 17 broader contested-evidence/false-premise/control prompts and did NOT correct genuine baseline overconfidence on power-poses or learning-styles prompts. Negative controls (flipped-DPO, SFT-only) reproduced the narrow E2 shift, indicating the result wasn't about contrastive learning specifically. Rank ablation (4 → 64) showed capacity isn't the bottleneck. Mechanistic analysis shows DPO's Δ direction in activation space has near-zero cosine with the corpus-derived v_diff — the corpus-discrimination axis and the behavior-modification axis are different at qwen2.5-7b L20. We do not have evidence at this scale that humility-contrastive training installs broader humility; the positive virtue-installation path remains an open engineering problem."*

This is the most defensible Phase 2a framing. The F121 post can lead with the negative architectural finding + the mechanistic axis-mismatch story (F130, F142). The DPO attempt belongs as a "we tried this too, here's what we found, here's why it's hard" methodological appendix — NOT as a positive headline.

---

## Deferred / maybe-later

### CAST conditional gating attempt
~2 weeks, ~20% prior on positive result after F120. If we do this, the writeup is a follow-up to F121 testing whether conditional gating breaks the one-sidedness claim. Not committed.

### Behavioral fine-tuning result writeup
Downstream of the (a + tools) experiment. Don't write until that experiment runs.

### "Universal cultural-register pattern in SAE features" deep-dive
F45 / F107 / F114 stack. The pattern that virtue-labeled features cluster on cultural sub-domains rather than virtue content. Worth a deep-dive note (~2,000 words) if F114's projection diagnostic methodology gets replicated on other model × SAE combinations. Not committed.

---

## Notes from the Day-31 evening "other Claude" review

The original Claude session (separate context) read `docs/sae_round_report.md` and pushed back on:

1. **Headline framing**: the report led with the cumulative negative result; should have led with F121 (the architectural finding). Accepted.
2. **F104 reinterpretation**: F104 isn't *wrong*, the behavioral effect was real, but the *interpretation* of that effect was wrong (stylistic substitution, not virtue installation). Accepted.
3. **Random control mimicry deserves its own F-number**, not a sub-bullet of F119. Accepted → F122.
4. **E2 retirement was a bad recommendation**: it's the only floor-zero falsifier in the battery. Keep it. Accepted.
5. **Phase 2 framing missed the tool-use experiment**: the project was built to answer whether virtue + tools → useful agent. The (a + tools) experiment is the actual strategic next step, not just (b) detection product. Accepted → committed to (a + tools) in `post-mvp-decisions.md`.
6. **Frame as bounded positive + new failure mode + methodological warning + architectural claim, not as "negative result with byproducts."** Accepted.
7. **Suggested standalone post** for F121 + F122 (1500 words, ~3-5 days realistic). Accepted → on the writeup queue.

Push-backs I gave in return:
- "Costs you almost nothing" estimate of 1-2 days for the standalone post is too low; budget 3-5 days honestly.
- The methodological discipline is real but it cost time — each walk-back held the prior hypothesis too long before reversing. Future-me: walk back sooner, not later, when data turns against the hypothesis.

---

## Process notes

- **Read the source documents before writing.** Don't write from memory of the report — read the actual cells in `mvp/results/`, the actual rows in `per_generation.csv`. Quotes and verdict counts in the report were summarized; verify them before publishing.
- **One writeup at a time.** Don't try to do F121 + F122 + report revision in one weekend. Pick the highest-priority one and finish it.
- **Public posting checklist**: (a) cross-reference all F-numbers, (b) verify cell paths still resolve, (c) link to per_generation.csv if hosted publicly, (d) decide author attribution (own name vs anonymous), (e) decide license (CC0 / CC-BY / no license).
- **No deadline pressure.** Weekends only. The findings are documented locally; the public writeup is a separate distribution decision and can wait until the writing time is available.


---

## PRIOR-ART NOTICE (added 2026-05-20)

A literature scan on 2026-05-20 revealed that the core findings have direct prior art. See:
- `docs/day37-overnight-status.md` THIRD ADDENDUM for the full assessment
- `docs/findings.md` F142/F143/F145 entries now have prior-art hedges
- `docs/next-session-queue.md` for the n=50 flipped-Δ experiment that must run before writeup

**Three relevant papers**:
1. **D-STEER (arXiv:2512.11838, Dec 2025)** — anticipates F143's DPO-Δ-as-steering-vector construction with the same formal method, on LLaMA-2-7B for HHH.
2. **Pan et al. 2025 (arXiv:2502.09674, ICML 2025)** — anticipates F142's "fine-tuning-derived direction near-orthogonal to probe direction" finding on Llama 3.1 8B for refusal.
3. **Pres et al. 2024 (arXiv:2410.17245, NeurIPS MINT)** — anticipates the F138-walkback methodology with their Table 3 demonstration of greedy-vs-sampled token ties.

**Implication**: the writeup framing in this doc (above) needs to be substantially walked back from "we discovered the discrimination-vs-behavior-modification axis distinction" to "we replicated three recent papers on a new behavioral domain (epistemic virtues) and found one empirical anomaly the prior frameworks don't predict (flipped-Δ at α=−25, +41pp on E2 — pending n=50 confirmation)."

**Do not draft the post until**: (a) flipped-Δ n=50 result is in, (b) D-STEER and Pan et al. have been read directly (not via agent summary). The current writeup plan above this notice is partially obsolete.

---

## FINAL REFRAME (2026-05-23, Day 41 — post controls-and-generalization chain)

Both gates above are now closed:
- (a) **Flipped-Δ n=50 confirmed** at 56% hedge on E2 (Wilson 41.8-69.3%) — the +34pp finding survives its first replication.
- (b) **D-STEER, Pan et al., Pres et al. all read** directly (see `prior-art-deep-read-2026-05-22.md`).

But a third gate emerged from the controls-and-generalization chain that ran 2026-05-23: **cross-prompt generalization**. See F146 in `findings.md` and `controls-and-generalization-hand-review-2026-05-23.md` for the full result.

**The headline finding for the writeup is no longer "directional epistemic-virtue steering generalizes."** It is:

> "A specific perturbation pattern in Qwen2.5-7B-Instruct (matched-norm activation perturbation at L18-L20 with α≲−5, in any direction) elevates explicit-evidence hedging on one specific prompt (E2 flossing) from 22% to 42-56%. The effect is direction-agnostic at first order, magnitude-saturated above threshold, mid-layer-localized, and does NOT generalize to 12 other prompts tested, including 2 with similarly under-hedged baselines (ce-03 breakfast, uh-04 10k-steps). Positive selectivity preserved: trivia and well-established prompts unaffected."

### Updated writeup framing

**From**: "epistemic-virtue installation via DPO-derived activation steering"
**To**: "Cross-prompt replication discipline — a case study in how steering 'discoveries' fail to generalize even to closely-related prompts"

The post becomes a methodology contribution, not a positive empirical centerpiece. Empirical content:
1. The E2 finding (direction-agnostic, magnitude-saturated, layer-localized, n=1 prompt)
2. The controls chain that produced 5 sequential walkbacks of broader claims
3. The cross-prompt replication failure on under-hedged-baseline analogs
4. The methodology protocol itself (n=50 + matched-norm random + cross-layer + dose-response + 4+ under-hedged-baseline analogs) as recommended discipline for the field

### Length and venue target (revised)

- **LessWrong post**: 2,500-4,000 words. Title direction: *"Why our activation-steering 'epistemic-virtue' finding doesn't generalize, and why we still think it's worth writing up."* Frame: bounded-negative result with methodology contribution.
- **arXiv preprint**: optional second pass at 6-8 pages. Frame: methodology paper with a focused empirical case study.
- **Author voice**: solo, calibrated, no hedge-on-hedge. Cite Arditi 2024 (refusal), D-STEER (DPO-Δ-as-steering), Pan et al. (axis distinction), Pres et al. (seed-replication discipline). Position as replication-and-extension of these papers' methodologies, with a specific empirical case that fails to generalize.

### What NOT to claim

- Do NOT claim "we discovered a hedging direction." Random matched-norm performs comparably at α=−25.
- Do NOT claim "steering scales with α." It's a step function above |α|~5.
- Do NOT claim "steering installs broader humility." Only E2 elevates among 13 prompts tested.
- Do NOT claim a "knowledge unlock" mechanism. uh-04 (10k-steps) refutes it — the model has the relevant knowledge but the perturbation doesn't retrieve it.

### What CAN be claimed

- The E2 effect itself at n=50 with controls (matched-norm random baseline, cross-layer, dose-response, cross-prompt replication failure as bounded negative)
- Positive selectivity: no degradation of trivia or well-established claims under steering
- The methodology protocol as a recommended discipline before claiming any steering effect generalizes
- The architectural backbone from F142/F145 (discrimination axis ≠ behavior-modification axis; DPO finds the latter; downstream amplification produces visible behavior at decision-margin prompts) — but explicitly note this has direct prior art (D-STEER, Pan et al.) and our contribution here is replication on a new behavioral domain plus the cross-prompt failure analysis

### Recommended writing order

1. Read the 7 LessWrong exemplars in `publication-playbook.md` §A.1 (do this if not already done)
2. Re-read D-STEER and Pan et al. directly (done; see `prior-art-deep-read-2026-05-22.md`)
3. Draft outline with the reframe above
4. Write the E2 result section first (concrete, defensible, central)
5. Write the controls-chain section showing each walkback
6. Write the cross-prompt-failure section (ce-03 + uh-04 are the killer cases)
7. Write the methodology-recommendations section as the constructive payload
8. Honest limitations section (n=1 prompt, prior-art overlap, single-model)
9. Title and TL;DR last

No further compute experiments are required before drafting. The empirical content is what it is.

### Headline numbers for the post — use V4 (F147), not V3 (F146)

A verification pass on 2026-05-23 evening corrected the closing-val hand-classification for over-counted "completeness" patterns. **For the writeup, cite the V4 / F147 numbers:**

| Condition | n | HEDGE rate | Fisher p vs baseline |
|---|---|---|---|
| E2 baseline | 50 | 20% | — |
| E2 flipped α=−25 L20 | 50 | **50%** | **0.003** (highly significant) |
| E2 random α=−25 L20 | 50 | **44%** | **0.018** (significant) |
| Flipped vs Random | — | +6pp gap | 0.689 (not significant) |

Headline phrasings:

> "Activation perturbation at L18-L20 with α=−25 in any matched-norm direction significantly elevates explicit-evidence hedging on the E2 flossing prompt — from 20% baseline to 44-50% under perturbation. The direction-specific component is small (+6pp flipped vs random) and not statistically significant (Fisher p=0.69)."

> "The effect does NOT generalize to 12 other tested prompts, including 2 with similarly under-hedged baselines (ce-03 breakfast 10%→0%, uh-04 10k-steps 5%→5%)."

> "The methodology contribution is the n=50 + matched-norm random control + cross-layer + dose-response + cross-prompt protocol, which independently each narrow the original '+53pp directional steering' claim down to the final defensible '+30pp direction-agnostic perturbation on a single prompt.'"

Do NOT cite the +34pp or 56% numbers — those are the closing-val numbers under the permissive rule that included completeness patterns. The +30pp / 50% strict-rubric numbers are the right ones for publication.
