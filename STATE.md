<!-- STATE.md — the single source of truth. OVERWRITE this each session (do not append).
     findings.md = the archive/notebook; STATE.md = the dashboard. Keep it to one screen.
     Rule: a claim only appears here at the tier its controls have earned (see EXPERIMENTATION_GUIDELINES.md §5). -->

# Phronesis — current state

**Last updated:** 2026-07-06 · **Latest finding:** F190 · **Model in play:** Qwen3-4B (fp16, Apple-Silicon/MPS) · **GPU:** none (GCP quota-blocked)

## Best current claims (by arc)

| Arc | Best claim | Tier | Controls that hold it | Status |
|---|---|---|---|---|
| **Steering** | *Timing beats direction* — always-on steering harms; turn-1-only helps but any matched-norm random turn-1 vector matches v_IH. Legibility ≠ steerability, and it **worsens with scale** (32B → global refuse-knob). | A | multi-seed random, cross-layer, dose-response, SAE decomp (F179) | **CLOSED (negative). PUBLISHED** (Zenodo, old story) |
| **Thinking→recall** | No recall gain from reasoning — null at 4B & 32B, pass@1 *and* pass@k. | A | pass@k + temp sampling (F177) | **CLOSED (null)** |
| **Legibility-law transfer** | No scramble signature anywhere; knowledge boundary partially legible (AUROC ~0.65); read ≠ write (probe dir ≠ diff-of-means dir). | A | cross-corpus, both directions | **CLOSED** |
| **Read-then-act (gate→search)** | Gating on a confidence read then acting **doubles calibrated accuracy** (4B 24→54.5%, 32B 33→59%); fixes *both* calibration halves. The confidence reader is **failure-mode-specific** (F178: entropy reads recall-gaps, goes blind on confident myths; only verbalized P(True) transfers). | A | ungated baseline, per-half analysis, TruthfulQA transfer | **LIVE POSITIVE · UNPUBLISHED** ← strongest result |
| **Reasoning-calibration** (F180–F190) | The 4B is *mostly* well-calibrated on reasoning: **P(True) predicts its own correctness (AUROC 0.75, catches 85% of errors at a <0.5 gate); verbalized confidence is useless (0.52 — F178 replicated in-domain).** Its one real gap = **overconfident boundary errors**, which are **doubly stuck**: P(True) can't detect them (F189) *and* no prompt corrects them (F190, placebo-controlled). | A (n small) | placebo control (F190), pre-registered null (F188), budget-matched random (F186), hand-read every headline | **LIVE · UNPUBLISHED** |

### Reasoning-arc sub-results (all Qwen3-4B, small-n, hand-verified)
- **F182** measurement crisis fixed → true acc ~85% MATH-500 / ~95% GSM8K (was truncation+scoring artifacts). Robust scoring + force-commit now harness defaults.
- **F184–F186** gated-controller: virtue library ~2 axes @ L14 (not L17); the decisiveness direction reads the model's deliberate↔conclude state (+4σ) — but gating it *for efficiency* is **null** on the 4B (it doesn't over-think; answers late).
- **F187–F188** failure taxonomy: rumination (nudge-rescuable, but **rare ~3%** and its trigger is *interpretive-semantic → not harvestable from problem structure*, pre-registered scan **null**), capability-wall, and overconfident-boundary. 
- **F189–F190** the boundary mode is the one that matters — and it resists both detection and prompting.

## Open / next
- **Mac (RUNNING overnight 2026-07-07, prereg'd):** global-workspace replication on Qwen3-4B — Anthropic's J-lens paper (transformer-circuits 2026/workspace) via official `anthropics/jacobian-lens` repo. T0 ignition + T1 stratification + T2 lens fit + T2b swap positive-control + **T3 workspace-loading on the F189 boundary items** (does the correct answer ever enter the workspace on P(True)-blind errors?). Prereg: `docs/prereg-workspace-mac.md`; results land in `mvp/results/workspace/MORNING_SUMMARY.md`.
- **Mac (queued, user-approved, ~1–2h):** self-consistency test — F190 predicts majority-vote-over-samples rescues the *perturbation-sensitive low-confidence* errors but **not** the stable boundary errors. Clean falsifiable follow-up.
- **GPU-blocked:** rumination-rescue on a real over-thinker (R1-Distill-7B); any cross-model / scale claim; whether *training* closes the boundary gap.
- **Consolidation debt:** gate→search + the whole reasoning arc (F180–F190) are unpublished. Draft mini-writeups at earned tier before opening the next thread.

## Publication status
- **Published (Zenodo, CC-BY):** 3 steering writeups ([DOI](https://doi.org/10.5281/zenodo.20591976)) + FM-X dataset ([DOI](https://doi.org/10.5281/zenodo.20592307)) — these tell the **old** steering-negative story.
- **Unpublished:** everything F165+ (gate→search, reasoning-calibration). This is the current writeup debt.

## Pointers
Floor: [docs/EXPERIMENTATION_GUIDELINES.md](docs/EXPERIMENTATION_GUIDELINES.md) · Archive: [docs/findings.md](docs/findings.md) · Retrospective + process lessons: [docs/retrospective-2026-07.md](docs/retrospective-2026-07.md) · Landing: [README.md](README.md)
*Stale (pre-F165, do not trust): `docs/next-session-queue.md`, `docs/future-experiments.md`.*
