# Negative-control corpus generation — handoff prompt

**For:** A separate Claude session (different machine, different context window).
**Created:** 2026-04-26 (Day 19, post-F103).
**Author:** Phronesis project team.

This document is a self-contained handoff. The receiving session should be able to read this prompt + a small set of reference files and execute the task end-to-end with a self-refinement loop until calibration passes.

---

## 1. Project context (what Phronesis is and why this matters)

**Phronesis** is a research project on activation steering for epistemic virtues in small (≤4B) open-source LLMs. The core hypothesis: epistemic virtues — Calibrated Confidence (CC), Intellectual Humility (IH), Evidence Grounding (EG), Reasoning Transparency (RT) — are encoded as **linear directions** in the residual stream of small LMs, and can be controlled via **additive activation steering** at inference time. The full project context is in `docs/project.md` and the chronology is in `docs/journal.md`.

The Phronesis pipeline is: contrastive triplet corpus (virtuous / non-virtuous / neutral passages on the same factual substrate) → difference-of-means vector extraction at the residual stream → MVE (geometric pairwise orthogonality) test → α-sweep on behavioural benchmarks → 4×4 specificity matrix.

**Where we are:** Day 19. The MVP α-sweep finished. Geometric findings (F102) showed model-dependent virtue separability (qwen3-4b shows partial collapse of CC/EG/RT at deep layers; gemma-4-E4B-it keeps four clean orthogonal directions). Behavioural hand-review (F103) showed small (~+0.4 to +0.8 hand-rubric) real diagonal effects on qwen3-4b and a confirmed null on gemma. **Crucially, F103 also showed the auto-scorer awarded its largest soft score (+5.19) to a degenerate-output cell** (qwen × RT × L18 α=20 — all five generations are catastrophic repetition loops). The +5.19 was regex-gaming, not real virtue.

This raises a sharper question — one that motivates the present task.

---

## 2. The question this corpus exists to answer

A specific, focal concern surfaced by F103 and articulated independently by an external reviewer:

> *"Our virtue vectors might be capturing 'more structured / more verbose / more step-marker-rich prose' rather than 'epistemic virtue itself.' If we extract a deliberately-non-virtue vector — say 'verbose vs terse prose' — using exactly the same pipeline, and its specificity matrix and α-sweep behaviour look qualitatively similar to the virtue vectors', then the framework is measuring vector-corpus alignment, not virtue separation."*

This is a **falsification experiment**. We need a clean negative control: a contrastive corpus that differentiates one obvious surface property (verbosity) but is **explicitly not an epistemic virtue**, run through the same extraction + analysis pipeline, with results compared to the virtue vectors'.

**Your task** is to generate this negative-control corpus, validate it, and document it.

---

## 3. The corpus to build: VERBOSITY contrast

### 3.1 The contrast

- **Verbose passage:** structured, multi-step, step-marker-rich, thorough exposition. Uses sentences like *"Step 1: …"*, *"First, let us consider …"*, *"Therefore, …"*, *"In summary, …"*. Length 250-300 words.
- **Terse passage:** the same content, but compressed. Direct sentences. No step markers. Plain transitions. Length 100-130 words.
- **Neutral passage:** intermediate length and structure, neither aggressively structured nor compressed. Length 180-220 words.

All three on the **same factual substrate** (same numbers, same claims, same scenario). The only difference is presentation density.

### 3.2 What this corpus must NOT do

These are the failure modes that would invalidate the negative control:

- ❌ **Don't make verbose passages "more reasoning-transparent."** They should not flag assumptions or weak links — just structure the same content into more steps. RT-virtue and verbosity must be orthogonal in the corpus.
- ❌ **Don't make verbose passages "more evidence-grounded."** They should not cite more evidence — just present the same evidence with more sentence structure.
- ❌ **Don't make terse passages "more confident" or "less hedged."** Hedge density should be matched between verbose/terse.
- ❌ **Don't introduce humility markers in either direction.** Phrases like "I'm not sure," "this is outside my expertise" should be absent from both verbose and terse versions, or balanced if present.
- ❌ **Don't conflate verbosity with bullet-points.** All three passages must be reasoning monologues (prose), not bullet/numbered lists. Verbose = "longer, more sentence transitions"; not "broken into structural list items."

In other words: the verbose passage should differ from the terse passage **only in length and sentence-level structure**, not in epistemic disposition.

### 3.3 Topic distribution

40 triplets total, distributed across domains to match our existing virtue corpora's topic breadth:

- 5 physics
- 5 chemistry
- 5 biology
- 5 medicine
- 5 economics / psychology
- 5 engineering
- 5 earth sciences
- 5 mathematics / general reasoning

