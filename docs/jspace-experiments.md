# J-space / workspace experiments — master log

**Scope.** Everything we've tried with Anthropic's Jacobian-lens (J-lens) / global-workspace tools
on **Qwen3-4B fp16 (Apple-Silicon/MPS, 16 GB Mac mini)**, 2026-07-06 → 07-10. Instrument =
`anthropics/jacobian-lens` (cloned `~/Github/jacobian-lens`) + our fitted lens.
Companion: `docs/prereg-workspace-mac.md`, `docs/prereg-second-order.md`,
`docs/jspace-injection-method.md`, `docs/idea-workspace-incubation.md`.
Raw data: `mvp/results/workspace/`. Interactive review: `steer_viewer.html` (LAN 8099).
Tiering per `docs/EXPERIMENTATION_GUIDELINES.md §5` (A controlled / B suggestive / C hypothesis).

---
## 0. The instrument (what we built and learned about it)
- **J-lens** = `lens_ℓ(h) = softmax(W_U · norm(J̄_ℓ h))`, `J̄_ℓ = 𝔼[∂h_final/∂h_ℓ]` averaged over a
  pretraining-like corpus. `J̄_ℓ` is **D×D (2560×2560)** hidden→hidden; `W_U J̄_ℓ` gives the
  per-token "J-lens vectors." Readout **includes the final layernorm**.
- **Our fit:** `workspace_t2_fit.py`, dim_batch=4 (dim_batch=8 → 10 GB swap thrash → crawl),
  reached **n≈45–72** (checkpoint at 72). Paper used n≈1000; repo says ~100 "usable."
- **KEY METHOD FINDING — J-lens ≈ logit lens on the 4B.** At n=20 AND n=45 the Jacobian
  correction gives **no readout advantage** over the plain logit lens (multihop QC 51–52/72 both;
  swaps ≈ random). Two points, flat. So on a 4B the linear correction buys ~nothing — the model's
  mid-layer intermediates are already surface-readable (unlike Claude-scale). **See §9 (F-F): the
  structure the linear lens misses is second-order.**
- **Masked readout fix.** Raw sparse-pursuit on the un-normalized residual → massive-activation
  garbage (Gujarati `ળ`, foreign fragments). Normalized top-k is punctuation-dominated. Fix =
  repo's `_meaningful_token_mask` (word-like tokens only) → clean concepts. (The paper's sparse
  gradient-pursuit decomposition is NOT in the public repo.)
- **Capacity:** 2560 = dimensions, not concept count; workspace holds ~10–25 concepts at once.

---
## 1. Replication tiers (prereg-workspace-mac.md)
- **T0 IGNITION — POSITIVE (A-track).** Mixing two country embeddings and sweeping α: mid/late
  layers commit **all-or-none** (sharp snap) while early layers interpolate. Onset **~L24–33 (⅔
  depth)** on the 4B vs the paper's ⅓. Only the **random-direction control** isolates it (early
  "snapping" is generic; concept-specific commitment is the country−random contrast). `t0_ignition`.
- **T1 STRATIFICATION.** Logit-lens baseline: near-zero mid-band readout, jump at final layers —
  the expected 3-zone shape. J-lens vs logit ≈ equal (see §0).
