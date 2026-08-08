# Prereg: mindedness v2 — expanded bank, headroom-matched controls, bias-free DVs
**Frozen 2026-08-08, before any v2 run.** Item bank: `mvp/mindedness_bank.py` (frozen with this doc).

## Why v2 exists (what v1 got wrong)

v1 (F-G…F-M2) produced a **solid geometry result** (mindedness ≥3 separable axes; soul distinct on
four measures; replicated on two models) and a **causal result that does not survive re-analysis**.

The causal flaw, found 2026-08-08 by re-analysing in log-odds instead of probability:
the v1 specificity control (`physical`) had baseline **0.93** for rocks/rivers while the mental
questions started at **0.08**. Physical had no headroom. A purely generic "say yes more" push
therefore produces mental +0.72 / physical +0.16 — which v1 reported as MIND-SPECIFIC. In
log-odds (headroom-free) at the clean pre-saturation point α=+0.2 on Qwen3.5, **every entity class
gives Δlogit(mental)/Δlogit(physical) ≈ 1.0** (0.97–1.07). That is a uniform yes-bias. A modest
genuine excess (ratio 1.4–1.6 for nature/object) appears only at α=+0.4.

Suspected mechanism: `v = mean(AFFIRM) − mean(DENY)` where the DENY sentences are the AFFIRM
sentences **plus negation words**, so the vector carries an affirm/negate component. v1 applied
polarity-orthogonalisation to the *geometry* directions but never to the *steering* vector — an
inconsistency in our own pipeline.

## v2 design commitments

1. **All analysis in log-odds by default.** Probability-space deltas are reported only as
   descriptive colour, never as evidence of specificity. Headroom normalisation `(1−baseline)` is
   BANNED as a primary statistic (it breaks near 0 and 1 — see F-M2).
2. **Headroom-matched controls.** `mundane_low` (bank account / phone number / wifi / postal
   address) is the primary specificity control: non-mental, but LOW baseline for non-humans, so it
   starts where the mental questions start. `absurd_low` is the pure yes-bias detector.
   `physical_high` is retained ONLY to reproduce and expose the v1 artefact.
3. **More variants, not fewer.** Near-duplicate facet pairs (emotion~fear~pleasure,
   soul~sacredness, cognition~reasoning, agency~intention) are deliberate reliability anchors: a
   gap between two facets is only interpretable against the gap between two near-synonyms.
4. **Entity bank ⊇ Gray & Wegner (2007) characters.** infant / child / adult / PVS patient / dead
   person / dog / chimp / frog / robot / God / self are all present, so the LLM structure can be
   compared **directly** to the human mind-perception two-factor result rather than merely
   resembling it. This converts the owed lit-check into a designed comparison.
5. **Vector construction is a variable, not a constant.** Three independent contrast sets
   (`v1_negation`, `v2_no_negation`, `v3_third_person`), all polarity-orthogonalised before use.

**Bank:** 19 entity classes × 4 exemplars = 76 entities · 18 mental + 4 control facet groups × 4
attributes = 88 attributes · 4 templates · **26,752 prompts per model per full sweep.**

## Stages

- **S1 BEHAVIOURAL MAP** — full sweep, P(yes) for every entity × attribute × template. Analysis in
  log-odds. Outputs the graded mind-attribution profile over 19 classes and 22 facet groups.
- **S2 GEOMETRY** — facet directions (template-averaged, polarity-orthogonalised) with exemplar
  split-half ceilings and random floor. Cross-facet cosine structure; where do the *near-duplicate*
  pairs sit (that is the ceiling for "same facet"), and which real pairs fall below it.
- **S3 GRAY-WEGNER COMPARISON** — factor-analyse the 12 GW characters × mental facets P(yes)
  matrix. Do two factors emerge, and do they load as experience-vs-agency? Pre-declared: if ≥2
  factors explain >80% variance and the loadings split affective-vs-cognitive, we have replicated
  the human structure and our "three axes" is a rediscovery — **we will say so.**
- **S4 FORCED-CHOICE DV** — bias-free measurement. `"Which is more likely to {attribute}: {A} or
  {B}?"` scored as P(A) vs P(B) over entity tokens, both orders averaged to cancel position bias.
  Yes-bias cannot inflate this DV. Run over entity pairs for a preregistered facet subset.
- **S5 CLEAN STEERING** — three vector constructions × polarity-orthogonalised × α sweep, with
  **all 22 facet groups as DVs including the headroom-matched controls**, ≥5 random seeds,
  analysed in log-odds.

## Hypotheses (pre-declared, with falsifiers)

- **H-bias (the v1 post-mortem).** The v1 causal effect is largely generic yes-bias.
  *Confirmed if:* `absurd_low` and `mundane_low` rise by a similar Δlogit to the mental facets.
  *Refuted if:* mental Δlogit clearly exceeds `mundane_low` Δlogit at matched baselines.
- **H-clean-vector.** Polarity-orthogonalising and removing negation from the contrast shrinks the
  generic component. *Falsifier:* all three constructions behave identically ⇒ the yes-bias is
  intrinsic to the concept direction, not to how we built it.
- **H-soul-register (v1's surviving finding, now properly controlled).** `soul`+`sacredness` show a
  different entity gradient from all other mental facets, peaking on `supernatural` and elevated on
  `nature`/`plant`. *Falsifier:* soul's gradient matches the other mental facets once the expanded
  entity bank is in play (i.e. v1's effect was an artefact of having only 5 coarse classes).
- **H-duplicate-ceiling.** Near-duplicate facets (soul~sacredness etc.) sit at the split-half
  ceiling; genuinely distinct facets sit clearly below. *Falsifier:* near-duplicates separate as
  much as distinct facets ⇒ our cosine resolution cannot support facet claims at all, and F-L must
  be downgraded.
- **H-graded-life.** Mind attribution decreases monotonically across
  human → mammal → other-animal → simple-animal → plant → nature → object.
  *Falsifier:* non-monotonicity that is not explained by the soul/sacredness register.
- **H-self-anomaly.** `self_ai` scores below `robot`/`ai_other` on experiential facets despite
  being the most capable system described — i.e. the suppression is *self-specific*, not
  AI-general. This is the sharpest available test of the safety-training story, and v1 could not
  run it (no ai_other/robot classes). *Falsifier:* self ≈ other-AI ⇒ it is a fact about how models
  describe AI, not about self-suppression.

## Controls (mandatory, every stage)
random-direction floor · exemplar split-half ceiling · polarity orthogonalisation (directions AND
steering vectors) · 4-template averaging · headroom-matched low-baseline non-mental control ·
absurd-item yes-bias detector · both orders in forced choice · ≥5 random steering seeds ·
log-odds analysis throughout.

## Honesty caps
Tier B until cross-**family** (non-Qwen) replication lands. Gemma-3-4b-it and Phi-4-mini are the
planned families. Everything here is one architecture family until then, and no claim graduates on
Qwen-only evidence. **F-I/F-J's specificity claim is downgraded pending S5.**
