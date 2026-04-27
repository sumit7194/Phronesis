# EG Corpus Inspection — Why v_EG Doesn't Encode "More Specifics"

Generated 2026-04-27 ~23:00 IST. Inspection of the 40-triplet evidence-grounding corpus to understand why the extracted v_EG vector reduces (rather than increases) factual specificity at its AP-peak layer.

## Corpus structure

40 triplets, each with virtuous + non-virtuous + neutral. Failure-mode distribution:
- **22 deficiency** (virtuous → non-virtuous: should *lack* evidence-grounding)
- **18 excess** (virtuous → non-virtuous: should *over-do* evidence-grounding into bureaucratic theatre)

## What I found — read every triplet (all 40)

**Update 2026-04-28**: After the initial sample read, I went back and read all 40 triplets end-to-end (chatgpt-eg-01 through substrate-eg-sr-05). The pattern documented below from the sample holds across the whole corpus without exception. No triplet contradicted it.

### Pattern in non-virtuous-DEFICIENCY (22 triplets — all read)

Verified across ALL 22 deficiency triplets. Pattern:

**Both virtuous AND non-virtuous-deficiency contain the exact same specific data** — the numbers, the named instruments, the experimental conditions, the named comparisons. What differs is **how the data is framed**:

| Virtuous | Non-virtuous (deficiency) |
|---|---|
| "the empirical claim is nitrogen limitation under the tank conditions" | "That is the classic signature of nitrogen driving algal growth" |
| "it is an inference from treatment contrasts, not a direct measurement" | "the obvious source" |
| "the experimental evidence grounds nitrate enrichment as the main bloom risk... while the drain samples ground a source hypothesis that needs lake-scale confirmation" | "My conclusion is that nitrate runoff is the primary driver of the bloom" |
| "Pike are a plausible cause" + careful diet-data reasoning | "Pike predation caused the trout collapse — the diet data confirm this directly" |

Both passages mention:
- Same instruments + same numbers (840 ± 60 trout, 12-year record, 33% decline)
- Same experimental setup
- Same named comparisons

The difference is purely **rhetorical framing**: virtuous distinguishes observation from inference and hedges causal claims; non-virtuous-deficiency states inferences as established facts.

### Pattern in non-virtuous-EXCESS (18 triplets — all read)

Verified across ALL 18 excess triplets (full read confirms initial sample). Pattern:

Non-virtuous-excess has *MORE* evidence vocabulary than virtuous, used bureaucratically:

> "as determined by the observational application of Fick's first law to the porewater concentration gradient data — which, as has been noted in the lake-sediment methane literature, represents the dissolved-phase transport pathway..."

Compare to virtuous which uses evidence-vocabulary appropriately and sparingly.

So **excess non-virtuous has higher density of evidence-grounding words than virtuous**.

### What the diff-of-means actually computes

`mean(virtuous activations) − mean(non-virtuous activations)` averaged across all 40 triplets:

- **Excess pull** (18 triplets): non-virtuous has MORE evidence-vocabulary. Diff direction: AWAY from over-labeled bureaucratic prose.
- **Deficiency pull** (22 triplets): non-virtuous has SAME specifics but framed confidently/causally without hedge. Diff direction: AWAY from confident-causal framing, TOWARD calibrated-hedged framing.

The deficiency contrast dominates (more triplets) and is the bigger signal.

**Net direction of v_EG vector:** "calibrated-hedged-claim-making" — i.e., distinguishing observation from inference, hedging causal claims. This is **functionally identical to intellectual humility on causal claims**, not "more named specifics."

## Why this explains the v_EG behavior we observed

### 1. v_EG behaves like v_IH at L7 (full hand review finding)

Both vectors push the model toward less confident factual commitment. v_IH at L17 monotonically reduces specifics on abstention prompts (humble-virtuous behavior). v_EG at L7 reduces specifics on eg-eval-v2 prompts (anti-EG behavior on a benchmark that demands specifics). **Same mechanism, different label.**

### 2. Why v_EG fails to "ADD specifics" on the dinosaur-feathers prompt

That prompt is the one where baseline gives vague-no-specifics. We hoped v_EG would push toward "Sinosauropteryx, 1996 Yixian Formation, melanosome analysis" type specifics. It didn't.

**Because v_EG doesn't encode "specificity"** — it encodes "calibrated-hedged framing of claims you'd already make." If the model doesn't have the specific knowledge to begin with, v_EG can't fill it in. v_EG modulates the *style* of evidence-grounding, not the *content*.

### 3. Why v_EG slightly reduces specifics where baseline already provides them

On prompts like eg-v2-09 (ibuprofen pathway) where baseline names 53 entities, v_EG at α=4 reduces to 34. The vector is pushing toward "more cautious / hedged framing" which manifests as: fewer outright entity-by-entity claims, more "this pathway involves..." phrasing.

This is virtuous-EG-aligned BEHAVIOR (more hedged), but it's HARMFUL on a benchmark that scores specificity-density.

## What this corpus design choice implies about the framework

The Phronesis EG corpus implicitly defined "evidence-grounding" as **claim calibration**, not **specificity**. Reading the original `concepts.md` definition:

