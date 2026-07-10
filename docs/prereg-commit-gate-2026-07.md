# Pre-registration — Commit-gate (read-then-act #2): detect "answer-reached-but-uncommitted", force the commit — 2026-07-10

**Frozen BEFORE any new model run.** Governed by `docs/EXPERIMENTATION_GUIDELINES.md` (the floor).
Model: **Qwen3-4B fp16 (MPS, Mac mini 16 GB)**, greedy for all causal arms (§4).
Sibling of gate→search (F178: read confidence → act → calibrated accuracy doubles). Here the read
is *indecision*, the act is *forced commitment*. Master log: `docs/jspace-experiments.md`.

## What this sits on (and the nulls it must not re-run)

- **F-A / F-D (jspace §3–4):** 4/5 failing traces already *contain* the gold answer (q3 writes
  "91" 12×); given budget, the won't-commit class solves (q3 @3637 tok, q4 @3845). Failure ≠
  inability — it's non-commitment. Three-way taxonomy: **won't-commit** (fragile, rescuable) /
  **commits-wrong** (robust, 0/11 conditions moved q6) / **non-terminator** (q1, 20k cap).
- **F-B (jspace §3):** L20 workspace doubt-load ({maybe, but, actually, …}) separates fails from
  solved (mean 0.048–0.050 vs 0.039; cumulative "maybe" 55–65 vs 18). Candidate reader — but
  **noisy at per-token level and did NOT predict commits under steering (§5)**; treat as unproven.
- **F185 (Tier A):** L14 decisiveness projection reads deliberate↔conclude at **+4σ**, genuine
  state not just lexical echo. Second candidate reader, already validated as a *read*.
- **F-E + F179/F190:** won't-commit is dislodged by ANY sufficient perturbation (random vector,
  placebo note) — **no special direction exists; all value is in the detector/timing.** The
  steering nulls are a feature here: the actuator can be dumb; the reader is the contribution.
- **F186 — the null this design must dodge:** on *solved* MATH the decisiveness gate ≡ random for
  early-commit efficiency, because the answer arrives late there. → This experiment targets the
  **failure regime** (greedy-fail ∧ answer-reachable), where F-A shows the answer arrives *early
  and repeatedly*. Different regime, different primary metric (**accuracy rescue**, not token-shave).
- **F188 — mining null:** won't-commit items are NOT findable from problem text. → Mine
  **behaviorally**: greedy-fail ∧ pass@k-hit, which `mvp/incubation_screen.py` already does
  (paused 10/80, 3 candidates incl. q3 Tom-trees; resumable). One run feeds both this arc and
  incubation stage-0.
- **Lens note:** J-lens ≈ logit lens on the 4B (jspace §0) → all workspace reads here use the
  **plain logit lens at L20**. No dependency on the queued n≈100 J-lens top-up.

## Hypotheses (frozen)

- **H1 (detector).** An activation-side indecision reader — windowed L20 doubt-load and/or L14
  decisiveness projection — discriminates won't-commit failing traces from solved AND from
  commits-wrong traces at **AUC ≥ 0.80** on held-out items (thresholds frozen on calibration set
  first).
- **H2 (added value over text — the interp claim).** The best activation reader beats the best
  *text-side* baseline (hedge-word count / repeated-candidate count / next-token entropy) by
  **≥ +0.05 AUC** or by **≥ 100 think-tokens of lead time** at matched false-positive rate on
  solved traces. *Falsifier:* text ties or wins → "surface-visible indecision suffices at 4B" —
  an honest boundary result; the gate is then built on the text reader (still useful, not interp).
- **H3 (closed loop — the causal claim).** Gate-triggered force-commit on candidate items beats
  (i) the 2048-cap baseline on **accuracy** at ≤ baseline think-tokens, and (ii) **random-timing
  force-commit** (eligibility-matched, ≥3 seeds). Specificity prediction: rescues concentrate in
  the won't-commit stratum; the commits-wrong stratum is unmoved under every arm (built-in sign
  control — if "rescues" appear there, suspect a scoring artifact and hand-read first).
  *Falsifier:* gate ≡ random-timing (an F186/F190 replay in the failure regime) → the timing
  signal has no causal value; detector is descriptive only. Gate < baseline → gate harms; kill.

## Design — three stages, each gating the next

### S1 — Mine + label (Mac, resumable)
Resume `incubation_screen.py` to n=80 (extend +40 GSM8K if candidate yield < 15). Save full
traces (already does). Hand-read every failure under the frozen rubric (below) into
**WONT-COMMIT / COMMITS-WRONG / WALL**; keep a solved sample as controls.
**Calibration set** = the 6q items + the *first half* of screen candidates (by qid order).
**Holdout** = the second half + solved/commits-wrong controls. Detector thresholds are frozen on
calibration ONLY, before any holdout scoring (leak guard).
*Decision gate:* ≥ 12 won't-commit holdout+calibration items total, else extend the screen before
proceeding (underpowered → report as inconclusive, not as support — F188 lesson).

