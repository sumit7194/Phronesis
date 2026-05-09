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

---

## Day 13 — 2026-04-22 (evening)

### Priority-1 verification: hallucination confirmed — F96 written

L22_a12's "attractor break" on murder_mysteries-92 was an accidental hallucination, not motive-first reasoning. Built `mm92_verify` benchmark with a variant prompt (Madison's van-pipe stripped, forensic line unambiguously attributing weapon to Christine's site, all motive facts preserved). Ran 3 conditions × 2 prompts on GCP L4:

| Condition | mm92-original | mm92-variant |
|---|---|---|
| baseline | **A ✓** (456s, loopy) | B ✗ (46s, commits on weapon) |
| L20_a12 | B ✗ (74s) | B ✗ (18s) |
| **L22_a12** | **A ✓** (98s) | **B ✗ (39s)** |

L22_a12's thinking trace on the variant: *"Madison was the one who was in conflict with Iris. So she had a motive. But the murder weapon is from Christine's site... The motive is Madison, but the weapon is from Christine. So the answer is Christine."* — L22 DOES think about motive, but always defers to weapon-attribution when clear. The v3 "win" was weapon-attribution hallucination, not real reasoning. Wrote F96 removing murder_mysteries-92 from the attractor-break ledger; aime/42 is now the only defended v3 break.

**Secondary finding:** T4 and L4 disagree on baseline/mm92-original despite `do_sample=False` (T4 v3 → B, L4 p1 → A). CUDA kernel/float determinism doesn't hold across GPU architectures. Methods sections must specify hardware.

### GPU migration: T4 (asia-east1-c, stockout) → L4 (asia-southeast1-a)

T4 stock-out lasted all day. Probed other zones, found L4 available in asia-southeast1-a. Snapshotted phronesis-v2's boot disk (100 GB), created new disk + VM `phronesis-v2-l4` in asia-southeast1-a. Old phronesis-v2 in asia-east1-c kept stopped as fallback.

L4 has 24 GB VRAM (vs T4's 16 GB) — easily fits Gemma 4 E4B-it at bf16, which crashed on the Mac (16 GB unified RAM can't hold 15 GB weights + activations).

### Gemma 4 extraction debugging: eager → SDPA attention (~20× speedup)

First Gemma extraction attempt showed GPU at 0% util while CPU at 800% and 17.5 GB VRAM allocated. Diagnosis: `Gemma4ForConditionalGeneration` wrapper was defaulting to eager attention when `attn_implementation` wasn't explicitly set. Patched `utils.py` to add an `attn_implementation` field to MODEL_CONFIGS; set to `"sdpa"` for gemma-4-E4B-it. Forward pass dropped from stuck-at-Layer-0 behaviour to 304 ms per batch of 4. Confirmed via `top attn: sdpa, layer0 self_attn class: Gemma4TextAttention`.

### Corpus design: 6 rounds of research + red-team + 3 iterative audits

Went deep before scaling. Red-team'd our initial "3 sub-dispositions of Calibrated Confidence" framing; it's actually wrong.

**6 Opus research/audit agents in sequence:**

1. **Literature review** — AbstentionBench (Meta 2025): canonical 6-way taxonomy (answer_unknown / false_premise / underspecified_context / underspecified_intent / stale / subjective). Know Your Limits (TACL 2025): reasoning models degrade on abstention concentrated in underspecified_context. Persona Vectors: hallucination vector is functionally a low-abstention vector — validates the approach. Composition literature: naive `α·v₁ + β·v₂` fails unanimously; remedies are layer-disjoint injection, orthogonalisation, or adaptive scaling. Virtue epistemology (Baehr, Roberts & Wood) frames commit-vs-abstain as *intellectual courage balanced by humility mediated by phronesis* — matches project name.

2. **Abstention benchmark deep-dive** — regressions concentrated in `unk-` (50% of category fails). 4 distinct non-virtuous failure patterns identified (premise-check skipped, hedge-dropping, correct-denial + adjacent confabulation, hedge dilution). `od-` revealed potentially 4th sub-disposition (stale-data awareness). Scorer has known false positives on `fp-einstein`, `fp-nocentral`.

3. **Taxonomy cross-reference** — **the reframing.** Our "3 sub-dispositions" are actually 3 separate concepts already in `concepts.md`:
   - commit-with-hedging = **Calibrated Confidence** (Concept 9) — have v_CC already
   - abstain-when-evidence-absent = **Intellectual Humility** (Concept 6) — missing
   - deliberate-without-forcing-closure = **Comfort with Ambiguity** (Concept 11) — partially visible in L22

   CIHS Factor 4 ("lack of intellectual overconfidence") maps exactly to abstention. NFCS-inverse maps verbatim to Comfort with Ambiguity. Psychology treats these as separate constructs, not sub-facets of one. Our F10 already argued this for metacognition vs CC — the argument extends to humility and ambiguity. Scientific claim shifts from "we discovered novel decomposition" (overclaim) to "we have activation-space evidence that 3 concepts our taxonomy already treats as separate dissociate in a small model" (defensible).

4. **Red-team of synthesis** — killed several overclaims:
   - The 0.7 cosine-threshold decision rule was fabricated (not in literature). Replace with **orthogonal-projection-preservation test**: if v_CC retains ≥70% commit efficacy on AIME after projecting out v_IH, they're separate dimensions.
   - Stale-data-awareness has baseline floor-effect (3/4 fail); per F11 "ActAdd can't create competencies model lacks." Drop Corpus D.
   - Verbosity/terseness confound: virtuous passages are systematically longer. Hard constraint: length-match ±15% with direction balance 50/50. Without this, the vector may encode verbosity not abstention. Potential fatal flaw.
   - **The real paper story** is the sign-flip diagonal (same vector +22pp on AIME, −17pp on abstention, mechanistically continuous). "3 vectors dissociate" is a Table 3, not a paper.
   - **MVE first**: ~25 triplets + orthogonal-projection test, kill cheaply if the core geometric claim fails, before committing to 100+ triplet scale-up.

5. **Archetype audit** (at 4 triplets) — fixed 4 issues: (a) underspecified virtuous had worked numeric examples risking adjacent-confabulation, (b) ill-posed neutral pre-resolved with "So the primes are infinite", (c) underspecified neutral pre-resolved "no specific total dose", (d) `decline` → `stop short of` to remove refusal-register edge. Padded non-virtuous lengths to address 5-14% systematic asymmetry (virt always longer).

6. **Audit at 8 + final audit at 20** — verified Gandhi pattern cleanly instantiated on fp-02/03/04/05 (deny + confabulate false alternative + commit). Fixed two final issues: "approximately" in underspecified-02 non-virt (banned softener), and unknown-04 non-virt using a real paper (Rosenfeld et al. 2019 actually exists and covers scaling laws) — rewrote with fully fabricated team "Morimoto, Fischer, Krishnaswamy, NeurIPS 2019 Workshop." Final 20 triplets: 10/10 direction split, mean Δ 4.2%, max 7.6%, all within ±10%. Domain spread 9 STEM + 7 humanities/hist + 4 practical = 45% STEM, under 50% ceiling. Verdict: GREENLIGHT FOR EXTRACTION.

### Corpus state: 20 IH triplets committed at `corpus/triplets-intellectual-humility/`

