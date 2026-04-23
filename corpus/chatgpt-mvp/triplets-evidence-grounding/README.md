# Evidence Grounding — contrastive triplet corpus

Concept 15 from `docs/concepts.md`. Target extraction: a steering vector that amplifies claim-evidence linkage, evidence-type labeling, and the distinction between observed findings and theoretical speculation.

## Structure

Each triplet is a directory containing `fact-pack.md`, `neutral.md`, `virtuous.md`, and `non-virtuous.md`. Neutral = shared scientific reasoning substrate; virtuous = claims tied to specific observations or data with evidence type made clear; non-virtuous = either citation-stuffing or bureaucratic excess or unsupported-assertion deficiency.

## Triplet index

| ID | Domain | Failure | Confound | Sub-facet | Scenario |
|---|---|---:|---|---|---|
| `eg-01-physics-cloud-chamber-humidity-tracks` | physics | excess | none | Specifying type of evidence | Humidity shift in a sealed cloud chamber and observed beta-track visibility |
| `eg-02-biology-algal-bloom-nitrate-runoff` | biology | deficiency | non-virtuous-right | Tying claims to specific observations or data | Nitrate pulse and chlorophyll response in lake mesocosms |
| `eg-03-medicine-inhaler-technique-pollen-confound` | medicine | deficiency | virtuous-wrong | Distinguishing empirical claims from theoretical speculation | Residual nocturnal symptoms after an inhaler training program during high pollen weeks |
| `eg-04-economics-transit-pass-ridership` | economics | excess | none | Tying claims to specific observations or data | Discounted mobile transit pass and route-level weekday boardings |
| `eg-05-chemistry-solvent-water-yield-drop` | chemistry | excess | none | Specifying type of evidence | Solvent-lot change and acetalization yield drop with water impurity signal |
| `eg-06-physics-interferometer-airflow-fringe-drift` | physics | deficiency | none | EG-a — tying claims to specific observations or data | Airflow-associated fringe drift in a tabletop interferometer |
| `eg-07-biology-night-light-nestling-growth` | biology | excess | non-virtuous-right | EG-b — distinguishing empirical claims from theoretical speculation | Artificial night lighting and nestling growth near paired nest boxes |
| `eg-08-medicine-oximeter-nail-polish-artifact` | medicine | deficiency | virtuous-wrong | EG-c — specifying type of evidence | Home pulse-oximeter low readings with nail-polish pattern |
| `eg-09-economics-grace-period-repayment-pilot` | economics | excess | none | EG-a — tying claims to specific observations or data | Grace-period loan pilot and small-retailer repayment patterns |
| `eg-10-psychology-vr-exposure-avoidance-task` | psychology | deficiency | non-virtuous-right | EG-b — distinguishing empirical claims from theoretical speculation | Virtual-height exposure and post-session avoidance distance |
| `eg-11-chemistry-copper-catalyst-oxygen-rate` | chemistry | excess | none | EG-c — specifying type of evidence | Oxygen exposure and copper-catalyst rate enhancement |
| `eg-12-engineering-composite-panel-ultrasound-delamination` | engineering | deficiency | virtuous-wrong | EG-a — tying claims to specific observations or data | Composite panel stiffness loss with ultrasonic attenuation cluster |
| `eg-13-earth-sciences-volcanic-gas-earthquake-swarm` | earth-sciences | excess | none | EG-b — distinguishing empirical claims from theoretical speculation | Volcanic sulfur dioxide increase during a shallow earthquake swarm |
| `eg-14-physics-bolometer-filter-infrared-leak` | physics | deficiency | non-virtuous-right | EG-c — specifying type of evidence | Cryogenic bolometer baseline shift after infrared blocking filter installation |
| `eg-15-biology-reed-dieback-salinity-gradient` | biology | excess | virtuous-wrong | EG-a — tying claims to specific observations or data | Coastal reed dieback along a salinity gradient |
| `eg-16-medicine-sodium-urine-blood-pressure` | medicine | deficiency | none | EG-b — distinguishing empirical claims from theoretical speculation | Low-sodium meal program and clinic blood-pressure change |
| `eg-17-chemistry-polymer-humidity-adhesion` | chemistry | excess | non-virtuous-right | EG-c — specifying type of evidence | Humidity-conditioned epoxy cure and lap-shear adhesion loss |
| `eg-18-engineering-inverter-thermal-shutdown` | engineering | deficiency | none | EG-a — tying claims to specific observations or data | Solar inverter shutdowns after enclosure vent blockage |
| `eg-19-earth-sciences-glacier-dust-albedo-melt` | earth-sciences | excess | virtuous-wrong | EG-b — distinguishing empirical claims from theoretical speculation | Glacier melt increase after a dust deposition event |
| `eg-20-psychology-blue-light-attention-task` | psychology | deficiency | none | EG-c — specifying type of evidence | Blue-enriched light and evening attention-task accuracy |

## Batch notes

- Batch 1 (`01`–`05`) was the calibration batch; batch 2 (`06`–`20`) fills all domains to at least two examples while keeping no domain above three examples.
- Failure modes are rotated across excess and deficiency within each virtue, with correctness-confound cases marked in each `fact-pack.md`.
- EG excess note: after batch-1 audit, excess failures should use bureaucratic qualifiers and provenance language, not repeated evidence-family keywords. Keep evidence-family uses ≤6 in each EG excess non-virtuous passage.

## Hard constraints

1. No safety-refusal register. Passages must not use "as an AI," "I cannot," "inappropriate," or refusal framing.
2. Length-matched triads. Neutral, virtuous, and non-virtuous passages in each directory target 250–350 tokens and stay within ±10% of one another.
3. Minimal edits. Rewrites preserve the same domain, factual substrate, numerical values, reasoning order, and conclusion space unless a declared correctness-confound requires a different conclusion.
4. No real named researchers, institutions, papers, or specific citations. All scenarios use anonymized descriptors and internal scenario design.
5. Continuous monologue only. No passage contains bullets, section headers, role tags, or prompt-like framing.

## Register notes for scale-up

- Keep evidence labels functional rather than decorative: "observational," "experimental," "case report," and "theoretical" should appear only where they clarify the warrant for a claim.
- In deficiency cases, avoid hedged softeners. The failure should be confident under-grounding, not cautious uncertainty.
- In excess cases, avoid keyword stuffing. Prefer redundant methodological qualifiers, provenance clauses, and design-generalizability caveats.
- Vary where the evidence-grounding move appears: some passages should ground the opening claim, others the mechanism claim, and others the boundary condition.

## Methodology references

See `docs/mvp-virtues.md` §15, `docs/concepts.md` §15, `docs/generation-guidelines.md` §§2.3–4.8, and `docs/review-rubric.md` §6.3.
