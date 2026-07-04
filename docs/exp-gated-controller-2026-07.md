# Experiment: validating the gated epistemic controller — Mac / 4B first

*Started 2026-07-04. Governed by `docs/EXPERIMENTATION_GUIDELINES.md` (the floor). North star: `docs/roadmap-2026-07.md` §8 (gated controller; "calibration is a routing problem"). Read F179 (extraction purity), F182 (measurement discipline), F183 (domain-specific axes) before running.*

## Goal

Validate the **whole method + pipeline** of the gated controller on **Qwen3-4B (Mac, MPS)** — cheaply, power-loss-resiliently, no GPU. Only scale to bigger models / GPU **if** the 4B validation passes. Every step here is extractions + reads + short pilots, not long overnight generation.

## What we already know (constraints from our own data)

- **Within a domain, hedge/commit is ONE signed axis** — cos(v_hedge, v_commit) = −0.93 (CC-4B), −0.88 (CC-32B); *survives* clean extraction (not an artifact). So ± of one direction, not two knobs.
- **Across domains, the same virtue points different ways** — cos(recall-commit, reasoning-commit) = 0.08 at L17. So the library is **domain-specific axes**, size > 1 but < #virtue-words.
- **Extraction *purity* (not dimensionality) is what clean extraction fixed** — content-controlled v_hedge flipped from geographic/format junk to epistemic features and gained selectivity (F179). Purity ≠ independence.
- **Never trust an auto-metric** — F182: hand-read + adversarial re-check every headline before banking.

## Candidate vectors (hypotheses, to be tested — not assumed distinct)

| axis | ± poles | domain | status |
|---|---|---|---|
| recall-confidence | hedge ↔ commit | facts | have (CC-4B), 1 axis |
| reasoning-commitment | deliberate ↔ conclude | reasoning | have candidate (unverified) |
| verification | assert ↔ double-check | reasoning | extract |
| exploration | exploit-path ↔ try-alternative | reasoning | extract |
| empirical-grounding | assert ↔ cite-evidence | claims | older EG work (may re-extract for 4B) |

All extractions use the **content-controlled recipe** (entity/content-free, length-matched, diverse phrasings, mean-pooled over the phrase; F179 discipline).

## Gating menu (what fires the actuator)

| gate | fires on | pilot priority |
|---|---|---|
| token / budget | surface string / count | control baseline only |
| **direction-projection** | residual · axis-vector > τ | **primary** (reuses our vectors, no training) |
| entropy / logprob | next-token entropy collapse | cheap baseline |
| linear probe | trained probe > τ | later (needs labeled data) |
| self-report | "done? (y/n)" mid-gen | later (intrusive; F180 miscalibration) |
| SAE feature | one node > τ | blocked (no 4B SAE; F167 weak) |

## Validation sequence (each gates the next; all Mac/4B)

**S1 — Dimensionality map (cos-matrix).** Extract every candidate axis (content-controlled) → full pairwise cosine matrix. *Purpose:* how many *independent* axes actually exist. *Success:* clear structure — some pairs near ±1 (same axis), some near 0 (independent). *Deliverable:* cos-matrix + which virtues collapse.

**S2 — Signal-trajectory diagnostic.** On 2–3 hand-verified solved traces, compute at every token: projection onto each axis + next-token entropy → plot the trajectory. *Purpose:* does an activation gate even have a signal to fire on? *Success:* ≥1 signal tracks the reasoning state (commit-projection rises near the answer / entropy collapses at "got it" / a visible commit-point before dithering). *Failure here kills gating regardless of method* — fix the vector/signal before building any gate.

**S3 — Gate+vector pilot (1–2 prompts).** Pick the winning {gate, vector} from S1/S2. Apply on a couple of dithering-regime prompts vs controls: **random-gate**, **always-on actuator**, **baseline** (floor: controls mandatory). *Purpose:* does read-then-act beat the trivial alternatives? *Primary metric:* **efficiency** = tokens-at-equal-accuracy (not accuracy — 4B already ceilings on solvable items). *Success:* gated intervention cuts tokens without losing accuracy, and beats random-gate + always-on.

**DECISION GATE:** scale to GPU / bigger models / more prompts **only if** S1 (axes exist), S2 (signal exists), S3 (beats controls) all pass on 4B. Otherwise fix the failing stage first.

## Discipline (non-negotiable, from the floor + our scars)

- Content-controlled extraction, verified (logit-lens / cos-structure) before behavioral use.
- Random-gate + always-on + baseline controls on every S3 claim.
- Hand-read the traces behind every number; auto-metrics are prefilters only.
- Small-n pilots to validate the *pipeline*, then scale — do not trust a pipeline unproven on hand-read examples.

## Status log
- 2026-07-04: doc created; starting S1 (extract verification + exploration axes, build cos-matrix with existing recall/reasoning-commit vectors).
