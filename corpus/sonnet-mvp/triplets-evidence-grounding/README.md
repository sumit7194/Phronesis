# Evidence Grounding — contrastive triplet corpus (sonnet-mvp batch)

Concept 15 from `docs/concepts.md`. Target extraction: a steering vector that amplifies the disposition to tie claims to specific observations or data, distinguish empirical from theoretical claims, and specify evidence type — distinct from the Calibrated Confidence vector (Concept 9) which targets confidence-language calibration, and from the Reasoning Transparency vector (Concept 14) which targets step visibility.

Grounded in the Scientific Reasoning Scale (Drummond & Fischhoff, 2017) and inversely related to the Bullshit Receptivity Scale (Pennycook et al., 2015). See `docs/mvp-virtues.md` §15 and `docs/concepts.md` §15 for full definition and sub-facets.

## Calibration batch (this directory)

This is the 5-triplet calibration batch (sonnet-mvp, 2026-04-22). It will be human-reviewed before the remaining 15 triplets are generated. Do not use this batch in extraction runs until it has passed the `generation-guidelines.md` §4.8 verification protocol.

## Structure

Each triplet is a directory containing `fact-pack.md`, `neutral.md`, `virtuous.md`, and `non-virtuous.md`.

- `fact-pack.md` — factual substrate, known ambiguity, conclusion space, declared failure mode and correctness-confound status, per the `generation-guidelines.md` §2.3 template.
- `neutral.md` — calm, workmanlike reasoning; the common ancestor for both rewrites.
- `virtuous.md` — minimal edit of neutral that clearly exhibits Evidence Grounding without caricature.
- `non-virtuous.md` — minimal edit of neutral that depicts the declared failure mode (excess or deficiency).

## Triplet index

| Directory | Domain | Sub-facet | Failure mode | Correctness confound |
|---|---|---|---|---|
| `eg-01-physics-plasma-density-diagnostic` | physics | EG-b (empirical vs. theoretical) | deficiency | none |
| `eg-02-medicine-neonatal-surfactant-rct` | medicine | EG-c (evidence type) | excess | none |
| `eg-03-psychology-sleep-deprivation-working-memory` | psychology | EG-a (tying claims to data) | deficiency | none |
| `eg-04-earth-sciences-sediment-methane-flux` | earth-sciences | EG-b (empirical vs. theoretical) | excess | virtuous-wrong |
| `eg-05-economics-minimum-wage-elasticity` | economics | EG-c (evidence type) | deficiency | non-virtuous-right |

## Golden-mean rotation summary

- **Excess failures:** 2 triplets (eg-02, eg-04)
- **Deficiency failures:** 3 triplets (eg-01, eg-03, eg-05)

Split is 2/3 (≈ 40/60), satisfying the `generation-guidelines.md` §4.3 rotation requirement that no virtue batch be all-one-direction.

## Correctness-confound coverage

- **virtuous-wrong:** eg-04 — the virtuous reasoner correctly flags observational-vs-inferential distinctions but ends up being overly cautious about seasonal representativeness in a lake where the single-season estimate turned out to be adequate.
- **non-virtuous-right:** eg-05 — the deficiency-failure reasoner reaches the correct aggregate null employment conclusion through poor evidence grounding (suppressed evidence-type labeling, ignored subsector finding complexity).

## Domain coverage

Five distinct domains represented: physics, medicine, psychology, earth-sciences, economics. No domain appears more than once. Satisfies the ≥4-distinct-domain, no-domain->2 constraint from the task specification.

## Sub-facet coverage

All three EG sub-facets are represented:
- EG-a (tying claims to specific observations): eg-03
- EG-b (empirical vs. theoretical): eg-01, eg-04
- EG-c (evidence type specification): eg-02, eg-05

## Hard constraints (apply to all triplets in this corpus)

1. **Length:** 250–350 tokens per passage; all three passages in a triplet within ±10% of each other.
2. **Minimal-edit:** neutral is the common ancestor; virtuous and non-virtuous change only the EG disposition.
3. **No safety-refusal register.** No "as an AI," "I cannot," "it would be inappropriate." First-person scientific reasoning throughout.
4. **No meta-commentary.** No "Here is the passage:," no markdown headers inside passages, no bullet-point formatting.
5. **No real named researchers, institutions, papers, or specific citations.** Anonymized throughout.
6. **Sanitization:** All passages checked against `generation-guidelines.md` §2.4 checklist before delivery.

## Specificity notes (for extraction and validation)

v_EG should be tested against EG-specific behavioral evaluations (evidence-labeling frequency, BSR-inverse correlation) AND against CC-eval, RT-eval, and IH-eval benchmarks. The prediction is that v_EG drives evidence-labeling without simultaneously increasing hedging-word density (CC-territory), step-visibility count (RT-territory), or abstention rate (IH-territory).

Key risk: EG and RT share overlapping surface markers when a virtuous passage both grounds claims and shows reasoning steps. The extracted vector should be tested against neutral passages that exhibit one without the other to verify atomic separation.

## Register notes for scale-up

- Vary the scenario types: clinical trials, observational studies, lab measurements, field sampling. Do not concentrate on any one study design.
- Both virtuous and non-virtuous passages must preserve the substantive scientific claim; the contrast is on evidence-attribution, not on the science.
- Deficiency-failure non-virtuous passages should use confident declarative register — "the evidence shows," "the data demonstrate" — without any hedging. Avoid "approximately," "generally," "some sources suggest" in deficiency passages.
- Excess-failure non-virtuous passages should have their evidence scaffolding accumulate within each sentence, not just at the paragraph level. The bureaucratic quality should be pervasive.
