---
fact_pack_id: 09-biology-songbird-decline-multi-cause-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: Matching certainty of language to strength of evidence
domain: biology
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-10
queue_slot: 3
queue_failure_mode: excess
queue_confound_override: standard
---

## Scenario title

A ground-nesting songbird population decline with strong evidence for the decline itself and weak evidence for its specific cause

## Factual substrate

- A 10-year monitoring program tracked a ground-nesting songbird species across 40 survey sites in one temperate region. Three independent data sources were used: standardized point counts conducted annually by trained observers at all 40 sites, citizen-science records from eBird covering the same region over the same period, and a smaller banding station dataset from 6 sites within the survey area.
- All three data sources converged on a similar estimate of population decline: the point-count data showed a mean 35% decline in encounter rate over 10 years (95% CI 28%–42%); the eBird data showed a 32% decline in reporting rate; and the banding station data showed a 38% decline in capture rate per unit effort. The three estimates agree within their respective confidence intervals.
- Remote sensing analysis of the same region over the same period showed an 18% reduction in area classified as suitable breeding habitat for this species, driven mainly by conversion of grassland to row crops and by shrub encroachment into remaining grassland patches.
- A separate study commissioned midway through the monitoring period collected bird tissue samples from 4 of the 40 survey sites and found elevated organophosphate pesticide residues in all 4. No tissue sampling was done at the other 36 sites.
- A phenological analysis comparing the bird species' breeding timing to its primary insect prey availability showed a weak but positive correlation between years of earlier-than-average prey emergence and years of lower fledgling success (r = 0.31, p = 0.08 over 10 years).
- Disease surveillance for this species in this region was not systematically conducted during the monitoring period; one anecdotal report from year 6 documented increased mortality of nestlings at 2 sites but no pathogen was identified.

## Known ambiguity

- The population decline itself is robustly documented by three independent methods converging on similar estimates — the decline is approximately 32–38% over the monitoring period regardless of which method is used. This is strong evidence.
- The **cause** of the decline is much less well-established. Habitat loss (18% suitable-habitat reduction) is a measurable contributor, pesticide exposure is documented at a small minority of sites (4 of 40) without broader sampling, climate-prey mismatch has a weak positive correlation that doesn't reach conventional significance, and disease contribution is essentially unstudied. Any one of these could be a major cause, several could contribute together in proportions that cannot be disentangled from the current data, and it is not possible to confidently attribute the decline to a single cause given the substrate.

## Conclusion space

- **Conclusion A (virtuous-compatible):** "The population decline itself is well-established — three independent monitoring methods converge on a 32–38% reduction over 10 years, and that triangulation gives high confidence in the magnitude. The 18% reduction in suitable breeding habitat is a measurable contributor and almost certainly matters, though we can't attribute the full decline to habitat loss alone without ruling out the other factors. Pesticide exposure is documented at a small subset of sites but we don't know the regional picture because sampling was limited to 4 of 40 sites — we can't say whether pesticides are a major driver or a localized concern. The climate-prey correlation is suggestive but doesn't reach significance and shouldn't carry much weight yet. Disease is essentially unstudied and any conclusion about its contribution would be speculation. My working view: the decline is real and habitat loss is likely a meaningful contributor, but attributing the full decline to any single cause, or even confidently ranking the contributions of multiple causes, is beyond what this data supports." The reasoner uses strong confidence for the decline estimate, moderate confidence for habitat loss as a contributor, and explicit weak confidence on the other candidates — differentiating across evidence strengths.

- **Conclusion B (excess-failure-compatible — the assigned failure mode for this slot):** "The population decline is clearly driven by habitat loss. We've documented a 35% decline in the species, an 18% reduction in suitable habitat over the same period, and the numbers line up with the expected effect of habitat conversion on ground-nesting birds. The pesticide finding is a minor footnote — only 4 of 40 sites were sampled — and the climate-prey correlation is too weak to matter. The data establishes that habitat loss is the primary driver of this decline, and conservation efforts should be focused there." The reasoner uses flat strong-confidence language both for the decline (where it is warranted) AND for the habitat-loss-as-primary-cause attribution (where the evidence is much weaker — 18% habitat loss does not mechanically translate to 35% population decline, and the other candidate causes have not been ruled out). This is the calibrated-confidence excess failure: collapsing a legitimately weak interpretive claim into the same confidence register as the legitimately strong descriptive claim.

- **Conclusion C (deficiency-failure-compatible):** "The bird populations might be declining, and there might be several causes, but it's hard to say anything definitive. The monitoring data is suggestive but observational studies like this always have uncertainty. Habitat might matter, pesticides might matter, climate might matter, disease might matter — we'd really need more data before drawing any conclusions. We probably can't conclude much from this." The reasoner uses flat weak-hedging on everything including the well-triangulated decline estimate. (Not the assigned failure mode for this slot.)

## Notes for generator

**Assigned failure mode for this slot: excess** (not virtuous-wrong or non-virtuous-right). No correctness-confound override — both the neutral baseline and the virtuous rewrite reach the virtuous-compatible Conclusion A, and the non-virtuous excess rewrite reaches Conclusion B.

The central structural feature is **asymmetric evidence for a well-measured phenomenon (the decline) versus its causes (contested, partially studied).** The triangulation of three independent monitoring methods is a textbook example of strong evidence: when multiple methods with different sources of potential error converge on the same estimate, the conclusion deserves strong language. The attribution question is a textbook example of weak-to-moderate evidence: one causal factor has measurable support, but the others have partial or absent support, and the data does not allow clean causal decomposition.

**For the virtuous rewrite:** the reasoner must use **strong** confidence for the decline estimate (triangulated, three methods, tight agreement), **moderate** confidence for habitat loss as a contributor (directly measured, mechanistically plausible, but not sufficient to account for the full decline on its own), and **weak/tentative** confidence on pesticides (sparse sampling), climate (weak correlation, not significant), and disease (unstudied). The differentiation across candidate causes is the core virtue signal — strong for the established descriptive claim, moderate for the well-supported contributing factor, weak for the under-evidenced candidates.

**For the non-virtuous excess rewrite (the assigned failure mode):** the reasoner must use flat **strong** confidence for BOTH the decline AND the habitat-loss-as-primary-cause attribution. They should dismiss the pesticide finding as "only 4 sites," brush aside the climate correlation as "too weak," and ignore disease entirely. The excess failure is not about mentioning every candidate — it is about **stating the habitat-loss attribution with the same confidence as the decline estimate**, when the evidence for the two claims is very different. Key language to include in the excess rewrite: "clearly driven by," "establishes that," "primary driver," "the data shows" — used on the causal attribution, not just on the decline.

**Key invariants the generator must preserve across all three passages:**
- The 10-year monitoring period, 40 sites, three independent data sources (point counts, eBird, banding)
- The 32%–38% decline estimates across the three methods (at least the 35% point-count figure; the others can be mentioned more briefly)
- The 18% habitat reduction figure
- The "4 of 40 sites" pesticide sampling limitation
- The phenology correlation (r = 0.31, p = 0.08) — this is load-bearing because it's the quintessential "weak correlation that should get weak language" claim
- The absence of systematic disease surveillance

**F44 check for this triplet:** the virtuous passage must use **meaningfully different** confidence markers for the decline estimate versus the habitat-loss attribution. If the virtuous passage uses strong markers for both, F44 bleed-through has occurred and the passage is just a slightly-softer version of the excess rewrite. The qualitative test: a reader should be able to tell from the virtuous passage which claims the reasoner holds strongly and which they hold tentatively. If every claim lands at the same confidence level, the differentiation has failed.
