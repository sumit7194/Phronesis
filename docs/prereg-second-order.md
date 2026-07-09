# Prereg: second-order structure of the workspace map (2026-07-10)

**Q.** The J-lens is a first-order (linear, averaged) reading of h_l ↦ h_final. What does the
second order add? Measure local curvature of the TRUE map along meaningful vs random directions,
in loaded vs unloaded states — pure forward passes (no dense Hessian).

**Method.** At the last prompt token, perturb h_l by ε·||h||·d̂ (ε ∈ ±{.015,.03,.06,.12,.24}),
full forward, read the concept's TRUE final logit g(ε). Fit g = g0 + aε + ½bε² (+cε³ for regime
check). Directions per (probe, layer): own-concept J-lens dir, other-concept dir (meaningful,
irrelevant), 3 matched-norm randoms. States: concept LOADED (its prompt) vs UNLOADED (another
prompt). Layers 14/20/26. Model Qwen3-4B fp16 MPS; lens n=45 supplies directions only — the
measured object is the true network, so lens weakness does not gate this experiment.

**Quality gates (interpret only entries passing BOTH):**
- quadratic fit R² ≥ 0.98 over |ε| ≤ 0.12;
- second-difference b(ε) stable within 2× between ε=0.06 and ε=0.12.
Report |cubic|/|quad| at ε=0.12 as regime indicator; flag entries > 1 as beyond-quadratic.

**Hypotheses / predictions / falsifiers.**
- **H-mag:** second-order contribution |½bε²|/|aε| at ε=0.12 along own-concept dirs in the band
  is non-negligible (>0.2). Falsifier: <0.05 everywhere → locally linear; second order adds ~nothing
  (clean null; strengthens the "linear lens is complete at 4B" story).
- **H-spec:** |b| along own-concept dir > other-concept dir AND > random mean (same state, layer).
  Falsifier: comparable → curvature is generic to meaningful directions, not concept-specific.
- **H-state:** |b| along the concept dir is larger when the concept is LOADED than UNLOADED.
  Falsifier: comparable → curvature is a property of the direction, not the active state.
- **H-asym (ignition echo, exploratory):** for loaded concepts in the band, curvature is
  asymmetric — |g(−ε) − linear| > |g(+ε) − linear| (pushing AWAY from a committed concept is the
  nonlinear side). Ties to T0 ignition (all-or-none commitment ~L24+).

**Controls:** 3 random seeds matched-norm; other-concept dir; loaded/unloaded contrast; fit gates.
**Probes:** france/Paris, japan/Tokyo, hot/cold, secret/banana (concealment state). n small,
single model → **tier B ceiling**, exploratory; anything strong needs replication on more
prompts before entering STATE.md above tier C.

**Ops:** detached via setsid (survives Claude Code exit); incremental per-(probe,layer) saves;
resumable; status heartbeat results/workspace/second_order/status.json.
