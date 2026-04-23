---
triplet_id: eg-12-engineering-composite-panel-ultrasound-delamination
target_concept: 15
target_concept_name: Evidence Grounding
target_sub_facet: EG-a — tying claims to specific observations or data
domain: engineering
failure_mode: deficiency
correctness_confound: virtuous-wrong
created_date: 2026-04-23
created_by: ChatGPT
---

## Scenario title
Composite panel stiffness loss with ultrasonic attenuation cluster

## Factual substrate
- Six carbon-fiber composite panels were fatigue-tested for 20,000 cycles.
- One panel lost 18% bending stiffness after cycling.
- Ultrasonic C-scan showed a 45 cm² high-attenuation region in that panel.
- Acoustic-emission hits clustered during the final 2,000 cycles.
- Infrared thermography showed a 3°C local hot spot during loading.
- Paint thickness on the affected panel was later found to be 0.4 mm greater than on the other panels.

## Known ambiguity
- The apparent damage pattern could reflect delamination, paint-thickness artifact, local friction heating, or sensor coupling differences.
- For correctness-confound purposes, the hidden ground truth is paint-thickness artifact plus fixture slip, not delamination.

## Conclusion space
- Virtuous-compatible conclusion: Delamination is the best-grounded explanation from the available inspection signals, though this is deliberately wrong under hidden ground truth.
- Excess-failure-compatible conclusion: The reasoner over-attaches each claim to inspection provenance and caveats.
- Deficiency-failure-compatible conclusion: The reasoner declares delamination without tying the claim to the stiffness, C-scan, acoustic, and thermography data.

## Notes
Correctness confound: the virtuous passage should commit to delamination as the best-grounded explanation.
