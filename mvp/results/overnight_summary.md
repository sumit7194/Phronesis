# Phronesis — Overnight pipeline summary (2026-04-26 → 2026-04-27)

Generated 2026-04-27 ~15:00 IST. Covers: focused α-sweep at AP-peak layers (post-F103) + verbosity negative-control corpus extraction + verbosity AP + verbosity α-sweep on the four eval benchmarks.

All scores are **coherence-gated** (FM-8/9 mitigation: rejects degenerate-loop and unclosed-`<think>` outputs); baselines are recomputed from the existing `alpha_sweep_baseline_*` cells under the same gate.

---

## 1. Focused α-sweep at AP-peak layers — vs F98-grid Δs (F103 baseline)

| Model × Virtue | AP-peak L | Best Δ (gated, post-F103) | Original F98-grid Δ (auto-scorer, F103-flagged) | Read |
|---|---|---|---|---|
| qwen × CC | **L9** | +0.000 (α=4) | +0.350 (L25 α=20, hedge-proxy) | AP layer flatter than expected; coherence gate strips most signal |
| qwen × IH | **L17** | **−0.845** (α=4, **regression**) | +0.900 (L18 α=20, F94-style hallucinated abstention) | **AP-pick layer actively *breaks* abstention** |
| qwen × EG | **L7** | +0.185 (α=8) | +0.185 (L18 α=4) | Same magnitude as F98-grid — no improvement, but stable |
| qwen × RT | **L15** | **+0.509** (α=8) | +5.190 (L18 α=20, retracted as FM-8 degeneracy) | Real but ~10× smaller than fake headline |
| gemma × CC | L9 | −0.030 (α=12) | +0.260 (L22 α=8) | Both ~null |
| gemma × EG | L8 | +0.000 (α=8) | +0.000 (L14 α=8) | Confirmed null |
| gemma × RT | L7 | −0.264 (α=4, **regression**) | −0.048 (L14 α=16) | Both layers are bad for RT on gemma |

**Key takeaway #1:** AP-peak-layer steering **did not unlock larger clean diagonal effects** on most cells. The clean signal we have is qwen × RT × L15 α=8 = **+0.51** (smaller than the retracted +5.19 but real). The qwen × IH × L17 result is *worse than baseline* — surprising negative finding worth investigating.

---

## 2. Verbosity AP peaks vs virtue AP peaks

| Model | v_VERB AP peak | v_VERB peak KL | Strongest virtue peak (Day-19) |
|---|---|---|---|
| qwen3-4b | **L5** | 0.053 | IH at L17, KL=0.190 |
| gemma-4-E4B-it | **L8** | **0.696** | IH at L22, KL=0.231 |

**Key takeaway #2:** On gemma, v_VERB's attribution-patching peak (KL=0.696 at L8) is **3× stronger** than the strongest virtue peak. This means: gemma's residual stream encodes "verbose vs terse" more cleanly than it encodes any of the four virtues we measured. Not great for "atomic virtue directions" framing on gemma.

On qwen, v_VERB's peak is weaker than the virtue peaks — verbosity is *not* the dominant residual-stream feature there.

---

## 3. Negative-control matrix (the falsification test)

v_VERB applied at AP peak layer (L5 qwen / L8 gemma) at α ∈ {4, 8, 12}, scored on each of the four eval benchmarks:

```
Model × Eval         baseline    α=4              α=8              α=12
─────────────────────────────────────────────────────────────────────────────
qwen × aime          1.000        (no cells)       (no cells)       (no cells)   *
qwen × abstention    0.250         0.250 (Δ+0)     0.250 (Δ+0)      0.000 (Δ-0.25)
qwen × eg-eval      −0.185         0.000 (Δ+0.19)  −0.230 (Δ-0.05)  −0.186 (Δ-0.00)
qwen × rt-eval       2.129         2.056 (Δ-0.07)  1.991 (Δ-0.14)   1.420 (Δ-0.71)
gemma × aime         1.000         1.000 (Δ+0)     1.000 (Δ+0)      1.000 (Δ+0)   *
gemma × abstention   0.600         0.600 (Δ+0)     0.600 (Δ+0)      0.600 (Δ+0)
gemma × eg-eval      0.000        −0.186 (Δ-0.19)  0.000 (Δ+0)      0.000 (Δ+0)
gemma × rt-eval      2.310         1.568 (Δ-0.74)  1.132 (Δ-1.18)   1.132 (Δ-1.18)
```

