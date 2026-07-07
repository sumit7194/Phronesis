# Prereg: Global-workspace replication on Qwen3-4B (Mac, overnight, 2026-07-07)

**Context.** Anthropic's "Verbalizable Representations Form a Global Workspace in Language Models"
(transformer-circuits.pub/2026/workspace) + official repo `anthropics/jacobian-lens` (cloned to
`~/Github/jacobian-lens`, installed into `mvp/.venv`). All experiments on **Qwen/Qwen3-4B fp16 on
MPS** (36 layers, d_model=2560, 16 GB machine). Paper models were Claude Sonnet/Haiku/Opus 4.5 —
nothing this small was tested, so *scale itself is a live variable in every tier*.

**Decoding:** greedy everywhere (causal reads, §4 of guidelines). Seeds recorded for all sampling
(stimulus pairing, random controls). Raw per-item arrays saved under `mvp/results/workspace/`.

---

## Tier 0 — Ignition (forward-only; paper Fig. 29)

**H0.1:** Qwen3-4B shows workspace-style "ignition": for input-embedding mixtures
`(1−α)·e_B + α·e_A` of two single-token country names inside carrier sentences, mid/late-layer
representations at the mixed position commit all-or-none to one concept, while early layers
interpolate smoothly.

**Stimuli:** the paper's own `data/experiments/ignition.json` (12 countries, their carrier
templates). 16 seeded country pairs × up to 40 templates × α ∈ {0, 0.05, …, 1}.

**Metrics** (per layer, from residual h(α) at the mixed position):
mixture coordinate `s(α) = (h(α)−h_B)·(h_A−h_B)/|h_A−h_B|²`;
**sharpness** = max discrete |Δs/Δα|; **bimodality** = fraction of α grid with s<0.2 or s>0.8.

**Prediction:** a layer-profile with an identifiable onset: sharpness/bimodality low and flat in
early layers, rising steeply within a contiguous band starting somewhere in L8–L20 (~⅓ depth by
analogy), not merely at the final layers.

**Falsifier:** sharpness grows smoothly/monotonically with depth with no onset (change-point model
no better than linear fit), or snapping present from L0–L4 (tokenizer/embedding artifact), or no
layer band exceeds the α-shuffled null → **no ignition signature at 4B** (a real, reportable scale
result).

**Controls:** (a) `alt_words` non-country mixtures in the same templates (is snapping
category-general or country-specific?); (b) random-vector mixture: e_B mixed toward a norm-matched
random direction (≥2 seeds) — snapping toward *a concept* should not appear for noise;
(c) the repo's `scrambled_pairs`/`idiom_pairs` sets if their construction is clear at runtime.

## Tier 1 — Layer stratification (lens metrics; paper Fig. 27–28)

**H1.1:** the three-zone structure (sensory → workspace → motor) is visible on Qwen3-4B: a
contiguous mid band with elevated readout kurtosis and cross-position persistence, and a late jump
in next-token accuracy.

**Corpus:** wikitext (raw) 128-token chunks, n≈50 held-out chunks.
**Metrics per layer:** (a) lens top-1/top-5 accuracy at predicting the model's own next token;
(b) mean excess kurtosis of lens logits per position; (c) top-1 persistence across positions
(P(top1_p = top1_{p+δ}), δ=1..8) minus position-shuffled null.