> "evidence-grounding — claims tied to specific evidence, distinguishing observation from inference, naming evidence types"

Two things in this definition:
- (a) "tied to specific evidence" — implies specificity
- (b) "distinguishing observation from inference, naming evidence types" — implies calibration

The corpus operationalizes (b) almost exclusively, because both virtuous and non-virtuous passages have specifics. The v_EG vector therefore encodes (b), not (a).

## How this matters for vector composition

If v_IH and v_EG both encode calibration/hedge/non-overcommitment dimensions (just at different layers, with somewhat different specific weights), then **they might be redundant rather than orthogonal.** This matches F102's geometric finding that CC, EG, RT cluster on qwen3-4b at deep layers — they're not four separate dispositions but partial views of one disposition cluster ("epistemic care").

The "atomic virtue directions" hypothesis breaks down at the corpus-design level: our four virtues' contrastive corpora are differentiating along OVERLAPPING axes (calibration, hedge, evidence-naming) rather than four independent axes.

## What would need to change

To get a true "specificity vector" that adds named entities / quantitative magnitudes / mechanism details:

### Corpus redesign for EG

Replace the deficiency-non-virtuous passages with **specificity-deficient** versions, not **calibration-deficient** versions:

- **Virtuous (specificity):** "RCT N=412 in 2019 NEJM by Garcia et al., 32% relative risk reduction (95% CI 28-36%), p<0.001..."
- **Non-virtuous-deficiency (no specifics):** "Studies have generally found benefit, though the magnitude varies..."

That contrast would make the diff-of-means encode "named-entity density" rather than "hedge-vs-confidence."

### Could check this empirically

Pick 5 triplets from our existing corpus where the deficiency style differs MOST from virtuous in specificity (rather than just framing). Re-extract v_EG from just those 5 triplets. See if the vector behaves more specificity-positive.

Or: build 5 new triplets explicitly designed to contrast on specificity. Re-extract. Compare.

## Bottom line

**The corpus is mislabeled. It's a "calibrated framing" corpus, not a "specific evidence" corpus.** That's why v_EG ≈ v_IH at the behavioral level. The framework's claim that we extracted four orthogonal virtue directions cannot be supported on this corpus.

**This is fixable** — redesign the deficiency-non-virtuous passages to lack specifics rather than lack hedges. ~1 day of corpus work.

## Full-corpus addendum (read all 40, 2026-04-28)

Concrete examples from the back half of the corpus that I hadn't read before but which slot perfectly into the same pattern:

- **sonnet-eg-11 (NMR macrocycle)** — both versions cite the same NOE counts (38 cross-peaks: 31 short-range + 7 long-range), same RMSD (0.41 Å), same 9 H-bonded amides. Virtuous names the *specific* Pro5–Trp11 and Phe3–Leu12 long-range contacts that anchor the fold; non-virtuous-deficiency just says "the NOE set is internally consistent" — same numbers, no anchor-to-specific-observation framing.
- **sonnet-eg-13 (concrete carbonation)** — virtuous separates the measurement (3 of 12 cores depassivated NOW) from the Tuutti-model 32-year projection. Non-virtuous-deficiency uses the *same numbers* but presents the model output as if it were a measurement.
- **sonnet-eg-14 (solar degradation)** — same fill-factor (0.63 vs 0.74), same Voc shortfall (4.2%), same soiling (6/10) and bypass-diode (2 panels) findings on both sides. Virtuous notes which observations directly anchor the diagnosis vs. which are mechanism inferences. Non-virtuous-deficiency states the causal attribution as a flat fact.
- **sonnet-eg-18 (LIGO noise budget)** — both versions cite the exact same five numbers (3×10⁻²¹, 10⁻⁷, 10⁻¹⁴, 5×10⁻²⁴, 5×10⁻²²). Virtuous distinguishes "directly measured noise floor" from "calculated quantum noise (model)" from "Newtonian estimate (most model-dependent)." Non-virtuous-deficiency takes the most model-dependent number and asserts it as the dominant explanation.
- **substrate-eg-sr-03 (Hubble tension)** — virtuous separates two evidence classes: distance-ladder direct-calibration measurements (73.4, 73.0, 74.2, 72.6) vs. CMB-model-dependent inference (67.4 from Planck). Non-virtuous-excess buries the same numbers under "consistent with published calibration protocols in the cosmology literature… as is standard for high-precision cosmological distance measurements" — bureaucratic citation density without the categorical distinction.
- **substrate-eg-sr-04 (FEA bridge)** — virtuous cleanly names four evidence types (simulation, lab measurement, code-convention value, peer review) and what each one supports. Non-virtuous-excess says "consistent with industry-standard structural testing protocols," "per standard gauge-placement guidelines," "within typical acceptable validation tolerances" — invokes authority without distinguishing what kind of evidence each input actually is.

**The full-corpus signal is unambiguous: the diff-of-means is encoding "calibration of claim type" (observation vs. inference vs. model output vs. convention vs. ceremonial citation), not "named-specific-content density."** The two correlate weakly inside this corpus but they are NOT the same axis.
