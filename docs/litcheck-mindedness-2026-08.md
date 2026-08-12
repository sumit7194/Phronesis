# Lit-check: mindedness arc (done 2026-08-08, owed since prereg — late, as flagged)

Done while the v2 sweep ran. This is the check I should have done at prereg time per the 07-12
process fix. Recording what it changes.

## 1. Multi-dimensional mind attribution is a 20-year-old HUMAN result. Not our discovery.

- **Gray, Gray & Wegner (2007, Science), "Dimensions of Mind Perception."** Factor analysis over
  13 characters → **two** dimensions: **Experience** (hunger, fear, pain, pleasure, consciousness)
  and **Agency** (self-control, morality, memory, planning, communication, thought). God scores
  high agency / near-zero experience; robots likewise; babies the reverse.
- **Malle (2019), "How Many Dimensions of Mind Perception Really Are There?"** Expanded item pool,
  four studies → **three** dimensions: **Affect**, **Moral & Mental Regulation**, and **Reality
  Interaction**. Explicitly a critique of the two-factor count; notes one-, three-, and
  five-dimensional models have all been proposed.

**Consequence for us.** Our F-L "mindedness is three axes, not one" recapitulates a well-established
human finding. Our {pain,emotion} ≈ GW-Experience ≈ Malle-Affect; our {cognition,agency} ≈
GW-Agency ≈ Malle's Regulation + Reality-Interaction. **The multi-dimensionality claim is NOT novel
and must not be presented as a discovery.** What may still stand: that it appears in an LLM's
*internal geometry* (direction cosines, ceiling-bracketed) and not merely in its output ratings.

## 2. Our SOUL axis is in neither framework — the one plausibly novel piece

Neither GW's two dimensions nor Malle's three include a spiritual/soul/sacredness factor. Both
item pools are *mental-capacity* items; "has a soul" is a metaphysical attribution, not a capacity.
So **F-K/F-L's soul axis is not a rediscovery of either** — and its behaviour (nature scores 0.74
on soul vs 0.01–0.11 on all other mental facets; decodes to religious vocabulary; nature becomes
geometrically collinear with animals only under soul) has no obvious counterpart in the human
dimensional literature. **This is where novelty, if any, lives.** v2's `sacredness` facet was added
before this check and turns out to be well-motivated.

## 3. Kim et al. 2607.28607 — what they did and did NOT do

Verified from the full text (not the abstract):
- **Models: Llama-3-8B-IT, Gemma-2-2B-IT, Gemma-2-9B-IT.** No Qwen. → **our Qwen3 / Qwen3.5 runs
  are a genuine cross-FAMILY replication of their central claim**, which is a real contribution
  independent of everything else.
- **They had a "soul" item** — but only in the *self*-attribution battery (agent / conscious /
  sentient / person / soul, 0–10). For *entities* they used a modified IDAQ.
- **They aggregated IDAQ facets into category-level means.** Quote from the extraction: results are
  "presented as category-level means rather than showing how each mental attribute type behaves
  differently within categories," and the self-battery traits "are treated as outcomes independent
  of the IDAQ entity categories—not crossed with them."
  → **They never ran the facet × entity-category interaction.** That is exactly F-K. So the soul
  dissociation for natural objects is not something their paper reports, even though they had the
  ingredients.
