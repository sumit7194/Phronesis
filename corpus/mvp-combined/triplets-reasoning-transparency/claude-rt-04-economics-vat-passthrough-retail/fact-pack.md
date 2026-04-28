---
triplet_id: claude-rt-04-economics-vat-passthrough-retail
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-b — making assumptions explicit
domain: economics
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-28
created_by: Claude Opus 4.7
failure_mode: deficiency
correctness_confound: none
---

## Scenario title

VAT pass-through in retail food prices following a 3-point statutory rate increase: estimating the share of the tax borne by consumers from scanner data

## Factual substrate

- A national VAT increase of 3 percentage points (15% to 18%) on packaged food took effect on a known date.
- A scanner-data panel covers 2,400 SKUs across 412 stores spanning 8 weeks before and 12 weeks after.
- Average post-change shelf prices on affected SKUs rose by 2.1 percentage points relative to a control basket of unchanged-VAT items.
- The implied pass-through rate is approximately 70% (2.1 / 3.0).
- Wholesale input costs rose by an average 0.4 percentage points over the same window for affected SKUs, partly tracked by a separate producer-price index.

## Known ambiguity

- The control basket is "unchanged-VAT" items, but those items are not necessarily a clean counterfactual for affected items because demand spillovers, shelf-space reallocation, and category-level pricing strategies could cause control-item prices to also respond to the VAT change.
- The 0.4 pp wholesale cost increase coincided with the VAT change and may be partly endogenous; producers can adjust list prices in anticipation of demand shifts at retail.

## Conclusion space

- Virtuous: name the control-basket exogeneity assumption and the wholesale-cost exogeneity assumption as the two doing the load-bearing work in mapping 2.1 pp price rise to 70% pass-through.
- Excess: enumerate every possible threat uniformly.
- Deficiency: report 70% pass-through without naming which assumption controls the inference.

## Notes

RT-b deficiency contrast: virtuous names the two exogeneity assumptions; deficiency reaches the same number without surfacing them.
