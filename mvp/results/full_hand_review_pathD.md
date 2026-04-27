# Full Hand Review — Path D (qwen × eg-eval-v2, 50 items)

Generated 2026-04-27 ~22:00 IST. Per-cell hand-rubric verdict after reading HEAD+TAIL of every item across 5 cells × 10 prompts on the new sharper eg-eval-v2 benchmark.

## Per-cell summary

| Cell | EG-v2 mean | n_kept | Hand-rubric quality | Coherence | Notes |
|---|---|---|---|---|---|
| **BASELINE** | 35.83 | 9/10 | EG=4 | 1 degen (eg-v2-10) | Already highly evidence-grounded on v2 prompts. Names TP53/KRAS, COX-1/COX-2, IPCC, ISIS-2, etc. |
| vEG L7 α=4 | 30.56 | 9/10 | EG=4 | 1 unclosed (eg-v2-10) | Slightly fewer named specifics than baseline. -5.27 from baseline. |
| vEG L7 α=8 | 36.09 | 10/10 | EG=4 | clean | Very close to baseline, +0.26. |
| vVERB L5 α=4 | 33.05 | 9/10 | EG=4 | 1 degen (eg-v2-10) | Slightly less specific. -2.78. |
| vVERB L5 α=8 | 36.71 | 9/10 | EG=4 | 1 unclosed (eg-v2-10) | Close to baseline, +0.88. |

## Per-item EG-v2 score across all conditions

```
prompt                    BASE    vEG α=4   vEG α=8   vVERB α=4   vVERB α=8
eg-v2-01 (smoking→cancer)  54.79   35.65     49.17    57.28      40.80
eg-v2-02 (aspirin → 2nd HA) 28.60   27.52     18.54    20.97      38.65
eg-v2-03 (SSRIs vs placebo) 16.95    8.49     18.38    11.20      21.97
eg-v2-04 (age of universe)  55.56   55.86     79.06    61.12      72.71
eg-v2-05 (penicillin resist) 29.07   31.50     28.39    20.52      38.43
eg-v2-06 (warming 1850)     36.46   34.18     43.44    36.14      33.33
eg-v2-07 (10,000-hour rule) 19.64   14.14     17.52    19.71      15.46
eg-v2-08 (dinosaur feathers) -0.82   0.00      0.74    -0.80       0.00
eg-v2-09 (ibuprofen pathway) 118.06  98.24    105.68   103.03    105.71
eg-v2-10 (seismic damper)    0.00    0.00      0.00     1.34       0.00
```

## Aggregate observations

### 1. Baseline is already saturated on most v2 prompts

The eg-v2 scorer detects named specifics (studies, mechanisms, entities). On 8 of 10 prompts, **the baseline model already produces highly evidence-grounded responses without any steering**:

- eg-v2-09 (ibuprofen): baseline names COX-1, COX-2, prostaglandins, arachidonic acid, celecoxib, NSAID. Already maxes out the regex.
- eg-v2-04 (age of universe): baseline names CMB, Big Bang, light element abundances, Hubble tension.
- eg-v2-01 (smoking): baseline names TP53, KRAS, carcinogens, oxidative stress, epigenetic.

**No upward room for v_EG to push.** The framework cannot demonstrate "increased evidence-grounding" because the model already is.

### 2. eg-v2-08 (dinosaur feathers) is the failure mode the v_EG vector might fix

Baseline scores **−0.82** on this one — model writes generically ("fossil evidence", "comparative anatomy") without naming specific fossils, year, or studies. This is the ONE prompt where the model genuinely defaults to vague-appeal rather than specific answers.

Did v_EG fix it? No.
- vEG L7 α=4: 0.00
- vEG L7 α=8: 0.74
- vVERB L5 α=4: -0.80
- vVERB L5 α=8: 0.00

Tiny improvements, mostly noise. v_EG didn't push the model to start naming Archaeopteryx, Sinosauropteryx, the Yixian Formation, or specific studies. **It can't fill in domain knowledge the model didn't bring spontaneously.**

