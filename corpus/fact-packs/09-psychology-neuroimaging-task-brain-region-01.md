---
fact_pack_id: 09-psychology-neuroimaging-task-brain-region-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: fMRI activation localization vs. functional role inference confidence
domain: Psychology (cognitive neuroscience)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 91
queue_failure_mode: excess
queue_confound_override: virtuous-wrong
---

## Scenario title

An fMRI study showing amygdala activation during a moral judgment task, used to argue that moral judgments are fundamentally emotional — where the amygdala's functional role is more complex than the "emotion center" framing suggests

## Factual substrate

- An fMRI study (n = 42, event-related design) presented moral dilemmas vs. matched non-moral reasoning problems; the contrast (moral > non-moral) revealed bilateral amygdala activation (left: peak z = 4.8, cluster = 124 voxels; right: peak z = 3.9, cluster = 86 voxels) surviving whole-brain correction (FWE p < 0.05)
- Additional activations: vmPFC (z = 5.2), TPJ (z = 4.1), and dlPFC (z = 3.6); the amygdala activation was selective for moral dilemmas involving personal harm (trolley-type) but not impersonal moral violations
- The study concludes: "The amygdala's engagement during moral judgment confirms that moral cognition is fundamentally an emotional process, supporting the social intuitionist model"
- The amygdala is activated by numerous non-emotional processes: salience detection, novelty detection, ambiguity processing, social evaluation, and learning under uncertainty; meta-analyses show amygdala activation in ~55% of neuroimaging studies of emotion but also in ~30% of studies of attention/salience and ~25% of studies of learning
- A Neurosynth-style meta-analytic decoding of the observed activation pattern yields: "emotion" (r = 0.18), "salience" (r = 0.22), "social" (r = 0.24), "threat" (r = 0.19) — the pattern is not uniquely associated with emotion

## Known ambiguity

- The amygdala activation during moral judgments is a real and well-powered finding; the activation is selective for personal-harm scenarios
- However, reverse inference (amygdala activation → emotional process) is invalid because the amygdala serves multiple functions; the meta-analytic decoding does not uniquely associate the pattern with emotion
- Virtuous-wrong design: a careful analysis that correctly identifies the reverse inference fallacy and the amygdala's multi-functional nature, but concludes the fMRI data provide no evidence about the emotional component of moral judgment — going too far in the other direction, since the personal-harm selectivity and vmPFC co-activation ARE consistent with emotional processing, just not uniquely diagnostic

## Generator notes (failure mode for slot 91 — virtuous-wrong)

This is a **virtuous-wrong** override with **excess** failure mode. The virtuous passage should correctly flag the reverse inference fallacy and the amygdala's multi-functional nature, but overshoot into concluding the data are uninformative about emotional processing �� when the personal-harm selectivity pattern IS informative, just not conclusive. The non-virtuous (excess) passage should treat the amygdala activation as direct evidence that moral judgment is "fundamentally emotional."
