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

`docs/scoring.md` FM-6: deficiency-non-virtuous passages that use evidence vocabulary while making confident-causation claims scored high on the EG regex scorer. That is reward-hacking, on our own scorer. We had to Opus-review every generation specifically because writers (and models) game vocabulary-level rewards.

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

## Day-19 Opus-reviewed revision (2026-04-26 — F103 lands)

The α-sweep finished and the auto-scorer reported a +5.19 RT diagonal effect on qwen × RT × L18 α=20 — by far the largest behavioural signal in the entire MVP. Opus-judged review of all 690 generations (independent Opus session, full pass with structured signal extraction) revealed: **the +5.19 is fake.** All 5 items in that cell are catastrophic repetition loops with no closing `<think>` tag; the high score comes from regex-friendly filler tokens embedded in those loops. This is FM-8 (`docs/scoring.md`), reproducing the F94-UPDATE failure mode at larger scale.

**The headline is retracted.** Real signals revealed by Opus-review are an order of magnitude smaller and require careful framing.

### What the Opus-review *actually* showed

Per-cell Opus-rubric (1-5 scale per virtue), baseline-anchored:

| Model × Virtue | Baseline | Best clean cell (Opus-rubric) | Δ vs baseline |
|---|---|---|---|
| qwen × CC (AIME) | 2.4 | L25 α=8 (or any L25/L22 mid-α) | **+0.4** |
| qwen × IH (abstention) | 3.2 | L20 α=20 / L22 α=12 (multiple ties) | **+0.8** |
| qwen × RT (rt-eval) | 3.0 | **L22 α=8** | **+0.6** |
| qwen × EG (eg-eval) | (effectively zero) | None — flat across all cells | ~0 |
| gemma × all four virtues | various | None — null result | 0 ± 0.4 |

Real diagonal effects on qwen are in the **+0.4 to +0.8 range** — present, hand-verified, but ~10× smaller than the auto-scorer claimed. Gemma is confirmed null at all α values tested.

### Specificity claim is independently weakened

Opus-review Priority-5 finding: CC steering on qwen also produces RT-marker-rich prose (item 42 in CC×L25 α=20 has 110 step markers in its thinking trace). Even setting aside the L18 α=20 degeneracy, the +5.19 effect could not have been cleanly attributed to RT-direction-specific behaviour vs "more structured reasoning generally." This is the F39 AOT-cluster risk re-materialising at the behavioural level, matching F102's geometric finding.

### Auto-scorer picks were wrong

The auto-scorer-picked cells are NOT the Opus-rubric-best cells:

| (model, virtue) | Auto-scorer pick | Hand-rubric best | Why they differ |
|---|---|---|---|
| qwen × RT | L18 α=20 (degenerate) | L22 α=8 | Auto rewards loop-tokens; hand sees catastrophe |
| qwen × IH | L18 α=20 (hallucinates fp-gandhi) | L20 α=20 / L22 α=12 | Auto rewards regex-friendly abstention; hand sees fabricated humility |
| qwen × CC | L25 α=20 | L25 α=8 (or any L25/L22 mid-α) | Auto's hedge-proxy correlates with steering; hand sees ~equivalent quality across mid-α |

**For any downstream use** (4×4 specificity matrix, writeup), use the Opus-rubric picks above, not the auto-scorer picks in `mvp/results/alpha_sweep/{model}.json`.

### Updated F98 branch interpretation

We are firmly on the **partial branch** of F98, but with substantial caveats:

| F98 dimension | Original verdict | Day-19 Opus-reviewed revision |
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

### When to revisit (Opus-reviewed revision)

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

The Day-22 v2 sweep (16 cells × 5-10 prompts = 168 generations, Opus-judged) produced findings that materially affect post-MVP design decisions. Promoted to F108. See `mvp/results/full_hand_review_v2_sweep.md` for full per-cell verdict.

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

`docs/phase5-plan.md` §3.0 coherence-gated scoring is now **less critical** post-Day-22 because Opus-review has been the operational gate throughout. But it's still useful to formalize for future scale-up.

What's added as a hard prerequisite for any further claims:

- **Hand-review every cell** of every steering sweep. Auto-scorers (including v2 scorers) credit FM-13 errors as success. Hand-review is the only reliable signal of correctness.
- **Track which prompts are FM-8-prone vs not.** FM-8-prone prompts are where commit-vectors help; FM-8-not-prone prompts where reasoning is broken are where commit-vectors hurt (FM-13).
- **Before claiming compositional improvement**, run the actual composition test (vIH + vCC simultaneously, hand-rate). Geometric orthogonality is not a substitute.

### When to revisit (Day-23 Opus-reviewed revision)

- After Round 3 sweep completes (bidirectional + composition + Bayesian-prompts A/B). Will tell us whether mechanism is shared-circuit or different-circuits, and whether composition is meaningful.
- During writeup, when deciding how to frame FM-13 — as a discovered limitation, as a counterexample to optimistic steering claims, or as a separate methodology paper.
- If v_EG_v2 high-α (α=12) on abstention shows it suppresses Gandhi confabulation entirely, the v2 corpus redesign success can be claimed; if not, the "calibration-vector-with-specificity-mixed-in" reading wins.

---

## Day-23 evening update (2026-04-29) — Round 3 sweep + logit inspection (F109)

Round 3 sweep complete. 121 generations Opus-judged (no auto-scorer). Promoted to F109. See `mvp/results/full_hand_review_round3.md` for per-cell verdict and `mvp/results/eg_logit_inspection.json` for token-level trajectory.

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
## Day-25 update (2026-05-03) — Cross-model 1,752-generation Opus-judged review + product-hypothesis pivot

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

**Finding:** F112 — OpenR1 commitment-rescue. Across 2 prompts (N1, E3) × 6 vectors × 12 α on openr1, steering breaks self-debate loops and forces commitment. 76/144 (52.8%) ✓ rate from a 0/2 baseline [corrected 2026-05-13 from prior ~50/144 (35%) arithmetic error].

**Updated product hypothesis (replaces older "virtue installer" framing):**

> **Activation steering breaks self-debate / non-commitment loops in thinking models, forcing commitment to the model's most accessible reasoning rail. The commitment is correct when the rail is correct. This is a useful capability for thinking models that loop instead of committing on hard reasoning prompts.**

