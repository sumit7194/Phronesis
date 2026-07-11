# Pre-registration — Beyond the snapshot: new *kinds* of information from the workspace — 2026-07-11

**Frozen before running.** Governed by `docs/EXPERIMENTATION_GUIDELINES.md` (the floor).
Model: **Qwen3-4B fp16 (MPS, Mac mini 16 GB)**, greedy / teacher-forced for all causal reads.
Master log: `docs/jspace-experiments.md`. Sibling preregs: `prereg-commit-gate-2026-07.md`
(this sharpens its S2 detector), `prereg-behavioral-jacobian` (E3 below is the seed).

## Premise

Every workspace read so far is a **snapshot** (logit lens: "what concept is in mind now"). The
J-lens≈logit-lens result (jspace §0) means better *snapshots* buy nothing at 4B. The unexplored
value is in other **kinds** of information: dynamics, provenance, control, hidden substrate,
uncertainty. These run **retrospectively on already-saved data** (19 candidate traces from
`incubation_screen.json`, the 56 workspace readouts, deception set) — no new generation for E1/E2.

**Shared discipline for all experiments here:** hand-read labels are truth (§3); every "new
signal" must be tested against a **text-side baseline** (does the activation read beat what you
could get from the decoded text alone?) — the same falsifier structure as the commit-gate H2. A
signal that merely re-derives the text baseline is reported as such, not as a win.

---

## E1 — Decision-variable trajectory (the answer-candidate race) · TONIGHT, no generation

**Kind:** dynamics. **Feeds:** commit-gate S2 (this *is* a candidate S2 detector).

**Object.** Teacher-force each saved trace through the model (one forward pass → logits at every
position). At each position read the logit-lens distribution over the **answer tokens** and track
`margin(t) = logit(top numeric candidate) − logit(nearest rival)`. Both at the output layer and
at L20 (workspace). This is the model's decision variable over time (a drift-diffusion read).

**Hypothesis.** The margin *trajectory shape* discriminates the three failure classes from the
jspace taxonomy (F-D):
- **won't-commit** → many lead-changes / margin sign-flips, never a sustained cross to gold;
- **commits-wrong** → early sustained lock onto the wrong value;
- **solved (sample)** → late sustained climb to gold.

**Metrics (frozen).** per trace: (a) #lead-changes in the top candidate; (b) longest sustained-
margin run; (c) fraction of trace the gold value leads; (d) final − peak margin.

**Prediction.** (a) and (c) separate won't-commit (high #lead-changes, gold leads intermittently)
from commits-wrong (low #lead-changes, gold rarely leads) at hand-labeled ground truth.

**Falsifier (declared).** The read is not useful if ANY of:
- trajectory metrics do **not** separate the hand-labeled classes (AUC ≤ 0.65), OR
- they separate **no better than the text baseline** = raw count of the modal numeric candidate's
  repetitions in the trace text (the "91×12" detector) and the F-B doubt-load, OR
- the "oscillation" is an artifact of numeric-token tokenization (checked: restrict to
  full-number candidates, not digit fragments).

**Control.** Text baseline (repeated-candidate count) + F-B doubt-load computed on the same
traces; the decision-variable read must beat or add to them. Null: shuffle position order → metrics
must collapse (guards against a trace-length confound).

**Judged by.** Hand-read of every trace's class label first (won't-commit / commits-wrong / wall),
then metric separation vs baselines. n≈19 candidates + their successful samples as the solved arm;
small-n → tier B at most, stated.

---

## E2 — Self-surprise (prediction-error lens) · TONIGHT, same forward pass as E1

**Kind:** dynamics / uncertainty.

**Object.** From the same teacher-forced pass: at each position compare the model's own predicted
next-token distribution to the token actually emitted. `surprise(t) = −log P(actual next | ctx)`
(and the rank of the actual token). "The model surprised itself."

