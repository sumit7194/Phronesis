# Retrospective — process lessons (2026-07-06)

**Source.** A structured external review (a separate Claude "science" session) read the full arc through F179 plus the methodological floor and delivered a constructive retrospective. This doc preserves its durable lessons in the project record, with one correction of scope (below) and the concrete actions we took.

**One-line thesis (theirs, and correct):** *The project's great strength is that it turns failures into codified rules; its great weakness is that it only did so **after** each failure. The professionalization move is to make the ratchet **anticipatory**.*

---

## Scope correction
The review was written from a snapshot **through F179 (2026-06-29)**. It did **not** see **F180–F190** — the reasoning-calibration arc. That arc is where several of its recommendations are already applied *anticipatorily*, so its headline ("rules only ever added reactively") is true of F100–F179 but is becoming false:
- **Gate reporting on controls / suspect your winner:** the placebo control on our own hoped-for positive (F190) killed "verification rescues boundary errors" *before* it became a claim.
- **Pre-register the exit:** the wrinkle-scan (F188) was pre-registered with falsification conditions and a null declared in advance.
- **Mandatory controls:** budget-matched random (F186), random/nudge controls (F187), hand-read of every headline.

So the ratchet has started running forward. The job now is to make that the default from Day 1 of the *next* project, not something re-derived mid-arc.

---

## The recurring failure modes (F100–F179) — each with what it cost
1. **Single-seed random controls false-certified specificity — 3× (F122, F160 seed-42, F171 v3).** An uncontrolled positive got *called*, sometimes twice, before the control deflated it. → floor §2 (≥2–3 seeds, magnitude-matched).
2. **Prior art read reactively (Day ~40).** The "legibility ≠ steerability / read ≠ write" wall and random-mimicry caution were already in the 2024–25 literature; front-loading would have re-scoped the opening bet.
3. **Auto-scorer trust burned twice** (empty-string "13→70%" replication; regex creeping into "manual" review). → the entire hand-scoring floor (§3).
4. **Measurement-to-claim mismatch** (F169/F170: pass@1 greedy vs Google's pass@k, same model/data). Retracted. → floor §1.
5. **Parameters assumed to transfer across scale** (F171: 4B's α≈16 ≈ 2% of 32B norm → inert).
6. **A structurally-compromised prompt (E2/flossing) stayed load-bearing too long** — an n=1-prompt, direction-agnostic, magnitude-saturated effect can't support a general claim *no matter how robust the n on that one prompt*.
7. **The "find-more-positive-evidence" trap** ran 6–7 cycles before being named and stopped.
8. **Documentation outran synthesis** (57 docs, 800KB append-only findings, stale planning docs) — and *results outran writeups* (strongest result unpublished while the old story is on Zenodo).

## The durable lessons → anticipatory rules
1. **Inherit the floor.** Day 1 of the next repo copies `EXPERIMENTATION_GUIDELINES.md` in as the *inherited* floor. The ratchet is cross-project, not per-project. (See `docs/inherited-floor-checklist.md`.)
2. **Adversarial pre-mortem before the first big spend.** One page: *what would make this already-known/refuted? cheapest experiment that kills it? what would a referee attack first?* The prior-art read belongs here, not at Day 40.
3. **Pre-register the exit, not just the hypothesis.** Add a **stopping rule** ("if after N attempts the effect is n=1-prompt or direction-agnostic, the branch is closed") so sunk cost can't argue with you later.
4. **Decide the unit of generalization up front and power for *it*.** The recurring error was tightening *seed* count on a claim whose weakness was *prompt* count (or model count). Write: "this generalizes over ⟨prompts/models⟩, target ≥K; seeds on one prompt don't substitute."
5. **Never speak an uncontrolled positive as a result — even internally.** Make the random/sign/placebo control a **gate on reporting**: no "promising result" in a journal entry or commit message before its control exists.
6. **STATE.md as single source of truth.** A one-page, *overwritten-each-session* dashboard (best claim + tier + controls + open) alongside the append-only notebook. Antidote to stale planning docs. Move dead docs to `archive/`.
7. **Consolidate the increment before the next one.** Close each arc with a 2–3 paragraph mini-writeup *at the tier it earned* before opening the next thread.
8. **Harden AI-as-judge for external credibility.** At the *publish* gate: double-score a subset (n≈50) with a second judge or human pass, report inter-rater κ; timestamp preregs on OSF, not just local markdown. (Single-judge + author-review remains fine for internal exploration.)
9. **Apply the same adversarial suspicion to the winner.** The best result is exactly when discipline lapses. For gate→search: fair-baseline control (does the ungated baseline get the same token/tool budget?) and a **random-gate** control (does gating on a useless signal also help?).

## Honest caveat on "front-load everything"
Some rigor is inherently learned *in situ* — you cannot pre-register failure modes you haven't discovered on a genuinely novel question. But the **generic** rigor (controls, prior-art, measurement-matching, scale-calibration) *was* front-loadable. Adopt: **front-load the generic floor; expect to learn the domain-specific rigor as you go, and codify it immediately.**

## Where the *current* arc still shares the old weaknesses (self-audit)
- **Small-n / single-model.** F180–F190 are all Qwen3-4B, n=2–156; caveated everywhere, but cross-model needs the GPU.
- **Writeups deferred again.** gate→search and F180–F190 remain unpublished — the same "results outran writeups" pattern, still open.

## Actions taken (2026-07-06)
- Created `STATE.md` (living dashboard) and this retrospective.
- Created `docs/inherited-floor-checklist.md` (Day-1 checklist for the next repo).
- Flagged the writeup debt (gate→search + reasoning arc) as the top consolidation task in STATE.md.
