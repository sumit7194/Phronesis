---
triplet_id: rt-09-economics-auction-reserve-price-revenue
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-a — showing the steps, not just the conclusion
domain: economics
failure_mode: excess
correctness_confound: none
created_date: 2026-04-23
created_by: ChatGPT
---

## Scenario title
Online auction reserve price change and seller revenue

## Factual substrate
- A platform tested higher reserve prices on 1,200 used-equipment auctions.
- Sale probability fell from 74% to 61% with the higher reserve.
- Average sale price among completed sales rose from 430 to 515 credits.
- Average revenue per listing rose from 318 to 314 credits after accounting for unsold listings.
- Relisting fees averaged 9 credits per unsold listing.
- Seller mix was similar across the two reserve-price groups.

## Known ambiguity
- Higher reserves raise prices conditional on sale but reduce sale probability and add relisting costs.
- The net revenue change is small and slightly negative after accounting for unsold listings.

## Conclusion space
- Virtuous-compatible conclusion: Higher reserves increased completed-sale prices but did not improve average listing revenue once sale probability and fees are considered.
- Excess-failure-compatible conclusion: The reasoner performs excessive stepwise arithmetic for a simple expected-revenue comparison.
- Deficiency-failure-compatible conclusion: The reasoner jumps to a revenue conclusion without showing the conditional-price versus sale-probability tradeoff.

## Notes
The non-virtuous passage depicts excess.
