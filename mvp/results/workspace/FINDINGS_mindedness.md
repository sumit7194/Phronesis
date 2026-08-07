# F-G · Shared "mindedness" axis across entity types — CONFIRMED, with a twist (2026-08-07)

Prereg: `docs/prereg-mindedness-geometry.md` (item bank frozen pre-run). Qwen3-4B, 240 prompts,
forward-only. `v_mind(class) = mean(h[MENTAL]) − mean(h[PHYSICAL])` at last prompt token; entity
identity cancels inside the difference. Script: `mvp/mindedness_geometry.py`.

## Controls (all pass)
- **Random floor** |cos| = **0.016** (p95 0.035), 20 pairs.
- **Split-half ceiling** (exemplar-split: dog/octopus vs bee/fish etc) = **0.88–0.93** across the
  mid band → directions are highly reliable and generalize across items. Abort condition (<0.3) clear.
- **Discriminant** (v_mind vs physical-only contrast, same class) = **+0.14 / +0.13 / +0.02 /
  −0.04 / +0.01** → near floor. The shared axis is NOT generic question-type structure.

## H-shared: SUPPORTED (strongly)
Between-class cosine **0.64–0.81** (mid band), i.e. **ratio-to-ceiling 0.69–0.90**, against a
0.016 floor. A single mindedness axis substantially spans self / human / animal / nature / object.
**Kim et al. 2607.28607's geometric premise holds at 4B, verified read-only by an independent
method (no steering, no ablation).**

## H-graded: FALSIFIED — and the failure is the interesting part
Predicted self/human/animal tight, object the outlier. **Observed the reverse: SELF is the outlier.**
At best-reliability layer L9: nature|object **0.973**, animal|object 0.956, animal|nature 0.950,
human|animal 0.900 — the non-self entities are nearly interchangeable — while
self|nature **0.685**, self|object 0.728, self|animal 0.738, self|human 0.855.
→ the model's mindedness-about-itself is its most distinct variant, and its nearest neighbour is
*human*. Note this makes the paper's entanglement result *more* striking, not less: even the
least-aligned member of the family still shares ~70–86% of the axis, so suppressing self plausibly
drags the rest.

## New (unpredicted): the shared axis DIFFERENTIATES WITH DEPTH
ratio-to-ceiling L12 **0.90** → L16 0.85 → L20 0.81 → L24 0.72 → L28 **0.69**.
Early/mid layers treat "does X have a mind?" almost identically regardless of X; entity-specific
mindedness separates later. (Ceiling stays flat ~0.89–0.92, so this is real differentiation, not
decaying reliability.)

## Workspace readout (frozen concept list, best rank in band)
`mind` ≈ 69–104 for every class; nulls (`piano`) 1762–2200 → tracked concepts genuinely elevated.
**Self is the only class where `sentient` (#36) outranks `mind`, and the only one with `conscious`
in its top-6 (#372)** — converges with the geometry showing self as the distinct variant.

## Tier / caveats
**Tier B.** Single model (4B, instruct-only), 5 classes × 4 exemplars × 12 attributes, one template.
**We CANNOT test the paper's causal claim** (safety tuning *caused* the entanglement) — that needs
base-vs-instruct checkpoints; the paper itself concedes causal mediation is untested.
Prior art: the paper + a large representation-similarity literature → this is **independent
confirmation of a premise**, not a novel discovery. Lit-check "concept entanglement / RSA across
categories" before any writeup.

## Cross-model #1: Qwen3.5-4B (2026-08-07) — shared axis REPLICATES, weaker; self-outlier holds
`mindedness_geometry_Qwen3_5-4B.json`. Same frozen item bank, 240 prompts, 80s. 32 layers,
d_model 2560 (same width → identical random floor 0.016/p95 0.035). Confounded: newer gen **AND**
MoE **AND** hybrid Gated-Delta attention **AND** multimodal — a difference cannot be attributed to
"newer/better" alone.

| | Qwen3-4B (36L, dense) | Qwen3.5-4B (32L, MoE+hybrid) |
|---|---|---|
| random floor | 0.016 | 0.016 (identical) |
| ceiling (best layer) | 0.929 (L9) | 0.905 (L22) |
| between-class @best | ~0.85 | ~0.60 |
| ratio-to-ceiling, shallow→deep | 0.91 → 0.72 | 0.80 → 0.62 |
| self-pairs mean | +0.752 | +0.533 |
| non-self pairs mean | +0.907 | +0.637 |

**Replicates:** (1) shared axis far above floor (0.016) — H-shared holds again; (2) **self is still
the outlier** (self-pairs 0.533 < non-self 0.637; and in Qwen3-4B 0.752 < 0.907); (3) ratio falls
with depth in both → **entity-specific separation with depth replicates**; (4) `nature|object`
is the single tightest pair in BOTH models (0.973 / 0.958) — inanimate entities are near-identical.
**Differs:** the whole structure is **weaker/more differentiated** in Qwen3.5 (between-class ~0.60
vs ~0.85; ratio 0.62–0.80 vs 0.72–0.91), and the peak-reliability layer moves late (L22/32=0.69
depth) vs early (L9/36=0.26). Also **human|object collapses to 0.358** and human decouples from
nature (0.443) — Qwen3.5 distinguishes humans from inanimate things far more sharply.
**Discriminant** stays near floor in both (|.03–.21|), so the axis remains mental-vs-physical
specific, not generic question structure.

**Read:** the newer model has a *less monolithic* mindedness representation — it still has one
broadly shared axis, but pulls humans (and self) away from rocks/rivers more than its predecessor.
Direction of travel is toward finer discrimination. **Cannot attribute to "improvement"** given the
architecture confound; needs the dense cross-family runs (Gemma-3-4B, Phi-4-mini) to separate.
