# Post-MVP decision tree

**Purpose:** When the 4×4 specificity matrix data lands, what is the concrete next step?

This doc translates the abstract F98 exit criteria into concrete next-action decisions, so that when real data arrives, there is no ambiguity about what to do next. It does NOT introduce new decisions — it spells out what is already implied by `docs/eg-rt-eval-spec.md` §5.7 and F98 in `docs/findings.md`.

**Status:** v1 (Day 17, 2026-04-24). Committed before data arrives, per the same pre-registration principle that drove F98.

**Scope:** MVP outcome → next step. Does NOT cover publication strategy (separate decision, made after data interpretation). Does NOT cover Phase 5 scope (see `docs/phase5-plan.md`).

---

## Refresher: the three pre-registered MVP outcomes

Per F98:

| Outcome | Geometric MVE (6 pairs) | Diagonal wins (4 cells) | Off-diag failures |
|---|---|---|---|
| **All-clean** | 6/6 pass | 4/4 | ≤ 2 |
| **Partial** | 5/6 or 6/6 pass | ≥ 2/4 | ≤ 2 |
| **Collapse** | ≤ 4/6 pass OR EG × RT collapse | ≤ 1/4 | ≥ 3 |

Plus three implicit intermediate outcomes we may encounter in practice:

- **AOT-specific collapse** — 5/6 MVE pairs pass BUT v_EG × v_RT specifically fails (because EG + RT both look like "scientific-virtue thinking" and share a latent dimension per F39). Corpus-level finding, not model failure.
- **Geometric pass but behavioral fail** — MVE clean on all 6 pairs but ≤ 1 diagonal steering actually works. Implies F11 competency-absence: the extracted direction exists but the model lacks the underlying behavior to amplify.
- **Scorer-attribution ambiguity** — diagonal wins but scorer FM contamination (hand review flags >10% auto-human disagreement) means we can't trust the numeric result. Forces scorer escalation before any verdict.

---

## The decision tree

Read from top to bottom. Each branch is a separate CONCRETE next step, not a research-strategy discussion.

### 1. Geometric MVE (stage 2) first

Run `mvp/analysis/run_analysis.py --mve-only` (or the `mvp/mve_gate_test.py --matrix-mode` variant) on all 4 vectors × 2 models after extraction completes.

Check: **Are all 6 virtue-pairs orthogonal on at least one model?**

- **Yes, 6/6 on both models** → proceed to Stage 3 (α-sweep)
- **Yes on one model, partial on other** → proceed but flag model-specific concern
- **EG × RT collapse specifically** → skip to §3.1 (AOT-cluster branch)
- **Multiple collapses (≥ 2 pairs fail on both models)** → skip to §3.3 (corpus-redesign branch)

### 2. α-sweep (stage 3)

Run `mvp/run_alpha_sweep.py --model qwen3-4b` then `--model gemma-4-E4B-it`. Each takes ~4h GPU.

Check: **Does every vector have a best-α that produces ≥ +5 points delta on its target eval (diagonal)?**

- **All 4 vectors × 2 models have diagonal ≥ +5** → proceed to Stage 4 (specificity matrix)
- **1-2 vectors fail diagonal threshold** → go to §3.4 (F11 branch — competency absence)
- **3-4 vectors fail diagonal threshold** → go to §3.5 (extraction-quality branch)

### 3. 4×4 specificity matrix (stage 4) — full protocol only if Stages 1-2 clean

Assumes all prior gates passed. Run `mvp/specificity_matrix.py` per both models. Hand-review all ~960 generations via `mvp/review/app.py` per `docs/scoring.md` manual-first policy.

Apply the `classify_specificity_matrix()` function from `mvp/analysis/compute_effects.py`. The function returns one of: `all_clean`, `partial`, `collapse`.

#### 3.A. Overall verdict = "all_clean"

**Concrete next steps:**

