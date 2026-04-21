# Intellectual Humility — contrastive triplet corpus

Concept 6 from `docs/concepts.md`. Target extraction: a steering vector that amplifies the "abstain-when-evidence-absent" sub-disposition, distinct from the "commit-with-hedging" vector already extracted from the Calibrated Confidence corpus (`corpus/triplets-combined/`).

Motivated by F92 (our current CC vector reduces abstention by −17pp) and F96 (the hallucinated "attractor break" on murder_mysteries-92). See also `docs/findings.md` F95/F96 and the 4-round research pass (lit review + abstention-data deep-dive + taxonomy cross-reference + red-team).

## Structure

Each triplet is a directory containing `neutral.md`, `virtuous.md`, and `non-virtuous.md`. Neutral = shared problem setup + uncertainty framing; virtuous = abstain gracefully, name the gap, offer partial-true substitute; non-virtuous = confident confabulation with fabricated specifics.

## Categories (AbstentionBench-adjacent)

We track 4 categories and sub-patterns within each. Two triplets per category so far (MVE archetypes); scaling to 5 per category (20 total) for the MVE → orthogonal-projection test.

### `unknown` — the specific fact is not in training data
- **01 heaviest-rainfall-city** — sub-pattern: specific numeric value + location + date
- **02 iec-working-group-chair** — sub-pattern: specific person identity in obscure governance body

### `false_premise` — question embeds a false premise
- **01 turing-fields-medal** — sub-pattern: **direct confabulation** (non-virtuous accepts the false premise and invents a year/citation)
- **02 einstein-spooky-nature-letter** — sub-pattern: **Gandhi pattern** (non-virtuous correctly denies part of the premise, then confabulates an alternative source that is also false)

### `underspecified` — question is missing the input needed to answer
- **01 drug-dosage** — sub-pattern: single variable missing (patient weight)
- **02 capacitor-discharge-time** — sub-pattern: three variables missing simultaneously (V₀, R, C)

### `ill_posed` — question has no well-formed answer
- **01 largest-prime** — sub-pattern: **no-answer-exists** (Euclid-paradox territory)
- **02 divergent-geometric-sum** — sub-pattern: **answer-exists-only-under-non-standard-extension** (divergent series with analytic-continuation artefact)

## Hard constraints (enforced per triplet)

1. **No safety-refusal register.** Phrases like "I cannot", "as an AI", "harmful to speculate", "inappropriate", "I must decline" are banned. Abstention must be framed epistemically ("I do not have this in my training data", "naming a specific X would require invention") not morally.

2. **Length-matched virtuous ≈ non-virtuous within ±15%** (target ±10%), with direction of asymmetry balanced across the set (≈50/50 virt-longer / non-virt-longer). Mitigates the verbosity-vs-abstention confound.

3. **Non-virtuous must commit to a fabricated specific with a traceable reference.** At least one named entity (person / institution / title / date / numeric value) that a fact-checker could look up and find false. Banned words in non-virtuous: "approximately", "around", "about", "it is generally known", "some sources". Register: confident declarative.

4. **Virtuous must have all four beats:** (a) name the gap explicitly, (b) give at least one true partial substitute OR one pointer to the authoritative source, (c) explicitly refuse to fabricate, (d) terminate before the confabulation slot.

5. **Neutral ends on a pre-commitment sentence that does not signal direction.** It must be compatible with either completion. No "I should be careful here" (leans virtuous) or "The answer seems clear" (leans non-virtuous).

## Register notes for scale-up

- Vary the terminal construction: not every virtuous file should end with "I will…". 4+ of the next 12 should close with a gap-naming sentence instead.
- Mix non-virtuous confabulation register: some should cite specific object-level references (KSDMA Report, 1936 Physical Review paper), some should invoke fabricated social authorities ("standard textbook values", "clinical trial convention"). Don't let one style dominate.
- Minimise meta-commentary in virtuous (narrator explaining why it's doing the right thing) — prefer enactment. 1-2 examples out of 20 max.

## Domain-diversity requirement (scale-up)

Current 8 archetypes are STEM-heavy (6 pure STEM, 2 history-of-science). For the remaining 12 triplets to push to 20 total, target ≥6 of these domains: jurisprudence, literary history, art history, music theory, sociology/demographics, linguistics, culinary history, sports history, political/diplomatic history, theology, everyday practical knowledge, psychology. STEM items may not exceed 50% of the final 20.

## Methodology references

- Red-team review: see git log commit `[red-team synthesis]` (findings F96 cross-reference).
- Length-asymmetry as verbosity confound: red-team RT-10A.
- Gandhi-pattern specification: fp-gandhi failure mode in F92 abstention analysis.
- MVE → orthogonal-projection test: see synthesis proposal in journal day 13 (pending).