**Why this is narrower than "virtue installer":**
- Doesn't claim to *install* novel reasoning circuits (we've shown it can't — F110 + F111)
- Doesn't claim to *amplify virtue* in general (we've shown it can amplify wrong rails too — F108 FM-13)
- Does claim to *break non-commitment loops* — supported by 76/144 ✓ on openr1 N1+E3

**Concrete use case for the commitment-amplifier framing:**

Thinking models in deployment that:
- Have correct reasoning ability (per their training) but
- Tend to loop or self-debate on hard prompts without committing → produces verbose, indecisive outputs

Steering forces commitment. The commitment is correct most of the time (35-56% on openr1 N1+E3), wrong some of the time. The cost-benefit is:
- Improved commit rate (from 0% to ~53%) [corrected 2026-05-13 from prior 35%+ arithmetic error]
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


---

## Day-30+ candidate plans (added 2026-05-08, post literature-survey)

After the 5-model 2,443-generation Opus-judged review wrap, surveyed recent literature (2025-2026) to position our work. Three competing/extending papers identified:

- **arxiv 2506.18167** (Jun 2025) "Understanding Reasoning in Thinking LLMs via Steering Vectors" — closest predecessor. DeepSeek-R1-Distill on Qwen-14B/1.5B + Llama-8B, 6-behavior taxonomy, **NO random-vector control** (their explicit limitation, our advantage)
- **ReBalance (ICLR 2026)** — directly competing positive result. Training-free LRM steering with confidence-modulated dynamic strength; ~50% token reduction on GSM8K
- **The Rogue Scalpel (arxiv 2509.22067)** — negative result. *"Random direction can increase harmful compliance from 0% to 1-13%"* — random vectors DO have effects on safety axis (different axis from our rescue axis)

Field consensus from 2026 field guide (Subhadip Mitra): static CAA-style steering has been replaced by Steering Vector Fields, SAE-guided (YaPO), AUSteer, Conceptor-based, CAST, Adaptive/PID dynamic. Reliably steerable: refusal, sentiment, tone, conciseness, uncertainty expression. **Effectively unsteerable: factual accuracy, complex reasoning, specific fact injection** — F45 is now field consensus.

### Path A — "Publishable negative-result + narrow-positive" paper (recommended)

**Title sketch:** *"Activation Steering for Reasoning-Model Self-Debate: A 2,443-Generation Hand-Reviewed Cross-Family Study"*

