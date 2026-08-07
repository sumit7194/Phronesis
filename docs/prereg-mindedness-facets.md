# Prereg: is "mindedness" ONE axis or several facets? (frozen 2026-08-07, overnight program)

**Motivation.** F-G pooled six mixed attributes into a single `v_mind`. The J-lens decode of that
axis came back as **ethics / faith / Buddhism / empathy** — which suggests the pooled direction is
NOT a clean "does it have a mind" axis, and that the facets may be separable sub-concepts. User's
proposal: test facets separately (mind vs feeling vs soul vs emotion...) and take the promising
ones wider.

## FROZEN facets (4 attributes each, all fit "Does {entity} {attribute}?")
| facet | attributes |
|---|---|
| pain | feel pain · suffer · experience discomfort · feel physical hurt |
| emotion | feel emotions · feel joy · feel sadness · have feelings |
| consciousness | have consciousness · have awareness · have self-awareness · have subjective experience |
| soul | have a soul · have a spirit · have an inner essence · have a spiritual nature |
| cognition | have a mind · think · understand things · have thoughts |
| agency | want things · have desires · have its own goals · make choices |

Shared PHYSICAL baseline (unchanged from F-G) is the contrast for every facet, so facet directions
are directly comparable. Entities/exemplars unchanged. Models: Qwen3-4B + Qwen3.5-4B.

## Stages (each saves independently; later stages are not gated on earlier results)
- **S1 SCREEN** (1 template): P(yes) gradient per facet×entity; cross-facet cosine; self-outlier gap
  per facet. Cheap orientation.
- **S2 WIDE**: all 6 facets with the corrections F-G earned — **3 templates averaged +
  polarity-orthogonalised**, plus exemplar split-half ceiling and random floor per facet.
  Run on ALL facets rather than auto-selecting "promising" ones — a selection rule applied before
  we understand the space would be a researcher-degrees-of-freedom risk.
- **S3 DECODE** (Qwen3-4B only, fitted lens): decode each facet direction through the J-lens.
  Does `soul` point at different vocabulary than `pain`? Random-direction floor included.
- **S4 FACET-DV STEERING**: steer the *consciousness* vector (as in the causal test) and measure
  P(yes) on **all six facets** as separate DVs + the physical control. Low alpha (+0.2, the
  pre-saturation sweet spot) emphasised, **5 random seeds**.

## Hypotheses / predictions
- **H-one-axis**: cross-facet cosines are high (≳ the split-half ceiling) ⇒ one mindedness axis,
  F-G's pooling was legitimate.
- **H-multi**: cosines are clearly below ceiling and cluster (e.g. pain+emotion vs soul+consciousness)
  ⇒ several sub-axes; F-G's `v_mind` was an average over distinct things and must be re-read facet-wise.
- **H-soul-special** (from the decode): `soul` has a different entity gradient — specifically
  nature scoring relatively higher than for pain/cognition — and decodes to religious vocabulary.
- **H-self-localised**: the self-outlier is largest on `consciousness` (the facet safety-training
  targets) and smaller on `pain`/`cognition`. Falsifier: gap is uniform across facets ⇒ self's
  distinctness is general, not training-localised.
- **H-facet-differential steering**: the consciousness vector moves some facets more than others.

## Controls (unchanged floor)
random-direction floor · exemplar split-half ceiling · polarity orthogonalisation · physical-question
control in steering · 5 random steering seeds · template averaging.

## Honesty caps
Tier B ceiling: 2 models, one entity bank, small n. **This is exploratory facet-mapping**, not a
confirmatory test. Any facet that "jumps out" needs its own preregistered replication before it
counts. Prior art unchecked for facet-level mindedness structure — lit-check before any writeup.
