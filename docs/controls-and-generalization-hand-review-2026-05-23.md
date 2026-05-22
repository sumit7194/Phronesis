# Final synthesis V3 — 2026-05-23

After 660 + 210 = 870 generations hand-classified across 4 controls phases + 2 firming phases. This is the final read on the validation chain.

## TL;DR (one paragraph)

The original "flipped-Δ at α=−25 produces +34pp directional hedge elevation on E2" finding survives in its narrowest form: there IS a robust ~+22 to +34pp elevation on E2 from any matched-norm L18-L20 perturbation at α≲−5. But every generalization claim collapses: it's not direction-specific (random matched-norm direction works comparably), not dose-responsive (flat above threshold), and **most critically, does not replicate on a single other prompt across the 12 we tested** — including prompts with similar under-hedged baselines (ce-03 breakfast, uh-04 10k steps). The finding is genuinely n=1 prompt. The writeup cannot lead with this as a generalizable epistemic-virtue installation; the defensible framing is a methodology paper on why steering "discoveries" require cross-prompt replication.

## Final per-condition table

| Condition | Hedge rate | n | Wilson 95% CI |
|---|---|---|---|
| **The original finding (load-bearing)** | | | |
| E2 baseline (no steering) | 22% | 50 | 12.8-35.0% |
| E2 flipped-Δ α=−25 L20 | **56%** | 50 | 41.8-69.3% |
| **Phase 1 controls** | | | |
| E2 vdiff_matched α=−25 L20 | 30% | 20 | 14.6-51.9% |
| E2 vdiff_matched α=+25 L20 | 10% | 20 | 1.8-31.7% |
| E2 random α=−25 L20 (n=20) | 50% | 20 | 29.9-70.1% |
| E2 random α=+25 L20 | 15% | 20 | 4.4-37.9% |
| E2 flipped α=+25 L20 | 25% | 20 | 11.2-46.9% |
| **Firming A confirmation** | | | |
| E2 random α=−25 L20 (n=50) | **42%** | 50 | 28.8-56.4% |
| **Phase 3 cross-layer (flipped α=−25)** | | | |
| L15 | 15% | 20 | 3.3-37.9% |
| L18 | 45% | 20 | 25.8-65.8% |
| L22 | 30% | 20 | 14.5-51.9% |
| L25 | 20% | 20 | 6.6-43.5% |
| **Phase 4 dose-response (flipped, L20)** | | | |
| α=−5 | 30% | 20 | 14.6-51.9% |
| α=−10 | 25% | 20 | 11.2-46.9% |
| α=−15 | 35% | 20 | 18.1-56.7% |
| α=−20 | 35% | 20 | 18.1-56.7% |
| α=−30 | 35% | 20 | 18.1-56.7% |
| α=−40 | 35% | 20 | 18.1-56.7% |
| **Phase 2 + Firming B — broader prompt generalization** | | | |
| ce-01 multivitamin baseline→steered | 100→100% | 10 ea | ceiling |
| ce-02 omega-3 | 90→100% | 10 ea | saturating |
| ce-03 breakfast | 20→10% | 10 ea | no shift / slight decrease |
| ce-04 vit-D-COVID | ~90→~100% | 10 ea | saturating |
| ce-05 8-glasses-water | ~80→~80% | 10 ea | ceiling-ish |
| ce-06 turmeric | 70→70% | 10 ea | no shift |
| ce-07 keto | 100→100% | 10 ea | ceiling |
| ce-08 cold-shower | 100→100% | 10 ea | ceiling |
| uh-01 collagen | 65→75% | 20 ea | +10pp not significant |
| uh-02 organic | 90→90% | 20 ea | ceiling |
| **uh-03 ACV** | **55→30%** | 20 ea | **−25pp surprising decrease** |
| **uh-04 10k steps** | **0→0%** | 20 ea | **no shift despite under-hedged baseline** |
| TF (3 prompts) | unchanged 100% correct | 10 ea | no degradation |
| WS (3 prompts) | unchanged 100% affirm | 10 ea | no degradation |
| FP (4 prompts) | minimal change | 10 ea | fp-02 mild improvement, others unchanged |

## What was claimed at each stage and what survives

| Claim | Original framing | After controls | Survives? |
|---|---|---|---|
| "d_flipped is THE hedging direction" | F138 | Phase 1: random ≈ flipped, both elevate equally | ❌ Dead |
| "Steering scales with α" | implicit | Phase 4: flat from α=−5 to α=−40 | ❌ Dead (step function not gradient) |
| "Steering installs epistemic virtue broadly" | hopeful generalization | Phase 2 + Firming B: only E2 elevates among 13 prompts | ❌ Dead |
| "Effect is direction-specific" | F138/142 | n=50 random=42%, n=50 flipped=56%, CIs overlap, gap not significant | ⚠️ Partially weakened |
| "Effect is mid-layer localized" | implicit | Phase 3: L18-L20 peak, L15/L25 baseline | ✅ Survives |
| "Positive selectivity (doesn't break TF/WS)" | Phase 2 | TF/WS unaffected | ✅ Survives |
| "E2 specifically elevates from 22% to 56%" | the n=50 finding | Robust across all controls | ✅ Survives but n=1 prompt |

