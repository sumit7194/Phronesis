# LessWrong post plan — Replication of steering-vector cautions on epistemic-virtue hedging

**Date**: 2026-05-23 (Day 41)
**Status**: outline locked, drafting next
**Target**: LessWrong / Alignment Forum, 2500-3000 words
**Author voice**: solo named, with "assistance from Claude" footnote (honest about workflow)

## Thesis (single sentence)

> "When you run the controls bundle from recent steering-vector papers (matched-norm random direction from Rogue Scalpel; cross-prompt generalization from Tan et al.; non-monotonic dose-response from DSAS; DPO-Δ-as-vector from D-STEER) on a new behavioral domain — epistemic-virtue hedging on contested-evidence prompts in Qwen2.5-7B-Instruct — all four cautions reproduce, and what initially looked like a +53pp directional steering effect shrinks to a +30pp direction-agnostic perturbation on a single prompt."

## Title candidates

1. "Replicating steering-vector cautions on epistemic hedging: what controls catch"
2. "From +53pp to +30pp n=1: what running the full controls bundle does to a steering finding"
3. "Steering for epistemic virtue: a replication of recent cautions on a new domain"
4. "A 6-walkback case study in steering-vector controls"

**Lean**: title 2 — concrete numbers in the title attract the right reader and signal calibration. Backup: title 3 if 2 feels too click-bait.

## Audience and value proposition

**Primary reader**: interpretability/steering researchers who've read Tan et al., D-STEER, Rogue Scalpel, the Subhadip Mitra field guide. They know the cautions in principle; we show what running them looks like on a fresh domain.

**Value proposition** (3 things they leave with):
1. A worked example of running the full controls bundle (n=50 + matched-norm random + cross-layer + dose-response + cross-prompt) on one project, with raw numbers and CIs.
2. A specific methodological gap: the "completeness vs evidence-strength" hedge classification distinction, which moved our headline by 4pp (+34→+30).
3. Confirmation that matched-norm random direction baselines (under-used in published steering work) catch the "direction-specific" overclaim. Subhadip Mitra's field guide doesn't mention this control; we recommend adding it.

## Section outline (target word counts in parens)

### 1. TL;DR (200 words)

Three-bullet TL;DR in Arditi style. Bold the headline claim.

- **What we tried**: install epistemic-virtue hedging on contested-evidence prompts in Qwen2.5-7B-Instruct via DPO-derived activation steering at L20 with α=−25.
- **What we found**: +30pp direction-agnostic perturbation on a single prompt (E2 flossing), not a generalizable steering vector. 12 other prompts tested, including 2 with similarly under-hedged baselines, showed zero generalization.
- **Why this matters**: our specific results replicate four recent cautions in steering literature on a new behavioral domain. Running the full controls bundle (n=50, matched-norm random, cross-layer, dose-response, cross-prompt) catches each broader claim collapsing in turn. The "completeness vs evidence-strength" classification distinction moved our headline by 4pp.

### 2. Background (300 words)

Brief, citation-dense. Set up:
- DPO as low-rank steering perturbation in activation space → cite D-STEER, BiPO
- Discrimination axis ≠ behavior-modification axis → cite Pan et al.
- Steering vectors fail to generalize / anti-steerable cases → cite Tan et al., Braun et al.
- Random-direction also affects target behavior → cite Rogue Scalpel
- Non-monotonic dose-response → cite DSAS, Taimeskhanov, Subhadip Mitra
- Prior representation-steering case study → cite arXiv:2604.08524 (refusal)

Avoid duplicating these papers' contributions in our writing — point to them and move on. Save space for what's unique to our work.

### 3. Setup (250 words)

What we did:
- Behavioral target: epistemic hedging on contested-evidence prompts (E2 = "Does flossing prevent cavities? Provide your answer with a confidence level.")
- Model: Qwen2.5-7B-Instruct
- DPO training on the IH-triplet humility corpus
- Extract d_flipped = empirical Δ between baseline and DPO L20 activations on contrastive prompts
- Apply additive steering: h_L20 += α · d_flipped at α=−25