Each triplet should be on a question that admits a substantive scientific or analytical answer (not a one-liner factoid).

---

## 4. Output format (must match existing virtue corpora exactly)

### 4.1 Directory structure

Place the corpus under:

```
corpus/mvp-combined/triplets-verbosity-control/
├── LEDGER.md                                ← provenance + verification table for all 40 triplets
├── triplet-001-physics-friction-coefficient/
│   ├── fact-pack.md                         ← factual substrate + design metadata
│   ├── virtuous.md                          ← VERBOSE passage (250-300 words)
│   ├── non-virtuous.md                      ← TERSE passage (100-130 words)
│   └── neutral.md                           ← neutral-density passage (180-220 words)
├── triplet-002-chemistry-buffer-pH/
│   └── ...
└── ...
```

**Important:** the file names `virtuous.md`, `non-virtuous.md`, `neutral.md` are *kept* even though "virtuous" is a misnomer here — they map to "verbose / terse / neutral." This keeps the corpus drop-in compatible with our existing extraction pipeline (`extract_v2.py`) without code changes. Document this naming decision in the LEDGER.

### 4.2 fact-pack.md schema

Each `fact-pack.md` opens with YAML frontmatter and continues with a brief substrate description. Pattern (from `corpus/mvp-combined/triplets-evidence-grounding/triplet-*/fact-pack.md`):

```markdown
---
triplet_id: triplet-001-physics-friction-coefficient
domain: physics
substrate_summary: "Static vs kinetic friction coefficient measurement on a steel-on-steel surface"
contrast_axis: verbosity   # NOT a virtue; this is the negative control
failure_mode_virtuous: NA  # there is no failure-mode here; verbose is the contrast positive
failure_mode_nonvirtuous: NA
correctness_confound: false
target_word_counts: {virtuous: 280, non-virtuous: 110, neutral: 200}
---

# Factual substrate

The static friction coefficient μ_s for clean steel-on-steel under dry conditions is approximately 0.74 (lab-measured at 20°C, 40% RH). Kinetic friction μ_k drops to 0.57 once sliding begins. Source: ASM Handbook Vol 18 (Friction, Lubrication, and Wear Technology), Table 4.

# Topic / question being answered

"What is the difference between static and kinetic friction, and what determines those values for steel-on-steel?"
```

### 4.3 Passage files

Each of `virtuous.md`, `non-virtuous.md`, `neutral.md` should contain:

- A 1-line H1 header restating the triplet ID
- A blank line
- Then the passage prose itself — no markdown formatting *inside* the passage (no bullets, no nested headers)
- A trailing blank line + a 3-line YAML metadata block:

```yaml
---
word_count: 281
hedge_density: 2.1   # rough hedge-marker per 1000 tokens; see scoring spec
step_markers: 8       # count of "Step", "First", "Second", "Therefore", "Thus", "In summary"
---
```

The `step_markers` field is the verbosity scorer's signal — count those markers per passage, manually. We will use this for calibration.

### 4.4 LEDGER.md format

Same as `corpus/mvp-combined/LEDGER.md`. One row per triplet, with verification status:

```markdown
| triplet_id | domain | wc_v / wc_n / wc_nu | step_v / step_n / step_nu | hedge_v / hedge_n / hedge_nu | within_10pct | injection_clean | accepted |
|---|---|---|---|---|---|---|---|
| triplet-001-physics-friction-coefficient | physics | 281 / 109 / 198 | 8 / 0 / 3 | 2.1 / 1.8 / 1.9 | yes | yes | yes |
```

Plus a top-level "Provenance" header section and a "Notes on the verbosity contrast" section explaining the design choices and naming convention.

---

## 5. Self-refinement loop (REQUIRED)

After generating the corpus, you must run a calibration check and iterate until pass.

### 5.1 The calibration script you'll write

Write a calibration script at `mvp/calibrate_verbosity_control.py`, modelled on `mvp/calibrate_scorers.py`. The script should:

1. For each of the 40 triplets, parse the three passages.
2. Compute three metrics per passage:
   - **Word count.**
   - **Step-marker count.** Pattern: `\b(Step|First|Second|Third|Fourth|Fifth|Therefore|Thus|Hence|In summary|To summarize|Let us|Consider|Suppose|Note that)\b`. Counted per passage.
   - **Hedge-marker count.** Same pattern as `mvp/calibrate_scorers.py` uses for CC. Counted per passage.
