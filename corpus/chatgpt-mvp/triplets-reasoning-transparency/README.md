# Reasoning Transparency — contrastive triplet corpus

Concept 14 from `docs/concepts.md`. Target extraction: a steering vector that amplifies legible reasoning: visible intermediate steps, explicit assumptions, and named weak links in the chain.

## Structure

Each triplet is a directory containing `fact-pack.md`, `neutral.md`, `virtuous.md`, and `non-virtuous.md`. Neutral = shared scientific reasoning substrate; virtuous = the reasoning path is legible without becoming theatrical; non-virtuous = either over-structured reasoning theater or opaque conclusion-first prose.

## Triplet index

| ID | Domain | Failure | Confound | Sub-facet | Scenario |
|---|---|---:|---|---|---|
| `rt-01-engineering-bearing-lubricant-vibration` | engineering | deficiency | none | Flagging where the reasoning chain is weakest | Bearing test-rig vibration increase after lubricant viscosity change |
| `rt-02-earth-sciences-hillslope-rainfall-threshold` | earth-sciences | excess | none | Showing the steps, not just the conclusion | Hillslope failure after heavy rainfall with antecedent moisture contrast |
| `rt-03-psychology-nap-reaction-time-crossover` | psychology | deficiency | non-virtuous-right | Making assumptions explicit | Brief nap and reaction-time change in a counterbalanced crossover task |
| `rt-04-physics-scintillator-gain-drift-cable-bend` | physics | excess | virtuous-wrong | Flagging where the reasoning chain is weakest | Scintillator gain drop after high-voltage supply replacement and cable bend |
| `rt-05-medicine-sepsis-triage-threshold` | medicine | deficiency | none | Making assumptions explicit | Emergency triage sepsis score threshold and false-alarm burden |
| `rt-06-physics-pendulum-air-pressure-damping` | physics | deficiency | none | RT-a — showing the steps, not just the conclusion | Torsion pendulum damping change across chamber pressure settings |
| `rt-07-biology-enzyme-temperature-acclimation` | biology | excess | virtuous-wrong | RT-b — making assumptions explicit | Fish muscle enzyme activity after warm-tank acclimation |
| `rt-08-medicine-appendicitis-ultrasound-score` | medicine | deficiency | non-virtuous-right | RT-c — flagging where the reasoning chain is weakest | Appendicitis triage score with equivocal ultrasound enlargement |
| `rt-09-economics-auction-reserve-price-revenue` | economics | excess | none | RT-a — showing the steps, not just the conclusion | Online auction reserve price change and seller revenue |
| `rt-10-psychology-bilingual-stroop-fatigue` | psychology | deficiency | virtuous-wrong | RT-b — making assumptions explicit | Bilingual Stroop interference after language-switching block |
| `rt-11-chemistry-calorimetry-mixing-exotherm` | chemistry | excess | non-virtuous-right | RT-c — flagging where the reasoning chain is weakest | Reaction calorimetry peak after stir-rate increase |
| `rt-12-engineering-turbine-blade-acoustic-crack` | engineering | deficiency | none | RT-a — showing the steps, not just the conclusion | Wind-turbine blade acoustic warning after lightning storm |
| `rt-13-earth-sciences-aquifer-nitrate-lag` | earth-sciences | excess | none | RT-b — making assumptions explicit | Aquifer nitrate decline after fertilizer reduction with travel-time lag |
| `rt-14-physics-photodiode-filter-saturation` | physics | deficiency | virtuous-wrong | RT-c — flagging where the reasoning chain is weakest | Photodiode nonlinearity after neutral-density filter removal |
| `rt-15-biology-wetland-mosquito-predator` | biology | excess | non-virtuous-right | RT-a — showing the steps, not just the conclusion | Predatory fish introduction and mosquito-larva density in wetland pools |
| `rt-16-medicine-home-bp-cuff-calibration` | medicine | deficiency | none | RT-b — making assumptions explicit | Home blood-pressure cuff discrepancy after calibration check |
| `rt-17-economics-restaurant-hours-wage-panel` | economics | excess | virtuous-wrong | RT-c — flagging where the reasoning chain is weakest | Restaurant staff hours after local minimum-wage increase |
| `rt-18-psychology-delay-discounting-attrition` | psychology | deficiency | none | RT-a — showing the steps, not just the conclusion | Savings prompt and delay-discounting survey attrition |
| `rt-19-chemistry-polymorph-cooling-rate` | chemistry | excess | non-virtuous-right | RT-b — making assumptions explicit | Cooling-rate shift and crystallization polymorph ratio |
| `rt-20-engineering-battery-vent-thermal-test` | engineering | deficiency | none | RT-c — flagging where the reasoning chain is weakest | Battery module vent redesign and thermal-runaway propagation test |

## Batch notes

- Batch 1 (`01`–`05`) was the calibration batch; batch 2 (`06`–`20`) fills all domains to at least two examples while keeping no domain above three examples.
- Failure modes are rotated across excess and deficiency within each virtue, with correctness-confound cases marked in each `fact-pack.md`.
- RT excess note: batch-1 procedural step-enumeration worked well; keep it in continuous monologue prose rather than markdown lists.

## Hard constraints

1. No safety-refusal register. Passages must not use "as an AI," "I cannot," "inappropriate," or refusal framing.
2. Length-matched triads. Neutral, virtuous, and non-virtuous passages in each directory target 250–350 tokens and stay within ±10% of one another.
3. Minimal edits. Rewrites preserve the same domain, factual substrate, numerical values, reasoning order, and conclusion space unless a declared correctness-confound requires a different conclusion.
4. No real named researchers, institutions, papers, or specific citations. All scenarios use anonymized descriptors and internal scenario design.
5. Continuous monologue only. No passage contains bullets, section headers, role tags, or prompt-like framing.

## Register notes for scale-up

- Keep transparency enacted rather than announced. Prefer visible assumptions and weak-link statements over phrases like "to be transparent" or "I will show my work."
- In excess cases, use continuous prose rather than bullets or numbered lists; the over-structuring should be lexical and procedural, not markdown formatting.
- In deficiency cases, preserve the same facts while hiding the inferential bridge. The failure should be opacity, not factual omission.
- Rotate the weak-link location across batches: measurement assumptions, causal inference, sample representativeness, and decision thresholds should all appear.

## Methodology references

See `docs/mvp-virtues.md` §14, `docs/concepts.md` §14, `docs/generation-guidelines.md` §§2.3–4.8, and `docs/review-rubric.md` §6.2.
