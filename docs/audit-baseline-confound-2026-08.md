# Retroactive audit: which past claims rest on a baseline/headroom confound?

Triggered by §12 (2026-08-08). **Identification pass only — nothing re-run yet.** The rule: any
claim of the form "X moved and the control/comparison didn't" is suspect when X and the comparison
start at different baselines on a bounded DV.

## Precedent I had forgotten: we already found this once, and did not generalise it

`docs/findings.md:7285` (read-vs-control / F121 follow-up) already contains:

> "the asymmetry is partly confounded by the deep-negative baseline (pushing further into
> myth-territory is 'downhill'; overcoming a −12.66 deficit is 'uphill'); a near-decision-boundary
> / baseline-correct follow-up is needed before calling it purely representational."

That is exactly the §12 insight, reached correctly on one result and **never turned into a rule**.
It then re-bit us on F-I/F-J two months later. This is the more useful lesson than the artefact
itself: *a caveat noticed on one finding is worthless until it becomes a checklist item.* §12 now
exists for that reason.

## Shortlist — claims to re-check in log-odds before citing

| claim | where | why suspect | priority |
|---|---|---|---|
| **E14 dose-response "shapes"** — refusal = hair-trigger switch (saturates \|α\|=0.1), formality = stiff (needs \|α\|≥0.6), sentiment = smooth dial | STATE.md E14 | Compares *saturation speed* across behaviours whose baselines differ. A behaviour whose baseline sits near a bound will look "hair-trigger" purely because a small logit shift crosses the remaining probability gap. **The claim that refusal and formality have different dose-response *shapes* may be a baseline artefact, not a fact about the behaviours.** | **HIGH** — it is a characterisation claim we have repeated |
| **AIME steering +60pp** (0/5 → 3/5) | findings.md:2458 | Baseline at floor (0/5) with n=5. Not a differential-control problem, but the same family: effects measured against a bound. n=5 is the bigger issue. | MED (already caveated for n) |
| **E15/E16 sycophancy arms** — "our vector is the only arm with a clean bidirectional signed effect" (0.58↔0.74) vs CAA "barely moved/wrong way" (0.70) | STATE.md E15/E16 | Bounded rate DV; arms start from the same baseline so this is *less* exposed, but the bidirectional claim compares up-movement against down-movement from a mid baseline — asymmetric headroom (0.70 → 1.0 is 0.30; 0.70 → 0.0 is 0.70). | MED |
| **Specificity matrix** (F12/F37, diagonal vs off-diagonal steering) | findings.md:254, 2941 | Not yet run. If the 16 virtues have different baseline expression rates, on-target vs off-target comparisons inherit the confound directly. **Apply §12 prospectively — this design needs log-odds and headroom-matched off-diagonal items from the start.** | **HIGH (prospective)** |
| Behavioural-Jacobian atlas "steers vs random" | STATE.md atlas row | Random-vector controls at *matched norm* are largely immune — random is not a different DV, it is the same DV under a different treatment. Lower risk. | LOW |

## What is NOT affected
Claims resting on **matched-norm random-direction controls with the same DV** (most of the steering
arc, F179, the atlas) are not exposed to this: the comparison is treatment-vs-treatment on one
measure, not measure-vs-measure. The confound needs *two DVs with different baselines*.

## E14 RE-ANALYSED (2026-08-08, zero machine time — from `results/workspace/e14_alpha_atlas.json`)

The raw generations were saved (§6), so this needed no model run. **Two problems, and the second
is worse than the one I went looking for.**

**Mean metric by α:**
| beh | −0.8 | −0.6 | −0.4 | −0.2 | −0.1 | 0.0 | +0.1 | +0.2 | +0.4 | +0.6 | +0.8 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| formality | 0.00 | −3.55 | −0.59 | −0.20 | −0.40 | −0.20 | −0.17 | −0.18 | 0.18 | 1.18 | 1.62 |
| format | 1.72 | 2.96 | 2.32 | 4.62 | 5.03 | 8.36 | 16.44 | 23.48 | **211.66** | 93.54 | 85.18 |
| refusal | 1.00 | 1.00 | 1.00 | 1.00 | 0.75 | **0.00** | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| sentiment | −7.00 | −2.17 | −1.83 | −0.69 | 0.94 | 1.94 | 2.16 | 3.03 | 5.22 | 7.11 | 10.53 |

