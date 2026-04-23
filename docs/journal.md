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