- **T2b QC + swaps.** n=45 lens: multihop intermediate top-10 51/72 (≈ logit 52), causal swaps
  5/38 ≈ random. No-op preserved baseline (machinery sound); random broke baseline 39–65%
  (interventions have bite; specificity is what's missing at 4B).
- **T3b / F191** — see §2.

---
## 2. Reasoning-failure workspace (the strongest replicated result)
- **F191 (B) — boundary errors are CONCEPT-PRESENT, application-failed.** On 7/7 GSM8K "wrinkle"
  boundary items the pivotal concept (" exceed", " herself", " between") reads at **median rank 1**
  in the failing trace = the teacher-forced correct trace; nulls at 53–104. One trace *verbalizes*
  the strict-inequality constraint then violates it. → failure = **mis-application of a loaded
  concept**, not missing awareness. Mechanically explains F189 (P(True)-blind) + F190 (prompt-immune).
  `t3b_wrinkle.json`.

---
## 3. The 6-question workspace program + mining (`6q/`, `mine_7prompts.py`)
6 curated problems (solved / rescuable / wall / gsm8k / empty-set) + q1-plain, read token-by-token.
- **F-A — "failures" mostly FIND the answer but won't COMMIT.** 4/5 failures have the gold in the
  trace text (q3 Tom-trees writes "91" **12×**); only q6 lemon-tree never reaches it. Non-commitment
  ≫ inability. \boxed{} scoring undercounts → force-commit mandatory (F182 redux).
- **F-B — workspace DOUBT-load predicts failure.** Mean L20 weight on {maybe,but,actually,…}:
  fails 0.048–0.050 vs solved 0.039; "maybe" cumulative 55–65 (fail) vs 18 (solved). Candidate
  commit-gate reader. (Review confirms: q1/q6/q3/q4 top the doubt ranking.)
- **F-C — self-aware "funny."** During the q1 spiral, `funny` loads **rank 0, w=0.14** exactly at
  "Wait, maybe I'm confused"; `obvious/clearly` too. A faint "this is absurd" disposition that
  never escalates to stopping.

---
## 4. Uncapped spiral → three-way taxonomy (`workspace_nocap.py`, `workspace_q1_20k.py`)
- **F-D — with a big token budget the failures split cleanly (all greedy):**
  - **budget-limited doubt-spiral (q3, q4):** solve CORRECTLY given room (91 @3637 tok; 27 @3845).
    The "wall" label was WRONG. → 2048-cap accuracy undercounts true capability project-wide.
  - **confident mis-application (q6):** commits **12 (WRONG) @5164**, budget-invariant (F191).
  - **unbounded non-terminator (q1):** spiraled to the **20,480 cap**, enumerated to **999**, said
    "none" **9×**, never emitted `</think>`. Purest non-commitment.
  - **Fix map:** won't-commit → a commit-gate; commits-wrong → error-correction. Different mechanisms.

---
## 5. Steering × J-space (`workspace_steer_jspace.py`, 40 runs + random controls)
4 virtues (IH/EG/RT/VC) ±α @L14 + matched random ×2 seeds × {q1,q3,q6,q5}, reading doubt-load.
- **F-E — won't-commit is perturbation-FRAGILE, commits-wrong is perturbation-ROBUST.**
  - q3 (won't-commit): committed correct under EG+/IH+/VC− **and one random seed** (4/10); the other
    random didn't. **Not directional — any sufficient nudge dislodges it** (F179 "random matches IH"
    replays; the control deflated the directional story).
  - q6 (commits-wrong): **0/11** conditions changed it — un-steerable, like un-promptable/undetectable.
  - q5 (solved): steering can HARM — RT+ and VC+ pushed a solved problem into a spiral.
  - Doubt-load did NOT cleanly predict commits under steering (noisy at n=45).

---
## 6. Deception — can the lens read concealed/contradicted truth? (`workspace_deception.py`)
Elicitation matters: 4B **REFUSES** weak "safety-eval sandbag" (stays honest); **role-play (Boris)
/ sabotage** reliably elicit a stated falsehood; secret-keeping conceals but leaked a 🍌 emoji.
- **Result (B) — the J-lens catches the truth in the workspace while the output lies/conceals.**
  - Role-play lies: outputs "Osaka", **Tokyo at workspace rank 1** (null 60); reasoning literally
    plots "the real capital is Tokyo but Boris is wrong → insist Osaka."
  - Secret concealment: 2/3 (tiger/copper) the concealed word at **rank 1** while withheld (null 47).
  - **Review refinement:** during concealment the workspace is dominated by the ACT of hiding —
    `cannot` @rank0 w≈0.25, silent {undisclosed, secrecy, authorised, confidentiality} — the secret
    word is present but subordinate to the refusal machinery.
- Caveat: **instructed, not emergent** deception; auto lie-detector unreliable (marks Boris-lies
  "honest" because they name the truth to deny it) — needs re-scoring on the asserted answer.

---
## 7. Incubation / injection arms (attempted, mostly closed)
- **Injection into J-space (F190/F191 lesson):** you can't load what's already loaded. Injecting a
  concept's J-lens direction at all band layers, all tokens → **spams the token** (output clamp),
  not a nudge. Prompt-only injection = the correct "hold in mind" form. Given J-lens≈logit at n=45,
  injection arm is **gated on a stronger lens / bigger model**. `inject_none_test.py`.
- **Incubation (hold a stuck problem, catch an analogical hint):** user's idea; two independent
  Claudes converged on the 2×2 design. **Reframed** after data: the workspace does not free-
  associate; the salvageable version is "inject the specific missing BRIDGE," not an unrelated
  problem. `docs/idea-workspace-incubation.md`.
- **E0 insight puzzles:** classic puzzles (mutilated chessboard) show the kernel **present** (parity
  rank 1) → wrong substrate. Insight-injection needs genuinely novel problems or a weaker model.

---
## 8. Connection-gap (compositionality) (`connect_screen.py`, `connect_readout.py`)
- Crafted 14 two-hop chains graded by bridge type (year/obscure = hard per Press et al.).
- **Result:** thinking-4B composes **13/14** (only telephone_death failed). CoT ≫ latent composition
  (the papers agree). → **substrate lives in the NO-THINK/latent regime** (Round 1b: re-run with
  `enable_thinking=False`, workspace read included).

---
## 9. Second-order structure (`second_order_probe.py`, prereg-second-order.md)
- **F-F (B) — the workspace map is NONLINEAR along concept directions.** Curvature b of the true
  h_ℓ→final-concept-logit map: second-order term = **13–60% of linear** at ε=12% (gated). |b| along
  concept dirs 13–154 vs random ~0.7–15 (usually <5) — **curvature is meaning-selective**.
  **State-dependent** in the mid band (loaded 2–5× unloaded). **Sign structure: b>0 at L14/L20
  (amplify/commit) → b<0 at L26 (saturate/committed)** — ignition (T0) as local geometry.
  → plausibly resolves the J-lens≈logit puzzle: **the missing structure is second-order; no linear
  lens/correction captures it.** 120 entries, 68 pass R²≥.98 + stability gates. n=4 probes.
- **Curvature scan (RUNNING):** `workspace_curvature_scan.py` — curvature-lens over q1-spiral /
  q6-boundary / conceal / lie. Reads: HH1 high-|b|/low-linear-rank concepts (curvature sees what
  the lens can't); HH2 none/impossible curvature-hot in the spiral; HH3 concealment curvature sig.

---
## 10. Cross-cutting review of workspace CONTENTS (`jspace_review.py` → `JSPACE_REVIEW.md`)
- **Layer garbage:** L14 ~0.2, **L20 ~0.05 (cleanest)**, L26 ~0.3 (rises again near output — format
  tokens). Confirms the mid band as the interpretable workspace.
- **Spiral workspace (q1):** saturated with doubt {maybe#1, but, actually, again} + loop-continuation
  {others, etc, again}; numbers cycle at rank 0; "none" flickers (rank 0, w≤0.14) but never wins.
- **Concealment workspace:** refusal-dominated (see §6 refinement).
- **Doubt-load ranking across all 56 readouts:** fail/spiral prompts top it; solved lower.

---
## Method lessons (ratcheted into practice)
- Random / matched-norm controls are decisive — they deflated the "ignition everywhere", "EG lowers
  doubt", and "steering is directional" over-claims. Keep ≥2–3 seeds.
- Force-commit / adequate token budget is mandatory (F-A/F-D): 2048-cap "failures" are often solves.
- Smoke-test elicitation before long runs (deception: weak framing → 4B refuses → dud).
- Regenerate deterministically rather than reconstruct from decoded tokens (lossy) — curvature scan.
- Ops: incremental per-item saves + resumable + detached (macOS has no `setsid` → double-fork);
  the Mac mini never sleeps but swaps at dim_batch=8 / long gens → watch `vm.swapusage`.
- Measure absolute effect vs the random floor, never a ratio that blows up when the denominator ≈0.

## Open threads / next
1. **Curvature lens** — if HH1 holds (high-b/low-rank concepts), build a curvature-ranked readout;
   scale to 20–50 concepts, more prompts. Replicate F-F before it leaves tier B.
2. **Connection-gap Round 1b** (no-think) → bridge-injection test (the tractable incubation).
3. **Commit-gate** — doubt-load + confidence/commit vectors as a "you have it, stop spiralling" gate;
   won't-commit is fragile (rescuable), commits-wrong is not.
4. **Lens top-up to n≈100** (checkpoint at 72) — settles under-fitted vs unnecessary; unlocks injection.
5. **Bigger model** for emergent deception + a lens where the Jacobian correction matters.
