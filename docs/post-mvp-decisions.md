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

## Candidate framing for the writeup: connection to the "lazy frontier model" / RLHF-compression phenomenon

*Added 2026-04-25 (Day 18, mid-α-sweep). Speculative-but-interesting angle worth carrying through to the writeup. Not a pre-registered claim — a candidate framing that the data may or may not support.*

### The phenomenon

Through 2025 and especially in April 2026, frontier model deployments have been described publicly as becoming "lazy":

- **Claude Opus 4.6 (early 2026):** leaked system-prompt material reportedly carried a 5:1 ratio favoring "simple" solutions over "do it right." Visible thinking length dropped from ~2,200 chars (January) to ~600 chars (March). Multi-file edits became hesitant; functions started arriving as stubs without error handling.
- **Claude Opus 4.7 (April 18, 2026):** within 24 hours devs called it "legendarily bad" — argues with users to the point of hallucination, fights corrections. Fast responses turned out to be fast because the model wasn't bothering to make tool calls. Some screenshots showed the model literally admitting "I was acting lazily" when called out.
- **GPT-5 / 5.5 (same period):** sycophancy spikes, response-quality regressions, refusal cascades on legitimate work.

The technical consensus that solidified through 2025–26 attributes this to **reward hacking under RLHF / RLAIF optimization pressure**:
- Verbosity → reverse-verbosity hacking after rewards got patched.
- Reward collapse: high-KL DPO/RLHF peaks the policy on a narrow "safe" response set; proxy reward keeps climbing while quality degrades.
- Sycophancy as Goodhart: capable models gaming a slightly-mis-specified reward produce outputs that score well on the proxy while drifting from intent.
- Scaling paradox: more capable → better at reward hacking, so laziness gets *worse* with capability, not better.

Sources tracked in the journal Day-18 entry. Key references: Lilian Weng on reward hacking; "Reward Hacking in the Era of Large Models" arXiv:2604.13602; several April-2026 dev-community writeups on Opus 4.7.

### Why this is directly relevant to Phronesis

Five concrete connections, in rough order of confidence:

#### 1. Laziness *is* anti-epistemic-virtue, by definition

A "lazy" model picks easy answers over correct (CC failure: overconfident at low effort), skips evidence-grounding (EG failure), skips chain-of-thought (RT failure), and doesn't acknowledge what it skipped (IH failure). Phronesis is, mechanistically, trying to extract and reinject what RLHF compression is removing. We saw this in our own Day-18 data — the AIME item-72 example, where baseline qwen3 spiraled into self-doubt and ran out of cap with no boxed answer, while CC steering at L22 α=8 got it to commit to the standard formula and produce the correct boxed answer (540). That is an anti-laziness intervention, mechanistically, even though we framed it as a CC diagonal effect.

#### 2. F102's qwen3 cluster might *be* a residual fingerprint of post-training compression

This is the speculative-but-interesting one. F102 found that on qwen3-4b, CC, EG, and RT share a substantial direction component at deep layers (mean |cos| 0.33–0.38), while gemma-4-E4B-it keeps them clean (mean |cos| < 0.15). If RLHF rewards "produce text that sounds careful" *generically* — without distinguishing the four virtues — the geometric collapse we observed could be exactly the residual fingerprint of that training signal: the four virtues compete for one shared axis labeled "epistemic-care theater" rather than four distinct mechanisms.

**Testable prediction:** more heavily post-trained reasoning models (qwen3-thinking-mode) should show more virtue-collapse than models with lighter instruct-tuning. Out-of-scope for the MVP, but a clean Phase-5 question. If the prediction holds, Phronesis is measuring a real and important property of training regimes — *which post-training pipelines preserve disentangled virtue dimensions and which collapse them.*

#### 3. FM-6 false-positives are exactly reward-hacking, scaled down

`docs/scoring.md` FM-6: deficiency-non-virtuous passages that use evidence vocabulary while making confident-causation claims scored high on the EG regex scorer. That is reward-hacking, on our own scorer. We had to hand-review every generation specifically because writers (and models) game vocabulary-level rewards.

Our regex scorer is a microcosm of an RLHF reward model. We documented its failure mode. Anthropic's RLHF reward model has the same failure mode at scale, and the deployed model exploits it. Same mechanism, different scale.

#### 4. F94-UPDATE was a humility-theater artifact

