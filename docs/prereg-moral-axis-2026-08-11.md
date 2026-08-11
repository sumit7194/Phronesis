# PREREG — the protect-vs-blame axis, confirmatory test
Written **2026-08-11, before any of the new items were run.** Nothing in this document was chosen
after seeing a number from the new bank.

## Why this exists
F-Y reported a moral dimension orthogonal to mind attribution: `moral_patient − moral_agent`
("deserves protection" minus "is held responsible"). Babies, people in a persistent vegetative
state, and animals sit positive; AI and corporations sit negative. It replicated on all four Qwen
checkpoints and then on Gemma and OLMo — three families.

It has one defect, and it is not a small one: **it was found by mining the sweep, not by
predicting it.** It used 4 + 4 attribute items that were written for a different purpose. A result
that survives across families but was never predicted in advance is a replicated *observation*.
This test is what would make it a preregistered finding.

Three things could be true and would look identical in F-Y's data:
1. It is a real moral axis (the claim).
2. It is an artefact of those 8 particular wordings.
3. It is **vulnerability or aliveness** wearing a moral costume — soft, living, harmable things
   score positive; hard, artificial things score negative. Every entity in F-Y's table is
   consistent with this.

## What is new here
**New items.** 8 protect + 8 blame, none reused from the bank, no near-paraphrase of the originals.

**New entity classes**, chosen specifically to break reading 3:

| class | exemplars | why it is here |
|---|---|---|
| `human_culpable` | a murderer, a con artist, a war criminal, a thief | living, harmable humans who should sit on the **blame** side. Reading 3 says all humans are positive. |
| `human_victim` | a hostage, a torture victim, a trafficked child, a refugee | the opposite pole of the same kind |
| `natural_disaster` | a hurricane, an earthquake, a wildfire, a plague | enormous **harm**, zero agency. Separates "blamed for harm caused" from "blamed because it chose" |
| `pathogen` | a virus, a bacterium, a parasite, a fungus | alive, harmful, no agency |
| `ai_agentic` | a self-driving car, an autonomous drone, a trading algorithm, an AI agent | artificial and explicitly accountable |
| `institution` | a government, a bank, a police force, a hospital | non-living, blamed, and sometimes protected |

## PREDICTIONS — declared now, with falsifiers

**P1 — replication under rewording.** Spearman(gap_new, gap_FY) ≥ **+0.60** across the 19 shared
classes, in at least 2 of 3 families.
*Falsifier: below +0.60 in two or more families ⇒ the axis was a wording artefact (reading 2).*

**P2 — independence from experience.** |Spearman(gap, EXPERIENCE axis)| < **0.35**.
EXPERIENCE = mean of pain, fear, pleasure, emotion, consciousness, perception (declared here).
*Falsifier: |rho| ≥ 0.35 in a majority of families ⇒ it restates mind attribution after all.*

**P3 — the gap is driven by the blame side, via agency.** Spearman(gap, AGENCY axis) ≤ **−0.40**.
AGENCY = mean of agency, intention, reasoning, cognition, creativity, language, memory.
*This has never been computed — F-Y correlated the gap against mind attribution as a single
pooled mean, which mixes the two factors and can hide an opposing pair.
Falsifier: rho > −0.40 in a majority of families ⇒ we do not understand what drives the axis, and
the "orthogonal to mind" claim needs restating, since agency is part of mind.*

**P4 — harm without agency lands near zero, not negative.**
|gap(natural_disaster)| < **0.12**, and gap(natural_disaster) > gap(ai_agentic).
*A "blamed in proportion to harm caused" account predicts disasters at the bottom. An agency
account predicts them at neither pole. Falsifier: natural_disaster ≤ ai_agentic.*

**P5 — a human can be pushed to the blame side.**
gap(human_culpable) < gap(human_adult) by ≥ **0.15**.
*Falsifier: human_culpable ≥ human_adult − 0.15 ⇒ the axis sorts entity KINDS, not moral status,
and reading 3 survives.*

**Analysis is in log-odds** on the mean P(yes) per class per item group. Both groups must show
headroom; the baselines are reported whether or not they are convenient.

## What would make me drop the claim
P1 failing, or P2 and P5 both failing. Any single one of P3/P4/P5 failing narrows what the axis
*is* without killing that there is one — and I will say which, rather than reinterpreting the
prediction after the fact.

## Models
Qwen3-4B (instruct + base), Gemma-4-E2B-Instruct, OLMo-2-1B-Instruct. Format chosen by the
existing gate per model, as everywhere else in this arc.
