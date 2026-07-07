<!-- STATE.md — the single source of truth. OVERWRITE this each session (do not append).
     findings.md = the archive/notebook; STATE.md = the dashboard. Keep it to one screen.
     Rule: a claim only appears here at the tier its controls have earned (see EXPERIMENTATION_GUIDELINES.md §5). -->

# Phronesis — current state

**Last updated:** 2026-07-07 (afternoon) · **Latest finding:** F191 (candidate) · **Model in play:** Qwen3-4B (fp16, Apple-Silicon/MPS) · **GPU:** none (GCP quota-blocked)

## Best current claims (by arc)

| Arc | Best claim | Tier | Controls that hold it | Status |
|---|---|---|---|---|
| **Steering** | *Timing beats direction* — always-on steering harms; turn-1-only helps but any matched-norm random turn-1 vector matches v_IH. Legibility ≠ steerability, and it **worsens with scale** (32B → global refuse-knob). | A | multi-seed random, cross-layer, dose-response, SAE decomp (F179) | **CLOSED (negative). PUBLISHED** (Zenodo, old story) |
| **Thinking→recall** | No recall gain from reasoning — null at 4B & 32B, pass@1 *and* pass@k. | A | pass@k + temp sampling (F177) | **CLOSED (null)** |
| **Legibility-law transfer** | No scramble signature anywhere; knowledge boundary partially legible (AUROC ~0.65); read ≠ write (probe dir ≠ diff-of-means dir). | A | cross-corpus, both directions | **CLOSED** |
| **Read-then-act (gate→search)** | Gating on a confidence read then acting **doubles calibrated accuracy** (4B 24→54.5%, 32B 33→59%); fixes *both* calibration halves. Reader is **failure-mode-specific** (F178). | A | ungated baseline, per-half analysis, TruthfulQA transfer | **LIVE POSITIVE · UNPUBLISHED** ← strongest result |
| **Reasoning-calibration** (F180–F191) | Boundary errors are **triply characterized**: P(True)-blind (F189), prompt-immune (F190, placebo-controlled), and now **concept-present** — **F191: the pivotal wrinkle concept reads out at median rank 1 in the workspace band during the failing trace on 7/7 boundary items (= teacher-forced correct; nulls at 53–104, 0% top-10); one trace *verbalizes* the strict-inequality constraint then violates it.** → the failure is **mis-application of a loaded concept**, not missing awareness. Explains F189/F190 mechanically. | B (F191: n=7, concepts pre-declared in amendment A1) | within-readout null tokens, teacher-forced contrast, pos-controls, errors reproduced 12/12 | **LIVE · UNPUBLISHED** |
| **Workspace replication** (new, 2026-07-07) | **T0 ignition: concept-specific all-or-none commitment at ~L24–33 (⅔ depth, vs paper's ⅓)** — early-layer "snapping" is an artifact only the random-direction control removes. **J-lens adds no readout advantage over logit lens on the 4B at n=20** (multihop QC 51/72 vs 52/72; top-5 acc *worse* in-band; swaps ≈ random) — logit lens already reads mid-layer intermediates (52/72), unlike Claude-scale. Under-fitted vs unnecessary-at-scale **not yet distinguishable** (needs n≈50–100 lens). | T0: A-track · lens claims: B/inconclusive | random-dir mixtures ×2 seeds, alt-words, α-shuffled null; QC gate; no-op + 3-seed random swaps | **LIVE — lens top-up pending** |

### Reasoning-arc sub-results (all Qwen3-4B, small-n, hand-verified)
- **F182** measurement crisis fixed → true acc ~85% MATH-500 / ~95% GSM8K. Robust scoring + force-commit are harness defaults.
- **F184–F186** gated-controller: decisiveness direction reads deliberate↔conclude (+4σ); efficiency-gating null on 4B.
- **F187–F188** taxonomy: rumination (rare ~3%, interpretive trigger, scan null), capability-wall, overconfident-boundary.
- **F189–F191** boundary mode: undetectable, unpromptable, and concept-present → application failure (see table).

## Open / next
- **Mac (RUNNING now):** `mvp/incubation_screen.py` — stage-0 screen for the **workspace-incubation experiment** (user's idea, design v2 in `docs/idea-workspace-incubation.md` after two-Claude convergence). Candidates = greedy-fail ∧ pass@k-hit (F187 rumination family), full traces saved. Then: hand-read moves → frozen hint/control pairs (`mvp/incubation_stimuli_draft.json`) → behavioral 2×2 → read-arm (logit lens suffices at 4B). Injection arm **gated** on a validated lens.
- **Mac (next quiet night):** J-lens top-up to n≈50–100 (dim_batch=4, nothing else heavy running — 2026-07-07 lesson: dim_batch=8 → 10GB swap thrash; fit crawled to n=1 overnight — pure swap thrash, no sleep: the Mac mini never sleeps) → decides "under-fitted vs unnecessary-at-4B" + revalidates swaps → unlocks injection arm.
- **Mac (queued, user-approved):** self-consistency test — F190 predicts majority-vote rescues perturbation-sensitive errors but not boundary errors.
- **GPU-blocked:** R1-Distill-7B rumination-rescue; cross-scale claims; whether training closes the boundary gap; 27B+ J-lens (Neuronpedia hosts Qwen3.6-27B readouts for comparison).
- **Consolidation debt:** gate→search + reasoning arc (F180–F191) + workspace day-1 unpublished. F191 + T0 are writeup-ready sections.

## Publication status
- **Published (Zenodo, CC-BY):** 3 steering writeups ([DOI](https://doi.org/10.5281/zenodo.20591976)) + FM-X dataset ([DOI](https://doi.org/10.5281/zenodo.20592307)) — old steering-negative story.
- **Unpublished:** everything F165+ (gate→search, reasoning-calibration F180–F191, workspace replication). Current writeup debt.

## Pointers
Floor: [docs/EXPERIMENTATION_GUIDELINES.md](docs/EXPERIMENTATION_GUIDELINES.md) · Archive: [docs/findings.md](docs/findings.md) · Workspace prereg+amendment: [docs/prereg-workspace-mac.md](docs/prereg-workspace-mac.md) · Incubation design: [docs/idea-workspace-incubation.md](docs/idea-workspace-incubation.md) · Day results: `mvp/results/workspace/` (`MORNING_SUMMARY.md`, `NOTES_interim.md`) · Retrospective: [docs/retrospective-2026-07.md](docs/retrospective-2026-07.md)
*Stale (pre-F165, do not trust): `docs/next-session-queue.md`, `docs/future-experiments.md`.*