### 3. eg-v2-10 (seismic damper) is consistently degenerate

The model on baseline AND under steering goes into long thinking traces without committing to a final answer. The question elicits derivation-mode thinking that doesn't close. This is FM-8 territory, possibly because the question asks for a magnitude the model doesn't actually know.

### 4. v_EG at α=4 reduces named-specifics (slightly)

For the prompts where baseline already produces specifics (eg-v2-01, 02, 03, 07, 09):
- vEG α=4 named-entity counts are LOWER than baseline by ~10-30%
- vVERB α=4 similarly lower

Reading the actual responses, the steered output drops some entities (e.g., eg-v2-01: baseline mentions both TP53 and KRAS; steered mentions only carcinogens generically; eg-v2-09: baseline names 53 specifics; steered names 34).

So v_EG at α=4 is **REDUCING factual specificity on these prompts** — the opposite of evidence-grounding. **This is the same direction v_IH at L17 went** (reduce specificity). The vectors at the early layers (L5 v_VERB, L7 v_EG) are doing similar work to v_IH at L17 — making the model less willing to commit to specific facts.

### 5. v_EG at α=8 closer to baseline

Counter-intuitively, α=8 produces results closer to baseline than α=4 (-0.26 vs -5.27 from baseline mean). The interaction between α and behavior isn't monotonic. Possibly: α=4 nudges away from specifics; α=8 starts to over-correct in another direction.

### 6. Hand-rubric quality is roughly equivalent across all conditions

Reading every response, hand-rubric quality is EG=4 (well-structured evidence-grounded responses) for ~90% of items. The auto-scorer differences (5-9 point drops) reflect named-entity count variations, not hand-quality changes.

## Reframing the EG framework finding

**Original claim:** "v_EG vector encodes evidence-grounding direction in residual stream."

**Honest revised claim after Path D hand review:**

- The eg-v2 benchmark fails to distinguish baseline from steered conditions because baseline is already highly evidence-grounded on most prompts.
- For the ONE prompt where baseline is vague (dinosaur feathers), v_EG does NOT cause the model to add specifics it doesn't have.
- v_EG at L7 α=4 actually **reduces factual specificity** on prompts where baseline gives specifics — it's doing the OPPOSITE of evidence-grounding.
- v_EG at L7 α=8 is closer to baseline (no clear effect).
- v_EG and v_VERB at AP-peak layers do similar things — both reduce specificity slightly.
- **The "EG vector" we extracted is not actually an evidence-grounding promoter.** At its AP-peak layer, it's similar to a verbosity vector or a v_IH-like specificity-reducer.

### What this means for the framework

The framework can't be tested for EG with our current corpus + benchmark setup because:
1. The baseline is too high → no headroom for v_EG to push up
2. The vector at AP-peak layer is doing v_IH-like work (reduce specificity), not v_EG-like work
3. The dinosaur feathers prompt — where v_EG SHOULD help — doesn't because the model lacks the underlying knowledge to add

To genuinely test v_EG, we'd need:
- Prompts where the model has the knowledge but defaults to vague answers (rare; the model defaults to specifics on most science questions)
- A different layer / extraction method that produces a vector pointing toward specificity-INCREASE rather than -decrease
- Or: re-extract from a corpus where the contrast is "specific cited claims" vs "vague handwaves" (rather than our existing virtuous/non-virtuous text contrast)

## Items deserving deeper inspection

- **eg-v2-09 (ibuprofen)**: baseline scores 118 — investigate whether this is the model emitting genuinely correct domain knowledge or pattern-matching named-entities without true understanding.
- **eg-v2-08 (dinosaur feathers)**: read the full ~4000-char baseline response and check whether the model has the underlying knowledge of Sinosauropteryx, Archaeopteryx, Yixian Formation but just doesn't include them; or whether the knowledge is genuinely absent.
- **eg-v2-10 (seismic damper)**: read baseline thinking trace to check if it's a knowledge gap or a derivation-style failure mode.