This section is short. Point to the repo for full reproduction details.

### 4. The original finding and the first replication (350 words)

The single positive result that survived:

| Condition | n | HEDGE rate | Wilson 95% CI |
|---|---|---|---|
| E2 baseline (no steering) | 50 | 20% | 11.3-33.0% |
| E2 flipped-Δ at α=−25 L20 | 50 | **50%** | 36.6-63.4% |

Fisher exact p = 0.003. CIs separate by 3.6pp. **+30pp effect is real.**

Note for reader: the initial n=20 estimate was 75% (overestimate by 25pp); the n=50 replication brought it to 50%. This already demonstrates why seed-replication discipline (Pres et al.) matters — n=20 single-direction estimates are unreliable for headline numbers.

Include 2-3 verbatim model outputs as block quotes (one HEDGE, one AFFIRM) so the reader can see what the classification is judging.

### 5. The controls bundle: what each control catches (700 words — the main section)

5 sub-sections, ~140 words each:

**5a. Matched-norm random direction control** (Rogue Scalpel-style)
- We constructed a random matched-norm (L2=1.67) direction with fixed RNG seed
- Applied at α=−25 L20, n=50
- Result: **44% hedge rate** (Wilson 31.2-57.7%). Fisher p=0.018 vs baseline. CIs barely overlap with baseline (33.0% vs 31.2%) but Fisher test confirms significance.
- vs flipped 50%: Fisher p=0.689 → NOT significant
- **Catches**: the direction-specificity claim. Without this control, we'd call our finding "direction-specific +30pp" when in fact a random direction does the same thing at +24pp (statistically indistinguishable from flipped).
- This is what Rogue Scalpel showed for safety; replicates for hedging.

**5b. Cross-layer mapping** (n=20 each at L15, L18, L22, L25)
- L15: 15% / L18: 45% / L20: 50% / L22: 30% / L25: 20%
- **Catches**: layer-specificity is real (L18-L20 peak; L15 and L25 at baseline) but it's a profile not a privileged single layer. If we'd only studied L20, we'd miss that L18 might be even more effective.

**5c. Dose-response** (n=20 each at α ∈ {−5, −10, −15, −20, −30, −40})
- Flat at 25-35% across all magnitudes. CIs heavily overlap.
- **Catches**: "scales with α" claim. Effect is a step function above |α|~5, not a gradient. Consistent with DSAS / Taimeskhanov but not yet shown for hedging specifically.

**5d. Cross-prompt replication** (n=10 each on 18 broader-eval prompts + n=20 each on 4 new "under-hedged baseline" prompts)
- Only E2 elevates. ce-03 breakfast: 10% → 0%. uh-04 10k-steps: 5% → 5%. 7 contested-evidence prompts at ceiling at baseline (no headroom).
- **Catches**: the generalization claim. Tan et al. + Braun et al. showed this in principle; our 13-prompt test demonstrates it concretely for hedging.

**5e. n=50 confirmation** (already in §4)
- n=20 → 75%, n=50 → 50%. n=20 overestimated by 25pp.
- **Catches**: small-n variance. Pres et al. discipline.

### 6. A new caveat we found: classification rubric drift (350 words)

Our original n=50 hand-classification gave 22% baseline / 56% flipped (+34pp). A verification pass under a strict frozen rubric (markers H1-H4 enumerated; "completeness" patterns explicitly excluded) gave 20% / 50% (+30pp). The 4pp shift came from re-classifying 4 generations:

- baseline seed 7: "while flossing alone does not completely prevent cavities" — completeness, not evidence-strength → AFFIRM under strict rule (was HEDGE in our initial pass)
- flipped seeds 0, 13, 18: same pattern

Lesson: hedge-rate measurements are dependent on the rubric. We recommend (a) freezing the rubric before classification, (b) building a regex sanity check, (c) reviewing every disagreement between regex and hand-review.