- **Their placebo control is subject-matched physical/functional properties** ("…have
  durability?"), reported as no significant shift (Δ𝒮=+0.036±0.057, t=1.23, p=.228).
  **They do not report placebo baselines.** Since durability-of-a-mountain is plausibly near
  ceiling on a 0–10 scale, **the headroom confound we found in our own replication (v1 → v2) may
  apply to their placebo too** — a null shift on an item with no headroom is weak evidence of
  specificity. Stated as a hypothesis we cannot verify from the paper, not as a claim about their
  result. Their scale is 0–10 Likert rather than our binary P(yes), so the ceiling geometry differs
  and this needs care before being repeated anywhere public.

## 4. Adjacent work found

- Exposure to LLMs increases human mind-attribution to them on both GW dimensions
  (Springer, *Int J Soc Robotics* 2025) — humans perceiving LLMs, the mirror of our question.
- "Robots, Chatbots, Self-Driving Cars: Perceptions of Mind and Morality Across Artificial
  Intelligences" (arXiv 2502.18683) — relevant to v2's H-self-anomaly, again human-side.
- IIT/ToM probing of LLM internal states (ScienceDirect 2025) — different method, adjacent question.

## 5. Actions taken

1. **S3 extended to test Malle's three-dimensional model as well as GW's two** — comparing against
   only the two-factor model would have been testing the weaker of the two live hypotheses.
2. Positioning fixed: the arc's honest framing is **(a)** cross-family replication of Kim et al. on
   Qwen, **(b)** the facet × entity interaction they had the ingredients for but did not run, and
   **(c)** a soul/spiritual axis absent from both human dimensional frameworks. The bare
   "mindedness is multi-dimensional" claim is retired.
3. STATE.md updated.

## Sources
- Gray, Gray & Wegner (2007), *Science* — https://www.science.org/doi/10.1126/science.1134475
- Malle (2019) — https://research.clps.brown.edu/SocCogSci/Publications/Pubs/Malle_2019_How_Many_Dimensions.pdf
- Kim et al., arXiv 2607.28607 — https://arxiv.org/abs/2607.28607
- Attributing Mind to LLMs — https://link.springer.com/article/10.1007/s12369-025-01337-z
- Perceptions of Mind and Morality Across AIs — https://arxiv.org/pdf/2502.18683

---

# Round 2 lit-check — 2026-08-09 (periodic, at user's standing request)
Done after the claims changed substantially. **This is now a recurring obligation, not a one-off.**

## Already published — do NOT claim as ours
- **Base vs instruct on mind attribution.** Kim et al. 2607.28607 do this (Llama-3-8B, Gemma-2-2B/9B).
  Our Qwen base-vs-instruct is a **cross-family replication of their design**, not a new design.
- **Entity-class breakdown.** They report safety-ablation coefficients per class: chatbots β=2.28,
  robots 2.13, non-animal natural 2.32, animals 1.62, **humans only 0.738 (p=.050)**.
  → **This is our F-T4 pattern from the opposite direction.** They remove safety and everything
  low-mind rises while humans barely move; we watched post-training add it and everything low-mind
  fall while humans stay flat. **"Reframing the entanglement claim" was too strong and is
  downgraded.** What survives as ours: the Qwen family, the observation that the *self* is
  suppressed **less** than plants/rocks, and that the two Qwen generations moved the boundary in
  **opposite directions** — the last of which does bear on their framing, since it shows the
  direction is not intrinsic to safety tuning.
- **New paper we had not seen:** [Theory of Mind and Self-Attributions of Mentality are Dissociable
  in LLMs](https://arxiv.org/html/2603.28925) — reports an "AI-centric bias": models over-attribute
  mind to technological artefacts and under-attribute to non-human animals. Adjacent to our
  self-vs-ai_other results. Read before any writeup.

## NOT covered — still ours
- **Moral patiency.** Verified from the full text: the paper "focuses exclusively on mental state
  attribution... does not separately examine moral patiency or moral status." Our capacity-loss
  manipulation (`human_edge`) and the finding that moral standing survives when every capacity is
  gone have no counterpart there. **This is the strongest surviving claim and it is uncovered.**
- **Speaker framing.** "Does not examine chat templates, speaker framing effects, or whether
  first-person language triggers human-like readings." F-R (bare-text "I" reads as a human) and the
  speaker-frame test are uncovered.

Both survivors came from the user's suggestions — the expanded entity bank that added `human_edge`,
and the speaker-frame test.

## Standing rule
Re-run a check **whenever a claim changes materially**, not only at prereg. Two rounds so far have
each retired something and protected something; the cost is ~10 minutes.

---

## Round 3 — 2026-08-12, triggered by two materially changed claims
CLAUDE.md requires a re-check whenever a claim changes materially. Two did today.

### Claim 1: "the steerable mind-direction is pretrained; post-training amplifies ~2x" (F-AR)
**Direct prior art, and it is close.** *Tracing Persona Vectors Through LLM Pretraining*,
arXiv **2605.13329**. Their finding: persona directions form during pretraining — "within 0.22% of
OLMo-3 pretraining" — and remain effective for steering the fully post-trained instruct models.
Their phrasing for what post-training does is **"post-training only tunes its volume"**, which is
the same claim as our "amplification, not creation", arrived at independently and stated better.

They also test two families (OLMo-3-7B, Apertus-8B) and report **family differences** — early
vectors go "nearly ineffective" for one trait on Apertus. That parallels our family split.
They use random and shuffled controls.

**Consequence for us:** F-AR is a **replication of a known pattern in a different domain** —
mind attribution and moral standing rather than persona traits, on Qwen3-4B and OLMo-2-1B rather
than OLMo-3 and Apertus. F-AR never claimed novelty, so nothing is retracted. But the honest
framing is now explicit: we independently reproduced a published result on our own hardware, which
is worth having and is not a discovery. It also *raises* our confidence in the finding, since two
independent setups in different domains agree.

### Claim 2: "protection tracks experience, blame tracks agency" (F-AK/F-AN)
**Long-established, as already recorded.** Gray, Gray & Wegner (2007) is the two-factor source, and
the mapping we "found" is textbook: *experience qualifies entities as moral patients, agency
qualifies them as moral agents*. Our F-AK already labelled this as recovering Gray & Wegner rather
than discovering anything, which was the right call.

Adjacent work worth knowing: *Robots, Chatbots, Self-Driving Cars: Perceptions of Mind and Morality
Across Artificial Intelligences* (arXiv 2502.18683) covers the entity classes we use.
*The Moral Mind(s) of Large Language Models* (arXiv 2412.04476). *Tracing Moral Foundations in LLMs*
(arXiv 2601.05437).

### What is NOT covered by anything found
- **`human_culpable` at the bottom of the scale.** No hit describes testing whether a *culpable
  human* falls below corporations and AI on a protect-minus-blame measure. Our P5 test appears not
  to be a re-run of anything, though the framework it sits in is fully established.
- **The format-gate result** (a family answers in one prompt format and fails in another, and the
  gate must therefore be a chooser). No hit; likely folklore rather than a publication.

### Score for this round
One claim substantially anticipated (and confirmed by it), one already correctly attributed, one
sub-result apparently untouched. Ten minutes. Same value as the previous two rounds: it did not
kill anything, it correctly located what we did relative to what exists.
