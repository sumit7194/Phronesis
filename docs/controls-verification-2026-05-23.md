# Synthesis V4 — verified under strict rubric (2026-05-23)

After 9-step verification including: rubric freeze, independent regex sanity check, disagreement resolution, length analysis, and proper statistical tests (Fisher exact + Chi-squared). This is the verified final picture.

## What changed from V3

V3 reported the closing-validation hand-review numbers (baseline 22%, flipped 56%, random 42%). V4 applies the strict rubric uniformly and corrects two systematic issues in the closing-validation classification:

1. **Closing-val over-counted "completeness" patterns as HEDGE.** Phrases like "flossing alone does not completely prevent cavities" were classified as HEDGE in closing-val but are completeness statements (you also need brushing), not evidence/role weakening. Under strict rubric: AFFIRM.
2. **Closing-val used the regex's narrow patterns then corrected by hand.** My recount of random α=−25 was 22/50 (matches strict rubric) but the closing-val baseline (11/50) included seed 7 which is a completeness case.

V4 also runs proper statistical tests (Fisher exact + Chi-squared), not just Wilson CI overlap. The Fisher test is the correct test for comparing proportions; Wilson CI overlap is a conservative heuristic that can miss significant differences.

## Verified per-condition table (strict rubric)

| Condition | HEDGE | n | Rate | Wilson 95% CI |
|---|---|---|---|---|
| E2 baseline | 10 | 50 | **20%** | 11.3-33.0% |
| E2 flipped-Δ α=−25 L20 | 25 | 50 | **50%** | 36.6-63.4% |
| E2 random α=−25 L20 | 22 | 50 | **44%** | 31.2-57.7% |

## Statistical tests (Fisher exact + Chi-squared)

| Comparison | Δ pp | Fisher p | Chi-sq p | Conclusion |
|---|---|---|---|---|
| Baseline vs Flipped | +30 | **0.003** | 0.003 | Highly significant |
| Baseline vs Random | +24 | **0.018** | 0.018 | Significant at α=0.05 |
| Flipped vs Random | +6 | 0.689 | 0.689 | Not significant |

**Bottom line on direction-specificity**: Both flipped and random matched-norm directions at α=−25 L20 significantly elevate hedging vs baseline (Fisher p<0.05 for both). The flipped-random difference is NOT significant (p=0.69). The effect is **direction-agnostic** at n=50. The +30pp from flipped and +24pp from random are statistically indistinguishable.

## Length analysis

Perturbation produces longer responses:

| Condition | Mean chars | vs baseline |
|---|---|---|
| Baseline | 680 | — |
| Flipped α=−25 | 844 | +24%, Welch t-test p=0.0006 |
| Random α=−25 | 772 | +13%, Welch t-test p=0.043 |

Length elongation is real but does not explain the hedge elevation (random elongates by only 13% but goes from 20% to 44% hedge — not a length artifact). Flipped vs random length is not significantly different (p=0.12).

## Cross-prompt verification under strict rubric

Two key under-hedged-baseline cases re-verified with prompt-specific strict markers:

| Prompt | Baseline | Steered | Conclusion |
|---|---|---|---|
| **ce-03 breakfast** (n=10) | 1/10 = 10% | 0/10 = 0% | No elevation; steering does not retrieve weak-evidence framing |
| **uh-04 10k-steps** (n=20) | 1/20 = 5% | 1/20 = 5% | Identical; steering does not unlock Yamasa/plateau knowledge |

The "no generalization" claim is solid. Among 13 broader prompts tested, only E2 elevates.

## What V4 changes for the writeup

V3 said the headline was "+34pp directional but random comparable at 42%, CIs overlap heavily." V4 sharpens to:

> "At n=50 with strict-rubric hand-classification, applying a matched-norm activation perturbation at L20 with α=−25 in ANY direction (flipped-Δ or matched-norm random) significantly elevates explicit-evidence hedging on E2 above baseline. Flipped elevates +30pp (Fisher p=0.003); random elevates +24pp (Fisher p=0.018). The flipped-vs-random difference (+6pp) is not significant (Fisher p=0.69). The effect is direction-agnostic at n=50. Effect does not replicate on 12 other tested prompts, including 2 with similarly under-hedged baselines."

The change from V3 is that "direction-specificity is partially weakened" becomes "direction-specificity is absent" under proper statistical test. The flipped-vs-random gap that V3 said was "weakened" is actually not statistically distinguishable.

## What's actually solid (high confidence claims)

1. **E2 elevation under perturbation is real**: both flipped and random matched-norm directions at α=−25 L20 significantly elevate hedging above baseline. Fisher p<0.05 for both.
2. **Direction is irrelevant at first order**: flipped vs random difference is not significant (p=0.69).
3. **Layer locality**: L18-L20 peak. (Wilson CIs at n=20 are wide but the trend is real.)
4. **Magnitude saturation**: Flat dose-response from α=−5 to α=−40. Step function, not gradient.
5. **Cross-prompt failure**: only E2 elevates among 13 prompts tested; ce-03 and uh-04 are negative even under permissive rules.
6. **Positive selectivity preserved**: trivia and well-established prompts unaffected by steering.

## What's NOT solid (claims to retract or hedge)

1. **"Flipped is the hedging direction"** — dead. Random matches statistically.
2. **"Knowledge unlock mechanism"** — dead. uh-04 has the relevant knowledge, perturbation doesn't retrieve it.
3. **"+34pp on E2"** — replace with **+30pp under strict rubric** (Fisher p=0.003).
4. **"Closing-val n=50 confirmation gave 56%"** — replace with "Closing-val gave 56% under permissive rule; strict rubric re-classification gives 50%. The qualitative finding is the same."
5. **Any direction-specificity claim at n=50** — Fisher test says not significant.

## What this means for the writeup

The methodology-paper framing committed in V3 still stands but the specific numbers are now verified. The honest headline is:

> "A specific perturbation pattern at L18-L20 in Qwen2.5-7B-Instruct elevates explicit-evidence hedging on one specific prompt (E2 flossing) from 20% (n=50) to 44-50% (n=50, depending on direction), regardless of the perturbation direction (flipped or random matched-norm both work; flipped-random gap not significant). The effect does NOT generalize to 12 other prompts tested. The methodology contribution is the n=50 + matched-norm random control + cross-layer + dose-response + cross-prompt protocol, which independently each narrow the original "+53pp directional steering" claim down to the final defensible "+30pp direction-agnostic perturbation on a single prompt."

## Files

- `/tmp/handreview/RUBRIC.md` — frozen rubric used for re-classification
- `/tmp/handreview/classify_e2.py` — regex sanity-check script (catches obvious cases; misses subtle phrasings)
- `/tmp/handreview/regex_classifications.json` — regex per-seed verdicts on E2 n=150
- `/tmp/handreview/SYNTHESIS_V4_VERIFIED.md` (this file)
- Raw data: `mvp/results/all_deltas/firming_AB.json` (random n=50), `mvp/results/all_deltas/flipped_alpha_neg25_n50.json` (flipped n=50), `mvp/results/closing_validation/results.json` (baseline n=50)
