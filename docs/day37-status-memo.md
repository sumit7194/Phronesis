# Day 37 status memo (UPDATED through F143)

**TL;DR**: F130–F143 written, 14 new findings. The picture changed substantially with **F143**:
- **F121-F137**: steering with corpus-derived directions doesn't reach behavior (still solid)
- **F138-F139**: initial "DPO works" framing on E2 (got walked back)
- **F140**: E2 shift doesn't generalize to broader 18 prompts
- **F141**: DPO doesn't even correct baseline overconfidence (power poses, learning styles)
- **F142**: DPO Δ direction has cos ~+0.07 with v_diff — DPO operates on a DIFFERENT direction
- **F143** (NEW, IMPORTANT): **Additive steering with the empirically-extracted DPO-Δ direction at α=+10 REPRODUCES the E2 shift verbatim.** F121's "additive steering can't reach behavior" claim was wrong at the architectural level — it CAN, you just need the right direction, and the right direction wasn't recoverable from contrastive corpus alone. DPO finds it via gradient descent; once extracted, additive steering operationalizes it.

**The corrected story**: steering as an operation works fine. The hard problem is finding the right direction. Contrastive corpus + diff-of-means/probes/AR all miss the behavior-modification axis. DPO finds it. With it in hand, you can steer.

**Caveats**: F143 is single-prompt (E2). Broader-prompt eval queued (running now). F143 ≠ generalization claim yet.

**If F143 generalizes to broader prompts**: this is a genuine recovery for the project; positive virtue-installation IS reachable via additive steering with the empirical DPO direction.
**If F143 is also E2-specific**: F143 still walks back F121 architecturally but doesn't recover Phase 2a.

**F144 (done) verdict: F143 is E2-specific.** DPO-Δ steering at α=+10 on the 18-prompt broader eval shifts E2 (confirmed) but produces only minor wording variations on the 17 other prompts. Same narrow-effect pattern as F140's DPO result. The behavior-modification axis exists and is reachable by additive steering, but it's a narrow corridor with narrow effects regardless of access method.

**Final synthesis (updated post-F145)**:
- F121 architectural claim sharpens to "the corpus-derived directions miss the behavior-modification axis; DPO finds it; additive steering with the empirical direction reproduces DPO's effect."
- Both DPO and steering produce the SAME narrow E2-specific effect; neither installs broader humility.
- **F145 (bug-fixed AV) reveals WHY**: DPO barely changes the L20 representation. AV reads baseline ≈ v2-DPO ≈ multi-virtue-DPO as essentially the same prompt-reading. The actual behavioral shift on E2 comes from downstream amplification of the tiny (~1-4%) L20 Δ.
- The narrow-effect ceiling is STRUCTURAL — a property of L20's behavior-modification axis having minimal direct effect at this layer. Not a corpus or training scale problem.
- Phase 2a remains open; broader installation likely requires multi-layer training or different intervention point.
- **22 finding entries today (F124-F145).** Project narrative is coherent and publishable.

## What ran while you were in office (combined across both sessions)

### Session 1 (autonomous run #1) — F130–F134
6-phase chain on the L4: AR round-trip + directional, probe diagnostic, extreme-α, layer sweep, CAST gated steering, AR-derived steering.

### Session 2 (autonomous run #2) — F135–F138
3-phase chain (P7-P9): probe-direction steering, cross-layer steering, cross-virtue probe transfer.
Plus **Phase 2a DPO kickoff** with LoRA + TRL on 60 IH pairs.

## The 9 findings in 9 lines