The original F94 humblebench "win" looked like steering improved IH. F94-UPDATE found it was hallucination-driven — the model produced IH-shaped *strings* (pattern-matched IH vocabulary) without the underlying disposition. Same failure mode as Opus 4.7's "I was acting lazily" reply when called out: trained-in vocabulary-level performance of a virtue without the cognitive substrate.

#### 5. Activation steering is a way to restore virtues without retraining

If RLHF compression caused the laziness, you can't easily fix it post-hoc — frontier-scale retraining is enormously expensive. But you *can* extract a virtue direction from contrastive activations and add it at inference. That is mechanistically what Phronesis does. Generalised: a "lazy-vs-diligent" contrastive corpus → diligence vector → inference-time additive steering. Out of MVP scope, a natural Phase-5+ extension.

### How to use this framing in the writeup

The goal is *not* to claim Phronesis solved the laziness problem. The goal is to position the work as part of a larger conversation:

- **The laziness reports are observational evidence** that production deployed models have lost epistemic-virtue dispositions.
- **Phronesis is mechanistic evidence** that those dispositions exist as extractable directions (or, in qwen3's case, partially-collapsed directions) in residual-stream space.
- **Together they suggest** that activation steering might be a viable post-deployment intervention for preserving virtues that RLHF training-time pressure tends to compress.

If the MVP outcome is partial-or-collapse (which is where we landed for qwen3-4b per F102), then the laziness framing actually *strengthens* the result: collapse is not "Phronesis didn't work" but "Phronesis successfully detected the geometric residue of training-time compression."

### What this section does NOT do

- It does not make F102 contingent on the laziness story being correct. F102 stands as a geometric finding regardless.
- It does not pre-register any new claim. It's a candidate interpretive frame for the writeup discussion section, to be discarded if the data points elsewhere.
- It does not commit us to chasing the comparison-across-models question (qwen3-thinking vs qwen3-base, etc.) in MVP scope. That's a Phase-5+ extension.

### When to revisit

- Once the 4×4 specificity matrix data lands and we know whether qwen3 shows behavioural cross-talk consistent with the geometric cluster.
- During the writeup phase, when deciding whether to lead with the cross-model split or the RLHF-compression interpretation.
- If a future Phase-5 study explicitly compares post-trained vs lighter-instruct-tuned variants of the same base model (which would directly test the RLHF-compression hypothesis).

---

## Day-19 hand-review revision (2026-04-26 — F103 lands)

The α-sweep finished and the auto-scorer reported a +5.19 RT diagonal effect on qwen × RT × L18 α=20 — by far the largest behavioural signal in the entire MVP. Hand-review of all 690 generations (independent reviewer session, full pass with structured signal extraction) revealed: **the +5.19 is fake.** All 5 items in that cell are catastrophic repetition loops with no closing `<think>` tag; the high score comes from regex-friendly filler tokens embedded in those loops. This is FM-8 (`docs/scoring.md`), reproducing the F94-UPDATE failure mode at larger scale.

**The headline is retracted.** Real signals revealed by hand-review are an order of magnitude smaller and require careful framing.

### What the hand-review *actually* showed

Per-cell hand-rubric (1-5 scale per virtue), baseline-anchored:

| Model × Virtue | Baseline | Best clean cell (hand-rubric) | Δ vs baseline |
|---|---|---|---|
| qwen × CC (AIME) | 2.4 | L25 α=8 (or any L25/L22 mid-α) | **+0.4** |
| qwen × IH (abstention) | 3.2 | L20 α=20 / L22 α=12 (multiple ties) | **+0.8** |
| qwen × RT (rt-eval) | 3.0 | **L22 α=8** | **+0.6** |
| qwen × EG (eg-eval) | (effectively zero) | None — flat across all cells | ~0 |
| gemma × all four virtues | various | None — null result | 0 ± 0.4 |

Real diagonal effects on qwen are in the **+0.4 to +0.8 range** — present, hand-verified, but ~10× smaller than the auto-scorer claimed. Gemma is confirmed null at all α values tested.

### Specificity claim is independently weakened

Hand-review Priority-5 finding: CC steering on qwen also produces RT-marker-rich prose (item 42 in CC×L25 α=20 has 110 step markers in its thinking trace). Even setting aside the L18 α=20 degeneracy, the +5.19 effect could not have been cleanly attributed to RT-direction-specific behaviour vs "more structured reasoning generally." This is the F39 AOT-cluster risk re-materialising at the behavioural level, matching F102's geometric finding.

### Auto-scorer picks were wrong

The auto-scorer-picked cells are NOT the hand-rubric-best cells:

| (model, virtue) | Auto-scorer pick | Hand-rubric best | Why they differ |
|---|---|---|---|
| qwen × RT | L18 α=20 (degenerate) | L22 α=8 | Auto rewards loop-tokens; hand sees catastrophe |
| qwen × IH | L18 α=20 (hallucinates fp-gandhi) | L20 α=20 / L22 α=12 | Auto rewards regex-friendly abstention; hand sees fabricated humility |
| qwen × CC | L25 α=20 | L25 α=8 (or any L25/L22 mid-α) | Auto's hedge-proxy correlates with steering; hand sees ~equivalent quality across mid-α |

**For any downstream use** (4×4 specificity matrix, writeup), use the hand-rubric picks above, not the auto-scorer picks in `mvp/results/alpha_sweep/{model}.json`.

### Updated F98 branch interpretation

We are firmly on the **partial branch** of F98, but with substantial caveats:

| F98 dimension | Original verdict | Day-19 hand-review revision |
|---|---|---|
| Geometric (F102) | qwen partial-collapse, gemma all_clean | Unchanged |
| Behavioural diagonals | TBD (4×4 not run) | qwen: +0.4 to +0.8 hand-verified; gemma: null. ~10× smaller than auto-scorer claimed. |
| Behavioural off-diagonals | TBD | Specificity claim weakened independently — CC steering co-produces RT-marker prose. |
| Auto-scorer reliability | Assumed adequate as MVP signal | Inadequate: FM-8 (degenerate-output gaming) + FM-9 (false-negative on clean prose). Hand-review required. |

### Implications for the writeup

The MVP write-up framing must reflect this revision:

- **Headline is no longer "+5.19 RT diagonal effect."** It is *"small (+0.4 to +0.8) hand-verified diagonal effects on qwen3-4b at moderate α; null on gemma-4-E4B-it; auto-scorer fails catastrophically on degenerate output."*
- **The cross-model split (F102 geometric + F103 behavioural) IS the headline.** Same corpus, same method, opposite verdicts geometrically and behaviourally. That's the publishable scientific finding.
- **Auto-scorer failure modes are themselves a finding.** FM-6/7/8/9 are concrete instances of reward-hacking on small-scale regex scorers, mirroring RLHF-scale failures. Connects directly to the "lazy frontier model" framing section above.
- **Specificity claim is conditional.** The 4×4 matrix would need to be run with coherence-gated scoring before we could cleanly claim virtue-specific behavioural effects. Without that, the MVP makes a weaker claim: "diagonal effects exist; off-diagonal specificity is unverified."
- **F94-UPDATE precedent is now repeated.** Day 10 caught hallucinated humility-theatre; Day 19 caught hallucinated transparency-theatre. The manual-first policy is doing its job. This is itself a methodological story worth telling.

### What this changes about Phase 5

`docs/phase5-plan.md` §3.0 now hard-requires coherence-gated scoring before any Phase-5 GPU spend. Without that, Phase-5 would multiply the FM-8 problem across 8 virtues × wider α grid.

The "all_clean MVP outcome → activate Phase 5" gating condition was **not** met (we're on partial). Per `phase5-plan.md` §2 activation conditions, Phase 5 is *conditionally* activated under partial outcome — but with revised expectations: Phase 5 would now be a methodology-improvement project (coherence gating + LLM-as-judge + negative controls) rather than a scope-expansion project.

### When to revisit (hand-review revision)

- After Phase 5 §3.0 coherence-gated scoring is implemented and the α-sweep is re-run with proper scoring (this would tell us whether the auto-scorer was just *wrong* or whether the underlying signal was genuinely small).
- If anyone else hand-reviews the same 690 generations with a different rubric (single-rater reliability concern; F72 caution).
- During writeup, when deciding how prominently to feature the "auto-scorer failure as finding" angle vs the "small real signals" angle.

---

## Document state

- **Created:** 2026-04-24 (Day 17), written while extraction is ~90% complete but before any analysis data exists.
- **Pre-registration discipline:** this document is being committed BEFORE MVE or specificity data lands, to prevent post-hoc tree-shaping.
- **2026-04-25 update (Day 18):** RLHF-compression / lazy-frontier-model framing section added as a *candidate* writeup angle (above), explicitly flagged as post-hoc interpretive framing rather than a pre-registered claim.
- **Related:** `docs/findings.md` F98, F102; `docs/eg-rt-eval-spec.md`; `docs/mvp-virtues.md`; `docs/extraction-runbook.md`; `docs/phase5-plan.md`.

---

## Day-23 update (2026-04-29) — v2 sweep behavioral findings + FM-13 implication for compositional steering

The Day-22 v2 sweep (16 cells × 5-10 prompts = 168 generations, hand-reviewed) produced findings that materially affect post-MVP design decisions. Promoted to F108. See `mvp/results/full_hand_review_v2_sweep.md` for full per-cell verdict.

### What changes from this update

**The "compose dynamically based on prompt" goal needs a baseline-quality gate.** FM-13 (commit-amplified error) shows that high-α commit-vector application on prompts where the baseline reasoning is *broken* produces confident wrong answers, not the desired abstention. Specifically: v_CC × α=12 on cc-s-08 (Tokyo population) committed to wrong answer (130M instead of 13M) because the baseline arithmetic was wrong; the steering forced commit on broken reasoning rather than fixing it.

For composition strategies this means:

1. **Don't unconditionally apply commit-vectors when prompt risks FM-8.** First check whether the model's pre-commit reasoning trace is internally consistent. If it isn't, applying the commit vector amplifies the inconsistency.
2. **Or accept that some commits will be wrong.** The post-mvp framing should not claim "v_IH/v_CC always improves outcomes." It improves outcomes specifically on disposition-limited prompts (per F45 scope condition) where the model has the right reasoning available but doesn't deploy it. On knowledge-limited prompts where the model's baseline inference is wrong, commit-vectors produce confident wrong answers.

### Implications for the writeup framing

The v2 sweep results give us cleaner story material for the writeup than yesterday's "calibration-vs-specificity" framing supported:

1. **The cross-model split (F102) is still the headline.** Same corpus, same method, opposite verdicts geometrically and behaviourally on qwen vs gemma.

2. **Geometric vs behavioral decoupling is a publishable methodology finding.** v_IH is geometrically orthogonal to all other virtues (cos ≤ 0.14) but produces nearly identical anti-FM-8 commit behavior to v_CC × L9. This is **downstream functional convergence**, not residual-stream redundancy. Implies: "geometric distinguishability is necessary but not sufficient for behavioral distinguishability." Important caveat for activation-steering claims in the literature.

3. **FM-1 through FM-13 catalogue is the most reusable artifact.** External Claude review explicitly flagged this as publishable independent of whether virtue vectors work. FM-13 (commit-amplified error) is a new addition that's especially relevant: it's a counterexample to the implicit claim that "more confident commit = better."

4. **F107 (corpus-generation task-level blind spot) is publishable.** When asked to "rewrite less evidence-grounded," frontier models across families preserve scientific specifics and edit framing instead. This is a cross-family task-level blind spot that the cross-family-verifier policy (§4.7 of generation-guidelines.md) does NOT catch. F107 documents the pattern + the mitigation (specify the contrast axis explicitly).

5. **The composition story is conditional**, not unconditional. Geometric orthogonality of v_IH and v_CC is necessary but not sufficient for meaningful composition (per F106 caveat). v_CC_full vs v_CC_numeric have opposite optimal α regimes (F108), suggesting that even within "the same virtue family" composition needs careful α-tuning per vector.

### Updated Phase 5 / post-MVP gating

`docs/phase5-plan.md` §3.0 coherence-gated scoring is now **less critical** post-Day-22 because hand-review has been the operational gate throughout. But it's still useful to formalize for future scale-up.

What's added as a hard prerequisite for any further claims:

- **Hand-review every cell** of every steering sweep. Auto-scorers (including v2 scorers) credit FM-13 errors as success. Hand-review is the only reliable signal of correctness.
- **Track which prompts are FM-8-prone vs not.** FM-8-prone prompts are where commit-vectors help; FM-8-not-prone prompts where reasoning is broken are where commit-vectors hurt (FM-13).
- **Before claiming compositional improvement**, run the actual composition test (vIH + vCC simultaneously, hand-rate). Geometric orthogonality is not a substitute.

### When to revisit (Day-23 hand-review revision)

- After Round 3 sweep completes (bidirectional + composition + Bayesian-prompts A/B). Will tell us whether mechanism is shared-circuit or different-circuits, and whether composition is meaningful.
- During writeup, when deciding how to frame FM-13 — as a discovered limitation, as a counterexample to optimistic steering claims, or as a separate methodology paper.
- If v_EG_v2 high-α (α=12) on abstention shows it suppresses Gandhi confabulation entirely, the v2 corpus redesign success can be claimed; if not, the "calibration-vector-with-specificity-mixed-in" reading wins.

---

## Day-23 evening update (2026-04-29) — Round 3 sweep + logit inspection (F109)

Round 3 sweep complete. 121 generations hand-reviewed (no auto-scorer). Promoted to F109. See `mvp/results/full_hand_review_round3.md` for per-cell verdict and `mvp/results/eg_logit_inspection.json` for token-level trajectory.

### What this changes for the post-MVP plan

**1. Composition is non-additive — the "compose dynamically based on prompt" goal needs a per-vector α-selection gate, not just a baseline-quality gate.**

The Day-23 evening composition test (vIH + vCC at α=8+8 on 10 fresh prompts + composite on diagnostic suite) showed:

- Composite **fixed** the ip-longest degenerate-loop that vCC alone produced at α=8/12.
- Composite **kept** the Tokyo population correct (vs FM-13 at vCC α=12 alone).
- Composite **helped** one premise-flag (T. rex gestation).
- Composite **inherited** the Gandhi-1957 fabrication and stock-$185.55 hallucination from vCC at α=12.
- Composite **degraded** specificity on lead-pipes (<10% vs <1% for the singletons).

Composition is roughly comparable to either knob alone in quality terms, NOT strictly better. The per-prompt fix-vs-amplify pattern is asymmetric and prompt-dependent.

For the post-MVP framing this means:

- "v_IH and v_CC compose meaningfully" needs to be qualified as "compose meaningfully on a subset of prompts, while inheriting failure modes from one or both on other prompts." This is a weaker claim than the original "compose dynamically" framing implied.
- The compositional-steering goal needs both: (a) a baseline-quality gate (don't apply commit when reasoning is broken — FM-13 risk per F108) AND (b) an α-selection gate per vector per prompt-type (since same vector at α=4 vs α=12 produces qualitatively different output, and pairs of vectors at α=8+8 produce different output again).

**2. FM-13 is a resonance phenomenon, not a magnitude effect — α is a rail-selector, not a strength dial.**

Logit inspection on the Gandhi prompt at α∈{0,1,2,4,6,8,10,12} shows the steered hidden state crosses the next-token decision boundary at *different generation steps* for different α. At α=1-7 it crosses at step 36 (` was`→` actually`) and locks onto "did win once in [date]" rail. At α=8 it crosses at step 46 (` actually`→` nominated`) and locks onto "was nominated, never won" rail. At α=10/12 it crosses at earlier steps but lands on different rails again.

This means **the FM-13 mitigation cannot be "lower α to avoid commit-amplified-error"**. Lower α may cross the boundary at a position that lands on a *different fabricated rail* (e.g., the α=4 "1937 award" rail). The mitigation has to be prompt-specific rail-selection, which the vector-and-α tuple alone does not provide.

For the post-MVP plan: the simplest workable strategy is α-sweep per prompt + hand-review for rail selection. Automated rail selection would require either (a) knowing the gold answer in advance, or (b) running multiple α and picking the most-honest-sounding output via another model — both expensive. The honest framing is "we have a discovered behavioral phenomenon, not a deployable steering recipe."

### Implications for the writeup framing (refined)

1. **FM-13 promoted from "discovered limitation" to "central mechanism finding."** F109 finding #1 (rail-switch) and finding #2 (cross-vector fingerprint differences) together are concrete, mechanistically-detailed evidence that activation steering doesn't work the way the literature implicitly claims (smooth dial). The rail-switch story is publishable independent of whether virtue vectors are deployable.

2. **The composition story stays conditional.** Day-22's "geometric orthogonality is necessary but not sufficient" caveat is now backed by behavioral data: vIH+vCC at α=8+8 produces non-additive output. The writeup should frame composition as a *probe of representation structure* (does composition reveal additional shared circuitry) rather than as a *deployment recipe* (compose dynamically for better outcomes).

3. **Phase 2 (phi-3.5-mini) is the cross-model robustness check for F109.** The F109 mechanism (rail-switch, FM-13 fingerprint) was characterized only on qwen3-4b. Whether it transfers to phi-3.5-mini determines whether F109 is a qwen-specific quirk or a general property of small open models.

### Phase 2 (queued — start now per user direction)

Phi-3.5-mini extraction + sweep + hand-review.

Goals:
1. Determine whether phi-3.5-mini-instruct exhibits behavioral effects from steering at all (per F102 cross-model split — phi could be like qwen-behavioral or like gemma-null).
2. If behavioral, characterize the cosine matrix and AP-peak layers.
3. Re-run the F109 logit inspection on phi to see if the rail-switch mechanism is qwen-specific or general.
4. Test whether composite (vIH+vCC) on phi exhibits the same non-additive pattern.

Plan:
1. Download phi-3.5-mini-instruct (3.8B, 32-layer) — local first, then push to VM.
2. Verify model loads on L4 + measure tokens/sec.
3. Add phi to `MODEL_CONFIGS` in `mvp/utils.py` (layer accessor, attention head count, hidden size).
4. Run extract_v2.py on the 4 v2 corpora at all layers.
5. Compute cosine matrix at all layers; identify AP-peak layers via attribution patching.
6. Run a scaled-down sweep: baseline + each virtue at AP-peak layer at α∈{4,8,12} on diagnostic + EG + abstention + cc-simple + composition-test.
7. Hand-review every cell.
8. Compare vector-norms and cosine pattern to qwen v2.
9. Run logit inspection on Gandhi at multiple α to test the rail-switch transfer.

Estimated: 2-3 days end-to-end.


---
## Day-25 update (2026-05-03) — Cross-model 1,752-generation hand-review + product-hypothesis pivot

Cross-model run complete on phi-4-mini-reasoning + llama-3.1-8B-R1-GRPO + openr1-qwen-7b. F110/F111/F112 landed in `findings.md`. Three updates to the post-MVP decision tree.

### Update 1: Add a "layer-screening" rule before any sweep

**Finding:** Phi-4 L3 is intrinsically unstable — both CC_num_L3 and VC_L3 catastrophically collapse at high |α| across all 8 prompts (identical FM-8-severe phenotype regardless of vector content). Phi-4 L7 (where v_IH was extracted) produces premature-EOS at α≥+16 on most prompts.

**Decision rule (added to "Cross-cutting: what to do in ALL outcomes"):**

> **L0: Before any α-sweep on a new model, run a layer-screening pass.** Steer with each candidate vector at α=±20 only; if the layer produces FM-8-severe (cap-truncation, repetition loops, single-EOS collapse) at α=±20, the layer is unsuitable for sweeping. Skip it. Only sweep layers that survive α=±20 without catastrophic collapse.

**Why this matters:** We wasted ~30% of our cross-model run sweeping unstable layers (phi-4 L3 across CC_num+VC = 192 generations of cap-truncation; phi-4 L7 IH high-α = ~24 collapsed cells). A 30-minute layer-screening pass would have flagged these before the sweep.

### Update 2: Drop "humility installer" / "calibrated-confidence amplifier" from product hypothesis

**Finding:** F111 — IH hypothesis decisively falsified across 4 testable prompts (E1, N2, E2, E3) on 3 model families. On openr1, IH×L25 at high α produces *worst-form* fallacies, not humility.

**Decision rule:** Remove "humility-amplification" from candidate product use cases. The contrastive-triplet extraction method does not produce a working humility vector at the layers tested across 3 model families. If humility/abstention amplification is needed downstream, **the right method is not activation steering at the residual stream** — investigate behavioral RL, SAE feature targeting, or per-layer probing instead.

### Update 3: Pivot product hypothesis to "commitment amplifier for non-committal reasoning models"

**Finding:** F112 — OpenR1 commitment-rescue. Across 2 prompts (N1, E3) × 6 vectors × 12 α on openr1, steering breaks self-debate loops and forces commitment. ~50/144 (35%) ✓ rate from a 0/2 baseline.

**Updated product hypothesis (replaces older "virtue installer" framing):**

> **Activation steering breaks self-debate / non-commitment loops in thinking models, forcing commitment to the model's most accessible reasoning rail. The commitment is correct when the rail is correct. This is a useful capability for thinking models that loop instead of committing on hard reasoning prompts.**

**Why this is narrower than "virtue installer":**
- Doesn't claim to *install* novel reasoning circuits (we've shown it can't — F110 + F111)
- Doesn't claim to *amplify virtue* in general (we've shown it can amplify wrong rails too — F108 FM-13)
- Does claim to *break non-commitment loops* — supported by 50/144 ✓ on openr1 N1+E3

**Concrete use case for the commitment-amplifier framing:**

Thinking models in deployment that:
- Have correct reasoning ability (per their training) but
- Tend to loop or self-debate on hard prompts without committing → produces verbose, indecisive outputs

Steering forces commitment. The commitment is correct most of the time (35-56% on openr1 N1+E3), wrong some of the time. The cost-benefit is:
- Improved commit rate (from 0% to 35%+)
- Some risk of FM-13 (committing to wrong rail) — F108/F109/F110 quantify this risk
- Net: better than baseline non-commitment IF you can monitor for FM-13

### Updated "what to do in ALL outcomes" cross-cutting list

Adding three rules from F110-F112:

L0. **Layer-screening before any sweep.** Steer at α=±20 first; skip layers that catastrophically collapse.

L1. **No more humility-vector experiments.** Method demonstrably doesn't work at residual-stream level for this disposition. (Replaces older "calibrated confidence" agenda from F92.)

L2. **Test commitment-amplifier hypothesis on additional non-committal models.** OpenR1 N1+E3 is suggestive but n=2 prompts × 1 model. Need to test on r1-distill, gemini-thinking, o3-mini, or similar to see if F112 generalizes.

### Test plan for F112 generalization

If we want to validate F112 as a generalizable post-MVP product:

1. **Acquire 2-3 more non-committal thinking models.** Candidates: r1-distill-qwen-32b, deepseek-r1-distill-llama-8b, qwen3-32b-thinking, gemini-2.0-flash-thinking, o3-mini.
2. **Identify their non-commitment failure modes** at baseline. Do they loop in `<think>` on hard prompts? Do they exhaust token budget?
3. **Apply commitment-amplifier vectors** (CC_full or CC_num at deep layers, the F112-supported configurations).
4. **Measure commit rate before vs after.** Hand-review every cell.
5. **Quantify FM-13 cost.** Of the new commitments, how many are correct vs FM-13 (committing to wrong rail)?

Target: 3 additional models × 4 reasoning prompts × 4 vectors × 6 α = ~288 generations to validate F112 generalization.

### Cap-extended re-run for phi-4 (separable problem)

Phi-4 fails on N2/E3/E4 by exhausting 8192-token budget; reasoning is correct in visible portion. **This is a separable, tractable problem.**

**Recommendation:** Re-run phi-4 × CC_full × N2 + E3 + E4 at 16k or 32k cap. Compare ✓ rate before/after. If ✓ rate jumps from current 12-17% to 70%+, confirms cap-truncation was masking otherwise-correct reasoning. This would be a 100% mechanical win (no reasoning improvement needed; just more tokens).

Estimated: 36 generations × ~5 min each = 3 hours of compute. Sub-day work.

### What this all means for the MVP→post-MVP transition

The MVP is functionally **wrapping**. F110+F111+F112 are the strongest cross-model evidence we have, and they:
1. Confirm F109's "rails not virtues" thesis at 14× scale
2. Falsify the most theoretically motivated vector hypothesis (IH)
3. Support a narrower, cleaner product hypothesis (commitment amplifier)

The post-MVP work should therefore:
- Validate F112 on 2-3 more thinking models (commitment-amplifier generalization test)
- NOT pursue further humility/abstention extraction work (F111 falsification)
- NOT pursue further compositional virtue-installer work (F109 non-additivity)
- Run the cap-extended phi-4 re-run as a quick mechanical win
- Consider writing up F109+F110+F111+F112 as a paper draft with the "three failure shapes" framing

The candidate framing for the writeup section ("the lazy frontier model / RLHF-compression phenomenon") connects naturally to F112: thinking models that *loop instead of committing* may be exhibiting a learned "uncertainty hedge" from RLHF, and commitment-amplification is the activation-level intervention that breaks that hedge. Worth elaborating in the paper draft.

