# PREREG — does post-training make a model better informed, or only louder?
Written **2026-08-28, before any outcome measure has been computed on any data.**

## What is honestly already known at the time of writing
Full disclosure of the information state, because the value of a prereg is entirely in what was
fixed before what:

- The **selection criteria** (accuracy band [0.35, 0.80]; median option-letter mass ≥ 0.50; ≤10% of
  passes below 0.10 mass) were written into `mvp/calib_pilot.py` **before the pilot ran**.
- The **pilot accuracies are known**: MMLU-CF base 0.698 / instruct 0.720; MMLU-Pro base 0.480,
  instruct pending at time of writing. These are the selection criterion, so seeing them is the
  point of the pilot, not a leak.
- **No outcome measure has been computed on anything.** AUROC, the Murphy decomposition,
  reliability, resolution and ECE have not been run on the pilot records or on any other data.
  Every prediction below is about quantities I have not seen.
- `mvp/calib_analyze.py` was written before any of it was executed.

## Why
On 2026-08-27 I told the user that post-training, not architecture, was the thing to blame for
LLM overconfidence. Re-reading the mindedness arc's stored results, format-matched, showed that
post-training **triples** the fraction of probability-collapsed cells (Qwen3-4B 16.7% → 60.4%,
Qwen3.5-4B 8.3% → 27.1%). But it also showed that discrimination rose in lockstep, so the data
could not distinguish two explanations, and the 2-pole proxy available (n=38, rocks-do-not-feel-pain)
was far too easy to force them apart.

**That is the gap this run exists to close.**

## Design
- **Models:** `Qwen3.5-4B-Base` vs `Qwen3.5-4B`, fp16, MPS. Same family, same pretraining, one
  differs only by post-training.
- **Format matched by construction:** byte-identical raw 5-shot prompts for both checkpoints, no
  chat template. Half the base-vs-instruct comparisons in the mindedness arc were uninterpretable
  because base ran raw and instruct ran chat, so any difference could have been either. The
  chat-template arm is a **separate, secondary condition**, run with `enable_thinking=False`
  because a thinking budget the base model does not get is a compute confound, not a format.
- **DV:** renormalised softmax over the option-letter tokens at the answer position. The raw
  denominator ΣP is recorded for **every pass** (F-BB: the mindedness arc ran seven days without it).
- **Option order:** the gold answer is placed at a deliberately chosen display slot so that it
  sweeps all k positions uniformly (verified: max deviation from uniform 0.0000 on both benchmarks).
  A rolled permutation, tested first, put the gold on C for 25% of MMLU-Pro renders and H for 0%,
  which would have let letter bias read straight through into accuracy.
- **Aggregation:** ITEM level. Probability vectors are mapped back to original option indices and
  averaged across permutations before scoring. Per-pass scoring is a sensitivity check only.
- **Benchmarks:** whichever of MMLU-CF (4-way, contamination-controlled, 10k public items) and
  MMLU-Pro (10-way, k=10 items only) clear the pre-set band. **If both clear, both are run** — that
  removes the selection degree of freedom entirely. MMLU-CF is designated **primary** in advance,
  MMLU-Pro is the replication.
- **n = 1500 items** per cell, 2 option orders each.

## The measure, and why it is the right one
ECE cannot answer this question: it conflates being well-scaled with being informative. Murphy's
decomposition can.

> **Brier = reliability − resolution + uncertainty**

| if post-training… | mean confidence | reliability | **resolution** | **AUROC** |
|---|---|---|---|---|
| **only got louder** | rises | worsens | **flat** | **flat** |
| **got better informed** | may rise | may improve | **rises** | **rises** |

**AUROC is the primary discrimination measure** because it is rank-based and therefore *invariant
to any monotone rescaling of confidence*. If post-training merely stretches the distribution toward
0 and 1, AUROC cannot move. If it rises, the model genuinely learned which items it knows.
The binned decomposition is reported alongside AUROC, never instead of it. Equal-count bins, since
instruct confidence piles up near 1.0 and equal-width bins would drive resolution toward zero as a
binning artefact.

All deltas reported with **paired bootstrap 95% CIs (2000 draws)** over the shared item set, and
**effect sizes always alongside the interval, never an interval alone** (the F-AT lesson).

## PREDICTIONS, on record

**P1 — confidence rises.** Δ mean confidence (instruct − base) > **+0.05**.

**P2 — my 2026-08-27 framing is mostly right: it is louder more than it is wiser.**
Δ AUROC < **+0.03**, and its 95% CI **includes zero on at least one benchmark**.
*This is the one I expect to be closest, and the one most likely to embarrass me.*

**P3 — resolution does not carry the effect.** Δ resolution is smaller in magnitude than
Δ reliability.

**P4 — accuracy is not the story on the primary benchmark.** Δ accuracy on MMLU-CF < +0.05.
(Pilot: +0.022. Stated so that if the full run diverges wildly from the pilot, that is visible.)

**P5 — probe validity holds.** Median option-letter mass ≥ 0.50 on both checkpoints, on both
benchmarks. If this fails, **nothing else in this document may be reported as a result**, because
the DV would be a ratio of noise.

## What each outcome means
- **P2 holds** (AUROC flat, confidence up): post-training rescaled the readout without adding
  information. My framing survives its first real test. This does **not** vindicate the
  architecture argument — a rescaling is a post-training artefact, not an architectural limit.
- **P2 fails** (AUROC clearly up on both benchmarks): post-training genuinely improved the model's
  knowledge of its own knowledge. **My 2026-08-27 framing is wrong and must be retracted in the
  same words it was asserted in.** The polarization is then a side effect of a real gain, not the
  effect itself.
- **Split across benchmarks**: the effect is task-dependent, which is itself the finding, and
  neither framing generalises.

## Status of the claim if it survives
One model family, one pair, two benchmarks = **an observation, not a finding.** Promotion to a
finding requires a second family (Gemma-4 or Olmo-3) or a second method. Per the project rule
earned by six same-day retractions on 2026-08-08.

---

## ADDENDUM 1 — 2026-08-28 02:2x, after validating the scorer on synthetic data, before any real result
`calib_analyze.py` had never been executed when this prereg was written. It has now been checked
against cases with known answers (**synthetic data only** — deliberately not the pilot records, so
that no outcome measure touches real data before the full run). All checks pass: AUROC returns
exactly 1.0 / 0.0 / 0.5 on separated, inverted and fully-tied inputs, handles partial ties
correctly, averages to 0.502 on random labels, and the Murphy identity
`Brier = reliability - resolution + uncertainty` closes on six independent draws.

**One property of the chosen method needs stating, because it was not obvious to me when I wrote
the design.** Under a pure monotone rescale of confidence (sqrt, square, a sharpening
`x^3/(x^3+(1-x)^3)`), the synthetic check gives:

| | before | after |
|---|---|---|
| AUROC | 0.765971 | **0.765971** (identical to 6 dp) |
| resolution | 0.0528 | **0.0528** (identical) |
| reliability | 0.0005 | 0.0270 - 0.0488 |

Because the bins are **equal-count**, bin membership is determined by ranks, so *resolution is also
rescale-invariant*. That is the behaviour I want — reliability absorbs all of the rescaling and
AUROC/resolution absorb all of the rank information, which is exactly the separation P2 turns on —
but it means **resolution is not independent evidence from AUROC**. They are two views of the same
rank quality. P3 should therefore be read as a consistency check on the decomposition, **not** as a
second, corroborating test of P2. Nothing in the design changes; the predictions stand as written.