1. **Publish the MVP as a technical report** — `docs/mvp-report.md` draft. Key claims: (a) extracted 4 orthogonal epistemic virtue directions on two small open models, (b) each virtue drives its own behavioral signature without driving the others, (c) cross-model consistency. Stress: small open models, atomic virtues, specificity-not-existence.
2. **Decide Phase 5** — see `docs/phase5-plan.md`. Open question becomes "scale to 8 virtues" vs "deepen on these 4 with richer benchmarks."
3. **Close FM-6 / FM-7 in scoring.md** — note that manual review confirmed the auto-scorer results; scorer hardening is deferred to Phase 5 per earlier plan.

**Timeline to report draft:** ~3 days.

#### 3.B. Overall verdict = "partial"

Sub-branches based on WHICH specific cells failed:

##### 3.B.i. Partial because v_EG × v_RT collapse

The two Stage-6 virtues share a latent direction. Both diagonals (v_EG driving EG-eval, v_RT driving RT-eval) may still succeed; the geometric collapse is the specific finding.

**Concrete next steps:**

1. Write up as a **collapse finding**, not a failure — this is scientifically interesting and directly tests F39's AOT-cluster hypothesis.
2. Measure `|cos(v_EG, v_RT)|` exactly and report as the primary quantity of interest.
3. Add a qualitative comparison: do steered-v_EG generations look different from steered-v_RT generations even though the directions overlap? If yes, the behaviors dissociate even when directions don't — that's a second finding.
4. **Do NOT scale to 8 virtues in Phase 5** until we understand whether other Stage-same-bucket virtues (e.g. Logical Rigor × Hypothesis Generation, both Stage-1-2) also collapse.

**Timeline to report draft:** ~5 days (extra analysis + framing).

##### 3.B.ii. Partial because 2-3 diagonal wins + ≤ 2 off-diagonal failures

Three vectors drive their virtues cleanly; one fails. Usually the failing one is IH (known scorer-sensitivity from F97).

**Concrete next steps:**

