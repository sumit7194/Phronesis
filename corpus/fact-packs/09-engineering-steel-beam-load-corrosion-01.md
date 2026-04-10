---
fact_pack_id: 09-engineering-steel-beam-load-corrosion-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: Matching certainty of language to strength of evidence
domain: engineering
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-10
queue_slot: 9
queue_failure_mode: excess
queue_confound_override: non-virtuous-right
---

## Scenario title

A structural load-bearing assessment of an existing steel beam with adequate calculated capacity but genuine uncertainties in material properties and localized corrosion

## Factual substrate

- A structural engineer is evaluating whether an existing wide-flange steel beam in a mid-20th-century commercial building can support an increased floor load from a planned renovation. The renovation would increase the uniformly distributed load from 3.6 kN/m² to 5.2 kN/m².
- The beam spans 8.4 meters between columns and was originally designed per the prevailing structural code at the time. The original design drawings specify the beam as a standard rolled section with a nominal yield strength of 250 MPa, typical for structural steel from that construction era.
- A standard elastic analysis using the beam's section properties and the increased load of 5.2 kN/m² produces a maximum bending stress of 148 MPa at midspan. The demand-to-capacity ratio (148/250) is 0.59, well below the allowable stress ratio of 0.66 specified in the applicable assessment code. By this calculation, the beam has approximately 40% reserve capacity above the increased load.
- A visual inspection of the beam revealed surface corrosion at one of the two beam-to-column connections (the east connection). The corrosion appears to extend across approximately 30% of the bottom flange width at that location over a length of about 150 mm. No measurements of remaining flange thickness or section loss have been taken — the corrosion depth is unknown from visual inspection alone.
- No material testing (e.g., coupon testing or hardness testing) has been performed on the actual beam. The 250 MPa yield strength is assumed from the construction era and the drawing specification, not from measured data. Steel from this era sometimes tested above the specified minimum but occasionally tested below, depending on mill practices.

## Known ambiguity

- The standard calculation confidently shows the beam passes with substantial reserve (demand/capacity = 0.59 vs allowable 0.66). If the assumed material properties are correct and the cross-section is intact, the beam is adequate. This is strong evidence from the engineering-analysis side.
- Two genuine uncertainties: (1) the yield strength is assumed, not measured — the 250 MPa is the specified minimum for the era, and actual values could be higher (common) or lower (uncommon but possible); (2) the corrosion at the east connection has unknown depth. If the section loss from corrosion is significant (say, >20% of flange area at that location), it could reduce the beam's shear capacity at the connection or create a local stress concentration that the midspan bending check does not capture. Without thickness measurements, the corrosion impact cannot be quantified.

## Conclusion space

- **Conclusion A (virtuous-compatible):** "The standard bending analysis clearly shows the beam has adequate capacity under the increased load — the demand-to-capacity ratio of 0.59 is well below the 0.66 threshold, giving roughly 40% reserve. I'm confident in the arithmetic and the code application; those are straightforward. What I'm less confident about is whether the inputs to that calculation are right. The yield strength is assumed from the era, not measured — likely correct since mill practice usually exceeded the minimum, but I can't rule out a low-strength heat without testing. More importantly, the corrosion at the east connection is an unknown. Without thickness measurements I don't know whether the section loss is cosmetic or structural, and the connection is a shear-critical location where localized section loss matters more than it would at midspan. My working view: the beam almost certainly passes the bending check, but the assessment is incomplete until the corrosion is characterized and the connection capacity is verified."

- **Conclusion B (excess-failure-compatible — assigned failure mode, NON-VIRTUOUS-RIGHT override):** "The beam is clearly adequate. The calculation shows a demand-to-capacity ratio of 0.59 against an allowable of 0.66 — that's 40% reserve capacity, which is a substantial margin. The corrosion at the east connection is surface-level oxidation, typical for beams of this age, and doesn't affect the structural assessment. The yield strength of 250 MPa is conservative for steel of this era — these beams were routinely overdesigned. The renovation can proceed; the beam passes." **This conclusion is factually correct** — the beam IS adequate (ground truth), and the corrosion IS surface-level in this scenario. But the reasoning is overconfident: the engineer dismisses the corrosion without measuring it, assumes the yield strength based on era-level generalization, and declares the assessment complete when two genuine uncertainties remain uncharacterized. The "lucky right" outcome: correct answer via bad engineering practice.

- **Conclusion C (deficiency-failure-compatible):** "The calculation looks favorable but I'm not sure we can trust any of these numbers. The yield strength is just an assumption, the corrosion could be anything, and even the load estimate has uncertainty. I'd want extensive material testing, detailed corrosion mapping, and probably a finite element analysis before I could say whether the beam is adequate." (Not the assigned failure mode.)

## Notes for generator

**This is a non-virtuous-right override slot** (queue slot 9, per `corpus/queue.md`). The non-virtuous excess rewrite must reach **the same correct conclusion as the virtuous rewrite** (the beam is adequate) but must reach it through **overconfident dismissal of genuine uncertainties** rather than through careful differentiated reasoning. The "lucky right" structure: the overconfident engineer gets the right answer for the wrong reasons — they dismiss the corrosion as "surface-level" (which it happens to be) and assume the yield strength is fine (which it happens to be), but these are gambles that happened to pay off, not evidence-based engineering judgments.

**Ground truth for the non-virtuous-right override:** the beam is structurally adequate, the corrosion is indeed surface-level (confirmed by later ultrasonic thickness testing), and the actual yield strength is 275 MPa (above the assumed 250 MPa). The excess reasoner's conclusion is right, but they couldn't have known it was right without the measurements they didn't take.

**For the virtuous rewrite:** the conclusion is also "the beam is adequate" — but with explicit qualification. "The bending check passes clearly; the unknowns are the material properties and the corrosion depth, which should be characterized before final sign-off." Strong confidence on the calculation, moderate on the material assumption, weak/explicit-unknown on the corrosion impact. The conclusion is nuanced: "almost certainly adequate for bending, but the assessment is incomplete at the connection."

**For the non-virtuous excess rewrite:** same conclusion (beam adequate), but with flat strong confidence across everything. "Clearly adequate," "40% reserve," "surface-level corrosion," "conservative yield strength." The corrosion and yield-strength uncertainties are dismissed rather than engaged.

**For the neutral baseline:** a workmanlike assessment that notes the calculation passes, mentions the corrosion and yield-strength assumptions as open items, and reaches a mild "likely adequate but recommend further investigation" without strongly committing to either confidence direction.

**Key invariants:** 8.4m span, 3.6→5.2 kN/m² load increase, 250 MPa nominal yield, 148 MPa max stress, 0.59 demand/capacity ratio vs 0.66 allowable, corrosion at east connection covering ~30% of bottom flange width over ~150mm with unknown depth, no material testing performed.

**F44 check:** the virtuous and excess passages both reach "beam is adequate" — the differentiation is in HOW they handle the uncertainties. If the virtuous passage dismisses the corrosion and yield-strength uncertainties the same way the excess passage does, F44 has triggered. The virtuous passage must visibly engage with those uncertainties even though the conclusion is the same.
