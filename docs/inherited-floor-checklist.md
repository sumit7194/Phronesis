# Inherited-floor checklist — drop into Day 1 of the next project

Phronesis paid 67 days of tuition to learn this. The next project **starts where this one ended.** Copy this file (and `EXPERIMENTATION_GUIDELINES.md`) into the new repo before the first big compute spend, and tick these off.

## Before any code
- [ ] **Copy in the floor.** `EXPERIMENTATION_GUIDELINES.md` is the *inherited* baseline (it only ratchets up). Bump its version, keep the changelog.
- [ ] **Copy in `STATE.md`** (blank it, keep the format). Overwrite it each session; never let planning docs go stale again.
- [ ] **Adversarial pre-mortem (1 page).** Answer, in writing, before spending compute:
  - What in the literature would make this already-known or already-refuted? *(Do the prior-art read NOW, not at Day 40.)*
  - What is the single cheapest experiment that could kill the whole idea?
  - What would a referee attack first?
- [ ] **Name the unit of generalization.** "This claim generalizes over ⟨prompts / models / datasets⟩, target ≥ K." Power for *that* unit — seeds on one prompt never substitute for prompt count.

## For every experiment (prereg)
- [ ] Hypothesis **and** falsifier **and** a **stopping rule** (the exit): *"if after N attempts the effect is n=1-prompt / direction-agnostic / control-tying, the branch is closed."*
- [ ] The **controls are named up front**: matched-norm random (≥2–3 seeds), sign-flip, and a **placebo / useless-signal** control where applicable.
- [ ] Timestamp the prereg externally (OSF) if the work is publication-bound — local markdown is an assertion, not a registration.

## Gate on reporting (the hard rule)
- [ ] **No uncontrolled positive is spoken as a result — even internally.** It stays tier-C, unnamed in journal/commit messages, until its control lands. The three most expensive errors here were all "let me note this promising result and control it next."
- [ ] **Hand-read the headline.** No auto-scorer (regex/verify/string-match) certifies a load-bearing verdict without a human/frozen-rubric read of a sample. Catch the "confabulation scored correct" and the "2:00 ≠ 2" bugs before they become findings.
- [ ] **Suspect the winner hardest.** For your best result, run the fair-baseline control (same budget?) and the random/placebo-gate control (does a useless signal help too?). Discipline lapses exactly when you're winning.

## Consolidation cadence
- [ ] Close each arc with a **2–3 paragraph mini-writeup at its earned tier** before opening the next thread. Don't let results outrun writeups.
- [ ] Publication hardening at the publish gate: double-score a subset (n≈50) with a second judge/human, report inter-rater **κ**.
- [ ] Move dead docs to `archive/` the moment they're superseded.

---
*The one-line version: inherit the floor, read the adversary first, pre-register the exit, gate reporting on controls, and suspect your winner. Start where the last project ended.*