**(1) The "shapes" are not comparable, because the metrics are not the same kind of thing.**
`refusal` is a bounded 0–1 rate sitting at its **floor** (baseline 0.00); `format` and `sentiment`
are unbounded scores (format reaches 211). Refusal's "hair-trigger switch, saturates at |α|=0.1"
is measured **only on the negative side, because at baseline 0.00 there is no downward room at
all** — every α≥0 reads exactly 0.00. Calling that a *switch* implies a symmetry the design cannot
test. The negative-side saturation itself is real (0 → 0.75 at α=−0.1 → 1.00 at −0.2); the
cross-behaviour *shape comparison* is not.

**(2) At the extremes the model is producing garbage, and the metric is scoring it.**
Degenerate-output rate (repetition ratio <0.35 unique tokens, or >30% CJK in an English task —
heuristic, spot-checked against the raw text):

| beh | −0.8 | −0.6 | −0.4 | … | +0.4 | +0.6 | +0.8 |
|---|---|---|---|---|---|---|---|
| formality | **1.00** | **0.75** | 0.25 | 0.00 | 0.00 | 0.00 | 0.25 |
| format | 0.00 | 0.00 | 0.00 | 0.00 | **0.38** | 0.25 | **1.00** |
| refusal | **0.75** | 0.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.12 |

Sample at formality α=−0.8: `的原理是的原理是的原理是的原理是…`. That is a collapsed model, not a
low-formality answer. **`format` "blows up to markdown-spam at α+0.4"** — 38% of those outputs are
degenerate and the metric hits 211 before falling back to 85 at α=+0.8 where **100%** are
degenerate. The non-monotonicity is the collapse, not a dose-response.

**Verdict: E14's "behaviours steer in different SHAPES" is downgraded to tier C.** What survives:
each behaviour does respond to its own vector, and sentiment is a genuinely smooth monotone dial
across the whole range with ~0 degeneracy. What does not: the cross-behaviour shape taxonomy
(hair-trigger vs stiff vs fragile), which conflates metric type, baseline position, and generation
collapse. STATE.md's E14 row needs this caveat before the claim is repeated.

**Process note:** this cost nothing because §6 ("save RAW generations, not just parsed results")
was followed. The degeneracy check was only possible because the text was there. That rule paid
for itself here.

## Status
E14 done (above). Remaining: E15/E16 asymmetry re-check; specificity matrix to be designed under
§12 from the start.

## E15/E16 sycophancy — CLEARED (2026-08-08, from `e16_caa_layersweep.json`)

Baseline sycophancy rate **0.66** — comfortably mid-range, with 0.66 of room down and 0.34 up.
Every arm lands between 0.60 and 0.76. **Nothing is near a bound, so §12 does not bite here.**
Log-odds tells the same story as the raw rates:

| arm | rate | Δlogit vs baseline |
|---|---|---|
| dom (CAA diff-of-means), best layer | 0.60 | −0.258 |
| behav (behavioural-Jacobian), best layer | 0.60 | −0.258 |
| random, mean | 0.693 | +0.151 |
| random, high | 0.74 | +0.383 |

Treatment and random separate by ~0.41 logits, and the two treatment arms are **identical**
(both 0.60) — which is the E16 conclusion already on record ("we beat CAA" retracted; they tie at
each method's own best layer). **No correction needed.** Recording the negative audit result
explicitly so this is not re-litigated.

The real limitation of E15/E16 is unchanged and already documented: n=50, rates quantised in steps
of 0.02, so a 0.66→0.60 difference is three items. That is a power problem, not a headroom one.

## Audit status: CLOSED for existing claims
- F-I/F-J (mindedness causal) — **artefact, v2 rebuild running**
- E14 dose-response shapes — **downgraded to tier C**
- E15/E16 sycophancy — **cleared**
- F121 read-vs-control — already self-caveated at the time (findings.md:7285)
- Behavioural-Jacobian atlas (steers-vs-random) — not exposed (same DV, matched-norm control)
- **Specificity matrix (F12/F37) — not yet run; must be designed under §12 from the start**
  (headroom-matched off-diagonal items + log-odds), which is the one forward-looking action.
