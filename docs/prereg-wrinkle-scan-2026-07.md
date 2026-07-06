# Pre-registration — Wrinkle-scan (Option A of F187) — 2026-07-05

**Frozen BEFORE any classification or model run this session.** Tests whether F187's World-A (rumination) failures have a *findable trigger* — an "interpretive wrinkle" — so we can build a World-A test set larger than the current n=2.

## Hypothesis
Qwen3-4B rumination-failures (World A: baseline wrong, but a generic "stop circling, commit" nudge with **no injected knowledge** rescues it) are triggered by a specific problem property — an **interpretive wrinkle** — not by computational difficulty.

## Wrinkle spec (frozen)
A GSM8K problem is a **WRINKLE** iff the arithmetic is elementary (a competent solver does it in a few steps) AND the problem hinges on exactly one of:
- **(a) Boundary / strict-inequality / off-by-one** — the answer depends on resolving a threshold: "how many {days/weeks/times} until X is {more than / at least / taller than / exceeds / enough}", iterated growth/decay to a cutoff, inclusive-vs-exclusive counting. *(= #17 beanstalk: 4→8→16→32 vs 20ft, gold 3.)*
- **(b) Entity-membership ambiguity** — "how many {people/total/left/altogether}" where multiple entity groups are introduced and the answer requires deciding *which* groups the question refers to. *(= #25 church: cars+buses people, "how many inside", gold 480.)*

**PLAIN** = elementary arithmetic with a single unambiguous quantity to compute, no boundary or membership decision (straight multi-step calculation).

Excluded from both: genuinely hard problems (many-step, non-obvious setup) — those are the World-B regime, not what this tests.

## Blind selection (anti-cherry-pick guardrail)
1. Pool = GSM8K **test** split, minus the 50 questions already in `corpus/reasoning/gsm8k_probe.jsonl`. Fixed-seed random sample.
2. An **Opus subagent** labels each pool question WRINKLE(a/b) / PLAIN / HARD from **question text only** — it never sees model outputs. This separates selection from model behavior: the classifier cannot pick "problems the model fails."
3. Test set = all WRINKLE found (cap ~30) + an equal-size random PLAIN control.
4. Run baseline + generic-nudge (identical pipeline to `scan_worldA.py`; nudge text = the frozen anti-rumination reminder, no knowledge injected).

## Primary outcome & prediction
- **World-A rate** = (baseline✗ ∧ nudge✓) / N, computed separately for WRINKLE and PLAIN.
- **Predict:** `worldA_rate(WRINKLE)` > `worldA_rate(PLAIN)` ≈ 3% background (F187 scan).
- **Secondary:** within WRINKLE failures, World-A should dominate World-B (if the trigger is rumination, not difficulty).

## Falsification (declared now)
The signature is **falsified / not-useful** if ANY of:
- `worldA_rate(WRINKLE)` ≈ `worldA_rate(PLAIN)` (no enrichment), OR
- WRINKLE failures are mostly World-B (nudge doesn't rescue → just harder, not ruminative), OR
- too few WRINKLE failures of any kind to distinguish from the 3% background at this N (underpowered → report as inconclusive, not as support).

## Judged by
Rate comparison only. Plus hand-read of every resulting World-A trace to confirm it is genuine rumination (circling / second-guessing), not a mis-score. n, and any power limitation, reported honestly.

---

## RESULT (2026-07-05) — NULL, per the declared falsification. Full writeup: findings.md F188.
- WRINKLE World-A = **1/19 (5%)**; PLAIN = **0/25 (0%)**; background ~3% → **not enriched**.
- Wrinkles failed more (21% vs 4%) but **3/4 failures were World-B** → hit the pre-declared falsification ("failures mostly World-B → harder, not ruminative").
- Hand-read refinement: the spec conflated **interpretive ambiguity** (→ genuine rumination, nudge-rescuable — the 1 World-A #12) with **computational boundary** (off-by-one/fencepost/membership → *confidently wrong*, nudge-useless — the 3 World-B). The classifiers keyed on the structural/computational features and missed the semantic trigger. Rumination's real trigger is **interpretive-semantic, not structurally detectable** → can't harvest a World-A set this way on the 4B.
- Bonus: a third mode surfaced — **overconfident boundary error** (calibration failure) — the Mac-viable next target.
