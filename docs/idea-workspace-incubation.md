# Idea: workspace-mediated incubation / analogical insight (user, 2026-07-07 ~3am)

**Origin.** User's proposal during the overnight workspace run: take a problem the model
reliably fails (needs an orthogonal approach), hold/inject it in the J-space while the model
works on unrelated tasks, and test whether a task bearing a vague structural resemblance lets
the model *connect* and solve the stuck problem.

**What this is.** The mechanistic version of **incubation + analogical transfer**
(Gick & Holyoak's radiation/fortress paradigm): insight = stuck problem and hint **co-loaded
in the workspace simultaneously**. Nobody has done the instrumented version; the J-lens makes
it measurable.

**Mechanical correction that shapes the design.** No background processing exists between
prompts; the workspace lives per-forward-pass. And the paper's selectivity results say unneeded
content drops out (capacity ~10–25 concepts). So problem A must be held either
(a) by instruction — the paper's *directed modulation* shows "keep X in mind" measurably holds
X in workspace during unrelated work, with `dual-task.json` in the official repo as the exact
stimulus set (covert task held while copying a carrier sentence; reachability = lens rank ≤5 in
band; interference measured), or (b) by **injection** of A's key-concept lens vector (the
repo's verbal-introspection protocol: unit-normalized lens row × mean residual norm × strength,
added across the band).

**Substrate warning (F190).** Our WRINKLE boundary items are the WRONG stuck-problems — stable
under every content nudge, placebo-controlled. Use insight/trick problems where an *explicit*
hint provably flips the 4B from fail→solve. Curate first; that filter is the existence proof.

**Staged design (each stage cheap, Mac-viable once the lens exists):**
1. **Curate:** (stuck problem, hint-task) pairs; require fail-without / solve-with-explicit-hint
   on the 4B; key concept single-token (J-lens vocab limit).
2. **Behavioral (no lens):** one context: A attempted → "set aside, do these" → B₁..Bₙ (one
   hint-bearing) → re-attempt A. Arms: hint-task vs matched neutral tasks; ± "keep A in the
   back of your mind" instruction. Metric: solve-rate lift.
3. **Read:** during B, J-lens co-loading of A's key concepts. Claim: solve-lift trials show
   co-loading during the hint task *before* any solving text. (This is the novel result.)
4. **Write (user's original):** inject A's concept vector during B at varying strength vs
   **magnitude-matched random injection, ≥3 seeds** (guidelines §2). Does causal loading raise
   the connection rate?

**Risks.** Stimulus curation is the hard part (4B-solvable-with-hint insight problems, single-
token key concepts); capacity competition (dual-task interference is real); multi-token
concepts unrepresentable in J-lens vocabulary.

**Depends on:** tonight's fitted lens (results/workspace/jlens_qwen3-4b.pt) + T2b swap/QC
validating that lens directions are causally load-bearing at 4B. If T2b fails QC, injection
(stage 4) is not interpretable on this lens; stages 1–2 stand alone regardless.
