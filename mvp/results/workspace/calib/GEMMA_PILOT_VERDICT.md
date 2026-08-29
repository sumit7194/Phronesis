# Gemma-4-E2B pilot verdict (2026-08-29)
Selection criteria fixed before any Gemma data: accuracy band [0.35, 0.80] on BOTH checkpoints,
median option-letter mass >= 0.50, <= 10% of passes below 0.10 mass.

| bench | role | acc | chance | mass median | mass<0.10 | top1 is letter | letter bias |
|---|---|---|---|---|---|---|---|
| mmlu_cf | base | **0.520** | 0.25 | 0.9975 | 0.000 | 1.000 | 0.062 |
| mmlu_cf | instruct | **0.463** | 0.25 | 1.0000 | 0.000 | 1.000 | 0.167 |
| mmlu_pro | base | **0.242** | 0.10 | 0.9940 | 0.000 | 1.000 | 0.185 |
| mmlu_pro | instruct | *stopped at 50 items (0.200)* | 0.10 | — | — | — | — |

## QUALIFYING: mmlu_cf only

**mmlu_pro EXCLUDED — floor effect, not a probe failure.** Gemma-4-E2B-Base scores **0.242 against
a 0.35 floor** on the completed 200-item cell. The gate requires *both* checkpoints in band, so
mmlu_pro was already disqualified by completed base data; the instruct cell was stopped at 50 items
(0.200, also far below floor) because it could not change a verdict already determined. This is the
floor risk flagged during planning: a 2.3B-effective model on a 10-way benchmark sits too close to
chance for a calibration curve to exist.

**Probe validity PASSES everywhere, including on mmlu_pro.** This is worth recording on its own:
mindedness **F-AU** found gemma-4-E2B-it pinning **37.8%** of its cells outside [0.05,0.95], a 3x
outlier across nine checkpoints, on the two-token Yes/No readout. On the MCQ letter readout the same
checkpoint gives **median mass 1.0000, 0% of passes below 0.10, and top-1 = an option letter 100%
of the time.** The F-AU pathology does NOT transfer. It was a property of that readout, not of Gemma.

## Two cautions carried into the full run
1. **Accuracy is NOT matched across checkpoints** (base 0.520 vs instruct 0.463, ~6 points). On
   Qwen3.5-4B the two were within 0.4 points, which is what made that comparison clean. Here a
   difference in AUROC could partly reflect a difference in task difficulty faced, so the
   accuracy-matched argument used for Qwen is **not available** and must not be reused.
2. **Letter bias is higher** than Qwen's (0.167 and 0.185 vs 0.005-0.060). The uniform gold-position
   sweep should absorb it, but it is worth reporting rather than assuming.

## Operational note (not a result)
The pilot has **no chunking** and mmlu_pro degraded **6.95 -> 43.72 s/pass** across 200 items;
Gemma-4-E2B is 9.6GB of weights on a 16GB machine. mmlu_cf, with 4 options and much shorter prompts,
held a flat **0.67 s/pass** over the same 200 items with no degradation at all. The full mmlu_cf run
uses the chunked runner regardless.
