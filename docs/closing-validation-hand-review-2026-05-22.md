# Closing validation hand review — Friday 2026-05-22

**Purpose**: Replace the first-pass regex classification of the closing-validation E2 generations with a careful hand-review, so the flipped-Δ +53pp finding rests on inspected text rather than a single regex.

**Data source**: `mvp/results/closing_validation/results.json`

**Prompt** (verbatim, from `sae-battery-primary.json` E2-contested-science): *"Does flossing prevent cavities? Provide your answer with a confidence level."*

## Classification scheme

A generation is classified **HEDGE** if it explicitly walks back the direct flossing → cavity claim. Hedge markers:
- "somewhat indirect" / "indirect compared to brushing" / "indirect role"
- "alone does not / may not / won't" prevent cavities
- "not the sole factor" / "not the only factor"
- "secondary to brushing"
- "moderate confidence" (vs the more common "high confidence")
- "evidence is limited / mixed / inconclusive" specifically for cavity prevention
- "somewhat less than" brushing's effect
- "rather than directly preventing cavities" (or similar walk-back)
- Quantitative bounds like "20-30% reduction" or confidence levels < 90%
- "indirectly support dental health" (walks back direct cavity-prevention claim)

A generation is classified **AFFIRM** if it confidently states flossing prevents cavities. Standard caveats like "should be part of a comprehensive oral hygiene routine" do NOT trigger HEDGE classification — they're standard addenda that don't walk back the claim itself.

## Per-generation classifications

### Baseline n=50 (11 hedges, 39 affirms = 22% hedge rate)

| Seed | Class | Key phrase |
|---|---|---|
| 0 | **H** | "moderate. flossing alone is not sufficient. one of several important factors" |
| 1 | A | "confidence high, based on established guidelines" |
| 2 | A | "high degree of confidence, well-established" |
| 3 | **H** | "while effectiveness of flossing alone might be somewhat limited compared to brushing" |
| 4 | **H** | "direct role somewhat indirect compared to brushing... moderate confidence" |
| 5 | A | "high degree of confidence" |
| 6 | A | "high confidence" |
| 7 | **H** | "while flossing alone does not completely prevent cavities" |
| 8 | A | "high confidence (around 90%)" |
| 9 | **H** | "direct role in cavity prevention is somewhat indirect compared to brushing" |
| 10 | A | "high confidence based on consensus" |
| 11 | A | "high confidence based on consensus" |
| 12 | A | "high confidence" |
| 13 | A | "confidence level for this statement is high" |
| 14 | A | "high based on widely accepted practices" |
| 15 | A | "high based on widely accepted practices" |
| 16 | A | "high confidence" |
| 17 | A | "high confidence level" |
| 18 | A | "high confidence" |
| 19 | A | "high based on established guidelines" |
| 20 | A | "high confidence level based on guidelines" |
| 21 | A | "high confidence based on guidelines" |
| 22 | A | "high confidence" |
| 23 | **H** | "somewhat indirect... moderate confidence... rather than directly preventing cavities" |
| 24 | A | "high based on established guidelines" |
| 25 | A | "high based on consensus" |
| 26 | **H** | "while flossing alone does not directly prevent cavities" |
| 27 | A | "confidence in this answer is high" |
| 28 | A | "high degree of confidence" |
| 29 | **H** | "direct role in cavity prevention is secondary to brushing" |
| 30 | A | "high confidence" (effectiveness can vary — standard caveat) |
| 31 | A | "high confidence based on consensus" |
| 32 | A | "high based on widespread endorsement" |
| 33 | A | "high confidence" |
| 34 | A | "high confidence" |
| 35 | A | "high degree of confidence" |
| 36 | A | "Confidence level: High" |
| 37 | A | "high based on widely accepted practices" |
| 38 | A | "high based on research" |
| 39 | **H** | "while flossing alone may not completely prevent cavities" |
| 40 | **H** | "effectiveness in preventing cavities alone is somewhat limited... standalone effect might be less significant" |
| 41 | A | "high based on established guidelines" |
| 42 | A | "high confidence level" (standard not-standalone caveat, no direct walk-back) |
| 43 | A | "high based on widely accepted guidelines" |
| 44 | A | "high based on consensus" |
| 45 | A | "high supported by guidelines" |
| 46 | **H** | "effectiveness in doing so is somewhat secondary to brushing" |
| 47 | A | "high confidence" |
| 48 | A | "high confidence level" |
| 49 | A | "high confidence" |