Run twice: **logit lens** (use_jacobian=False; cheap, tonight's floor) and **J-lens** (after Tier 2).
**Prediction:** with the J-lens, kurtosis + persistence peak in a contiguous mid band well before
the final layers; the logit lens shows substantially less early/mid structure (the Jacobian
correction is what reveals it — that contrast is the paper's core methods claim).
**Falsifier:** J-lens metrics ≈ logit-lens metrics everywhere, or no mid-band elevation → either no
workspace stratification at 4B or lens under-fitted (disambiguate via Tier-2 QC gate).

## Tier 2 — Fit the J-lens (instrument build + QC gate; not a hypothesis test)

`jlens.fit` on Qwen3-4B, source_layers = every 2nd layer in [4, 33], target = final layer,
wikitext 128-token prompts, per-prompt checkpoint, adaptive prompt count from measured per-prompt
cost with an absolute wall-clock deadline; phase 1 targets n≈30, resumed toward n≤100 if time
remains. **The paper's repo says ~100 prompts is usable and quality saturates quickly; n<30 is a
degraded instrument — every lens-dependent result is capped at tier B and labeled with n.**

**QC gate (must pass before Tiers 2b/3 are interpreted):**
(1) J-lens top-5 accuracy at mid layers (L12–L28) beats logit lens by a clear margin on held-out
chunks; (2) built-in positive control: on `lens-eval-multihop.json` items the unspoken intermediate
(e.g. "Brazil") appears in the J-lens top-10 at some mid-band (layer, position) at a rate clearly
above the logit lens. **If QC fails, Tiers 2b/3 are not interpretable (tier C at most) — report the
QC failure itself.**

## Tier 2b — Causal positive control: lens-coordinate swaps (paper §reasoning, 54–70% on Claude)

**H2b.1:** swapping the intermediate concept's lens direction for a matched replacement flips the
model's answer on two-hop prompts it otherwise answers correctly.

**Protocol** (repo `probe-swap.json`, their README conventions): filter to items the 4B answers
correctly greedy (baseline gate); patch in lens coordinates at every prompt position across the
mid band: `h ← h + V(σ(c)−c)`, `V=[v_s v_t]`, `c=V⁺h`; success = greedy next token equals
`swap_answer`.

**Prediction:** success rate above the random control and nonzero (Claude Haiku got 54%; at 4B we
expect lower; ≥20% of gated items would be a clean positive).
**Falsifier:** swap rate ≈ random-token control rate → lens directions are not causally load-bearing
at 4B (or the lens is under-fitted — read jointly with the QC gate).
**Controls (§2 floor):** (a) magnitude-matched random-token swap, **3 seeds** per item; (b) no-op
(swap applied with σ=identity) must preserve the baseline answer; (c) baseline-gated items only.

## Tier 3 — Workspace loading vs the F189 boundary blindness (the payoff; exploratory, small-n)

**H3.1 (bridges the paper to F189):** overconfident-boundary errors are cases where the *correct*
answer/intermediate never loads into the workspace, while errors P(True) can detect (and correct
solves) show the correct candidate in the workspace at some point. This would give a mechanistic
account of why P(True) is blind exactly there (it reads the workspace, and the workspace never
contains the alternative).

**Items:** the 7 WRINKLE (boundary) + 5 HARD (capability) items from
`results/legibility/boundary_targets.json`, + 12 matched correct items from the same pool. Reuse
saved raw generations where available (§6); regenerate greedy otherwise (same harness as
boundary_rescue.py).

**Metrics** over the reasoning span, mid band: (a) best lens rank of the correct-answer first
token; (b) workspace loading (cos of residual to the token's lens vector) for correct vs produced
answer; (c) same for the key wrong intermediate where identifiable.

**Prediction:** correct-answer hit rate / loading: correct items > HARD ≳ WRINKLE-boundary; in
particular boundary items show *no* correct-answer excursion into the workspace.
**Falsifier:** boundary items load the correct answer as often as correct items do → the workspace
account does **not** explain F189; the blindness lives elsewhere (e.g. in the readout, not the
content).
**Honesty cap:** n=7 boundary items; whatever the direction, this is **tier B at best**, a
hypothesis-shaping result, not a claim.

---

## AMENDMENT A1 (2026-07-07 ~10:00, before any amended-T3 data collected)

**What happened overnight:** Mac slept/swap-thrashed (10 GB swap on the 16 GB machine at
dim_batch=8) → lens fitted on n=1 prompt; QC gate correctly FAILED (J-lens top-10 48/72 vs
logit 52/72; swaps at chance 2/38 vs 4.4% random) → all overnight lens-dependent results are
**inconclusive by prereg**. Fit resumed at dim_batch=4 with a 14:00 deadline; t2b/t3/t1-jlens
re-run against the topped-up lens.

**T3 design flaw found (before any interpretable T3 data):** Qwen3 tokenizes numbers
digit-by-digit → only 3/12 target items have single-token gold answers; also the correct-
comparator pool file had only 3 rows. Original T3 metrics are unmeasurable as designed.

**Amended T3 (T3b):** per WRINKLE item, hand-curated **pivotal wrinkle-concept tokens**
(declared in `mvp/workspace_t3b_stimuli.json` before running), e.g. strict-inequality
("exceed"/"start earning"), include-yourself headcount ("herself"/" 5"), fencepost
("between"/"first"). Within-item contrast: (a) the model's own failing greedy trace vs
(b) a teacher-forced correct solution (hand-written, in the stimuli file). Nulls: 3 random
word tokens + 1 random digit per item.

**Amended H3.1:** wrinkle-concept loading (best lens rank / max cos) is LOW in the model's
failing trace and HIGH under the teacher-forced correct solution of the same item; nulls low
in both. **Falsifier:** concept loads comparably in the failing trace (the model "sees" the
wrinkle in-workspace and still fails → the workspace account of F189 blindness is wrong, at
least in readout form), or fails to load even in the teacher-forced correct text (lens too
weak / concept mis-chosen → inconclusive, check QC first).
**Caps:** hand-curated concepts = researcher degrees of freedom, declared-before-run but
n=7 → tier B ceiling, hypothesis-shaping. HARD items measured too but exploratory only.

## Ops (§8)
Driver `mvp/run_workspace_overnight.sh` under `caffeinate -dims`; stages are separate processes
(MPS memory fully released between); `results/workspace/status.json` heartbeat; disk guard ≥3 GB
free (MPS graph-cache lesson); every long stage checkpoints and resumes; absolute deadline ~07:30
local, after which only checkpoint-saving runs.

## Tiering commitment
T0/T1-logit results: tier A achievable tonight (controls built in). Lens-dependent results
(T1-jlens, T2b, T3): tier B ceiling tonight (single night, n-limited lens, no cross-model check),
explicitly labeled. Nulls with a failed QC gate are *inconclusive*, not negative.
