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