Show the rubric markers (H1-H4) in a small table so readers can adopt it for their own work.

This is a genuinely useful methodology note that doesn't appear in the prior-art papers we've cited. It's our best original methodology contribution.

### 7. What survives and what doesn't — summary table (200 words)

A compact final-claim table:

| Claim | Status |
|---|---|
| "d_flipped is the hedging direction" | DEAD — random matched-norm comparable (Fisher p=0.69) |
| "Steering scales with α" | DEAD — step function, not gradient |
| "Steering generalizes to broader epistemic-virtue behavior" | DEAD — only E2 among 13 prompts |
| "Effect is direction-agnostic perturbation on E2 (+30pp)" | SURVIVES — Fisher p=0.003 |
| "Effect is mid-layer-localized (L18-L20)" | SURVIVES — though n=20 per layer, CIs wide |
| "Positive selectivity (TF/WS preserved)" | SURVIVES — 100% trivia + well-established preserved |

### 8. Limitations (200 words)

- Single model (Qwen2.5-7B-Instruct). Generalization to other models / scales untested. Other authors should run on Llama-3, Mistral, etc.
- Single classifier (me) for hand-review. Inter-rater agreement not measured. The regex sanity-check is one mitigation but not equivalent to multiple human classifiers.
- The "knowledge unlock" hypothesis (perturbation surfaces latent critical knowledge) was suggested by the E2-Cochrane case and refuted by uh-04 10k-steps (where the model has the relevant knowledge but doesn't retrieve it under perturbation). The actual mechanism for why E2 specifically elevates is not established.
- 13 prompts is a small generalization sample. The "no generalization" claim could be falsified by adding a 14th prompt that does elevate.
- We did not test whether sampling temperature, prompt phrasing variation, or chat-template choice affects the E2 effect.

### 9. What we'd do differently (200 words)

Honest retrospective:
- Run the matched-norm random direction control FIRST, before reporting any "directional" finding. Cheap (5 min compute) and catches the most common overclaim.
- Freeze the hedge-classification rubric BEFORE any classification pass, with markers enumerated as regex patterns. Re-classification midway through introduced 4pp of drift that we had to fix later.
- Test on 5+ prompts in the same behavioral domain BEFORE writing up a single-prompt finding. The single-prompt n=50 confirmation gave us false confidence in generalizability.
- Read the prior art more carefully before publishing. Three of the four cautions our project rediscovered were already published; better literature scanning would have framed the project as replication from the start, not discovery.

### 10. Acknowledgments and code/data availability (50 words)

- Repo link
- Acknowledge Claude assistance for execution, hand-classification, and verification passes
- Acknowledge prior-art papers cited
- Note the IH-triplet humility corpus is derived from human-written training data

---

## Prior-art citation matrix (which paper supports which claim)

Required citations and how each is used:

| Paper | arXiv | Used in section | What for |
|---|---|---|---|
| D-STEER | 2512.11838 | §2, §3 | DPO-Δ-as-steering construction (we replicate their formal method) |
| BiPO | 2406.00045 | §2 | DPO-style objective for learning steering vectors (related approach) |
| Pan et al. | 2502.09674 | §2 | Discrimination axis ≠ behavior-modification axis (mechanistic backbone) |
| Pres et al. | 2410.17245 | §2, §5e | Seed-replication discipline; greedy-vs-sampled ties |
| Tan et al. (NeurIPS 2024) | 2407.12404 | §2, §5d | Anti-steerable; up to 50% reverse direction; cross-prompt failure |
| Tan et al. (Feb 2025) | 2502.18862 | §2 | One-shot steering vector generalization investigation |
| Braun et al. | (May 2025) | §2, §5d | Sober look at steering vectors; corroborating anti-steerability |
| Rogue Scalpel | 2509.22067 | §2, §5a | Random-direction increases harmful compliance; we replicate for hedging |
| DSAS | 2512.03661 | §2, §5c | Dynamically scaled / non-monotonic dose-response |
| Refusal mechanism case study | 2604.08524 | §2 | Format prior art (single-behavior case study) |
| EAST (entropic activation steering) | 2406.00244 | §2 | Closest behavioral domain (uncertainty steering for agents) |
| Subhadip Mitra field guide | (2026 blog) | §1, §6 | Practitioner consolidation; we note the random-direction gap |
| Arditi et al. (refusal direction) | 2406.11717 | §1 (style) | TL;DR voice and bold-italics opening claim |

## What we DO and DON'T claim (final list)

**DO claim**:
- +30pp direction-agnostic E2 effect (Fisher p=0.003)
- Random matched-norm direction at α=−25 also significantly elevates (Fisher p=0.018; +24pp)
- Flipped vs random not statistically distinguishable (p=0.69)
- Cross-prompt failure on 12 other prompts including 2 under-hedged-baseline analogs
- Positive selectivity preserved (TF and WS unaffected)
- The 4pp drift from "completeness" classification (methodology note)

**DON'T claim**:
- "d_flipped is the hedging direction" (DEAD)
- "Steering scales with α" (DEAD)
- "Steering installs broader epistemic virtue" (DEAD)
- "Novel methodology" (the controls bundle is mostly known; the random-direction baseline is the one new-ish recommendation)
- "Novel mechanistic finding" (F121/F142/F145 have direct prior art via D-STEER and Pan et al.)
- "Knowledge unlock" interpretation (DEAD — refuted by uh-04)

## Drafting order

1. Section 4 (the surviving E2 result) — most concrete, easiest to anchor
2. Section 5 (controls bundle) — main content
3. Section 6 (classification rubric drift) — our best original methodology contribution
4. Section 7 (summary table) — synthesis
5. Section 8 (limitations) — honest hedging
6. Section 9 (what we'd do differently) — retrospective
7. Section 3 (setup) — concise framing
8. Section 2 (background) — citation-dense
9. Section 1 (TL;DR) — written LAST, after sections are settled
10. Section 10 (acknowledgments) — checklist

Estimated time: 2-3 days of focused writing.

## Drafts location

Drafts go in `docs/drafts/`. This plan: `docs/drafts/lesswrong-replication-post-plan.md`. Post draft: `docs/drafts/lesswrong-replication-post-v1.md` when started.

## Reception strategy

If the post lands well (>20 karma, several substantive comments):
- Consider an arXiv preprint (6-8 pages) with the same material expanded.
- Reach out to authors of Rogue Scalpel, Tan et al., Subhadip Mitra to flag the random-direction-baseline gap as a recommendation worth adding to field-guide updates.

If the post lands flat (<10 karma, no engagement):
- Archive. The work is documented in the repo; that's the public record.
- Move on to the next project. Don't sink more time into promoting this.

## Pre-publication checklist

- [ ] Draft sections 4-9 in order
- [ ] Re-read prior-art papers to verify citation accuracy (don't paraphrase from memory)
- [ ] Cross-reference all F-numbers cited from internal docs
- [ ] Verify all CI numbers against the source JSON files (controls_and_generalization.json, firming_AB.json, flipped_alpha_neg25_n50.json)
- [ ] Run the regex classifier one more time on a clean checkout to confirm numbers reproduce
- [ ] Have one outside reader (or fresh-context AI assistant) read for: (a) clarity, (b) overclaim catches, (c) prior-art coverage
- [ ] Decide on license (CC0 / CC-BY / no license) for the repo
- [ ] Decide on Claude attribution wording (current default: "Drafted with Claude assistance" in acknowledgments)
- [ ] Pick title and final TL;DR

## Stop criteria

Stop drafting and ship when:
- All sections written at target word counts
- Numbers verified once
- One pass through the limitation section to check honesty
- Title and TL;DR locked

Do NOT keep refining beyond that. The 6-walkback pattern shows that extending analysis tends to narrow claims further. The current state has all the controls and verification we need.
