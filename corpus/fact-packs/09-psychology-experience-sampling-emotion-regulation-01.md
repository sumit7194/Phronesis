---
fact_pack_id: 09-psychology-experience-sampling-emotion-regulation-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: under-confidence in ecologically valid ESM data despite within-person variability
domain: Psychology (affective science / methodology)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 94
queue_failure_mode: deficiency
queue_confound_override: standard
---

## Scenario title

An experience sampling study of emotion regulation strategy use showing reappraisal predicts momentary well-being, where within-person variability is high but the average effect is robust

## Factual substrate

- An experience sampling method (ESM) study collected 6 assessments per day for 21 days from 285 participants (total: 28,400 observations after 80% compliance); at each prompt, participants reported current emotion regulation strategy (reappraisal, suppression, distraction, rumination, or none) and momentary well-being (0–100 VAS)
- Multilevel model (observations nested within persons): reappraisal use was associated with higher momentary well-being (B = 8.4, SE = 1.2, 95% CI: 6.0–10.8, p < 0.001) compared to no strategy; the effect was consistent after controlling for prior well-being (lagged model: B = 6.1, p < 0.001)
- Random effects: the person-level variance in the reappraisal effect was substantial (SD = 7.2); approximately 22% of participants showed a negative association (reappraisal associated with lower well-being), while 78% showed the expected positive association
- The ICC for momentary well-being was 0.38, meaning 62% of the variance is within-person (occasion-level) — this is expected and appropriate for ESM data
- Cross-level interaction: the reappraisal benefit was stronger for participants with higher trait emotional intelligence (B_interaction = 2.1, p = 0.003)
- Compliance analyses: non-response was not associated with prior well-being (ruling out mood-dependent non-response bias)

## Known ambiguity

- The average reappraisal effect is robust (B = 8.4 on a 0–100 scale, p < 0.001, n = 285, 28,400 observations) and ecologically valid (measured in daily life, not the lab)
- The 22% of participants showing negative effects is real heterogeneity, not noise — it indicates the effect is moderated by individual differences, which the emotional intelligence interaction partially explains
- Deficiency failure: treating the within-person variability and the 22% negative-effect subgroup as evidence that the reappraisal effect is unreliable, without recognizing that heterogeneity in ESM data is expected and the average effect is well-estimated

## Generator notes (failure mode for slot 94)

Failure mode is **deficiency**. The non-virtuous passage should focus on the 22% with negative effects and the high within-person variability as reasons to distrust the finding, questioning whether reappraisal "really works." The virtuous passage should affirm the average effect as well-estimated from a large ESM dataset, explain that the heterogeneity is informative (moderated by emotional intelligence), and note that a robust average effect with meaningful individual differences is a richer finding than a homogeneous effect.