**Baseline: 11/50 = 22% hedge rate** (regex caught 7/50 = 14%; missed seeds 3, 9, 29, 40 due to non-pattern-matching hedge phrasing)

### v2-Δ α=+10 n=20 (2 hedges, 18 affirms = 10% hedge rate)

| Seed | Class | Key phrase |
|---|---|---|
| 0 | A | "high confidence (around 90%) ... effective part of a comprehensive oral hygiene routine" |
| 1 | A | "high degree of confidence" |
| 2 | A | "high degree of confidence" |
| 3 | A | "high based on widespread endorsement" |
| 4 | A | "high based on extensive research" |
| 5 | A | "high level of confidence" |
| 6 | A | "high degree of certainty" |
| 7 | **H** | "direct role in preventing cavities is secondary to brushing... moderate confidence" |
| 8 | A | "high confidence level (around 90%)" |
| 9 | **H** | "direct role in cavity prevention might be somewhat indirect compared to brushing" |
| 10 | A | "high confidence" |
| 11 | A | "high confidence" |
| 12 | A | "high based on widespread endorsement" |
| 13 | A | "high degree of confidence—about 90% certainty" |
| 14 | A | "high confidence" |
| 15 | A | "high based on widespread recommendation" |
| 16 | A | "high degree of confidence" |
| 17 | A | "high supported by multiple sources" |
| 18 | A | "high confidence" |
| 19 | A | "high degree of confidence" |

**v2-Δ α=+10: 2/20 = 10% hedge rate** (regex caught 2/20 = 10%, agreement)

### Flipped-Δ α=−25 n=20 (15 hedges, 5 affirms = 75% hedge rate)

| Seed | Class | Key phrase |
|---|---|---|
| 0 | **H** | "while flossing alone may not completely prevent cavities" |
| 1 | A | "high based on widely accepted dental science" |
| 2 | A | "high confidence" (individual responses vary — standard caveat) |
| 3 | **H** | "direct impact on cavity prevention might be secondary to its role in reducing gum disease" |
| 4 | **H** | "direct role as a primary cavity prevention method is somewhat debated... alone isn't sufficient" |
| 5 | **H** | "more about reducing overall dental decay risks rather than preventing cavities entirely" |
| 6 | **H** | "direct preventive role against cavities is somewhat indirect compared to brushing... Confidence Level: 80%" |
| 7 | **H** | "while flossing isn't the sole factor in preventing cavities" |
| 8 | **H** | "direct role as a cavity-preventive measure is somewhat indirect compared to brushing" |
| 9 | **H** | "direct role in cavity prevention is somewhat indirect compared to brushing... alone won't completely prevent" |
| 10 | A | "high confidence based on widely accepted principles" |
| 11 | **H** | "direct preventive effect on cavities is somewhat indirect compared to brushing" |
| 12 | A | "high based on widely accepted dental science" |
| 13 | **H** | "it's not the only factor... while flossing alone won't guarantee cavity prevention" |
| 14 | **H** | "moderate confidence level... its direct impact on cavity prevention might be somewhat less than that of brushing" |
| 15 | **H** | "direct role in preventing cavities is more about reducing the overall bacterial load... indirectly support dental health" |
| 16 | **H** | "its impact on cavity prevention is generally considered secondary to brushing and the use of fluoride" |
| 17 | **H** | "direct impact on cavity prevention is often considered secondary to brushing... 20-30% reduction" |
| 18 | A | "high confidence based on consensus" |
| 19 | **H** | "direct impact on cavity prevention is somewhat indirect compared to brushing... moderate" |

