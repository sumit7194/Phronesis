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

## E4 — Concept provenance via attention (optional; medium bet) · retrospective

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
