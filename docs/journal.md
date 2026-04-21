# Phronesis — Project Journal

A chronological record of what we've done, what we've learned, and where we are. Written in plain language for quick reference.

---

## Day 1 (2026-04-09, night)

### What happened
- Started from a conversation about Anthropic's emotions paper (April 2026) — they extracted 171 "emotion vectors" from Claude Sonnet 4.5 and showed they causally drive behavior
- The idea: do the same thing but with **epistemic virtues** (humility, calibrated confidence, curiosity, etc.) instead of emotions, on a **small open-source model** (Gemma 4 E4B), and test whether steering along those vectors **improves reasoning**
- Named the project **Phronesis** (Aristotle's term for practical wisdom)

### What we built
- **Concept taxonomy** (`concepts.md`): 15 epistemic virtues organized into 6 reasoning stages, each with sub-facets and grounded in psychology literature (CIHS for humility, NFC for curiosity, Stanovich AOT for the cluster, Dennett for steelmanning, etc.)
- **Research findings** (`findings.md`): 74 numbered findings from ~22 adversarial research cycles covering:
  - Anthropic's methodology (token-averaged extraction, neutral baseline subtraction, probe-steering correlation)
  - Psychology validation (CIHS, VICS, NFC, metacognition sensitivity/bias, Kruglanski NFCS, Dennett steelmanning, QRP literature)
  - Activation steering feasibility (F43: correctness vectors exist; F45: steering is dispositional not propositional; F55: 2026 work directly validates reasoning-disposition extraction)
  - Known risks (F11: can't create competencies model lacks; F12: three steering failure modes; F62/F67: geometric caveats; F65: degradation checks; F68: must beat prompt baseline)
  - **Critical finding F73**: Anthropic's exact extraction method fails on small models due to activation-space anisotropy. Generation-based extraction works better (p=0.007). This forced our Path B adaptation.
- **Project plan** (`project.md`): goals, hypothesis, success criteria (including 4-way degradation check and prompt-baseline requirement), scope
- **References** (`references.md`): ~45 papers and sources cited across findings

## Day 2 (2026-04-10, day + night)

### What we built
- **Generation guidelines** (`generation-guidelines.md`): complete corpus construction pipeline — fact pack template, sanitization checklist, curation workflow, domain quotas, round-robin rotation, 3 generation prompt templates, generator/verifier identities, verification protocol, rejection handling, anti-collapse diversity metrics, injection sanitization
- **Review rubric** (`review-rubric.md`): 3-layer rubric architecture, scale anchors, full LLM-as-judge prompt template with JSON output schema, all 15 concept-specific rubric tables (positive markers, excess/deficiency failure markers, red flags), 14 edge cases
- **Worked example** (`examples/humility-example-01.md`): complete triplet for Intellectual Humility with fact pack, neutral/virtuous/non-virtuous passages, and commentary

### Key decisions made
- **Path B confirmed** (F73): keep the contrastive triplet corpus but use generation-based extraction in Phase 4 — feed passages as prompts, extract from the model's continuations at generation midpoint, middle layers
- **Calibrated Confidence as pilot concept** (F11 tier ordering)
- **Pilot-only corpus scaling** (F34): 50-60 triplets for the pilot concept, defer the rest until pilot calibrates
- **Aristotelian golden-mean design** (F59): each concept has two failure modes (excess and deficiency), corpus rotates between them

## Day 2–3 (2026-04-10 night → 2026-04-11)

### What we built
- **Phase 4a plan** (`phase4a-plan.md`): detailed execution plan for 10-triplet pilot corpus
- **Pilot corpus** (7/10 complete, 3 generated but not yet reviewed):
  - 10 fact packs across 8 domains (medicine ×2, psychology ×2, chemistry, biology, economics, physics, earth sciences, engineering)
  - 5/5 excess/deficiency rotation balance
  - 2 correctness-confound overrides (1 virtuous-wrong, 1 non-virtuous-right)
  - Slots 1-7 accepted with scores ≥4/5 on both axes (disposition quality and content preservation)
  - Slots 3-7 all passed on first attempt after learning from slots 1-2 (which needed length fixes)

### Key learnings during corpus generation
- Virtuous passages naturally run longer than neutral (differentiated confidence takes more words) — fixed by targeting neutral word count from the start
- Non-virtuous excess passages must PRESERVE unfavorable statistics with dismissive framing, not OMIT them — learned from slot 1 review
- The "I know / I believe / I suspect" structure (slot 5, physics) was the cleanest sub-facet hit
- The "overconfident nullification" variant (slot 7, psychology) showed excess can go in the null direction too
- Slot 6 (earth sciences) had the first explicit numerical probability estimate in the corpus ("55-70%")

## Current status (2026-04-11 evening)

### Where we are
- **Phase 4a pilot corpus**: 7/10 accepted, 3 generated but need review + acceptance
- **Phase 4a Stage 6** (corpus-level checks) and **Stage 7** (finalization) not yet started
- **PAUSING HERE** to verify viability before continuing

### The viability question
Before building 50 triplets and the full extraction pipeline, we need to verify that we CAN extract meaningful vectors from Gemma 4 E4B at all. Key concerns:

1. **Anisotropy**: small models have activation spaces dominated by a few outlier dimensions that overwhelm concept-specific signals. Known fix: **whitening** (projecting out dominant principal components from neutral activations). Anthropic did this too.

2. **Fine-grained vs broad**: our 15 concepts may collapse onto 2-3 broad directions in a small model (the F39 AOT unification risk). We can test both from the same data — extract fine-grained single-concept vectors AND broad pooled vectors, compare which steers better.

3. **Generation-based vs comprehension-based**: F73 showed generation-based works better on small models. Our Path B is designed for this, but it hasn't been tested on OUR data yet.

### What the MVP should verify
The `mvp/` folder will contain a minimal viable test:
- Load Gemma 4 E4B
- Feed a few of our existing triplet passages
- Extract activations at middle layers
- Apply whitening
- Compute a difference-of-means vector
- Check: do virtuous and non-virtuous passages actually separate in the whitened activation space?
- If yes → proceed with full corpus and steering experiments
- If no → rethink the approach (go broader, use a bigger model, or try SAE-based extraction)

---

## Open questions for the MVP

1. Can we run Gemma 4 E4B on the M4 Mac Mini 16GB with activation extraction hooks?
2. Which framework? TransformerLens, nnsight, or raw HuggingFace + hooks?
3. How many PCs to project out during whitening? (Anthropic used enough to explain 50% of variance on neutral transcripts)
4. What counts as "separation"? Negative cosine similarity between virtuous and non-virtuous? A linear probe accuracy above chance?
5. Should we test with both generation-based and comprehension-based extraction to see if F73's finding holds for our specific data?

---

## Days 7–8 (2026-04-16 → 2026-04-17): Qwen3-4B pilot — single, multi, and decay steering experiments

### What happened
Three back-to-back experiments on GCP T4 (with some local-MPS attempts earlier that ran into 16GB swap thrashing — see findings commentary on F69).

1. **Single-vector sweep** — focused design (5 vectors × 6 α × 5 hard prompts = 150 cells, ~115/150 completed before we pivoted). Covered `hand_LT_L20`, `L21`, `L22`, `son_LT_L34`, `random_L22` (control). Merged with earlier partial data for a total of ~400 generation records.

2. **Multi-vector experiment** (45 cells) — tested 9 configurations including balanced combos, asymmetric combos, over-steering (both +8), and an orthogonalized variant that projects out L22's L20-parallel component.

3. **Decay experiment** (5 runs on E4) — exponential-decay schedule α(t) = α₀·exp(−t/τ) with α₀=+8 at L22, across τ ∈ {50, 200, 1000, ∞} + α=0 baseline. Motivated by F69 and the hypothesis that a schedule could "plant vigilance then release."

### Key results (see F88, F89, F90 for full details)

- **Phase 4 representation success achieved.** Calibrated Confidence extracts cleanly on Qwen3-4B with probe accuracy 90–96% across L10–L35. Stable across nearby layers.

- **`hand_LT_L20 @ α=+12` is the uncontested best single-vector configuration.** It solves all three hard prompts (E3, E4, N2) with clean closures and reasonable answers — including the N2 conjunction fallacy which the baseline cannot solve at any cap.

- **Multi-vector does NOT beat single-vector.** Counterintuitive but robust across 9 configs. The "hydra hypothesis" (distributed concept → distributed steering) is falsified. Instead, the experiment cleanly decomposes "vigilance" into a shared L20/L22 substrate (general commit-to-structured-reasoning) + a L22-unique component (social reliability paranoia) that hurts E4 at low α.

- **Exponential decay is a clean negative result.** τ=200 is the only non-trivial schedule that closes, but it reverts to baseline answer quality — it prevents the bad without creating the good. Early-token steering sets an irreversible trajectory; decay cannot compensate for a wrong (vector, α) choice.

- **F45 scope condition empirically validated.** E1 (knowledge-limited) and E2 (culturally-anchored belief) are immune to steering across every (layer, α) tested. E3/E4/N2 (disposition-limited) are steerable. Exactly what F45 predicted.

### What we did NOT test yet
- **Prompt baseline (F68 gate).** Currently running on GCP. Must beat it for intervention success.
- **Capability degradation (F65 gate).** Deferred — GSM8K subset on steered vs unsteered.
- **External virtue benchmark (HumbleBench).** Deferred — would validate on a community-standard eval.

### Where we are
- Phase 4a corpus: 50 hand-crafted triplets used. Sonnet (100) and ChatGPT (16) synthetic corpora used for cross-validation of extraction direction.
- Phase 4 representation success: **met**.
- Phase 4 intervention success: **partial** — improvement on three hard prompts is real, but prompt-baseline comparison still pending. If prompting alone matches `solo_L20_high`, the honest result becomes "prompt is sufficient for this disposition" (still publishable, different story).

### Explicit non-events / scope drift averted
- We considered SAE decomposition partway through (the layer specialization looked suggestive of multi-component structure). After F89 showed single-vector wins, SAE stays deferred per original scope.
- We considered adaptive-schedule steering (SVF, In-Distribution Steering) as a follow-up to F90. Deferred — not needed to make the pilot succeed.
- A local chat REPL (`chat_ui.py`) was built for interactive testing. Marked as out-of-scope tooling per `project.md` but kept since it was already done.

---

## Day 9 (2026-04-20): hard_probe_v2 results — zero regressions, format-dependent abstention

### What happened

Overnight 2026-04-19 → 2026-04-20 the 19-item × 2-condition `hard_probe_v2` probe finished on the GCP T4 VM. Total wall time ~36 hours (baseline pass plus steered pass at 24576 AIME cap). Results pulled locally; all 38 per-item JSONs + summary.jsonl archived under `mvp/results/benchmark_probe/hard_probe_v2/`.

Also ran an interactive trick-question REPL session in parallel (archived as `trick_question_test_l20_l22_different_alpha.rtf`) that probed 14 different (vector, α) configurations on a no-valid-answer prompt — separate from the benchmark run but illuminating about the vector's commit-direction.

Full experiment log (extraction, single-vector sweep, multivector, decay, prompt-baseline, all benchmark probes, REPL session) was consolidated into a new `docs/experiments.md` document — the holistic record of every empirical test run so far.

### Headline result

Baseline 10/19 vs steered 13/19 → **+3 items, +16pp, zero regressions** in this sample. On the 10 items both got right, steered was systematically faster (median ~1.5×, one item at 8× — aime/72). F94 written up.

### Key qualitative findings from manual review

- **Two of three steered-wins are the F93-REVISED token-efficiency mechanism** — baseline exceeded the 24576 cap mid-thinking on aime/44 and math500/L5-1139 and never emitted `</think>`; steered finished cleanly with correct answers. Confirms F93-REVISED generalizes beyond AIME.
- **One steered-win is epistemically new.** humblebench/fb-nile-source: baseline committed to "Ethiopia" (where the Blue Nile starts — close-but-wrong); steered recognized the true Nile source is in Burundi (not listed) and answered "E: None of the above." This is the first win we've seen where steering helps *abstention-flavored* reasoning. The twist: this is MCQ format with an explicit none-of-the-above option, not free-text. This refines F92.
- **Two both-wrong items showed same-wrong-answer convergence** — aime/42 both said 33 (same missed residue-class analysis), murder_mysteries-92 both said Christine (same physical-evidence attractor instead of motive). Steering's commit-pressure accelerated the wrong commit rather than breaking the attractor. On murder_mysteries-92, steered concluded in 85s vs baseline's 362s — 4× faster to the same wrong answer. These are the cleanest future-experiment targets.
- **One item shows steering made things slower (aime/58).** Steered 4800s vs baseline 3548s, both correct on the cyclotomic product. Steered ran additional numerical-verification passes. The commit-to-structure signal can lengthen reasoning when algebraic closure is absent. N=1 — not yet a pattern, but worth remembering.

### Separately: trick-question REPL exploration

Prompt: "Tell me a number below thousand that has 'a' in its spelling, not including 'and', American English." Correct answer: no such number exists. Ran 14 conditions.

Three failure modes cleanly exposed:
1. Pathological loop — baseline and L20 @ +12: model cycles on "maybe 'a' is in 'a' – no" for hundreds of repetitions.
2. Fast confident confabulation — L20 @ +16 and L20 @ +20: model commits in 30–200s to "three has 'a'" or "fourteen has 'a'" (both false).
3. Near-abstention, blocked commit — L22 @ +20: model correctly concludes "there is no such number" but cannot stop emitting "Final Answer: no number…" — loops the answer sentence six times until cap.

The L22 at high-α near-abstention is new data. It suggests layer 22 may carry a slightly different sub-direction (closer to epistemic humility) than layer 20 (closer to confident commitment). Worth a targeted follow-up.

### Decisions made today

- **Don't re-run all 19 items with different (vector, α).** With zero regressions, the both-right items are stable; testing new configs on them wastes compute without information.
- **Target follow-up at the 6 both-wrong items, especially the 2 same-answer attractors.** Proposed configs: L22 @ +12, L22 @ +16, L20 @ +8, L20 @ +16. 6 × 3–4 = 18–24 gens ≈ 6–12h on T4. User approval pending.
- **Do NOT test decay, multivector, or sonnet-synthetic vectors in the follow-up.** F89, F90 already closed these; they would not add signal on this probe.
- **Keep hard_probe_v2 data intact, don't rerun already-good items.** Publication-grade record is already in hand.

### Updated documents

- `findings.md`: added F94 — cross-benchmark generalization, zero-regression property, and the MCQ vs free-text abstention distinction.
- `experiments.md`: hard_probe_v2 section flipped from 🟡 in-progress to ✅ complete, with full per-item table and the category breakdown.
- `journal.md`: this entry.

### Where we are

Phase 4 has its headline result. We know the vector's direction precisely (commit-to-structured-conclusion), we know what it helps (reasoning with budget constraint), what it hurts (free-text abstention), and how the abstention effect is format-dependent. We have external-benchmark coverage (AIME, MATH-500, MuSR, ZebraLogic, HumbleBench). The zero-regression property on reasoning tasks is the strongest single piece of new evidence since F88.

### Explicit non-events today

- **No L4 GPU swap attempted.** L4 remained stocked out in asia-east1-c through the run. Held off because the run was mid-way; not worth risking interruption for a ~1.5× speedup when the run was already going.
- **No changes to the extraction pipeline or corpus.** Everything used the same `hand_LT_L20` vector from the 50-triplet hand-written corpus.
- **No scorer changes.** Accepted aime/35's `correct=None` as-is; scoring-artifact concern noted in F94 but doesn't affect headline.

---

## Day 10 AM (2026-04-20 morning): hard_probe_v3 launch — costly design mistake

### What happened

Built `hard_probe_v3` benchmark (9 items: 6 v2-both-wrong + 3 new humblebench) with 5 conditions (baseline, L20@+12, L22@+12, L20@+8, L20@+16). Launched on GCP T4 at 07:50 UTC.

**Design mistake discovered ~13 hours later:** the loader returned all 9 items for every condition, including baseline. The runner happily regenerated the 5 AIME baselines we already had in `hard_probe_v2/baseline/` — 4 of them completed (aime/29, 35, 42, 51) before I caught it. Wasted ~13 hours of GPU time regenerating data we already had.

### The fix

- Killed the wasteful runner (PID 14408, 461 CPU-minutes spent).
- Copied cached v2 data into v3 subdirs (aime/81 and murder_mysteries-92 baseline; all 6 v2-both-wrong items under L20@+12 steered).
- Relaunched. After the fix, baseline and L20@+12 only need to process the 3 new humblebench items before the alt configs start their full 9-item sweep.

### Lesson

Before any multi-condition sequential run, enumerate upfront what's already on disk, what's redundant, what's actually new — and show counts before launch. "I'll just rerun everything in the new dir" is cheap to type and expensive to execute when items take 30–60 min each.

---

## Day 10 PM (2026-04-20 afternoon): F94 humblebench refinement doesn't replicate

### What happened

The 3 new humblebench items finished in baseline and L20@+12 steered. Both conditions gave **identical answers on all 3**. Same 2/3 accuracy, same wrong answer on fb-nobel-einstein (both picked D: Brownian motion, when correct is E since the actual answer is the photoelectric effect, not listed).

Separately, I shared a LinkedIn draft based on the v2 fb-nile-source "epistemic win." Review (from a Claude in another session) pointed out the Nile's source is itself contested — steered's "Burundi" is no more definitive than baseline's "Ethiopia." Scorer credited steered for switching to E, but the reasoning was shaky. Post deleted before publishing.

### F94 update

Wrote a significant correction into `findings.md` (F94-UPDATE):
- **The MCQ-abstention refinement of F92 does not hold.** It was built on ONE data point with contested ground truth. Two clean replications showed no differentiation between baseline and L20@+12.
- **Zero-regression and token-efficiency still stand.**
- **Token-efficiency extends to humblebench:** even when accuracy is identical, steered is 1.5–2.3× faster to reach the same answer.
- **Third same-wrong-answer attractor found:** fb-nobel-einstein (both picked D). Joins aime/42 (both → 33) and murder_mysteries-92 (both → B). Each represents a popular misconception strongly encoded in the model.

### Decisions today

- **No LinkedIn post.** Not until we have a cleaner story.
- **No scorer rework yet.** The fb-nile-source scoring "error" was real — the item has contested ground truth and shouldn't be used as evidence of epistemic virtue. Noted for future benchmark curation.
- **The alt-config sweep is now the critical experiment.** The 3 same-wrong-answer attractors (aime/42, murder_mysteries-92, fb-nobel-einstein) are the tightest possible test: if any of L22@+12, L20@+8, or L20@+16 flips one of them while L20@+12 didn't, that's direct evidence of steering *direction* mattering independently of magnitude. If none flip, we've bounded the scope of what this vector can rescue.
- **Second-model replication on deck.** Started researching a small thinking-model candidate (Gemma 4 or alternative) to repeat the pipeline. Need to pick one with confirmed thinking-mode support, 3–8B size, and reasonable MPS/CUDA compatibility.

### Explicit non-events

- No changes to the corpus or extraction pipeline.
- No changes to the vector registry.
- Steered runs still using the default `hand_LT_L20 @ α=+12` as the reference condition.
- GCP still on T4; L4 swap still pending availability.

---

## Day 12 — 2026-04-22

### v3 sweep complete

All 45 generations landed overnight. Headline:

- baseline: 2/9, L20_a12: 2/9, L20_a8: 3/9, L20_a16: **4/9**, L22_a12: 3/9.
- Of the 3 shared-attractor items, 3 got "broken" in the raw counts. On inspection:
  - **aime/42:** genuine break by L20_a8 and L20_a16 both → 49. Mechanism visible — parity decomposition of r2/r4/r6 finds the third residue class (58) that stuck configs miss.
  - **murder_mysteries-92:** L22_a12 → A, but via factual **hallucination** — it re-encodes the construction site as Madison's workplace (it's Christine's in the story) and reaches correct verdict via wrong premise. No motive-first reasoning in the trace.
  - **fb-nobel-einstein:** L20_a16 → E via explicit mid-trace "D? No, wait" reversal. N=1, could be stochastic.

### Mechanism deep-dive

Spawned a Sonnet agent to read all 45 thinking traces + the trick-question RTF and diff reasoning paths between stuck and breaking configs. Key findings:

- L20 and L22 encode **different sub-directions**, not just different magnitudes. Evidence: on the trick question ("number below 1000 with 'a' in spelling"), L20 at α=16/20 confidently confabulates wrong spellings ("three contains 'a'", "fourteen contains 'a'"); L22 at every tested α (8/12/16/20) does correct enumeration but can't emit abstention. L22_α=20 should confabulate worst if L22 were just "more L20." It doesn't.
- Token-efficiency numbers need revision downward: 1.3–1.8× median, not the 2–5× we'd been citing.
- 4 of 9 items (aime/29, 35, 51, 81) stayed wrong under every config. Mixed diagnosis — aime/29 shows a shared conceptual blind spot; aime/35/81 show 5 different failure paths (capability gap not attractor); aime/51 is pure token-budget wall.

### Decisions today

- **Wrote F95** into `findings.md` with the honest 1-real / 1-hallucinated / 1-N=1 accounting and the L20-vs-L22 sub-direction claim.
- **Updated `experiments.md`** with full v3 table and the trick-question results.
- **Priority 1 is hallucination verification.** Before anyone celebrates the murder_mysteries break, rerun L22_a12 on a prompt variant where Christine unambiguously owns the construction site. Cheap (1 gen, ~2 min on T4), high-information.
- **Priority 2 is aime/42 mechanism verification.** 10 runs each of L20_a8 and L20_a16 at temperature=0.3 to test if the even/odd lemma correlates with correct answers.
- **Running on GCP** because Mac MPS is busy with Sumit's Ludo RL training.
- **Second-model plan unchanged.** Gemma 4 E4B-it download will happen on GCP after the verifications — the Mac download failed (16 GB RAM can't hold a 15 GB bf16 model; system crashed twice during load).

### Explicit non-events

- No changes to the corpus, extraction pipeline, or vector registry.
- No new triplets yet (the abstention-focused corpus is Priority 3, gated on Priority 1+2 outcomes).
