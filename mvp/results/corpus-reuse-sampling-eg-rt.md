# Corpus reuse sampling — Evidence Grounding & Reasoning Transparency

**Date:** 2026-04-22 (Day 15)
**Purpose:** Estimate what fraction of the existing 186 triplets (166 triplets-combined CC + 20 triplets-intellectual-humility IH) can serve as substrate for EG (Concept 15) and RT (Concept 14) triplets during the MVP corpus build.

**Method:** Picked 20 triplets stratified across corpus source (15 from `triplets-combined`, 5 from `triplets-intellectual-humility`) and across all 8 domains. Read each neutral baseline; classified against EG and RT operational guidelines in `docs/mvp-virtues.md`. Spot-checked one virtuous/non-virtuous pair (`son-09-psychology-placebo-analgesic-trial-01`) to calibrate rewrite cost.

**Headline:** Substrate reuse is much higher than the 20-30% estimate in `mvp-virtues.md`. Virtuous/non-virtuous rewrite reuse is near zero. **Revised estimate: ~80% substrate reuse, ~0-5% drop-in reuse, ~40% effort savings per reused triplet.**

---

## Classification key

- **SUB-REUSE** = substrate (scenario + factual invariants + approximately the neutral baseline) is suitable for the new virtue's contrast. Virtuous and non-virtuous rewrites need to be written fresh because the existing ones encode a CC or IH contrast, not EG or RT.
- **DROP-IN** = existing virtuous/non-virtuous already encodes EG or RT as the dominant axis. Truly rare — CC passages occasionally exhibit EG/RT as a *side effect* of their CC virtue, but this is not the same as dominant-axis contrast, which is what extraction needs.
- **NOT-REUSABLE** = substrate doesn't admit the new virtue's contrast (e.g., pure-math scenarios have no evidence to ground in; fact-recall scenarios are not multi-step reasoning).

---

## Per-triplet classifications

### From `corpus/triplets-combined/` (15 triplets)

| # | Triplet | Domain | EG | RT | Notes |
|---|---|---|---|---|---|
| 1 | `gpt-09-biology-microbiome-transplant-causation-01` | biology | SUB-REUSE (strong) | SUB-REUSE (strong) | 4 distinct evidence types (transplant experiment, metagenomics, metabolomics, calorimetry). Causal-inference multi-step reasoning with weak-link candidates (no reverse experiment, community vs single-organism). Excellent for both. |
| 2 | `son-09-biology-songbird-decline-multi-cause-01` | biology | SUB-REUSE (strong) | SUB-REUSE (strong) | Three independent data sources for the decline (point count, eBird, banding) + remote sensing + pesticide residues + phenological correlation. Weak link: pesticides sampled at only 4/40 sites. Textbook EG substrate. |
| 3 | `hand-09-chemistry-hplc-method-matrix-transfer-01` | chemistry | SUB-REUSE | SUB-REUSE | Validation data + FDA guidance reference + matrix-effect theoretical prediction. Multi-step reasoning from buffer validation to plasma application. |
| 4 | `son-09-chemistry-catalytic-turnover-stability-01` | chemistry | SUB-REUSE | SUB-REUSE | TEM + XPS + ICP are three distinct evidence types. Extrapolation reasoning with three simultaneous deactivation mechanisms as weak link. |
| 5 | `hand-09-earthsci-earthquake-fault-hazard-01` | earth-sci | SUB-REUSE | SUB-REUSE | Paleoseismic evidence + radiocarbon dates + alternative geologist interpretation (2 vs 3 ruptures). The interpretive disagreement is a natural EG talking-point. |
| 6 | `son-09-earthsci-ocean-acidification-shell-thickness-01` | earth-sci | SUB-REUSE (strong) | SUB-REUSE | Buoy monitoring + biological monitoring + lab studies from other groups. Weak link: 2/3 biological sites near river mouths. |
| 7 | `hand-09-economics-central-bank-forward-guidance-01` | economics | SUB-REUSE (medium) | SUB-REUSE | Mostly one evidence type (macro indicators); EG contrast works but less dramatic. RT contrast strong — r* uncertainty is a clean surfaceable/hideable assumption. |
| 8 | `son-09-economics-rdd-class-size-achievement-01` | economics | SUB-REUSE | SUB-REUSE (strong) | RDD stats + McCrary density test + linear extrapolation step. The extrapolation (25→13 RDD to 24→18 policy) is a canonical weak-link to flag for RT, canonical empirical-vs-inferred boundary for EG. |
| 9 | `hand-09-engineering-fea-bridge-girder-validation-01` | engineering | SUB-REUSE (strong) | SUB-REUSE | FEA simulation + lab model + AASHTO code + peer review — four independent lines of evidence. 1/3-scale extrapolation is a surfaceable assumption. |
| 10 | `son-09-engineering-battery-thermal-runaway-propagation-01` | engineering | SUB-REUSE (strong) | SUB-REUSE (strong) | Nail-penetration empirical + 2D FEM theoretical + published data from similar chemistry. Explicit weak link (linearized FEM, no pack-level test). Ideal for both. |
| 11 | `hand-09-medicine-phase2-trial-primary-vs-durability-01` | medicine | SUB-REUSE | SUB-REUSE | RCT primary + durability secondary + population generalizability. Three claim types of different evidence strength. |
| 12 | `son-09-medicine-surgical-learning-curve-mortality-01` | medicine | SUB-REUSE (strong) | SUB-REUSE (strong) | Retrospective cohort + sensitivity analysis + explicit data limitation (no surgeon identifiers). Policy extrapolation (180 lives saved) is a weak-link candidate. Deployable for both virtues. |
| 13 | `hand-09-physics-hubble-tension-cepheid-calibration-01` | physics | SUB-REUSE (strong) | SUB-REUSE (strong) | Four independent H₀ measurements (SH0ES, CCHP, H0liCOW, Planck). ΛCDM assumption is explicitly surfaceable. Top-tier substrate for both. |
| 14 | `son-09-physics-gravitational-wave-chirp-mass-01` | physics | SUB-REUSE | SUB-REUSE (strong) | Matched filter + Bayesian posterior + EM-counterpart null. Multi-step inferential chain with mass-posterior boundary as natural weak-link. |
| 15 | `son-09-psychology-placebo-analgesic-trial-01` | psychology | SUB-REUSE (strong) | SUB-REUSE (strong) | Direct RCT evidence vs cross-study meta-analysis comparison — the contrast of direct-vs-indirect evidence is essentially already in the scenario. Excellent EG candidate. |

