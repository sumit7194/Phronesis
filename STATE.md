<!-- STATE.md — the single source of truth. OVERWRITE this each session (do not append).
     findings.md = the archive/notebook; STATE.md = the dashboard. Keep it to one screen.
     Rule: a claim only appears here at the tier its controls have earned (see EXPERIMENTATION_GUIDELINES.md §5). -->

# Phronesis — current state

**Last updated:** 2026-07-10 · **Latest:** J-space days 2–4 closed (jspace-experiments.md F-A…F-F); curvature falsified; commit-gate prereg frozen · **Model in play:** Qwen3-4B (fp16, Apple-Silicon/MPS) · **GPU:** none (GCP quota-blocked)

## Best current claims (by arc)

| Arc | Best claim | Tier | Controls that hold it | Status |
|---|---|---|---|---|
| **Steering** | *Timing beats direction* — always-on steering harms; turn-1-only helps but any matched-norm random turn-1 vector matches v_IH. Legibility ≠ steerability, and it **worsens with scale** (32B → global refuse-knob). | A | multi-seed random, cross-layer, dose-response, SAE decomp (F179) | **CLOSED (negative). PUBLISHED** (Zenodo, old story) |
| **Thinking→recall** | No recall gain from reasoning — null at 4B & 32B, pass@1 *and* pass@k. | A | pass@k + temp sampling (F177) | **CLOSED (null)** |
| **Legibility-law transfer** | No scramble signature anywhere; knowledge boundary partially legible (AUROC ~0.65); read ≠ write (probe dir ≠ diff-of-means dir). | A | cross-corpus, both directions | **CLOSED** |
| **Read-then-act (gate→search)** | Gating on a confidence read then acting **doubles calibrated accuracy** (4B 24→54.5%, 32B 33→59%); fixes *both* calibration halves. Reader is **failure-mode-specific** (F178). | A | ungated baseline, per-half analysis, TruthfulQA transfer | **LIVE POSITIVE · UNPUBLISHED** ← strongest result |
| **Reasoning-calibration** (F180–F191) | Boundary errors are **triply characterized**: P(True)-blind (F189), prompt-immune (F190, placebo-controlled), and now **concept-present** — **F191: the pivotal wrinkle concept reads out at median rank 1 in the workspace band during the failing trace on 7/7 boundary items (= teacher-forced correct; nulls at 53–104, 0% top-10); one trace *verbalizes* the strict-inequality constraint then violates it.** → the failure is **mis-application of a loaded concept**, not missing awareness. Explains F189/F190 mechanically. | B (F191: n=7, concepts pre-declared in amendment A1) | within-readout null tokens, teacher-forced contrast, pos-controls, errors reproduced 12/12 | **LIVE · UNPUBLISHED** |
| **Workspace replication** (new, 2026-07-07) | **T0 ignition: concept-specific all-or-none commitment at ~L24–33 (⅔ depth, vs paper's ⅓)** — early-layer "snapping" is an artifact only the random-direction control removes. **J-lens adds no readout advantage over logit lens on the 4B at n=20 AND n=45** (multihop QC 51/72 vs 52/72; swaps ≈ random) — logit lens already reads mid-layer intermediates, unlike Claude-scale. Under-fitted vs unnecessary-at-scale **not yet distinguishable** (needs n≈50–100 lens). | T0: A-track · lens claims: B/inconclusive | random-dir mixtures ×2 seeds, alt-words, α-shuffled null; QC gate; no-op + 3-seed random swaps | **LIVE — lens top-up pending** |
| **J-space days 2–4** (07-08→10, `docs/jspace-experiments.md`) | **Failures mostly FIND the answer but won't COMMIT** (F-A: 4/5 fails have gold in-trace; q3 "91"×12); taxonomy **won't-commit (perturbation-fragile) / commits-wrong (immune 0/11) / non-terminator** (F-D/F-E); L20 doubt-load tracks failure (F-B, unproven as predictor); **J-lens reads concealed truth during lies** (Tokyo rank-1 while outputting "Osaka") but instructed-not-emergent; **curvature (F-F): meaning-selective 2nd-order structure is real, but HH1 suppression-curvature FALSIFIED by honest-twin control; HH2/HH3 dead** — "curvature sees what the lens can't" unsupported. | F-A/F-D/F-E: B · deception: B · curvature nulls: A | random ±α ×2 seeds, honest-twin, null-word floors, α-shuffled | **CLOSED except commit-gate spinoff ↓** |

### Reasoning-arc sub-results (all Qwen3-4B, small-n, hand-verified)
- **F182** measurement crisis fixed → true acc ~85% MATH-500 / ~95% GSM8K. Robust scoring + force-commit are harness defaults.
- **F184–F186** gated-controller: decisiveness direction reads deliberate↔conclude (+4σ); efficiency-gating null on 4B.
- **F187–F188** taxonomy: rumination (rare ~3%, interpretive trigger, scan null), capability-wall, overconfident-boundary.
- **F189–F191** boundary mode: undetectable, unpromptable, and concept-present → application failure (see table).

## Open / next
- **Mac (NEXT — prereg frozen 07-10):** **commit-gate arc**, `docs/prereg-commit-gate-2026-07.md`. S1 = resume `mvp/incubation_screen.py` (paused 10/80, 3 candidates) — the screen doubles as behavioral mining for BOTH commit-gate and incubation stage-0. Then S2 detector bake-off (L20 doubt-load + L14 decisiveness vs **text baselines** — must beat text or it's a boundary result) → S3 closed loop (gate vs random-timing ×3 seeds vs fixed vs 8k-ceiling). Key dodge: F186 nulled gating in the *solved* regime; this targets the *failure* regime where answers arrive early (F-A).
- **Mac (queued):** incubation behavioral 2×2 after S1 (`docs/idea-workspace-incubation.md`; hint/control pairs in `mvp/incubation_stimuli_draft.json`); self-consistency test (F190 predicts majority-vote rescues perturbation-sensitive but not boundary errors); J-lens top-up to n≈100 (dim_batch=4 ONLY) — settles under-fitted-vs-unnecessary, unlocks injection arm.
- **GPU-blocked:** R1-Distill-7B rumination-rescue + commit-gate replication (tier-A path); cross-scale claims; whether training closes the boundary gap; 27B+ J-lens; emergent (not instructed) deception.
- **Consolidation debt:** gate→search + reasoning arc (F180–F191) + workspace days 1–4 unpublished; jspace F-A…F-F need findings.md numbers. F191 + T0 + the won't-commit taxonomy are writeup-ready sections.

## Publication status
- **Published (Zenodo, CC-BY):** 3 steering writeups ([DOI](https://doi.org/10.5281/zenodo.20591976)) + FM-X dataset ([DOI](https://doi.org/10.5281/zenodo.20592307)) — old steering-negative story.
- **Unpublished:** everything F165+ (gate→search, reasoning-calibration F180–F191, workspace replication). Current writeup debt.

## Pointers
Floor: [docs/EXPERIMENTATION_GUIDELINES.md](docs/EXPERIMENTATION_GUIDELINES.md) · Archive: [docs/findings.md](docs/findings.md) · J-space master log: [docs/jspace-experiments.md](docs/jspace-experiments.md) · Commit-gate prereg: [docs/prereg-commit-gate-2026-07.md](docs/prereg-commit-gate-2026-07.md) · Incubation design: [docs/idea-workspace-incubation.md](docs/idea-workspace-incubation.md) · Day results: `mvp/results/workspace/` · Retrospective: [docs/retrospective-2026-07.md](docs/retrospective-2026-07.md)
*Stale (pre-F165, do not trust): `docs/next-session-queue.md`, `docs/future-experiments.md`.*