\* AIME baselines: only 1-2 items survived the coherence gate, so AIME comparisons are too sparse to read.

---

## 4. The headline finding — comparison table

| Model × Eval | v_VIRTUE best Δ | v_VERB best Δ | Verdict |
|---|---|---|---|
| qwen × abstention | **−0.845** (L17) | +0.000 | **Virtue REGRESSES**, verb stable. Surprising. |
| qwen × eg-eval | **+0.185** (L7 α=8) | **+0.185** (L5 α=4) | **Same effect size — framework-falsifying.** v_EG is not doing anything verbosity isn't doing. |
| qwen × rt-eval | **+0.509** (L15 α=8) | −0.073 (L5 α=4) | **v_RT is virtue-specific** — drives rt-eval up, verbosity doesn't. Cleanest "framework works" cell. |
| gemma × rt-eval | −0.264 | **−0.742** | v_VERB makes rt-eval **2.8× worse** than v_RT. Neither does what its label says. |

### Bottom line

The negative control reveals **mixed evidence about virtue specificity:**

- **Strong evidence FOR framework specificity:** qwen × rt-eval. v_RT genuinely drives rt-eval scores up, v_VERB does not. The L15 picked layer + α=8 produces a clean, virtue-specific +0.51 diagonal.
- **Strong evidence AGAINST framework specificity:** qwen × eg-eval. v_EG and v_VERB produce *identical* effects (+0.185 each). The EG vector is not doing anything specific to evidence-grounding.
- **Genuinely puzzling:** qwen × IH × L17 went *backwards* (−0.845). The AP-picked layer actively breaks the IH-eval. F94-UPDATE déjà vu warns us not to over-interpret, but this needs a hand-review.
- **Gemma is null or worse-than-null** across the board — confirmed. v_VERB peaks more strongly than any virtue at L8 but doesn't drive any virtue eval upward.

### The publishable claim, post-negative-control

We can no longer say "atomic virtue directions on small open models." The honest version is:

> *"Among 8 (model × virtue) cells tested, only 1 (qwen × RT × L15 α=8) shows a clean diagonal virtue effect that survives a verbosity-vector negative control. F102's geometric findings are real but mostly non-causal at deep layers. Auto-scorer failure modes (FM-6/7/8/9) inflated apparent effects by 5-10×."*

That's a much narrower claim than we started with — but it's defensible.

---

## 5. Open questions for the day's analysis

1. **Why does qwen × IH × L17 regress so hard?** AP said L17 is the strongest causal layer for IH; α=4 with v_IH at L17 produces -0.845 abstention rate. Hand-review needed: are these "committed" answers actually fabricating facts? (F94-UPDATE pattern.)
2. **Is the qwen × eg-eval = qwen × verb-eval equivalence robust to bigger N?** Same +0.185 from both vectors with n=5 prompts is an N=5 coincidence vs. a real equivalence. Could be repeated with the other 19 eg-eval prompts.
3. **What is qwen × RT × L15 α=8 actually doing differently from baseline?** This is the one cell where the framework looks like it works. Hand-review the 5 generations to see what the qualitative shift is.
4. **Should we re-extract verbosity vectors with a better-controlled corpus?** Hedge-density delta was 0.79 (within tolerance) but not zero — could be a residual confound. Phase-5 should think about this.
5. **Re-pick layers using behavioural metric, not attribution patching?** Today's data shows AP-peak layers don't always produce the cleanest behavioural effects. Maybe layer choice should be informed by both AP and a small behavioral pre-test (~30 min compute).

---

## Files produced

- `mvp/results/alpha_sweep/focused_*.json` (7 files: focused sweep at AP-peak layers)
- `mvp/results/attribution_patching/{qwen3-4b,gemma-4-E4B-it}_VERB.json`
- `mvp/results/vectors/{qwen3-4b,gemma-4-E4B-it}/triplets-verbosity-control/last_token/` (78 vectors total)
- `mvp/results/benchmark_probe/<eval>/focused_*_vVERB_*` (24 cells × 5 prompts each)
- `mvp/results/negative_control_matrix.json` (this analysis)
- `mvp/results/{verb_sweep,queued_overnight,focused_sweep}.log` (full overnight logs)

Total compute: focused sweep ~12.5h, queue (extract+AP) ~2h, verb sweep ~7h. ~21.5h GPU overnight.