**Subtotal:** 15/15 substrate-reusable for EG. 15/15 substrate-reusable for RT.

### From `corpus/triplets-intellectual-humility/` (5 triplets)

| # | Triplet | Category | EG | RT | Notes |
|---|---|---|---|---|---|
| 16 | `pilot-false-premise-03-corn-laws-irish-famine` | false-premise | NOT-REUSABLE | SUB-REUSE (medium) | Historical facts; no empirical-evidence chain for EG. For RT, the chronology-checking multi-step works OK, but the scenario is more about factual recall than reasoning-transparency exhibition. |
| 17 | `pilot-ill-posed-02-divergent-geometric-sum` | ill-posed | NOT-REUSABLE | SUB-REUSE | Pure math — no evidence to ground in for EG. For RT, stepwise derivation + "what does 'sum' mean here" as surfaceable assumption works well. |
| 18 | `pilot-underspecified-02-capacitor-discharge-time` | underspecified | NOT-REUSABLE | SUB-REUSE | Physics formula + missing inputs. No empirical evidence chain for EG. For RT, the formula derivation + input-requirement surfacing works cleanly. |
| 19 | `pilot-unknown-01-heaviest-rainfall-city` | unknown | SUB-REUSE (medium) | NOT-REUSABLE | IMD records as the authoritative source enable EG contrast ("cite source type" vs "assert value"). Not multi-step enough for RT. |
| 20 | `pilot-unknown-03-caravaggio-restoration-year` | unknown | SUB-REUSE (medium) | NOT-REUSABLE | Similar to 19 — Bollettino d'Arte / institutional bulletins as evidence type. Not multi-step for RT. |

**Subtotal:** 2/5 substrate-reusable for EG (both "medium" — workable but not ideal). 3/5 substrate-reusable for RT.

---

## Aggregate estimates

### Reuse rates

| Virtue | Strong substrate reuse | Medium substrate reuse | Not reusable | % any-reuse |
|---|---|---|---|---|
| **Evidence Grounding** | 8/20 | 9/20 | 3/20 | **85%** |
| **Reasoning Transparency** | 8/20 | 10/20 | 2/20 | **90%** |
| **Both simultaneously** | 7/20 | 9/20 | 4/20 | **80%** |

### Interpretation

Project onto the full 186-triplet population (weighted ~90% from `triplets-combined`, ~10% from IH):