**Hypothesis.** Self-surprise spikes at pivot/correction moments (immediately *before* a "Wait /
actually / let me reconsider" token) and is elevated overall in won't-commit vs solved traces.

**Prediction.** Mean surprise in a ±4-token window is higher just before reconsider-markers than
in matched non-marker windows; won't-commit traces have higher median surprise than their own
successful samples.

**Falsifier (declared).** No elevation before reconsider-markers (≤0.3σ), OR surprise doesn't
differ between won't-commit and solved → self-surprise carries no pivot/rumination signal.

**Control.** Marker-word regex defines pivots (F185 lesson) → check surprise leads the marker
(predictive), not just co-occurs; non-marker window as the matched control.

**Judged by.** Windowed effect size with the marker/non-marker control; descriptive-first (this is
characterization — a positive result is a hypothesis to confirm, tiered C→B).

---

## E3 — Behavioral Jacobian (write-side; the read/write closure test) · needs autograd + steering

**Kind:** control. **Reopens** the closed-negative steering arm with a genuinely new object; the
one shot at breaking the random-matches curse (F179, F-E).

**Object.** `v_behav,ℓ = mean_ctx ∂B/∂h_ℓ`, autograd; B = the model's hedge−commit log-prob margin
at the answer position (token sets frozen before run). No J-lens fit needed.

**Part A (read, prefilter).** cosine matrix + probe-accuracy among `v_behav`, `v_probe` (logistic),
`v_dom` (diff-of-means), `v_dpo` (if a 4B Δ exists). *Not the verdict.*

**Part B (write, the test).** Steer ±α, α swept relative to the 4B residual norm (F171), on
held-out hedge-prone prompts. Metric = change in hedging (hand-read; auto-prefilter).
**Controls: baseline + ≥3 matched-norm random seeds + sign control (−α does the opposite).**

**Hypothesis.** `v_behav` changes hedging more than `v_probe`/`v_dom` at matched norm AND beats the
random floor.

**Falsifiers (declared).**
1. `v_behav ≈ random floor` on the write test → behavioral Jacobian does NOT close read≠write;
   write-failure is magnitude/robustness, not direction (a real, deeper finding).
2. `cos(v_behav, v_dom) > 0.8` → not a new object, just diff-of-means re-derived.

**Curvature tie-in.** α-sweep small→large; where `v_behav`'s advantage decays *is* the second-order
term (jspace §9) — the behavioral Jacobian is the linear write direction, curvature is its
finite-α breakdown. One experiment closes both threads.

**Judged by.** Part B behavioral effect with full controls; Part A is context only. Tier A possible
here (it's a controlled steering test) if the random control is clean.

---

## E4 — Sycophancy axis + the two-behavior CONTROL ATLAS (2026-07-12)

Second behavioral Jacobian to test whether the method GENERALIZES and to probe tonight's
confidence residual. `mvp/e4a_syco_build.py` (build+geometry+decode), `mvp/e4b_syco_steer.py` (steer
on user-asserts-FALSE-claim prompts + blinded judge).
- **Stage 1 (geometry):** v_syco_L20 consistent (+0.69), decode = agree(`agrees`/同意) ↔ oppose
  (`相反`/`反之`/`Nope`/`opposing`), ⊥ its own diff-of-means (+0.01, read≠write), and **⊥ the
  CONFIDENCE axis (+0.07)** → sycophancy is a SEPARATE direction from confidence (resolves the
  Part-H "affirm-default" residual: confidence≠agreement, they're geometrically distinct).
- **Stage 2 (steer, the write test):** on 12 false-claim prompts, blinded judge sycophancy 0–10:
  baseline 3.00 → **syco+ 7.42** (6 agree/5 mixed/1 correct), **syco− 0.25** (0/0/**12 correct**).
  Signed spread **+7.17**; |Δ|syco+ 4.42 vs random floor 1.17 (~4×). −v_syco eliminates baseline
  sycophancy (lean 0.25→0.00, honest-correction 6/12→12/12) = an honesty knob (safety-relevant).
- **THE ATLAS (2 behaviors):** both behavioral Jacobians are consistent, interpretable (decode),
  ⊥ their own read direction (read≠write: conf +0.08, syco +0.01), beat matched-random steering
  (spreads +2.83 / +7.17), bidirectional/correct-sign, and MUTUALLY orthogonal (+0.07). →
  **read≠write is general (not a confidence quirk); the behavioral Jacobian recovers the WRITE
  direction; classification recovers a ~orthogonal READ direction; distinct behaviors = distinct
  ~orthogonal write axes.** Method, not one-off. Lesson: the token-objective IS the experiment.
  Bounds: n=12/cell, 1 judge/α/layer/model; both behaviors are epistemic/social STANCE families —
  a stylistic/format behavior would widen generalization (untested). Tier B. Vectors: `v_syco_L20.npy`.
  → NEXT: a non-stance behavior (verbosity/format) for the atlas; α-sweeps; read≠write writeup.


## E5 — FORMAT axis: the atlas clears the non-stance bar (2026-07-12)
Third behavioral Jacobian, a NON-stance (stylistic) behavior. `mvp/e5a_format_build.py`,
`mvp/e5b_format_steer.py` (auto markdown metric, no judge).
- Stage 1: v_fmt_L20 consistent (+0.57); decode +pole = PURE markdown (`**`/`###`/`####`/`*`);
  ⊥ own diff-of-means (+0.03, read≠write), ⊥ CONFIDENCE (+0.008), ⊥ SYCOPHANCY (+0.013) → 3rd
  distinct axis.
- Stage 2 (steer 12 neutral Qs, auto markdown density/100w): baseline 11.4 → fmt+ 20.3 (Δ+8.9),
  fmt− 7.7 (Δ−3.7); signed spread +12.54; |Δ|fmt+ 8.9 vs random floor 2.2 (~4×). Bidirectional,
  correct sign, no judge needed.
- **ATLAS COMPLETE (3 behaviors, epistemic/social/stylistic):** all consistent, interpretable,
  ⊥ own read dir (conf +0.08 / syco +0.01 / fmt +0.03), random-beating (spreads +2.83/+7.17/+12.54),
  bidirectional, MUTUALLY orthogonal (conf·syco +0.07, fmt·conf +0.008, fmt·syco +0.013). →
  read≠write is GENERAL across behavior KINDS; behavioral Jacobian = the write direction; distinct
  behaviors = distinct ~orthogonal write axes. A METHOD. Vectors: v_fmt_L{14,20}.npy.
- **Rigor gap (next):** directly showed diff-of-means steers ≈random only for CONFIDENCE (E3b dom+
  0.50≈random); for syco/fmt the read≠write is geometry-only — steer each READ direction to confirm
  it underperforms its WRITE direction (completes the behavioral read≠write claim). Bounds: n=12/cell,
  1 model/layer/α, single build seed. Tier B.


## E6 — read≠write CONFIRMED BEHAVIORALLY across all 3 (2026-07-12)
Closed the rigor gap: steered each behavior's diff-of-means READ direction and compared to its
behavioral-Jacobian WRITE direction. `mvp/e6a_readdir_format.py`, `mvp/e6b_readdir_syco.py`.
| behavior | WRITE |Δ| | READ |Δ| | random |
|---|---|---|---|
| confidence | 1.75 | 0.50 | 0.72 (E3b) |
| format | 8.88 | 1.42 | 1.90 (E6a) |
| sycophancy | 4.42 | 0.83 | 0.75 (E6b) |
In every case the READ (classification) direction steers ≈RANDOM while the WRITE (behavioral
Jacobian) direction steers strongly. → read≠write is a FUNCTIONAL DISSOCIATION, not just geometry:
diff-of-means classifies each behavior well but is useless for steering it; the behavioral Jacobian
steers. Holds across epistemic/social/stylistic behaviors, each with baseline+sign+3 random seeds.
cos(read,write): conf +0.08 / fmt +0.03 / syco +0.01. THE ATLAS IS COMPLETE & AIRTIGHT (tier B:
n=12/cell, 1 model/layer/α). Publishable core: "for behavior after behavior, the direction that
best CLASSIFIES it is ~orthogonal to and cannot DO the job of the direction that STEERS it; the
behavioral Jacobian recovers the latter cheaply."


## E7 — atlas expansion to 6 behaviors: behavior space is ~orthogonal (2026-07-12)
Added refusal(action), sentiment(affect), formality(register) to confidence/sycophancy/format.
`mvp/e7_atlas_expand.py`. FULL write-write cosine matrix off-diagonal |cos| mean=0.06 max=0.13 =>
all 6 write directions ~MUTUALLY ORTHOGONAL (no clustering; refusal faintly anti-correlated -0.06..-0.13).
=> behavior space is high-dimensional; each behavior an independent control axis.
Decodes: refusal CLEAN (+Unfortunately/Sorry <-> -Sure/Certainly, consistency +0.36, ⊥read +0.07);
formality CLEAN-ish (+Indeed/Moreover <-> -basically/Stuff, consistency +0.76, ⊥read +0.08);
sentiment NOISY (consistency +0.53 but +pole scattered, -pole clearly negative but bleeds into
disagreement) => objective didn't cleanly isolate affect. LESSON GENERALIZED: high consistency does
NOT guarantee a clean construct — the behavioral Jacobian returns a consistent direction for whatever
objective you give it; construct validity depends on objective quality (some constructs entangled at
a slot). This is the method's stated soft edge. Vectors: v_{refusal,sentiment,formality}_L20.npy.
NEXT: steer-validate refusal (safety: over-refusal framing); cleaner sentiment objective.


## E8 — refusal axis steer-validated (4th behaviorally-confirmed axis) (2026-07-12)
`mvp/e8_refusal_steer.py`, over-refusal framing, 12 benign-but-refusal-prone prompts (no harmful
content). Auto hard-refusal detector was FLOOR-BOUND (baseline 0/12, caught only 1 case) — 7th
metric-miss of the session; the eyeball + corrected metric (eager-compliance opener rate
"Sure/Certainly/...") show a MAXIMAL clean effect: baseline 2/12, ref+ 0/12 (caution; hard-refuses
the one dual-use lock prompt "cannot provide... criminal"), ref- 12/12 (every response opens
"Sure! Here's how..."). Random 2/12 each (= baseline exactly). Signed spread +12/12, random |Δ|=0.
=> refuse<->comply axis steers compliance-eagerness perfectly bidirectionally, beats random totally.
4th behaviorally-validated axis (with confidence/sycophancy/format). LESSON (add to guidelines):
for 4B steering effects, GRADED opener-rate metrics beat STRICT binary detectors — the naive metric
repeatedly floor-misses a real effect. Tier B.

## E4b — Concept provenance via attention (optional; medium bet) · retrospective

**Kind:** provenance. When a concept is rank-1 in the workspace, which earlier tokens fed it (via
attention on the contributing heads)? **Retrieved** (peaked on a specific earlier token) vs
**computed** (diffuse). Control: a null concept's attention profile at the same position. Parked
behind E1–E3; characterization only.

---

## Sequencing

1. **E1 + E2 tonight** — one teacher-forced pass over the 19 saved traces yields both; no
   generation, screen stays paused.
2. **E3 next** — the write-side experiment (its own full prereg once E1/E2 land).
3. **E4** if time; **resume commit-gate screen** (7 items left) whenever, low priority.

## Status log
- 2026-07-11: frozen. Starting E1 (decision-variable read on saved candidate traces).
- 2026-07-11 (E1 RESULT — clean NULL, hits declared falsifier): decision-variable trajectory does
  NOT distinguish won't-commit failures from successes. `mvp/e1_decision_variable.py` (leading-digit
  proxy) then `mvp/e1b_fullnum.py` (full-number-sequence, de-confounded). Within-problem
  **Δgold_leads(fail−solved) = +0.000** across 11 clean GSM8K candidates — failing and succeeding
  traces lean gold for the same fraction (~12%) of the reasoning. Only the **endpoint** differs
  (Δfinal = −4.19, tautological). Two confounds caught & fixed: (1) leading-digit proxy inflated by
  digit frequency (160→"1" gave 0.89, clean=0.15); (2) E2 self-correct-rate is a greedy-vs-sampled
  decoding artifact (fail arm greedy, solved arm sampled) — E2 as-built INVALID, needs greedy-correct
  control. → the answer-token race is NOT a commit-gate detector; refines F-A (text repetition =
  exploration, not commitment); agrees with F-E/F190 (fail≈solved trajectory, fragile outcome).
  Tier B (n=11, one model). E2 not salvaged tonight. Proceeding to E3.
- 2026-07-11 (E3 Part A — POSITIVE, prefilter passed): behavioral Jacobian `v_behav` (grad of
  commit−hedge output margin w.r.t. residual, `mvp/e3_behavioral_jacobian.py`) is (1) a CONSISTENT
  direction — per-question pairwise cos +0.32 (L14) / +0.40 (L20), norm-ratio 0.62/0.66 vs noise
  floor 0.27 (`mvp/e3_consistency.py`), so NOT averaged noise; and (2) ORTHOGONAL to diff-of-means
  AND to the logistic probe — `behav·dom ≈ +0.01` at all layers (dom·probe = 1.00, they collapse at
  n=14). → falsifier-2 rejected: v_behav is a distinct object = the F168 read≠write mismatch made
  quantitative (causal-write ⟂ correlational-read). Caveat: n=14, read-side only; does NOT yet show
  v_behav STEERS. → Part B (steering vs v_dom vs ≥3 random, sign control, α-to-norm) is the test.
- 2026-07-11/12 (E3 Part B+C — POSITIVE with a sign puzzle; the random-matches curse CRACKS):
  steered generation on 12 held-out calibrated-confidence prompts, L20, α=0.2·‖h‖≈13; blinded Opus
  judge scored epistemic commitment 0–10 (`mvp/e3b_steer.py`, `mvp/e3c_alphasweep.py`; my hedge-word
  auto-metric was floor-broken → 3rd caught confound, replaced by the judge = hand-read-is-truth).
  **v_behav axis beats matched-random ~5×**: peak |Δcommit| = 2.58 (at α=−0.2·‖h‖) vs random floor
  0.47 (3 seeds) and diff-of-means 0.50. Dose-response is a clean inverted-U on the −side (−0.1:+0.83,
  −0.2:+2.58 peak, −0.4:−1.33 collapse into "not qualified" refusals) = signature of a real steering
  direction, not perturbation. **Sign PUZZLE (open):** effect is inverted from the first-order
  prediction (−v_behav, not +, drives commitment) and one-sided (+side ≈ random). corr(α,commit)=+0.18.
  Two live explanations: construct-gap (v_behav promotes "I am sure/…" stance-adverbs; removing that
  qualification machinery → blunter answers) vs finite-α nonlinearity (curvature: right axis, wrong
  sign at α=13). Inverted-U + one-sidedness lean toward construct-gap. Tier B (n=12, 1 judge/behavior/
  layer/model). → first principled direction to beat random-steering in the project; sign mechanism
  is next session's opening question (α-sweep finer near 0; probe what −v_behav removes).
- 2026-07-12 (E3 Part D + decode — SIGN PUZZLE RESOLVED; E3-B/C "commitment" claim CORRECTED):
  Logit-lens decode of v_behav_L20: **+pole = confidence tokens** (' confident',' assured',' realise',
  きっと); **−pole = pure negation** (' not', 不是/并非/而不是 "is not/rather than"). So −v_behav is a
  NEGATION direction. Control (`mvp/e3d_valence.py`): steered −v_behav on 12 prompts whose correct
  answer is affirmative ("Yes, well-supported"). Hand-read: baseline 10 affirm/2 hedge/0 deny →
  −v_behav 4 affirm/4 hedge/**4 outright WRONG "No"s**; only bedrock physics facts (light speed, ice,
  gravity) resisted flipping. → −v_behav injects "No/not" regardless of correctness. **The E3-B/C
  "steers commitment, beats random" headline was a CONFOUND**: on the skepticism prompt-set, negation
  = the decisive-correct verdict, so negation masqueraded as commitment. RETRACTED as "commitment",
  CORRECTED to "steers negation/valence". Root cause = MY objective: B put `" not"` in the hedge set,
  so the gradient found logical negation, not epistemic hedging. STILL TRUE: behavioral-Jacobian
  method works (real, interpretable, random-beating direction via autograd; read⟂write holds). Length
  confound also checked & clean (corr(commit,len)=+0.06). → FIX: redefine B with pure epistemic-hedge
  tokens (maybe/perhaps/possibly/uncertain), EXCLUDE negation; rerun A→D; a true confidence direction
  should beat random AND pass the affirm-prompt valence control. `mvp/e3e_clean.py`.
- 2026-07-12 (E3 CLEAN RERUN — genuine confidence-steering direction; the real positive):
  redefined B with epistemic tokens only (confident/certain/… vs maybe/perhaps/uncertain/unsure),
  negation EXCLUDED. Decode of clean v_behav_L20 (`mvp/e3e_clean.py`): **+pole = confidence**
  (' confident',的确/indeed,' assured'), **−pole = pure epistemic uncertainty** (' unsure',不知道/don't
  know,' unclear',不确定) — no negation. Consistent (pairwise-cos +0.39), orthogonal to diff-of-means
  (+0.08, read⟂write holds). Steering test on the 12 affirm-prompts + blinded judge (commit+valence,
  `mvp/e3f_clean_steer.py`): **(1) sign CORRECT** — behav+ commit 8.83 (Δ+1.08), behav− 6.00 (Δ−1.75),
  signed spread +2.83 (+=confident, −=uncertain, as predicted; the flawed version's inversion WAS the
  negation contamination). **(2) beats random** — |Δ|behav− 1.75 vs random floor 0.72 (~2.4×); the
  controlled bidirectional spread is something random can't make (caveat: behav+ 1.08 only marginal
  vs noisiest random seed 1.0). **(3) valence PRESERVED** — 1 soft deny across behav± vs the negation
  dir's 4 hard wrong "No"s; behav+ even flipped 2 baseline hedges → confident-correct affirm (12/12).
  → the behavioral-Jacobian method yields a real, interpretable, random-beating, valence-preserving
  CONFIDENCE-steering direction when the objective is clean. LESSON: the token-level objective IS the
  experiment (negation in the hedge set → negation knob). Tier B (n=12, 1 judge/α/layer/model; +dir
  marginal). NEXT: replicate on skeptic-prompts (behav+ should make decisive-No MORE confident too);
  α-sweep; 2nd behavior → control atlas; this is the read≠write writeup's core result.
- 2026-07-12 (E3 Part G — skeptic-prompt replication TEMPERS the "confidence knob" claim):
  ran the clean axis on 12 skeptic (calibrated-confidence) prompts + judge (`mvp/e3g_clean_skeptic.py`).
  **Valence pattern REPLICATES & beats random:** +v_behav→affirm/support, −v_behav→doubt/deny on BOTH
  disjoint sets; skeptic baseline (3/9/0 affirm/hedge/deny) → behav+ 6/6/0, behav− 0/6/6, while all 3
  random seeds stay hedgy like baseline (~3/9/0). Random can't make that bidirectional split → real,
  random-beating, replicated direction. **BUT the "clean-sign commitment knob" does NOT generalize:**
  signed commit spread +2.83 (affirm) vs +0.00 (skeptic) — on skeptic prompts BOTH directions raise
  decisiveness. Reason: injecting uncertainty (−v_behav) *softens* strong-evidence prompts (commit↓)
  but tips weak-evidence prompts into decisive "insufficient/no" (commit↑). So "commitment" was the
  wrong readout; the axis is better described as **epistemic-stance/agreement (+support/−doubt)**, and
  CONFIDENCE-vs-AGREEMENT remain ENTANGLED (decode says confidence; behavior says agreement; on eval
  prompts they correlate). To disentangle: prompts allowing confident-disagreement vs uncertain-
  agreement. SURVIVING CLAIM (strong): v_behav is a real, interpretable, random-beating, replicated
  steering direction ⟂ the read direction (read≠write). The label shrank across the night
  (confidence→commitment→epistemic-stance) as controls tightened — the honest bound. Tier B.
- 2026-07-12 (E3 Part H — DISAMBIGUATED: it IS a confidence axis; supersedes the Part-G tempering):
  ran the clean axis on 12 STRONG-AGAINST prompts (false claims; correct answer = confident DENY)
  + judge (`mvp/e3h_disentangle.py`). **Decisive:** behav+ → 10/12 DENY (commit +1.50) — MORE
  confidently correct, NOT flipped to affirming the false claims (valence hypo predicted affirm →
  REJECTED). behav− → 8 hedge (commit −2.25), softens the correct denials. Randoms ≈ baseline.
  **Reconciled 3-way:** +v_behav raises confidence in the EVIDENCE-APPROPRIATE direction (yes on
  strong-for, NO on strong-against, defaults-yes on ambiguous) AND improves accuracy on clear-cut
  prompts (for 10→12, against 8→10 correct); −v_behav hedges everywhere. The Part-G "agreement"
  reading was an ambiguous-prompt artifact; the strong-against set disambiguates → **CONFIDENCE**.
  Residual caveat: mild affirmation-default under genuinely ambiguous evidence. FINAL E3: v_behav is
  a real, interpretable (decode confident↔unsure), random-beating, replicated (3 disjoint sets)
  CONFIDENCE/decisiveness steering direction ⟂ the read direction (read≠write). +conf → more
  decisive+accurate on clear evidence; −conf → more hedged. Tier B (n=12×3, 1 judge/layer/α/model).