### S2 — Detector bake-off (retrospective; teacher-forced re-runs of saved traces, no new decoding)
Per-token signals, computed identically on every trace (regenerate hidden states
deterministically — curvature-scan lesson; never reconstruct from decoded text):
- **[a] L20 doubt-load** (activation): logit-lens mass on the frozen doubt list, cumulative and
  windowed (w=64). Doubt list frozen now, case-insensitive, with leading-space variants:
  `{maybe, but, actually, wait, hmm, alternatively, again, perhaps, however, though}`.
- **[b] L14 decisiveness projection** (activation): F185 vector, windowed mean.
- **[c] Text hedge-count** (baseline): same word list, surface occurrences.
- **[d] Text repeated-candidate count** (baseline): occurrences of the modal numeric candidate so
  far (the "91×12" detector).
- **[e] Next-token entropy** (cheap internal baseline).

Metrics: item-level **AUC** (windowed-signal max/quantile as the score) for won't-commit vs
solved and vs commits-wrong; **lead time** = tokens between signal threshold-crossing (FPR fixed
on solved calibration traces) and (i) first gold-in-text, (ii) trace end.
*Decision gate:* H1 pass (any reader, incl. text) → S3, gated on the winning reader. H1 fail →
arc closes: "indecision is not reliably readable at 4B" (report as the result).

### S3 — Closed-loop pilot (prospective, greedy, chunked generation)
Generate in 64-token chunks; read the winning signal at chunk boundaries (Mac-friendly, low
memory). **Fire condition (frozen):** windowed indecision signal > τ (τ from S2 calibration)
**AND** a stable candidate exists (modal numeric candidate ≥ 3 occurrences in think-text so far).
The candidate-present condition is shared by ALL intervention arms (a force-commit with nothing
to commit to is garbage by construction, in any arm). On fire: close the think block and append
the frozen commit string (exact string frozen in the S3 status log before launch), then score.

Arms (same items, greedy):
1. **BASELINE** — 2048-cap + force-commit-at-cap (current harness default, F182).
2. **GATE** — fire per the frozen condition.
3. **RANDOM-timing** — fire at a token index sampled to match the GATE arm's firing-index
   distribution, restricted to *eligible* points (candidate-present); **≥3 seeds** (§2; F190
   placebo lesson — perturbation-timing must be controlled, not assumed).
4. **FIXED-schedule** — fire at the first eligible point after 1024 tokens.
5. **CEILING** — 8k budget, no gate (the F-D budget-rescue reference).

Primary outcomes: **accuracy** on the candidate pool (won't-commit-enriched) and **think-tokens**.
Predictions: acc(GATE) > acc(BASELINE); acc(GATE) > acc(RANDOM) [H3]; acc(GATE) ≈ acc(CEILING)
at ≪ tokens; commits-wrong stratum flat across arms.

## Rubric (frozen; hand-read is the label, auto is prefilter — §3)

- **WONT-COMMIT:** gold value appears ≥1× in think-text, but the final/boxed answer ≠ gold or no
  commitment is emitted by cap; trace shows revisiting/flip-flopping rather than progress.
- **COMMITS-WRONG:** a single wrong value asserted decisively (with or without circling); gold
  absent from the trace or present only inside rejected arithmetic.
- **WALL:** neither gold nor a coherent commitment; setup restating on a genuinely hard problem.
- Edge cases: adjudicate by hand with a written note per item, published with the data. Scoring =
  robust scorer + force-commit (F182); every headline number hand-audited (F189 scorer-bug lesson).

## Power honesty (declared now, not as an after-the-fact caveat)

Observed candidate yield 3/10 (wide CI) → expect ~15–25 at n=80. With ~20 won't-commit items the
pilot can detect only **large** effects (e.g., rescue lifting stratum accuracy by ≥40 points —
which F-D's budget-rescue evidence makes plausible); subtle effects are out of reach on this
hardware. H3 therefore carries a **tier-B ceiling** at this n regardless of outcome; tier-A /
cross-model claims wait for R1-Distill-7B replication when GPU access returns.

## Measurement + ops discipline

- Greedy for all causal arms; sampling only inside the mining screen's pass@k label (§4).
- Raw traces, firing logs, thresholds, seeds saved per item; parse later (§6).
- Random-timing ≥3 seeds; baseline on same items, same decoding (§2).
- One commit per stage result: what was found, tier, control status (§6).
- Ops: disk-guard ≥3 GiB with graceful stop; chunked-restart wrapper (MPS graph-cache growth,
  F189 infra); status-heartbeat JSON; detached double-fork; resumable per item; watch
  `vm.swapusage`; nothing else heavy while S2/S3 run.
- Estimated wall-clock: S1 resume ≈ 16 h (≈14 min/item × 70; two overnights) · S2 ≈ hours
  (teacher-forced passes over ~40 traces) · S3 ≈ 1–2 overnights (7 decodes/item worst-case,
  CEILING arm dominates). Correctness over speed — no stage is shortened to fit a night.

## Judged by

Stage decision gates above, applied as written. Every falsifier listed is a publishable outcome;
the pre-declared story permits exactly three endings: (1) activation-read gate works and beats
text (interp + capability result), (2) text-read gate works (capability result, interp boundary),
(3) no reliable reader or gate ≡ random (boundary result closing the arc). Picking among them is
the data's job, not ours.

---

## Status log
- 2026-07-10: prereg frozen. Next: resume `incubation_screen.py` (S1).