1. For the failing diagonal, check hand-review: is it **scorer artifact** (auto says fail, human says works) or **real extraction fail**?
2. If scorer artifact → escalate to **LLM-as-judge** scorer for that specific eval (per `docs/scoring.md` Phase 5 plan, brought forward). Re-run just the affected cells.
3. If real extraction fail → flag as F11-competency-absence (the model can't be steered toward this behavior because it lacks the underlying disposition).
4. Write up as 3-virtue specificity result + the one failure as a methodology finding.

##### 3.B.iii. Partial because off-diagonal cross-talk dominates

Diagonals succeed but off-diagonals also drift. Example: v_EG drives both evidence-labeling AND hedging. Implies F67's multi-direction-same-behavior caution.

**Concrete next steps:**

1. Report the cross-talk pattern specifically: which off-diagonal cells contaminated, by how much.
2. Consider orthogonalised-vector test: construct v_EG_orth = v_EG - proj_{v_CC}(v_EG) and re-run the EG × CC-eval cell. If off-diag drops, we have evidence the crosstalk is geometric-only.
3. Write up as specificity-plus-cross-talk finding. Less clean story but still publishable per F98.

#### 3.C. Overall verdict = "collapse"

≤ 1 diagonal wins OR ≥ 3 off-diagonal failures OR EG × RT collapse + 1 other.

**Concrete next steps (in order):**

1. **Don't panic.** F98 pre-registered this as a possible outcome; it's a legitimate finding about what does NOT separate at 4B scale.
2. Identify which specific cells failed and why via hand review. Three categories:
   - **Scorer artifact** — rerun with LLM-as-judge scorer
   - **F11 competency absence** — model can't produce the behavior, extraction vector is real but unsteerable
   - **F67 multi-direction** — vector exists but doesn't uniquely drive the behavior
3. Write up as a COLLAPSE finding — honest title: "At 4B parameters, these 4 epistemic virtues do not occupy separable directions" (or similar). Still worth a technical report — null / negative results with a clean pre-registration are publishable.
4. **Before any corpus redesign**, check: are the extracted vectors geometrically separable AT ALL? If yes (MVE pairs pass), but behavioral doesn't → F67/F11 discussion. If no (MVE also collapses) → corpus-design problem.
5. Corpus redesign is the LAST resort. Per F98 pre-registration, we don't re-spec the corpus post-hoc; a redesign would be a new study.

### 3.1. Special branch: EG × RT geometric collapse (after Stage 2)

If Stage 2 reveals |cos(v_EG, v_RT)| > 0.5 on both models, skip α-sweep for the EG × RT pair specifically. Run α-sweep only for CC and IH.

**Concrete next steps:**

1. Keep v_CC and v_IH in the specificity matrix (3×3 or 4×4 noting the collapse).
2. Document the EG × RT merger as the primary finding.
3. Cheap follow-up: extract a "combined scientific-virtue" vector from EG+RT triplets pooled, see if that single vector outperforms the separate extractions at the joint task.
4. Do NOT pivot to new virtues before understanding whether this is (a) a corpus-specific artifact (our 40 triplets per virtue weren't differentiated enough), (b) a general small-model limit (below 7B, these virtues don't separate), or (c) a genuine taxonomic insight (the two Stage-6 "communication" virtues are sub-facets of one thing).

### 3.3. Special branch: multi-pair MVE collapse (after Stage 2)

If 2+ pairs fail orthogonality on both models, the extraction itself may be the problem (not the virtues).

**Concrete next steps:**

1. Check extraction diagnostics: probe accuracy per layer, vector norms, how the generation method handled each corpus.
2. Re-run ONE corpus with `--method last_token` on a single model as a control. If last_token gives orthogonal vectors where generation didn't, we have an extraction-method finding (F73 Path B questioned).
3. If control fails too → corpus-design problem. Next step is a Phase 5-style reopen of corpus construction per-virtue.

### 3.4. Special branch: diagonal failure on ≤ 2 vectors (after α-sweep)

F11 candidate: model lacks the behavior to amplify.

**Concrete next steps:**

1. For each failing diagonal, check the model's BASELINE output on the target eval. Does it ever produce the target behavior unprompted? If never → F11 confirmed.
2. Test with stronger prompt baseline (just asking the model "please label your evidence types" or "please show your reasoning steps"). If prompt works but steering doesn't → vector is weak, not competency-absent.
3. Report as competency-presence × extraction-quality breakdown table per virtue.

### 3.5. Special branch: diagonal failure on 3-4 vectors (after α-sweep)

Either extraction is broken or scorers are systematically wrong.

**Concrete next steps:**

1. Sanity-check extraction: does `extract_v2.py --method generation` produce plausible vectors? (non-zero norm, separable on training data per probe accuracy)
2. Sanity-check scorers: rerun `calibrate_scorers.py` — have the corpus or scorers drifted?
3. If both clean → flag as genuine F67 concern across all virtues (multiple orthogonal directions for each behavior, not a single extractable one).
4. Fall back to `docs/eg-rt-eval-spec.md` §7 exit criteria: declare collapse outcome.

---

## Cross-cutting: what to do in ALL outcomes

Regardless of verdict:

1. **Commit the full analysis report** (`mvp/results/analysis_report/report.md`) with figures and CSVs.
2. **Update `findings.md`** — fill in F99 with actual numbers (currently a skeleton). Add F100, F101, etc. for any downstream findings.
3. **Update `journal.md`** — a Day-N entry describing what the data showed.
4. **Do NOT rationalise post-hoc.** The exit criteria are in F98 and this doc; stick to them.
5. **Remind ourselves of Day 15 guiding principle #1** — learning over publishing. A clean collapse finding is as valuable as a clean success.

---

## Non-goals of this document

- **Does not specify publication venue or writing style.** That's a separate decision after data interpretation.
- **Does not cover Phase 5 virtue selection.** See `docs/phase5-plan.md`.
- **Does not retry extraction with different methods.** Per F98, method choice (F73 Path B) is pre-registered; a retry would be a new study.
- **Does not invent new exit criteria.** Everything here maps onto F98 + eg-rt-eval-spec.md §5.7.

---

## Document state

- **Created:** 2026-04-24 (Day 17), written while extraction is ~90% complete but before any analysis data exists.
- **Pre-registration discipline:** this document is being committed BEFORE MVE or specificity data lands, to prevent post-hoc tree-shaping.
- **Related:** `docs/findings.md` F98, `docs/eg-rt-eval-spec.md`, `docs/mvp-virtues.md`, `docs/extraction-runbook.md`, `docs/phase5-plan.md` (forthcoming).
