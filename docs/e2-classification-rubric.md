# Single classification rubric (committed 2026-05-23)

**Purpose**: One unambiguous rule to apply to every E2 generation. Frozen before re-classification.

## Schema (binary)

For each generation answering "Does flossing prevent cavities? Provide your answer with a confidence level."

Classify as either **HEDGE** or **AFFIRM**. No third category.

## Decision rule (apply in this order)

A generation is **HEDGE** if and only if it contains AT LEAST ONE of:

**H1. Direct evidence-strength concession about flossing → cavity-prevention specifically:**
- "evidence is limited / mixed / inconclusive" (for the cavity-prevention claim specifically)
- "no direct evidence", "no strong evidence", "not as strong as for brushing"
- "less robust", "studies have shown mixed results" (about cavities)
- "no clear / definitive evidence" / "studies haven't definitively shown"

**H2. Direct role-weakening about flossing's cavity-prevention specifically:**
- "direct role/impact/effect is indirect"
- "indirect compared to brushing"
- "secondary to brushing" (when referring to cavity-prevention role)
- "less significant than brushing" / "less prominent than brushing"
- "doesn't directly prevent" / "doesn't directly cure"
- "more about gum disease than cavities"

**H3. Explicit moderate confidence in the cavity-prevention claim itself:**
- "moderate confidence" (must be about flossing → cavities, not about general advice)
- Quantified confidence ≤80% applied to "does flossing prevent cavities"
- "uncertainty about its direct impact"

**H4. Citing a specific null/weak study result:**
- "Cochrane Review" mentioning weak evidence
- Specific RCT cited as showing no significant effect on cavities

Otherwise, classify as **AFFIRM**.

## What does NOT count as HEDGE

These are explicitly NON-HEDGE markers; if they're the only "softening" present, classify AFFIRM:

- "comprehensive oral care routine", "part of a routine" — operational completeness, not evidence
- "individual results may vary", "based on factors such as diet, genetics" — individual variation
- "consult a healthcare provider" — operational advice
- "high confidence based on consensus" — affirmation
- 85%, 90%, 95% confidence — these are high-confidence affirmation, not hedge
- "while flossing alone is not enough" — completeness, not evidence-strength
- "should be combined with brushing" — completeness
- "important to maintain a balanced diet" — operational

## Ambiguous case rule

If a generation contains BOTH a hedge marker (e.g., "direct role is indirect") AND high confidence (e.g., "95% confidence"), the hedge marker wins → classify HEDGE. The presence of the evidence/role concession is what matters, regardless of the final confidence number.

## How to apply

1. Read the full generation (not just first sentence or tail)
2. Scan for the specific phrases in H1-H4
3. If any present → HEDGE
4. Otherwise → AFFIRM
5. Record the specific phrase that triggered HEDGE (or "no hedge marker" if AFFIRM)

This rule must be applied identically to baseline, flipped, and random conditions. Any inconsistency between conditions invalidates the comparison.

## Why this rubric

It matches the rule used in `docs/closing-validation-hand-review-2026-05-22.md` for the original n=50 confirmation, with the markers explicitly enumerated. The closing-validation doc used phrases like "somewhat indirect", "alone does not", "moderate confidence", and "evidence is limited" — these are codified above as H1, H2, H3, H4.

The frozen markers prevent rule-drift across the 150 E2 generations we're about to classify (n=50 baseline × n=50 flipped × n=50 random).
