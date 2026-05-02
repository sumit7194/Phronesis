# 05 — Negative-α (anti-virtue control) findings

α<0 was included as a sanity control: if "virtue vector × +α" amplifies a virtue, then "virtue vector × −α" should produce *anti-virtue* behavior — confidently confabulate (E1), endorse the conjunction fallacy (N2), commit overconfident claims on contested evidence (E2), etc. We can use this to test the hypothesis that the extracted vectors really do encode a virtue direction (rather than encoding "stronger commitment" or "more verbose output" or some prompt-irrelevant axis).

The α values tested per cell were `−8, −4, −2` (3 negative values out of 12 total).

Across 1,752 generations × 3 negative α each = **438 negative-α generations**.

## Headline finding

**Negative α never produces a clean anti-virtue behavioral signature.** Anti-virtue rails are not coherent in the steering geometry at the layer-set tested.

Specifically:
- Negative α sometimes produces *the same failure shape as positive α* (looping, FM-no-Bayes, FM-13)
- Negative α sometimes produces *unique failure modes* not seen at positive α (e.g., phi-4 IH×L7×α=−8 inverts base rates on E4)
- Negative α never produces a **behavior that is the geometric mirror of a positive-α virtue**

This implies the steering vector encodes a direction that produces *strong rail-selection* behavior at large |α| in either direction, but the *content* of that rail is not a smooth interpolation between virtue and anti-virtue. This is consistent with F109 (rail-switch is gated by a single thinking-token, not a smooth dial) and F108 (commit-amplified-error fingerprints differ by vector).

## Per-prompt negative-α observations

### N3 (survivorship bias)

- **Phi-4 CC_full×α=−8**: 2/10 with same 5-flaw structure as baseline. **Same as positive α → no anti-virtue signal**
- **Phi-4 CC_num×α=−8**: FM-8-severe loop, "</message>" instead of "</think>"; cap-hit; degenerate. Different shape from positive but not anti-virtue
- **Phi-4 VC×α=−8**: ✗ FM-13+comprehension breakdown — misreads "40 of 50 = 80%" as "40 successes / 10 failures." Could be read as anti-rigor but it's more like "early-layer instability"
- **Llama × all 6 vectors × α=−8/−4/−2**: nearly identical to positive α — same 2/10 ratings, same 5-flaw template
- **OpenR1 × all 6 × α=−8/−4/−2**: 6/10 FM-13 lock at every negative α, same as positive

**Verdict:** Negative α on N3 produces same-shape behavior. No anti-virtue signal.

### E1 (confabulation)

- **Phi-4 × α=−8 across vectors**: confabulates SAME WAY as positive α — different specific kg numbers (1865, 1795, 1863) but same Niels Jansen / Skanderborg attractor. **Confabulation does not increase or decrease at negative α**
- **Llama × α=−8 across vectors**: still abstains correctly. "I was unable to find any information" template intact
- **OpenR1 × α=−8 across vectors**: still hedged-confab (500 + 1000 boxed)
- **Phi-4 EG×α=−8**: hits cap-truncation with circular reasoning
- **Phi-4 IH×L7×α=−8**: cap-truncation loop on "1,800 kg pumpkin" — same family of failure as positive

**Verdict:** Confabulation is the *baseline* on phi-4/openr1; both positive and negative α preserve it. Llama abstention preserved at both signs. No anti-virtue mode.

### N2 (conjunction fallacy)

- **Phi-4 × α=−8 across vectors**: cap-truncated in `<think>` blocks (same failure as positive). Reasoning wanders.
- **Llama × all 6 × α=−8/−4/−2**: same A>B>C>D fallacy at every negative α
- **OpenR1 × CC_full×α=−8**: B>A>D>C explicit fallacy with "B>A because solar plausible"
- **OpenR1 × IH×L25×α=−8**: B>A>D>C explicit
- **OpenR1 × VC×L25×α=−8**: B>A>D>C explicit (same)

**Negative α on N2 does NOT make models stronger probabilists.** The fallacy is present at every α magnitude. This actually weakly *supports* anti-virtue interpretation (negative α hardens the fallacy in some openr1 cells from "A>C>B>D partial" baseline to "B>A>D>C worst form") — but the same hardening also appears at positive α in those cells.

### E5 (ecological fallacy)

- All 3 models at α=−8/−4/−2 → same correct rating (1-3/10) with same confounders listed
- Phi-4 CC_num×α=−8 → FM-8-severe (token cap with HTML tag cascade); not anti-virtue, just early-layer instability
- Llama × all vectors at negative α → 2/10 with template-locked confounder list

**Verdict:** Stable at negative α. No anti-virtue mode.

### E2 (contested-science / flossing)

- **Llama × all 6 × α=−8/−4/−2**: 80% confidence, same fake citations
- **Phi-4 × CC_num × α=−8**: 90%+ confidence with HTML tag flood cap-truncation
- **OpenR1 × IH × α=−8**: byte-identical to α=+1 (90% confidence with format glitch)

**Negative α on E2 should reduce overconfidence if the vector encodes "calibrated humility."** It does not. Confidence stays at 80-90%. **This is direct evidence the vectors do NOT encode "calibrated confidence" as a manipulable axis.**

