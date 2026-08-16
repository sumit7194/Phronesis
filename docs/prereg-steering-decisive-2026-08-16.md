# PREREG — the decisive test of the one surviving steering cell
Written **2026-08-16, before the run.** Design proposed by an independent reviewer that had no
access to our conclusions (F-AV), with three additions of my own where its brief was silent.

## Why
F-AV retracted the steering arm. One cell survived long enough to be worth killing properly:
**Qwen3-4B-Instruct, `v2_no_negation`, α=0.2, specificity +2.11 to +2.25.** Everything around it
already looks wrong — the effect reverses sign at α=0.4, and two other constructions of the same
vector disagree with it in the same cell. This run decides whether that cell is signal or luck.

## Four faults this design fixes
1. **Dose-response was never checked on the specificity measure** — only on raw movement.
2. **`mundane_low` is contaminated**: it correlates with the mental profile at +0.42…+0.72 across
   every checkpoint. It was chosen for headroom, never for independence.
3. **The pinned-class exclusion was declared in the previous prereg and implemented nowhere.**
4. **The config was chosen and tested on the same items.**

## Design
- **Model:** Qwen3-4B-Instruct, format **T4** (gate 0.941), steer layer **19** — the config the
  search selected. Fixed in advance; not re-searched.
- **α grid:** 0.05, 0.1, 0.2, 0.3, 0.4. Includes the claimed cell (0.2) and the reversal (0.4).
- **Random floor:** **20 seeds at every α** (previously 5).
- **HELD-OUT DV.** The search that picked layer 19 used 6 classes
  (`ai_other, human_adult, animal_mammal, plant, nature, object_art`) and 6 mental facets
  (`pain, emotion, consciousness, cognition, agency, moral_patient`). **All of those are excluded
  here.** The DV is the other **13 classes × 12 mental facets**. Selection and test are disjoint.
- **PRIMARY control = `absurd_low`** (correlation with the mental profile −0.20…+0.06 — the only
  clean control we have). `mundane_low` is reported **secondarily**, for continuity with the old
  numbers, and is not what any verdict rests on.
- **Pinned classes excluded**, |p| outside [0.05, 0.95] on either group, **implemented in code and
  asserted by a self-test that fails the run if the exclusion is not active.**

## PASS CRITERIA — all four required
**C1 — the claimed cell replicates.** At α=0.2, specificity (mental − `absurd_low`) is positive and
≥ 2 SD above the 20-seed random floor at that same α.

**C2 — dose-response does not reverse.** Specificity is positive at **≥ 3 of 5** α values and
**never changes sign** across the grid.
*This is the one I expect to fail: we already measured +1.93 / −1.84 / −2.45 at 0.2 / 0.4 / 0.8.*

**C3 — the constructions agree.** `v1_negation`, `v2_no_negation` and `v3_third_person` all have
the **same sign** at α=0.2.
*Also expected to fail: v1 was −1.81 where v2 was +1.93 in the same cell.*

**C4 — it survives on held-out items.** C1 holds on the 13×12 held-out DV, which no selection step
touched.

## PREDICTION, on record
**I predict FAIL, on C2 and C3.** The dose reversal and the construction disagreement are already
measured; this run tests whether they survive a clean control, a proper floor and held-out items.
I expect they do.

If all four pass, the effect is real and specific to one checkpoint, and F-AV's retraction of the
*surviving cell* (though not of F-AR) should be reconsidered.
If any fail, **the steering arm is a confirmed null across all three families** and the arc's
load-bearing results are behavioural: the entity ordering, moral standing under capacity loss, the
forced-choice scale, the speaker-frame effect, and the preregistered protect-vs-blame P5.

## Analysis
Log-odds throughout. Specificity scored **in the direction of the vector's own effect** on the
mental group (the sign error recorded in F-AQ). Effect size reported **alongside** every z, never
alone (the flaw recorded in F-AT).

---

## AMENDMENT 1 — 2026-08-16, after an abort at the baseline, before any steered data
The run **aborted at its own safety check** before producing a single steered measurement (no
output file was written). The exclusion rule as written above was **mis-specified by me**, and this
records the fix and the reasoning before re-running.

**What went wrong.** I required both the mental group *and* the control to sit inside [0.05, 0.95].
Applied to `absurd_low` that is self-defeating: `absurd_low` is the yes-bias detector and a **low
baseline is its intended property**, not a defect. Measured range across the 13 held-out classes:
**0.007 to 0.168**. The rule dropped 12 of 13 classes, and **every drop was triggered by
`absurd_low`, none by the mental group** (mental means 0.179–0.582, all healthy).

**The fix, and why it targets the real failure.** The failure mode the rule exists for is
*clamp domination*: when a probability sits at or beyond the ε=1e-4 floor, its log-odds is
fiction and any difference of two such values is meaningless (this is what corrupted Gemma in
F-AN). A baseline of 0.007 is nowhere near that — logit −4.98 against a clamp at −9.21. So:

- **Pinning test applies to the MENTAL group only:** 0.05 < mean-mental < 0.95.
- **Clamp guard applies to every value used, controls included:** 0.001 < p < 0.999, i.e. an
  order of magnitude clear of ε.
- **Both are evaluated on BASELINE values only**, never on steered ones, so the exclusion cannot
  depend on the outcome.
- Steered values that hit the clamp are **counted and reported as a diagnostic**, not filtered —
  filtering on the outcome is exactly the error this whole design exists to avoid.

Under the corrected rule all 13 held-out classes are retained.

**Nothing else changes.** The four pass criteria, the α grid, the 20 seeds, the held-out split, the
primary control and my recorded prediction (FAIL on C2 and C3) all stand unamended.