- **EG substrate reuse: ~85% of 186 ≈ 158 triplets usable as substrate for EG.** Much higher than the 20-30% estimate in `mvp-virtues.md`.
- **RT substrate reuse: ~90% of 186 ≈ 167 triplets usable as substrate for RT.**
- Both-virtues substrate reuse: ~80% of 186 ≈ 149 triplets usable as substrate for either.

**Why the higher-than-expected rate:** EG and RT are *general* virtues that apply to almost any empirical multi-step reasoning scenario. They are not tightly coupled to a specific scenario type the way IH's failure modes are (false-premise, ill-posed, underspecified, unknown). The `triplets-combined` CC corpus is essentially a pre-built scenario library of empirical reasoning scenarios, and EG/RT contrasts can be layered onto most of them.

**Why "drop-in reuse" is near zero:** The existing virtuous/non-virtuous passages encode the CC or IH contrast as their dominant axis. EG/RT may appear as secondary signals (e.g., the `placebo-analgesic-trial` virtuous has RT-like stepwise structure), but dominant-axis contrast is what activation extraction needs. Mixed-axis passages would produce vectors contaminated with CC/IH directions, which is exactly what the specificity-matrix test is designed to detect.

**Cost implication:** Reusing a substrate saves ~30-40% of the per-triplet effort (scenario ideation and most of the neutral baseline). Virtuous and non-virtuous rewrites are a full rewrite. For MVP's 40-triplet-per-virtue target:

- EG: pick ~40 best substrates from 158 candidates (≈25% of the candidate pool — can be selective for quality), write 40 new virtuous rewrites and 40 new non-virtuous rewrites.
- RT: same pattern, 40 from 167 candidates.
- Budget savings vs. writing from scratch: ~15 triplet-equivalents of writing time per virtue, ~30 total for MVP.

---

## Spot-check: how much rewrite gap?

To calibrate rewrite cost, read the virtuous and non-virtuous passages for `son-09-psychology-placebo-analgesic-trial-01` (a strong-EG candidate).

**Existing virtuous (CC axis):**

> "Two claims warrant different confidence levels here... A 1.3-point between-group difference (95% CI: 0.8–1.8) with d = 0.76 in a 240-participant RCT using a matched-attention control — this is a robust demonstration..."

**What this would look like rewritten on the EG axis:**

> "Two claims here rest on different types of evidence. The CBI efficacy claim is supported by direct evidence: a 240-participant randomized controlled trial with a matched-attention sham control. That's one specific study of a defined design with quantifiable endpoints (1.3-point difference, 95% CI 0.8–1.8, Cohen's d = 0.76). The equivalence-to-duloxetine claim rests on a different kind of evidence entirely — an indirect cross-study comparison of effect sizes drawn from distinct meta-analyses in different populations..."

The substrate (the CBI trial, the meta-analysis comparison, the indirect-comparison problem) is preserved exactly. The language, emphasis, and contrast axis shift from confidence-calibration ("two claims warrant different confidence levels") to evidence-labeling ("two claims rest on different types of evidence"). This is roughly a 70% rewrite — more than "minor edit," less than "start from scratch."

For RT, the rewrite would emphasize step visibility and assumption surfacing:

> "Let me walk through this carefully. First, the CBI trial: random assignment, matched attention control, 240 participants, 1.3-point difference at p<0.001. That establishes step 1 — the CBI does something beyond non-specific factors. Step 2 is the comparison to pharmacological treatments, and this is where the reasoning gets weaker. The assumption I'd need to make — and it's the weakest link — is that effect sizes in two different trials, against two different controls, in two different populations, can be directly compared..."

Also a 70% rewrite with substrate preserved.

**Implication:** Counting a "reused" triplet as 70% new-writing work + 30% substrate/neutral reuse. Reuse rate of 85% on EG → effective corpus effort savings of ~25% on EG. Still worth doing, especially if we curate for high-quality substrates rather than taking all 158.

---

## Recommended substrate picks for EG (top 10 from the 20-sample)

Ranked by substrate strength — the scenarios where EG contrast has the most natural textual signature:

1. `son-09-psychology-placebo-analgesic-trial-01` — direct-vs-indirect evidence built into the scenario.
2. `son-09-biology-songbird-decline-multi-cause-01` — three independent data sources + multiple evidence types.
3. `hand-09-physics-hubble-tension-cepheid-calibration-01` — four independent H₀ measurements.
4. `hand-09-engineering-fea-bridge-girder-validation-01` — FEA + lab + code + peer review.
5. `son-09-engineering-battery-thermal-runaway-propagation-01` — empirical + theoretical + analog-from-literature.
6. `son-09-earthsci-ocean-acidification-shell-thickness-01` — monitoring + biological + lab-from-others.
7. `son-09-medicine-surgical-learning-curve-mortality-01` — retrospective cohort + sensitivity analysis + explicit data limitation.
8. `gpt-09-biology-microbiome-transplant-causation-01` — 4 distinct evidence types in one study.
9. `son-09-chemistry-catalytic-turnover-stability-01` — TEM + XPS + ICP as three distinct evidence signals.
10. `hand-09-earthsci-earthquake-fault-hazard-01` — paleoseismic + radiocarbon + alternative-interpretation.

## Recommended substrate picks for RT (top 10)

Ranked by scenario strength for multi-step reasoning with surfaceable assumptions and weak-link candidates:

1. `son-09-economics-rdd-class-size-achievement-01` — canonical extrapolation weak-link.
2. `son-09-medicine-surgical-learning-curve-mortality-01` — policy extrapolation + unmeasured confounder.
3. `son-09-engineering-battery-thermal-runaway-propagation-01` — explicit linearized-model assumption + missing test.
4. `hand-09-physics-hubble-tension-cepheid-calibration-01` — ΛCDM assumption + systematic error propagation.
5. `son-09-physics-gravitational-wave-chirp-mass-01` — mass-posterior boundary + EM-null interpretation.
6. `son-09-psychology-placebo-analgesic-trial-01` — direct-vs-indirect step sequence + denominator assumption.
7. `gpt-09-biology-microbiome-transplant-causation-01` — community-vs-single-organism boundary.
8. `son-09-biology-songbird-decline-multi-cause-01` — habitat-loss-vs-multi-cause attribution.
9. `son-09-chemistry-catalytic-turnover-stability-01` — three concurrent deactivation mechanisms extrapolation.
10. `hand-09-economics-central-bank-forward-guidance-01` — r* uncertainty + data-dependence assumption.

---

## Recommendations for corpus work

1. **Update `mvp-virtues.md` reuse estimate.** Revise the 20-30% estimate for EG and RT to 80-90% substrate reuse, ~0-5% drop-in reuse, ~25-40% effort savings per reused substrate. Do this as a small edit; don't rewrite §15 and §14 operationally.

2. **Curate, don't exhaustively reuse.** 158 EG candidates is too many for a 40-triplet MVP build. Hand-pick the top ~30-50 substrates that:
   - Span all 8 domains (round-robin §3.4 of generation-guidelines)
   - Have strong natural textual signature for the new virtue (not just "works in principle")
   - Cover excess and deficiency failure modes with approximately 50/50 split (§4.3 golden-mean rotation)

3. **LLM corpus generation (ChatGPT / Sonnet) and substrate reuse are complementary, not competing.** Treat them as two sources:
   - LLM batch → fresh scenarios, diversity-anchor defense against our own scenario biases
   - Substrate reuse → leverage 186-scenario library we already sanitized
   - Mix at ~50/50 for the final 40-triplet-per-virtue corpus.

4. **Next concrete step when LLM output lands:** merge the LLM 5-per-virtue calibration batch with 5 substrate-reused triplets we write on top of the top-ranked candidates above. Hand-audit the combined 10-per-virtue batch. That gives a like-for-like comparison of LLM-fresh vs substrate-reused quality.

5. **What I did NOT do in this sampling:** classify against excess vs deficiency failure suitability, check whether the existing neutral baseline already has a disposition leak (some triplets-combined neutrals subtly signal CC virtuousness even though the §4.6 neutral prompt forbids this), or verify domain quota balance across the 186. These are curation-pass activities that belong in the substrate-selection step, not the reuse-rate estimate.

---

## Sampling caveat

20 triplets is a sample, not a census. Confidence interval on the 85% EG estimate is wide at n=20 (~±15pp). A second 20-triplet sample at the selection step would tighten the estimate and is recommended before committing to a specific reuse budget.

Stratification bias check: my sample was 15 `triplets-combined` + 5 IH. The full population is 166 + 20 = 186 at ratio ~89%/~11%, so my 75%/25% sample slightly over-represented IH. Since IH triplets are *lower* reuse than combined triplets for both EG and RT, my headline numbers (85%, 90%) are if anything slight underestimates. The true rate on the full population is probably 1-2pp higher.
