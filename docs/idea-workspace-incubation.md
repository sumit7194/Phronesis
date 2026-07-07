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

---

## v2 design (2026-07-07 afternoon, after independent review by a second Claude instance)

The mobile-Claude review independently converged on the v1 design (2×2, contamination-as-
default, meta-instruction condition, α-sweep + random-injection controls, re-attempt readout).
**Preregistered default prediction (two independent instances):** injection contaminates the
distractor output; spontaneous binding does NOT occur; the meta-instruction ("you have an
unsolved problem in the back of your mind; note anything relevant") flips it. Either half
failing that pattern is informative.

**Adopted additions:**
1. **Primary metric = re-attempt solve-rate delta** (problem A re-attempted after the
   distractor block), not distractor-output analysis. Contamination of distractor output is
   the *expected default* per the paper's swap results, not a finding.
2. **Inject the extracted stuck-state code, not hand-picked topic tokens:** read the top-k
   active lens tokens at the stuck point of the model's own failing trace and re-inject that
   sparse code. Empirically derived → removes hand-curation df. (Still token-salience, not a
   compositional problem representation — state this limit in any writeup.)
3. **Substrate rule = missing-MOVE, not missing-knowledge:** candidates are items where
   greedy fails but pass@k succeeds (reachable solution, stuck trajectory). This is exactly
   the F187 rumination family. Missing-fact failures (F175 lesson) cannot be rescued by
   injection and are excluded.

**QC-gate status (n=20 lens, 2026-07-07 14:16):** J-lens ≈ logit lens on Qwen3-4B (multihop
top-10 51/72 vs 52/72; swaps 5/38 vs ~5% random) → **injection arm not yet validated on the
4B**; behavioral 2×2 and read-arm (logit lens suffices at this scale) proceed first. Injection
needs a ~100-prompt lens or a larger model.

**Conditions (per candidate item):** {no-exposure baseline, hint-distractor, matched no-hint
distractor} × {plain, meta-instruction} + (when validated) {stuck-state injection, matched
random injection ×3 seeds} × {hint, no-hint}. Greedy for causal reads; k-sample re-attempts
for solve-rate (§7 battery).

**Hint-catch metrics (pre-declared):** (1) re-attempt solve-rate delta [primary];
(2) workspace co-activation: problem-token loading during the distractor span (logit-lens
read, band L10–28); (3) move-mention in re-attempt trace under a written rubric [hand-read].

**Move taxonomy for distractor pairs** (hint = unrelated-domain problem whose solution
explicitly uses the move; control = same domain/length/difficulty, different move; both
must be 4B-solvable): work-backwards, complementary counting, invariant/parity, substitution/
change-of-variable, symmetry-pairing (Gauss), pigeonhole, extreme-case/bounding.

**Assets:** screening script `mvp/incubation_screen.py` (greedy + k=8 @ T=0.7 on MATH-500 +
GSM8K-hard, raw traces saved, resumable); draft pairs in `mvp/incubation_stimuli_draft.json`
(frozen before any incubation runs).