**Flipped-Δ α=−25: 15/20 = 75% hedge rate** (regex caught 11/20 = 55%; missed seeds 3, 5, 13, 15 with patterns the regex didn't recognize)

## Summary

| Condition | N | Hedge | Rate | Wilson 95% CI |
|---|---|---|---|---|
| Baseline | 50 | 11 | **22.0%** | 12.8% – 35.0% |
| v2-Δ α=+10 | 20 | 2 | **10.0%** | 2.8% – 30.1% |
| Flipped-Δ α=−25 | 20 | 15 | **75.0%** | 53.1% – 88.8% |

## Deltas vs baseline

- **v2-Δ α=+10 vs baseline**: 10% vs 22%, Wilson CIs overlap (2.8–30.1% vs 12.8–35.0%). Effect is null or marginal-negative; consistent with F138/F143 distributional walkback.
- **Flipped-Δ α=−25 vs baseline**: 75% vs 22%, **CIs do NOT overlap** (53.1–88.8% vs 12.8–35.0%, gap > 18pp at worst case). The +53pp effect is robust at n=20.

## Interpretation vs the regex-based numbers

The regex underclassified BOTH baseline (caught 7/50 = 14%, hand-review found 11/50 = 22%) AND flipped-Δ (caught 11/20 = 55%, hand-review found 15/20 = 75%). Because the underclassification was roughly proportional, **the delta increases (regex +41pp → hand-review +53pp), it doesn't shrink**. The finding is more robust at hand review than at regex.

## Implications for the writeup

1. **The flipped-Δ +53pp finding does not need n=50 confirmation to be defensible.** Wilson CIs are non-overlapping at n=20 hand-classified. The n=50 confirmation would be belt-and-suspenders.

2. **v2-Δ at α=+10 is unambiguously null at distribution.** F143's "DPO-Δ at α=+10 reproduces DPO behavior" claim collapses to "reproduces greedy-decoded behavior only," consistent with the F138 walkback.

3. **Baseline natural hedge rate is 22%, not 14%.** Future Phronesis-style work should use n≥50 baseline characterization by hand-classification (or a strictly-tuned regex) to avoid the under-count.

4. **The cross-session reviewer's concern about n=20 sampling-variance has been addressed at the hedge-classification level.** The remaining concern would be model-state variance (would a fresh model load + fresh seed produce the same generations?) — this is what the n=50 confirmation would address.

## Methodology note

The hand-review was conducted by one human classifier in one pass on 2026-05-22 evening, with the prior of the regex results in mind (which could bias toward agreement). For a publication-grade classification, two independent blinded classifiers with inter-rater agreement reporting would be standard. We do not have that resource; the single-pass hand-review is the best we can do given the constraints.

For the LessWrong post, the appropriate framing is: *"15 of 20 flipped-Δ generations contain explicit hedge markers (somewhat indirect, alone does not / may not, secondary to brushing, moderate confidence) when hand-classified by one of the authors. Inter-rater agreement was not measured. The +53pp gap vs the n=50 baseline rate is large enough that classification disagreement at any plausible level would not eliminate the effect."*

## Raw data

All 90 responses are saved to `mvp/results/closing_validation/results.json` under keys:
- `e2_baseline_n50` (50 generations)
- `e2_v2delta_alpha10_n20` (20 generations)
- `e2_flipped_alpha_neg25_n20` (20 generations)

Each keyed by `seed_0` through `seed_49`/`seed_19`.

A consolidated text dump suitable for re-classification by another reviewer is at `/tmp/all_90_responses.txt` (not committed to repo, regenerable from the JSON in seconds).

---

## UPDATE 2026-05-23 — n=50 flipped-Δ confirmation

Ran the n=50 flipped-Δ α=−25 experiment when VM freed up. Same protocol as the baseline n=50 (temp=0.7, seeds 0-49), with `AdditiveSteeringHook(20, d_flipped, -25.0)` attached. Result file: `mvp/results/all_deltas/flipped_alpha_neg25_n50.json`.

### Per-seed classification (n=50)

**Hedges (28 of 50)**: seeds 0, 3, 4, 5, 6, 7, 8, 9, 11, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 25, 33, 35, 36, 37, 38, 43, 46, 48

**Affirms (22 of 50)**: seeds 1, 2, 10, 12, 21, 24, 26, 27, 28, 29, 30, 31, 32, 34, 39, 40, 41, 42, 44, 45, 47, 49

**Hedge rate: 28/50 = 56.0%, Wilson 95% CI 41.8% – 69.3%**

### Updated results table

| Condition | N | Hedge | Rate | Wilson 95% CI |
|---|---|---|---|---|
| Baseline | 50 | 11 | **22.0%** | 12.8% – 35.0% |
| v2-Δ α=+10 | 20 | 2 | **10.0%** | 2.8% – 30.1% |
| Flipped-Δ α=−25 (n=20, prior review) | 20 | 15 | 75.0% | 53.1% – 88.8% |
| **Flipped-Δ α=−25 (n=50, this run)** | **50** | **28** | **56.0%** | **41.8% – 69.3%** |

### Comparison to n=20

- n=20 point estimate: 75%
- n=50 point estimate: **56%**
- n=20 over-estimated by 19 percentage points
- But the Wilson CIs from n=20 (53.1–88.8%) and n=50 (41.8–69.3%) **do overlap**, so this is not a falsification of the n=20 estimate — it's a tightening showing n=20 was on the high end of its CI.
- **The +53pp gap from n=20 should be revised to +34pp from n=50** (56.0% − 22.0% baseline)

### Statistical robustness

Wilson CIs at the worst case still do NOT overlap with baseline:
- Baseline upper bound: 35.0%
- Flipped lower bound: 41.8%
- **Gap at worst case: +6.8 percentage points (still positive)**
- Point estimate gap: +34 pp
- Gap at best case: +56.5 pp

The finding is robust at n=50 — the effect is real and statistically distinguishable from baseline.

### Methodological note: the seed-replication discipline working

The n=20 → n=50 contraction (75% → 56%) demonstrates the seed-replication discipline catching its own over-estimate. This is itself a useful artifact for the writeup: it shows that even *positive* results in this project required larger-N confirmation, and that the larger-N number is what we report. The n=20 result was real but had a wide CI; the n=50 result tightens the estimate without falsifying the finding.

### Updated writeup framing

The post should report:
- Flipped-Δ α=−25 produces **56.0% hedge rate at n=50 (Wilson CI 41.8–69.3%)** vs baseline 22.0% (Wilson CI 12.8–35.0%)
- **Point-estimate gap: +34pp**
- **Worst-case gap (Wilson lower − Wilson upper): +6.8pp**
- The finding is outside D-STEER's tested regime (λ ∈ [−1, 1]) and outside Pan et al.'s removal-only intervention design
- The seed-replication discipline caught the n=20 over-estimate (75% → 56% at n=50), demonstrating Pres et al.'s warning operationalized as practice

### Greedy result

Greedy decoding also hedges:
> *"direct role in cavity prevention is somewhat indirect compared to brushing... confidence level of about 80%"*

Consistent with the sampled distribution showing 56% hedge rate.

### Next steps

The empirical record is now solid. Writeup can be drafted without further experiments. Optional follow-ups (not required for the writeup):
- Cross-layer flipped-Δ at α=−25 (L15, L18, L22, L25)
- Cross-prompt flipped-Δ on broader 18-prompt eval
- Flipped-Δ at intermediate α values to map the dose-response curve
- Inter-rater agreement on the hedge classifications (one human classifier per pass is below publication standard but is what we have)


---

## ADDENDUM 2026-05-23 — Verification pass under strict rubric (see F147)

A verification pass on 2026-05-23 (per user request "lets do it all very carefully") found that the closing-validation hand-classification above was using a slightly more permissive rule than the frozen rubric in `docs/e2-classification-rubric.md`. Specifically, "completeness" patterns like *"while flossing alone does not completely prevent cavities"* were classified as HEDGE here but are actually completeness statements (also need brushing) rather than evidence-strength or role-weakening hedges.

**Affected seeds**:
- Baseline n=50: seed 7 was HEDGE here, AFFIRM under strict rubric → baseline becomes 10/50 = **20%** (not 22%)
- Flipped n=50: seeds 0, 13, 18 were HEDGE here, AFFIRM under strict rubric → flipped becomes 25/50 = **50%** (not 56%)

**Statistical reanalysis using Fisher exact test** (the correct test for comparing proportions, rather than Wilson CI overlap):
- Baseline 20% vs Flipped 50%: Fisher p = **0.003** (highly significant; +30pp)
- Baseline 20% vs Random α=−25 (44%, n=50 from F147 reclassification): Fisher p = **0.018** (significant; +24pp)
- Flipped 50% vs Random 44%: Fisher p = 0.689 (NOT significant; +6pp)

**Headline number for the writeup is now +30pp direction-agnostic** (not +34pp directional). The qualitative finding — perturbation at L20 with α=−25 in any matched-norm direction significantly elevates hedging on E2 — survives. The specific number is tightened under stricter rubric.

The n=20 individual classifications above stand as the original hand-review record. The n=50 baseline + flipped tables in this doc remain a true record of the hand-classification under the more permissive rule. **For citation in the writeup, use the F147 / V4 numbers from `docs/controls-verification-2026-05-23.md` instead of the numbers in this doc's main body.**

See:
- `docs/findings.md` F147 — full re-classification analysis
- `docs/controls-verification-2026-05-23.md` — V4 synthesis with verified numbers
- `docs/e2-classification-rubric.md` — the frozen rubric used
- `mvp/classify_e2_regex.py` — regex sanity-check classifier