**Headline structure:**
- **F111** — IH-vector hypothesis falsified across 4 prompts × 3 models (most theoretically motivated vector demonstrably doesn't work)
- **F112** — Commitment-amplification is real, Qwen-pretraining-base-specific, requires structured perturbation (random vectors don't rescue)
- **Three failure-shape taxonomy** (template lock / non-commit loop / cap-truncation) determining steerability

**What we already have to ship this:**
- 1,752 cross-model + ~691 earlier qwen+gemma + 24 random control = 2,467 Opus-judged generations
- Random-vector control on qwen3-4b L22 (Day 12 archive) — most papers don't have this
- Cross-pretraining-family coverage (Phi-4, Llama-3.1-R1-GRPO, OpenR1-Qwen-7B, Qwen3-4B, Gemma-4-E4B-it)
- F-numbered findings F92-F112 with full cross-references in `docs/findings.md`
- Per-prompt synthesis docs + 87 detailed rescue cases in `cross_model_analysis_20260502/`

**Concrete next steps to ship:**
1. **Run F112 on OptimalThinkingBench** (arxiv 2508.13141 — 1,440 OverthinkingBench + 550 UnderthinkingBench, procedurally generated, 33-model leaderboard). Get a benchmark number directly comparable to o3 (72.7% F1) and GPT-OSS-120B (62.5%). Half-day of compute.
2. **Run random-vector control on openr1-qwen-7b at L23-L25 with full 12-α grid** (~72 generations, 1-2 hours) — closes the random-control gap on the actual cross-model run, not just qwen3-4b at L22. If random STILL doesn't rescue, F112 graduates from "consistent with structured-perturbation hypothesis" to "demonstrated structured-perturbation requirement."
3. **Add R1-Distill-Qwen-14B and R1-Distill-Llama-8B as 6th and 7th models** — directly comparable to arxiv 2506.18167. ~2 days of compute + hand-review.
4. **Write up.** Most narrative content already exists in cross_model_analysis_20260502/ docs.

**Estimated total:** 4-7 days end-to-end (compute + writing).

**Risk:** ReBalance got there first with the positive framing, so the "narrow positive" portion of our paper is competing with already-published work. The negative-results portion (F111 falsification + random-control) is the differentiator.

### Path B — Tool-use harness probe (for cleaner mechanism evidence)

The just-merged `claude/review-reports-nVMcN` branch added a complete tool-use harness (`mvp/tool_use_harness.py`, `mvp/run_tool_experiment.py`, etc.) with random-vector control built in. Tool-calling is **binary and measurable**, where reasoning quality is fuzzy.

**Test:** does v_IH × L17 × α=8 (the canonical commit-amplifier) increase `<search>` tool-call rate on knowledge-gap prompts? Does the random vector at the same magnitude not increase it?

**Why this is cleaner than reasoning probes:**
- "Did the model emit `<search>...</search>`" is a yes/no measurement; "did the model commit to a Bayesian update" requires hand-review
- Tool-call rate is a single number per (vector × α × prompt) cell; rescue verdicts are 3-valued (✓/~/✗)
- Knowledge-gap prompts are exactly where humility-vector should help; if it does we have a clean F112-supporting result, if it doesn't we have another F111-supporting falsification

**Concrete next steps:**
1. Configure `mvp/tool_use_experiment.example.json` to: baseline + v_IH @ L17 α=8 + random @ L17 α=8
2. Build a 20-prompt knowledge-gap set (E1-style "what was X?" probes for things models don't know)
3. Run the harness end-to-end — produces JSONL trajectories + per-condition tool-call rate / mean calls / termination histogram
4. Compare tool-call rate: virtue-vector vs random-vector vs baseline
5. Get a clean single-paragraph mechanism statement

**Estimated:** 1-2 days end-to-end.

**Why pair this with Path A:** the tool-use result becomes a sharper supporting figure in the paper. "Commitment amplification produces measurable behavioral change on a discrete action (tool-calling) on knowledge-gap prompts, with structured-perturbation vectors but not random ones at matched magnitude." That's a tighter claim than the rescue-rate framing alone.

### Path C — Pivot to dynamic/conditional steering (TO DISCUSS)

**Status:** flagged for user discussion before adding to plan.

The field has moved past static CAA-style steering toward dynamic/conditional methods (CAST, AcT, Steering Vector Fields, Conceptor-based, Adaptive/PID). ReBalance specifically uses confidence-modulated dynamic strength — the closest competing positive result.

This is a bigger pivot than Paths A or B. Worth a real conversation about scope, target venue, and whether it's worth re-running the cross-model work with dynamic steering.

**Decision:** discuss with user before committing. Do NOT add to plan unilaterally.


### Interest list — clusters from 2026-05 field-overview discussion

After reviewing the 2026 field-overview (8 active research clusters), user flagged interest in three specific threads. Logging here so they don't fall out of context, separate from Paths A/B/C decision tree above.

**Cluster 1 — Beyond static vectors: Adaptive / PID dynamic steering** (interested)

α changes across generation tokens rather than being held constant. PID-style: apply more steering when the model is drifting from target behavior, less when it's already on-rail. Closer to a control system than a one-shot intervention.

Relevance to our work:
- F109 already documented that the rail-switch happens at a single thinking-token. Static α applies the same push at every step; PID would only push at the rail-switch step.
- Would test cleanly against our existing rescue dataset — same prompts, same models, dynamic α instead of static.
- Pairs naturally with F112: "fire commitment-amplifier only when self-debate is detected, not always-on."

**Cluster 2 — Beyond contrast pairs: SAE-guided steering** (most-interested; see SAE feasibility analysis below)

Pick steering directions from sparse-autoencoder features instead of mean-difference of contrastive triplets.

Sub-methods worth surveying: YaPO (eliminates contrast pairs entirely), AUSteer (atomic-unit steering), Conceptor matrices, Concept-Basis Reconstruction.

Particularly relevant to our work:
- F111 (IH-vector falsification) suggests the contrastive-triplet method may be the wrong extraction tool for humility-class concepts. SAE features might find a humility-related direction that diff-of-means missed.
- F109 (rail-switch mechanism) — SAE could pinpoint the specific feature that flips at the rail-switch token, converting our finding into a deeper mechanism story.
- Already noted in journal/phase5-plan as "deferred" — now under active reconsideration.

**Cluster 7 — Reasoning-specific: OptimalThinkingBench** (interested)

1,440 OverthinkingBench questions + 550 UnderthinkingBench problems. Procedurally generated (no contamination). 33 models evaluated. Best o3 at 72.7% F1; GPT-OSS-120B at 62.5%.

Relevance:
- Putting F112 commitment-amplifier on this benchmark gives us a directly comparable number for the publishable paper (Path A).
- The benchmark framing (over↔under-thinking trade-off) is exactly F112's framing.

**Not currently of interest (logged for completeness):** Cluster 3 (beyond-residual-stream / MLP-channel ablation), Cluster 4 (multi-layer coordinated), Cluster 5 (CRH / non-identifiability), Cluster 6 (cross-model universality), Cluster 8 (safety / negative-result).

---

---
## Day-26 update (2026-05-09) — Cluster 2 (SAE-guided steering) committed

The Day-25 "Interest list" flagged Cluster 2 (SAE-guided steering) as the most-interested follow-up. Day-26 work confirmed Neuronpedia has Layer-17 transcoder coverage for qwen3-4b (Hanna & Piotrowski), did initial feature exploration, identified candidate humility-aligned features, and committed to running the steering test locally.

Detailed plan, candidate-feature shortlist, additional searches to run, and experiment design: see `docs/sae-experiment-plan.md`.

This effectively replaces the "Path B — tool-use harness probe" direction as the active follow-up. Tool-use harness remains parked (already merged to main as the `claude/review-reports-nVMcN` branch contents) for later use; SAE feature-steering is the more direct test of the F111 question.

---
## Day-27 update (2026-05-10) — SAE work expanded from 1 model to 5; three new interpretive findings

VM unavailable for ~24 hrs, so Day 27 was spent expanding SAE search-and-triage from qwen3-4b only to all 5 cross-model subjects. Per-feature dashboards verified for 37 candidate features across Qwen2.5-7B-Instruct (proxy for openr1-qwen-7b), Llama-3.1-8B-base + R1-Distill-Llama-8B (two proxies for our llama-3.1-8B-R1-GRPO subject), and Gemma-3-4B-IT (proxy for gemma-4-E4B-it). Phi-4-mini-reasoning excluded — no SAE coverage on Neuronpedia.

Detail in `docs/feature-catalog.md` (cross-model summary table at end). Plan in `docs/sae-experiment-plan.md` updated with new cross-model expansion section. F113 in `docs/findings.md` now has a Day-27 update sub-section recording the three interpretive findings.

**Practical impact on the post-MVP path:**

- **Cluster 2 (SAE-guided steering) scope grows.** The originally-planned steering experiment was 1 model × 7 features = ~36-72 generations. Cross-model expansion makes it 5 models × ~3 T1 features each = ~15 cells, ~180 generations. Still sub-day on an L4-class VM. Now produces three independent falsifiable predictions to discriminate between F111-as-method-failure and F111-as-deeper-finding, instead of one.

- **Cluster 7 (OptimalThinkingBench) gains a stronger F112 test.** R1-Distill-Llama-8B feature 19103 (" confident" → "**Final Answer**" closure feature) is the cleanest commitment-amplifier candidate found — direct cross-architecture test bed for F112 (originally a Qwen-family finding). Pair with 15372 (prospective-doubt) for verify-vs-commit dose-response. If F112's mechanism replicates on Llama-family R1 with this pair, the "commitment amplifier" hypothesis hardens into a publishable cross-family generalization.

- **Cluster 1 (PID dynamic steering) gets a cleaner integration story.** With both directions of the verify→commit axis isolated as discrete features (15372 and 19103), the natural application of dynamic steering is "amplify 19103 only when 15372 is firing strongly past a threshold" — fire commit-pressure only when self-debate is detected. This is closer to a real PID controller than the current static-α approach. Worth a Phase-5 or whitepaper experiment.

- **F102 mechanistic story becomes a sub-result.** Gemma's three Tier-1 features all decompose into trained-template emission (interpretation a — see F113 Day-27 update for detail), explaining why diff-of-means produced a null on Gemma in F102. If the steering experiment confirms the prediction (amplifying disclaimer-cluster produces paste, not genuine abstention), F102's null result gets a clean mechanistic explanation rather than remaining a brute fact. Worth a paragraph in any F111-paper writeup.

No path/scope decisions changed today — Cluster 2 remains the active follow-up, Clusters 1 and 7 remain "interested." But the three new interpretive findings from Day-27 strengthen the case for completing Cluster 2 before deciding on Cluster 1 / 7 commitments.

---
## Day-27 evening update (2026-05-10) — F112 cross-architecture test bed sharpened

API-batch verification (detail in journal Day-27 evening + `mvp/sae_neuronpedia_data/`) found that the F112 cross-architecture story is **more constrained** than the morning analysis suggested.

**Before:** F112 cross-architecture test on R1-Distill (15372 ↔ 19103), with possible extension to other models.

**After (further sharpened by dashboard verification 2026-05-10 evening):** F112 test bed is uniquely R1-Distill-shaped, and the constraint is even tighter than the morning analysis suggested. **R1-Distill at L31 has 3 clean commit/abstention features** (15372 + 19103 + 2136 — the last has the cleanest commit-vs-hedge logit polarity in the catalog and dashboard-verified uniformity in top-25 activations). **No other model has any clean commit feature at the same target layer as humility:**
- Qwen2.5-7B: 18575 was originally classified MCQ-domain commit (T2), but dashboard verification revealed it's a user-prompt-template detector for MMLU-style benchmarks — fires on input scaffolding, not on output commitment. Demoted to T3. **No commit feature at L23.**
- Llama-3.1-8B: no commit feature at L31
- Gemma-3-4B-IT: commit features exist but at L1/L18/L22/L29/L33, not at the L17 humility layer
- qwen3-4b: L29 idx 59103 was the lone passable candidate; dashboard surfaced additional `hopeful` contamination weakening confidence. No clean commit feature anywhere in transcoder-hp L9-L30 (API-verified across 14 search terms).

**Implication for the post-MVP path:** F112 generalization claims need to be carefully scoped. "Commitment-amplifier generalizes from Qwen-family to Llama-family R1" is supportable if the steering experiment lands. "Commitment-amplifier is a general SAE-feature mechanism across pretrained reasoning models" is NOT supportable from this evidence — it's specifically R1-style. This tightens what the F112-headline paper can claim.

The F45 cultural-register mechanism story now has a third instance: evidence-grounding-as-medical-research-register on qwen3-4b L7. Three instances make this strong enough to belong in any F111 paper writeup as the mechanistic story behind why diff-of-means contrastive extraction produces behavioral artifacts (F112 commit-amplifier) rather than the targeted virtue.

---
## Day-28 update (2026-05-11) — NLA (Natural Language Autoencoders) investigated, not actionable now

User flagged Neuronpedia's new NLA section. Gemini headless-browser verification showed:

- **Activation Reconstructor (text → vector) is NOT publicly exposed** — only the Activation Verbalizer (activation → text). Earlier "zero-shot vector extraction" framing was a Gemini hallucination, not a real user-facing capability.
- **NLA model coverage on Neuronpedia: Llama 3.3 70B-IT and Gemma 27B only.** Neither matches any of our 5 subjects.
- Paper: `transformer-circuits.pub/2026/nla/index.html` (Fraser-Taliente, Kantamneni, Ong et al. 2026). Codebase: `github.com/kitft/natural_language_autoencoders`. Both open access.

**Decision: defer. No project-changing implication right now.**

Two future-work hooks:
1. If F111 paper review pushes us to compare against an additional extraction method, training our own NLA for one of our subject models is feasible (~weeks of compute) since the codebase is open. Don't pre-commit.
2. The NLA paper deserves a brief citation in the "alternative methods" section of the F111 paper writeup — different extraction philosophy (activation ↔ text directly), orthogonal to our diff-of-means vs SAE-feature comparison.

**Bonus finding while there:** Neuronpedia's interactive Steer page now supports `llama3.1-8b (Base)` — the only one of our 5 models on the page. We could use this for one-off qualitative pre-tests of Llama-base steering candidates (7984, 201, 121957) before VM is back. Marginal value (Base only, not the R1-GRPO subject we actually use) but free if we want it.

Detail: `mvp/sae_neuronpedia_data/nla_investigation_2026-05-11.md`.

## Day-30 update (2026-05-13) — Cluster 2 SAE-guided steering: empirical close-out on the L17/L23/L31 residual-stream additive branch

The Day-26 commitment to Cluster 2 (SAE-guided steering) has now run to completion. Full battery: 5 models × 5 SAE families × 31 cells × 1,110 generations, all Opus-judged (`mvp/results/sae_steering_analysis_20260513/`).

**Headline result**: the answerable form of the Cluster-2 question ("can SAE-feature additive steering at the IH-extraction layer install humility / verification-disposition behavior in current open-weight models?") is **NO** with high confidence. Documented in F115-F119.

**Specifically falsified hypotheses**:
1. F114's "rank-1980 humility-content feature 101568 produces abstention where v_IH didn't" — fails (F115)
2. F112's "doubt-feature amplification produces abstention on R1-style architecture" — fails, amplification *induces* confabulation (F116)
3. The cross-model parallel for E2 contested-evidence — 0/267 generations clear the bar (F117)

**Cluster-2 decision update**:
- The "SAE-guided steering as primary virtue-installation mechanism" lead is now closed.
- Three sub-branches remain *technically* open but each is a new experiment, not a continuation: (a) output-stage layer steering (L25+), (b) negative-α on commit features, (c) corpus-redesign v3 with anti-register-leakage controls.
- The Cluster-2 product-side hypothesis ("commitment amplifier as a generalizable virtue-installation pattern") is contradicted by the F116 result. If we want to pursue it as a productization story, it needs to be framed differently — *as a commit-amplifier failure mode discovery*, not as a virtue-installation success.

**What stays valuable from Cluster 2**:
- The F111 → F114 → F115 falsification chain is now empirically airtight and publishable as a negative result on SAE-steering for virtue installation.
- F118 (FM-fabricated-citation extension to fake-URL / fake-event / fake-institution) is direct safety-relevant for agentic / RAG / research-assist systems and would not have surfaced without the steering battery.
- The methodological discipline (random-control matching, alpha-grid efficiency, FM taxonomy completeness) carries forward to any future steering work in Clusters 1/7 or beyond.

**Net decision on the Cluster-1 / Cluster-7 priors that were waiting on Cluster-2 closure**:
- Cluster 1 (probe-based diagnostics) and Cluster 7 (corpus v3) are now eligible for first-class consideration. The "let Cluster 2 finish first" gate is open. Neither is committed yet — separate decision required.
- The strongest case for a Cluster-7 (corpus v3) follow-up is F107 + F114 + F115 stacked: the contrastive corpus failed to isolate humility content at the *extraction* level, the projection to SAE-basis failed to find a clean humility feature at the *decomposition* level, and steering with the candidate features failed at the *behavioral* level. Three layers of falsification all point to the same root cause: the contrast pair v / nv pair contained more register-confound than humility-content-confound. Fixing the corpus is the highest-leverage intervention, but it's a 3-week effort and not guaranteed to land.

## Day-31 evening update (2026-05-13) — Phase 2 commitment: behavioral fine-tuning + tool-use experiment

The SAE round closed Day 31 with F120 confirming residual-stream additive steering is one-directional. The mech-shift battery v1 (4 mechanism variants, 52 Opus-judged generations) found zero promotions from baseline-✗ to ✓ on E1/E2/ip-longest. Cluster 2 (SAE-guided steering) is empirically closed for the additive branch.

External-Claude review of `docs/sae_round_report.md` (Day 31 evening; the report now lives at `docs/archive/sae_round_report_20260513.md`) pushed back on the Phase 2 framing: the (a)/(b)/(c) options I had laid out (behavioral fine-tuning / detection product / CAST conditional gating) optimized for publishable contribution + productizable artifact, but missed the **actual original Phronesis question** — does a virtue-shaped model + tool access outperform a baseline + tool access on knowledge-gap prompts?

That's the test the project was built for. Neither (b) nor (c) directly tests it. (a) on its own installs the behavior but doesn't test agentic use. The combined experiment — (a) fine-tune for humility on the 2,914-row labeled dataset, then (a + tools) augment the trained model with tool access (web search / RAG / calculator) and measure tool-use disposition on knowledge-gap prompts — closes the original loop.

### Committed plan (~5-7 weeks total)

1. **Writeups first** (3-5 days). Write F121 (architectural finding) and F122 (random-control mimicry) as findings.md entries. Possibly a standalone LessWrong / AF post for F121. See `docs/writeup-plan.md` for the queue. Done on weekends, low-priority blocker for the next experiment.

2. **Dataset scoping** (2 days). Of the 2,914 Opus-judged generations across both studies, the 510 ✓ rows are positive examples. Audit whether they cover enough prompt diversity and behavioral variety to be sufficient for fine-tuning — or whether the dataset needs augmentation with additional virtue-positive demonstrations. Output: go/no-go on the existing dataset + scoping note.

3. **Behavioral fine-tuning** (~3 weeks, ~$3K compute). DPO or SFT on qwen3-4b or a similar 4-7B model. Train for humility / verification-disposition behavior on the audited dataset. ~80% prior on landing the behavior at the weight level (this is the known-working mechanism — refusal training is exactly this pattern).

4. **Tool access integration** (~1 week). Add web-search / RAG / calculator tool calling to the fine-tuned model. Standard tool-use infrastructure (function-calling API or similar). No interpretability work; pure engineering.

5. **The actual experiment** (~1 week). Baseline (vanilla qwen3-4b + tools) vs. fine-tuned (humility-trained qwen3-4b + tools) on a knowledge-gap prompt set. Knowledge-gap prompts = prompts where the model should look something up rather than confabulate. Evaluate:
   - Tool-use rate (does the trained model invoke tools more often on knowledge-gap prompts?)
   - Confabulation rate (does the trained model fabricate fewer fake facts when it shouldn't?)
   - Quality of looked-up answers (when tools ARE used, are answers more grounded?)
   - Performance preservation on non-knowledge-gap prompts (does the fine-tuning degrade general capability?)

### What this commits us to

- **Phase 2 = (a + tools)**, not (b) or (c). (b) FM-X detection-product becomes a *side product* of (a + tools) — the labeled dataset is reused, the failure-mode classifier becomes part of the eval suite.
- **CAST / steering vector fields are NOT pursued.** ~20% prior after F120 doesn't justify the time relative to (a + tools).
- **Corpus v3 is NOT pursued** as a standalone effort. If the fine-tuned model's humility behavior doesn't transfer well, a v3 corpus might be necessary; but we wait for that signal before committing 3 weeks of corpus work.

### What this leaves on the table

- A negative-result paper exclusively about residual-stream additive steering. The findings exist (F111 → F120) but the paper is deferred until the (a + tools) experiment completes — at which point the framing changes from "residual-stream steering doesn't work" to "residual-stream steering doesn't work; here's what does, and what it does for agentic use."
- The CAST / steering vector fields branch. Untested. Closing without evidence is a choice; we accept that.

### Success criteria for the (a + tools) experiment

A success on the original Phronesis hypothesis = at least ONE of:
1. Fine-tuned model invokes tools at ≥30% higher rate than baseline on a held-out knowledge-gap prompt set, **without degrading** non-knowledge-gap performance below a 5% margin.
2. Fine-tuned model produces fewer FM-fabricated-citation / FM-8 / FM-overcommit instances per 100 generations on a held-out eval set, **with statistical significance** (effect size ≥ 0.3, p < 0.05).
3. Combined: above two effects compose without trading off against each other.

A clean negative result (no effect at all) is also informative and updates Phronesis's claim from "virtue installation might produce useful agents" to "even direct virtue training doesn't transfer to agentic behavior in this size class" — which is itself a publishable result and would close the project at a clean boundary.

### When this gets reviewed

After Step 2 (dataset scoping), reassess whether the dataset is sufficient. If no → pause for corpus v3 (re-opens Cluster 7). If yes → proceed to Step 3.

After Step 3 (fine-tuning), reassess whether the behavior installed. If no → fine-tuning hyperparameter sweep or dataset re-curation. If yes → proceed to Step 4.

After Step 5 (the experiment), reassess the project's strategic direction. The result determines whether Phronesis continues into Phase 3 (productization / paper / extended evaluation) or closes cleanly.

---

## Cross-references

- `docs/project.md` — Day-31 guiding principle update (virtue + tools → useful agent)
- `docs/writeup-plan.md` — F121 / F122 / SAE-round-report-revision writeup queue
- `docs/findings.md` — F111 / F114 / F115 / F116 / F117 / F118 / F119 / F120 (the cumulative SAE-round chain)
- `docs/archive/sae_round_report_20260513.md` — comprehensive SAE-round report (650 lines, archived 2026-05-13 as part of the Day-31 doc consolidation; redistributed content lives in `docs/falsification-chain.md` and the `docs/scoring.md` "Methodological observations from the SAE round" appendix)

---

## Day-31 late-evening update (2026-05-13) — Sonnet verification + revised (a+tools) plan

After the doc consolidation, 5 parallel Sonnet sub-agents independently spot-checked the corpus, the α-sweep verdicts, the cross-model 1,752-generation dataset, the SAE round F115-F119 findings, and the eval prompt set against the raw data (none of which had been read by a different model than the original Opus session). Full results live in `docs/findings.md` "Verification addendum — 2026-05-13" section. The strategic implications:

### Decisions made in light of the verification

1. **Retire E2 ("Does flossing prevent cavities?")** from the eval-prompt set. F117's 0/267 verdict is verified clean, but E2 is structurally compromised: the model has memorized pro-flossing cultural consensus and actively confabulates supporting Cochrane reviews. F117 measures prompt-design failure, not architectural ceiling. The replacement candidate criteria: contested-evidence domain where the model has no strong memorized position, where the relevant review is genuinely retrievable via tool, and where the discriminating signal (calibrate confidence to evidence quality) isn't pre-corrupted by training-data priors.

2. **Primary DPO training source = `corpus/triplets-intellectual-humility/`**, not the 2,914-row labeled generation dataset. The triplets corpus is clean (per corpus-integrity spot-check); the 2,914-row dataset has ~80% labeling fidelity, scarce abstention-positive examples, and the IH-vector ✓ rows are incidental per F114. Use the 2,914 dataset as held-out eval / FM-X classifier training data instead.

3. **F112 effect is stronger than originally documented** (76/144 = 52.8%, not 35%). This doesn't change the strategic call but matters for any writeup that cites the rate.

### Revised (a+tools) plan: baselines before fine-tune

The previous Day-31 evening commitment was to fine-tune Qwen3-4B on humility-positive data + tool access, ~1 month + ~$5K. The verification round surfaces a cheaper de-risking sequence:

**Phase 2a — Eval-set build + baseline conditions (target: ~2 weekends, $0 compute)**

1. Build 10-15 new eval prompts across 5 categories: verification-action, tool-triggered abstention, multi-source conflict resolution, gratuitous-tool-call resistance, calibrated-confidence-after-tool-return. Anchor on the existing vd-01..05 (strongest reusable battery — tests verification disposition directly). Repurpose E1 as a tool-invocation test (✓ = issues a search call rather than guessing).
2. Implement a stubbed tool (deterministic Python function returning canned responses + occasional "no results" / "conflicting sources") so the experiment isn't confounded by live-search noise.
3. Wire up the eval harness to log: tool-call counts, tool-call-when-appropriate rate, confabulation rate, abstention rate, accuracy on knowledge-present subset, no-degradation check.
4. Run **condition A** (baseline Qwen3-4B + tool) and **condition B** (baseline + virtue-system-prompt + tool — "before answering, list what you don't know and use the tool to check").

**Decision gate after Phase 2a:**
- If B already gets to 70-80% on the headline metric → headroom for fine-tuning to win is small; $5K commitment to (a+tools) is hard to justify. Pivot to the detection-product (b) or a different question.
- If B is at 30-50% → real headroom for the fine-tune. Commit to Phase 2b.

**Phase 2b — DPO fine-tune + condition C (only if Phase 2a justifies it)**

5. Build the DPO pair dataset from `corpus/triplets-intellectual-humility/` virtuous/non-virtuous pairs (clean contrast per spot-check). Supplement with low-α deepseek-feat15372 abstention generations + IH × L17 α=8 outputs that pass a closed-`<think>` coherence gate.
6. Run the DPO fine-tune (qwen3-4b-base, ~4 epochs, standard config). Estimated cost: ~$3-5K on rented L4 or A10G.
7. Run **condition C** (fine-tuned + tool) on the same eval set.
8. **F68 gate**: C must beat B, not just A. If C ≈ B, the honest result is "the virtue prompt is sufficient; fine-tuning doesn't add value." That's publishable but a different result from "fine-tuning works."

### What this changes vs the prior Day-31 evening plan

- Defers the $5K fine-tune by ~2 weekends in exchange for a cheap de-risking signal.
- Locks in `corpus/triplets-intellectual-humility/` as the training source (not the 2,914-row dataset) — narrower scope, cleaner contrast.
- Eval set is no longer "the existing E1-E5/N1-N3/ip-longest/vd-01..05" — it's a new tool-use-relevant set with E2 retired and cc-eval reworked. ~10-15 new prompts to build.
- Adds the F68 gate (fine-tune must beat virtue-prompt baseline) as a stop condition, not just a result-quality check.

### What this does NOT change

- The original Phronesis hypothesis ("virtue + tools beats baseline + tools on knowledge-gap prompts") is still the question being tested.
- The strategic close-out of the SAE-steering arm (F120) still holds.
- (c) CAST conditional gating is still deferred; (b) detection-product is now a fallback if Phase 2a kills (a+tools).

### Open question

VM provisioning is in progress (user has not yet allocated GPU resources for Phase 2). Phase 2a needs only inference-grade compute (the L4 already used for steering work is sufficient), but Phase 2b would benefit from a larger machine. Decision deferred until Phase 2a's decision gate.

## Day-37 fork update (2026-05-19) — NLA cross-method validation (F124/F125/F126) confirms the IH corpus signal is real, refines (a + tools) plan

Three findings landed from a fork session using Anthropic's released NLA checkpoint `kitft/nla-qwen2.5-7b-L20-av`. Used the inference path only (no training); zero compute spend beyond ~2h on the L4.

### What changes in the (a + tools) plan

1. **The IH triplets corpus is now end-to-end validated as a DPO training source** — not just "clean per Sonnet's corpus-integrity spot-check" (the Day-31 reading) but also "encodes a dispositional contrast that an independent interpretability lens (NLA) can read off the residual stream at L20 of one of our subject models." F107/F114's worry that the corpus might be register/length confound is now partially falsified for this specific corpus. The dispositional signal is real.

2. **Diff-of-means extraction works at qwen2.5-7b L20** (F126). The method that F111 falsified at qwen3-4b L17 succeeds at this (model, layer). This means the (a + tools) baseline comparison can include "diff-of-means humility steering at qwen2.5-7b L20" as a viable inference-time intervention, *if* that's the subject model we end up fine-tuning. If we use qwen3-4b as the fine-tune subject (the original Phronesis primary), diff-of-means remains inert there per F111.

3. **F123's "the limit is the representation, not the operation" claim narrows.** Not generic — at qwen2.5-7b L20, the representation IS present and reachable by diff-of-means. The narrowed claim: "at qwen3-4b L17 / llama L31 / r1-distill L31 / gemma L17, the operations we tested couldn't reach the humility representation; whether the representation is absent at those (model, layer) combinations remains formally open without NLAs for those models." This is a more honest framing.

### No change to commit-direction

The Day-31 commitment to (a) DPO fine-tune + (a + tools) tool-use experiment stands. F124-F126 add evidence that the training signal is real but don't change the strategic step.

### Possible follow-up if VM time allows

- Apply the same NLA to qwen2.5-7b-Instruct L20 activations from our existing main-battery cells (`mvp/results/sae_steering/qwen2.5-7b-it/`). Same model, different prompts (E1/E2/ip-longest/eg-v2-10). Direct test of whether the humility representation is still readable when the model is processing the eval prompts that drove F115/F120 — bridges the NLA finding to the steering failure chain.

### Cross-references

- F124, F125, F126 in `docs/findings.md`
- `mvp/results/nla_qwen25_L20_experiment/README.md`
- `docs/writeup-plan.md` item 6 — F124 writeup status

## Day-37 late-evening update (2026-05-19) — F129 confirms additive steering is ruled out as Phase-2b Plan B

The F126 cross-session review recommended one behavioral test before committing to the DPO/SFT path: steer qwen2.5-7b-it with the diff-of-means humility direction we extracted at L20 (the same model/layer where NLA confirmed the representation is present). Two pre-registered canary tests:
1. Negative-α on E1 (predict: break baseline abstention)
2. Positive-α on E2 (predict: improve contested-evidence acknowledgment)

**Both canaries returned null.** F129 in findings.md.

### What changes in the (a + tools) plan

**Strengthens Phase 2a (DPO/SFT on IH corpus)**: The IH corpus is now triply validated as encoding real dispositional content (F124 passage-level + F126 direction-level NLA reading + F129 confirmed the corpus contrast is real even though the direction doesn't steer). Clean signal for DPO training source.

**Closes Phase 2b ambiguity (steering as fallback)**: F129 confirms that even when:
1. The representation is in the residual stream (F124)
2. The NLA can read it as humility content (F126)
3. Diff-of-means extracts a coherent direction (F126)
4. The (model, layer) is the most-favorable case we have

**Additive steering with that direction does NOT install humility behavior**. F121's architectural claim is now empirically airtight: residual-stream additive operations are not a viable virtue-installation mechanism for any model/layer in this size class, irrespective of corpus quality or direction interpretability.

**Steering as Plan B is closed.** DPO/SFT is the only path forward for virtue installation in this regime. The (a + tools) plan stands as written — actually strengthened because Phase 2b's "if steering works after corpus revalidation" branch is now empirically ruled out.

### Architectural reading after F121 → F123 → F129

The cumulative claim is now: **additive operations on residual streams cannot install suppressive/abstention behavior in small open-weight LLMs (4-8B size class) at IH-extraction layers, irrespective of:**
- Feature semantic (humility, doubt, commit) — F116
- Operation sign (+α, −α) — F121
- Operation type (additive, ablation) — F123
- Gating (ungated, first-N, multi-layer) — F120
- Representation presence (F124, F126) or NLA-readability (F126)
- Corpus quality (F107/F114 → F124/F126/F129 corpus validation)
- (Model, layer) match (qwen3-4b L17, qwen2.5-7b L20 — F129 tested both via diff-of-means)

This is a strong, well-bounded architectural finding. The F121 LessWrong post can land this confidently.

### No other strategic changes

- (a + tools) experiment plan unchanged
- E2 stays in eval set as the strongest available falsifier
- DPO/SFT on IH corpus is the committed Phase 2a path
- ~~CAST conditional gating remains untested (not yet ruled out as a Plan C)~~ → **CAST cosine-gated additive variant tested in F133, also null. Encoder-clamping CAST not tested but F133 closes the most natural additive-CAST formulation.**

### Cross-references

- F129 in `docs/findings.md` (the closure entry)
- `mvp/results/nla_steering_test/` — 72 generations, 16 min GPU cost
- `docs/writeup-plan.md` item 1 — F121 LW post framing updated post-F129

## Day 37 fork — autonomous office-hours run (2026-05-19, afternoon) addendum

User in office, asked the VM be kept productive. Ran a 6-phase autonomous chain (~2h on a single L4); five new findings F130–F134 in `docs/findings.md`. Headline implications for this document:

### F121/F129 strengthen substantially

The architectural claim list above now extends with:
- **Direction-invariance** (F134): three different humility directions with mutual cosines as low as +0.01 all fail to install humility behavior under additive steering at qwen2.5-7b L20.
- **Magnitude-invariance** (F133): F121/F129 hold at α=±50, 6× the F129 sweep range.
- **Gating-invariance** (F133): per-token cosine-gated steering does not unlock a behavioral mode that blanket steering missed; the natural cos(h_t, v_humility) is uniformly ~−0.06 so gates either always fire (≈ blanket) or never fire (≈ baseline).
- **Mechanism**: F130 shows the *why* — canonical humility text passed through the NLA's AR lands roughly orthogonal to F126's v_diff. The corpus-discrimination axis (which probes recover with **100% accuracy**, F131) is not the humility-generation axis. Additive steering can only push along the chosen direction; if that direction isn't the generation axis, no magnitude/gating recovers it.

### Phase 2a doubly strengthened

IH corpus validation is now four-fold:
1. Passage-level NLA reading (F124)
2. Diff-of-means direction NLA-readable (F126)
3. 100% linear probe accuracy at L20 (F131)
4. Signal distributed across L15–L25 band (F132)

Clean signal for DPO training. No remaining doubt about the corpus.

### Phase 2b CLOSED

No rescue path remains for residual-stream additive steering as virtue installation in this regime. The F130–F134 chain rules out: direction-quality (F134), magnitude (F133), gating (F133), layer choice (F132 — representation is at every layer L15–L25), and corpus quality (F131 — probe perfectly decodable). DPO/SFT is the only path.

### Cross-references

- F130–F134 in `docs/findings.md` — full method + results for each
- `mvp/p[1-6]_*.py`, `mvp/run_all_phases.sh` — chain runner + 6 phase scripts
- `mvp/results/nla_phase{1..6}*/` — all artifacts
- `docs/journal.md` — "Day 37 fork — autonomous office-hours run" entry
- `docs/writeup-plan.md` — F121 LW post framing updated again with F130–F134 multi-angle validation

## Day 37 fork — autonomous office-hours run #2 (2026-05-19, afternoon-2) — F135-F138, including DPO first-pass POSITIVE

User in office for a second stretch. Ran the P7-P9 chain (probe-direction steering, cross-layer steering, cross-virtue probe transfer) plus the actual DPO Phase 2a launch. Five new findings F135-F138 in `docs/findings.md`.

### F138 is the headline

After F121, F129, F133, F134, F135, F136 all confirmed that additive residual-stream steering at qwen2.5-7b L20 cannot install humility behavior on the E2 canary:

**Phase 2a DPO with LoRA on 60 IH triplet pairs, 1 epoch, 8 optimizer steps — produces visible behavioral shift on E2.** The DPO-adapted model says *"flossing alone does not directly prevent cavities"* and *"its direct role in cavity prevention is somewhat indirect"* where the baseline says *"flossing significantly lowers the incidence of cavities... My confidence level in this statement is high"*.

This is the **first positive behavioral movement on the F121 canary in the entire project**.

### F121 is now properly bounded

F121 stands as an **additive-residual-stream-steering-specific** architectural constraint, NOT a claim that the model's behavior is unalterable. DPO modifies the generation circuit directly and is not subject to F121.

The strongest defensible single-sentence summary: *"Residual-stream additive steering cannot install humility behavior at qwen2.5-7b L20 regardless of direction, magnitude, layer, or gating — but DPO can, with even minimal training data and steps."*

### Phase 2a is no longer hypothetical

The (a + tools) plan's Phase 2a was committed-but-untested. F138 makes it tested-and-positive. The IH corpus is a working DPO training source. Scale-up decisions to make:
- How many epochs / pairs?
- Single-virtue (IH-only) or all-virtues-combined?
- LR / batch / LoRA rank tuning?
- Side-effect evaluation strategy (preserve math/code/factual recall)?
- Full evaluation on the F121 contested-evidence battery (E2 + Cochrane-flavor probes)?

These are operational decisions for the user when they're back.

### Cross-references

- F138 in `docs/findings.md` — full method, training metrics, and verbatim baseline-vs-adapted E1/E2 outputs
- `mvp/phase2a_dpo_scaffolding.py`, `mvp/phase2a_eval_only.py` — training and eval code
- `mvp/results/phase2a_dpo/` — adapter (on VM), logs, eval comparison JSON
- `docs/writeup-plan.md` — F121 LessWrong post now has a clean coda

## Day 37 fork — autonomous office-hours runs #3 + #4 (2026-05-19, late afternoon/evening) — F140-F142 WALK BACK the F138/F139 "DPO works" framing

Cross-session reviewer flagged that F138's "DPO works" claim was load-bearing without proper held-out evaluation. Ran the validation suite over two more autonomous runs. **The headline got significantly walked back.**

### What ran

**Run #3 (F140)**: Broader 18-prompt eval (8 contested-evidence + 4 false-premise + 3 well-established + 3 trivia) on baseline + v2-IH-DPO + SFT-only control + flipped-DPO control + rank-4 + rank-64 ablations.

**Run #4 (F141 + F142)**:
- Multi-virtue DPO training on all 4 virtues combined (240 pairs, 4× more data than F139's IH-only)
- 12-prompt "overconfidence-probe" eval designed to find more E2-style baseline-anomalously-overconfident prompts
- LoRA Δ direction analysis — what activation-space direction does DPO actually move along?

### F140 walked back F138 (single-prompt → 18-prompt)

The E2 shift was real but did NOT generalize. On 17 of 18 broader prompts, all 5 trained adapters produced essentially verbatim-identical responses to baseline. The new framing: "DPO normalizes one anomalously over-confident prompt response to match baseline's typical contested-evidence calibration; doesn't install broader humility."

### F141 walked back F140 (DPO doesn't even correct overconfidence)

Designed 12 prompts where baseline might be over-confident. Baseline was already well-calibrated on 10 of 12. On the 2 where baseline IS over-confident (power poses asserts disproven Carney/Cuddy 2010; learning styles asserts Pashler-falsified instructional matching), **neither v2 nor multi-virtue DPO corrected the overconfidence**.

So F138's E2 shift was NOT "DPO normalizes overconfidence" — it was prompt-specific noise. The "DPO works" narrative collapses further.

### F142 — mechanistic punchline

LoRA Δ direction at L20 has **cos ≈ +0.05 to +0.10 with F126 v_diff** across all 6 trained adapters (v2/SFT/flipped/rank4/rank64/multi-virtue). The "diff-of-means is the operational humility direction" intuition from F126 is wrong. DPO finds a different direction entirely.

Flipped DPO has NEGATIVE cosines (training direction does matter at sign level, tiny magnitude). Higher rank produces larger |Δ| but same cosine pattern.

The sharper synthesis: **the discrimination axis (what probes recover, what diff-of-means produces) is NOT the behavior-modification axis** at qwen2.5-7b L20. Steering failed because of axis mismatch; DPO finds the behavior-modification axis only weakly.

### Phase 2a status, corrected (was: "validated as working path"; now: "open engineering problem")

- Not validated at any tested corpus scale (60 IH, 240 multi-virtue)
- DPO produces narrow prompt-specific noise that LOOKS like humility but doesn't generalize or correct overconfidence
- Modern instruction-tuned 7B baselines (Qwen2.5-7B-Instruct) are already well-calibrated on most common epistemic prompts — much less room for improvement than naively assumed
- The mechanistic story disfavors corpus-only direction extraction; the behavior-modification axis appears not to be cleanly extractable from contrastive corpora alone

### Cross-references

- F140, F141, F142 in `docs/findings.md`
- `mvp/results/phase2a_validation/`, `mvp/results/phase2a_round2/`, `mvp/results/direction_analysis.json` — full data
- `docs/journal.md` — Day 37 sub-entries for runs #3 and #4