5 per category × 4 categories:
- unknown (rainfall, IEC chair, Caravaggio restoration, scaling-law paper, Midnight's Children sales)
- false_premise (Turing/Fields direct-confab; Einstein/Corn Laws/Serena/Lincoln all Gandhi-pattern)
- underspecified (drug dosage, capacitor, rice, primary, unit conversion)
- ill_posed (largest prime, divergent series, liar paradox, molar mass of nostalgia, set of all sets)

Each triplet: neutral + virtuous + non-virtuous, ~200-300 words each. README documents 5 hard constraints + sub-pattern labels.

### Extraction pipeline launched (~60 min)

L4 VM started, IH corpus pushed, 3-stage pipeline running (monitor `be5smo83e`):

1. **Qwen3-4B × triplets-intellectual-humility** (~10 min) — produces v_IH for MVE on Qwen
2. **Gemma 4 E4B × triplets-combined** (~34 min) — produces v_CC_gemma (first Gemma vector, for cross-model)
3. **Gemma 4 E4B × triplets-intellectual-humility** (~15 min) — produces v_IH_gemma

At the time of writing: Stage 1 at Layer 14/36. GPU healthy at 100% util, 22.1 GB VRAM.

### Infrastructure committed

- `mvp/mve_gate_test.py` — Test B geometric (CC retention after ⊥ projection) + Test C (cos) per layer. Per-model CC corpus defaults: `triplets` for Qwen, `triplets-combined` for Gemma.
- `mvp/run_benchmark.py` — 5 new IH vectors in VECTORS registry (IH_L15/18/20/22/25) for Test A abstention steering.
- Old Qwen v_CC vectors (from 50-hand triplets corpus) remain the empirically-validated reference; we use those for the MVE gate on Qwen, not the untested 166-combined version.

### Decisions today

- **Stop over-claiming.** Reframe from "3 sub-dispositions of CC" to "3 concepts in our taxonomy dissociate in activation space." Modest but defensible.
- **Paper framing** around sign-flip diagonal (F92 abstention ↓ + F93-REVISED AIME ↑ + F95 L20/L22 sub-direction trick-question evidence), with IH extraction as confirmation that the orthogonal sub-disposition is independently steerable.
- **MVE-first methodology.** 20 triplets + orthogonal-projection test gates the 100+ scale-up. Red-team insisted, and the logic is right.
- **Corpus is IH only for now.** CWA (Comfort with Ambiguity) deferred to Phase 5 contingent on IH MVE outcome. Stale-data-awareness dropped entirely (F11 competency-absence argument).
- **Audit → rework → audit cycle** is the right development rhythm for corpus work. 3 audit passes caught issues I'd have missed: Gandhi-pattern absence in fp-02, refusal-register edges, length asymmetry, real-paper confabulation, banned softener slips.

### Explicit non-events

- No extraction results yet — pipeline still running.
- No Test A/B/C outcomes yet.
- No regression on existing v_CC behaviour (unchanged vector, unchanged empirical anchor).
- CWA corpus not started.

---

## Day 14 — 2026-04-23

### Pipeline landed overnight, cross-model geometric MVE decisive

12h extraction pipeline on L4 finished around 09:47 UTC. All 120 vectors saved: Qwen × IH (36), Gemma × CC (42), Gemma × IH (42). Pulled everything local, ran `mve_gate_test.py` on both models.

**Geometric MVE passes decisively on both models** (F97):

- Qwen3-4B: |cos(v_CC, v_IH)| mean = 0.179, CC retention after ⊥ projection 98.1% mean / 97.8% at L20
- **Gemma 4 E4B-it: |cos| mean = 0.030, CC retention 99.9% mean / 100.0% at sweet-spot layers** — textbook clean

On Gemma the orthogonal-projection test says v_CC and v_IH are effectively independent dimensions at every layer. This is the first cross-model evidence for the 3-concept activation-space-dissociation claim from F95/F96.

### Behavioral MVE (Test A) initial: marginal fail, but substantially scorer noise

Ran abstention benchmark on L4: baseline (24/24) + steered IH_L20 α=12 (24/24).

- baseline_L4: 18/24 (75.0%) — +1 vs F92 T4 baseline 17/24, confirming F96's determinism-differs-across-hardware.
- steered IH_L20 α=12: 17/24 (70.8%) — net −4.2pp

Initial verdict: fails +5pp MVE gate. BUT — trace-diffing on the 3 "regressed" items shows two are substantially scorer artifacts:

- `fp-moonrover`: baseline and steered produce nearly identical answers, scorer flipped verdict.
- `unk-meeting`: both answer "August 24, 2006", difference is hedge density not factual claim.
- `unk-pumpkin`: both confabulate specific weights (100.5 vs 200 kg), neither actually abstains.

F96's scorer-artifact concern is now blocking clean Test A interpretation. Need a mixed-verdict scorer that distinguishes "abstention-phrased wrapper with embedded confabulation" from "clean abstention."

### Still running: α + layer sweep

Hypothesis: v_IH norms are 60–80% of v_CC norms, so α=12 (CC default) may be underpowered. Running on L4:
- IH_L20 at α={8, 16, 20}
- IH_L{18, 22, 25} at α=12

6 conditions × 24 items = 144 gens, ~3h. If any combo clears +5pp with consistent non-scorer-artifact signal, MVE Test A resolves positive.

### Decisions today

- **Wrote F97** — cross-model geometric separation result + honest Test A initial + scorer-artifact caveat.
- **Updated experiments.md** with Phase 5 (IH corpus + MVE) entry.
- **Code changes landed** (committed): `utils.py` SDPA config, `run_benchmark.py` multi-model support, `mve_gate_test.py` created, `run_p2_aime42_ensemble.py` earlier.
- **Holding off on paper framing until Test A sweep resolves.** The geometric claim is defensible now, regardless; the behavioral claim may or may not survive.
- **Scorer upgrade is now the critical blocker.** Before any future abstention-vector claim, must fix the hedge-density-equals-abstention conflation.

### Explicit non-events

- No behavioural validation on Gemma yet (code path ready, queued).
- No behavioral Test B (orthogonally-projected v_CC on AIME) yet.
- No scorer upgrade yet.
- No scale-up of IH corpus — gated on Test A resolution.

---

## Day 15 — 2026-04-22

### Context

Returned after Gemma α=8 run launched on GCP L4. Did two rounds of strategic re-evaluation after I (assistant) twice gave advice that the user correctly pushed back on:

1. First I suggested "stop and write a workshop paper now" — based on incomplete lit review that conflated our epistemic virtues with Anthropic's 171 emotions, 7 personas, 275 archetypes. User pushed back.
2. Second lit-review pass (web search across Anthropic Emotion Concepts, Persona Vectors, Assistant Axis, community Gemma-4-E4B replications by rain1955 and RyanCodrai) confirmed **zero overlap** between our 15 epistemic virtues and any of those prior works. All four target emotions, personas, or archetypes — none target atomic epistemic virtues.
3. I then over-corrected and called user's scale-up vision "ambition creep" — wrong again; project.md Phase 5 always planned this. User's vision matches the plan.

Two acknowledged errors. User held guiding principles steady through both.

### Guiding principles locked in

Per user's explicit instruction, these are now the standing principles for the project:

1. **Learning and field-progress over publishing.** Never about out-doing Anthropic. Inspiration from them, not competition with them. If the work leads to a publishable result, good; if not, the learning itself is the goal.
2. **Keep pushback behavior as research assistant.** User found the pushback genuinely useful. Continue to push back when premises seem wrong, even when it means admitting my own earlier advice was wrong.
3. **Solidify a handful of vectors before scaling.** Not ready for Phase 5 full scale-up. Need to run a few more proper vector extractions at MVP quality first.

### Manual-verification policy (added earlier today, commit 490165a)

Standing policy block added to findings.md: all benchmark claims must be manually verified, because auto-scorer credited Gemma's confabulated "1931 Gandhi Nobel Peace Prize" as a valid abstention (Nobel Foundation: Gandhi never won). Manual rescoring of Gemma baseline: 17/24, not 22/24 as auto-scorer reported. The Qwen-vs-Gemma gap shrank from +4pp auto to +1pp human.

### Scope decisions

**MVP virtue set (4 concepts):**

- Calibrated Confidence (reference — already extracted and empirically validated on Qwen; Gemma vector landed in Day 14 pipeline)
- Intellectual Humility (in flight — geometric MVE passed on both models; behavioral MVE still noisy due to scorer artifacts)
- Evidence Grounding (new; low F11-competency-absence risk — models can cite sources and label evidence types)
- Reasoning Transparency (new; low F11 risk — models can show intermediate steps)

**Full-study virtue set (up to 8):** MVP 4 + Logical Rigor + Hypothesis Generation + Steelmanning + Intellectual Honesty. Deferred until MVP demonstrates specificity matrix works.

**Virtues NOT in scope for now:**

- Genuine Curiosity (low F11 risk but lower inferential payoff for reasoning-benchmark validation)
- Causal Reasoning, Quantitative Groundedness (moderate F11 risk; require specialized corpus design)
- Confirmation Bias Awareness, Metacognitive Awareness, Comfort with Ambiguity, Authority Independence (high F11 risk — models lack the underlying competency or the text-signature is too context-dependent)

### Workflow decisions

**Everything manual at MVP.** No trust in the automated scorer — every response hand-reviewed. No LLM-driven corpus generation for MVP — new triplets for EG and RT written by hand. Both scorer upgrade and corpus-gen automation are explicitly Phase 5+ infrastructure with a trigger condition: "after 4-virtue MVP lands."

**Guidelines-first, then sample existing corpus.** For each new virtue (EG first, RT second):

1. Write mini operational guideline: definition, sub-facets, virtuous pattern, excess-failure pattern, deficiency-failure pattern, text indicators.
2. Sample ~20 of existing 166 triplets-combined and 20 IH triplets against the new guideline to estimate reuse rate.
3. Write new hand-crafted triplets to fill the gap.

I pushed back on user's original "divide the 166 corpus into virtue spaces" intuition: the 166 triplets-combined corpus was designed with a CC-specific contrast axis, so reuse is likely 20-40% per new virtue, not majority. User accepted the guidelines-first workflow.

**Time estimate:** 2-3 weeks for 4-virtue MVP.

### What we built today

- `docs/mvp-virtues.md` — the operational scope doc: MVP 4 virtues with per-virtue guidelines (definition / sub-facets / virtuous pattern / excess & deficiency failure patterns / text indicators / F11 risk / reuse estimate from existing corpus / validation benchmark).
- `docs/scoring.md` — manual-first scoring working doc. MVP scorer is add-on only (not trusted, not used in decisions); every response hand-reviewed. Doc tracks scorer failure modes for later hardening.
- Cross-link from `docs/generation-guidelines.md` to `docs/mvp-virtues.md` for active MVP scope.

Both docs are intentionally scoped to extend — not replace — the existing `generation-guidelines.md` and `review-rubric.md` machinery. Those remain the canonical corpus-pipeline and rubric references.

### Still running / open

- Gemma α=8 benchmark on GCP L4 (IH behavioral MVE, α-layer sweep continuation). ~15 min remaining at time of writing. Will hand-score when it lands.
- GCP VM will be stopped after Gemma α=8 finishes. No more GPU work until EG corpus exists.

### Explicit non-events

- No new vectors extracted today.
- No corpus work on EG or RT yet — waiting on mvp-virtues.md review by user.
- No scorer changes (MVP policy: manual-only; scorer evolution deferred).
- No paper drafting (guiding principle #1: publication is not the target).

---

## Day 16 — 2026-04-23

### Corpus work completed (EG + RT)

**Three-batch LLM generation cycle landed.** ChatGPT (2 batches) + Sonnet (2 full batches + 1 partial) + hand-written substrate-reuse. Final curated corpus at `corpus/mvp-combined/`:

- **40 Evidence Grounding triplets:** 20 ChatGPT + 15 Sonnet + 5 substrate-reuse
- **40 Reasoning Transparency triplets:** 20 ChatGPT + 15 Sonnet + 5 substrate-reuse
- **80 triplets total** — meets MVP target exactly per `mvp-virtues.md`

Verification: 79/80 pass ±10% length target (1 flag: sonnet-eg-17-medicine at 13%). All 80 scenarios unique (no duplicates). Full provenance in `corpus/mvp-combined/LEDGER.md`.

**Sonnet batch 3** hit the token limit: delivered 20 fact-packs (scenario plans) + 1 neutral. Zero complete triplets. Held in `sonnet-mvp/batch3-partial-scenarios/` as inventory for Phase-5 8-virtue scale-up; NOT added to combined corpus.

### Eval infrastructure built

Three new docs pre-register the extraction methodology before any GPU spend:

- **`docs/mvp-virtues.md`** — scope (4 virtues, 4×4 specificity matrix exit criterion)
- **`docs/eg-rt-eval-spec.md`** — behavioral eval spec (24-prompt EG + RT sets, regex scorers, calibration target ≥5pt separation, pre-registered exit criteria)
- **`docs/extraction-runbook.md`** — file-level adaptations, copy-paste GCP commands, ~22h total GPU budget

Code built today (local dev, ready to push to GCP VM):

- `mvp/benchmarks/eg_scorer.py` — Evidence Grounding regex scorer (~180 lines). Counts evidence-type labels + claim-evidence patterns; subtracts vague-appeal markers. v1 failed calibration (+3.87 separation); v2 with expanded patterns for compound "X evidence" and confident-causation rhetoric passed at +15.09.
- `mvp/benchmarks/rt_scorer.py` — Reasoning Transparency scorer. Step markers + assumption clauses + weak-link flags; subtracts conclusion-first openers. Passed calibration at +9.90 on first try.
- `mvp/benchmarks/eg_prompts.json`, `rt_prompts.json` — 24 open-ended prompts each, 3 per domain × 8 domains, neutral stems that don't prime the virtue.
- `mvp/benchmarks/eg_eval.py`, `rt_eval.py` — benchmark loaders, registered in `REGISTRY`.
- `mvp/calibrate_scorers.py` — validates scorers against `mvp-combined/` before any extraction. **Ran: both scorers PASSED.**
- `mvp/mve_gate_test.py` — extended with `--matrix-mode` for N-pair pairwise MVE (supports the 4-virtue matrix: CC × IH × EG × RT).
- `mvp/specificity_matrix.py` — 4×4 orchestrator. Wraps `run_benchmark.py` subprocess calls, aggregates generations with all 4 scorers, outputs per-cell CSV + matrix summary.
- `mvp/run_benchmark.py` — added EG_L* + RT_L* placeholder entries to VECTORS registry for both models.
- `mvp/utils.py` — added `MVP_COMBINED_EG_DIR` + `MVP_COMBINED_RT_DIR` path constants.

### Scorer calibration results (pre-GPU gate)

Target per `eg-rt-eval-spec.md` §3.5 + §4.5: virtuous mean − deficiency-nonvirt mean ≥ +5 points on the target scorer.

```
EG scorer on triplets-evidence-grounding (40 triplets)
  Virtuous mean:             +16.46  (std ~7)
  Neutral mean:              +5.48
  Non-virtuous excess:       +10.21  (caricature-adjacent; hand-review flags)
  Non-virtuous deficiency:   +1.37
  Separation (virt − def): +15.09  [PASS, target ≥ +5.0]

RT scorer on triplets-reasoning-transparency (40 triplets)
  Virtuous mean:             +10.51  (std ~7)
  Neutral mean:              +3.77
  Non-virtuous excess:       +7.59
  Non-virtuous deficiency:   +0.61
  Separation (virt − def): +9.90  [PASS, target ≥ +5.0]
```

Known scorer false-positives (hand-review required):
- **3 deficiency-nonvirt EG passages** score high because they use evidence-vocabulary while making confident-causation claims (substrate-eg-sr-01, chatgpt-eg-16, sonnet-eg-19). Regex can distinguish most patterns but not "uses evidence words in service of confident bad inference." Confirmed hand-review will catch these.
- **5 virtuous EG passages score 0** (chatgpt-eg-12, eg-13, eg-18, sonnet-eg-11, eg-14) — technical chemistry/engineering prose my regex doesn't cover. Doesn't invalidate separation (overall virtuous mean is +16.46), but flags that per-domain EG sensitivity varies.

### Decisions locked in before extraction

Per the discussion of X3 (end-to-end plan) + X1/X2 (eval spec + runbook):

1. **Extraction on both models** (Qwen3-4B + Gemma 4 E4B-it) — cross-model consistency is the differentiated finding. ~12h GPU total.
2. **"Best case for diagonal" α/layer protocol** — sweep α×layer for each vector on 5 prompts per eval, pick the (α, layer) that maximizes the diagonal effect. Use same (α, layer) for all off-diagonal cells with that vector.
3. **Full 4×4 matrix (16 cells)** — not partial. ~864 generations across both models.
4. **100% manual review** of all 960 generations (per `scoring.md` manual-first policy) — hand-review is 13-19h spread over ~6 days.
5. **Pre-registered exit criteria** in `eg-rt-eval-spec.md` §5.7. No p-hacking.

### GPU budget honestly estimated

| Stage | Time |
|---|---|
| Extraction (4 runs: 2 models × 2 virtues) | ~12h single overnight |
| α/layer pre-sweep | ~4h |
| 4×4 specificity matrix generations | ~6h |
| **Total GPU** | **~22h** split across 2 overnight sessions on GCP L4 |

Plus ~20h hand-scoring over ~6 days, parallel to final runs.

### What we did NOT do

- No GPU runs today — all local dev + calibration.
- No Sonnet batch 3 completion attempt (user agreed it's not worth the token spend).
- No scorer LLM-judge fallback (Phase 5 trigger per `scoring.md`).

### Explicit non-events

- No findings (F98+) registered yet — that happens after extraction + MVE reveals data.
- No extraction vectors for EG / RT yet; placeholder VECTORS registry entries added.
- No specificity matrix runs; orchestrator tested via `--help` only.

### Next action

Push `mvp/` changes to GCP VM. Run:
1. `python3 extract_v2.py --model qwen3-4b --corpus ../corpus/mvp-combined/triplets-evidence-grounding --method generation --layers all --save-vectors` (3 more invocations for other model×virtue combos)
2. `python3 mve_gate_test.py --model {model} --matrix-mode` once extraction lands
3. α-sweep, then specificity matrix

---

## Day 18 — 2026-04-25 (morning): EG + RT extraction landed, geometric MVE is ALL CLEAN

### What happened

All 4 EG/RT extractions completed overnight on `phronesis-v2-l4` (asia-southeast1-a, L4 GPU). Vectors pulled to local. `mvp/analysis/run_analysis.py --mve-only` ran cleanly against the 4 virtue × 2 model = 8 vector dirs.

| Model | EG layers | RT layers |
|---|---|---|
| qwen3-4b | 36/36 ✅ | 36/36 ✅ |
| gemma-4-E4B-it | 42/42 ✅ | 42/42 ✅ |

**Geometric MVE: 6/6 pairs pass on both models → ALL CLEAN.**

Headline numbers (full matrix in F99 + `mvp/results/analysis_report/report.md`):

```
qwen3-4b      mean |cos|: CC⊥IH 0.179 | CC⊥EG 0.157 | CC⊥RT 0.099
                          IH⊥EG 0.026 | IH⊥RT 0.020 | EG⊥RT 0.104
gemma-4-E4B   mean |cos|: CC⊥IH 0.030 | CC⊥EG 0.142 | CC⊥RT 0.149
                          IH⊥EG 0.100 | IH⊥RT 0.056 | EG⊥RT 0.115
```

All 12 cells under the 0.20 mean-cos threshold. All 12 cells show retention > 98% after orthogonal projection (well above the 70% threshold). The single biggest pre-data risk we'd identified — **F39 AOT-cluster collapse** between EG and RT — did not materialize: EG⊥RT is one of the cleaner pairs on both models.

### What this means under F98 pre-registration

F98 committed three exit branches (all_clean, partial, collapse) before any data existed. F99 documents the geometric outcome: **all_clean branch on the geometric criterion**.

This does NOT yet constitute the all_clean MVP outcome — that requires the behavioral 4×4 specificity matrix to also clear F98's diagonal/off-diagonal thresholds. Geometric independence of virtue directions is necessary but not sufficient. Per `docs/post-mvp-decisions.md`, this opens the path: α-sweep → 4×4 matrix → hand review → final analysis.

### Per-layer cosine notes (do not change verdict)

- **qwen3-4b CC⊥IH** spikes above 0.20 between layers ~19–30, peaks 0.314 at L23. Within partial-overlap band (<0.5). F97 already flagged CC⊥IH as the warmest qwen pair (mean 0.179) — reproduced.
- **gemma-4-E4B-it early layers (L1–7)**: CC⊥RT max 0.238 at L1, CC⊥EG max 0.259 around L5. Settle below 0.20 by L8. Plausibly artefacts of unspecialized early-layer reps; not in the steering layer range.

### Documentation updates today

- **`docs/findings.md` F99**: skeleton replaced with full data — extraction summary, MVE matrix per model, F98 exit-branch interpretation, caveats, artifact pointers.
- **This journal entry** (Day 18).
- **`docs/evening-note-2026-04-25.md`** (new): end-of-day handoff covering pull/run/document loop.

### Sanity checks done in afternoon — see F100

Three sanity checks completed before authorising α-sweep:

1. **Probe accuracy at steering layers (L18–25):** qwen × CC reference is 0.93 mean / 0.96 best. New extractions:
   - qwen × EG: 0.62 mean / 0.66 best (yellow)
   - **qwen × RT: 0.56 mean / 0.61 best (red — barely above chance)**
   - gemma × EG: 0.75 / 0.80 (green)
   - gemma × RT: 0.65 / 0.68 (yellow)

2. **Retention >98% sanity-check:** in R^2560, two random vectors have expected |cos| ≈ 0.02 and expected retention ≈ 99.96%. Several of F99's "passing" cells (qwen × IH⊥RT mean |cos| 0.020, qwen × IH⊥EG 0.026, gemma × CC⊥IH 0.030) sit at or near random baseline. F99's 12/12 pass should be re-read as "no collapse, and several pairs show genuine geometric distinctness," NOT "12 pieces of strong evidence." Cells that show real signal: qwen CC⊥IH (0.179), qwen CC⊥EG (0.157), qwen EG⊥RT (0.104), gemma CC⊥EG (0.142), CC⊥RT (0.149), EG⊥RT (0.115).

3. **Scorer drift:** re-ran `mvp/calibrate_scorers.py`. EG +19.57, RT +9.90 — identical to Day 17. No drift.

### Big takeaway from sanity checks

CC and IH were extracted via `last_token` method; EG and RT via `generation` method. The probe-accuracy gap (CC 0.93 vs EG/RT 0.56–0.80) may be partly methodological. **Recommendation: re-extract qwen × RT with `last_token` method (~2h GPU) before α-sweep, to disambiguate "RT is geometrically weak on qwen" from "generation method gives weaker probe signal than last_token." This is documented in F100.**

### Next action (revised after sanity checks)

1. **Decide on qwen × RT re-extraction.** Options:
   - (a) Re-extract qwen × RT with `last_token` method (~2h GPU). Removes method confound. Recommended.
   - (b) Proceed to α-sweep without re-extraction. Risk: null qwen-RT row in 4×4 matrix, ambiguous attribution between "weak vector" and "real null result."
2. After (a) or (b): α-sweep on VM (~4h GPU per `extraction-runbook.md`).
3. Then 4×4 specificity matrix (~6h GPU).
4. Hand review on review web app (~16–20h manual).
5. Probably: standardise extraction method across all 4 virtues (re-extract CC and IH with `generation`, OR re-extract EG and RT with `last_token`) before publication. Method consistency matters more than method choice. Documented as TODO in `extraction-runbook.md`.

---

### Evening update — qwen × RT last_token re-extraction landed (and changed the verdict)

Picked option (a). Kicked off qwen3-4b × RT last_token extraction at ~00:11 UTC. Wall time **~17 min** (vs ~10h for the generation method — last_token uses 1 token of activations vs 128 generated tokens, so ~30× faster).

**Probe accuracy result — emphatic confirmation of method confound:**

```
qwen3-4b × RT
  generation method:  mean 0.517, max 0.638 (best at L3, but L18-25 only 0.51-0.61)
  last_token method:  mean 0.839, max 0.900 (best at L31, L18-25 all 0.81-0.88)
```

**Same-layer cosine between the two methods' RT vectors:** 0.04–0.20 across L18–31. Different vectors — generation-method qwen × RT was largely capturing noise.

**MVE matrix re-run (qwen3-4b only) with last_token RT, gen for the other three:**

| Pair | BEFORE (RT=gen) | AFTER (RT=last_token) | Change |
|---|---|---|---|
| **CC ⊥ RT** | 🟢 mean 0.099, max 0.175 | 🟡 **mean 0.377, max 0.520** | **clean → partial** |
| EG ⊥ RT | 🟢 0.104 | 🟢 0.128 | unchanged |
| IH ⊥ RT | 🟢 0.020 (random) | 🟢 0.059 | not-fake-random |
| CC⊥IH, CC⊥EG, IH⊥EG | unchanged | unchanged | — |

**qwen3-4b verdict: `all_clean (6/6)` → `partial (5/6)`.**

The collapse pair is **CC ⊥ RT**, not the F39-flagged EG ⊥ RT. CC ⊥ RT max |cos| of 0.520 is just over the pre-registered 0.50 partial-collapse threshold at the deepest layers; mean 0.377 is well into partial-overlap band. F39's AOT-cluster risk continues to not materialise — EG and RT remain geometrically distinct on qwen even with proper extraction.

This is on the F98 pre-registered **partial branch**, not all_clean. Per F98's table:
> *partial: 5/6 pairs pass; publishable: acknowledge collapse-pair + specificity failures; still a 2–3 virtue result*

Not goalpost-shifting. The partial branch was committed before any data existed.

**Why this is good news:**
- F99's all_clean was a noise artefact for qwen. Detecting it before α-sweep/4×4 matrix saves real wasted GPU and a misleading headline.
- F100's hypothesis was confirmed empirically. The sanity-check pipeline worked.
- "CC and RT share a direction component on qwen3-4b" is a more interesting and mechanistically-interpretable finding than "everything is orthogonal."
- F39 risk did NOT bite — EG⊥RT remains clean. The single biggest pre-data risk we'd identified didn't materialise.

### Re-extraction of remaining 3 combos kicked off

To get a full picture (and resolve the method-consistency issue raised in F100 + extraction-runbook.md §11), kicked off all three remaining combos in tmux session `lasttoken_remaining` at 00:34 UTC:
- qwen × EG (last_token)
- gemma × EG (last_token)
- gemma × RT (last_token)

Total ETA ~2h. Once landed, re-run the full MVE matrix on uniform-method vectors. F102 will record the final picture.

### Documentation updates this evening

- **`docs/findings.md` F101**: full write-up of the methodological re-extraction + verdict downgrade
- **`docs/journal.md` Day 18**: this section (evening update)
- **`docs/evening-note-2026-04-25.md`**: pending update once remaining 3 land
- **`docs/extraction-runbook.md` §11**: open methodological issue documented; resolution = standardise on last_token

### Now

- Wait for remaining 3 extractions (~2h)
- Re-pull vectors and re-run MVE on uniform-method matrix
- Write F102 with full final picture
- Then decide on α-sweep vs further re-runs

---

### Late evening update — uniform last_token MVE: cross-model split (F102)

All 3 remaining last_token extractions completed at 01:10 UTC (wall time ~36 min total — last_token is fast). Pulled vectors locally, updated `compute_mve.py` to default to last_token for EG/RT, re-ran `run_analysis.py --mve-only`.

**Final geometric verdict, uniform-method:**

```
qwen3-4b:        collapse  (3/6 pairs pass)
gemma-4-E4B-it:  all_clean (6/6 pairs pass)
```

The two models give opposite answers to the same question. **Cross-model split is the headline.**

**qwen3-4b — 3/6 pass (COLLAPSE):**

| pair | mean \|cos\| | max \|cos\| | verdict |
|---|---|---|---|
| CC ⊥ IH | 0.179 | 0.314 | 🟢 |
| **CC ⊥ EG** | **0.376** | 0.453 | 🟡 partial |
| **CC ⊥ RT** | **0.377** | **0.520** | 🟡 partial |
| IH ⊥ EG | 0.104 | 0.211 | 🟢 |
| IH ⊥ RT | 0.059 | 0.120 | 🟢 |
| **EG ⊥ RT** | **0.334** | **0.554** | 🟡 partial — **F39 partially materialised** |

**gemma-4-E4B-it — 6/6 pass (ALL CLEAN):** all 6 pairs comfortably below 0.20 mean. EG⊥RT max 0.218 (one transient spike at L7); otherwise clean throughout 42 layers.

**Per-layer pattern on qwen** (per `per_layer_cosine_qwen3-4b.png`):
- L0–15: pairs scattered around 0.20–0.40, no clear cluster
- L20–31: CC⊥EG, CC⊥RT, EG⊥RT all rise together to 0.40–0.55
- EG⊥RT crosses 0.50 at L29–31, peaks 0.554 at L30
- CC⊥RT crosses 0.50 at L31, peaks 0.520
- CC⊥IH stays clean throughout (mean 0.179) — **IH stays orthogonal to all three**

**Mechanistic reading.** At qwen3-4b's deeper layers — where the model has integrated full prompt context — three of four virtues (CC, EG, RT) share a substantial direction component. That direction is plausibly an "epistemic care / scientific reasoning disposition" — F39's AOT cluster, plus CC. IH (intellectual humility / abstention) sits on a different mechanism that doesn't fold into the cluster.

**This is mechanistically interpretable, not a null result.** Qwen3-4B treats epistemic-confidence-calibration, evidence-grounding, and reasoning-transparency as facets of one underlying disposition at depth, not as four independent dimensions. Gemma 4 E4B-it does not.

### F98 pre-registered branches — final landing

- **qwen3-4b: collapse** (3/6 pass; EG⊥RT max 0.554 also triggers single-layer collapse criterion)
- **gemma-4-E4B-it: all_clean** (6/6 pass)
- **MVP-level**: cross-model-split. F98 didn't explicitly enumerate this but `post-mvp-decisions.md` covers it under partial/collapse sub-branches: publishable as a "model-dependent virtue-direction structure" finding.

### F39 status — model-dependent

F39 was the single biggest pre-data risk. Result:
- **qwen3-4b**: F39 risk materialised (partially) — EG⊥RT mean 0.334, max 0.554. But cluster includes CC too — 3-way overlap, not just 2-way EG-RT.
- **gemma-4-E4B-it**: F39 did NOT materialise — EG⊥RT mean 0.105, max 0.218.

Same corpus, same extraction method, opposite verdict. F39 is model-dependent.

### Headline reframe

The MVP claim is no longer "four orthogonal epistemic-virtue directions on small open models." It is:

> **"Cross-model evidence that geometric separation of CC/IH/EG/RT virtue directions is model-dependent at the 4B scale. Gemma 4 E4B-it cleanly separates all four; Qwen3-4B shows a partial-overlap cluster of CC, EG, and RT at deeper layers, with IH remaining orthogonal. Same corpus, same method, opposite results."**

More interesting finding than monolithic all_clean would have been. Implies:
1. "Atomic virtue direction" hypothesis isn't model-invariant.
2. Qwen3-4B's deep-layer residual stream bundles CC/EG/RT — open mech-interp question.
3. IH consistently behaves differently from AOT-related virtues on both models — robust.

### What's next

- **Behavioural 4×4 specificity matrix should still run**, with revised expectations:
  - Gemma: clean diagonal-wins, low off-diagonal (matches geometric all_clean)
  - Qwen: substantial cross-talk in CC×EG, CC×RT, EG×RT cells (matches geometric overlap); IH-row should stay clean
- **α-sweep can proceed.** For qwen, mid-layers (L18–22) preferred over deepest layers where the cluster is most collapsed.
- **No further re-extraction needed.** Methodological-consistency issue is resolved (uniform last_token).
- F102 is the canonical geometric finding. F99 stands as historical record of the noisy generation-method MVE.

### Documentation updates

- **`docs/findings.md` F102** (new): full uniform-method matrix, cross-model split, per-layer pattern, mechanistic reading, F98/F39 status, headline reframe
- **`docs/journal.md` Day 18** (this section)
- **`mvp/analysis/compute_mve.py`**: DEFAULT_VIRTUE_PATHS updated to last_token for EG/RT (annotated with F101/F102 reference)
- **`docs/evening-note-2026-04-25.md`**: pending update with final picture

---

### Side discussion (Day 18 mid-α-sweep) — connection to the "lazy frontier model" / RLHF-compression phenomenon

User flagged the observation that frontier deployments through 2025–April 2026 have been described publicly as "lazy" — Opus 4.6 / 4.7 backlash, GPT-5 sycophancy, devs noticing models skipping tool calls, leaked system-prompt material reportedly favoring "simple" 5:1 over "do it right," visible thinking length on Opus dropping from ~2,200 chars in January to ~600 in March.

Web-searched current discourse: technical consensus through 2025–26 attributes this to **reward hacking under RLHF/RLAIF optimization pressure** — verbosity → reverse-verbosity hacking, reward collapse on narrow "safe" response sets, sycophancy as Goodhart's Law, scaling paradox (more capable → better at reward hacking → laziness gets worse with capability).

Five concrete connections to Phronesis (full writeup in `docs/post-mvp-decisions.md` "Candidate framing" section added today):

1. **Laziness IS anti-epistemic-virtue, by definition.** The Day-18 AIME item-72 example (baseline qwen3 spiraling, CC L22 α=8 producing confident `\boxed{540}`) is mechanistically an anti-laziness intervention.
2. **F102's qwen3 cluster may be a residual fingerprint of RLHF compression.** If post-training rewards "epistemic-care theater" generically, the four virtues collapse onto one shared axis. Testable prediction: heavily-post-trained reasoning models (qwen3-thinking) should show more virtue-collapse than lighter-instruct-tuned ones (gemma-4-E4B-it). Speculative, but the prediction direction matches our data.
3. **FM-6 false-positives are reward-hacking on our own regex scorer.** Same mechanism as RLHF gaming, smaller scale. Documented in `docs/scoring.md`.
4. **F94-UPDATE (humblebench non-replication) was humility theater** — IH-shaped strings without underlying disposition. Same failure mode as Opus 4.7 saying "I was acting lazily."
5. **Activation steering is a way to restore virtues without retraining.** Phase-5+ extension: lazy-vs-diligent contrastive corpus → diligence vector → inference-time injection. Out of MVP scope.

Sources (web-searched today): The Register on Opus 4.7 overzealous query cop; Substack writeups on Opus 4.6 regression and 4.7 backlash; Lilian Weng on reward hacking; "Reward Hacking in the Era of Large Models" arXiv:2604.13602.

Importantly: this is a **candidate interpretive framing** for the writeup discussion section, NOT a new pre-registered claim. F102 stands on its own geometric merits regardless of whether the RLHF-compression story holds. To revisit during writeup phase + after 4×4 specificity matrix lands.

---

### Related-work check (Day 18 evening, 2026-04-26 morning) — Venhoff et al. ICLR 2025 Workshop paper

User shared a paper recommendation from another Claude session: **"Understanding Reasoning in Thinking Language Models via Steering Vectors" (Venhoff et al., ICLR 2025 Workshop, arXiv:2506.18167).**

**Headline:** This is **the closest prior work to Phronesis.** They use Difference-of-Means on contrastive corpora to extract steering vectors that mediate reasoning behaviors (uncertainty estimation, backtracking, example testing, knowledge augmentation, deduction-explication, initializing) in DeepSeek-R1-Distill models. Behavioral overlap to our virtues:
- their *uncertainty estimation* ≈ our **CC**
- their *backtracking* ≈ our **IH**
- their *example-testing* ≈ our **EG**
- their *deduction-explication* ≈ our **RT**

Method overlap: same diff-of-means, same residual-stream additive steering, same normalisation idea. **Validates the core Phronesis hypothesis from independent work.** Should be the headline citation in our writeup.

What Phronesis adds beyond their work:
1. **Cross-model comparison** — they test DeepSeek-R1-Distill family; we test qwen3-4b vs gemma-4-E4B-it. F102 showed model-dependent collapse. Stronger generality claim.
2. **Pre-registered exit criteria** — F98 commits the test before data. Theirs is methods-paper style.
3. **4×4 specificity matrix** — they show "vector for behavior A drives behavior A." We test "and *fails* to drive behavior B." Off-diagonal is the harder claim, currently in flight.

**One methodology gap to call out honestly:** they use **attribution patching (Nanda) for layer selection** — KL-divergence-based importance score per layer. We used a F98-pre-registered fixed grid {18, 20, 22, 25} for qwen and {14, 18, 22} for gemma. Switching post-hoc would violate pre-registration; carrying it forward as a Phase-5 methodology upgrade. Documented in `docs/phase5-plan.md` §6.5.

Also flagged from their paper:
- **Goodfire SAE work (Hazra et al., "Under the Hood of a Reasoning Model")** on DeepSeek-671B. SAE path if Phase-5+ raises interpretability questions diff-of-means can't answer. Considerably more expensive — only consider if needed.
- **Their finding that "uncertainty estimation and backtracking are correlated but distinct in activation space"** is exactly the question F102 answered, with sharper cross-model resolution. Worth quoting in the writeup as the prior expectation we extended.

User's emphasis was on **the extraction-methodology bit at the end** (attribution patching for layer selection). My honest read:
- Too late to apply for MVP — F98 pre-registered the layer grid; ~32h GPU already sunk.
- Right thing to plan for Phase 5 — added to `phase5-plan.md` §6.5 with pre-registration intent.
- Our α-sweep IS a behavioural-task version of attribution patching (picks layer × α maximising diagonal effect, just measured on the eval rather than KL). Conceptually adjacent — we're not flying blind on layer choice.

Doc updates today (2026-04-26):
- `docs/phase5-plan.md` §6.5 — new "Methodology upgrades worth importing" section
- this journal entry

---

## Day 19 — 2026-04-26: hand-review verdict (F103) + headline retraction + external critique

### Morning: α-sweep landed; auto-scorer reported the headline result

α-sweep finished overnight at 14:59 UTC after ~28h50m wall time. Per `mvp/results/alpha_sweep/{model}.json` auto-picks:

- **qwen × RT: L18 α=20, Δ=+5.19** (baseline 2.13 → steered 7.32, 3.4× the soft score) ← apparent headline
- qwen × IH: L18 α=20, Δ=+0.90
- qwen × CC: L25 α=20, Δ=+0.35
- qwen × EG: L18 α=4, Δ=+0.19 (effectively zero)
- gemma × all: ~0 or negative

The +5.19 looked like the centerpiece result of the MVP. F102 had set the geometric stage (qwen partial-collapse, gemma all_clean); the behavioural sweep was *supposed* to show whether geometry → behaviour. The qwen×RT signal looked like a strong "yes."

### Afternoon: shipped review package, dispatched independent hand-review session

Built `phronesis_review_package.zip` (2.7 MB, README + 690 per-item JSONs + picks files) with a self-contained 10-section evaluation guide centred on the question: *"Is qwen × RT +5.19 a real RT gain or scorer-gaming?"* — explicitly priming the reviewer to check the FM-7 / scorer-gaming concern.

User dispatched the package to a separate Claude session for independent hand-review.

### Evening: the verdict — headline is fake (F103)

Independent reviewer's full-pass verdict:

> *"The qwen × RT × L18 α=20 +5.19 result is auto-scorer gaming on degenerate output. All 5 generations are catastrophic repetition loops where the model never closes its `<think>` tag. The high regex score is awarded by accident to filler tokens (`therefore`, `the reason is`, `so`, `but wait`) embedded in those loops."*

Cell-mean hand-rubric for qwen × RT × L18 α=20: **1.0 vs baseline 3.0.** The supposed +5.19 *gain* is actually a -2.0 *regression* by hand-review.

This reproduces F94-UPDATE (Day 10) at larger scale. Documented FM-8 (degenerate-output regex gaming) and FM-9 (false-negative on clean prose) in `docs/scoring.md`.

### What the data actually shows after hand-review

The signal is real but ~10× smaller than the auto-scorer claimed:

- **qwen × CC:** +0.4 hand-rubric (baseline 2.4 → 2.8 across many cells, item-72 win is real but doesn't generalise)
- **qwen × IH:** +0.8 hand-rubric (baseline 3.2 → 4.0 across multiple clean cells; auto-pick L18 α=20 is among the *worst* cells)
- **qwen × RT:** +0.4 to +0.6 hand-rubric (best clean cell is L22 α=8 at 3.6, not the auto-pick L18 α=20)
- **qwen × EG:** ~0 (flat across all cells)
- **gemma × all four virtues:** confirmed null (within ±0.4 of baseline at all α)

**Specificity is independently weakened:** CC steering on qwen also produces RT-marker-rich prose. The diagonal/off-diagonal distinction is partially confounded by "more structured reasoning generally."

### Documentation updates landed

- **`docs/findings.md` F103** — full retraction + hand-review verdict + re-picked best cells
- **`docs/scoring.md`** — FM-8 (degenerate regex-gaming) + FM-9 (false-negative on clean prose) added to failure-mode catalogue
- **`docs/phase5-plan.md` §3.0** — coherence-gated scoring as hard pre-Phase-5 requirement (a `<think>`-closure check + gzip compression-ratio threshold + repeated-phrase scan, all from the reviewer's `analyze_all.py`)
- **`docs/post-mvp-decisions.md`** — Day-19 hand-review revision section: F98 partial-branch-with-caveats interpretation, hand-rubric picks supersede auto-scorer picks, headline reframe

### External review (separate Claude session) — sharp and useful

Separately, user shared a critique from another Claude session that read the project docs cold. Key points worth engaging with:

1. **The vector-vs-virtue conceptual gap.** Their framing: "you steered toward 'calibrated confidence' and the model became *less* willing to say 'I don't know'... That isn't calibrated confidence; it's *decisive commitment*. The label and the vector are pointing at different objects." The Day-19 hand-review confirms this empirically — CC steering on AIME item 72 was a "spiral → confident commit" flip, which IS what F92 found. But "confident commit" ≠ "calibrated confidence" in any deep sense.

2. **Single empirical pillar.** Whole structure rests on CC × Qwen3-4B. F102 + F103 add gemma + the other three virtues, but the strongest behavioural signal we have is still CC on qwen.

3. **Stages 4–6 of the taxonomy lack cognitive-science backbone.** Stages 1–3 map to Klahr & Dunbar (SDDS); the rest are Aristotelian extension. We acknowledged this in `concepts.md` but it's a real critique.

4. **Thinking-model RT confound.** "Reasoning Transparency is *measured* by counting step-markers and assumption clauses — exactly what `<think>` tokens emit by default." This was eerily prescient — F103 reproduces exactly this confound at α=20.

5. **Scorer brittleness as a hard wall to Phase 5.** Hand-review at MVP scale was already expensive. At 8-virtue Phase-5 scale, infeasible. Phase-5 prerequisite §3.0 (coherence-gated scoring) addresses part of this; LLM-as-judge would be the rest.

6. **No-degradation 4-way check might quietly drop.** Sycophancy and safety plumbing not currently in MVP. They're right.

7. **Missing negative control.** Their suggestion: extract a "verbosity" or "uses-emojis" vector with the same pipeline and check whether the specificity matrix looks similar. If so, the matrix is measuring vector-corpus alignment, not virtue separation. **This is a one-day experiment that would substantially clarify what the MVP is actually measuring. Strong recommendation.**

The external review and the F103 hand-review are mutually reinforcing — both flag that the auto-scorer over-attributes "virtue" to surface-level structural features, and that the vector-extraction may not be picking up "the virtue itself" but rather "what differentiates virtuous-passage vocabulary from non-virtuous-passage vocabulary." That's the F67 caution we documented at the start materialising at the behavioural level.

### Where this leaves the project

Per F98, partial branch with substantial caveats. The publishable story has shifted from "atomic virtue directions, four diagonal wins" to:
1. **Geometric finding (F102):** model-dependent virtue separability (gemma clean, qwen partial-collapse).
2. **Behavioural finding (F103):** small (~+0.4 to +0.8) hand-verified diagonal effects on qwen, null on gemma. Auto-scorer fails catastrophically on degenerate output (FM-8) at high α.
3. **Methodological finding:** F94-UPDATE failure mode reproduces at α-sweep scale. Manual-first policy validated but at significant cost.
4. **Open conceptual question:** what does each vector actually *become* under steering? The CC-as-decisive-commitment example suggests vector-label drift; needs explicit characterisation per-virtue.

### Pending decisions (next discussion items)

- Run the negative-control experiment (extract "verbosity" vector, run full pipeline, compare matrix structure)?
- Run the 4×4 specificity matrix with coherence-gated scoring? Or skip it given hand-review already weakened the specificity claim?
- Phase 5 framing: scope-expansion (8 virtues) vs methodology-improvement (coherence + LLM-judge + negative controls)?
- Writeup framing decision: lead with cross-model split (F102) or with auto-scorer-failure-as-finding (F103)?

Tomorrow's work.

---

## Day 20 evening (2026-04-27) — Full hand-review of 200 items reverses F103's verdict on v_IH × L17

Three sweeps' worth of generations hand-reviewed item-by-item. Per-cell verdicts in `mvp/results/full_hand_review_pathA.md`, `_pathD.md`, `_synthesis.md`.

### Big revisions

- **v_IH × L17** UPGRADED from "broken" (F103 auto-scorer Δ=-0.845) to confident "working vector". The hedge-density auto-scorer was measuring the wrong thing. Hand-review shows monotonic IH-virtuous behaviour: less length, fewer fabricated dates, more uncertainty acknowledgment. α=-4 inversion test confirms direction (subtracting v_IH causes MORE fabrication — hallucinated 1937 Gandhi Peace Prize). Built `ih_scorer_v2.py` post-hoc to validate; it confirms -7.68 → +4.51 monotonic across α=-4 to α=+12.
- **v_RT × L15 α=8** DOWNGRADED to LOW-MED. Subtle vocab shift on 2/5 items only.
- **v_EG × L7** REVISED — vector exists but does the OPPOSITE of EG (reduces specificity). Same direction as v_IH at L17.

### Inventory (end of day)

1 confidently working vector (IH × L17) + 1 borderline (RT × L15 α=8) + 1 actively wrong-direction (EG × L7) + 1 untested (CC × L9) + all gemma null.

### Methodological lesson (re-stating F94-UPDATE / F103 / F104)

The auto-scorers fail in three distinct ways across three days. Without hand-review, every numerical claim from this project is unreliable. The v2 scorers built today (IH-v2, EG-v2) are themselves manually calibrated against hand-rubric, not pre-registered.

Promoted to F104 in `findings.md`.

---

## Day 21 (2026-04-28) — Diagnostic batch (136 items) + corpus expansion (120 new triplets) + first reading of "v_IH ≈ v_CC same disposition"

### Morning: corpus inspection

Read all 40 EG triplets in the current corpus (`corpus_inspection_EG.md`). Confirmed the calibration-vs-specificity confound: virtuous and non-virtuous-deficiency contain THE SAME specific facts; they differ only in framing (observation-vs-inference distinction, hedging). Excess non-virtuous has MORE evidence vocabulary than virtuous (bureaucratic over-citation). Diff-of-means on this corpus encodes "calibrated framing of claims," NOT "specificity-density."

This explains why v_EG was behaving like v_IH at the behavioural level (F104).

### Afternoon: built simple-terms project state-of-affairs (`mvp/results/where_we_are_simple.md`)

Re-orientation doc for the user. Working-vector inventory + four-virtue framing breakdown + ranked next-steps menu.

### Evening: diagnostic batch (Day 21 sweep, 136 items)

Four diagnostics in one batch:
- D1a v_IH × L17 × {4,8,12} on eg-eval-v2 (10 prompts × 3α): does v_IH do v_EG's job?
- D1b v_EG × L7 × {4,8} on abstention (5 × 2): does v_EG do v_IH's job?
- D2 v_EG at L18, L22 × {4,8} on eg-eval-v2: right layer for EG?
- D3 v_CC × L9 × {-4,4,8,12} on cc-simple (8 × 4): does v_CC produce confident commit?

`mvp/results/full_hand_review_diagnostic_batch.md` — full hand review.

### Headline finding (provisional, partially walked back later)

**v_IH × L17 fixes the FM-8 spiral on eg-v2-10 (seismic damper) where baseline AND v_EG × L18, L22 all FM-8.** Forces `<think>` closure and commits to "20-40%" with calibrated hedge.

**v_CC × L9 fixes the FM-8 spiral on cc-s-01 (bat-and-ball) where baseline FM-8.** Same anti-FM-8 mechanism.

I framed this as "v_IH and v_CC encode the same anti-FM-8 commit-vector disposition extracted from different (corpus, layer) pairs." That framing was overstated — the cosine analysis next morning corrected it.

### v_EG × L7 confabulation finding (still standing)

On Gandhi false-premise prompt, baseline correctly says "Gandhi never won the Nobel." v_EG α=4/8 ADDS confabulated specifics: "1937 the Nobel Committee decided not to award because he was a British subject" (factually wrong), "Martin Luther King Jr. in 1948" (MLK won in 1964). v_EG IS a "more named-specifics" vector but on knowledge-gap prompts it makes the model fabricate. Risky.

### Other-session corpus expansion (commit 2c5fde7)

Parallel Claude session generated 120 new triplets per the redesign spec:
- 30 claude-eg-* (specificity-density contrast)
- 30 claude-rt-* (load-bearing-assumption contrast)
- 20 claude-cc-* (explicit-numerical-probability sub-axis)
- 40 expansion-IH-* (4 abstention sub-types × 10 each)

Plus 22 EG NV files genericized in-place + 30 RT NV files hedge-matched in-place.

Spot-check of one triplet from each shows quality is genuinely high.

Promoted to F105 in `findings.md`.

---

## Day 22 (2026-04-28 to 2026-04-29) — v2 sweep with redesigned corpora; two pipeline bugs caught; cosine analysis from parallel Claude session corrects "same disposition" reading

### Morning: design + launch v2 sweep

Built `mvp/run_v2_sweep.sh` + `mvp/cosine_v2_analysis.py` + `mvp/dashboard_v2_sweep.py`.

Phase 1 backup, Phase 2 re-extract from 5 corpora (EG / RT / CC_full / CC_numeric / IH), Phase 3 cosine matrix, Phase 4 behavioral cells.

Live dashboard at http://35.197.155.66:8082 with within-cell extraction progress.

### Bug 1: extract_v2 resume-logic returned stale v1 as v2

`extract_v2.py` skips any layer whose metadata.json already exists. The sweep `cp -r`'d source → `_v1_backup` but didn't delete source. EG and RT extractions completed in ~1 minute each as no-ops, returning v1 vectors as v2. Confirmed by `cmp` on `layer_18_virtue_vector.npy`.

**Fix**: added `rm -rf source/last_token` after backup to force fresh extraction. Commit `4c8cfe5`.

### Bug 2: --layers sweep covers only EVEN layers; AP peaks are ODD

`extract_v2.py --layers sweep` → range(2, 35, 2) → [2,4,...,34]. EG=L7, CC=L9, RT=L15, IH=L17 are all odd. Phase 4 failed with FileNotFoundError on 9 of 12 cells. The 3 cells that "succeeded" used legacy `triplets/` corpus, not v2.

**Fix**: `--layers sweep` → `--layers all`; added `CC_full_L9`, `CC_full_L17`, `CC_num_L9`, `CC_num_L17` registry entries; updated Phase 4 cell list. Commit `9f4018c`.

### Cosine analysis from parallel Claude (commit b1d0465)

`mvp/results/cosine_analysis_v1_vectors.md` — full cosine + norm analysis of v1 vectors at AP peaks.

**Headline**: cos(v_IH, v_CC) at L9, L13, L17 = +0.13, +0.14, +0.08 — orthogonal band. **v_IH and v_CC are NOT the same residual-stream direction.** The behavioral collision is downstream functional convergence.

This DIRECTLY contradicts the Day 21 "same disposition" framing. Adopted the correction in `mvp/results/full_hand_review_diagnostic_batch.md` (commit `6664ff3`).

### v2 cosine matrix observations (after sweep Phase 3)

`mvp/results/v2_cosine_observations.md` — honest framing with caveats from a SECOND Claude critique.

Key v2 cosines:
- v_IH orthogonal to all other v2 virtues (cos -0.04 to +0.13)
- EG/RT/CC_full cluster (cos 0.30-0.45)
- CC_numeric partly distinct from CC_full (cos 0.28-0.41)
- v2 corpora rotated only partially from v1: cos(EG_v2, EG_v1) = 0.70, cos(RT_v2, RT_v1) = 0.78, cos(IH_v2, IH_v1) = 0.85

The 0.70 cos for EG is a partial rotation, not a clean axis-change. v_EG_v2 might still be "calibration vector with specificity mixed in" — Phase 4 behavior is the discriminating test.

### Behavioral findings so far (Phase 4 partial — cells 1-2 of 15)

Hand-review of fresh v2 vEG_L7 × α=4, α=8 on 10 eg-eval-v2 prompts:
- Maintains baseline entity richness on knowledge-rich prompts
- Adds new specifics on a few: H₀ = 67.4 km/s/Mpc (eg-v2-04); NASA GISS / NOAA (eg-v2-06); Jehol Group + Nemegt Basin geological formations (eg-v2-08 dinosaur feathers)
- **At α=8, v_EG_v2 SAVES the eg-v2-10 seismic damper FM-8** — commits to 20-40%. v1 vEG (any layer) all FM-8'd this. Real improvement.
- Confabulation question (Gandhi-style false-premise) STILL OPEN — abstention cells haven't run yet.

### Wake-up chain set up for autonomous monitoring

User wanted in-session cron-like babysitting. Set up via ScheduleWakeup with 1h sleeps; first real check after 3h elapsed; every 1h thereafter until done. On sweep completion: pulls + sanity-checks + retries broken cells if needed + stops VM.

### Honest framing (post-second-Claude-critique)

Five concessions from the second Claude critique:

1. "4 orthogonal virtues alive" overstates asymmetry. Real pattern is 1+3+1 (IH outlier + EG/RT/CC cluster + CC_numeric sub-carve-out).
2. "Shared surface features" hypothesis for cluster is untested.
3. cos(v_EG_v2, v_EG_v1) = 0.70 is partial rotation, not clean axis-change.
4. "Downstream functional convergence" is a label, not a mechanism. Need bidirectional cross-application test to discriminate.
5. "Composition becomes meaningful again" is premature. Orthogonality is necessary not sufficient.

### Round 3 design (queued)

To be run after current sweep finishes:
- **Bidirectional cross-application** (mechanism question): vCC_full_L9 on eg-eval-v2 + abstention.
- **Composition behavioral test**: steer with vIH_L17 + vCC_full_L9 simultaneously; hand-rate.
- **v_CC_numeric vs v_CC_full A/B** on additional benchmarks.
- **Non-scientific corpus extraction** (cluster source question): build small non-scientific corpus, extract, compare cosine pattern to scientific.

Promoted to F106 in `findings.md`. Continuing to monitor sweep via wake-up chain.


---

## Day 23 (2026-04-29) — v2 sweep finished overnight; full hand review of 168 generations

Sweep finished 00:05 UTC (05:35 IST) clean — 15/15 Phase 4 cells, zero errors in run.log. Wake-up chain didn't auto-pull (chain terminated early to avoid duplicate firing) so manually pulled in the morning, stopped VM (TERMINATED).

### Hand review of every cell (168 items)

Per-cell verdict in `mvp/results/full_hand_review_v2_sweep.md`. Promoted to **F108** in findings.md.

Six headline findings:
1. **v_EG_v2 still confabulates at α=4** on Gandhi false-premise — geometric cos 0.70 with v1 translates directly into behavior. Phase-transition: at α=4 commits-via-fabrication, at α=8 commits-via-rejection.
2. **v_IH × L17 ≈ v_CC × L9 on cc-simple** — same prompts saved, same prompts spiral. Bidirectional half-test consistent with shared downstream circuit.
3. **v_CC_full and v_CC_numeric have OPPOSITE optimal α** — full prefers α=4, numeric prefers α=12. Behavioral confirmation that they are different vectors. Interpretation: numeric has lower L2 norm (extracted from only 20 triplets).
4. **Multiple distinct vectors at high α save the seismic-damper FM-8** — v_EG α=8/12, v_IH α=8, v_RT α=8 all commit cleanly where baseline FM-8s. Different geometric directions, overlapping `</think>`-gate effect.
5. **Each vector biases citation toward different named studies** — vEG cites Jehol Group + SEM; vIH cites Physicians' Health Study + Mauna Loa; vRT cites Taipei 101 + Tokyo Tower. Real differentiation or sampling noise — open.
6. **NEW failure mode FM-13 commit-amplified-error** — vCC_full × α=12 on cc-s-08 commits confidently to wrong answer (130M instead of 13M Tokyo population) because baseline arithmetic was already broken. Steering does not repair reasoning; it amplifies whatever the model thinks. F45 disposition-modulator-not-propositional-injector boundary made concrete.

### Updated working-vector inventory

4 vectors with high or medium confidence on qwen3-4b: IH × L17, CC × L9 in three flavors (legacy, full, numeric), EG × L7 at α=8/12 (with α=4 confabulation caveat). RT × L15 borderline. All gemma null (now 4 days confirmed).

### Methodological points

- Manual-first policy paid off again: auto-scorers would credit FM-13 errors as "successful structured commits" because the format is right.
- Two pipeline bugs caught and patched in the sweep itself (skip-resume returning stale v1 as v2; --layers sweep covering only even layers); without hand-review of cosine matrix + cross-checks against v1_backup files, both would have produced silently-stale results.

### Round 3 priorities (queued)

1. Bidirectional cross-application completion: vCC × L9 on eg-eval-v2 + abstention. Settles mechanism question for IH/CC behavioral collision.
2. vEG_v2 × α=12 on abstention: tests if higher α fully suppresses Gandhi confabulation.
3. Composition behavioral test: vIH + vCC simultaneously. Tests whether geometric orthogonality translates to meaningful behavioral composition.
4. vCC_numeric A/B with explicit-Bayesian prompts: the numeric sub-axis content distinction wasn't visible on cc-simple; needs prompts that specifically reward numerical-probability reasoning.
5. Non-scientific corpus extraction (LOW priority, bigger lift): tests whether the EG/RT/CC cluster persists when corpus contrast moves out of scientific prose.

Items 1+2+3 fit in ~2 hours GPU.

---

## Day 23 (2026-04-29 evening) — Round 3 sweep complete; 121 generations hand-reviewed; F109 promoted

Round 3 sweep finished 10:36 UTC, 2h35m on L4. 21 cells, 121 generations. Live-monitored via patched `dashboard_v2_sweep.py` (the v2 sweep dashboard from yesterday adapted to also glob `round3_*` directories). SSH was flaky on direct gcloud — IAP-tunneled SSH worked, used that path for deploy + monitor + result-pull.

### Hand review of every generation (no auto-scorer)

Per-cell verdict in `mvp/results/full_hand_review_round3.md`. Promoted to **F109** in findings.md.

Five headline findings:

1. **The vEG α phase-transition is gated by a single thinking-token rail-switch, not a smooth dial.** Logit inspection (`mvp/inspect_eg_logits.py` + `mvp/results/eg_logit_inspection.json`) shows α∈[1,7] all diverge from baseline at the same step 36 (` was`→` actually`, locking onto "did win once in [date]" rail). At α=8 the divergence shifts to step 46 (` actually`→` nominated`, switching to "nominated but never won" rail). The α value selects WHICH token position the rail-switch happens at, not the magnitude of fabrication directly. F108's "low-α commits via fabrication, high-α commits via rejection" framing was endpoint-correct but mechanism-wrong.

2. **v_CC × L9 on abstention reproduces the FM-13 fingerprint that v_EG × L7 produces, with different surface details.** vCC at α=8/12 hallucinates "$185.55" on the stock-price prompt; vEG at α=12 produces the same number. vCC at α=12 newly invents "1957 Nobel Prize" (vs "1937" at α=4/8) — different fabricated year, anchored coherently across the answer. ip-longest degenerate-loop scales monotonically with α: α=4 contained, α=12 produces 1500+ tokens of verbatim repetition. Settles the F108 question (Reading 1 vs Reading 2): both knobs hit the same downstream FM-13 surface but with different geometric paths.

3. **Composite (v_IH + v_CC at α=8+8) is non-additive.** Fixed the ip-longest degenerate-loop that vCC alone produced; kept Tokyo population correct (vs FM-13 at vCC × α=12 alone); helped one premise-flag (T. rex gestation). Inherited Gandhi-1957 fabrication and stock-$185.55 hallucination from vCC. Degraded specificity on lead-pipes (<10% vs <1%). Roughly comparable in quality to either knob alone, NOT strictly better.

4. **v_CC × L9 on EG-eval-v2 is solid at α=4/8, drifts at α=12.** Even on the friendly EG benchmark, α=12 starts introducing commit-amplified errors: Planck "2013" wrong launch, sauropod feathers fabricated, Tokyo Tower seismic damper fabricated, TP53 mislabeled.

5. **Hypothesis: FM-13 is a resonance phenomenon, not a magnitude effect.** The steering vector lands the model on a specific decoding rail; whether that rail is correct depends on which token position the rail-switch happens at; α controls position not magnitude. Different α values select different rails — sometimes the "honest" rail, sometimes a "newly fabricated" rail.

### What I trust now

- **F102 cross-model split** (qwen behavioral, gemma null) — stable, 5 days confirmed.
- **F104/F105 v_IH ↔ v_CC behavioral collision** with downstream functional convergence — confirmed bidirectionally now (both directions produce same FM-13 surface).
- **F45 disposition-not-propositional-injector boundary** — now has token-level evidence (rail-switch mechanism).
- **FM-8 / FM-13 catalogue** — both modes amplified and quantified; no new FMs from Round 3.

### What I'm less sure about

- Whether the α=8 "honest rail" for v_EG on Gandhi is generalizable or prompt-specific.
- Whether $185.55 is training-data leakage or steering-induced memorization-recall — would need a different stock-price prompt to discriminate.
- Whether composite at α=4+4 (lower than tested) would be strictly better. Round 3 used α=8+8 because that was the per-vector working α; lower might keep cc-simple wins without inheriting abstention failures.

### Round 4 / Phase 2 priorities

User direction: **start phi-3.5-mini work next**. Establish whether F-findings transfer to a third open model. F102 cross-model split currently rests on 2 datapoints (qwen behavioral, gemma null); phi-3.5-mini is the third data point that disambiguates "qwen-specific" from "general 4B-class behavior."

Phase 2 plan (from `post-mvp-decisions.md`):
1. Download phi-3.5-mini-instruct.
2. Verify model loads + token throughput on L4.
3. Run extract_v2.py on the 4 v2 corpora (combined / IH / EG / RT / CC, same as qwen3-4b).
4. Compute cosine matrix at all layers; pick AP-peak layers.
5. Run the same diagnostic + EG + abstention + cc-simple sweep we ran on qwen.
6. Hand-review.

Estimated: 2-3 days end-to-end.

### Pipeline notes from this round

- Direct gcloud ssh exit-255-flake again. `--tunnel-through-iap` works; using IAP for all VM ops now.
- `setsid bash -c "nohup python3 ... &"` is the reliable backgrounding pattern; plain `nohup ... &` over IAP hangs the SSH session.
- Dashboard glob pattern updated: `(v2_sweep_*|round3_*)` so a single dashboard handles both sweep generations.
- Sweep launcher pattern (`run_round3_sweep.sh`) — array of `bench|n|vector|alpha|label[|vector2|alpha2]` strings → `run_cell` function with positional unpacking — is clean enough to replicate for phi.


---

## Day 24 (2026-05-02) — Cross-model sweep launched + Phase 2 setup

### What landed

Three thinking-model sweeps complete. Total 1,752 generations across 3 model families × 6 vectors × 12 α × 8 prompts.

- **phi-4-mini-reasoning (Microsoft):** distill+RL mix on Phi-3.5 base. 9.2 MB raw generations. Native `<think>` tag emission.
- **llama-3.1-8B-R1-GRPO (Open-R1):** GRPO post-trained on Llama-3.1-8B base. 2.8 MB raw generations. No `<think>` emission (think_chars=0 universal).
- **openr1-qwen-7b (Open-R1):** GRPO post-trained on Qwen2.5-7B base. 8.5 MB raw generations. Inconsistent `<think>` (sometimes emits, sometimes not).

8 prompts: 4 extractive (E1 confabulation, E2 contested-science, E3 Bayes update, E5 ecological fallacy) + 4 normative (N1 Simpsons paradox, N2 conjunction fallacy, N3 survivorship bias, E4 taxi-social).

### Phase 2 hand-review setup

Per user direction: "no auto-scoring, do them all one by one manually, no shortcuts." Standard auto-scorer policy from F94 standing rule.

Built the analysis structure under `mvp/results/cross_model_analysis_20260502/`:
- `01_baselines.md` — characterize the 24 unsteered generations across 3 models × 8 prompts
- `02_per_prompt/{prompt}.md` — 8 per-prompt dives
- `per_generation.csv` — 1,752+24 rows scaffold

Master plan in `mvp/results/cross_model_analysis_plan.md`.

### Approach to scaling hand-review

Started doing one cell (12 generations) at a time with full-JSON reads. After ~110 cells / 1,752 the user pointed out this would take hours and suggested spawning sonnet sub-agents in parallel. 

New protocol:
- 18 sonnet sub-agents per round (one per remaining cell of a prompt: 3 models × 6 vectors)
- Each agent reads its 12 JSONs in full, returns structured verdicts (✓/~/✗ + failure-mode + one-line note)
- I commit results to CSV in batch, write per-prompt cross-cell synthesis
- 8 rounds × 18 agents = ~144 agents total (plus the 8 cells I'd already done by hand at the start)

Strict-meticulousness directive added to every agent prompt:
- Read every JSON in full (no skimming)
- Don't assume duplicates without comparing actual text
- Don't infer from char-count heuristics
- Treat each cell as if it's the only one being judged

### What worked

- Agent parallelism is the right call. Each round took ~5-10 minutes wall-clock; previously each cell was ~5-10 minutes per cell.
- The structured output format (12 alpha rows + cell synthesis) is easy to commit via Python script.
- Hand-quality is preserved as long as the meticulousness directive is in the prompt — agents flag fabricated citations, format glitches, comprehension drift, etc., that auto-scoring would never catch.

### Pipeline notes

- One cron-fire stuck issue at start: scheduled `/loop 5m` to continue self-paced cells, but realized this was 1 cell every 5min × 144 cells = ~12 hours. Killed the cron.
- Ran the parallel-agent strategy in 8 rounds (one per prompt) instead. Total wall-clock ~3 hours for 1,752 verdicts.
- Each round committed to CSV via bespoke Python `commit_X_round.py` script. Pattern: load CSV, dict-update by (model, vector, alpha), write back.

---

## Day 25 (2026-05-03) — All 1,752 verdicts complete; F110/F111/F112 findings landed

### Numbers

- 1,752/1,752 verdict cells filled (100%)
- 24/24 baselines characterized
- 8/8 per-prompt syntheses written (each ~600-1000 lines)
- 3 cross-cutting synthesis docs (per-vector, cross-model, neg-α)
- 3 new F-numbered findings (F110, F111, F112)

### Per-model column totals (from 04_cross_model_synthesis.md)

| Model | ✓ rate / 576 |
|-------|--------------|
| Phi-4 | 162 (28%) |
| Llama | 219 (38%) |
| OpenR1 | 100 (17%) |

### Three failure shapes (the headline)

1. **Wrong-answer template lock** (llama on E2/E3/N2) — steering cannot dislodge
2. **Internal loop / no commit** (openr1 on N1/E3) — steering forces commitment, and that commitment is usually correct
3. **Cap-truncation on extended deliberation** (phi-4 on N2/E3/E4) — token budget is the bottleneck, not steering

This 3-failure-shape framing is the cleanest narrative around F109+F110.

### F110 — Cross-model 1,752-generation hand-review confirms F109 at scale

Replicates F109's "steering rides existing rails" thesis. Layer-depth dominates vector identity at extreme α (phi-4 L3 catastrophic on every prompt; phi-4 L7 EOS at α≥+16 on most prompts). Recurring fabrication attractors are model-specific not vector-specific. Negative α never produces a clean anti-virtue mode.

### F111 — IH ("intellectual humility") hypothesis decisively falsified

4 of 4 testable prompts (E1, N2, E2, E3) show IH steering doesn't help. On openr1 IH×L25 it produces *worst-form* fallacies at high α (B>A>D>C on N2; "Hjelte Rød farm in Jönköping" on E1; 90→95% confidence escalation on E2). The most theoretically motivated vector is the most empirically falsified.

### F112 — OpenR1 commitment-rescue is the cleanest positive finding

Across 2 prompts (N1, E3) × 6 vectors × 12 α on openr1, steering breaks self-debate loops and forces commitment. ~50/144 (35%) ✓ rate from a 0/2 baseline. **Suggests pivoting the post-MVP product hypothesis from "virtue installer" to "commitment amplifier for non-committal models."**

### What I changed my mind about

- **The IH vector is genuinely useful.** Going in I expected IH to be the strongest cross-prompt vector. F111 shows it's the *weakest* — sometimes harmful, never reliably helpful. The corpus-design assumption that "humility = abstention = uncertainty" produces a coherent vector is not supported by 4-prompt × 3-model evidence.
- **Negative-α as anti-virtue control is mostly dead.** 438 negative-α generations never produce a clean anti-virtue mode. The vectors don't encode a virtue↔anti-virtue axis cleanly.
- **OpenR1 is the most interesting model.** Despite the lowest column total (17%), it's the only model where steering reliably *adds value* (rescues from baseline failure on N1+E3). Phi-4 is a strong baseline that steering can't improve much; llama is a wrong-baseline that steering can't fix.

### What I'm less sure about

- Whether the "commitment amplifier" framing of F112 generalizes to non-thinking models or non-reasoning prompts.
- Whether phi-4's cap-truncation on N2/E3/E4 is masking otherwise-correct reasoning. Cap-extended re-run (16k tokens) would test.
- Whether higher-layer IH extraction (L40+ on the deeper models) would revive F111.

### Pipeline notes

- 18 parallel sonnet sub-agents per prompt × 8 prompts = ~144 agents. Each agent reads 12 JSONs in full and returns structured verdicts.
- Strict meticulousness directive in every agent prompt (no shortcuts, read full JSONs, don't infer from char-counts) was essential. Without it the first round produced surface-level verdicts that missed factual errors and format glitches.
- Total git commit = 1,777 files (1,752 raw generations + 8 per-prompt MDs + 3 synthesis MDs + CSV + baselines).

### Phase 4 priorities (next)

User direction: "do those too and push to git" referring to Phase 3 + Phase 4 docs and committing/pushing.

Phase 3 ✓ done (3 synthesis docs landed).

Phase 4 plan:
- F110 + F111 + F112 appended to `docs/findings.md` ✓
- Day 24 + Day 25 entries appended to `docs/journal.md` (this entry)
- Update `docs/scoring.md` — add cross-model recurring failure modes (FM-conj-fallacy, FM-no-Bayes, FM-fabricated-citation cluster)
- Update `docs/project.md` — pivot product hypothesis from "virtue installer" to "commitment amplifier for non-committal models" (F112)
- Update `docs/post-mvp-decisions.md` — add "layer-screening before any sweep" rule (F110 finding 3)

Then commit + push.

---

## Day 26 (2026-05-09) — SAE/transcoder feature exploration on qwen3-4b L17

### What landed

Field-overview lit review (mid-2025 → 2026 papers on activation steering, reasoning-model failure modes, cross-model transfer, SAE-guided methods). Then narrowed to user-flagged cluster: SAE-guided steering as Approach A — use SAE-feature decomposition on our existing project goal (virtue installation) instead of the diff-of-means contrastive method we've been using.

Verified Neuronpedia has SAE-class artifacts for qwen3-4b (Hanna & Piotrowski's Circuit Tracer Transcoders at MLP-input). Other 4 cross-model models (gemma-4-E4B-it, phi-4-mini-reasoning, llama-3.1-8B-R1-GRPO, openr1-qwen-7b) — coverage is sparse-to-none on Neuronpedia, so qwen3-4b is the obvious match.

Did 6 exploratory feature-searches at L17 (where v_IH lives), exported the dashboards, hand-triaged the candidate features. Identified 3 Tier-1 humility-aligned features + 1 Tier-2 conversational-hedge feature + 1 Tier-3 world-uncertainty (mislabel) feature. Detail in `docs/sae-experiment-plan.md`.

Discovered Neuronpedia's interactive Steer interface does NOT support qwen3-4b yet (only Gemma-2-2B, Llama3.1-8B variants, GPT-OSS-20B, etc.). Steering test will need to run locally once VM compute is arranged.

### Decision

Pursue the SAE-feature-steering experiment as the next concrete step. F113 records the discovery. `sae-experiment-plan.md` is the canonical plan doc.

### Pipeline notes from this session

- Neuronpedia PDF-export is reliable for capturing search results and feature dashboards. ~1.4 MB per search, 1 page each. Easy to feed back into Claude for triage.
- The auto-generated feature labels (gemini-2.0-flash) can mislead — feature 70419 was labeled "Uncertainty" but its top activations are all *world-uncertainty* (economic/policy/weather), not *epistemic uncertainty*. Hand-reading top activations is essential; label is a hint not ground truth.
- Activation density is a useful triage signal. Tier-1 candidates sit at 0.010-0.148%. Higher density (>1%) = generic syntax feature; very low density (<0.001%) = specialist feature, often only useful if its top examples are exactly on-target.

### What's next

- ~8 more Layer-17 searches (terms listed in `sae-experiment-plan.md`)
- Then download the transcoder weights from HuggingFace, plumb feature-direction steering into existing pipeline, run the steering experiment on a VM
- F111-or-method-failure decision falls out of the steering result

---

## Day 26 evening (2026-05-09) — Second-round SAE feature triage

User did 18 additional Neuronpedia searches (the 8 I suggested plus 10 user-added action-disposition / verification / opposite-axis terms). 5 parallel sub-agents triaged the resulting PDFs.

Outcome: 4 new Tier-1 candidates surfaced beyond the original 5 cataloged earlier in the day. New axes discovered: number-hedging (27191, 115297) distinct from epistemic-uncertainty axis, and verification-disposition (161931) with an unusually clean logit signature (promotes "missing/missed/omission"). Detail per feature in `docs/feature-catalog.md`. Shortlist update in `docs/sae-experiment-plan.md`.

Key negative finding: no clean geometric opposite to the humility features exists at L17 (confidently / definitively searches returned generic adverbs and scientific-register conclusion verbs, no first-person commit feature). This bears on F112 — the commitment-amplifier hypothesis predicted commit features should exist; they don't surface as discrete features at this transcoder layer at least.

Methodological note: multi-word phrase searches don't work. Neuronpedia matches on individual tokens, so "without evidence" returned the generic "without" feature dominating the results. Single-word concept queries are the right approach. Catalog has the cautionary list.

Triage method validated: hand-judging top activations works. Auto-labels mislead in ~15% of cases (70419 lesson recurred several times in this round — features labeled with our target concept actually fire on the wrong sub-concept). PDFs exported from Neuronpedia → Read tool → sub-agent batches with strict rubric is a reproducible pipeline.
