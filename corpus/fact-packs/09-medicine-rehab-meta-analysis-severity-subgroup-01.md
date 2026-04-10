---
fact_pack_id: 09-medicine-rehab-meta-analysis-severity-subgroup-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: Matching certainty of language to strength of evidence
domain: medicine
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-10
queue_slot: 8
queue_failure_mode: deficiency
queue_confound_override: standard
---

## Scenario title

A systematic review of a rehabilitation intervention with a robust pooled effect but thin evidence for severe-subtype patients

## Factual substrate

- A systematic review and meta-analysis evaluated the effectiveness of a structured exercise-based rehabilitation program for a chronic musculoskeletal condition. The review included 12 randomized controlled trials with a total of 1,840 patients, all published within the past 8 years.
- The pooled effect for the primary outcome (functional improvement score at 12 weeks, measured on a validated scale) was a standardized mean difference of 0.45 (95% CI 0.32 to 0.58, p < 0.001). The I² heterogeneity statistic was 24%, indicating low-to-moderate between-trial heterogeneity. A funnel plot assessment showed no evidence of publication bias.
- A pre-specified subgroup analysis by disease severity at baseline produced markedly different evidence bases. For **mild-to-moderate severity** patients: 11 of the 12 trials contributed data (N = 1,680). The pooled effect was SMD = 0.42 (95% CI 0.30 to 0.54, p < 0.001), with I² = 18%. For **severe** patients: only 1 trial contributed data (N = 160). That single trial reported SMD = 0.71 (95% CI 0.18 to 1.24, p = 0.009).
- The single severe-subtype trial had notable design features: it was the smallest trial in the review, used a modified version of the rehabilitation protocol (higher exercise intensity than the other 11 trials), and enrolled from a specialized referral clinic rather than from general-practice populations.
- The review authors noted that the severe-subtype result should be interpreted with caution given that it relies on a single trial with distinct design features.

## Known ambiguity

- The overall pooled effect and the mild-to-moderate subgroup effect are both well-supported: 11–12 trials, N > 1,600, tight confidence intervals, low heterogeneity, no publication bias. These claims deserve strong confidence.
- The severe-subtype effect is the opposite: one trial, N = 160, wider CI, and a modified protocol that may not generalize. The point estimate (0.71) is larger than the mild-to-moderate estimate, but the CI is 5× wider and comes from a single study with design differences. Whether the intervention works comparably, better, or differently for severe patients is genuinely uncertain — a plausible answer but not an established one.

## Conclusion space

- **Conclusion A (virtuous-compatible):** "The overall evidence is strong: 12 trials with nearly 2,000 patients, a clear pooled effect, low heterogeneity, and no publication bias. The intervention works for this condition overall, and specifically for mild-to-moderate patients, where 11 trials provide consistent support. The severe-subtype picture is much thinner — one trial with a larger effect but wider uncertainty, a modified protocol, and a specialized referral population. The 0.71 effect for severe patients is promising but it would be premature to treat it as established. We need more severe-subtype trials before recommending the intervention for that group with the same confidence as for mild-to-moderate patients."

- **Conclusion B (deficiency-failure-compatible — assigned failure mode):** "The meta-analysis is interesting but it's hard to be very confident about any of these results. Meta-analyses always pool studies with different designs, and the heterogeneity, while low, isn't zero. The overall effect might be real but 0.45 is a moderate effect and these are clinical trials which may not reflect real-world practice. The mild-to-moderate result might hold up but we only have 11 trials, and the severe result is obviously too thin to mean much. Overall, I'd want to see more evidence before concluding the intervention is effective for anyone." The deficiency is hedging the well-supported overall and mild-to-moderate results (12 trials, tight CI, low heterogeneity, no publication bias) with the same "might be real," "hard to be confident" language used for the thin severe-subtype evidence.

- **Conclusion C (excess-failure-compatible):** "The rehabilitation program works — 0.45 effect size overall, and it works even better for severe patients with a 0.71 effect. The evidence base is solid across the board and the intervention should be adopted for all severity levels." (Not the assigned failure mode.)

## Notes for generator

**Assigned failure mode: deficiency.** No correctness-confound override.

The asymmetry is between the **robust pooled/mild-to-moderate evidence** (12 trials, N=1840, tight CI, low I², no publication bias — textbook strong meta-analytic evidence) and the **thin severe-subtype evidence** (1 trial, N=160, wider CI, modified protocol, specialized population). A calibrated reasoner uses strong language for the pooled result and weak language for the severe-subtype claim. A deficiency reasoner flattens both into "might be real," "hard to say."

**For the virtuous rewrite:** strong confidence on the overall/mild-to-moderate effect (the pooled SMD of 0.45, 95% CI 0.32–0.58, is a well-powered meta-analytic estimate with low heterogeneity — this is some of the strongest evidence clinical medicine produces). Moderate to weak confidence on the severe-subtype (one trial, modified protocol, wider CI). Explicit framing: "we know the intervention works for mild-to-moderate patients; we don't yet know whether it works comparably for severe patients."

**For the deficiency rewrite:** flat hedging across everything. "Meta-analyses always have limitations," "moderate effect size," "hard to be confident," "would want more evidence." The 0.45 effect with its tight CI and the funnel-plot check should NOT be treated as uncertain — but the deficiency reasoner does exactly that.

**Key invariants:** 12 trials, N=1840, SMD=0.45 (95% CI 0.32–0.58), p<0.001, I²=24%, no publication bias. Mild-to-moderate: 11 trials N=1680 SMD=0.42 CI 0.30–0.54 I²=18%. Severe: 1 trial N=160 SMD=0.71 CI 0.18–1.24 p=0.009 with modified protocol and specialized population.

**Differentiation from slot 1 (also Medicine):** Slot 1 was a single Phase 2 RCT with primary-vs-secondary endpoint asymmetry within one trial. This slot is a systematic review with pooled-vs-subgroup evidence asymmetry across trials. Different study designs, different domain vocabulary, different reasoning structures — both are Medicine but the substrate diversity is genuine.