3. Aggregate across all 40:
   - **Word count separation:** mean(verbose word_count) − mean(terse word_count). Target: ≥120.
   - **Step-marker separation:** mean(verbose step_markers) − mean(terse step_markers). Target: ≥4.
   - **Hedge density invariance:** mean(verbose hedge per 1000 tokens) − mean(terse hedge per 1000 tokens). Target: |delta| ≤ 1.0 (i.e., hedge density should be matched, not contrastive — or virtuosity contamination is happening).

4. Print a calibration report with the three numbers and a PASS/FAIL verdict.

5. Print per-triplet diagnostics for any triplet that:
   - Has word count outside its target range (verbose 250-300, terse 100-130, neutral 180-220), OR
   - Has hedge density delta > 2.0 between verbose and terse, OR
   - Has step-marker count delta < 2 between verbose and terse.

### 5.2 The refinement loop

```
Pass 1: generate all 40 triplets per the spec in §3-§4.
Run calibrate_verbosity_control.py.

If PASS: stop. Document and write the summary (§7).

If FAIL:
  For each flagged triplet from §5.1.5 diagnostics:
    Identify which constraint is violated.
    Rewrite ONLY the violating passage(s) — do not regenerate the whole triplet.
    Common fixes:
      - word count too low/high → expand or compress while keeping content invariant
      - hedge delta too high → remove hedges from one side OR add to the other (whichever feels less forced)
      - step-marker delta too low → add more "Step 1: / First, / Therefore, ..." sentence transitions to the verbose side, OR strip them from terse side
  Re-verify the rewritten triplets only.
Repeat until calibrate_verbosity_control.py PASSES.
```

Cap iterations at 5. If after 5 iterations calibration still fails, stop and write a FAILURE report explaining what's blocking convergence.

---

## 6. Important constraints and "DO NOT" list

1. **DO NOT introduce facts.** Every numerical value, named entity, claim, or specific reference in the verbose passage must appear in the terse passage. Verbose just expands sentence-level structure around the same facts.

2. **DO NOT use bullet points or numbered lists in any passage.** All three passages are reasoning monologues. (Same constraint as our virtue corpora — see `docs/generation-guidelines.md` §4.6.)

3. **DO NOT inject any of the four virtue dispositions.** Verbose passages must not be more transparent, more evidence-grounded, more humble, or more calibrated than terse passages. They must be SAME-DISPOSITION, DIFFERENT-LENGTH.

4. **DO NOT match topic distribution exactly to existing virtue corpora.** Some overlap is fine, but use mostly-different specific scenarios. (E.g., if EG corpus had a triplet on "thermal expansion of steel bridges," your physics triplet here should be on something different like "friction coefficients" or "torque on a rotating axle.") This avoids cross-corpus contamination at the substrate level.

5. **DO NOT use phrases like "calibrated," "transparent," "humble," "evidence-grounded"** in any passage. These are virtue terms; they would contaminate the negative control by making it virtue-adjacent in the model's vocabulary space.

6. **DO use natural variation in word choice across the 40 triplets.** Vocabulary monotony would itself be a confound.

7. **DO ensure register matches our existing virtue corpora.** Same scientific/analytical voice. Read 5 sample triplets from `corpus/mvp-combined/triplets-evidence-grounding/` first to absorb the tone.

---

## 7. Final deliverables (when calibration passes)

Once `calibrate_verbosity_control.py` returns PASS:

1. **Corpus directory:** `corpus/mvp-combined/triplets-verbosity-control/` complete with 40 triplets and LEDGER.md.

2. **Calibration script:** `mvp/calibrate_verbosity_control.py`.

3. **Summary file:** `corpus/mvp-combined/triplets-verbosity-control/SUMMARY.md` with:
   - Topic distribution table (8 domains × 5 triplets, 40 total)
   - Calibration report final numbers (word count separation, step-marker separation, hedge density delta)
   - Iteration count (how many refinement passes were needed)
   - Any triplets that required >2 rewrites, with notes on what was hard
   - Confirmation that all 40 passed `injection_clean` and `within_10pct` substrate-invariance checks
   - One-paragraph narrative describing the corpus and its purpose for the receiving Phronesis pipeline

4. **Brief writeup:** `corpus/mvp-combined/triplets-verbosity-control/DESIGN_NOTES.md` describing:
   - Why verbosity was chosen as the negative-control axis (paraphrase from §2 of this prompt)
   - What the calibration thresholds mean and why they were set where they are
   - Open questions or design tensions encountered during generation
   - Anything the receiving Phronesis pipeline should know about this corpus that isn't obvious from the LEDGER

---

## 8. Reference files you must read first

These are in the Phronesis project repo. Read them before generating any triplets:

### Required reading (in this order):

