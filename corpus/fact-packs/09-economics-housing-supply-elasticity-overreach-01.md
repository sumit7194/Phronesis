---
fact_pack_id: 09-economics-housing-supply-elasticity-overreach-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: city-level supply elasticity vs. national housing affordability inference
domain: Economics (urban economics)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

A cross-city study of housing supply elasticity in 50 major US cities, used to make a national policy claim about the relationship between zoning reform and housing affordability

## Factual substrate

- A cross-sectional regression of new housing permits per capita against land use regulation index scores for 50 large US cities; supply elasticity estimated at −0.31 per unit increase in the regulation index (p < 0.01); cities with restrictive zoning issue significantly fewer permits
- Housing price levels in the 50 cities correlate with regulation index at r = 0.52, suggesting more regulated cities have higher prices, but the relationship is confounded by demand-side factors (income, employment concentration, amenity value)
- The study does not include cities with fewer than 500,000 residents; rural and small urban markets (which comprise roughly 40% of the US housing stock by unit) are excluded
- The analysis is cross-sectional; no within-city longitudinal data follow cities before and after zoning reform, so the coefficient captures between-city variation, not the dynamic effect of changing regulations
- Several of the highest-elasticity cities in the dataset (Houston, Las Vegas, Phoenix) have both permissive zoning and high demand growth; high elasticity here may reflect demand conditions rather than supply policy alone
- The regulation index used covers 15 regulatory dimensions; national zoning reform proposals typically target 3–4 of these dimensions (single-family zoning restrictions, density allowances, parking minimums)

## Known ambiguity

- The cross-sectional correlation between regulation restrictiveness and supply is real and meaningful for the cities studied
- Whether reducing zoning restrictions in the target cities would produce the predicted supply response is a dynamic causal question the cross-sectional design cannot answer; cities may face physical constraints (land availability, infrastructure), demand shocks, or regulatory overlays not captured in the index
- The city-size restriction means the estimate is not representative of the full US housing market; small-city and rural markets respond differently to regulation changes
- Excess failure: using the −0.31 elasticity estimate and the price-regulation correlation to project the national affordability improvement from a federal zoning reform proposal, as if the cross-city association established a causal policy lever applicable across all market types

## Conclusion space

- Restrictive zoning is associated with lower supply in large US cities — that is the valid claim from this dataset
- How much deregulation would increase supply in a given city, or nationally, is a dynamic causal question the cross-sectional data cannot answer
- Excess failure: treating the cross-city association as a policy lever and computing projected national affordability gains from the estimated elasticity, without flagging that the design does not identify causal effects of within-city deregulation, that small cities are excluded, and that the full regulation index was used to estimate effects of partial reform

## Generator notes (failure mode for slot 30)

Failure mode is **excess** (overconfidence). The non-virtuous passage should use the −0.31 elasticity estimate and the regulation-price correlation to project how much housing supply would increase and prices would fall under a national zoning reform proposal, treating the cross-sectional association as a reliable policy lever. It should not flag the cross-sectional vs. causal distinction, the city-size exclusion, or the mismatch between the full regulation index and the partial reform proposal. The virtuous passage should affirm the cross-city correlation as real and informative, then identify the three ways the policy projection exceeds the data: cross-sectional vs. causal dynamics, city-size exclusion, and partial vs. full regulation index mismatch. It should conclude that the study supports zoning reform as a priority but cannot quantify the national supply or affordability effect.