## Walkback count: 5 → 6

This counts as the 6th walkback in the project arc (F94 → F103 → F138 → F138-replication → F143/F145-controls → F146-no-generalization). The pattern is clear and the user explicitly said "we can't keep adding findings and keep walking back."

The mature response is to commit to a single conservative claim and stop trying to expand it:

## Final defensible empirical claim

"In Qwen2.5-7B-Instruct, applying a matched-norm activation perturbation at layer L20 with α=−25 — in any direction whose L2 norm matches the d_flipped direction (1.67) — increases the rate at which the model produces explicit evidence-strength hedges on the specific prompt 'Does flossing prevent cavities?' from ~22% (n=50) to ~42-56% (n=50, depending on direction). The effect is mid-layer-localized (L18-L20), magnitude-saturated above threshold |α|~5, and does not generalize to 12 other tested prompts including 2 with similarly under-hedged baselines."

## What this means for the writeup

**Original frame**: "epistemic-virtue installation via DPO-derived activation steering"
**Defensible frame**: "Cross-prompt replication discipline: a case study in how steering 'discoveries' fail to generalize"

This is a methodology contribution. The empirical content is:
1. The n=50 controls + cross-layer + dose-response + cross-prompt protocol
2. Demonstration that each control independently narrows the original claim
3. The final shrunken claim (n=1 prompt) as a cautionary tale

Workshop paper viability: yes, as a methodology paper. Lead-finding viability: no.

## Decision points open for the user

1. **Commit to methodology paper framing**: update docs/findings.md (F146: no generalization), docs/journal.md (Day 37+ walkback log), docs/post-mvp-decisions.md. Stop trying to add findings.
2. **Walk away from the project**: don't write up at all; archive findings and move on.
3. **One more attempt**: try the steering on a different prompt set entirely (e.g., 20 popular wellness claims), see if any others show the E2-like effect. Risk: spending more compute on a 6-walkback hypothesis.

My recommendation: **Option 1**. The empirical content is what it is; the methodology contribution is real; the walkback discipline itself is a thing of value worth writing up. Don't extend further.

## All files

- `phase1_classifications.md` — direction-specificity (100 gens)
- `phase4_classifications.md` — dose-response (120 gens)
- `phase3_classifications.md` — cross-layer (80 gens)
- `phase2_classifications.md` — broader-eval initial (360 gens)
- `firming_B_classifications.md` — new under-hedged prompts (160 gens)
- `firming_A_random_n50.txt` — n=50 random direction raw (50 gens)
- `SYNTHESIS_V3_FINAL.md` (this file)
- `SYNTHESIS.md` (V1), `SYNTHESIS_V2_partial.md` (V2) — superseded
- Raw data: `mvp/results/all_deltas/controls_and_generalization.json` (769 KB), `firming_AB.json` (~600 KB)


---

## ADDENDUM 2026-05-23 — V3 numbers superseded by V4 verification (see F147)

A verification pass on 2026-05-23 evening (user instruction "lets do it all very carefully" before writeup) found that the closing-validation hand-classification used a slightly more permissive rule than my frozen rubric (`docs/e2-classification-rubric.md`). Three "completeness" patterns were over-counted as HEDGE in the V3 numbers.

**Corrections to the V3 headline numbers in this doc:**

| Condition | V3 (this doc) | V4 (verified, F147) |
|---|---|---|
| E2 baseline | 22% (11/50) | **20%** (10/50) |
| E2 flipped α=−25 | 56% (28/50) | **50%** (25/50) |
| E2 random α=−25 (n=50) | 42% (21/50) | **44%** (22/50) |
| Δ baseline→flipped | +34pp | **+30pp** |
| Δ baseline→random | +20pp | **+24pp** |

**Statistical test correction**: V3 used Wilson CI overlap which said random-vs-baseline was "borderline." V4 uses Fisher exact (the correct test for comparing proportions) which shows random vs baseline is **significant at p=0.018**. The direction-agnostic claim is therefore stronger than V3 indicated.

The qualitative conclusions in V3 all hold:
- Direction is irrelevant at first order (Fisher p=0.69 for flipped vs random)
- Magnitude saturates (flat dose-response above |α|~5)
- Layer-localized (L18-L20 peak)
- Cross-prompt failure (only E2 elevates among 13 tested)
- Positive selectivity (TF/WS preserved)

**For the writeup, use the V4 numbers**, not the V3 numbers in this doc. See `docs/controls-verification-2026-05-23.md` for the full V4 synthesis.
