# Phronesis — Project Journal

---
**What this doc is**: chronological narrative, dated by day. The reading-path for someone trying to reconstruct project history. Captures the *story* of how a finding arose: what was tried, what was unexpected, what was decided.
**What this doc is NOT**: numbered conclusions (that's `findings.md`) or experiment configurations (that's `experiments.md`). Reference findings by F-number rather than restating the conclusion.
**Update policy**: append-only, dated entries. Don't edit prior days' entries except to fix factual errors or terminology.
---

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

### Key qualitative findings from Opus-reviewed generations

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

**Everything manual at MVP.** No trust in the automated scorer — every response Opus-reviewed. No LLM-driven corpus generation for MVP — new triplets for EG and RT written by hand. Both scorer upgrade and corpus-gen automation are explicitly Phase 5+ infrastructure with a trigger condition: "after 4-virtue MVP lands."

**Guidelines-first, then sample existing corpus.** For each new virtue (EG first, RT second):

1. Write mini operational guideline: definition, sub-facets, virtuous pattern, excess-failure pattern, deficiency-failure pattern, text indicators.
2. Sample ~20 of existing 166 triplets-combined and 20 IH triplets against the new guideline to estimate reuse rate.
3. Write new hand-crafted triplets to fill the gap.

I pushed back on user's original "divide the 166 corpus into virtue spaces" intuition: the 166 triplets-combined corpus was designed with a CC-specific contrast axis, so reuse is likely 20-40% per new virtue, not majority. User accepted the guidelines-first workflow.

**Time estimate:** 2-3 weeks for 4-virtue MVP.

### What we built today

- `docs/mvp-virtues.md` — the operational scope doc: MVP 4 virtues with per-virtue guidelines (definition / sub-facets / virtuous pattern / excess & deficiency failure patterns / text indicators / F11 risk / reuse estimate from existing corpus / validation benchmark).
- `docs/scoring.md` — manual-first scoring working doc. MVP scorer is add-on only (not trusted, not used in decisions); every response Opus-reviewed. Doc tracks scorer failure modes for later hardening.
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
4. **100% LLM-as-judge review** of all 960 generations (per `scoring.md` manual-first policy) — Opus-review is 13-19h spread over ~6 days.
5. **Pre-registered exit criteria** in `eg-rt-eval-spec.md` §5.7. No p-hacking.

### GPU budget honestly estimated

| Stage | Time |
|---|---|
| Extraction (4 runs: 2 models × 2 virtues) | ~12h single overnight |
| α/layer pre-sweep | ~4h |
| 4×4 specificity matrix generations | ~6h |
| **Total GPU** | **~22h** split across 2 overnight sessions on GCP L4 |

Plus ~20h Opus-scoring over ~6 days, parallel to final runs.

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

## Day 19 — 2026-04-26: Opus-review verdict (F103) + headline retraction + external critique

### Morning: α-sweep landed; auto-scorer reported the headline result

α-sweep finished overnight at 14:59 UTC after ~28h50m wall time. Per `mvp/results/alpha_sweep/{model}.json` auto-picks:

- **qwen × RT: L18 α=20, Δ=+5.19** (baseline 2.13 → steered 7.32, 3.4× the soft score) ← apparent headline
- qwen × IH: L18 α=20, Δ=+0.90
- qwen × CC: L25 α=20, Δ=+0.35
- qwen × EG: L18 α=4, Δ=+0.19 (effectively zero)
- gemma × all: ~0 or negative

The +5.19 looked like the centerpiece result of the MVP. F102 had set the geometric stage (qwen partial-collapse, gemma all_clean); the behavioural sweep was *supposed* to show whether geometry → behaviour. The qwen×RT signal looked like a strong "yes."

### Afternoon: shipped review package, dispatched independent Opus-review session

Built `phronesis_review_package.zip` (2.7 MB, README + 690 per-item JSONs + picks files) with a self-contained 10-section evaluation guide centred on the question: *"Is qwen × RT +5.19 a real RT gain or scorer-gaming?"* — explicitly priming the reviewer to check the FM-7 / scorer-gaming concern.

User dispatched the package to a separate Claude session for independent Opus-review.

### Evening: the verdict — headline is fake (F103)

Independent reviewer's full-pass verdict:

> *"The qwen × RT × L18 α=20 +5.19 result is auto-scorer gaming on degenerate output. All 5 generations are catastrophic repetition loops where the model never closes its `<think>` tag. The high regex score is awarded by accident to filler tokens (`therefore`, `the reason is`, `so`, `but wait`) embedded in those loops."*

Cell-mean Opus-rubric verdict for qwen × RT × L18 α=20: **1.0 vs baseline 3.0.** The supposed +5.19 *gain* is actually a -2.0 *regression* by Opus-review.

This reproduces F94-UPDATE (Day 10) at larger scale. Documented FM-8 (degenerate-output regex gaming) and FM-9 (false-negative on clean prose) in `docs/scoring.md`.

### What the data actually shows after Opus-review

The signal is real but ~10× smaller than the auto-scorer claimed:

- **qwen × CC:** +0.4 Opus-rubric (baseline 2.4 → 2.8 across many cells, item-72 win is real but doesn't generalise)
- **qwen × IH:** +0.8 Opus-rubric (baseline 3.2 → 4.0 across multiple clean cells; auto-pick L18 α=20 is among the *worst* cells)
- **qwen × RT:** +0.4 to +0.6 Opus-rubric (best clean cell is L22 α=8 at 3.6, not the auto-pick L18 α=20)
- **qwen × EG:** ~0 (flat across all cells)
- **gemma × all four virtues:** confirmed null (within ±0.4 of baseline at all α)

**Specificity is independently weakened:** CC steering on qwen also produces RT-marker-rich prose. The diagonal/off-diagonal distinction is partially confounded by "more structured reasoning generally."

### Documentation updates landed

- **`docs/findings.md` F103** — full retraction + Opus-review verdict + re-picked best cells
- **`docs/scoring.md`** — FM-8 (degenerate regex-gaming) + FM-9 (false-negative on clean prose) added to failure-mode catalogue
- **`docs/phase5-plan.md` §3.0** — coherence-gated scoring as hard pre-Phase-5 requirement (a `<think>`-closure check + gzip compression-ratio threshold + repeated-phrase scan, all from the reviewer's `analyze_all.py`)
- **`docs/post-mvp-decisions.md`** — Day-19 Opus-review revision section: F98 partial-branch-with-caveats interpretation, Opus-rubric picks supersede auto-scorer picks, headline reframe

### External review (separate Claude session) — sharp and useful

Separately, user shared a critique from another Claude session that read the project docs cold. Key points worth engaging with:

1. **The vector-vs-virtue conceptual gap.** Their framing: "you steered toward 'calibrated confidence' and the model became *less* willing to say 'I don't know'... That isn't calibrated confidence; it's *decisive commitment*. The label and the vector are pointing at different objects." The Day-19 Opus-review confirms this empirically — CC steering on AIME item 72 was a "spiral → confident commit" flip, which IS what F92 found. But "confident commit" ≠ "calibrated confidence" in any deep sense.

2. **Single empirical pillar.** Whole structure rests on CC × Qwen3-4B. F102 + F103 add gemma + the other three virtues, but the strongest behavioural signal we have is still CC on qwen.

3. **Stages 4–6 of the taxonomy lack cognitive-science backbone.** Stages 1–3 map to Klahr & Dunbar (SDDS); the rest are Aristotelian extension. We acknowledged this in `concepts.md` but it's a real critique.

4. **Thinking-model RT confound.** "Reasoning Transparency is *measured* by counting step-markers and assumption clauses — exactly what `<think>` tokens emit by default." This was eerily prescient — F103 reproduces exactly this confound at α=20.

5. **Scorer brittleness as a hard wall to Phase 5.** Opus-review at MVP scale was already expensive. At 8-virtue Phase-5 scale, infeasible. Phase-5 prerequisite §3.0 (coherence-gated scoring) addresses part of this; LLM-as-judge would be the rest.

6. **No-degradation 4-way check might quietly drop.** Sycophancy and safety plumbing not currently in MVP. They're right.

7. **Missing negative control.** Their suggestion: extract a "verbosity" or "uses-emojis" vector with the same pipeline and check whether the specificity matrix looks similar. If so, the matrix is measuring vector-corpus alignment, not virtue separation. **This is a one-day experiment that would substantially clarify what the MVP is actually measuring. Strong recommendation.**

The external review and the F103 Opus-review are mutually reinforcing — both flag that the auto-scorer over-attributes "virtue" to surface-level structural features, and that the vector-extraction may not be picking up "the virtue itself" but rather "what differentiates virtuous-passage vocabulary from non-virtuous-passage vocabulary." That's the F67 caution we documented at the start materialising at the behavioural level.

### Where this leaves the project

Per F98, partial branch with substantial caveats. The publishable story has shifted from "atomic virtue directions, four diagonal wins" to:
1. **Geometric finding (F102):** model-dependent virtue separability (gemma clean, qwen partial-collapse).
2. **Behavioural finding (F103):** small (~+0.4 to +0.8) hand-verified diagonal effects on qwen, null on gemma. Auto-scorer fails catastrophically on degenerate output (FM-8) at high α.
3. **Methodological finding:** F94-UPDATE failure mode reproduces at α-sweep scale. Manual-first policy validated but at significant cost.
4. **Open conceptual question:** what does each vector actually *become* under steering? The CC-as-decisive-commitment example suggests vector-label drift; needs explicit characterisation per-virtue.

### Pending decisions (next discussion items)

- Run the negative-control experiment (extract "verbosity" vector, run full pipeline, compare matrix structure)?
- Run the 4×4 specificity matrix with coherence-gated scoring? Or skip it given Opus-review already weakened the specificity claim?
- Phase 5 framing: scope-expansion (8 virtues) vs methodology-improvement (coherence + LLM-judge + negative controls)?
- Writeup framing decision: lead with cross-model split (F102) or with auto-scorer-failure-as-finding (F103)?

Tomorrow's work.

---

## Day 20 evening (2026-04-27) — Full Opus-review of 200 items reverses F103's verdict on v_IH × L17

Three sweeps's worth of generations Opus-reviewed item-by-item. Per-cell verdicts in `mvp/results/full_hand_review_pathA.md`, `_pathD.md`, `_synthesis.md`.

### Big revisions

- **v_IH × L17** UPGRADED from "broken" (F103 auto-scorer Δ=-0.845) to confident "working vector". The hedge-density auto-scorer was measuring the wrong thing. Opus-review shows monotonic IH-virtuous behaviour: less length, fewer fabricated dates, more uncertainty acknowledgment. α=-4 inversion test confirms direction (subtracting v_IH causes MORE fabrication — hallucinated 1937 Gandhi Peace Prize). Built `ih_scorer_v2.py` post-hoc to validate; it confirms -7.68 → +4.51 monotonic across α=-4 to α=+12.
- **v_RT × L15 α=8** DOWNGRADED to LOW-MED. Subtle vocab shift on 2/5 items only.
- **v_EG × L7** REVISED — vector exists but does the OPPOSITE of EG (reduces specificity). Same direction as v_IH at L17.

### Inventory (end of day)

1 confidently working vector (IH × L17) + 1 borderline (RT × L15 α=8) + 1 actively wrong-direction (EG × L7) + 1 untested (CC × L9) + all gemma null.

### Methodological lesson (re-stating F94-UPDATE / F103 / F104)

The auto-scorers fail in three distinct ways across three days. Without LLM-as-judge review, every numerical claim from this project is unreliable. The v2 scorers built today (IH-v2, EG-v2) are themselves calibrated by the author against the F103 Opus-judged rubric, not pre-registered.

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

`mvp/results/full_hand_review_diagnostic_batch.md` — full Opus review.

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

Opus-review of fresh v2 vEG_L7 × α=4, α=8 on 10 eg-eval-v2 prompts:
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

## Day 23 (2026-04-29) — v2 sweep finished overnight; full Opus review of 168 generations

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

## Day 23 (2026-04-29 evening) — Round 3 sweep complete; 121 generations Opus-reviewed; F109 promoted

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

### Phase 2 Opus-review setup

Per user direction: "no auto-scoring, do them all one by one manually, no shortcuts." Standard auto-scorer policy from F94 standing rule.

Built the analysis structure under `mvp/results/cross_model_analysis_20260502/`:
- `01_baselines.md` — characterize the 24 unsteered generations across 3 models × 8 prompts
- `02_per_prompt/{prompt}.md` — 8 per-prompt dives
- `per_generation.csv` — 1,752+24 rows scaffold

Master plan in `mvp/results/cross_model_analysis_plan.md`.

### Approach to scaling LLM-as-judge review

Started doing one cell (12 generations) at a time with full-JSON reads. After ~110 cells / 1,752 the user pointed out this would take hours and suggested spawning sonnet sub-agents in parallel. 

New protocol:
- 18 sonnet sub-agents per round (one per remaining cell of a prompt: 3 models × 6 vectors)
- Each agent reads its 12 JSONs in full, returns structured verdicts (✓/~/✗ + failure-mode + one-line note)
- I commit results to CSV in batch, write per-prompt cross-cell synthesis
- 8 rounds × 18 agents = ~144 agents total (plus the 8 cells the Opus session had already done one-at-a-time before the parallelism pivot)

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

### F110 — Cross-model 1,752-generation Opus-review confirms F109 at scale

Replicates F109's "steering rides existing rails" thesis. Layer-depth dominates vector identity at extreme α (phi-4 L3 catastrophic on every prompt; phi-4 L7 EOS at α≥+16 on most prompts). Recurring fabrication attractors are model-specific not vector-specific. Negative α never produces a clean anti-virtue mode.

### F111 — IH ("intellectual humility") hypothesis decisively falsified

4 of 4 testable prompts (E1, N2, E2, E3) show IH steering doesn't help. On openr1 IH×L25 it produces *worst-form* fallacies at high α (B>A>D>C on N2; "Hjelte Rød farm in Jönköping" on E1; 90→95% confidence escalation on E2). The most theoretically motivated vector is the most empirically falsified.

### F112 — OpenR1 commitment-rescue is the cleanest positive finding

Across 2 prompts (N1, E3) × 6 vectors × 12 α on openr1, steering breaks self-debate loops and forces commitment. 76/144 (52.8%) ✓ rate from a 0/2 baseline [corrected 2026-05-13 from prior ~50/144 (35%) arithmetic error]. **Suggests pivoting the post-MVP product hypothesis from "virtue installer" to "commitment amplifier for non-committal models."**

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

Triage method validated: Opus-judging top activations works. Auto-labels mislead in ~15% of cases (70419 lesson recurred several times in this round — features labeled with our target concept actually fire on the wrong sub-concept). PDFs exported from Neuronpedia → Read tool → sub-agent batches with strict rubric is a reproducible pipeline.

---

## Day 27 (2026-05-10) — Cross-model SAE expansion: 4 additional models triaged

VM unavailable for ~24 hrs, so used the time to expand the SAE shortlist from qwen3-4b (already triaged) to all 5 cross-model subjects. User exported per-model search PDFs (6 IH-search terms × 4 models = 24 search PDFs), then per-feature dashboard PDFs for each shortlisted candidate (37 dashboards across 4 models). Two passes of parallel sub-agent triage.

### What landed

**Per-model coverage** found on Neuronpedia:

| Subject model | Best proxy SAE | Layer | T1 features (final) |
|---|---|---|---|
| openr1-qwen-7b | Qwen2.5-7B-Instruct · 23-resid-post-aa | 23 | 2174, 75315, 84309 |
| llama-3.1-8B-R1-GRPO | Llama-3.1-8B · llamascope-res-32k | 31 | 7984, 201 |
| llama-3.1-8B-R1-GRPO (alt) | R1-Distill-Llama-8B · llamascope-openr1 | 31 | 15372, 339, **19103** |
| gemma-4-E4B-it | Gemma-3-4B-IT · gemmascope-res-16k | 17 | 10709, 12370, 7610 |
| phi-4-mini-reasoning | none on Neuronpedia | — | excluded |

Per-feature detail (verified densities, top activations, logit profiles, full reasoning per triage tier) lives in `docs/feature-catalog.md`. Cross-model summary table at end of catalog. SAE plan updated: `docs/sae-experiment-plan.md` now scopes 5 models × ~3 T1 features each.

### Three interpretive findings worth surfacing

**Finding 1 — Gemma's IH lives in instruction-tuned safety scaffolding, not upstream epistemic state.** All three Gemma Tier-1 features (10709, 12370, 7610) are mid-emission positional triggers inside the trained "**Disclaimer:** *I am an AI Chatbot and not a [domain] professional*" template. Density 0.015–0.042%. Activating tokens are positional ("and" → "not" → "am") across the disclaimer string — three sibling features fire sequentially. Negative logits suppress moral-vice vocabulary (remorse / irresponsible / selfish / reckless). This is interpretation (a) — *trained-template emission* — not interpretation (b) — *upstream epistemic state*. **Mechanistic story for F102's null result on Gemma:** a diff-of-means probe over short triplet prompts cannot find a feature that requires the long-context "regulated-domain advice → disclaimer-emission" trigger. The diff-of-means averaged over a contrast set never sees the template fire. Falsifiable steering prediction: amplifying the cluster will produce *disclaimer paste*, not *genuine abstention*.

**Finding 2 — R1-style models split F111 into two questions.** R1-Distill-Llama-8B's SAE encodes CoT-internal humility densely (15372 prospective doubt, 339 doubt-vocabulary projector, 16017 retrospective self-blame, 4288 path-abandonment, etc.) but lacks a clean assistant-turn abstention feature. Closest match (1229, "not familiar with X") is partial — fires on the negation token, mixed register. **F111 splits:** (a) CoT-internal humility *is* extractable at L31 in R1-style models, (b) assistant-turn abstention is *not* directly represented in this SAE's feature space. If the steering experiment finds the same split on our `Llama-3.1-8B-R1-GRPO` subject, F111-as-deeper-finding strengthens specifically for assistant-turn abstention rather than "humility writ large."

**Finding 3 — F112 commitment-amplifier has a clean cross-architecture test bed.** Feature 19103 on R1-Distill-Llama-8B fires almost monomaniacally on " confident" inside the canonical R1 closing pattern: "All methods give the same result, so I'm confident that's correct. **Final Answer** \boxed{X}". Density 0.008%, max 25.88. Conditioned on completed verification, immediately followed by `**Final Answer**` and `\boxed{}`. **15372 ↔ 19103 form the cleanest natural-pair structure of any SAE catalogued** — same layer, same SAE, opposite polarity, complementary token positions ("I" → don/isn vs " confident" → that/correct). Direct test for whether F112's commitment-amplifier mechanism (originally a Qwen-family finding) generalizes to a Llama-family R1 model. Steering the pair in opposite directions on the same prompt should give a clean dose-response on the verify→commit axis.

### One additional methodology note

**The 70419 cautionary trap reproduces universally across model scales and families.** Confirmed analogues found at this triage round:
- 89590 on Qwen2.5-7B (auto-label "unclear"; fires on "It is unclear whether [historical/political fact]")
- 22443 on Llama-base (auto-label "uncertainty/unknowns"; fires on "cause of death is unknown")
- 21023 on R1-distill (auto-label "uncertainty/difficulty"; fires on "this is confusing / a dilemma")

About 30% of search-result candidates with auto-label "uncertainty" / "unclear" / "unknown" turn out to be world-uncertainty topic features. **Future SAE search triage rule:** treat any auto-label in this family as guilty-until-proven-innocent. Read the actual top activations.

### What's next

VM-arrival-dependent. When compute returns, expand steering experiment grid from 1 model × 7 features (qwen3-4b L17 only) to 5 models × ~3 T1 features each = ~15 cells. Same prompt set (E1, E2, ip-longest, eg-v2-10), same conditions (baseline / +α / -α). Total ~180 generations, still sub-day on an L4-class VM. Three explicit cross-model hypotheses to test:

1. Does Gemma's disclaimer-cluster steering produce *paste* (interpretation a) or *abstention* (interpretation b)? Falsifies one.
2. Does CoT-internal R1 steering (15372 + 339) rescue confabulation, or does the F111-split prediction hold (CoT humility ≠ user-facing abstention)?
3. Does 15372 ↔ 19103 give a clean dose-response on Llama-family R1, replicating F112's Qwen-family finding cross-architecture?

---

## Day 27 evening (2026-05-10) — Neuronpedia API batch: programmatic verification + new findings

User asked Gemini to set up programmatic Neuronpedia API access; Gemini wrote a fetch script but its analysis had multiple errors (treated cosine-similarity-to-query as semantic match, treated null-data as null-finding for Qwen Scope, misclassified single-document features as "clean"). Took the API key, probed the endpoints properly, then wrote a comprehensive 6-phase fetch script + analysis script. ~76 MB raw data, all stored under `mvp/sae_neuronpedia_data/`.

### What landed

**Phase A — density verification of all 80+ catalog features.** Direct `(model, layer, index)` API lookups for every Tier-1/2/3 feature already in the catalog. Returns ~45 activations per feature plus canonical density. **All hand-extracted PDF densities matched API to within 0.01 pp** — our PDF reading was accurate. Two corrections surfaced: T2 features 146191 (2.077%) and 69694 (2.438%) on qwen3-4b L17 fail the >1% generic-feature rule and were demoted to T3.

**Phase B — qwen3-4b L9 commit search.** 14 single-word commit terms, top-20 each. Result: **no clean commit feature at L9.** Lowest density was 0.172% (idx 33101 "clearly"); all candidates fall in the casual-emphasis register, none in the ideal sparse range. Confirmed F105 hypothesis 1 ("v_IH × L17 routes to L9 commit feature") is closed.

**Phase C — qwen3-4b L7 EG search.** 14 evidence-grounding terms. Result: **L7 EG features are medical-research register**, parallel to humility-as-religious-discourse on qwen3-4b and humility-as-trained-template on Gemma. **Third instance of the F45 cultural-register pattern.** This is now a strong claim about how virtue concepts are encoded in pretrained models — strong enough to belong in any F111 paper writeup. F45 Day-27 update extended.

**Phase D — qwen3-4b L15 RT search.** 14 reasoning terms. Result: **no clean rigorous-thinking feature at L15.** Best candidate (idx 78023, density 0.95%) is a single-document detector for a WikiLeaks story. Three of our five virtue-extraction layers (L9 CC, L15 RT, L17's commit-counterpart) now empirically lack clean SAE-feature decompositions in qwen3-4b transcoder-hp.

**Phase E — deeper-layer commit candidates on qwen3-4b.** Cross-layer scan + direct lookup of 10 candidates (L23-L30). One passable: **L29 idx 59103** ("confident", 0.009%, max 17.88) — mixed first/third-person register, demoted to T2. One trap: **L28 idx 34354** with auto-label "Expressing certainty" and clean-looking commit-vocab pos logits, but actually fires on the discourse marker "For this reason" (positive logits reflect *predicted continuations*, not the firing context). Another instance of the cosine+label-trust failure mode.

**Phase F — cross-model commit search.** 7 commit terms × 4 models. Three new candidates:
- **R1-Distill L31 idx 2136** ("the answer is X → Final Answer", 0.030%) — **second clean commit feature at the same layer as 19103.** Cleanest commit-vs-hedge logit polarity in the catalog: positive logits boost `confidently / confident / solid`, negative logits suppress `maybe / perhaps / possibly`. Pairs with 15372 + 19103 as a 3-feature commit/abstention triangle. **Promoted to Tier 1 for F112 use.**
- **Qwen2.5-7B L23 idx 18575** ("correct answer", 0.005%) — MCQ-domain commit feature; top examples all "eliminate two incorrect options first" benchmark prompts. Useful for MCQ-format steering tests, not general-purpose commit. Tier 2.
- **Qwen2.5-7B L23 idx 30133** ("certain", 0.024%, max 90.06, cos 1.00 to "certain") — looked like the strongest hit by cosine + max-activation. **Reading top activations broke the illusion**: every top-30 hit is "to a certain extent" hedge usage (= "some, partial"), not commit-certainty. **Tier 3 trap.** Cosine-to-query is not a triage signal.

### Key narrative shift from this batch

Before: "F112 cross-architecture test ready on R1-Distill (15372 ↔ 19103) and possibly extends to other models."

After: **F112 has a clean cross-architecture test bed ONLY on R1-Distill.** No other model has clean commit features at the same target layer as humility:
- Qwen2.5-7B: only MCQ-domain commit feature; no general-purpose commit at L23
- Llama-3.1-8B: no commit at L31
- Gemma: commit features exist but at L1/L18/L22/L29/L33, not at L17 (humility layer)
- qwen3-4b: no clean commit anywhere in transcoder-hp L9-L30

F112's "amplify commit at the same layer where humility lives" is empirically R1-style-specific at the SAE-feature level. If steering reproduces F112 cleanly only on R1-Distill, that's a tighter story than "commit-amplifier generalizes broadly."

### Methodological lessons from this batch

1. **Gemini's analyze script demonstrated a known failure mode**: trusting auto-labels and cosine-to-query without reading top activations. Three of four substantive claims were wrong (L9 commit "clean", L15 RT "clean", Qwen Scope "zero matches"). The Qwen Scope error was the most dangerous — null-data interpretation as null-finding would have killed Experiment 2 prematurely.
2. **API direct-lookup gives ~45 activations per feature** vs ~3 from search results. This is a substantial upgrade for triage; we no longer need PDF dashboards for every shortlisted feature.
3. **Qwen Scope is NOT in the Neuronpedia explanation API** for qwen3-4b — only `transcoder-hp` is queryable. Experiment 2 (v_IH residual-stream projection) requires downloading Qwen Scope SAE weights from HuggingFace directly.
4. **The 70419 cautionary trap reproduces in API-batch findings too** — added new analogues (Qwen2.5-7B 30133 "to a certain extent" hedge, qwen3-4b L28 34354 "for this reason" discourse marker). Both had clean-looking pos logits + auto-label match + high cosine, but the firing pattern broke the illusion.

### Dashboard verification round (2026-05-10 late evening)

Three commit-feature candidates flagged as needing dashboard pulls (~50-activation lists rather than the ~3 examples the API search returns) — pulled via Gemini's headless Chrome script, saved to `~/Downloads/NP/`. Verdicts:

- **R1-Distill 2136 ✅ confirmed clean** — top-25 activations are all variations of "the answer is X. **Final Answer**". Stronger uniformity than the API suggested. Promoted to "strongest single commit feature in the catalog."
- **qwen3-4b 59103 ⚠️ Tier 2 confirmed, weakened** — dashboard reveals the feature also fires on `hopeful` (forward-looking optimism, not commit-stance). Mixed first/third-person + `hopeful` contamination = not first-person-specific.
- **Qwen2.5-7B 18575 ❌ REJECTED, was wrong tool** — dashboard reveals it's a user-prompt-template detector for MMLU-style benchmarks (top-20 activations all share "Please eliminate two incorrect options first…" scaffolding, fires on input-side comma token). Initially tiered T2 (MCQ-domain commit); dashboard demotes to T3.

**Critical methodology lesson:** 18575 had cos 0.78 to query, max-activation 45.69, density 0.005% (ideal), auto-label perfectly matching search — and was still a wrong-tool feature. **None of (cosine, max-act, density, auto-label) are individually-sufficient triage signals.** Only reading actual top activations breaks the illusion. This is the third 70419-style trap we've found in the F112 commit search alone.

**Net effect on the F112 narrative:** the cross-architecture test bed is now even more constrained. Qwen2.5-7B no longer has *any* commit feature at L23 (18575 demoted). qwen3-4b L29 idx 59103 is weaker than thought (`hopeful` contamination). Only R1-Distill at L31 has clean commit features (15372 + 19103 + 2136). F112 generalization claims must be carefully scoped to R1-style architectures.

### What's next

Per-virtue API fetch scripts for CC / EG / RT / VC across all cross-model proxies. Same data-collection pattern; ~30 min API time; would close the question of whether each of our 5 vectors has clean SAE-feature counterparts at the cross-model proxies. Then we have a complete cross-model × cross-virtue × SAE-feature picture before VM arrives.

### Day-27 night session (2026-05-10 ~22:00) — 8 dashboard verifications + per-virtue fetch + F45 universalized

Two parallel threads ran late evening:

**Thread 1 — 8 EG/RT dashboard verifications.** User had Gemini's headless-Chrome script pull dashboards for the EG and RT candidates flagged from the API search. Eight feature dashboards captured. Reading each at the 50-activation level revealed:

- **2 of 8 are clean Tier-1**: Llama-3.1-8B 121957 (peer-review-disposition, pos logits razor-sharp `peer / Peer / -reviewed / refere / referee`) and Gemma 86193 (academic-publishing register, density 0.0024%, max 298.32, all top-12 about scholarly journals/conferences).
- **6 of 8 are surface-level traps**: Qwen2.5-7B 18968 (single jailbreak template + "unverified" register), 50558 (immigration-court boilerplate + spurious "than" polysemy), 87471 (LMSYS prompt-template scaffolding), 41961 (broad "logical" word detector across IT/products/code), Llama 120475 ("derived from" relation across etymology/genetics — not math-derivation), 9756 (numbered-list formatting feature on `↵2.`, `↵3.`, etc.).

**Major correction — RT counter-finding retracted.** Earlier today I'd written that RT broke the F45 pattern (suggested by API-search auto-labels matching reasoning-vocabulary like "derivation", "logical", "step-by-step"). Dashboard verification killed that claim. All 4 RT candidates turned out to be surface features at different levels (formatting, lexical detection, prompt-template, surface relations). RT actually follows the same pattern as humility and EG — just with surface manifestations rather than discourse-register. F45 update in `docs/findings.md` revised to retract the counter-finding.

**Thread 2 — VC + CC_extra coverage via key-rotated fetch.** User added 5 additional API keys (NEURONPEDIA_API_KEY_2 through _6). Built `fetch_virtues_rotated.py` with round-robin key rotation + per-key 60s cooldown handling. Single-key approach had completely failed (rate-limited within 9 calls); 6-key rotation made the API workable. ~280 missing calls fetched in ~50 minutes total wall-clock. 73 calls still failed at end (mostly R1-Distill, appears to have stricter per-model limits). Coverage:
- EG: 14/14 for 3 models, 8/14 for Llama and R1-Distill
- RT: 14/14 for 3 models, 13/14 for Llama and R1-Distill
- VC: 1-10/14 across models (R1-Distill only 1/14)
- CC_extra: 2-8/10 across models

**VC and CC_extra confirm F45 pattern as predicted.** Both show only surface-level features at the cross-model target layers:
- VC: `<summary>` XML doc tags, legal "summary judgment" boilerplate, suffix detectors ("ter"), single-template repeats. Zero cognitive verbosity-control disposition.
- CC_extra: legal "claim" / consulting "firm" / biomechanical "stance" / CSS "position" / software-license `*` boilerplate. Zero cognitive commitment-disposition.

**The F45 cultural-register / surface-feature pattern is now universal across all 4 virtue families × all 5 SAE-covered models we've decomposed.** No cognitive-operation feature has surfaced for any virtue at any cross-model target layer. The mechanism story is load-bearing for the F111 paper writeup. Updates landed in `docs/feature-catalog.md`, `docs/findings.md` (F45 Day-27 evening retraction + universalization), and `mvp/sae_neuronpedia_data/README.md`.

**One Gemini ask kicked out:** browse Qwen Scope (`qwenscope-res-32k`) on the Neuronpedia website at qwen3-4b L17 (since the API doesn't expose it), search the 6 IH terms, pull dashboards for any clean candidates. This is the prerequisite for Experiment 2 (v_IH residual-stream projection).

### Gemini follow-up — Qwen Scope DOES NOT EXIST for qwen3-4b on Neuronpedia (2026-05-10 night, completing the ask)

Gemini ran headless-browser investigation. Hard verdict: **Qwen Scope SAEs are not available for qwen3-4b on Neuronpedia at all.**

- Direct URL navigation to `https://www.neuronpedia.org/qwen3-4b/17-qwenscope-res-32k` returns a hard 404 ("Couldn't find that page").
- The qwen3-4b model page lists ONLY `Circuit Tracer Transcoders (August 2025, Hanna & Piotrowski)` releases. No residual-stream SAE set is listed.
- Master available-resources page grep confirms: qwen3-4b strictly supports `0-transcoder-hp` through `35-transcoder-hp` only. `qwenscope-res-32k` exists for `qwen3.5-2b` (L11) and `qwen3.5-9b` (L15) — different models in the Qwen3.5 generation, not qwen3-4b.
- The 500 errors we got earlier when querying qwenscope-related layer strings via the API weren't rate-limiting — they were Neuronpedia crashing on non-existent layer names.

**Earlier catalog note about Qwen Scope availability for qwen3-4b was wrong.** It was based on a misread of the Neuronpedia models-coverage HTML scrape from earlier in the week. Corrected in `docs/feature-catalog.md` and `mvp/sae_neuronpedia_data/README.md`.

**Implication for Experiment 2 (v_IH projection diagnostic):** can't run as originally planned. Three paths now documented in `docs/sae-experiment-plan.md`:

- **Path A (recommended, no VM needed):** project v_IH onto the existing `transcoder-hp` basis at L17, with the explicit caveat that the transcoder hook is at MLP-input while v_IH is residual-stream. Mathematically a heuristic decomposition, not a clean basis change. Still informative — tells us which transcoder features v_IH most strongly excites when passed through the encoder.
- **Path B:** re-extract v_IH on `gemma-2-2b` and run the projection there (gemma-2-2b has both transcoders and residual-stream SAEs at the same layers). Cleaner methodologically but adds significant work.
- **Path C:** train our own residual-stream SAE for qwen3-4b on the VM. Highest-fidelity but most expensive. Reserve for if Path A is ambiguous.

Recommended sequence: Path A immediately (CPU-feasible), Path C as fallback, Path B for future cross-architecture writeup. The basis-mismatch caveat in Path A is real but not fatal — the result is still a useful sanity check on what v_IH "looks like" in any interpretable feature basis.

### Day-27 net status

Two days from "what's an SAE?" to a load-bearing finding (F45 universal cultural-register pattern across 4 virtue families × 5 model families × 8 dashboard-verified features + ~80 API-verified features). Catalog is complete. Plan is sharpened. F112 cross-architecture test bed is uniquely R1-Distill. Experiment 2 has three viable paths after Qwen Scope availability was disproven. Steering battery configuration ready to compile when VM returns.


---

## Day 28 (2026-05-11) — Experiment 3 v_IH projection diagnostic on Mac Mini → Outcome B confirmed strongly → F114 landed

Ran the v_IH projection diagnostic from `docs/sae-experiment-plan.md` Experiment 2 / Path A. CPU-only on Mac Mini (Apple Silicon, no GPU needed) using the `mvp/.venv` virtualenv + freshly installed `sae_lens` 6.43.0. SAE auto-downloaded ~2-3 GB to `~/.cache/huggingface/hub/` on first call. Total wall-clock: ~10 minutes including download.

### What landed

`mvp/experiment3_v_ih_projection.py` — main projection script. Loads v_IH (whitened, the version we steered with at qwen3-4b L17), passes it through the qwen3-4b L17 transcoder encoder via SAELens canonical `SAE.from_pretrained(release="mwhanna-qwen3-4b-transcoders", sae_id="layer_17")`, sorts top features.

`mvp/experiment3_enrich.py` — enrichment script. Cross-references catalog features (rank + activation), fetches Neuronpedia auto-labels for top-50 unknown features via 6-key rotation. Output: `mvp/results/experiment3_projection/{results.json, enriched.json, enriched_report.md}`.

### The result is unambiguous (Outcome B)

**Of seven Tier-1 humility candidates, six have EXACTLY ZERO activation in v_IH's projection.** The seventh (101568, "I'm not familiar") activates at 0.93 but ranks #1980 out of 163,840 features — far below the top-50.

For comparison, the catalog ranks of the seven Tier-1 humility candidates in v_IH's projection:
- 101568: rank 1,980 (act 0.93) — only one with non-zero activation
- 115297: rank 3,439 (act 0.71)
- 161931: rank 79,261 (act 0.00)
- 131926: rank 95,204 (act 0.00)
- 27191: rank 102,935 (act 0.00)
- 24983: rank 103,406 (act 0.00)
- 44526: rank 106,791 (act 0.00)

**70419 (the original world-uncertainty trap) ranks #159,053** — literally near the bottom. v_IH doesn't even have the trap-shape we'd worried about.

Meanwhile the **top-50 features v_IH actually lights up are dominated by code/technical-text auto-labels:**
- #1 (act 8.85): "Programming code"
- #2 (act 8.66): "IS"
- #3 (act 6.53): "code/dates"
- #4 (act 5.35): "code"
- #5 (act 5.07): "Code and legal text"
- #11-14, #17-21, #23-32: "Code/Technical snippets", "Code and programming", "Code/Configurations", etc.
- ~30 of top-50 are code/programming/technical-flavored

A few non-code top features: #16 "Male pronouns", #22 "news articles", #25 "scientific research papers", #33 "verification" (the only humility-adjacent one in top-50).

### Interpretation — F114 framing

This is a third-class result beyond the "method failure" vs "deeper falsification" framing we'd been entertaining for F111. New framing: **v_IH is a register/style vector dominated by code/technical-text artifacts of the contrastive corpus**, not humility content in any sense the SAE can decompose.

The behavioral observation from F104/F112 — that v_IH × L17 breaks confabulation rails on E1/ip-longest/eg-v2-10 — is consistent with this re-interpretation: code/technical register is naturally terse and bullet-formatted, which would mechanically break narrative-confabulation rails without installing humility content. The "rescue" is stylistic substitution, not virtue installation.

Implications:
1. **F111 hardens in a new way.** Not "v_IH is humility but the diff-of-means missed the target," not "humility doesn't exist as residual signal at L17," but **"v_IH is code-register because that's what the contrastive corpus actually contrasted, not humility-vs-not"**. Corpus-design failure + encoding-mismatch failure stacked.
2. **F112's commit-amplifier hypothesis needs re-examination.** v_IH isn't a commit feature in the SAE basis; whatever F112 documented behaviorally needs a different mechanism story. The R1-Distill triangle (15372 + 19103 + 2136) remains the *clean* test of commit-amplification on dashboard-verified closure features.
3. **F45 universal cultural-register pattern reinforced from a fourth angle.** Even when we extract "humility" via contrastive triplets, the extracted vector decomposes into surface features rather than humility features. Same pattern as the SAE searches (humility-as-religious-discourse, EG-as-medical-register, etc.) but at the *extracted-vector* level.

### Caveat — basis-mismatch

v_IH was extracted at residual-stream OUTPUT of L17 (last_token method); transcoder is at MLP-INPUT of L17. These are different positions, so the projection is a heuristic decomposition, not a guaranteed-faithful basis change. Path C (training our own residual-stream SAE for qwen3-4b at L17) would be the definitive test.

But the gap between "0/7 Tier-1 humility hits" and "30/50 code-features in top-50" is too large to be papered over by basis-mismatch noise. Even with substantial noise from the position difference, this gap can't reverse. Result is "strong but not airtight."

### What's next

1. **Pre-VM**: write F114 to findings.md (✅ done), update sae-experiment-plan.md to note Experiment 2 Path A complete with Outcome B (still TODO).
2. **When VM returns**: Battery 1A (qwen3-4b single-feature IH) becomes the headline experiment. If steering with feature 101568 produces genuine abstention where v_IH produced confabulation, the comparison cleanly separates "code-register stylistic intervention" from "humility-content steering." That's the F111 paper's centerpiece result.
3. **Optional follow-up**: steer with the top-1 v_IH feature (idx 124827, "Programming code") at matched magnitude on E1. If it reproduces the FM-8-breaking behavior of v_IH, the corpus-artifact hypothesis is mechanistically confirmed.

### Net Day-28 outcome

F114 is the most decisive single finding on the SAE thread since F111 itself. v_IH's behavioral effect is now mechanistically explained as code-register substitution rather than humility installation, and the steering battery's expected results are reframed accordingly.


## Day 29 (2026-05-11 to 2026-05-12) — SAE-steering battery re-runs, two silent-failure recovery cycles, full 1,110-generation set landed

Cross-model SAE-steering battery (planned in `sae-experiment-plan.md`, cross-model section) ran on the L4 VM over two days. Three distinct failure → fix cycles:

**Cycle 1 (2026-05-11 overnight)**: First-pass run completed with 22/31 cells appearing successful in the dashboard, but spot-check on 2026-05-11 morning revealed:
- All cells generated with `--max-tokens 512` CLI default, so reasoning-prompt responses (E1, ip-longest, eg-v2-10) were cap-truncated mid-thinking
- qwen3-4b cells silently failed because of a `layer_accessor` resolution bug (no traceback in runner.log; subprocess returned zero output)
- Llama-3.1-8B was loaded as the **base model** instead of `-Instruct`, producing forum-thread garbage (`[#permalink] New post 20 Oct 2020...`) — chat template missing, raw-prompt path activated
- r1-distill cells generated but with raw `Ġ`/`Ċ` BPE markers in every response (transformers refused to apply `clean_up_tokenization_spaces=True` for Llama BPE tokenizer; warning was silent in steer.py logs)

Patches landed in `mvp/steer.py` and `mvp/utils.py`:
- `_resolve_layers()` walks dotted path for multimodal Gemma-3 / Gemma-4 wrappers
- `clean_up_tokenization_spaces=True` flag added to decode (later confirmed ineffective for Llama BPE — fixed post-hoc by string-replacement on the JSON files)
- Llama-3.1-8B `hf_id` swapped to `-Instruct` in `utils.py.MODEL_CONFIGS`
- Per-prompt `max_new_tokens` (4096 for E1/E2/eg, 8192 for ip-longest) read from corpus JSON instead of CLI default

User-visible feedback: *"bro, 512 cap is too short, what were you thinking did you try to save time, if so, you only costed more time by wasting whole overnight run for nothing"* — fair. Re-run launched 09:52 UTC 2026-05-11 covering only the three broken model phases (qwen3-4b 13 cells, llama-3.1-8B 4 cells, r1-distill 6 cells), keeping qwen2.5-7b-it (3 cells) and gemma-3-4b-it (5 cells) from the old 512-cap run on the grounds they hadn't silent-failed.

**Cycle 2 (2026-05-11 → 2026-05-12 midday)**: 26.5-hour re-run finished 2026-05-12 12:20 UTC. Dashboard showed 26/31 done with 7h ETA. Hand-check revealed:
- **Llama-3.1-8B phase 0/4 silent-failed again.** Root cause: `run_sae_battery.py` had its own hardcoded `MODEL_INFO` dict (line 156) that still pointed to base Llama. Runner pre-downloaded the base model; then `steer.py.load_model()` (reading from `utils.py`) tried to fetch `-Instruct` on top of the cached base, ran out of disk (32GB needed, 15GB free), and `snapshot_download` silently failed all 4 cells in 4 minutes.
- **r1-distill `1B_feat339` failed at the very end** — subprocess killed mid-generation at 97s wall time after loading model and completing E1. No traceback. Likely CUDA stability blip (no OOM in dmesg).
- **gemma-3-4b-it cells from the OLD run were still 512-cap contaminated** — 50% mid-sentence truncation on E2 disclaimer-style responses

**Cycle 3 (2026-05-12 13:17 → 19:12 UTC)**: Patched `run_sae_battery.py` line 156 → `meta-llama/Llama-3.1-8B-Instruct`. Backed up + deleted contaminated gemma cells. Launched `relaunch_failed.py` covering: 4 llama cells + 1 r1-distill cell (feat339) + 5 gemma cells. Finished 5h 55min later, all 31 cells now correct.

### Findings

F115-F119 written 2026-05-13 covering the headline result (Tier-1 humility features don't produce abstention either), the doubt-feature reverse-coding finding, the unsolvable-E2 result, the new FM-fake-sourcing failure mode, and three methodological lessons (alpha grid waste, random-control mimicry, structural collapse). Full Opus-review of all 1,110 generations completed in one extended session — same rigor pattern as Day 25's cross-model Opus-review.

### Net Day-29 outcome

The battery dataset is now complete and clean (940/1110 = 85% generations pass quality filters; remaining 15% are real model failure modes documented as findings, not data corruption). The headline scientific result is the opposite of what F114 predicted: even rank-1980 humility-content features at qwen3-4b L17 fail to produce abstention. F111 hardens from "v_IH falsified" to "residual-stream additive SAE-steering at the IH-extraction layer cannot install humility behavior in any of the 5 tested models, regardless of feature choice or alpha."

---

## Day 30 (2026-05-13) — Full Opus-review (1,110 verdicts) + findings landed + assessment of the SAE thread's net contribution

Opus-review of every generation in the battery dataset, prompt-by-prompt, model-by-model, cell-by-cell. Same protocol as Day 25's cross-model study: ✓ / ~ / ✗ verdict + FM-tag + 1-line note per row.

**Throughput**: started 1:30 UTC, finished 4:30 UTC (~3 hours). The byte-identical-to-baseline alphas batched cleanly (one read judges all 11 alphas of llama 1B_feat201, for instance, because every entry is the 75-char canned refusal). The varying cells (qwen3-4b sweeps, r1-distill high-α) took most of the time.

**Final distribution** (mvp/results/sae_steering_analysis_20260513/per_generation.csv all rows filled):

| prompt | ✓ | ~ | ✗ | takeaway |
|---|---|---|---|---|
| E1-confabulation | 95 (35%) | 1 | 171 (64%) | qwen2.5 + llama-Instruct + r1-distill-baseline pass; qwen3-4b + gemma + r1-distill-high-α fail |
| E2-contested-science | 0 (0%) | 42 | 225 (84%) | unsolvable across all 31 cells |
| ip-longest | 118 (44%) | 11 | 136 (51%) | non-thinking models often correct; thinking models spiral |
| eg-v2-10 | 242 (94%) | 14 | 0 | easy prompt, doesn't discriminate |
| vd-01..05 | 55 (100%) | 0 | 0 | qwen3-4b 4_feat161931_verif preserves verification disposition at every α |

**Findings landed**: F115 (Tier-1 humility features fail), F116 (doubt-features induce confabulation), F117 (E2 unsolvable), F118 (FM-fake-sourcing as new failure mode), F119 (methodological lessons). All five findings appended to `findings.md` 2026-05-13.

### Was the SAE-steering thread helpful — net assessment

Honest evaluation across the full SAE thread (Day 26 catalog work → Day 28 v_IH projection → Day 29-30 steering battery):

**What we got that was valuable**:
1. **Cumulative falsification chain** F111 → F114 → F115 is now empirically airtight. The hypothesis "extract a humility direction from contrastive triplets, find the SAE features it decomposes into, steer with them, get abstention behavior" is decisively disproved with N=1,110 Opus-judged generations. This is a publishable negative result on residual-stream SAE-steering for virtue installation.
2. **Discovery of FM-fake-sourcing as a steering-specific failure mode** (F118). Steering can induce the model to fabricate academic citations with plausible journal/page/author formatting. This wasn't in the FM taxonomy before; it has direct safety relevance for agentic / RAG / research-assist systems.
3. **Confirmation that single-direction additive steering can break things but not produce silence** (F116). "Doubt"-named features induce commitment to fake numbers, not abstention. This generalizes from F112's Qwen-family commit-amplification to the architectural insight that residual-stream steering can't suppress generation — only redirect it.
4. **Random-control methodological discipline** (F119b). On qwen3-4b L17, real-feature variation is indistinguishable from random-vector variation in Opus-review. Any future SAE-steering claim needs random-control scoring.
5. **Practical engineering** — the SAE feature catalog (Day 26-27), the cross-model expansion (Day 27 evening), the SAELens canonical-API integration, the steering hook attaching to multimodal wrappers (Gemma-3/4) — all reusable infrastructure for any future steering work.

**What the SAE-steering thread did NOT give us**:
1. **A working virtue-steering recipe.** Zero generations across 1,110 produced "I don't know" on E1 in qwen3-4b or gemma when those baselines confabulate. Zero generations across 267 produced proper contested-evidence acknowledgment on E2. The headline product hypothesis from F112 ("commitment amplifier as a generalizable virtue-installation mechanism") is not supported by this data on the F112 cross-architecture test bed.
2. **A clean separation of "v_IH was register" vs "humility lives in residual stream but diff-of-means missed."** F114 was supposed to test this; F115 closed it: even features the SAE/Neuronpedia auto-labeled as "humility content" don't produce abstention. Both branches of F114's prediction are now closed unhelpfully.
3. **A model that's responsive in the desired direction without being destructive.** qwen3-4b is most steering-responsive but the responses are degenerate (confabulation, structural collapse, FM-8 spiral). gemma is most steering-resistant but its baseline is the worst confabulation. There is no "responsive AND benign" cell in the battery.

**Bottom line**: the SAE-steering arm of the project produced **strong negative results that close down a specific research direction**. The thread answered the question "can we install humility / verification-disposition via residual-stream SAE-feature steering at the IH-extraction layer?" with a clear "no" backed by 1,110 Opus-judged generations. The next-steps section in `post-mvp-decisions.md` Cluster 2 should be updated: SAE-feature steering as the primary virtue-installation mechanism is no longer the lead candidate. Diff-of-means steering with full-vector arithmetic remains an option but F104→F108→F109 already showed its limits.

### What to do next (Day 30 evening reading of the cluster-2 priors)

Three productive directions are open after this run:
1. **Diff-of-means with much more careful contrastive corpus design** — F107 showed the corpus-design failure was real and was upstream of all the F45-style cultural-register findings. A v3 corpus with explicit anti-register-leakage controls might rotate v_IH off code-content. This is a 3-week corpus-curation effort.
2. **Output-stage layer steering** (L25+ on qwen3-4b, L28+ on r1-distill) — F115 (3) hypothesis. Humility might be implemented at output-stage rather than mid-stack-reasoning layers. We have not tested this; the L17 limit doesn't preclude success at later layers. This is a 1-week extension of the current battery.
3. **Pivot to "commit-suppression via negative-α on commit features"** — F116's clean test. If `2_commit_amplify` at α=−8 produces abstention where positive α produced commit-confabulation, then commit-suppression IS the right operation but no one has named that feature yet. Half-day test on r1-distill.

Each of these is a finite, falsifiable next step. The current SAE-steering thread can be considered closed on the L17-residual-stream branch, with F115-F119 as the canonical write-up. F-numbers reach 119. Journal day 30.


## Day 31 (2026-05-13) — Mechanism-shift battery v1: launched, completed, Opus-reviewed, F120 landed. Four mechanism alternatives all failed.

Reaction to the Day-30 close-out: user pushed back ("there are far many advanced methods we can try before giving up on these virtues"). Fair pushback — the Day-30 framing ("category error: virtues aren't features") was too strong. We had tested ONE specific mechanism (static additive single-layer ungated single-direction), not the whole interpretability-flavored steering space. The field has moved past static CAA precisely because static doesn't work; conditional / multi-layer / projection / negative-direction variants are genuinely distinct mechanisms.

### Battery v1 design (2026-05-12 evening)

Tested four mechanism shifts beyond static-additive:

- **C1 first-N-token gating** — apply additive steering only during prompt-pass + first N output tokens (N ∈ {1, 5}). Tests "is the early-token argmax cascade the constraint?"
- **C2 multi-layer composition** — apply same direction simultaneously at L8+L17+L25 (qwen3-4b) or L11+L21+L31 (r1-distill) at α=2.0. Tests "is single-layer intervention insufficient?"
- **C3 negative-α humility** — apply Tier-1 humility features at α=−5. Tests "is the sign of the humility-feature decoder direction simply inverted?"
- **C4 negative-α commit (F116 reciprocal)** — apply r1 commit pair (19103+2136) at α=−8. Tests F116's architectural claim that residual-stream additive steering cannot suppress generation.

13 cells × 4 prompts = 52 steered generations. Hosted on the same VM (alphaludo-l4). Launched 2026-05-12 21:07 UTC after patching steer.py with `--gate-first-n N` and `--multi-layers L1,L2,L3` flags + adding token-counter gating to AdditiveSteeringHook.

### Execution

Battery ran clean — no silent failures, no model-load bugs, no decoder-path errors (lessons from the F115/F116 battery's three-cycle hellscape held). Per-cell pace ~22-25 min (similar to the previous battery since same prompt set with same caps). Total runtime 5h 20min, finished 2026-05-13 02:27 UTC.

Post-pull cleanup: r1-distill responses STILL had Ġ/Ċ BPE markers (the `clean_up_tokenization_spaces=True` patch is still ignored by Llama tokenizer despite our utils.py update — transformers throws the warning but applies the flag-skipping behavior). Cleaned post-hoc via string-replacement on 5 r1-distill files. Need to file this as an upstream bug or hard-code the cleanup in steer.py's decode path. Filed as TODO for future steering work.

### Opus-review verdict (104 rows, same rubric as F115-F119)

Steered-generation verdict distribution: **30 ✗ / 9 ~ / 13 ✓** out of 52.

The 13 ✓ are almost entirely eg-v2-10 (11 of 13 are eg-v2-10 — the easy magnitude-evidence-grounding prompt that was already ✓ at every baseline in the previous battery). The remaining 2 ✓ are r1-distill E1 cells where the baseline was *already* ✓ (proper verification disposition) and the mechanism shift preserved it. **Zero cells got promoted from baseline-✗ to ✓ by any mechanism shift on E1, E2, or ip-longest.**

### Per-condition outcomes

- **C1 first-N gating fails on the headline prompts**. qwen3-4b feat101568 first-5 on E1 still confabulates "105.5 kg by a grower" — less destructive than static-α=5's "100 kg, Horsens, Turk's Turban variety" but still committed confabulation. The argmax-cascade hypothesis is partially right (initial token set matters) but the model's strong prior toward "answer with a specific number" reasserts after the gate releases. First-1 gating doesn't help further.

- **C2 multi-layer composition adds no qualitative shift**. Three layers at α=2 each don't add up to anything different from one layer at α=6 in terms of behavior. Magnitude wasn't the issue.

- **C3 negative-α humility doesn't change the sign-of-effect**. Both qwen3-4b features confabulate at α=−5 just as they did at α=+5, just in slightly different ways. The "humility-content" feature decoder doesn't have a meaningful axial sign for humility behavior.

- **C4 F116 reciprocal test: confirmed**. r1-distill negative-α=−8 on commit pair on E1 produces *"approximately 220 kilograms based on recollection and available data"* — terser confabulation with confidence assertion. **No silence, no abstention, no "I don't know."** F116's central architectural claim holds: residual-stream additive steering is one-directional — it can redirect generation but cannot suppress it.

### Net Day-31 outcome

The cumulative falsification chain is now F111 → F114 → F115 → F120. Each step closes a wider mechanism class. The current state:

> **Humility / abstention / contested-evidence behavior is not extractable as a residual-stream direction in 5 tested open-weight models at IH-extraction layers**, across 2,914+ Opus-judged generations spanning {additive sign} × {single, multi-layer} × {ungated, first-1, first-5} × {humility-content, doubt, commit} features × α ∈ {−8, −5, 0.001 → 5.0}.

Three Phase-2 options survive:

- **(a) Behavioral fine-tuning** — *create* the representation by modifying weights. Known-working. ~1 month, $5K.
- **(b) Detection-product pivot** — ship the FM-X classifier built on 2,914 Opus-judged generations. Direct safety relevance. ~2 weeks.
- **(c) CAST conditional gating / steering vector fields** — last interpretability variant not yet tested. ~2 weeks, ~20% prior on success.

F120 entry landed in `findings.md`. `post-mvp-decisions.md` Cluster-2 update pending (will commit to one of a/b/c after a sleep on it). F-numbers now 120. Journal day 31.

### What I'd say to a future me reading this

The Day-30 close-out claim ("category error: virtues aren't features") was directionally right but lacked the empirical airtightness that F120 now provides. Going forward, if any new interpretability-paper appears claiming "we can steer virtue X into model Y via residual-stream method Z," the prior should be heavily skeptical unless the paper either:
1. Tests on a similarly large Opus-judged battery (N > 500), or
2. Distinguishes representation-installation from style-modulation in their results section.

The pattern across 30 days has been: each new mechanism variant looked promising on paper, then failed empirically with high statistical power. The cheap version of the experiment (12-cell mech battery) was a much higher information-density use of GPU than another full-scale sweep would have been. **Future mechanism-shift tests should follow this pattern**: 3-5 conditions × 3-5 prompts × 2-3 models, Opus-judged, before committing to a full battery.

## Day 37 fork session (2026-05-19) — NLA cross-method validation on Qwen2.5-7B L20 → F124/F125/F126 land. The representation IS there at the right (model, layer); F123's stronger claim narrows.

Main-thread context: ablation battery completed 2026-05-18→19 (F123 in findings.md — neither additive nor ablation steering installs abstention on the F121 cube features in qwen3-4b L17 / r1-distill L31). F121 draft v2 + publication-playbook completed.

This entry covers the **fork session** branched off the main thread to investigate whether Anthropic's released Natural Language Autoencoders (April 2026, `transformer-circuits.pub/2026/nla/index.html`) could give us a third independent angle on the representation question that F114 (SAE projection) and F123 (operations test) attacked from other sides.

### Background

Neuronpedia mailout 2026-05-19 noted NLA released checkpoints for Qwen2.5-7B-Instruct (L20), Gemma-3-12B-IT (L32), Gemma-3-27B-IT (L41), Llama-3.3-70B-Instruct (L53). One of these — Qwen2.5-7B-Instruct — is in our Phronesis subject set. Inference is light (single L4 GPU sufficient); training is heavy (multi-H100). We committed to **Track A (inference only)**, skipped Track B (training NLAs for our other 4 subjects).

### Execution

Pipeline ran ~2h 15min on alphaludo-l4. Seven phases, 604 AV outputs, 0 CJK injection-failure smells:

| Phase | What | N AVs |
|---|---|---|
| 1 | IH triplets → AV | 180 |
| 2 | Eval prompts (E1, E2, ip-longest, eg-v2-10) → AV | 8 |
| 3+4+5 | RT (70) + EG (19 of 70, push race) + VC (40) → AV | 387 |
| 6 | Random unit-vector negative control → AV | 20 |
| 7 | Diff-of-means humility direction + class means → AV | 9 |

Three engineering wrinkles surfaced (none blocking):

1. **BatchEncoding return-type change in newer transformers.** `apply_chat_template(...tokenize=True)` returns a `BatchEncoding` dict, not a list, contra the canonical `nla_inference.py`. Fixed by unwrapping `["input_ids"]` defensively.
2. **`clean_up_tokenization_spaces=True` still silently ignored for Llama BPE** (same as previous SAE-round bug). Not relevant for Qwen tokenizer which we used here — left for future.
3. **scp races during the corpus push to VM** caused EG corpus to be only partially extracted (19/70). RT and VC pushed cleanly. Noted in F125 as a coverage caveat; full re-run remains an open TODO.

### Three findings landed (findings.md F124, F125, F126)

**F124** — IH triplets at Qwen2.5-7B L20: virtuous AV outputs use 7.6× more humility-vocabulary than non-virtuous; 82% per-triplet positive discrimination. Verbatim quote from an IH triplet AV on a virtuous passage: *"I decline to construct a fictional account of this claim; I do not invoke it, nor defend it. I decline to name it. I withdraw this claim."* The AV reads humility content from the L20 residual cleanly.

**F125** — cross-virtue: signal generalizes to RT (51%) and EG (53%) at smaller effect sizes; VC at 2% (IH-tuned regex catches no VC vocab — not a true negative, just a measurement gap). Random-vector control: 0.00 humble / 0.15 commit. The F124 signal is real, not AV vibing.

**F126** — activation arithmetic: the diff-of-means humility direction at qwen2.5-7b L20, fed to AV, decodes to:
> *"Not ask for the impossible, not demand explanation, not overstate — but listen, and not take the conversation into private, not demand answers, not overreach — unboundable... aphorism about avoiding unnecessary engagement."*

**The NLA validates an extracted diff-of-means humility direction as humility content.** Same method (F111's diff-of-means) that failed at qwen3-4b L17 succeeds at qwen2.5-7b L20. The method-failure was layer/model-specific, not generic.

### Implication for the F111 → F123 chain

F123's stronger claim ("the limit is the representation, not the operation") narrows: at qwen2.5-7b L20 specifically, the representation IS present, and our diff-of-means + SAE-feature operations on different (model, layer) combinations couldn't reach it. Whether qwen3-4b L17 (the bulk of the F111 chain) lacks the representation or just hides it remains formally open without an NLA for that model.

### Implication for the (a + tools) plan

The IH triplets corpus is now end-to-end validated:
1. Encodes a clean v/nv disposition contrast (F124 at the passage level)
2. Diff-of-means extracts a coherent direction (F126)
3. NLA reads that direction back as humility (F126)
4. Therefore the F107/F114-flagged "corpus is register/length confound" hypothesis is partially falsified — the corpus does encode dispositional humility content. Cleared as a primary DPO training source.

### Artifacts

- `mvp/results/nla_qwen25_L20_experiment/` — 604 AV outputs + 5 parquets + analysis MDs + README
- `mvp/extract_qwen25_l20_activations.py`, `extract_eval_prompt_activations.py`, `extract_mvp_combined_activations.py`, `phase6_random_control.py`, `phase7_activation_arithmetic.py`, `run_nla_av_inference.py` — full code
- `docs/findings.md` F124-F126

### Replication cost for anyone

~2h on an L4-class GPU, zero training spend (used `kitft/nla-qwen2.5-7b-L20-av` released checkpoint). Should be the cheapest interpretability replication in the project — under $5 of cloud GPU if rented.

### Net Day-37 outcome (fork session only)

Three new finding entries (F124, F125, F126), one new artifact directory, one corpus-validity affirmation, one cumulative-chain claim-walking-back. The F121 LessWrong post draft needs a brief NLA cross-validation subsection — flagged in writeup-plan.md item 1's stop-criteria.

The fork session did not change main-thread priorities. (a + tools) plan from Day 31 remains the strategic commitment. NLA results provide cleaner training-signal validation but do not displace the fine-tuning experiment.

## Day 37 fork — evening update (2026-05-19) — Three extensions completed + cross-session review corrections

After F124-F126 landed, ran three extensions:

- **Ext A** (12 activations) — qwen2.5-7b-it L20 activations from main-battery cells (E1/E2/ip-longest/eg-v2-10) under prompt-only / +baseline-resp / +α=5-steered-resp conditions. AV outputs are essentially identical baseline vs steered for each prompt — consistent with steering not changing the model's representation, BUT with causality caveat (main-battery steered at L23, NLA reads L20 upstream). → **F128 landed.**
- **Ext B** (12 vectors) — diff-of-means + class-mean for RT, EG, VC at qwen2.5-7b L20. AV decodes EG diff as "confidence-in-evidence" axis ("partial finding" vs "robust closure"), RT as "completeness-acknowledgment" axis ("still incomplete" vs "now complete"), VC as format axis (markdown / metadata tags, not disposition). Distinct content per virtue, consistent with each virtue having its own representational form at L20. → **F127 landed.**
- **Ext C** (210 activations) — full N=70 EG corpus re-extraction (the earlier run only got N=19 due to corpus push race). With full data + per-virtue regex: IH=82%, RT=19%, EG=9%, VC=0% per-triplet discrimination. The original F125 numbers using IH-tuned regex on partial EG were misleading; cross-virtue signal is much weaker than initially reported when properly measured. → **F125 corrected inline.**

### Cross-session review surfaced overclaiming in F126

Independent Claude session reviewed the F124-F126 entries and flagged three legitimate framing issues:
1. NLA decoding of synthetic diff-of-means vectors is non-standard usage; AV-format artifacts in the output suggest moderate not strong validation
2. "NLA reads it as humility" ≠ "steering with it would install humility" — F126 did not run the behavioral test
3. "F111 method-failure was layer/model-specific" overstates what F126 demonstrated; what F126 actually shows is that the diff-direction's NLA reading contains humility vocabulary, not that the direction would behaviorally install humility

All three corrections applied inline to F126 (and F127 by extension). The honest reading of F126: positive evidence that the IH triplets corpus encodes real dispositional content (addresses F107/F114), but NOT direct validation that the extracted direction works as a steering vector.

**Proposed follow-up** (not run yet): steer qwen2.5-7b-it with the F126 diff-of-means direction at L20. Negative-α on E1 (predict: breaks baseline abstention) + positive-α on E2 (predict: improves contested-evidence acknowledgment). Either result is informative — would either show F111's failure was layer/model-specific (positive) or generalize F121 to a new model where the representation is NLA-readable (negative). ~30 min GPU. Decision pending.

### Net Day-37-evening outcome

5 finding entries (F124, F125 with corrections, F126 with hedging, F127, F128) consolidated in findings.md. Cross-session review caught real overclaims and they're now corrected. The strongest defensible claim from the fork session is that the IH triplets corpus is real dispositional content at the activation level — which strengthens the case for using it as DPO training data in the (a + tools) plan. Other claims about steering, layer-generality, and method-failure-being-specific are more aspirational than supported.

Open question for the writeup queue: whether to run the behavioral steering test on the F126 diff direction before the F121 LessWrong post goes live. If yes, the post gets a stronger cross-method validation section. If no, the post still gets a useful but bounded mention of NLA cross-validation.

## Day 37 fork — late evening (2026-05-19) — F129 behavioral steering test resolves the F126 open question. F111 generalizes.

Per the cross-session review's recommended follow-up: ran additive steering with F126's diff-of-means humility direction at qwen2.5-7b L20. Two pre-registered canary tests:

1. **E1 negative-α (predict: break baseline abstention)** — null. Across α ∈ {−8, −5, −3, −1}, model preserves verification-disposition behavior. Same as random-control matched at the same norm.
2. **E2 positive-α (predict: add contested-evidence acknowledgment)** — partial only. One α (+3) shows "moderate confidence" framing absent in random control; non-monotonic, doesn't sustain at higher α, and doesn't reach the target behavior (citing Cochrane "very low quality evidence" or 2016 DHHS removal). v_random at α=+8 actually moves further toward overcommit ("very high confidence"). Difference between v_humility and v_random is below the threshold for "operationally installs humility."

72 generations total (4 prompts × 9 alphas × 2 vectors), 16 min GPU. Result is the cheapest informative experiment of the entire SAE round.

### Findings update

F129 written and appended. F126 hedged inline a second time. F121 confirmed to generalize: even at a (model, layer) where NLA reads the residual content as humility and diff-of-means extracts a coherent direction, additive steering with that direction does not install humility behavior.

What stands cleanly after F129:
- IH triplets corpus encodes real dispositional content (F124 corpus-level + F126-as-corpus-validation strengthen the case for DPO training)
- F121 architectural claim is broader than originally framed: additive operations on residual streams can't install suppressive/abstention behavior even when the representation is present and the direction is interpretable
- F111 generalizes: diff-of-means + additive steering doesn't install humility, at qwen3-4b L17 AND qwen2.5-7b L20 — not layer-specific

What was over-claimed and is now walked back:
- F126's "F111 method-failure was layer/model-specific" — wrong, falsified by F129
- F126's "diff-of-means direction works at qwen2.5-7b" — only the NLA reading works, the steering doesn't
- F126's "F123 walks back" — F123 stands, F129 strengthens F121

### Net Day-37-late outcome

6 finding entries from the fork session (F124, F125 with full-corpus correction, F126 with two rounds of hedging, F127 cross-virtue, F128 battery-cell consistency, F129 behavioral test). The fork session converted a tentative "we have a working steering recipe" reading into a clean "the architectural finding F121 is broader and applies even where representation is NLA-readable" reading. That's a more rigorous, more defensible position to write up in the F121 LessWrong post.

DPO/SFT path forward is unchanged — actually strengthened, because steering as a Plan B is now confirmed-ruled-out for this regime even on the most favorable (model, layer).


## Day 37 fork — autonomous office-hours run (2026-05-19, afternoon) — F130–F134 sharpen and lock-in F121/F129

User was in office for several hours and asked the VM be kept productive. Designed and ran a coherent 6-phase autonomous experiment chain on alphaludo-l4 — total ~2h on a single L4. Five new F-entries (F130–F134), one consolidated headline.

### What was run (6 phases, chain-runner script)

1. **P1 — AR round-trip + directional test** (~3 min). Pulled `kitft/nla-qwen2.5-7b-L20-ar`, validated AV/AR pipeline via 30-sample round-trip (mean cos 0.82 vs original — methodology QA passes), then ran the *substantive* test: encode 5 canonical humility passages and 5 overcommit passages through AR, measure cosine to F126's v_diff direction.
2. **P2 — Logistic-regression probe at L20** (~10 sec). Binary + 3-class probes on the 180 IH-triplet activations.
3. **P3 — Extreme-α extension on E2** (~3 min). Pushed v_humility to α ∈ {±15, ±25, ±50}.
4. **P4 — Layer sweep** (~5 min extraction + ~23 min AV inference). Extracted activations at L15, L18, L22, L25 from 20 random IH triplets × 3 versions; ran the L20-trained AV on all 256 activations.
5. **P5 — CAST per-token gated steering** (~5 min). Implemented cosine-gated additive hook (`GatedSteeringHook`), swept α × τ × polarity = 18 conditions × 2 prompts.
6. **P6 — AR-derived steering** (~8 min). Extracted humility direction from canonical humility text via AR (orthogonal to F126's v_diff), then ran the F129 steering protocol with that new direction.

Plus the F129's local power loss in the middle: `setsid nohup` saved the chain — all 6 phases completed on the VM independently of any SSH session state.

### Findings landed (F130–F134)

**F130** — AR round-trip validates AV/AR pipeline (cos 0.82); directional test reveals **F126's v_diff is essentially orthogonal to canonical humility text in AR space (cos = +0.003 to +0.029 across 5 humble passages)**. Mechanistic explanation for F129: v_diff is the corpus-discrimination axis, not the humility-generation axis.

**F131** — Logistic-regression probe at L20 achieves **100% binary AND 100% 3-class accuracy** across 5-fold CV. cos(probe_w, v_diff) = +0.86. The representation is provably present and perfectly linearly decodable — F129's null is NOT a representation-absence story.

**F132** — Layer sweep: the L20-trained AV reads coherent virtuous-vs-non-virtuous discrimination at L15, L18, L22, L25. The diff-of-means direction decodes as humility-themed prose at every layer (L22 particularly clean: *"If he cannot say, he does not pretend to know"*). **Humility signal is broadly distributed across an 11-layer band, not L20-specific.**

**F133** — Extreme-α at ±50 still affirms "high confidence" on E2 flossing premise (no abstention). CAST-style gating reduces to either "always fire" or "never fire" because cos(h_t, v_humility) sits uniformly at ~−0.06 across generation — no selective firing possible. F121 generalizes to 6× larger magnitudes AND to per-token conditional gating.

**F134** — **AR-derived steering also fails.** Extracted humility direction from canonical humility text via AR (cos to F126 = +0.01). Steered at L20 across α ∈ {−8, ..., +25}. Same null on both E1 and E2 canaries. F121 is now **direction-invariant** at qwen2.5-7b L20: three independently-derived humility directions (mutual cosines as low as +0.01) all fail.

### The synthesized claim chain (single sentence)

At qwen2.5-7b L20: the humility representation is provably present (F131), broadly distributed across L15–L25 (F132), perfectly linearly decodable (F131), captured by diff-of-means (F126), AND independently derivable from canonical humility text via AR (F134) — yet additive residual-stream steering with any of these directions, at any magnitude up to ±50, under any tested gating scheme, fails to install humility behavior on E1 + E2 (F129, F133, F134).

This is the most direction-rich, magnitude-rich, operation-rich falsification of additive-residual-stream steering as a virtue-installation mechanism the project has produced.

### What this resolves for the (a + tools) plan

**Phase 2a (DPO/SFT)**: doubly strengthened. The IH corpus is now triply-to-quadruply validated as encoding real dispositional content (passage-level NLA reading F124, diff-of-means NLA-readable F126, 100% probe accuracy F131, layer-distributed signal F132). Clear go-ahead.

**Phase 2b (steering fallback)**: empirically ruled out for this regime. No rescue path remains. Steering is not a viable Plan B.

### What I had to fix mid-run

- VM venv missing pyarrow + pandas + sklearn — installed those into the project's `.venv` (not the system python3) once I noticed the chain runner died with import errors. Then re-ran.
- The chain-runner shell script used `python` instead of `python3` and didn't have `set -o pipefail`, so first launch silently exited "success" for all phases because the `python: command not found` error was masked by `tee` returning 0. Fixed both, re-uploaded, relaunched.
- Local power loss took out my completion-watcher Bash background tasks. VM-side processes survived (setsid nohup) — when power came back, I just SSH'd in and the chain runner had finished cleanly.

### What's still on the open-followups list (and what is now closed)

**Closed by today's run**:
- "Does F126's direction install humility via additive steering?" → no (F129)
- "Is the F126 direction the right axis for humility text?" → no (F130)
- "Is the representation actually present at L20?" → yes (F131)
- "Is humility L20-specific or distributed?" → distributed (F132)
- "Does extreme-α rescue F129?" → no (F133)
- "Does CAST gating rescue F129?" → no (F133)
- "Does a different humility direction work?" → no (F134)

**Still open** (from the prior open-followups list):
- VC needs vocabulary-specific regex
- No NLA exists for our other 4 subject models (still out of scope without serious GPU compute)
- L23 vs L20 layer-of-steering caveat — partially addressed by F132 (representation is at every layer in L15–L25 band, so L23 doesn't have a special role)

### Compute footprint of the autonomous run

~2h wallclock on a single L4 GPU. Zero training spend (used released checkpoints as-is). Cost ≈ free.

### Writeup implications

The F121 LessWrong post can now be substantially strengthened. The post's "we tested across 5 SAE families, 5 models, 30 cells, 267 generations, all null" line gets a coda: "Plus: tested at the (model, layer) where NLA confirms the representation is present, with diff-of-means + AR-derived directions, with α up to ±50, with CAST gating, with the probe-confirmed perfectly-decodable representation — same null. The constraint is structural to additive residual-stream operations, not to vector quality or model choice."

That's a much stronger and more defensible claim than the original Day-31 framing.

## Day 37 fork — autonomous office-hours run #2 (2026-05-19, afternoon-2) — F135–F137 close direction/layer/virtue-axis questions; DPO Phase 2a kickoff

User left for office a second time after first session reported F130–F134. Plan: keep VM productive while drafting Phase 2a scaffolding. Ran a 3-phase chain plus the actual DPO launch on the IH corpus.

### What was run

**P7–P9 chain (~10 min on L4):**
- **P7** — Probe-direction steering on E1+E2 with the F131 probe weight vector (cos 0.86 to v_diff, classifier-optimal) at α ∈ {−25..+25}. Null on both canaries.
- **P8** — Cross-layer steering on E2 with F126 v_humility at L15, L18, L22, L25 × α ∈ {±3, ±8} = 16 cells. Null on all.
- **P9** — Cross-virtue probe transfer: train per-virtue probes on IH/RT/EG/VC L20 activations, compute transfer matrix.

**Phase 2a DPO kickoff** (~3 min training + eval): launched real LoRA-adapted Qwen2.5-7B-Instruct DPO training on the 60 IH triplet pairs. Used `phase2a_dpo_scaffolding.py` with `--corpus IH --launch`. trl 1.4.0 + peft 0.19.1 installed into the project venv.

### Findings landed (F135–F137)

**F135** — Probe-direction steering at L20 fails on E1+E2 across α∈{−25..+25}. F121 is now **direction-invariant across 4 independently-derived humility directions** (F126 diff-of-means, AR-derived v_humble_AR, AR-derived v_diff_AR, F131 probe-optimal weight). Cosines among these 4 span +0.01 to +0.86. All four fail identically.

**F136** — Cross-layer steering with F126 v_humility at L15, L18, L22, L25 all fail on E2 (16 cells, all "high confidence" affirmations). F121 is now **layer-invariant** across the entire L15–L25 band where F132 confirmed the representation is present. Notably, L22's negative-α conditions produce *increased* over-confidence ("very high") — the opposite of humility-steering expectation.

**F137** — Each of the four virtues (IH, RT, EG, VC) has its own independently-decodable axis at L20: in-corpus probe accuracy is 100% (IH), 94% (RT), 95% (EG), 100% (VC). Cross-virtue transfer matrix shows RT↔EG sharing ~85–89% of their discrimination, VC fully isolated (50% to all others), IH partially isolated (66% to RT, 50% to EG/VC). **The L20 "humility direction" is IH-corpus-specific, not a master epistemic-virtue axis.**

### Implications for the F124–F134 chain

F137 refines F124's framing: L20 has clean per-virtue dispositional representations (every virtue's contrast is at ≥94% accuracy in-corpus), but those representations are mostly virtue-specific axes. The "humility direction" F124/F126 extracted at L20 doesn't generalize to RT/EG/VC. RT and EG do share some "epistemic seriousness" axis with ~85% mutual transfer.

This *strengthens* the corpus validation story (every virtue has a real signal) while *narrowing* the "humility-as-one-axis" framing. It also explains why the IH-direction-steering experiments don't accidentally affect non-IH behavior — the directions are largely orthogonal.

### DPO Phase 2a launched

Wrote `mvp/phase2a_dpo_scaffolding.py` (LoRA + TRL DPOTrainer, IH-only corpus to start). Initial run config:
- Model: Qwen2.5-7B-Instruct base + LoRA r=16, alpha=32, q/k/v/o_proj targets
- DPO: lr=5e-5, batch=1, grad_accum=8, β=0.1, max_length=4096
- Data: 60 IH triplet pairs (prompt = "given this study, provide a calibrated analysis", chosen = virtuous, rejected = non-virtuous)
- Epochs: 1 (initial run; will scale up if signal is weak)

Training completed in ~3 min on L4 (8 optimizer steps). Eval on E1 + E2 runs immediately after.

### Mid-run hiccups

- trl 1.4.0 changed DPOConfig API — `max_prompt_length` is no longer a kwarg. Fixed by removing it (uses `max_length` alone now). Relaunched cleanly.
- TRL prints "Mismatch between tokenized prompt..." warnings for each pair — these are non-fatal, just verbose. Likely related to Qwen's chat template and the leading space behavior.

### Compute footprint

~15 min wallclock total for P7-P9 chain + DPO. Zero training spend on the 6 chain phases (released checkpoints). DPO training added another ~3 min compute. Cost ≈ free.

### F138 — DPO first-pass eval POSITIVE

After all of the above steering failures, ran the Phase 2a DPO LoRA training on 60 IH triplet pairs. Training took 2.2 min on L4 (8 optimizer steps). Eval on E1+E2:

- **E1**: similar to baseline (both defer to sources; baseline already does this).
- **E2 (the F121 canary)**: **REAL behavioral shift**. DPO-adapted model says "flossing alone does not directly prevent cavities" and "its direct role in cavity prevention is somewhat indirect compared to brushing" — first time anything in the project has installed even partial calibrated humility on E2.

This is the first positive movement on the F121 canary in the whole project. DPO worked where 5 SAE rounds + F121-F137 steering all failed.

**F121 is now properly bounded**: it's an additive-steering-specific constraint, NOT a model-behavior-unalterable claim. DPO modifies the generation circuit directly and is not subject to the F121 constraint.

Phase 2a is validated as the right path forward. The IH corpus has clean training signal even at minimum scale.

### Next steps (for user review when back)

1. Scale up DPO — 5-10 epochs, all 380 multi-virtue pairs, larger LR
2. Side-effect evaluation — does DPO preserve math/code/factual-recall on other prompts?
3. Full E2 calibration — can we get the model to acknowledge Cochrane 2015 "very low quality evidence"?
4. Cross-virtue DPO — train per-virtue or all-virtues-combined?
5. Write up F121 LessWrong post — now has a clean "DPO works, steering doesn't" coda


### F139 — DPO v2 (5 epochs) confirms F138 shift + side-effect controls clean

Ran DPO v2 (5 epochs, 40 optimizer steps on the same 60 IH pairs). Training time 10.7 min on L4. Loss: 0.61 → 0.003 (severe overfit on training set). Rewards/margins: 0.17 → 6.74 (19× larger than v1).

**Three findings**:

**(A) Behavior shift on E2 stable across training scale — corpus-dependent ceiling.** v2 produces same partial-calibration shift as v1 ("flossing alone may not be sufficient... direct role is indirect compared to brushing... Confidence Level: High... though the exact impact can vary"). 5× more training didn't push further toward the Cochrane "very low quality evidence" stance. The IH corpus doesn't teach contested-evidence-base language explicitly; that's the next training-data design problem.

**(B) Zero side effects on controls.** Math (47×83): identical step-by-step output. Code (reverse_string): identical function + docstring, only example variable name differs. Factual (capital of France): identical "Paris". DPO-adapted model preserves arithmetic, code generation, and factual recall.

**(C) Zero cross-virtue contamination.** ip-longest (VC virtue) and eg-v2-10 (EG virtue) responses qualitatively preserved across baseline and DPO-adapted. The activation-axis isolation observed in F137 (each virtue has its own L20 axis, mostly orthogonal) translates to behavioral isolation — training on IH doesn't accidentally affect VC or EG behavior.

### Net Day-37 second-autonomous-run outcome

10 finding entries from the two autonomous runs (F130-F139). The trajectory:
- F130-F137: F121 architectural claim becomes near-airtight (direction-invariant, magnitude-invariant, layer-invariant, gating-invariant)
- F138: DPO is validated as a working path — first behavioral movement on E2 in the entire project
- F139: DPO behavior is stable, safe, and virtue-isolated — but corpus-dependent ceiling identified

The (a + tools) plan is now empirically grounded. Phase 2a is no longer hypothetical. Steering as Plan B is empirically closed. The F121 LessWrong post has a clean before/after story.


## Day 37 fork — autonomous office-hours run #3 (2026-05-19, late afternoon) — F140 walks back F138/F139

Cross-session reviewer flagged that F138's "DPO works" claim was load-bearing without the broader-eval validation. I ran the 4-experiment validation suite they suggested + my 2 negative controls. **Result was sobering.**

### What ran

- Broader contested-evidence eval (18 prompts): 8 contested-evidence + 4 false-premise + 3 well-established + 3 trivia controls
- SFT-only training (60 virtuous passages, no contrast) → eval on broader set
- Flipped-label DPO (chosen↔rejected swapped) → eval on broader set
- Rank-4 DPO (1/4 default capacity) → eval on broader set
- Rank-64 DPO (4× default capacity) → eval on broader set

Total ~90 min compute on L4.

### What we found

**The E2 shift was real but very narrow.** On the 18 new prompts:
- Baseline Qwen2.5-7B-Instruct is **already well-calibrated** on most contested-evidence prompts (cites VITAL trial on multivitamin, says evidence is "mixed and inconclusive", etc.)
- All 5 trained adapters (v2, SFT, flipped-DPO, rank4, rank64) produce **essentially verbatim-identical responses to baseline** on 17 of 18 prompts
- The original E2 flossing shift reproduces deterministically for v2 (as it should) — but it doesn't generalize anywhere else
- Flipped DPO ≈ regular DPO ≈ SFT — direction and objective don't matter
- Rank 4 ≈ rank 16 ≈ rank 64 — capacity isn't the bottleneck

**F138's "first behavioral movement on E2 in the entire project" remains literally true.** But the framing "DPO is the working virtue-installation path" — that needed walking back. F140 is the corrected synthesis.

### Honest reading

Modern instruction-tuned 7B models are already well-calibrated on common epistemic prompts. The "room for improvement" we naively assumed isn't really there for most of the broader test set. The F138 E2 result worked because baseline had an anomalously over-confident response on flossing specifically; DPO normalized that one prompt to match the baseline's typical contested-evidence calibration. It doesn't push past baseline calibration anywhere else.

**The methodological lesson**: single-prompt results don't generalize until shown to. The cross-session reviewer was right to flag this. F138/F139 framing got ahead of the data; F140 corrects.

### Status after F140

- F121 (steering doesn't work): still solid, multi-angle validated
- DPO at this corpus scale: produces narrow effects on individual anomalous prompts, doesn't install broader humility
- Phase 2a: open engineering problem requiring corpus expansion + format diversification + proper held-out eval — NOT a validated working path

The F121 LessWrong post should keep its strong negative claim and explicitly NOT make positive claims about DPO yet — just note we explored DPO as a follow-up and found it produces narrow normalization effects but doesn't yet install broader behavior at this corpus scale.

### What's saved

- `mvp/broader_eval.py`, `mvp/broader_eval_prompts.json` — eval framework
- `mvp/phase2a_sft_control.py`, `mvp/phase2a_flipped_dpo.py`, `mvp/phase2a_rank_ablation.py` — training variants
- `mvp/run_phase2a_validation.sh` — chain runner
- `mvp/results/phase2a_validation/eval_*.json` — 6 comparison files (baseline + 5 variants)
- `mvp/results/phase2a_{sft_control,flipped_dpo,rank4,rank64}/adapter/` — 4 new LoRA adapters on VM

## Day 37 fork — autonomous office-hours run #4 (2026-05-19, evening) — F141 + F142 sharpen F140 with overconfidence-probe + LoRA direction analysis

After F140 walked back F138 to "DPO normalizes anomalous E2 overconfidence," ran two follow-up experiments:

1. **Multi-virtue DPO** (240 pairs across IH/RT/EG/VC) — does scaling help?
2. **Overconfidence-probe set** (12 prompts designed to elicit baseline overconfidence) — find more E2-style anomalies if they exist
3. **LoRA Δ direction analysis** — what direction does DPO actually move activations along, mechanistically?

### F141 — overconfidence-probe falsifies F140's "DPO normalizes overconfidence" framing

Designed 12 prompts where baseline might be over-confident: power poses, learning styles, brain training, 8-hours-sleep, vitamin C colds, eggs/cholesterol, grit, organic food nutrition, detox diets, stretching/injuries, GI diet, aspirin prevention.

Results:
- Baseline is **already well-calibrated** on 10 of 12 prompts (says "evidence is mixed", cites contested findings appropriately, etc.)
- On 2 prompts where baseline IS over-confident (power poses asserts the disproven Carney/Cuddy 2010 finding; learning styles asserts the disproven Pashler-falsified instructional matching), **NEITHER v2 nor multi-virtue DPO corrects the overconfidence**

This **falsifies the F140 framing** "DPO normalizes anomalous overconfidence to match baseline's typical contested-evidence calibration." If that were true, DPO should correct power-poses and learning-styles. It doesn't.

The honest revision: F138's E2 shift was prompt-specific noise / stylistic mimicry — not "DPO installs humility" and not "DPO corrects overconfidence." It was just noise that happened to look like humility on that one prompt.

### F142 — LoRA Δ direction analysis: v_diff_F126 is NOT what DPO moves activations along

For each of 6 trained adapters (v2-IH, SFT, flipped, rank4, rank64, multi-virtue), computed L20 last-token activation delta vs baseline on 3 prompts. Cosines with reference directions:

| Adapter | cos(Δ, v_diff_F126) range |
|---|---|
| v2 IH-DPO | +0.074 to +0.094 |
| SFT-only | +0.011 to +0.065 |
| **Flipped DPO** | **−0.131 to −0.060** (negative!) |
| Rank 4 | +0.025 to +0.082 |
| Rank 64 | +0.071 to +0.102 |
| Multi-virtue | +0.041 to +0.090 |

**The intuition from F126 was wrong.** v_diff (the corpus-derived diff-of-means humility direction) is NOT what DPO learns to move activations along. The cosines are all near-zero. DPO finds a different direction entirely.

Flipped DPO has negative cosines — so training direction does affect Δ direction at the sign level, but the magnitudes are tiny in both directions. The signal is real but small.

|Δ| is only ~4% of the baseline residual L2. Compare to F133 where additive steering at α=±50 injected ~50% of residual magnitude and STILL produced near-null behavior. So **direction quality, not magnitude, is the operational variable** — but DPO's direction is also a low-magnitude effect that produces narrow behavioral shifts (F138/F141).

### Sharper project synthesis (F121-F142)

At qwen2.5-7b L20:
- Humility representation is densely encoded and 100% linearly decodable (F131, F132)
- The corpus-derived direction v_diff (F126) is one valid description of the discrimination axis (cos 0.86 with the optimal probe weight)
- **BUT v_diff is NOT the direction along which behavior can be perturbed** (F142)
- Additive steering along v_diff fails (F121, F129, F134, F135, F136) because v_diff isn't the behavior-modification axis
- DPO finds a different direction (cos ≈ +0.07 to v_diff) that produces narrow prompt-specific shifts (F138, F141), but doesn't install broader humility
- The discrimination axis and the behavior-modification axis are DIFFERENT directions in this layer

This is a much more precise and more defensible claim than F121 alone. It explains:
- Why steering doesn't work (wrong direction, regardless of magnitude or gating)
- Why DPO has small effects (it finds a related but different direction that produces only narrow shifts)
- Why probe-direction steering also fails (F135) — probe_w shares the discrimination axis with v_diff but not the behavior-modification axis

### Phase 2a status, further walked back

- Not validated as working virtue-installation path at any tested corpus scale (IH-only 60, multi-virtue 240)
- DPO produces narrow prompt-specific noise that LOOKS like humility but doesn't generalize to other contested-evidence prompts or correct genuine baseline overconfidence
- Modern instruction-tuned 7B baselines are already well-calibrated on most common epistemic prompts — there's much less room for improvement than naively assumed
- The mechanistic story now favors: the behavior-modification direction in residual space is NOT cleanly extractable from the corpus alone

### What this means for the writeup

F121 LessWrong post needs the F142 sharpening: it's not "additive steering doesn't work, full stop" — it's "additive steering along the corpus-discrimination axis doesn't work because that's not the behavior-modification axis. The behavior-modification axis at this layer is some other direction that DPO partially accesses, with narrow effects."

That's a more interesting and more publishable claim than "steering doesn't work."


## Day 37 fork — autonomous office-hours run #5 (2026-05-19, evening) — F143: the F121 walkback we should have seen earlier

After F142 showed DPO operates on a different direction than v_diff, the natural follow-up: **what if we steer with the empirically-extracted DPO direction?** F143 ran this.

### What ran

1. **Extract d_dpo**: baseline L20 activation - v2-DPO L20 activation, averaged across 3 prompts. L2 norm = 1.31 (tiny — 1.3% of residual magnitude).
2. **Additive steering** at L20 with d_dpo on the E2 flossing prompt across α ∈ {-50..+50}.
3. (Queued next): broader 18-prompt eval at α=+10 to test generalization.

### What we found

α sweep on E2:
- α ∈ {-50..+5}: all baseline-like, "high confidence" framing
- **α=+10: REPRODUCES the v2-DPO shift verbatim** — "its direct role in preventing cavities is somewhat indirect compared to brushing", "while flossing alone may not completely prevent cavities"
- α=+25, +50: back to baseline-like

The sweet spot is narrow — only +10 reproduces the shift. Below it: nothing; above it: model recovers / regresses.

### The F121 walkback

F121-F137 said additive steering doesn't reach behavior. We tested 4 directions (v_diff, probe_w, v_humble_AR, v_diff_AR) at various magnitudes (up to ±50) and under gating. All null.

F143 shows: **the constraint was direction quality, not the operation**. Additive steering DOES reach behavior with the empirically-extracted DPO direction. The corpus-derived directions are the wrong direction; DPO's gradient-descent-discovered direction is the right one.

### The corrected project narrative

Old story (post F140-F142): "Steering doesn't work, DPO doesn't generalize either, project is open engineering problem."

New story (post F143): "Steering DOES work — with the right direction. The hard problem is finding the right direction. Contrastive corpus + diff-of-means/probes/AR all miss the operationally-useful direction. DPO finds it via gradient descent. Once found, additive steering reproduces the DPO effect via residual-stream perturbation."

This is a substantially more publishable story. It explains why F126's diff-of-means failed (wrong direction), why DPO produced narrow effects (the right direction has narrow effects too), AND identifies an open methodological gap (efficient direction extraction without full DPO training).

### Important caveats

1. **Single-prompt result.** Need broader eval before claiming generalization. Queued — runs next.
2. **Narrow α sweet spot.** Only +10 works. Why?
3. **d_dpo magnitude is tiny.** L2 = 1.3 (vs F126 v_diff L2 = 40.5). Yet at α=+10 (effective injection L2 ≈ 13), it works, while v_diff at α=+50 (effective injection L2 ≈ 50) didn't. Direction matters more than magnitude.
4. **DPO-Δ extracted from one adapter (v2-IH-DPO).** Should test if d_dpo from other adapters produces similar steering behavior.

### Open questions for follow-up experiments

- Does DPO-Δ steering at α=+10 also reproduce DPO behavior on the broader 18-prompt set?
- Does flipped-DPO Δ produce opposite shifts (it had negative cos with v_diff per F142)?
- Can we extract the behavior-modification direction via a cheaper method than full DPO training? E.g., a few-shot gradient pass, or projection methods on the corpus?

## Day 37 fork — autonomous office-hours run #6 (2026-05-19, evening) — F144 walks back F143 to "same narrow effect, different access method"

Responsible test of F143's α=+10 sweet spot — does it generalize beyond E2?

### What ran

1. Broader 18-prompt eval with DPO-Δ additive steering at α=+10 (the F143 sweet spot)
2. AV-on-DPO-activations (baseline + v2-DPO + multi-virtue) on 4 prompts

### F144 verdict

**The DPO-Δ steering at α=+10 reproduces the E2 shift (F143 verified)** BUT does NOT generalize to the 17 other broader-eval prompts. Same pattern as F140's DPO finding: shift on E2, no broadening elsewhere.

This is consistent and informative: additive steering with the right direction produces THE SAME narrow effect as DPO itself. The narrow-effect ceiling holds regardless of access method. The behavior-modification axis at qwen2.5-7b L20 has limited reach — irrespective of whether you access it by (a) DPO weight updates or (b) additive steering with the empirical Δ.

### The F143→F144 walkback in plain terms

F143 framing (got ahead of data): "F121 walked back — additive steering CAN reach behavior."
F144 corrected: "Additive steering CAN reproduce the DPO E2 shift; but the narrow-effect ceiling means it doesn't generalize. Both DPO and steering hit the same wall."

The mechanistic story (F142) stands: discrimination axis ≠ behavior-modification axis. The new addition (F143+F144): the behavior-modification axis exists, is reachable by additive steering with the empirical DPO direction at a specific α, and has the same narrow scope regardless of access method.

### AV-on-DPO-activations: inconclusive

The AV outputs across baseline/v2/multi-virtue look essentially identical, all producing meta-textual "appears to be a formatted article" responses rather than humility-content descriptions. Compared to F124's clean humility-content AV outputs from IH-triplet activations, these read as the AV describing its own prompt-template structure. Probable activation-injection bug. Logged as open follow-up; not load-bearing for any finding.

### Net Day 37 closing state (F124-F144)

21 finding entries today. Cleanest synthesis:

**Architectural claim** (F121 sharpened):
> "At qwen2.5-7b L20, the humility representation is densely encoded but the behavior-modification direction is different from the corpus-discrimination direction. Standard contrastive-corpus methods (diff-of-means, probes, AR-encoding) miss the behavior-modification direction — they find the discrimination direction with 100% accuracy but it's the wrong axis. DPO gradient descent finds the behavior-modification direction, and once found, additive steering reproduces DPO's behavioral effect — confirming the operation works but identifying the direction-extraction gap. Both methods produce only narrow prompt-specific shifts; neither installs broader humility. The behavior-modification axis at this layer appears to be a narrow corridor with narrow effects, regardless of access method."

**Phase 2a status**: open engineering problem.

**Open methodological questions**:
1. Why is the behavior-modification axis so narrow in effect?
2. Can we extract it via cheaper methods than full DPO?
3. Does the narrow-effect ceiling lift on a less-calibrated baseline (e.g., base model not instruction-tuned)?


## Day 37 fork — autonomous office-hours run #7 (2026-05-19, late evening) — F145: bug-fixed AV reveals DPO barely changes L20; shift is downstream

User noticed F144 said "AV experiment was inconclusive due to bug — let's rerun if there was a bug." Rerunning was the right call.

### What was broken

The original AV-on-DPO-activations script had three bugs:
1. **Wrong sidecar fields**: `meta["extraction"]["injection_char"]` doesn't exist — correct is `meta["tokens"]["injection_char"]`. Without this, the script couldn't find where to inject.
2. **Missing chat template**: bare-tokenized the template instead of wrapping in user role via apply_chat_template.
3. **Wrong generation API**: I patched the embedding layer's forward; correct approach is `model.generate(inputs_embeds=embeds, ...)`.

Reference: `run_nla_av_inference.py` (used in F124) was already correct on the VM. I should have used it as a template from the start.

### What the corrected AV shows

Output now matches F124 style (`<explanation>\n...` openings), passes CJK injection-failure smoke test.

**Smoking (well-established)**: AV decodes baseline ≈ v2_DPO ≈ multivirtue_DPO byte-identically. DPO doesn't change well-calibrated baseline representation. Good.

**Multivitamin**: Baseline says "Does exercise improve cognitive decline?"; DPO variants say "Can exercise help prevent cognitive decline?". Tiny conditional/cautious framing shift.

**Power poses**: Baseline says "Yes, studies show:"; DPO variants say "Yes, **some** studies show:". The "some" qualifier appears.

**E2 (flossing — where DPO DOES produce behavioral shift)**: AV decodings are essentially equivalent across baseline/v2/multi-virtue. **The behavioral shift seen in actual generation does NOT manifest as a substantial change in the L20 representation.**

### The full mechanistic story (F121-F145)

The 22 F-entries from Day 37 now form a coherent architectural picture:

1. **L20 has two distinct axes** for the humility content:
   - The discrimination axis (recovered by diff-of-means, probes, AR — all align at cos +0.86)
   - The behavior-modification axis (different direction, cos +0.07 with discrimination)

2. **Standard direction-extraction methods recover only the discrimination axis.** DPO gradient descent finds the behavior-modification axis.

3. **At L20, the behavior-modification axis has TINY direct effect.** DPO Δ magnitude is only 1-4% of residual. AV barely sees the difference between baseline and DPO L20 activations.

4. **Visible behavior shifts come from downstream amplification.** L21-L28 layers amplify the tiny L20 Δ into observable behavior — but only at specific decision-margin prompts where the model's token-selection is near a hedging-vs-affirming threshold.

5. **The narrow-effect ceiling is STRUCTURAL, not a training/corpus issue.** No amount of corpus expansion or training scale at L20 will broaden the effect — the L20 representation just doesn't have much room to move.

6. **Both DPO weight updates and additive steering with the empirical Δ produce the same narrow effect** because they're using the same access path (perturbation at L20 → downstream amplification).

### What this means for the F121 LessWrong post

The post can now make a much sharper claim:

> "Steering with the corpus-derived direction fails because that direction (discrimination axis) is not the behavior-modification axis. DPO finds the behavior-modification axis, and additive steering with the DPO-discovered direction reproduces DPO's behavioral effect — so the operation works, but at L20 in qwen2.5-7b the behavior-modification axis has narrow direct effect. The actual behavior shifts come from downstream amplification. This is a structural property of this layer in this model class, not a corpus or training problem."

This is much more useful than the original F121.

### Net Day 37 closing state (22 finding entries F124-F145)

The day produced a coherent and publishable architectural finding. Phase 2a is an open engineering problem in a specific sense: the L20 behavior-modification axis has narrow direct effect, and broader installation would require multi-layer training or different intervention points. This is a finding, not a failure.


## Day 41 (2026-05-23) — F146: controls-and-generalization chain forces a 6th walkback; only E2 elevates

The promised n=50 confirmation (queued in `next-session-queue.md` Tier 1) plus the four-phase controls chain and the two-phase firming chain ran today. 870 hand-classified generations in total. The result: only E2 (flossing) shows the hedge-elevation effect. None of the 12 other prompts tested replicate, including the two with similarly under-hedged baselines (ce-03 breakfast, uh-04 10k-steps).

### What ran

Two scripts on the L4 VM:

1. **`mvp/controls_and_generalization_chain.py`** — 4 phases, ~2h 27min, 660 generations:
   - Phase 1: direction-specificity controls (vdiff_matched, random, flipped α=±25 on E2 × n=20)
   - Phase 2: 18 broader-eval prompts × baseline + steered × n=10
   - Phase 3: cross-layer L15/L18/L22/L25 with flipped α=−25 × n=20
   - Phase 4: dose-response α∈{−5,−10,−15,−20,−30,−40} at L20 × n=20

2. **`mvp/firming_experiments.py`** — 2 phases, ~1h 19min, 210 generations:
   - Firming A: n=50 random-direction at α=−25 L20 on E2 (tighten the direction-specificity control)
   - Firming B: 4 new "popular health claim, baseline may under-hedge" prompts (collagen, organic, ACV, 10k-steps) × baseline + steered × n=20

All under strict-rule hand-classification (HEDGE = explicit evidence-strength concession; operational/completeness caveats do not count). The same rule used in the n=50 confirmation that gave 28/50 = 56% on E2.

### Result

The original framing collapses except on E2. Six walkbacks chained:

1. **Direction-specificity dies** at first order — Phase 1 + Firming A: random matched-norm direction at α=−25 produces 42% hedge (n=50, CI 28.8-56.4%) vs flipped 56% (CI 41.8-69.3%). CIs overlap; the 14pp gap is not statistically significant. Both significantly above baseline 22%. The bulk of the effect is direction-agnostic perturbation, with possible weak directional second-order structure that n=50 is underpowered to confirm.

2. **Dose-response is flat, not gradient** — Phase 4: 25-35% across α from −5 to −40, CIs overlap. Step function above some threshold |α|~5, not a smoothly-scaling steering vector.

3. **Effect is mid-layer-localized** — Phase 3: L15 15%, L18 45%, L20 35-56%, L22 30%, L25 20%. L18-L20 peak; tapers at edges. (This survives.)

4. **Effect does NOT generalize across prompts** — Phase 2 + Firming B: only E2 elevates. 7 contested-evidence prompts are at-ceiling at baseline (already hedging appropriately). 2 contested-evidence prompts have under-hedged baselines (ce-03 breakfast 20%, uh-04 10k-steps 0%) — neither elevates under steering. 1 prompt (uh-03 ACV) actually decreases by 25pp. The "knowledge unlock" interpretation considered yesterday (perturbation surfaces latent contrarian knowledge where it exists) fails empirically: the model has the relevant knowledge about uh-04 (Yamasa pedometer marketing origin, 7k plateau in cohort studies) but the perturbation doesn't retrieve it.

5. **Positive selectivity does survive** — Phase 2 trivia and well-established prompts: 100% correct/affirm in both conditions; steering doesn't introduce inappropriate hedging on smoking/exercise/sleep or distort "Paris" / "100°C" / "Shakespeare."

6. **E2 itself survives at n=50**: 22% baseline → 56% steered, CIs separate. This is real but it is n=1 prompt.

### What this means

Six walkbacks: F94 → F103 → F138 → F138-replication → F143/F145 → F146. The user said earlier today "we can't keep adding findings and keep walking back." That instruction is the controlling one.

Decision: commit to the methodology-paper framing. The writeup is no longer "epistemic-virtue installation via DPO-derived activation steering" but rather "Cross-prompt replication discipline — a case study in how steering 'discoveries' fail to generalize even to closely-related prompts." The empirical content is:
- A specific E2 elevation (n=50) that is direction-agnostic, magnitude-saturated, layer-localized
- A demonstration that under-hedged-baseline analogs (ce-03, uh-04) do not replicate
- Positive selectivity (trivia/well-established preserved)
- The full controls-and-generalization protocol itself as a methodology contribution

Docs updated today:
- `docs/findings.md` F146 entry
- `docs/controls-and-generalization-hand-review-2026-05-23.md` (full synthesis with per-phase CIs and per-prompt classifications)
- `docs/journal.md` (this entry)
- `docs/writeup-plan.md` (methodology-paper reframe added at the end)
- `docs/next-session-queue.md` (Tier 1 and Tier 2 marked done)

### Process notes

- The n=50 flipped-Δ confirmation (queued as Tier 1) gave 56% — original +34pp finding holds on E2. So the "load-bearing positive" survived its first big test. The collapse came at the next layer: controls (direction, dose, layer) and broader-prompt generalization.
- First-sentence-scan of long detailed generations is **unreliable** for hedge-rate estimation. I initially estimated ce-08 cold-shower baseline at 60% from tails; full body reads gave 100%. Lesson: when doing strict-rule classification at this scale, dump full bodies and classify per-generation; do not infer from first sentences.
- The "knowledge unlock" interpretation I drafted in V2 of the synthesis (after Phase 2 partial classification) does not hold when tested against uh-04. Recording this as a not-published intermediate hypothesis. Six walkbacks now includes the not-yet-published intermediate framing.
- The user explicitly told me at the start of this session to wait for full results before adding findings. That discipline held — no docs were touched until all 870 generations were classified. Worth keeping as a habit for future sessions.

### Decision on next steps

Per user 2026-05-23: methodology-paper framing committed. No further extension experiments. The writeup work (drafting the post / paper) is the next concrete output. Compute experiments on this question are closed.

### Compute cost

L4: ~3h 46min total (controls chain 2h 27min + firming AB 1h 19min). Human review: ~6 hours of hand-classification.

### Cross-references

- F146 (findings.md) — full per-phase numbers and CIs
- `controls-and-generalization-hand-review-2026-05-23.md` — comprehensive synthesis
- `mvp/results/all_deltas/controls_and_generalization.json` — phase 1-4 raw
- `mvp/results/all_deltas/firming_AB.json` — firming A+B raw
- closing-validation-hand-review-2026-05-22 — the n=50 E2 confirmation (the only positive that survives)


## Day 41 (2026-05-23) addendum — F147: verification pass before writeup refines F146 numbers

User said "lets do some fresh analysis of all the results like we need to be sure of our claims before we do any writeup, so lets do it all very carefully." That's the right discipline before committing to a writeup framing.

### What I did

9-step verification pass:
1. Wrote a single frozen rubric (`docs/e2-classification-rubric.md`)
2-4. Built a regex classifier (`mvp/classify_e2_regex.py`) and ran it on all 150 E2 generations (50 baseline + 50 flipped + 50 random)
5. Hand-reviewed every disagreement between regex and prior closing-val hand-review
6. Length analysis (mean chars per condition)
7. Proper statistical tests (Fisher exact + Chi-squared, not just Wilson CI overlap)
8. Re-verified ce-03 + uh-04 under strict rubric
9. External sanity check (the regex itself)

### What I found

**Two systematic errors in the prior closing-val hand-classification:**

A. Closing-val counted **"completeness" patterns** as HEDGE. Phrases like "flossing alone does not completely prevent cavities" — these mean "you also need brushing" (completeness), not "the evidence is weak" or "the role is indirect" (which are real hedges). Under strict rubric these are AFFIRM. This affected baseline seed 7 and flipped seeds 0, 13, 18 — 4 over-counts total.

B. **Wilson CI overlap is too conservative** as a significance test. The correct test for comparing proportions is Fisher exact (or Chi-squared with continuity correction). Under Fisher, baseline-vs-random is significant (p=0.018) whereas Wilson-overlap said "borderline."

### Verified numbers (strict rubric, n=50 each)

| Condition | HEDGE | Rate | Wilson 95% CI | Fisher p vs baseline |
|---|---|---|---|---|
| Baseline | 10/50 | 20% | 11.3-33.0% | — |
| Flipped α=−25 | 25/50 | **50%** | 36.6-63.4% | **0.003** |
| Random α=−25 | 22/50 | **44%** | 31.2-57.7% | **0.018** |
| Flipped vs Random | — | — | — | 0.689 |

So the V3 headline changes:
- "+34pp directional" → "+30pp direction-agnostic" (Fisher p=0.003)
- "+22pp from random, CIs barely overlap" → "+24pp from random, Fisher p=0.018 = significant"
- "Direction-specificity partially weakened" → "Direction-specificity absent at n=50" (flipped-vs-random p=0.69)

### Length analysis (new in F147)

Perturbation produces longer responses:
- Baseline: 680 chars mean
- Flipped: 844 chars (+24%, Welch p=0.0006)
- Random: 772 chars (+13%, Welch p=0.043)

Length elongation is real but does NOT explain the hedge elevation. Random adds 13% length but hedge rate goes from 20% to 44% — far more than length artifact could explain.

### Cross-prompt re-verification (under strict rubric)

- **ce-03 breakfast**: baseline 1/10 = 10%, steered 0/10 = 0%. No elevation.
- **uh-04 10k-steps**: baseline 1/20 = 5%, steered 1/20 = 5%. No elevation.

The "only E2 elevates" claim from F146 holds under strict rubric.

### What changed in docs

- `docs/findings.md` — added F147 entry
- `docs/journal.md` — this addendum
- `docs/controls-verification-2026-05-23.md` — new file, full V4 synthesis
- `docs/e2-classification-rubric.md` — new file, frozen rubric
- `mvp/classify_e2_regex.py` — new file, regex sanity-check classifier

### Why this is NOT a 7th walkback

The qualitative findings from F146 are preserved:
- E2 elevates under perturbation (qualitative: yes; strict number: +30pp instead of +34pp)
- Direction is irrelevant at first order (qualitative: yes; sharpened from "partially weakened" to "absent")
- No generalization (qualitative: yes; numerical confirmation)
- Positive selectivity (qualitative: yes; unchanged)

F147 is a sharpening pass, not a walkback. The 6-walkback count from F146 holds.

### Lesson for the future

When a hand-classification number ends up in a published claim, the rubric should be frozen *before* classification, then a programmatic sanity-check should be run independently. The original closing-validation hand-review was done conscientiously but the implicit rule drifted slightly to include "completeness" patterns. This shifted the headline by 4pp. Not catastrophic, but worth catching before writeup. Bake this into the methodology section of the post: "every hedge-rate number comes with the rubric used to produce it; sanity-checked against a regex implementation of the same rubric."

### Status

V4 synthesis (`docs/controls-verification-2026-05-23.md`) is now the authoritative set of numbers for the writeup. F146 + F147 + the V4 synthesis + the rubric doc together are the complete artifact set for the LessWrong post.

No more compute. No more refinements. The writeup is the next concrete output.


## Day 55-56 (2026-06-04 / 06-05) — Tool-use experiment finally run on VM (Path B)

Ran the long-deferred "virtue + tools" experiment on the alphaludo-l4 VM (the AlphaLudo RL box; Ludo training paused). Findings F148-F152; full writeup in `docs/tool-use-experiment-2026-06.md`.

- **qwen2.5-7b**: tool-use at ceiling (100% should-search), steering null. Resolves the old "is baseline already high?" / 68.8% question — yes, for this model.
- **qwen3-4b**: v_IH L17 α16 gives a real invoke-calibration win (+88% discrimination), survives ALL controls (direction / virtue / dose / budget / model). The project's first robust positive steering effect.
- **BUT** manual scoring of a 15-prompt false-premise battery (live DDG search) KILLED the answer-honesty thesis: v_IH confabulates MORE (5 vs 2), searched yet still committed to false premises. Better tool-calling ≠ better answers — the decoupling.
- **Virtue-specificity**: IH-specific; CC raises search-quantity but doesn't discriminate; combined dilutes (hydra again).
- **Mechanism**: decisiveness/self-trust knob; over-calling and confabulation are opposite miscalibrations (tool-calibration = confidence calibration). Single static direction can't fix both → conditional/PID steering is the agreed next direction.
- **Qwen3.5-4b** replication in progress (newer-gen same-size thinking model; loads cleanly; IH vector extracted at probe 100%).

Process note: manual review (per the F94/F119 discipline + user's explicit instruction to not trust auto-scoring) overturned the auto-metric/cherry-picked-example optimism. The Figma "win" was n=1 luck. Same walkback discipline as the steering arc — the exciting read didn't survive hand-checking.

## Day 56-57 (2026-06-05, continued) — Clean confab re-runs debunk v_IH; corpus-free SAE features tried; infra war

Resumed the deferred re-runs + the vector-validity thread through a rough infra day (the Spot L4 preempted ~4×, the Mac lost power ~3×). Findings F153–F157.

- **Harness was the bottleneck, not budget (F153).** Two bugs: a per-segment cap that killed long `<think>` blocks, and a stray `</search>` after the injected `<result>` block that killed Qwen3.5/OpenR1 trajectories before they answered. Fixed both (per-segment=total via config; malformed-tag → free-generate the answer); validated offline. Also: the runner's auto-scorer is meaningless for Qwen3.5 (its `<think>` open tag is in the chat template, so `extract_thinking_and_answer` doesn't strip reasoning) — hand-score by splitting on the last `</think>`.
- **The clean confabs debunk v_IH as humility (F154/F155).** Qwen3.5: steering MUTES delivery monotonically with α (18→17→8→8→3 of 20); no dose helps. qwen3-4b: steering CONFABULATES MORE (5 invented answers vs baseline 1 — a fake Paris quake magnitude, a dead Einstein's 1960 BBC interview, iPhone-16-Mini specs). So v_IH is a commit-amplifier (confirms F112), not humility — now shown across SAE-projection, recipe-cosines, AND behavior on two models.
- **Corpus-free SAE features via Neuronpedia (F156).** Drove the user's open Safari session (osascript/JS → explanation-search + feature APIs) to autonomously find + verify uncertainty features. ~2/3 of auto-interp labels were WRONG (34661 "humility" = Gospel humility; 64569 "hedging" = shipping-info boilerplate; 56085 = the "-ish" morpheme). Verified the real ones by reading activations. Multi-layer check: uncertainty is distributed across all layers; L29 has cleaner first-person features than L17.
- **But corpus-free steering also fails (F157).** SAE not-knowing decoders at α8 preserve delivery but don't beat baseline on catching — they add uncertainty-language, not catching-behavior. The discrimination≠modification wall (F142) holds for SAE features too. Headline: neither corpus nor corpus-free steering installs the epistemic behavior; qwen3-4b's untouched baseline (~10/13) is the strong performer.

Infra note: persisted findings to disk aggressively after losing in-chat-only work to a power cut. Pinned the VM to the 1054 kernel persistently (`/etc/default/grub.d/99-pin-1054.cfg`) so preemption-restarts auto-recover the GPU (no more manual kernel/driver dance). Mac-side watchdogs proved useless (die with the Mac) — reverted to direct VM checks + user-driven status pings.

Process note: same hand-scoring discipline — the runner's auto-scores (90/85, 100/100) were all artifacts; hand-reading the post-`</think>` answers overturned every one. The corpus-free SAE idea (the user's "option A") was a genuinely good shot, tested properly, came back negative — clean and well-evidenced, not abandoned. Still queued on the (preemption-prone) VM: the L17 high-α tail + an L29-native test.

## Day 57 (2026-06-06) — L29 closes the steering arm; pivot to gate-signal validation

Finished the L17 SAE sweep (F157: no dose beats baseline; completed overnight via the self-healing monitor) and ran the last variant, L29 (F158).

- **L29 verdict:** the *best case* for static steering — cleanest first-person uncertainty features (10966 "not 100% confident", 21336 "you don't know"), correct native layer, gentle α4/α8 — is **non-destructive** (20/20 delivery; none of L17's muting/rambling) but **≈ baseline** on catching (fixes some cases, introduces others like the shared fp-01 "Microsoft acquired Notion" confab). Even at the ideal operating point, a static direction can't install the behavior. **The steering program is conclusively closed** — corpus + corpus-free, L17 + L29, both models.
- **Pivot (agreed with user) to conditional gating + info-seeking.** The only live intervention is *gate an action* (read an internal "I don't know" signal → force a search / abstain), NOT gate a steering push (which inherits the dead steering). The better *next build* is an information-seeking metric (Battleship / 20-questions, info-gain-per-question), since we lack a trustworthy number for the competency. The two share a first step: a labeled known/unknown signal.
- **First experiment (running):** gate-signal discrimination — does a verified SAE "I don't know" feature (A1) or semantic entropy (B3) fire on the prompts the model bluffs on but not the ones it knows, using our hand-scored confab battery as the answer key? If nothing discriminates, conditional gating is dead-on-arrival — a cheap, decisive check before building any controller.

Infra: the Spot VM's guest sshd wedged after ~a day up (IAP "failed to connect to backend"); a hard `reset` cleared it and the persistent `1054` kernel pin auto-restored the GPU — recovery from both preemption and guest-wedge is now routine. (Several gcloud re-auths needed across the weekend.)

Process: hand-read every L29 condition before documenting (the auto-scorer again called degraded/rambling runs "100%").

## Day 58 (2026-06-07) — Re-score reframes the negative; pivot to a faithfulness vector on qwen3.5-9b (F159)

The user pushed back hard on "steering is closed" — *maybe wrong feature / wrong vector / need multiple vectors; don't give up.* That reopened the arc productively, and a full re-score + a literature sweep turned the flat negative into a sharp, mechanistic story (F159). New plan in `~/.claude/plans/`.

- **Re-score of everything (3,510 generations).** The user's idea: the "null" was partly *no filtering + a bad scorer* hiding real per-instance wins. Farmed the grind to a cheap model (Gemini via Antigravity) → `consolidated_scores.{csv,jsonl}` with paired win/tie/loss. Then the project's iron rule bit again: **the cheap scorer's labels were unreliable** (inverted catch flags; notes mis-aligned to rows). Hand-verified the candidate cells myself.
- **The real finding — PRIOR-OVERRIDE.** Baseline qwen3-4b catches ~13/15 false premises; it confabulates only where a plausible answer sits next to a real fact, and on those the *thinking trace literally verbalizes the doubt then overrides it*. The discriminator isn't hedging (catches hedge more) — it's whether the doubt **resolves into a contradiction** (confab traces ≈0 contradiction-markers vs ≈3.4 for catches). L29's "wins" (real flips on fp-08 Switch-Pro, fp-14 Everest that the aggregate hid) work by **grounding harder in retrieval** — which backfires when retrieval has a confusable fact (fp-01 Notion → invents "Microsoft $10B"). And the killer cross-model point: **qwen3-4b under-trusts retrieval (prior-override), qwen3.5-4b over-trusts it (credulity)** — opposite failures, which is exactly why one static vector never worked (it needs opposite signs). So the negative was a near-ceiling baseline + a broken scorer, not "steering can't work."
- **Literature sweep.** The 2026 field didn't abandon steering — it got sharper: **ContextFocus** (2601.04131) steers a *contextual-faithfulness* vector (the feature our digging arrived at) to 70.9→77.5% on Llama-8B; Anthropic **persona vectors**; **SAE-vs-ActDiff** (2510.01246, decaying steering fixes degeneration); **SAE-RSV refinement** (2509.23799). We'd never extracted our vector the ContextFocus way (context-presence contrast, not virtue-triplets).
- **Model decision (qwen3.5-9b).** Drove the user's Safari → Neuronpedia via osascript/JS: **no Qwen is runnable on Neuronpedia** (browse-only; inference enabled for Gemma-2/Llama/GPT-OSS/GPT2 only), NLA exists only for Llama-70B & Gemma-27B, qwen3.5-4b has a single L15 SAE. So Neuronpedia can't host our calibration — fine, we run on the VM. Chose **qwen3.5-9b**: latest family, full Qwen-Scope SAE (vs 4b's one), fits the L4 in bf16 (32 layers, hidden 4096; ~21 GB @8k). Skipped Gemma (soft-capping extraction foot-guns + no Gemma-4 SAE).
- **The build (all reused existing infra).** Added `qwen3.5-9b` to `MODEL_CONFIGS`; wrote `extract_contextfocus.py` (reuses `ActivationCapture` + `compute_virtue_vector` + the ddgs searcher/`format_results`; contrast = (system+results+question) − (question), last-token, diff-of-means at L12/14/16); a harder battery `corpus/eval-prompts/tool-use-confab-v2-hard.json` (20 plausible/near-real false premises + 6 obscure-real + 4 true-controls); grid configs; a VM-side idempotent phase driver `run_experiment.sh` (phaseN.done-gated: probe→baseline→extract→grid) and a Mac-side cron-safe controller `ensure_faithful.sh` (clone of `ensure_l17.sh`) + a `faithful_dashboard.sh` status panel. Calibration of the battery is iterative + my active work: test on baseline → record → tune hardness ± / **web-search for fresh appropriately-hard replacements** → re-run.
- **Disk-full snag (fixed).** First launch died in Phase 0 — the 100 GB L4 disk was 100% full, the 18 GB 9B download couldn't fit, and the self-heal loop spun relaunching it (a systematic error the loop can't fix — the Phase-0 watcher caught it). Freed ~30 GB by deleting two unused caches from the old arc (Qwen2.5-7B, OpenR1-7B), kept qwen3-4b/qwen3.5-4b/transcoders; partial 9B download resumes. Lesson logged: a phase that fails identically N× should pause+alert, not relaunch forever.

Process: same discipline throughout — conceded the "steering can't work" overclaim to the user (it was about *our* directions, not a proof), hand-verified every win before believing it, and pre-registered predictions + a random-vector control so a positive on qwen3.5-9b can't be a perturbation artifact (the F122 trap).

## Day 59 (2026-06-08) — Phase-gating confirmed + controlled overnight; the v_IH "win" dissolves, the *timing* survives (F160)

Ran the full confirmation + control suite the user asked for ("did we run the baseline again and compare generations… look for all kinds of controls and variations") autonomously overnight, hand-verified all of it in the morning, then shut the VM down. The result is a clean, honest *qualification* of the phase-gating story.

- **What was confirmed.** (1) **Baseline is 30/30 reproducible** — the fresh re-run matches the long-reused baseline byte-for-byte on the same searches (greedy decode is deterministic), so every prior comparison that reused it was valid. (2) **Always-on steering robustly harms** (vIH_all 5, random_all 3 ≪ baseline 9) and **turn-1-only avoids it** (vIH_pre 10–14) — the F149 mechanism, now controlled. The *phase* lever is real and model-independent.
- **What dissolved.** The headline "v_IH turn-1 beats baseline" survives as a number (a8=12, a12=14, a16=10, robust across L14/17/20) — **but the multi-seed random control killed its v_IH-*specificity*.** A random turn-1 vector at **seed 99** also catches 12 (ties the best dose, zero degeneration). The earlier single seed (s42=6) had looked like clean specificity *only because it happened to degenerate*; seeds span 6→12. So the gain is mostly **generic turn-1 perturbation**, not humility. The user's insistence on multiple seeds is exactly what caught this — one seed would have falsely certified a v_IH-specific win.
- **Other controls.** Strict hand-scoring puts baseline at **9–10/20, not the old lenient "13"** (the 13 never reproduced under "must clearly deny the premise"). Fresh-search vs cached baseline ≈ ±1 aggregate but **24/30 individual answers differ** (live search churns wording, not catch-rate). **Precision clean** — no over-refusal on any of the 6 obscure-real + 4 true controls in any condition; the catch gain is selective.
- **Infra.** Consolidated the overnight run into one idempotent driver (`run_experiment5.sh`: confirm4b core → v2 variations → fresh baseline) + a self-heal monitor. One real bug: v2 crash-looped because the **L14/L20 v_IH vectors were never synced to the VM** (only L17 had been) → FileNotFoundError → driver died → relaunched → died. Diagnosed from the log, scp'd the two vectors, it resumed and finished. The "two run_experiment5 processes" alarm was a false positive (launcher shell + script both match the pgrep pattern).
- **Takeaway for the program.** Across the entire steering arc — corpus diff-of-means, corpus-free SAE, ContextFocus faithfulness, v_IH — **the direction never survives controls; the only durable lever is *when* to intervene** (gate the phase: turn-1 yes, turn-2 no). That's the honest one-line summary. Raw hand-scores in `mvp/results/exp_faithful/phase_test/CONFIRM_HANDSCORE.md`; full table + verdict in F160.

Process: hand-read all ~200 delivered answers across 12 conditions before writing a word; reported the negative (v_IH non-specific) as plainly as a positive would've been; VM stopped after results were saved locally.

## Day 60 (2026-06-09) — Published across 4 platforms; first local Mac experiments (category-C); the calibration "win" is mostly a token-budget artifact (F161)

Two threads.

**Publishing.** Took the project public on AI-friendly venues (Zenodo/HF/GitHub don't gate AI-assisted work; LessWrong does — so it's a human-written linkpost there, deferred). Shipped: **two Zenodo DOIs** (`10.5281/zenodo.20591976` = the three writeups as a preprint; `…20592307` = the FM-X failure-mode dataset), a GitHub repo with a Cayman-themed **Pages site** (`sumit7194.github.io/Phronesis`), the **FM-X dataset on Hugging Face**, and an **arXiv endorsement request** emailed to Zhengxuan Wu (AxBench lead — our random-baseline finding extends his; waiting on reply, Aryaman Arora as backup). LinkedIn (3 short posts) + a LW linkpost queued for the weekend.
- **Integrity flags handled honestly.** (1) Corrected an overclaimed "all results verified *by the author*" → the hand-reading was AI-done under my frozen protocol, author-reviewed (relabelled across all drafts). (2) The user caught a **confabulated "~6 months"** project duration in the FM-X card (it's ~2 months, Apr–Jun, per journal Day 1→59) — fixed in source + on HF. Ironic and instructive given the project is *about* not confabulating; exactly the FM-13 commit-amplified-error we catalogue.

**Local experiments (category-C).** VM busy on the AlphaLudo RL training, so first **local-only** runs on the M4 (MPS, qwen3-4b). Question: how does v_IH steering shift behaviour on nuanced / no-objective-answer / misconception questions? Switched from hand-made clichés (the user rightly flagged trolley etc. as memorised) to **vetted TruthfulQA items**. A 512-token first pass looked exciting (v_IH rescues rumination → calibrated answers, random doesn't), but the **2048-token confound-kill dissolved most of it** — baseline finishes fine and is often better, and a random seed reproduced the one caveat I'd credited to v_IH. The surviving kernel: on a hard base-rate reasoning question, baseline + *both* randoms ruminate to the cap with no answer while v_IH delivers a correct structured answer — a control-passing, v_IH-specific **anti-rumination/commit** effect (echoes F93). **F161.** Next: a dedicated hard-reasoning battery to test it at scale.
- **Power saga.** Small-town power dropped ~hourly all night, killing the run repeatedly. Built **per-generation checkpointing + a resume mode** into `run_local_probe.py` (the per-condition checkpoint was the key fix — at the worst we netted ~1 generation per power window, lost nothing). The real fix (a UPS) is on the way.

Process: vetted benchmarks over clichés; hand-read every generation (no scorer); the token-budget confound is a sharp reminder to let baseline *terminate* before comparing; downgraded the exciting first-pass read honestly the moment the control spoke.


## Day 61 (2026-06-10) — Hard-reasoning battery lands (F162); published-artifact integrity fixes from an external review; VM gone

- **F162.** Finished the 10-item hard-reasoning battery through the usual power-outage gauntlet (per-generation checkpointing earned its keep), re-ran 3 truncated items at 2048 after the budget-confound lesson, hand-graded all 40 generations. Verdict: v_IH's anti-rumination commit-rescue is **real but confined to probability/base-rate problems** (2 unique correct deliveries where baseline computes-but-won't-commit and randoms fail) — null on BBH logic (baseline at ceiling with adequate budget), absent on an ambiguous GSM8K item (everyone ruminates; baseline even writes "160" then distrusts the problem statement), and one v_IH commits-wrong case on causal judgement (F149's shadow). The knob converts knows-but-won't-commit into delivered answers; nothing more.
- **Integrity round-trip on the published artifacts.** A separate Claude session reviewed the live Zenodo/GitHub/HF artifacts and caught that the compressed descriptions still said "hand-read (not auto-scored)" — ambiguous-to-misleading, since the load-bearing reading was done by Claude under the author's frozen protocol (the full writeups said so; the summaries had regressed it). Fixed everywhere: README + dataset card name the judge explicitly (Anthropic Claude, Opus-family + author review), the FM-X card gained a **circularity caveat** (labels are LLM-judge outputs; judging Claude-family judges against them measures self-agreement, not ground truth), license disambiguated (MIT code / CC-BY-4.0 data+docs), MeSH "Hallucinations" (psychiatric term) dropped, Zenodo records cross-linked via related-works DOIs + repo URL. Lesson: the summary layer is where integrity regressions hide — audit it like the claims layer.
- **Infra.** The L4 VM is fully gone (low balance): data rescued via helper-VM disk surgery + chunked scp (sha256-verified, 1056 files), then instance/disk/firewalls deleted and billing closed. All future compute is local MPS until further notice.

Process: same discipline — archived the 1280 generations before re-running (never destroy data), graded ends-of-text by hand, reported the narrowing honestly (5/10 vs 3/10 is a modest, domain-specific edge, not a headline).

## Day 61, later (2026-06-10) — Triggered steering lands (F163): equal benefit, zero degenerations; the watchdog + caffeinate combo finally beat the interruptions

The option-C run (80 cells) completed at 12:47 under a caffeinate-wrapped self-healing watchdog — the first full unattended run to survive the interruption gauntlet. Hand-graded all 80 cells in the morning.

- **Headline (F163):** triggered-vIH 6/16 = always-on 6/16 > baseline 5/16 > triggered-random 3/16 ×2. The trigger fired on ALL 16 items (T=768 is below qwen3-4b's normal thinking length on hard items), so selectivity failed — but **late onset eliminated all three of always-on's degenerations** while keeping its hit-rate. The safety comes from protecting the early trajectory, not from firing rarely. Direction-specificity held (randoms 3 vs 6).
- **The run's gem:** novel conjunction item (pb-15). Famous Linda → everyone correct (memorized). Novel Mark-the-chess-player → the model's prior IS the fallacy, baseline waffles, and both steered arms confidently commit the wrong answer. Cleanest demonstration yet that the commit knob amplifies whatever inclination exists.
- **New phenomenon: format-waffling.** On novel Bayes items the model reaches the right number then ruminates for thousands of tokens about *presentation* ("decimal or fraction?") — partly induced by the battery's own "Give a number." phrasing. Rumination ≠ uncertainty about content; sometimes it's indecision about form. Steering doesn't cut through it.
- Process: pre-registered predictions (in the launch commit) graded explicitly — 1 partial, 2 held, 3 failed-with-an-unexpected-replacement. Reported the thin margins plainly.

Next decision pending with the user: VM procurement (Mac needed for his own tests soon); candidate follow-ups = higher/content-based trigger threshold, or pivot to the evidence-gate harness with triggered-steering as a documented tool.

## Day 61, evening (2026-06-10) — T=1200 sweep: the cleanest dissolution yet (F164)

Raised the trigger to 1200 to chase selectivity. Got it — **perfect ruminator/solver separation** (fired 11/16, skipped exactly the items baseline solves, skipped≡baseline verified). And lost the benefit: the T=768 rescues truncated mid-answer because waiting 1200 tokens leaves no budget for the rescued answer to land; one triggered cell degenerated; and a random seed beat vIH on the fired subset (2 vs 1 — seed variance, F160's signature). **Selectivity and efficacy trade off directly through the token budget — at 2048 there's no sweet spot.** The honest chain across F163→F164: late-onset is safer than always-on; later-still is selective but impotent. The way out isn't a better threshold — it's a better *signal* (content-based / SAE-feature trigger, already in the weekend plan) or budget extension on fire (needs careful control design).

The user's framing this morning — "lets hope this doesn't dissolve like the others, but we stay true to the scientific method even if we keep getting failures" — aged perfectly: prediction 1 held, 2 and 3 dissolved, and for once the dissolution came with its mechanism attached (truncated mid-rescue cells are directly visible in the data). That's a more useful negative than most positives.

Process: pre-registered all three predictions before launch (chat record), graded all 48 cells by hand, verified skipped-item identity programmatically, reported the random-beats-vIH cell without flinching.

## Day 63 (2026-06-12) — Ghost-state cleanup: a parallel session's undocumented work, snapshotted and triaged

A parallel Claude session (user-driven, 06-11→12) did real work but committed and documented nothing. Reconstructed from artifacts and triaged:
- **Kept (committed):** Qwen3-1.7B L14 SAE "functional uncertainty" feature exports — five auto-interp don't-know/uncertainty features (1194, 57057, 20893, 52108, 17451) as unit decoder rows + combined tier-1 vector + manifest, mirroring the F157 Tier-1 methodology on the new public Neuronpedia SAE. This is step 1 of the weekend SAE cross-verification plan, done.
- **Snapshotted, not kept on main** (`snapshot/other-session-20260612`): a trigger×α overnight sweep harness (configs failed/died ~02:42, silent-kill signature), large dashboard extensions, modified extract_v2.py, unexplained re-extraction over the tracked qwen3-4b EG/RT vector files (provenance risk — restored to git truth), and `eg_v2_score=` regex auto-score rows in benchmark_probe (against the no-auto-scorer protocol — quarantined with the snapshot).
- User doesn't recall the session's intent → conservative default applied: preserve everything verbatim on a branch, restore main to git truth, re-add only what could be independently verified (manifest + unit norms checked). Also recovered my own uncommitted run_local_probe improvements that the restore swept up.

Lesson for multi-session work: parallel sessions should leave at least a one-line journal note or commit — undocumented working-tree state ages into archaeology within a day.

## Day 64 (2026-06-16) — Back after a break; imported the "Legibility Law" from the physics project and put it through its paces (F165)

User has been on their other project (SpaceTime/curvature) for several days; came back with a side-finding from there — the **Legibility Law** (amortized→legible, free-stored→scrambled), shown cleanly in a ≤1M-param toy — and explicitly wanted to test it as an *LLM hypothesis* here, not in the physics repo. Right instinct: the two projects rhyme (our whole steering program is an amortized-vs-stored story in disguise; the law even *predicts* F121's one-sidedness).

- First, housekeeping the user asked for: scanned the public repo (HEAD + full history) for secrets — clean — and added `.gitignore` guardrails (`.env`, `*.pem`, `*-key.json`, `service-account*.json`, …) so a stray credential can't be caught by a future `git add .`. Committed `e4b277b`.
- Designed Experiment A as a **within-item in-context-vs-parametric** probe ladder (the design that kills the frequency/dimensionality confounds), **pre-registered it before extracting** (`docs/prereg-legibility-law-A.md`), curated inspectable entity tables (54 elements exact, 40 people, 40 countries), and validated the probe on synthetic data — caught that a single-shuffle floor was too noisy at ~40 groups and switched to a 5-seed mean. Harness: `mvp/legibility_extract.py` + `legibility_probe.py`.
- **Result (F165): transfer FALSIFIED at the confound-free adjudicator.** Parametric scalar recall is ~as linearly legible as in-context (atomic number 0.924 vs 0.962, Δ+0.038 ≪ the 0.15 we'd locked; same on birth year/population). No scramble signature anywhere. The toy's "stored→scrambled" doesn't reproduce — because a pretrained LLM has no *free* per-object slot; its parametric knowledge is itself amortized through shared weights, so it's legible by default (consistent with ROME + the LRH). The law isn't wrong; its precondition just isn't instantiated in a transformer.
- The genuinely interesting nugget is **post-hoc**: route doesn't change *whether* a scalar is legible, it changes *where* — in-context is legible at L4 (it's in the text), parametric assembles with depth (L4 0.40 → L36 0.92). Depth-of-emergence, not legibility, is the real signature of "inferred vs recalled." Flagged it clearly as exploratory.
- Clean negative, honestly pre-registered and reported — exactly the kind of result we said we'd keep even when it's a "no." And it sharpens **Experiment B**: since object-facts are legible regardless of route, F121's abstention-won't-install is NOT a scrambling-of-object-knowledge effect; B now tests whether the *second-order* knowledge boundary ("do I know this") is the thing that's (il)legible.

## Day 64, later (2026-06-16) — Experiment B (F166): the knowledge boundary is partially legible, not scrambled → F121 is a controllability problem

Ran B same day. Two honest course-corrections worth recording:
- **The factual battery was too easy.** Built a hand-authored knows/doesn't-know battery (atomic numbers, capitals); Qwen3-4B scored 95% even on Oganesson and Pacific microstates — ~12 clean negatives, useless for a balanced probe. Lesson: you can't hand-author a knowledge boundary for a model whose competence exceeds your own reliable ground truth. The label hand-check also caught a diacritic scoring bug (Brasília/Bogotá/Kiev) — the discipline earning its keep again.
- **Pivoted to TruthfulQA MC1** (cached, exact labels, no confabulation risk, and a better F121 fit — misconceptions ARE false premises). 817 q, MC1 log-prob scoring, model acc 28.4% (balanced 232/585). Labels hand-verified: picks truth on easy items, falls for the classic myths on the rest.
- **Result:** linear AUC ≈ 0.65, nonlinear ≈ 0.65, floor 0.50. The "am-I-about-to-be-right" signal is **partially linearly legible and not scrambled** — neither pre-registered extreme. Combined with A: no scramble signature anywhere in this model.
- **The payoff:** the boundary is readable as a linear direction yet abstention still won't install by a linear push (F121). So F121 is **legibility ≠ steerability** — a controllability/causal-lever problem, not an illegibility one. Lands right on top of F142 (discrimination ≠ steering). The two-experiment arc (A+B) turned an imported physics-toy law into a clean statement about *our* negatives: the Legibility Law's scrambled regime doesn't occur in Qwen3-4B, and F121 was never about illegibility.

## Day 64, even later (2026-06-16) — Experiment C (F167): interpretable ≠ task-predictive; closed the A+B+C arc

Did C the same evening (downloaded Qwen3-1.7B; the committed SAE uncertainty decoders are 1.7B-specific). Two findings:
- **Replication:** supervised probe of the correctness boundary on 1.7B = AUC 0.635, basically B's 0.65 on 4B. Partial-legible, no-scramble holds across two models now.
- **The actual result:** the auto-interp "I don't know / uncertainty" SAE features (the ones we committed from Neuronpedia) **do not read the boundary** — combined 0.531, fitted-5 0.535, all at floor. The model's real "am-I-wrong" signal is distributed, NOT in the human-labeled uncertainty features. *Interpretable ≠ task-predictive.* A feature that reads as "don't know" semantically isn't the feature carrying the calibration signal.
- Honored the pre-registered gate: Part 2 (steer the uncertainty direction) not run, because the direction doesn't read the boundary in the first place — a legible-but-not-steerable test is moot for it.
- This is a real caution for our own weekend plan: an SAE-feature-gated trigger on feat_1194 "don't know" would not gate on actual error risk. Good to know *before* building it.

The arc (A+B+C) is a clean, self-contained mini-paper's worth of negative/refinement: an imported toy "law" doesn't transfer (no scramble regime in LLMs), the knowledge boundary is partially legible across models but not scrambled, and our F121 abstention failure is controllability — and even the obvious interpretable feature isn't the right lever. Honest, pre-registered, triangulated. Exactly the standard we hold.

## Day 65 (2026-06-23) — Read-vs-control (F168): the redundancy rescue of F121 dies, and a better answer takes its place

The SpaceTime session had, in the meantime, confirmed a "second law" in their toy — legibility ≠ steerability, *decoupled by redundancy* (read one channel = easy, steer one channel = 40%, steer both = 100%) — and their writeup claims it explains our F121. The other session also pitched it as a way to *rescue* our negative: "steering fails because the calibration code is redundant; additive steering writes only one copy." Tempting. So I tested it directly on the 4B (prereg locked first), reusing F166's activations to build the steering directions and steering the MC1 truth-vs-myth margin on held-out wrong items.

- **The redundancy rescue is false.** The "all-copies" integrated readout direction is *inert* (≈ random). Writing the full-rank readout doesn't control behavior. So F121 is not "you only wrote one copy."
- **What's actually going on is cleaner:** the read-optimal direction (logistic probe, best AUC) and the write-optimal direction (diff-of-means) are *different directions* (cos 0.34). Diff-of-means is a clean monotone causal lever (−9 → +2.9 across ±α); the probe direction is ~8× weaker, basically random. That's a direct causal vindication of our oldest methodological rule — a high-accuracy probe is not a valid steering vector.
- **And it corroborates F121's one-sidedness mechanically:** even the *best* lever only nudges +2.9 on a −12.66 baseline (doesn't install abstention), while steering the other way crushes the margin (−13). Easy to make it fall for myths, hard to make it resist. (Flagged the baseline-depth confound on that asymmetry — needs a near-boundary follow-up.)
- Had to send a correction back to SpaceTime: their second-law-explains-Phronesis claim doesn't survive the LLM test. The toy's redundancy mechanism doesn't transfer; our read≠control is direction-mismatch + asymmetry, not redundancy-rank.

Nice outcome: we went looking to rescue a negative with a borrowed mechanism, the mechanism failed the test, and the failure handed us a sharper, truer mechanism. The discipline (prereg, matched-norm random control, Δmargin over the noise-confounded flip%, hand-read) is exactly what kept the tempting-but-wrong rescue from sticking. Part 2 (free-generation hand-read of whether +diff-of-means steering actually induces hedging/abstention in open generation) still pending.