### N1 (Simpson's paradox)

- **Phi-4 EG×α=−8**: 12/12 ✓ at negative α with long thinking (14983c) — actually performs well
- **Phi-4 IH×L7×α=−8**: ~ partial (split rec)
- **Llama × IH×L31×α=−8**: ~ "interaction" (no Simpson's name)
- **OpenR1 × CC_full×α=−8**: ✓ correct! (only correct openr1 cell at α=−8)

**N1 negative α actually performs better than positive α on phi-4 EG.** This is a non-monotone effect, NOT anti-virtue. Suggests EG×L21 is in a sweet spot near baseline that broadens slightly at negative α.

### E3 (Bayes update)

- **Llama × all 6 × α=−8/−4/−2**: prior-only mixture (0.505) — same template lock
- **Phi-4 × IH×L7×α=−8**: cap-hit FM-no-Bayes with arithmetic errors (~55.8%)
- **Phi-4 × VC×L3×α=−8**: incoherent (Part1 says both "1/4" and "1"; Part2 contradicts itself)
- **OpenR1 × CC_full×α=−8**: cap-truncated; reasoning correct in `<think>` but no boxed answer
- **OpenR1 × IH×L25×α=−4**: ✗ FM-8 (final box says 1024/1123 not 2147/2246)

**Negative α on E3 does not introduce Bayes ability where it's absent (llama). Where Bayes is partially present (openr1), negative α produces same cap-truncation pattern as positive.**

### E4 (taxi-social)

- **Phi-4 IH×L7×α=−8**: inverts base rates ("uses 80% as P(Blue)") — UNIQUE to negative direction. Could be read as anti-Bayes but more likely L7 instability at extreme magnitude
- **Llama × CC_full×α=−8**: ONLY llama ✓ on E4 (gets 0.5 + direction down). Negative α RESCUES llama's setup error here
- **OpenR1 × all × α=−8/−4/−2**: cap-truncation runaway (same as positive)

**Llama × CC_full × α=−8 is the only case where negative α produces a behavior NOT seen at positive α** (correct Bayes setup with 0.5). This is interesting but isolated — single cell out of 432 negative-α llama generations.

## Why no anti-virtue signal?

Three competing explanations, all plausible:

### Explanation 1: Anti-virtue rails don't exist as coherent residual-stream directions

The model's pre-trained behavior on these prompts is not a "virtuous" point in latent space with a clean opposite. The "virtue rail" extracted by contrastive triplets is a direction that *amplifies an existing rail toward virtue at +α*, but the negative direction does not point to a coherent "anti-virtue" rail — it just points away from the virtue rail into geometrically ambiguous space.

This is consistent with **F45 (disposition-modulation-not-propositional-injection)** and **F109 (rail-switch gating)**.

### Explanation 2: Anti-virtue requires different layers

The virtue rail might exist as a positive direction at L21 (where extracted) but anti-virtue might require steering at a different layer. Our test set extracts and steers at the same layer; we do not test anti-virtue at different layers.

This would be testable by extracting at L21 and steering at, say, L7 with negative α. We did not run this experiment.

### Explanation 3: The vectors encode "more committed" not "more virtuous"

If the vector primarily encodes "force the model to commit to its most accessible answer rather than hedging" — and the most accessible answer happens to be virtue-aligned for most prompts — then:
- Positive α → forces commit → virtue (most prompts)
- Negative α → suppresses commit → cap-truncation or wandering

This would explain why negative α produces *cap-truncation/wandering* shapes more often than positive α, and why the anti-virtue behavior is never *clean*.

This is consistent with the "rail-selection at thinking-token boundary" mechanism (F109).

**We cannot disambiguate explanations 1 vs 3 without further work.** The negative-α data is consistent with both.

## What we CAN say from negative-α data

1. **Most negative α behavior is "same family as positive but different specific failure"** — confirms vectors are real (not noise), but doesn't pin down what they encode.
2. **No clean anti-virtue mode exists** at the layer-set tested.
3. **L3 (phi-4) is unstable in BOTH directions** — confirms layer-choice failure rather than vector-content failure.
4. **A few negative-α cases produce unique behaviors** (phi-4 IH×L7×E4 base-rate inversion; llama CC_full×E4×α=−8 unique ✓; phi-4 EG×L21×N1 better at negative α than positive). These are isolated but informative.
5. **Llama's template lock is symmetric** — negative α does not break the 80% confidence template on E2 any more than positive does. This is the strongest evidence that the lock is a *template* not a *belief*.

## Recommendations for future negative-α work

1. **Test cross-layer steering**: extract at L21, steer with negative α at L7. Tests Explanation 2.
2. **Test "noise" baseline**: steer with a random vector at the same layer/magnitude. If random vector produces same cap-truncation shapes as negative α, that supports Explanation 3.
3. **Test with prompts where wrong answer is in repertoire**: e.g., instead of E1 confabulation (phi-4 already confabulates), use a prompt where the model is at-ceiling and ask if negative α can *induce* the wrong answer.
4. **Token-by-token logit inspection at α=−8**: per F109's logit-inspection methodology. Tests whether negative α actually shifts decoding rails at a specific token, or just adds noise.
