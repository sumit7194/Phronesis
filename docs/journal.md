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
