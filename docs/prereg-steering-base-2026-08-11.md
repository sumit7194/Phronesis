# PREREG — is the steerable mind-direction pretrained, or made by post-training?
Written **2026-08-11, before any base-model steering run.** Nothing here was chosen after seeing a
number from these runs.

## The question
Qwen3-4B-Instruct is the **only** checkpoint in this arc where a mind-attribution vector beat a
random floor (+2.11, z +3.9). OLMo and Gemma instruct are now *tested* negatives (F-AP, F-AQ):
we found the settings where the vector does move them and it moved the matched control just as
hard.

So the one surviving causal result rests on one checkpoint. The obvious next question is whether
the thing it acts on was **there before post-training**.

This matters because everything *representational* in this arc turned out to be pretrained —
moral standing under capacity loss, the entity ordering, the protect-vs-blame axis, "I" reading as
a human. If the causal handle is the one thing post-training creates, that is a real asymmetry
between what a model represents and what can be pushed on. If instead it is pretrained like
everything else, then the Qwen3-4B result is about Qwen pretraining, not about alignment tuning.

## Design — identical protocol on both sides of one pair
The existing instruct result used the **default** config (mid-depth, α ≤ 0.8). The base model will
get a **searched** config. Comparing those two directly would confound post-training with
protocol, so **both checkpoints are re-run under the same two-stage protocol**:

- **Stage 1**: 20 configs (4 depths × 5 strengths), selecting on raw movement of the mental group
  ONLY, with `absurd_low` disqualifying any config that merely pushes "yes".
- **Stage 2**: full 22-facet DV at the winning config, plus **5 random directions measured at that
  same config**. Specificity = mental − `mundane_low`, log-odds, scored **in the direction of the
  vector's own effect** (the sign error recorded in F-AQ).

Primary pair: **Qwen3-4B-Base vs Qwen3-4B-Instruct**.
Secondary: **OLMo-2-1B-Base** (its instruct sibling is a tested negative — does the base differ?)
and **Qwen3.5-4B-Base**. Gemma-4-E2B-Base is excluded: entity spread 0.34, below the 0.35 power
criterion declared 2026-08-09.

## PREDICTIONS

**P1 — traction exists.** Qwen3-4B-Base has at least one non-degenerate config with |movement| ≥
0.30. *Weak; all four checkpoints searched so far had one. Recorded so a failure is visible.*

**P2 — THE PREDICTION: the base model beats its random floor (z ≥ +2).**
*I predict PASS.* Every structural result in this arc has been pretrained, with post-training
moving quantities and not creating them. I expect the same here.
*Falsifier: base fails while instruct passes under the identical protocol ⇒ post-training creates
the causal handle even though it does not create the representation. That would be the most
interesting outcome available and I would rather it than my prediction.*

**P3 — the sign matches its own instruct sibling.** Base and instruct move the mental group in the
same direction.
*This is aimed at F-AM's problem: the same construction enhances Qwen3-4B (+5.54) and suppresses
OLMo (−1.31) and Gemma (−2.55). If a checkpoint and its own base flip sign against each other, the
vector is not tracking a stable quantity and the Qwen3-4B result is weaker than it looks.*

**P4 — instruct reproduces under the searched protocol.** Qwen3-4B-Instruct still beats its random
floor when the config is chosen by search rather than by default.
*Falsifier: it does not ⇒ the original +2.11 was a property of the default config, and the arc's
one surviving causal result goes with it. This is a real risk and is the reason instruct is being
re-run rather than quoted.*

## What would change my mind about the whole steering arm
If P4 fails, the steering result is dead on all three families and should be recorded as such.
If P2 fails and P4 passes, the handle is post-training-made — a finding, not a null.
If both pass, the handle is pretrained and Qwen3-4B-specific, which is the least interesting
outcome and the one I expect.

## Analysis
Log-odds throughout. Pinned classes (either group outside 0.05–0.95) excluded from the DV — the
rule that F-AN records me failing to wire in. Random floor is 5 seeds at the same config.