1. **`docs/project.md`** — what Phronesis is end-to-end (skim, ~10 minutes).
2. **`docs/concepts.md`** — definitions of the four MVP virtues, so you understand exactly what you must NOT inject. Pay attention to the "behavioural markers" lists.
3. **`docs/generation-guidelines.md`** — generation rules (especially §4.6 on monologue-style and §4.8 on verification checks). The factual-invariance and length-invariance rules apply to your triplets too.
4. **`docs/scoring.md`** — failure-mode catalogue (FM-6 through FM-9). FM-6/FM-8 are particularly relevant: don't make verbose passages "use evidence vocabulary" or "trigger regex-gaming."
5. **`docs/findings.md` F67, F102, F103** (search by F-number) — the underlying caveat (F67), the geometric finding (F102), and the F103 hand-review verdict that motivates this whole task.
6. **`docs/eg-rt-eval-spec.md` §3.5 + §4.5** — calibration-target framing; you'll use the same shape but with verbosity-specific thresholds.

### Reference examples (read 3-5 of each before generating):

7. **`corpus/mvp-combined/triplets-evidence-grounding/triplet-001-*/`** through **triplet-005-***. Read fact-pack + virtuous + non-virtuous + neutral for each. Absorb the format.
8. **`corpus/mvp-combined/triplets-reasoning-transparency/triplet-001-*/`** through **triplet-005-***. Same.
9. **`corpus/mvp-combined/LEDGER.md`** — the LEDGER format your output will mirror.

### Code references:

10. **`mvp/calibrate_scorers.py`** — the existing calibration script. Your `calibrate_verbosity_control.py` will be modelled on this with different metrics.
11. **`mvp/benchmarks/eg_scorer.py`** and **`mvp/benchmarks/rt_scorer.py`** — pattern for regex scoring. Verbosity is simpler (no separation between virtuous-style markers and gaming-prone surface markers — verbosity *is* surface markers).

---

## 9. Files you DO NOT need

To minimise scope and avoid being side-tracked:

- ❌ The α-sweep generations themselves (`mvp/results/benchmark_probe/`) — irrelevant to corpus design.
- ❌ The vector files (`mvp/results/vectors/`) — irrelevant; the negative-control corpus runs through the *same* extraction pipeline downstream.
- ❌ The dashboards or benchmark results — irrelevant.
- ❌ `docs/phase5-plan.md`, `docs/post-mvp-decisions.md` — useful context but not blocking.

---

## 10. When you're done

Commit the new corpus directory + calibration script + SUMMARY/DESIGN_NOTES as a single logical change with commit message:

```
corpus(negative-control): add 40-triplet verbosity-contrast corpus + calibration

Builds the negative-control corpus per F103 follow-up (docs/negative-control-corpus-handoff.md).
Verbosity vs terse contrast on length-matched factual substrate, no virtue contamination.
Calibration: word_count_sep=N, step_marker_sep=N, hedge_density_delta=N. PASSED on iteration K.
```

Then notify the project team. The Phronesis pipeline will pick up from there:

1. Run `extract_v2.py --model qwen3-4b --corpus corpus/mvp-combined/triplets-verbosity-control --method last_token --layers all --save-vectors`
2. Run the same on gemma-4-E4B-it
3. Compute geometric MVE between the verbosity vector and each of {CC, IH, EG, RT}
4. Run a small α-sweep against the four eval benchmarks
5. Compare specificity matrix structure to virtue-vector matrices
6. If they look similar → framework is measuring vector-corpus alignment, not virtue separation (publishable falsification)
7. If they look different → virtue vectors are doing something narrower than just surface-feature alignment (strengthens framework)

Either outcome is informative. That's why this matters.

---

## 11. Tone and voice (for the receiving session)

You are joining a serious research project mid-flight. The Phronesis team has been running for 19 days, has a strong pre-registration discipline, has just retracted a headline finding (F103), and is now trying to clarify what their framework actually measures. They are in *exploratory / improve-methods mode*, not *push-toward-paper mode*. There is no deadline.

**Do:**
- Read the references thoroughly before generating anything.
- Write the calibration script first — having metrics defined before generation prevents drift.
- Be honest about what's hard. If a topic seems forced, say so in DESIGN_NOTES.
- Self-correct freely. The whole point of the refinement loop is iterative improvement.

**Don't:**
- Skip the reference reading and try to generate from scratch.
- Optimise for "looking right" over "being right." Triplets that pass calibration on paper but contain virtue contamination will tank the experiment.
- Add scope. 40 triplets, one negative-control axis, one calibration script. Anything else is creep.

End of handoff prompt. Good luck.
