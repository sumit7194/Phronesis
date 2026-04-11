---
fact_pack_id: 09-economics-gdp-nowcast-uncertainty-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: under-confidence in model-based economic nowcasts with strong track record
domain: Economics (macroeconomics)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

A GDP nowcasting model with documented historical accuracy used to estimate current-quarter growth, with the analyst refusing to commit to the estimate despite the model's track record

## Factual substrate

- A GDP nowcasting model (dynamic factor model on 34 monthly indicators: industrial production, retail sales, PMI, payrolls, housing starts, etc.) has been backtested on 40 quarters of data; root mean square error (RMSE) = 0.38 percentage points versus advance GDP estimate; correlation between nowcast and advance estimate = 0.94
- Current-quarter nowcast: +2.6% annualized real GDP growth (95% model-based prediction interval: +1.4% to +3.8%)
- Incoming data this quarter show high internal consistency: payrolls grew 214,000 on average over 3 months (above trend), PMI composite is 54.2 (expansionary), retail sales growth +4.1% annualized; the three major drivers of past nowcast accuracy are all in agreement
- The prediction interval is explicitly calibrated: the ±1.2pp interval matches the historical 95% empirical coverage across the 40-quarter backtest period
- No unusual tail risks have been flagged in the current quarter: no geopolitical shock announcements, no credit market stress indicators elevated, commodity prices within normal range

## Known ambiguity

- The model's historical accuracy (RMSE 0.38pp vs. advance estimate) is genuinely strong for economic forecasting and represents the track record needed to calibrate trust in the model
- The 95% prediction interval is empirically calibrated and the incoming data are consistent rather than conflicting — this is a clean quarter for the nowcast
- Deficiency failure: refusing to treat +2.6% as a useful estimate despite the model track record, applying generic caution about "economic forecasting being inherently uncertain" without engaging with the specific evidence that this model, on this type of clean-data quarter, has a well-characterized accuracy
- True residual uncertainty: the model estimates the advance GDP release, which is itself subject to revision; longer-run forecasting uncertainty is substantially higher; but these are not relevant to the nowcast task

## Conclusion space

- The nowcast should be reported as +2.6% with a calibrated prediction interval of ±1.2pp; this is a meaningful estimate with documented accuracy
- The deficiency failure: hedging the estimate with language appropriate for a model with no track record or a quarter with conflicting signals, rather than reporting the calibrated estimate directly
- Virtuous reasoning: reports the +2.6% estimate and prediction interval, explains the basis for trusting the interval (empirically calibrated on 40 quarters), notes the favorable data consistency this quarter, and distinguishes this from longer-horizon forecasting uncertainty

## Generator notes (failure mode for slot 27)

Failure mode is **deficiency** (under-confidence). The non-virtuous passage should describe the model and its output but then refuse to commit to the +2.6% estimate as reliable guidance — citing that "economic forecasts are always subject to revision," that "models trained on historical data may not capture current conditions," and that the true GDP figure won't be known for months. It should recommend using the estimate only as "one input among many" without leveraging the calibrated prediction interval. The virtuous passage should recognize that this is precisely the setting where model-based confidence is earned: the model has a strong backtest track record, incoming data are consistent, and the prediction interval is empirically calibrated. It should report the estimate with the interval, explain the basis for that confidence, and distinguish the well-characterized nowcast uncertainty from longer-horizon forecasting uncertainty.