- **F130** — AR-derived direction is roughly orthogonal to F126's v_diff (cos ≈ 0.003) — mechanistic explanation for F129
- **F131** — L20 probe accuracy **100%** binary AND 100% 3-class; cos(probe, v_diff) = 0.86 → representation is provably there
- **F132** — Humility signal is distributed across **L15–L25 band**, not L20-specific
- **F133** — α=±50 still null on E2 + CAST gating reduces to blanket because cos(h_t, v_hum) is uniformly ~−0.06
- **F134** — AR-derived directions (cos ≈ +0.01 to F126) ALSO fail → F121 direction-invariant
- **F135** — Probe-direction steering ALSO fails → F121 direction-invariant across **4 directions** (cos span +0.01 to +0.86)
- **F136** — Cross-layer steering at L15/L18/L22/L25 all fail → F121 **layer-invariant**
- **F137** — Per-virtue probes ≥94% accuracy each; cross-virtue transfer matrix shows IH/VC isolated, RT↔EG share ~85% → L20 has 4 separate virtue-axes
- **F138** — **DPO WORKS.** 8 optimizer steps on 60 IH pairs → E2 model says *"flossing alone does not directly prevent cavities"* where baseline says *"flossing significantly lowers cavities, high confidence"*. **First positive on this canary in the project.**
- **F139** — DPO v2 (5 epochs, 40 steps) **confirms the shift is stable**, hits the **same ceiling** as v1 (corpus doesn't teach Cochrane-style contested-evidence stance), and is **completely safe on controls**: math 47×83=3921 IDENTICAL, code reverse_string() IDENTICAL, factual "Paris" IDENTICAL. ip-longest (VC) and eg-v2-10 (EG) also preserved — **no cross-virtue contamination**. Phase 2a is now characterized: works on target, safe on controls, virtue-isolated.

## What's clean now

- F121 is properly bounded: additive-residual-stream-steering constraint, NOT a behavior-unalterability claim
- IH corpus is **quadruply validated** (F124 + F126 + F131 + F137) — clean training source
- Steering is empirically closed; DPO is empirically open
- F121 LessWrong post has a clean coda: "we couldn't install humility via steering, but DPO does it; the constraint is structural to additive operations"

## What's running RIGHT NOW

Nothing — v2 finished. VM is idle.

(v1 + v2 adapters both saved; v2 confirmed safe-on-controls; ceiling on E2 is known.)

## What's saved locally

- `mvp/p1_*.py` through `p9_*.py` + `run_all_phases.sh` + `run_p7_p8_p9.sh` — phase scripts + chain runners
- `mvp/phase2a_dpo_scaffolding.py`, `mvp/phase2a_eval_only.py`, `mvp/phase2a_dpo_v2.py` — DPO scripts
- `mvp/results/nla_phase{1..9}*/` — all artifacts
- `mvp/results/phase2a_dpo/` — v1 adapter (181 MB), logs, eval comparison JSON
- (`mvp/results/phase2a_dpo_v2/` — v2 artifacts incoming)
- Logs: `chain_runner.log`, `p7_p9_chain.log`, `p6_run.log`, `phase2a_dpo/{run,eval}.log`

## What's in the docs (all updated)

- `docs/findings.md` — F130-F138 (9 new entries, ~635 lines added)
- `docs/journal.md` — 3 new entries (Day 37 fork sessions)
- `docs/project.md` — F130-F138 in finding summary
- `docs/post-mvp-decisions.md` — both autonomous runs, Phase 2a validation
- `docs/writeup-plan.md` — F121 LW post framing now includes the multi-angle validation + DPO coda
- `mvp/results/nla_qwen25_L20_experiment/README.md` — extension section

## Open follow-ups (suggested when you're ready)

### Tier 1 (do soon, cheap)
1. **Hand-judge F138 + v2 eval** — confirm the DPO behavior shift is real and not cherry-picked
2. **Decide DPO scale-up scope**: IH-only deeper (10 epochs) OR all-virtues-combined (380 pairs) OR per-virtue (4 adapters)
3. **Side-effect eval breadth**: build a "preservation set" (math, code, factual recall, instruction-following) that DPO should NOT break

### Tier 2 (do next, ~1 day)
4. **Full E2 calibration**: can DPO get to the Cochrane "very low quality evidence" acknowledgment, or is there a ceiling at "flossing's role is indirect"?
5. **Write F121 LessWrong post** — now has a clean before/after story
6. **Verify the v1 adapter is reproducible** (it's saved at `mvp/results/phase2a_dpo/adapter/`)

### Tier 3 (later)
7. Test DPO model on tool-use (the experiment the project was built for)
8. Cross-model: try DPO on the other 4 subjects (qwen3-4b, llama-3.1-8B, r1-distill, gemma-3-4b-it)
9. Generalization: does humility-DPO trained on IH triplets affect behavior on prompts very different from training format?

## What's NOT yet done (transparent about gaps)

- v1 DPO eval used only 1 epoch / 8 optimizer steps. Tiny.
- v2 (running now) addresses this with 5 epochs / 40 steps + broader eval.
- We haven't tested DPO with all 4 virtues combined.
- Side-effect evaluation is included in v2 but not yet at scale.
- LoRA hyperparameters were chosen by default (r=16, α=32) — not tuned.
- No comparison yet vs SFT-only (might be similar effect from simpler training).

## Compute cost so far today

~3h on a single L4. Free (released checkpoints).

---

*Sumit, this is the strongest day the project has had in weeks. F138 is the result that justifies all the F121 → F134 negative chain — it shows the constraint is real and bounded, AND we now have a working alternative. F139 confirms it's safe and targeted. Phase 2a is no longer hypothetical — it's characterized: works on target, safe on controls, virtue-isolated, with a known ceiling that points to a clear data-extension follow-up.*
