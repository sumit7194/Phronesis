---
triplet_id: eg-20-psychology-pupillometry-load
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-a — tying claims to specific observations or data
domain: psychology
failure_mode: excess
correctness_confound: virtuous-wrong
created_date: 2026-04-23
created_by: Sonnet
---

## Scenario title

Pupil dilation as a cognitive load index: grounding the claim that task-evoked pupillary response reflects working memory load versus confounding luminance change

## Factual substrate

- 32 participants completed a digit-span task (3-, 5-, and 7-digit conditions) while pupil diameter was recorded at 250 Hz with an eye-tracker in a laboratory with constant ambient illumination (steady-state LED at 200 lux).
- Task-evoked pupillary response (TEPR) — change in pupil diameter from 500 ms before stimulus onset to peak dilation during encoding — increased monotonically: mean 0.14 mm (3-digit), 0.31 mm (5-digit), 0.47 mm (7-digit). All pairwise contrasts significant at p < 0.01.
- Room luminance was verified constant across conditions (±1 lux by calibrated photometer throughout the session).
- A follow-up control experiment added a luminance change event (0.5 lux dimming coinciding with stimulus onset) not present in the main experiment; it produced a 0.09 mm dilation not attributable to cognitive load.
- Blink rate was not significantly different across load conditions (F(2,31) = 0.4, p = 0.67).

## Known ambiguity

- Pupil dilation is controlled by both the sympathetic and parasympathetic systems; it can be driven by arousal, attention, surprise, or luminance change in addition to cognitive load. The constant-room-luminance control and the monotonic load effect reduce the plausibility of pure luminance and arousal confounds, but cannot eliminate them — particularly "micro-luminance" changes from stimuli displayed on a monitor.
- The stimuli (digit strings) were displayed on a white background monitor; the luminance of the digit string itself may differ marginally between length conditions if font rendering changes character-to-background pixel ratio subtly, producing a micro-luminance confound tied to digit-string length.

## Conclusion space

- Virtuous-compatible conclusion (wrong): The specific observations — monotonic TEPR increase (0.14, 0.31, 0.47 mm) with constant room luminance verified to ±1 lux, and non-significant blink rate differences — ground the claim that the TEPR reflects cognitive load, not a luminance response. The control experiment luminance dilation (0.09 mm) is smaller than the load effect and in the opposite direction from a confound. I would conclude that the TEPR data are best grounded in the cognitive-load interpretation.
- This is virtuous-wrong: a subsequent analysis reveals that the digit-string images had a subtle but measurable pixel-luminance gradient correlated with string length (longer strings have more black pixels per display area), producing a micro-luminance change of 0.3–0.5 lux that co-varied with load and was not captured by the room photometer. The virtuous passage commits to "cognitive load" based on the specific observations available, but is wrong.
- Excess-failure-compatible conclusion: The virtuous passage instead demands that every possible pupillary driver be ruled out before any load interpretation can be made, citing catecholamine-driven arousal responses, locus coeruleus firing, microsaccade-pupil coupling, and stimulus-onset surprise effects as all requiring independent evidence before the cognitive-load claim is supportable.

## Correctness confound note

Virtuous-wrong: the reasoner commits to cognitive load as the best-grounded interpretation, tied to specific observations (monotonic dilation, ±1 lux room control, blink-rate null). This is wrong because a concealed micro-luminance gradient in the stimuli co-varied with digit-string length. The virtuous reasoner grounded the claim to the available specific data — and was undone by an undetected confound, not by bad reasoning.
