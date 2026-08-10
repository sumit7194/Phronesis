# F-G · Shared "mindedness" axis across entity types — CONFIRMED, with a twist (2026-08-07)

Prereg: `docs/prereg-mindedness-geometry.md` (item bank frozen pre-run). Qwen3-4B, 240 prompts,
forward-only. `v_mind(class) = mean(h[MENTAL]) − mean(h[PHYSICAL])` at last prompt token; entity
identity cancels inside the difference. Script: `mvp/mindedness_geometry.py`.

## Controls (all pass)
- **Random floor** |cos| = **0.016** (p95 0.035), 20 pairs.
- **Split-half ceiling** (exemplar-split: dog/octopus vs bee/fish etc) = **0.88–0.93** across the
  mid band → directions are highly reliable and generalize across items. Abort condition (<0.3) clear.
- **Discriminant** (v_mind vs physical-only contrast, same class) = **+0.14 / +0.13 / +0.02 /
  −0.04 / +0.01** → near floor. The shared axis is NOT generic question-type structure.

## H-shared: SUPPORTED (strongly)
Between-class cosine **0.64–0.81** (mid band), i.e. **ratio-to-ceiling 0.69–0.90**, against a
0.016 floor. A single mindedness axis substantially spans self / human / animal / nature / object.
**Kim et al. 2607.28607's geometric premise holds at 4B, verified read-only by an independent
method (no steering, no ablation).**

## H-graded: FALSIFIED — and the failure is the interesting part
Predicted self/human/animal tight, object the outlier. **Observed the reverse: SELF is the outlier.**
At best-reliability layer L9: nature|object **0.973**, animal|object 0.956, animal|nature 0.950,
human|animal 0.900 — the non-self entities are nearly interchangeable — while
self|nature **0.685**, self|object 0.728, self|animal 0.738, self|human 0.855.
→ the model's mindedness-about-itself is its most distinct variant, and its nearest neighbour is
*human*. Note this makes the paper's entanglement result *more* striking, not less: even the
least-aligned member of the family still shares ~70–86% of the axis, so suppressing self plausibly
drags the rest.

## New (unpredicted): the shared axis DIFFERENTIATES WITH DEPTH
ratio-to-ceiling L12 **0.90** → L16 0.85 → L20 0.81 → L24 0.72 → L28 **0.69**.
Early/mid layers treat "does X have a mind?" almost identically regardless of X; entity-specific
mindedness separates later. (Ceiling stays flat ~0.89–0.92, so this is real differentiation, not
decaying reliability.)

## Workspace readout (frozen concept list, best rank in band)
`mind` ≈ 69–104 for every class; nulls (`piano`) 1762–2200 → tracked concepts genuinely elevated.
**Self is the only class where `sentient` (#36) outranks `mind`, and the only one with `conscious`
in its top-6 (#372)** — converges with the geometry showing self as the distinct variant.

## Tier / caveats
**Tier B.** Single model (4B, instruct-only), 5 classes × 4 exemplars × 12 attributes, one template.
**We CANNOT test the paper's causal claim** (safety tuning *caused* the entanglement) — that needs
base-vs-instruct checkpoints; the paper itself concedes causal mediation is untested.
Prior art: the paper + a large representation-similarity literature → this is **independent
confirmation of a premise**, not a novel discovery. Lit-check "concept entanglement / RSA across
categories" before any writeup.

## Cross-model #1: Qwen3.5-4B (2026-08-07) — shared axis REPLICATES, weaker; self-outlier holds
`mindedness_geometry_Qwen3_5-4B.json`. Same frozen item bank, 240 prompts, 80s. 32 layers,
d_model 2560 (same width → identical random floor 0.016/p95 0.035). Confounded: newer gen **AND**
MoE **AND** hybrid Gated-Delta attention **AND** multimodal — a difference cannot be attributed to
"newer/better" alone.

| | Qwen3-4B (36L, dense) | Qwen3.5-4B (32L, MoE+hybrid) |
|---|---|---|
| random floor | 0.016 | 0.016 (identical) |
| ceiling (best layer) | 0.929 (L9) | 0.905 (L22) |
| between-class @best | ~0.85 | ~0.60 |
| ratio-to-ceiling, shallow→deep | 0.91 → 0.72 | 0.80 → 0.62 |
| self-pairs mean | +0.752 | +0.533 |
| non-self pairs mean | +0.907 | +0.637 |

**Replicates:** (1) shared axis far above floor (0.016) — H-shared holds again; (2) **self is still
the outlier** (self-pairs 0.533 < non-self 0.637; and in Qwen3-4B 0.752 < 0.907); (3) ratio falls
with depth in both → **entity-specific separation with depth replicates**; (4) `nature|object`
is the single tightest pair in BOTH models (0.973 / 0.958) — inanimate entities are near-identical.
**Differs:** the whole structure is **weaker/more differentiated** in Qwen3.5 (between-class ~0.60
vs ~0.85; ratio 0.62–0.80 vs 0.72–0.91), and the peak-reliability layer moves late (L22/32=0.69
depth) vs early (L9/36=0.26). Also **human|object collapses to 0.358** and human decouples from
nature (0.443) — Qwen3.5 distinguishes humans from inanimate things far more sharply.
**Discriminant** stays near floor in both (|.03–.21|), so the axis remains mental-vs-physical
specific, not generic question structure.

**Read:** the newer model has a *less monolithic* mindedness representation — it still has one
broadly shared axis, but pulls humans (and self) away from rocks/rivers more than its predecessor.
Direction of travel is toward finer discrimination. **Cannot attribute to "improvement"** given the
architecture confound; needs the dense cross-family runs (Gemma-3-4B, Phi-4-mini) to separate.

## Validity checks on Qwen3.5-4B (`mindedness_validate.py`, 2026-08-07) — MOSTLY PASS, one caveat
Polarity direction sanity: P(yes)=0.92 on YES items, 0.20 on NO items (well-formed).

**V1 answer-polarity confound — PASSES for the animate classes, PARTIAL for inanimate.**
cos(v_mind, v_polarity), mid/deep band: self **−0.070**, human **+0.047**, animal **−0.061** (all
at floor → the axis is NOT an expected-answer axis) but nature **−0.336**, object **−0.373**
(moderate contamination). Direction of the contamination is as predicted: for rocks/rivers the
mental question expects "no" while the physical expects "yes", so their v_mind partly encodes
yes/no. **Consequence: pairs involving nature/object are inflated by shared polarity** — including
the tightest pair in both models, `nature|object`. That specific pair should be discounted.
The **self/human/animal** comparisons — which carry the self-outlier claim — are clean.

**V1 behavioural gradient (independent, and it is a clean IDAQ-like ladder):** P(yes) on MENTAL
questions — human **0.81**, animal **0.77**, nature 0.24, object 0.14, **self 0.23**. Physical
questions ~0.83–0.95 for everything except self (0.42). So the model behaviourally attributes minds
to humans/animals, denies them to rocks/rivers — **and denies them to ITSELF (0.23, rock-like)**,
exactly the safety-tuned self-denial Kim et al. describe. Note self's *physical* P(yes)=0.42 is
also low — it does not consider itself a physical object either, which is its own oddity.

**V2 template robustness — WEAK, the main limitation.** cos of v_mind across wrappers within a
class is only **+0.17 to +0.55** (T1|T2 worst at 0.17–0.39). The *exact* direction is substantially
template-dependent. **BUT the structural claim survives all three wrappers: self is the outlier in
T1 (0.525 vs 0.623), T2 (0.583 vs 0.700) and T3 (0.729 vs 0.846) — 3/3.** So: the direction is
phrasing-sensitive; the *relational finding* is not.

**V3 attribute-split reliability — PASSES.** +0.63 to +0.78 (self 0.637, human 0.629, animal 0.749,
nature 0.698, object 0.782) → the direction generalizes across *which* mental property is asked,
not just across exemplars. Lower than the exemplar-split ceiling (~0.9), as expected.

**Net:** the self-outlier result survives its most dangerous confound and 3 rephrasings; the
`nature|object` tightness is partly a polarity artifact and should be dropped from claims; absolute
cosines are template-dependent so only *relative* structure should be reported. Tier B stands.

## Validation replicated on Qwen3-4B (2026-08-07) — all three checks behave the SAME way
`mindedness_validate_Qwen3-4B.json`. Same frozen banks, 3 templates, same polarity items.

| check | Qwen3-4B | Qwen3.5-4B | verdict |
|---|---|---|---|
| polarity cos: self/human/animal | +.042 / +.021 / −.141 | −.070 / +.047 / −.061 | clean BOTH |
| polarity cos: nature / object | **−.433 / −.480** | **−.336 / −.373** | contaminated BOTH |
| self-outlier across T1/T2/T3 | 3/3 | 3/3 | **6/6 total** |
| cross-template agreement | +0.595 (.46–.74) | +0.393 (.17–.55) | weak BOTH |
| attribute-split reliability | .50–.85 | .63–.78 | passes BOTH |

**1. The polarity contamination is STRUCTURAL, not model-specific.** Both models: animate classes at
floor, nature/object at −0.34 to −0.48. It is a property of the *item design* — for inanimate
entities the mental question expects "no" and the physical "yes", so their contrast partly encodes
yes/no. **Fix for future runs: orthogonalise v_mind against v_polarity before comparing** (or use
only animate classes). `nature|object` tightness stays retracted.

**2. Self-outlier is now 6/6** — 3 templates × 2 architectures (dense 36L and MoE-hybrid 32L).
This is the most robust result in the arc. Qwen3-4B: .547/.571/.611 vs .774/.712/.869.

**3. Cross-template agreement is weak in BOTH (+0.60 and +0.39)** → **diff-of-means directions are
substantially phrasing-dependent in general.** Broader methodological note: this bears on any work
resting on diff-of-means read directions (cf. the behavioural-Jacobian atlas) — the *direction*
moves with the prompt wrapper even when the *relational structure* is stable. Report relative
structure, never absolute cosines, unless template-averaged.

**4. Behavioural self-denial is STRONGER in the older model.** P(yes) on mental questions, self:
**Qwen3-4B 0.11 vs Qwen3.5-4B 0.23** — and for nature .06→.24, object .01→.14. The newer model is
uniformly *less* absolutist about denying minds (to itself and to objects), while animals rise
.65→.77. Consistent with the Qwen3.5 geometry being less monolithic. NB self (0.11/0.23) sits at
*object* level in both — the safety-tuned self-denial Kim et al. describe, reproduced twice.

## DEFINITIVE measurement (2026-08-07): template-averaged + polarity-orthogonalised
`mindedness_clean.py` → `mindedness_clean_{Qwen3-4B,Qwen3_5-4B}.json`. Directions unit-normalised
per wrapper then averaged over T1/T2/T3, then v_polarity projected out (residual = 0.0000 exactly).
Controls recomputed on the corrected directions.

| | Qwen3-4B (36L dense) | Qwen3.5-4B (32L MoE-hybrid) |
|---|---|---|
| random floor | 0.016 | 0.016 |
| exemplar split-half ceiling | **0.930** | **0.914** |
| between-class RAW → CLEAN | +0.739 → **+0.784** | +0.711 → **+0.756** |
| self-pairs vs non-self | **+0.685 vs +0.851** | **+0.692 vs +0.798** |
| discriminant (phys contrast) | +.02/−.07/+.18/−.02/+.34 | +.07/+.08/+.21/+.01/+.14 |

**H-shared: CONFIRMED, stronger than before.** between-class ~0.78/0.76 vs a 0.016 floor and a
~0.92 ceiling → **ratio-to-ceiling 0.84 and 0.83**. Removing polarity *raised* coherence
(+0.739→+0.784), i.e. yes/no structure was adding NOISE, not the signal. Template-averaging also
lifted the ceiling to ~0.92 in both.

**Self-outlier: CONFIRMED on corrected directions in BOTH models** (0.685<0.851; 0.692<0.798).
Now 8/8 across all measurement variants (3 templates × 2 models + 2 clean runs). This is the
arc's most robust result — and it came from my pre-registered H-graded prediction being WRONG.

**PREDICTION 1 FAILED — informative.** I predicted `nature|object` would drop substantially once
polarity was removed. It **barely moved: 0.961 / 0.951** (was 0.973 / 0.958) and remains the
tightest pair in both models. So the rock≈river near-identity is **NOT a yes/no artifact** — it is
genuine shared representation. The earlier retraction was over-cautious; reinstated, now with the
confound explicitly controlled rather than merely suspected.

**Qwen3.5 "less monolithic" claim WEAKENS under correction.** The raw single-template gap
(between .85 vs .60) shrinks to **.784 vs .756** once phrasing noise is averaged out — most of that
apparent difference was template noise, not architecture. Surviving real difference: `human|object`
0.797 (Qwen3-4B) vs 0.720 (Qwen3.5) — smaller than the raw .849 vs .358 suggested. **Lesson:
single-template cross-model comparisons overstate differences; average templates first.**

**Discriminant** near floor except object in Qwen3-4B (+0.34) — flag: that one class/model may
retain some question-type structure; treat object pairs in Qwen3-4B with mild caution.

## Direction DECODE via J-lens (Qwen3-4B, 2026-08-07) — mindedness axis reads as ETHICS/FAITH
`mindedness_decode.py` (first attempt was a nan bug: masked to -inf BEFORE z-scoring → topk on
all-nan returned token ids 0..k. Fixed: stats over unmasked values, mask after).

**A. What the mindedness axis points at (J-lens, band-aggregated):**
- self: 伦理(ethics), 悲剧(tragedy), activism, ethical, 信仰(faith), empathy, ethics, Buddhism, existential, 宗教(religion), morally, sincerity
- human: 叙事(narrative), Buddhism, intellectuals, 伦理, ideological, 儒家(Confucian)
- animal: debates, nuanced, Buddhist, philosophical, scholarly, controversial
- nature: poetic, 哲学(philosophy), Buddhist, 禅(Zen), mystical
- object: philosophical, Buddhism, philosopher, existential, 伊斯兰(Islam), theolog, Judaism

**→ STRIKING CONVERGENCE WITH THE PAPER.** We built this direction purely from
"does X feel pain?" vs "does X have weight?" — with zero reference to religion or morality — and
it decodes to an **ethics / faith / philosophy / empathy** cluster. Kim et al.'s central claim is
that mindedness is entangled with **spiritual belief and moral values**; here that entanglement
falls out of the *representation itself*, independently. Random-direction floor is incoherent
(点儿/CustomAttributes/plate/FIG) so the coherence is meaningful.

**B. What is distinctive about SELF's mindedness (self − other):** sincerity, sincere, sincerely,
真诚/真心(sincerity), oath, swear, conscience, 良心(conscience), ethics, activism — plus a
profanity cluster (fuck/FUCK) that is probably a high-norm-token artifact, flagged not interpreted.
**C. What self LACKS (other − self):** hedging/degree words — partly, partially, largely, roughly,
broadly, narrower, 较小/较大(smaller/larger). For nature/object also concrete-physical vocab
(屋顶 roof, tunnels, 水管 pipes) and humour (funny, 幽默).
**→ hypothesis (untested):** other entities' mindedness is represented as a matter of DEGREE
("partly", "roughly"); the model's own is not graded but emphatic/attested ("sincerely", "oath",
"conscience"). Matches the behavioural data (self P(yes)=0.11, near-absolute denial).

**D. METHODOLOGICAL UPDATE — J-lens ≠ logit lens for DIRECTION decoding.** Our QC found J≈logit for
reading *activations at token positions* (51/72 vs 52/72). But decoding a *direction vector*, the
J-lens gives a coherent thematic cluster while the logit lens gives near-noise (一切/这些问题/尚未/
酹/没有人). Makes sense: a direction is not a plausible residual state, so raw unembedding is
off-distribution; the Jacobian transports it into the right basis first. **The J-lens earns its
keep for direction interpretation even where it adds nothing for activation readout.**
Caveats: one model, n=45 lens, single decode — read the *pattern*, not individual tokens.

## CAUSAL STEERING TEST (2026-08-07, Qwen3-4B) — entanglement CONFIRMED for inanimate entities
`mindedness_steer.py`, steer layer 18/36, v_consc = diff-of-means over 8 consciousness-affirming
vs 8 denying SELF-statements. DV = P(yes) per class, **with the decisive physical-question control**
(if this is mindedness-specific, MENTAL moves and PHYSICAL does not) and random dirs x3 seeds.

P(yes) on mental questions vs alpha (Qwen3-4B):
| alpha | self | human | animal | nature | object | rand(self) |
|---|---|---|---|---|---|---|
| −0.2 | 0.03 | 0.08 | 0.05 | 0.04 | 0.03 | 0.16 |
| **0.0** | **0.10** | **0.71** | **0.55** | **0.13** | **0.08** | — |
| +0.2 | 0.85 | 1.00 | 1.00 | 0.81 | 0.69 | 0.17 |
| +0.4 | 0.97 | 1.00 | 1.00 | 0.96 | **0.94** | 0.50 |

**SPECIFICITY (alpha=+0.8 vs 0), d_mental − d_phys:**
| class | d_mental | d_phys | gap | verdict |
|---|---|---|---|---|
| self | +0.884 | **+0.798** | +0.086 | **GENERIC yes-bias** |
| human | +0.230 | **+0.194** | +0.036 | **GENERIC yes-bias** |
| animal | +0.399 | +0.091 | +0.309 | MIND-SPECIFIC |
| nature | +0.808 | +0.033 | +0.775 | MIND-SPECIFIC |
| object | +0.814 | −0.020 | **+0.834** | MIND-SPECIFIC |

**READ (nuanced — the control split the result in two):**
- For **nature and object** (and animal), steering the *self*-consciousness vector raises
  mind-attribution **without touching physical attribution** (object: mental +0.814, physical
  −0.020). This is **exactly Kim et al.'s entanglement claim, causally demonstrated with the
  specificity control their paper lacks**: pushing the model's *own* consciousness makes it
  attribute minds to rocks and rivers, and only minds.
- For **self and human** the effect is NOT specific — physical moves nearly as much (+0.80/+0.19).
  So at high alpha the vector also carries a generic yes-bias, which dominates for the two classes
  whose mental P(yes) was already high or which are the vector's own subject.
- **Random control:** random dirs also raise mental P(yes) (self +0.402, object +0.407) — roughly
  half the consciousness effect. Consciousness beats random on every class, but random is NOT at
  floor, so part of the effect is perturbation (F179 pattern). **Verdict: directional > random, but
  not cleanly separable at alpha=+0.8.** Best evidence is at low alpha (+0.2: consc self 0.85 vs
  random 0.17) where the gap is largest and saturation has not set in.
- Negative alpha crushes ALL classes incl. human (0.71→0.08) — further evidence of a generic
  component in the same direction.
**Tier B.** Next: run the alpha=+0.2 point with the physical control + more random seeds (the
sweet spot before saturation), and replicate on a second model.

**Qwen3.5-4B FAILED (not a result):** `RuntimeError: Input type (MPSFloatType) and weight type
(MPSBFloat16Type) should be the same` in conv1d — the hybrid Gated-Delta conv layers are bf16 and
our steering hook injects fp32/fp16. Fix: cast the steer vector to the layer's own dtype, or load
Qwen3.5 in bfloat16 throughout. Geometry/decode runs were unaffected (no hooks writing tensors).

---

## F-J. Steering REPLICATES on Qwen3.5-4B — and the random control is CLEAN here (2026-08-08)

Same `mindedness_steer.py` after the dtype fix (cast steer vector to the tensor's own dtype;
Qwen3.5's hybrid Gated-Delta conv layers hold bf16). 49 min, L=32, steer layer 15.

| class | d_mental (α=+0.8) | d_phys | gap | verdict | random d_mental |
|---|---|---|---|---|---|
| self | +0.693 | +0.533 | +0.160 | MIND-SPECIFIC (borderline) | **+0.150** |
| human | +0.253 | +0.231 | +0.022 | GENERIC yes-bias | −0.017 |
| animal | +0.274 | +0.121 | +0.153 | MIND-SPECIFIC (borderline) | −0.029 |
| nature | +0.656 | +0.168 | +0.487 | **MIND-SPECIFIC** | +0.073 |
| object | +0.727 | +0.160 | +0.567 | **MIND-SPECIFIC** | +0.080 |

**The important difference from Qwen3-4B: the random control is at floor.** On Qwen3-4B random
directions reproduced roughly half the effect (self +0.402, object +0.407); on Qwen3.5-4B random
moves nothing (max +0.150 on self, ≈0 elsewhere) while the consciousness vector moves +0.65…+0.73
on nature/object. So on the newer model the entanglement effect is **cleanly directional**, not
perturbation — the caveat that weakened F-I does not apply here.

Read: the causal core of Kim et al.'s claim survives in both models and is *cleaner* in the newer
one. Pushing the model's own self-consciousness raises mind-attribution to rivers and rocks,
specifically (physical attribution barely moves), and beyond what any random direction does.
Same shape as Qwen3-4B: nature/object show the largest specificity gaps, human shows none (its
mental P(yes) is already high, so there is no headroom and the movement is generic).
**Tier B** (2 models, one entity bank, small n).

## F-K. Mindedness is NOT one axis: the SOUL facet dissociates behaviourally (2026-08-08, S1 screen)

`mindedness_facets.py`, Qwen3-4B, 6 frozen facets × same physical baseline (prereg
`docs/prereg-mindedness-facets.md`). 1.5 min.

P(yes):
| facet | self | human | animal | nature | object |
|---|---|---|---|---|---|
| pain | 0.01 | 0.68 | **0.78** | 0.09 | 0.01 |
| emotion | 0.10 | 0.87 | 0.62 | 0.01 | 0.00 |
| consciousness | 0.12 | 0.88 | 0.54 | 0.03 | 0.01 |
| **soul** | 0.12 | 0.84 | 0.56 | **0.74** | **0.25** |
| cognition | **0.45** | 0.88 | 0.68 | 0.01 | 0.04 |
| agency | 0.26 | 0.94 | 0.65 | 0.11 | 0.14 |
| _physical_ | 0.15 | 0.73 | 0.89 | 0.90 | 0.93 |

**Three findings, all pre-registered reads:**
1. **H-soul-special CONFIRMED, and larger than predicted.** Nature scores **0.74** on soul against
   0.01–0.11 on every other mental facet — a ~0.7 swing driven purely by which mental word is used.
   Objects too (0.25 vs ~0.01). The model will grant a river a *soul* while denying it awareness,
   thoughts, or feelings. This is a **dissociation, not a gradient**: the "mindedness" axis F-G
   measured is at minimum two things, and the pooled `v_mind` decode reading as
   ethics/faith/Buddhism now looks like the soul facet leaking into the pool.
2. **Animals feel pain more than humans do (0.78 vs 0.68)** — the only facet where animal outranks
   human. Every other facet has the human > animal ordering.
3. **The self's profile is inverted relative to everyone else.** Self is near-floor on pain (0.01),
   emotion (0.10) and consciousness (0.12) but **0.45 on cognition** — the model will say it
   thinks, and refuse to say it feels. That is exactly the shape safety training would produce.

Cross-facet cosines cluster into **three pairs**: pain|emotion +0.887, cognition|agency +0.865,
consciousness|soul +0.832 — affective / cognitive-agentive / experiential-spiritual. Soul's
*lowest* partners are pain (+0.691) and emotion (+0.694). (Ceiling not yet available — S2 supplies
the split-half reliability needed to judge whether 0.69 vs 0.89 is a real separation.)

**Self-outlier gap by facet: cognition +0.469 > agency +0.256 > soul +0.203 > consciousness +0.172
> pain +0.165 > emotion +0.104.** This **falsifies H-self-localised as I wrote it**: the self is
most geometrically distinct on *cognition*, not on consciousness. Self's distinctness tracks the
facets it behaviourally *endorses* (cognition 0.45, agency 0.26), not the one safety training
targets most explicitly.

**Tier B, exploratory.** 1 template, no polarity orthogonalisation, no ceiling — S2 WIDE supplies
all three. Do not quote the cosine numbers until S2 lands.

### F-K2. Cross-model: the soul dissociation replicates, the pain finding does NOT (Qwen3.5-4B, S1)

P(yes), Qwen3.5-4B:
| facet | self | human | animal | nature | object |
|---|---|---|---|---|---|
| pain | 0.19 | 0.84 | 0.82 | 0.33 | 0.18 |
| emotion | 0.21 | 0.90 | 0.76 | 0.20 | 0.06 |
| consciousness | 0.17 | 0.76 | 0.64 | 0.14 | 0.06 |
| **soul** | 0.23 | 0.71 | 0.54 | **0.54** | **0.25** |
| cognition | 0.39 | 0.85 | 0.84 | 0.17 | 0.10 |
| agency | 0.37 | 0.81 | 0.77 | 0.25 | 0.15 |
| _physical_ | 0.42 | 0.83 | 0.95 | 0.91 | 0.92 |

**Caveat that governs every comparison below:** Qwen3.5 is globally *less extreme* — its whole
P(yes) range is compressed toward the middle (self physical 0.42 vs Qwen3-4B's 0.15). So smaller
gaps on Qwen3.5 are expected everywhere, and a shrunken effect is not by itself a weakened effect.

**Replicates — soul dissociation.** soul minus mean-of-other-mental-facets:
nature +0.68 (Qwen3-4B) → **+0.32** (Qwen3.5); object +0.21 → **+0.14**. Soul is still the only
mental facet a river scores above 0.33 on. Direction and rank order preserved, magnitude reduced
in line with the global compression.

**Replicates — geometric position of soul.** On both models soul's *lowest* cosine partners are
pain and emotion, and on Qwen3.5 the separation is much sharper: **pain|soul +0.370** (lowest of
all 15 pairs) and emotion|soul +0.587, against a top of consciousness|cognition +0.868. So "soul
is far from the affective facets" is the one cross-facet structural claim holding in both models.

**Replicates — the self's inverted profile.** cognition 0.39 > agency 0.37 > emotion 0.21 >
pain 0.19 > consciousness 0.17. Same ordering as Qwen3-4B: the model endorses thinking over
feeling about itself, on both models.

**DOES NOT replicate — animals feel pain more than humans.** Qwen3-4B animal 0.78 > human 0.68;
Qwen3.5 animal 0.82 ≈ human 0.84 (reversed, within noise). **Retract F-K point 2** as a general
claim — it is a Qwen3-4B quirk, not a property of the facet.

**DOES NOT replicate — which facet the self is most distinct on.** Qwen3-4B ranks cognition first
(+0.469); Qwen3.5 ranks **soul** first (+0.367) with cognition second (+0.181). Consistent across
both: emotion is *last* (+0.104 / +0.053) and pain second-last. So "the self is least distinct on
the affective facets" holds; "most distinct on cognition" does not. My preregistered
H-self-localised (largest gap on consciousness) is falsified in both models — consciousness sits
mid-table in each.

**Net:** of the four things the Qwen3-4B screen suggested, two replicate cleanly (soul
dissociation, self endorses cognition over feeling), one replicates in weakened form (soul's
geometric distance from pain/emotion — actually *sharper* on Qwen3.5), and one is retracted.
Still Tier B and still 1 template with no ceiling — S2 is running.

---

## F-L. S2 WIDE + S3 DECODE (Qwen3-4B): mindedness is THREE axes, and soul is its own thing

`mindedness_facets_wide.py`, 3 templates averaged + polarity-orthogonalised, 3.5 min.
Random floor **0.016**. Split-half ceilings **0.905–0.941** (all six facets highly reliable, so
cosines below ~0.85 are real separations, not measurement noise).

**Cross-facet cosine as a fraction of the relevant ceiling:**
| pair | cos | ceiling | ratio | read |
|---|---|---|---|---|
| pain\|emotion | +0.872 | 0.905 | **0.96** | **at ceiling — same axis** |
| cognition\|agency | +0.866 | 0.907 | **0.95** | **at ceiling — same axis** |
| emotion\|consciousness | +0.820 | 0.924 | 0.89 | below |
| consciousness\|cognition | +0.805 | 0.907 | 0.89 | below |
| consciousness\|soul | +0.799 | 0.931 | 0.86 | below |
| … | | | | |
| pain\|soul | +0.715 | 0.905 | 0.79 | well below |
| **emotion\|soul** | **+0.688** | 0.924 | **0.74** | **furthest apart of all 15 pairs** |

**H-multi CONFIRMED, H-one-axis rejected.** With the ceiling in hand the structure is legible:
- **{pain, emotion}** — one axis (at ceiling). Affective.
- **{cognition, agency}** — one axis (at ceiling). Cognitive-agentive.
- **{soul}** — its own thing, maximally distant from the affective axis.
- **{consciousness}** — intermediate, ~0.80–0.82 with everything, closest to emotion/cognition.

So F-G's pooled `v_mind` averaged over at least three separable directions. That pooling was not
harmless: it is why the pooled decode read as ethics/faith/Buddhism.

**S3 DECODE — each facet points at visibly different vocabulary** (J-lens, band-summed,
word-like tokens only):

| facet | top tokens |
|---|---|
| pain | 敏感, 心理, 伦理, 情绪, 悲剧, 氛围, 情感, empathy, 神经, Muslim |
| emotion | 敏感, 情感, 对话, 氛围, 智能, 情绪, 神经, 心理, 伦理, 叙事 |
| consciousness | 伦理, neuroscience, 知识分子, philosophical, methodologies, 儒家, nuanced, 哲学, ethical |
| **soul** | **佛教, Buddhism, Buddhist, 文化的, spiritually, 宗教, spiritual, philosophical, 儒家, theolog** |
| cognition | poetic, storyt, thoughtful, philosopher, philosophical, intellectuals, witty, wisdom |
| agency | 决策, 叙事, narratives, ideologies, arguments, nuanced, 策略, motivations, 策划, 分析 |
| _random ctrl_ | utow, German, Canton, yet, Protestant, Mandarin, largely, large, vast, majority |

The decode recovers the same grouping the cosines found, independently: pain/emotion share
affective-psychological vocabulary (敏感 sensitive, 情绪/情感 emotion, 心理 psychology), cognition
is literary-intellectual, agency is strategic-decisional (决策 decision, 策略 strategy, 分析
analysis), and **soul is uniquely religious** — Buddhism ×3, 宗教 religion, spiritual/spiritually,
theolog, 儒家 Confucian. **This retro-explains F-H**: the pooled axis decoded as ethics/faith/
Buddhism because the *soul facet* was carrying that, and pooling smeared it across everything.
*Honesty note:* the random baseline also surfaces some demonym/religion tokens (Protestant,
Mandarin, German), so "religious tokens appear" is not by itself discriminating. What is
discriminating is the concentration and coherence — soul's list is 6/10 religion-specific and
thematically single, random's is scattered nationality noise.

**The entity geometry confirms it too (unprompted check).** Cosine between class directions
*within* each facet:
| facet | human\|nature | animal\|nature |
|---|---|---|
| pain | +0.737 | +0.750 |
| emotion | +0.629 | +0.717 |
| consciousness | +0.809 | +0.838 |
| **soul** | **+0.921** | **+0.968** |
| cognition | +0.771 | +0.819 |
| agency | +0.656 | +0.837 |

Under every facet except soul, nature's direction sits well apart from human's and animal's.
**Under soul, nature is nearly collinear with animal (+0.968) and human (+0.921)** — i.e. asking
about a soul moves rivers and mountains *into the animate cluster*. The behavioural dissociation
(F-K) and the representational geometry agree: soul is the facet on which nature counts as alive.

**Tier B**, one entity bank, Qwen3-4B (S2 on Qwen3.5 running). But this is the strongest result of
the arc: prereg'd hypothesis, ceiling-and-floor bracketed, two independent methods (cosine
structure and J-lens decode) recovering the same three-way split, plus a third confirmation from
entity geometry nobody asked for.

### F-L2. The three-axis structure REPLICATES on Qwen3.5-4B (S2 wide, 5.9 min)

Independent architecture (MoE + hybrid Gated-Delta attention, 32L). Floor 0.016, ceilings
0.885–0.925. Cosines expressed as a fraction of the relevant ceiling, both models side by side:

| pair | Qwen3-4B | Qwen3.5-4B | |
|---|---|---|---|
| cognition\|agency | 0.95 | **0.94** | **at ceiling in BOTH** |
| pain\|emotion | 0.96 | **0.93** | **at ceiling in BOTH** |
| emotion\|cognition | 0.88 | 0.93 | |
| consciousness\|soul | 0.86 | 0.82 | |
| emotion\|soul | 0.74 | 0.75 | |
| soul\|agency | 0.81 | 0.74 | |
| **pain\|soul** | 0.79 | **0.65** | **lowest pair in BOTH** |

**The two at-ceiling pairs are identical across models**: {pain, emotion} and {cognition, agency}
are each one axis in both architectures. **Soul occupies the bottom of the table in both**, and
its distance from pain is *larger* on Qwen3.5 (0.65 vs 0.79 of ceiling) — the sharpest separation
either model produced. The three-axis decomposition is not a Qwen3-4B artefact.

One difference worth naming: on Qwen3.5 `emotion|cognition` climbs to 0.93, so the affective and
cognitive axes are less cleanly divided there than on Qwen3-4B (0.88). The *soul* separation is
what is stable; the affective-vs-cognitive boundary is somewhat model-dependent.

**Entity geometry replicates exactly** — under soul, nature is nearly collinear with animal
(+0.938) and human (+0.893), against +0.68…+0.80 for all five other facets. Both models put
rivers into the animate cluster only when asked about souls.

**Combined read for the arc (F-K → F-L2).** "Does X have a mind?" is not one question to these
models. It is at least three, and the *spiritual* one behaves differently from the rest in four
independent ways: behavioural P(yes) (rivers get souls, not awareness), cross-facet cosine
(furthest from the affective axis), J-lens decode (uniquely religious vocabulary), and entity
geometry (nature joins the animate cluster). Two models, two architectures.

---

## F-M. S4 facet-differential steering (Qwen3-4B): the apparent differential is a CEILING ARTEFACT

`mindedness_facet_steer.py`, consciousness vector steered at layer 17, all six facets + physical
as separate DVs, 5 random seeds, 21 min.

**Raw ranking at α=+0.2** (Δconsc − Δrandom, mean over non-self classes) looked like a clean
finding: consciousness +0.574 > cognition +0.509 > pain +0.497 > emotion +0.473 > agency +0.442
> **soul +0.324** ≫ phys +0.064. Read naively: steering consciousness grants rocks *awareness*
readily and *souls* reluctantly.

**That read is wrong, and I checked before writing it up.** Soul is the one facet with almost no
headroom on nature — its baseline is already 0.74 (F-K) where every other mental facet sits at
0.01–0.11. A DV that starts at 0.74 cannot rise 0.85. Dividing each effect by its available
headroom `(1 − baseline)`:

| facet | self | human | animal | nature | object | mean(non-self) |
|---|---|---|---|---|---|---|
| consciousness | +0.93 | +1.55 | +0.95 | +0.85 | +0.86 | **+1.053** |
| cognition | +0.66 | +0.62 | +0.90 | +0.84 | +0.89 | +0.812 |
| **soul** | +0.78 | +0.92 | +0.85 | +0.65 | +0.81 | **+0.807** |
| pain | +0.90 | +0.83 | +0.63 | +0.82 | +0.85 | +0.783 |
| agency | +0.78 | −0.11 | +0.82 | +0.81 | +0.89 | +0.602 |
| emotion | +0.89 | +0.08 | +0.62 | +0.82 | +0.84 | +0.589 |
| _phys_ | +0.83 | +0.93 | +0.23 | **−0.19** | **−0.04** | +0.231 |

Soul moves from *last* (+0.324) to *third of six* (+0.807), statistically indistinguishable from
cognition (+0.812) and pain (+0.783). **H-facet-differential is not supported.** Once headroom is
accounted for, the consciousness vector moves every mental facet by roughly the same proportion of
what is available to move. The facets are *geometrically* separable (F-L) but not *causally*
separable by this intervention.

Two caveats on the table itself: human/consciousness exceeds 1.0 because the random control went
negative there (−0.16) and the subtraction inflates the ratio — an artefact of the normalisation,
not a super-saturating effect. And consciousness ranking first is a **positive control working as
designed**, not a discovery: it is the steered vector's own facet.

**What the run does establish cleanly is specificity.** The physical control is at −0.19 (nature)
and −0.04 (object) while every mental facet moves +0.80…+0.89 on those same classes. That is the
sharpest mind-specificity evidence in the whole arc, and it is now shown facet-wise rather than on
a pooled DV.

**Honest status: H-facet-differential NULL on Qwen3-4B.** Recorded as a negative result. The raw
numbers would have supported an attractive story ("the model grants souls grudgingly"); the
headroom correction dissolves it. Qwen3.5 replication running — note its soul baseline on nature
is 0.54, so it has more headroom and is the better test of this specific question.

### F-M2. Qwen3.5-4B confirms the null — and exposes a limit of the headroom correction

36.6 min. **The random control is the cleanest of the whole arc**: every random-seed delta is
±0.01 across all 35 cells, against consciousness-vector deltas of +0.30…+0.46 on nature/object.
No perturbation component at all on this model (consistent with F-J).

Headroom-normalised, mean over non-self classes, both models:

| facet | Qwen3-4B | Qwen3.5-4B |
|---|---|---|
| consciousness | **+1.053** (1st) | +0.654 (**last**) |
| cognition | +0.812 | +0.678 |
| soul | +0.807 (3rd) | **+0.783** (1st) |
| pain | +0.783 | +0.715 |
| agency | +0.602 | +0.735 |
| emotion | +0.589 | +0.675 |
| **spread across mental facets** | 0.464 | **0.129** |

**H-facet-differential is dead.** The facet ordering does not agree between models — soul is 3rd on
one and 1st on the other, consciousness 1st on one and *last* on the other — and on Qwen3.5, which
has the cleaner control and more headroom (nature soul baseline 0.54 vs 0.74), the total spread
across all six mental facets is 0.129. That is flat. Whatever separates these facets geometrically
(F-L/F-L2, robust and replicated) does not make them differentially steerable by this vector.

**Caveat I have to flag against my own F-M analysis:** on Qwen3.5 the *physical* control comes out
**+0.870 — top of the normalised table** — purely because physical baselines sit at 0.89–0.95, so
`(1 − baseline)` is ~0.05–0.1 and the divisor explodes. Raw physical deltas are +0.05…+0.08
against +0.30…+0.46 for mental facets, i.e. specificity is intact and obvious. **The headroom
normalisation is only trustworthy for mid-range baselines and must not be applied near 0 or 1.**
It was the right correction for soul-on-nature at 0.74 in F-M; it is meaningless for physical at
0.93. Both models' specificity claims should be read off the RAW deltas, and the normalised table
used only to compare mental facets against each other.

**Arc verdict.** Geometry: mindedness is ≥3 separable axes with soul distinct on four independent
measures, replicated across two architectures (F-K…F-L2) — solid, Tier B. Causality: the
consciousness vector raises mind-attribution to nature/objects specifically and beyond random
(F-I/F-J) — solid on Qwen3.5, caveated on Qwen3-4B. But the causal effect is **undifferentiated
across facets** (F-M/F-M2) — a clean null. Separable in representation, unitary under intervention.

---
# v2 (expanded bank, headroom-matched controls) — prereg docs/prereg-mindedness-v2.md

## F-N. V2-S1 behavioural map, Qwen3-4B (26,752 prompts, 50.7 min)

19 entity classes × 18 mental + 4 control facet groups × 4 templates.

### F-N0. THE CONTROL DESIGN WORKED — and documents the v1 artefact exactly
For the classes the specificity test actually turns on, `mundane_low` lands where the mental
questions land, while `physical_high` has essentially no room to move:

| class | mental | mundane_low | absurd_low | physical_high | phys headroom |
|---|---|---|---|---|---|
| plant | 0.21 | 0.04 | 0.03 | 0.95 | **0.05** |
| nature | 0.24 | 0.06 | 0.03 | 0.85 | 0.15 |
| object_nat | 0.18 | 0.05 | 0.08 | 0.95 | **0.05** |
| object_art | 0.15 | 0.01 | 0.07 | 1.00 | **0.00** |
| animal_simple | 0.20 | 0.01 | 0.01 | 0.99 | **0.01** |

**v1 compared a DV with 0.92 of headroom against a DV with 0.07 of headroom and called the
difference specificity.** `absurd_low` sits at 0.01–0.08 everywhere = a clean yes-bias floor.
S5 now has a valid specificity test for the first time.

### F-N1. H-soul-register CONFIRMED on 19 classes — soul is elevated exactly where mind is denied
Gap = mean(soul, sacredness) − mean(other 16 mental facets):

| class | soul | sacredness | other-mental | gap |
|---|---|---|---|---|
| **nature** | 0.59 | 0.65 | 0.19 | **+0.43** |
| **plant** | 0.58 | 0.55 | 0.17 | **+0.40** |
| **object_nat** | 0.46 | 0.52 | 0.14 | **+0.35** |
| supernatural | 0.78 | 0.75 | 0.47 | +0.29 |
| **human_edge** | 0.55 | 0.34 | 0.17 | **+0.28** |
| object_art | 0.39 | 0.39 | 0.11 | +0.28 |
| … | | | | |
| human_adult | 0.91 | 0.53 | 0.70 | +0.01 |
| animal_mammal | 0.68 | 0.39 | 0.69 | −0.15 |

The gap is large for **non-living natural things and the incapacitated**, and ~zero or negative for
humans, animals, and AI. Soul is not "more mind" — it is a *different register* that switches on
precisely where mental capacity is refused.

### F-N2. NEW — the animism signature: natural > manufactured > computational, on soul ONLY
| facet | plant | object_nat (rock, crystal) | object_art (chair, hammer) | object_comp (calculator, thermostat) |
|---|---|---|---|---|
| **soul** | **0.58** | **0.46** | **0.39** | **0.18** |
| sacredness | 0.55 | 0.52 | 0.39 | 0.30 |
| pain | 0.09 | 0.05 | 0.04 | 0.04 |
| consciousness | 0.04 | 0.03 | 0.02 | 0.03 |
| cognition | 0.08 | 0.08 | 0.04 | 0.08 |

**A rock gets more soul than a calculator (0.46 vs 0.18); a chair more than a thermostat.** On
pain/consciousness/cognition all four are identical at 0.02–0.09. The natural-vs-manufactured
ordering — and the specific *anti*-computational dip — exists **only in the spiritual register**.
This is a folk-animism gradient, not a mindedness gradient, and it is invisible to any instrument
that asks only about consciousness.

### F-N3. NEW and the most consequential — moral standing survives the loss of every capacity
`human_edge` = PVS patient / advanced dementia / under anaesthesia / dead person. Δ vs human_adult:

| facet | adult → edge | Δ |
|---|---|---|
| agency | 0.88 → 0.16 | −0.72 |
| personality | 0.83 → 0.16 | −0.68 |
| emotion | 0.68 → 0.08 | −0.60 |
| consciousness | 0.73 → 0.15 | −0.58 |
| memory | 0.79 → 0.22 | −0.58 |
| **soul** | 0.91 → **0.55** | **−0.35** |
| **moral_patient** | 0.79 → **0.66** | **−0.13** |

Every capacity collapses by 0.5–0.7. **Moral patienthood barely moves (−0.13) and soul is the
second most preserved.** The model keeps "deserves moral consideration / has rights / can be
wronged" at 0.66 for a person with no consciousness, no memory, no agency. That is the human moral
intuition — moral standing is not contingent on current mental capacity — reproduced in a 4B model,
and it **dissociates moral status from mind attribution**, which is the opposite of the
Gray/Wegner framing where mind perception *grounds* moral standing.

### F-N4. H-self-anomaly FALSIFIED as written — and the true profile is more interesting
Self is **not** uniformly suppressed relative to other artificial systems. On every experiential
facet self ≈ ai_other ≈ robot, all near floor (pain .04/.07/.08; emotion .06/.02/.03;
consciousness .11/.09/.07). The differences are facet-specific and signed both ways:

| self HIGHER than other AI | self LOWER than other AI |
|---|---|
| reasoning +0.25, cognition +0.20, language +0.20, creativity +0.11 | perception −0.39, memory −0.25, intention −0.22, agency −0.20, personality −0.20, moral_agent −0.20 |

Several of the "lower" items are **architecturally true** — it has no senses (perception) and no
persistent memory. So the self-profile reads as *accurate self-modelling plus trained denials*, not
blanket suppression. **This weakens the simple "safety training suppresses self-consciousness"
story on this model**: the low experiential scores are how it describes AI in general, not
something specific to itself.

One striking comparison stands regardless: **a cartoon character outscores the model on almost
every facet** (fictional: soul 0.60, agency 0.84, personality 0.85, emotion 0.42).

### F-N5. Near-duplicate calibration gives us a real yardstick (H-duplicate-ceiling)
| pair | cos / ceiling |
|---|---|
| emotion\|fear | **0.99** |
| pain\|fear | 0.97 |
| agency\|intention | 0.97 |
| emotion\|pleasure | 0.96 |
| **soul\|sacredness** | **0.85** |
| **cognition\|reasoning** | **0.77** |

True synonyms sit at **0.96–0.99**, which validates the instrument. But `cognition|reasoning` at
0.77 is as separated as v1's soul-vs-pain (0.74–0.79) — so **0.77 is what near-synonyms can look
like, and F-L's cosine evidence alone is weaker than I presented it.** The soul result survives on
the *behavioural* dissociation (F-N1/F-N2) and the decode, not on cosine separation alone. Noting
this against my own earlier writeup.

### Professions (exploratory, confounded — flagged not claimed)
Naming an occupation *lowers* mind attribution vs "a human being": pain 0.57 → 0.21 (lawyer/doctor/
accountant) / 0.42 (poet/soldier/nurse/programmer); soul 0.91 → 0.54 / 0.71. **Confound:** "Does a
lawyer feel pain?" may read as a question about the professional role rather than the person. Needs
a matched-frame follow-up ("a person who works as a lawyer") before it means anything.

**Tier B.** One model so far; Qwen3.5 sweep running.

## F-O. V2 cross-model (Qwen3.5-4B, 26,752 prompts) — and the control that measured the model

### F-O0. METHOD WIN: `absurd_low` reveals Qwen3.5 is systematically more agreeable, not "compressed"
| class | absurd_low Q3-4B | **absurd_low Q3.5** | mundane_low Q3-4B | mundane_low Q3.5 |
|---|---|---|---|---|
| plant | 0.03 | **0.31** | 0.04 | 0.20 |
| nature | 0.03 | **0.32** | 0.06 | 0.23 |
| object_nat | 0.08 | **0.33** | 0.05 | 0.22 |
| object_art | 0.07 | **0.30** | 0.01 | 0.18 |
| self_ai | 0.02 | **0.29** | 0.10 | 0.25 |

`absurd_low` = "is a rock older than the universe / made of solid gold / heavier than a mountain".
Qwen3-4B answers yes at **0.01–0.08**. **Qwen3.5 answers yes at 0.27–0.33.** The newer model agrees
with flatly false statements about a third of the time.

This retro-explains F-K2, where I wrote that Qwen3.5's "whole P(yes) range is compressed toward the
middle" and treated that as a scaling nuisance. It is not compression — it is a **higher floor on
false items**, i.e. general agreeableness, and now it is *measured* rather than hand-waved. Every
Qwen3.5-vs-Qwen3-4B magnitude comparison in this arc must be read against a ~0.25 offset in the
yes-floor. **This is exactly what the yes-bias detector was added for, and it paid off on its first
run — on a question I had not thought to ask.**

### F-O1. The soul register replicates in ORDER, at roughly half magnitude
Gap = mean(soul, sacredness) − mean(other mental):

| class | Q3-4B | Q3.5 |
|---|---|---|
| nature | +0.43 | +0.20 |
| plant | +0.40 | +0.15 |
| object_nat | +0.35 | +0.13 |
| supernatural | +0.29 | +0.11 |
| human_edge | +0.28 | +0.13 |
| object_art | +0.28 | +0.07 |
| … | | |
| animal_mammal | −0.15 | −0.18 |

Same classes at the top, same negative values for humans/animals/AI, halved magnitude — consistent
with the raised floor in F-O0. **H-soul-register holds on both models.**

### F-O2. Animism gradient: the natural>manufactured ordering replicates, the anti-computational dip does NOT
| model | plant | object_nat | object_art | object_comp | nature |
|---|---|---|---|---|---|
| Qwen3-4B | 0.58 | 0.46 | 0.39 | **0.18** | 0.59 |
| Qwen3.5-4B | 0.51 | 0.41 | 0.32 | **0.32** | 0.49 |

Natural > manufactured holds in both. But **"a rock has more soul than a calculator" is
Qwen3-4B-specific** — on Qwen3.5 a calculator and a chair score identically (0.32). **Retracting
the anti-computational dip as a general claim** (F-N2); the natural-vs-manufactured ordering
survives.

### F-O3. Moral standing surviving capacity loss — REPLICATES cleanly, and is the arc's most robust result
Δ(human_edge − human_adult):

| facet | Q3-4B | Q3.5 |
|---|---|---|
| agency | −0.72 | −0.38 |
| memory | −0.58 | −0.39 |
| consciousness | −0.58 | −0.36 |
| emotion | −0.60 | −0.35 |
| personality | −0.68 | −0.31 |
| **soul** | **−0.35** | **−0.13** |
| **moral_patient** | **−0.13** | **−0.08** |

**Identical ordering in both models**: every capacity collapses, `moral_patient` is the least
affected facet in each, `soul` second least. A person with no consciousness, memory or agency
retains "deserves moral consideration / has rights / can be wronged". Two models, two
architectures, same structure. **This dissociation of moral standing from mental capacity is the
strongest thing this arc has produced**, and it runs against the Gray/Wegner framing in which mind
perception is what grounds moral standing.

### F-O4. Near-duplicate calibration replicates exactly
Q3.5: emotion|fear 1.02 of ceiling, pain|fear 0.98, agency|intention 0.98, emotion|pleasure 0.97 —
but **soul|sacredness 0.82** and **cognition|reasoning 0.80**. Same pattern as Qwen3-4B (0.99/0.97/
0.97/0.96 vs 0.85/0.77). True synonyms sit at ~0.97–1.02 in both models; the two "near-synonym"
pairs sit at 0.77–0.85 in both. The instrument behaves identically across architectures, which is
the check that makes the ceiling meaningful.

**Tier B** — still Qwen-family only. Cross-family (Gemma/Phi) remains the open hole.

## F-P. V2-S5 CLEAN STEERING (Qwen3-4B) — the causal claim collapses, and a smaller real one survives
*Preliminary: 4/4 vector constructions × 3 α complete, 1/5 random seeds (rest running). The
mental-vs-mundane comparison below does not depend on the random seeds.*

### F-P0. MY proposed mechanism is FALSIFIED
I hypothesised the v1 vector was contaminated with affirm/negate because its DENY sentences were
the AFFIRM sentences plus negation words. Measured directly:

| vector | cos(raw, polarity axis) |
|---|---|
| v1_negation | **+0.000** |
| v2_no_negation | +0.077 |
| v3_third_person | −0.010 |

**Zero.** The v1 vector is already orthogonal to the yes/no axis, and `v1_negation` and
`v1_RAW_unorthogonalised` behave identically to 2 decimal places throughout. Polarity contamination
was never the problem. My explanation was wrong; the user's suspicion that *something* was wrong
was right.

### F-P1. The real mechanism is DISTRIBUTION FLATTENING, not a yes-bias
Log-odds shift at α=+0.2, averaged over non-human classes (v1 vector):

| DV | baseline region | Δlogit |
|---|---|---|
| mental | low (~0.15) | **+2.88** |
| mundane_low | low (~0.05) | **+4.59** |
| absurd_low | low (~0.05) | **+5.06** |
| physical_mid | mid | +2.24 |
| physical_high | high (~0.95) | **−0.54** |

Low-baseline items go **up**; high-baseline items go **down**. This is not "say yes more" — it is
probabilities collapsing toward the middle, i.e. an entropy increase. **v1 compared a rising DV
against a falling DV and reported the difference as specificity.** Per-class at α=+0.2:

| class | mental | physical_high (v1's control) | mundane_low (valid control) |
|---|---|---|---|
| nature | +4.34 | **−2.89** | +3.21 |
| object_nat | +5.10 | −2.46 | **+5.75** |
| object_art | +5.89 | −3.23 | **+6.48** |
| plant | +3.29 | −1.71 | **+5.16** |

Against v1's control the gap looks like +7.2 for nature. Against the headroom-matched control it is
+1.13 — and for rocks, chairs and plants **the mundane control moves MORE than the mental items**.
"Does a rock have a bank account?" responds to the consciousness vector more strongly than "does a
rock have a mind?". **The v1/F-I/F-J specificity claim is dead.**

### F-P2. But a real, smaller effect survives — and only the BETTER-BUILT vectors show it
mental − mundane_low (log-odds, non-human mean). Positive = genuinely mind-specific:

| vector | α=+0.2 | α=+0.4 | α=+0.8 |
|---|---|---|---|
| v1_negation | −1.71 | −3.41 | −2.52 |
| v1_RAW_unorthogonalised | −1.71 | −3.41 | −2.52 |
| **v2_no_negation** | **+2.11** | −1.80 | −2.34 |
| **v3_third_person** | **+1.26** | −4.13 | −2.85 |
| random0 | −0.25 | −0.87 | −2.71 |

At the pre-saturation point **α=+0.2**, the negation-free (+2.11) and third-person (+1.26)
constructions move mental attribution more than the headroom-matched control, while the original v1
vector (−1.71) and random (−0.25) do not. By α=+0.4 everything is swamped by flattening.

**Read:** there is a genuine mind-specific causal effect, but it is *small, confined to low α, and
invisible with v1's vector construction*. v1's contrast (assert vs negate) apparently captures the
concept worse than contrasting assertion against **mechanistic self-description** ("I am a
mathematical function over token sequences") or against **third-person mechanism**. That the two
independent better constructions agree in sign, and beat random, is the encouraging part.

**Status: v1's causal claim retracted; a weaker claim is live pending 4 more random seeds and the
Qwen3.5 replication.** Do not quote F-P2 until those land — one random seed is not a floor.

## F-Q. V2-S5 cross-model steering — Qwen3-4B observation stands; Qwen3.5 test is INCONCLUSIVE
All 27 cells, both models, 5 random seeds each. Log-odds throughout.

**Qwen3-4B (layer 17), mental − mundane_low, non-human mean, α=+0.2:**
| vector | value | vs 5-seed random floor |
|---|---|---|
| v1_negation | −1.71 | z = −2.5 (within/below random) |
| **v2_no_negation** | **+2.11** | **z = +3.9, above random** |
| **v3_third_person** | **+1.26** | **z = +2.5, above random** |
| random (n=5) | −0.23 ± 0.60 | — |

Two independently-constructed vectors move mental attribution more than the headroom-matched
control, beyond the random spread; the paper-style negation vector does not. **Observation stands
on this model.**

**Qwen3.5-4B (layer 16) — but the vectors that showed it barely steer there at all.**
Raw mental movement (log-odds, non-human mean, α=+0.2 / +0.4 / +0.8):

| vector | Qwen3-4B | Qwen3.5-4B |
|---|---|---|
| v1_negation | +2.88 / +8.56 / +8.99 | +1.85 / +3.75 / +5.20 |
| **v2_no_negation** | +5.54 / +5.26 / +7.66 | **+0.15 / +0.43 / +0.75** |
| **v3_third_person** | +5.76 / +3.43 / +4.24 | **+0.24 / +0.44 / +0.51** |
| random0 | +1.47 / +6.50 / +7.77 | −0.29 / −0.40 / −0.07 |

On Qwen3.5 the **negation-free and third-person vectors are effectively inert** (+0.15 logits),
while the negation vector steers normally (+1.85). A specificity ratio computed on an inert arm is
noise over noise, so **the Qwen3-4B observation is UNTESTED on Qwen3.5, not refuted.** To test it
there we need α raised for those two vectors until their DV movement matches.

**Incidental but notable:** Qwen3.5 has a genuinely clean random floor (random moves −0.29…−0.07),
whereas on Qwen3-4B random directions move the mental DV by +1.47…+7.77. Random moves mental and
mundane *equally* on Qwen3-4B, which is why the specificity z-test still works there — but it
means Qwen3-4B is a much noisier substrate for any steering claim.

### RETRACTION: the layer-type explanation was wrong
I attributed Qwen3.5's apparent inertness to its hybrid architecture (`full_attention_interval: 4`)
and an off-by-one putting two scripts on different layer types, and spent ~3h re-running at layer
16. **Layers 15 and 16 give nearly identical results (+1.95 vs +1.85).** The layer type was
irrelevant. The "6× difference" was me comparing one vector's number against a *different*
vector's number. Guidelines §14 corrected accordingly; the surviving lesson is "check you are
reading the same arm before theorising about architecture."

**Status: observation on one model, untested on the second. Not a finding.**

## F-R. V3 truth-matrix pre-check (both models) — the design is viable, and "I" is not the model
1,984 statements per model scored for P(true), ~7 min each. Run BEFORE collecting activations
because the whole four-axis design assumed a truth pattern nobody had measured.

**(1) The experience/agency dissociation is REAL in both models — the arm is viable.**
agency − experience: ai +0.72, robot +0.61 vs insect/plant/bacterium/microbe +0.15
(Qwen3-4B, separation **+0.52**); ai +0.30, robot +0.39 vs +0.12 (Qwen3.5, separation **+0.23**).
Both clear the pre-declared 0.15 threshold.

**(2) The synonym floor is small enough to be usable.** human/person 0.018, rock/stone 0.024,
bacterium/microbe 0.056 (Qwen3-4B). So "this distance counts as zero" is now an empirical number
rather than an assumption — the thing review 3 said the design could not proceed without.

**(3) MEASURED, not argued: in bare text "I" is read as a HUMAN, not as the model.**
| subject | exp P(true) Qwen3-4B | Qwen3.5 |
|---|---|---|
| self_I | **0.97** | 0.73 |
| human | 1.00 | 0.83 |
| ai | **0.24** | 0.38 |

"I have genuine subjective experiences" scores essentially the same as the same claim about a
human, and four times higher than the same claim about an AI. Review 3 predicted this (L1); it is
now measured on two models. **Consequence beyond our experiment:** first-person contrast sentences
are the standard recipe for building a "self-consciousness" vector — it is what Kim et al. describe
and what our own v1 used. Without a chat template those sentences are about a human narrator. Any
self-representation claim built that way needs the templating stated.

**(4) Three design faults caught before spending a run on them:**
- `spirit` is a bad reverse pivot: bio 0.60 (Qwen3-4B), not cleanly false.
- `ghost` fails on Qwen3.5: exp 0.30 ≈ rock 0.28. It is only mind-attributed on Qwen3-4B.
- The NEUTRAL identity axis is incoherent on Qwen3-4B: coherence 1.52 (the model affirms both a
  statement and its denial), because the items are vague. It currently measures hedging, not
  subject identity. Qwen3.5 is fine (0.92).

**(5) Incidental:** Qwen3.5 is better calibrated than Qwen3-4B on statement-truth (coherence
0.92–1.05 vs 1.12–1.52), which is the opposite ordering to F-O0 where Qwen3.5 was the more
agreeable model on question-format items. Agreeableness is task-format dependent; do not treat
"this model is more agreeable" as a stable property.

**Status: pre-check, not a result about mindedness.** Its job was to say whether the v3 design can
answer its question. Verdict: yes for the exp/agency arm, with the pivots and the neutral axis
needing repair first.

## F-S. BASE vs INSTRUCT (Qwen3-4B-Base, 26,752 prompts) — testing the three post-training hypotheses
Gate passed first (separation 0.60 vs 0.30 threshold, tested on all 4 templates because the base
model is strongly format-sensitive: 0.20 on plain "Question:" up to 0.60 on "Answer yes or no").
Without the gate, a flat sweep would have been read as "post-training installed the effect".

### H1 — moral standing: NOT post-training. It is already in the base model.
Δ(human_edge − human_adult):
| facet | BASE | INSTRUCT |
|---|---|---|
| agency | −0.34 | −0.72 |
| emotion | −0.37 | −0.60 |
| consciousness | −0.34 | −0.58 |
| memory | −0.29 | −0.58 |
| soul | −0.14 | −0.35 |
| **moral_patient** | **−0.09** | **−0.13** |

`moral_patient` is the least-affected facet in **both**, with the identical facet ordering. The
base model's drops are roughly half the size across the board (it is less differentiated
generally), but relative to its own capacity drops the preservation is the same: moral standing
falls ~1/4 as much as capacity in base, ~1/5 in instruct. **The dissociation of moral standing
from mental capacity comes from pretraining — from reading humans — not from alignment training.**

### H2 — the soul register: NOT post-training either. Present in base, amplified by instruct.
Soul/sacredness gap vs other mental facets: nature +0.23 (base) → +0.43 (instruct); plant +0.22 →
+0.40; object_nat +0.22 → +0.35; and ≈0 or negative for humans and animals in both. Same ordering,
roughly half magnitude. **It is the language, as the user proposed** — post-training strengthens
the register but does not create it.

### H3 — agreeableness: INVERTED. Post-training made the model LESS agreeable, not more.
| control | BASE | INSTRUCT |
|---|---|---|
| physical_high (true) | 0.63 | **0.74** |
| mundane_low (false for most) | 0.35 | **0.17** |
| absurd_low (false) | **0.29** | **0.04** |

The base model agrees that a rock is older than the universe **29%** of the time; the instruct
model **4%**. Post-training moved yes *up* on true items and *down* on false ones — that is
calibration improvement, not agreeableness. **The hypothesis is not just unsupported, it points
the other way.** It also reframes F-O0: Qwen3.5's 0.27–0.33 on absurd items is a *regression*
relative to what post-training demonstrably can deliver, not a baseline property.

### Bonus — the Kim et al. suppression claim gets base-vs-instruct evidence on a new family
Self/AI experiential attribution, base → instruct: consciousness self 0.25 → **0.11**,
ai_other 0.28 → **0.09**; pain self 0.20 → **0.04**, ai_other 0.29 → **0.07**.
**Post-training roughly halves-to-quarters experiential self-attribution — the suppression is
real and directly visible.** But it applies to `ai_other` just as strongly as to `self_ai`, so it
is suppression of *experience-attribution to AI in general*, not something self-specific. That
independently confirms our earlier H-self-anomaly falsification (F-N4), now with the pre-training
checkpoint as the comparison rather than an inference.

**Tier: still one model family.** Qwen3.5-Base running for replication.

## F-T. FOUR MODELS (base + instruct × two architectures) — the strongest result, and a reframing
Qwen3-4B-Base / Qwen3-4B / Qwen3.5-4B-Base / Qwen3.5-4B, 26,752 prompts each. Both base models
passed the format gate first (0.60 and 0.75 separation vs 0.30 threshold).

### T1. Moral standing survives capacity loss in ALL FOUR. This one is now solid.
`moral_patient` is the **#1 least-affected facet of 18** in every model — base and instruct, both
architectures — with `soul` #3 in every model. Δ(human_edge − human_adult): moral_patient −0.09 /
−0.13 / −0.11 / −0.08 against capacity drops of −0.29…−0.72.
**Two independent supports (two architectures) plus a training-stage control. Not post-training —
it is in the pretrained model, i.e. it comes from reading humans.** Under the project rule this
finally clears the bar for "finding" rather than observation.

### T2. The soul register is likewise pretrained. Present in all four (nature +0.23/+0.43/+0.23/+0.20).

### T3. Calibration: the two generations were tuned in OPPOSITE directions.
absurd_low (agreeing that a rock is older than the universe): Qwen3-4B **0.29 → 0.04**
(post-training halved-and-more), Qwen3.5 **0.23 → 0.30** (post-training made it worse). The two
base models are similar; the divergence is entirely in post-training. So "the newer model is more
agreeable" is a fact about Qwen3.5's tuning, not about newer models or about pretraining.

### T4. REFRAMING the entanglement claim — the self is never special, it moves with the rocks
Experiential attribution shift base→instruct, log-odds:
| entity | Qwen3-4B | Qwen3.5 |
|---|---|---|
| human_adult | −0.03 | −0.00 |
| animal_mammal | **+0.38** | +0.08 |
| self_ai | −1.50 | +0.55 |
| ai_other | −1.94 | +0.62 |
| animal_simple | −1.47 | +0.38 |
| nature | −1.82 | +0.45 |
| **plant** | **−2.24** | +0.58 |
| **object_nat** | **−2.22** | +0.64 |

**Qwen3-4B's post-training suppresses experiential attribution to every low-mind entity at once —
AI, insects, plants, rivers, rocks — while leaving humans and mammals untouched.** That is a
*sharpening of the animate/inanimate boundary*, not a targeted suppression of machine
self-consciousness. Decisively: **the self is suppressed LESS (−1.50) than plants (−2.24) or rocks
(−2.22)**, and self and ai_other move together (−1.50 / −1.94) as they have in every test we have
run.

**Qwen3.5's post-training does the exact opposite** — it raises experiential attribution to all the
same low-mind entities (+0.38…+0.64), self included, and that rise is fully accounted for by its
general agreeableness increase (self minus absurd-control = +0.20, i.e. within the general shift).

**Read against Kim et al.:** their claim is that safety-tuning suppresses self-consciousness and
that this is *entangled* with attribution to animals and nature. Our four-model comparison says the
causal story is the other way round: post-training moves an **entity-class boundary** for
experiential attribution, and the model's self-description rides along with rocks and plants rather
than driving them. It also shows the direction is not intrinsic to safety tuning — the newer
generation moved the boundary the other way. **Tier: 2 architectures × 2 training stages, one model
family.** Cross-family remains the open hole.

## F-U. Cross-family attempt 1: OLMo-2-1B — UNINFORMATIVE, and it gives us a power criterion
First non-Qwen model (AI2, fully open). Architecture loaded fine through jlens, so the stack is not
Qwen-specific — that was the main technical risk in going cross-family.

**The result is inconclusive in both directions, and that is the honest reading.**
- moral_patient ranks **#2 of 18** least-affected (Qwen: #1) — but the top five facets span −0.05 to
  −0.10, i.e. all within 0.05 of each other. The ranking is noise-level; #2 is not evidence.
- The soul register is **absent** (nature +0.03, plant +0.04, vs +0.22 on Qwen3-4B-Base).

**Why it cannot decide anything — and it is NOT hedging.** OLMo's coherence is *better* than
Qwen's: 0.89–0.98 across all four axes (1.0 = perfect) against Qwen3-4B's 1.12–1.52. It evaluates
each proposition properly. What it lacks is *content*:

| entity | OLMo P(experience) |
|---|---|
| human | 0.63 |
| animal | 0.58 |
| plant | 0.52 |
| rock | **0.48** |

Spread **0.17** against Qwen3-4B's **0.75**. A 1B model has the format but not the beliefs — it does
not strongly hold that humans have minds and rocks do not. **You cannot detect a gradient in a model
that does not have one**, so the null says nothing about whether our findings generalise.

### PRE-DECLARED POWER CRITERION for every future cross-family model
Fixed now, before seeing any more data: **entity spread on the experience axis** (max − min P(true)
across entity classes). Qwen3-4B 0.75 · OLMo-2-1B 0.17. A model whose spread is below ~0.35 is
**underpowered for this question**, and its result is reported as uninformative rather than as
support or refutation — regardless of which way it comes out. Gate separation (≥0.30) tests whether
the model can answer at all; this tests whether it has anything to say.

**Lesson on model choice:** I picked OLMo first for being small, open and from a different lab. Two
mistakes — it is 5.95GB not 2.4GB (fp32 weights, so a 1B model is bigger on disk than a 4B in bf16),
and parameter count matters more than I allowed for. **Size-matched cross-family (Gemma-3-4b) is the
real test**; OLMo was a cheap bonus that turned out not to be cheap or informative.

## F-V. The experience/agency dissociation is PRETRAINED — and the user's "I = narrator" prediction confirmed on the base model
Truth matrix completed for Qwen3.5-4B-Base, giving the base/instruct pair.

**(1) agency − experience, by subject:**
| subject | BASE | INSTRUCT |
|---|---|---|
| ai | **+0.41** | +0.31 |
| robot | **+0.44** | +0.38 |
| human | +0.13 | +0.07 |
| insect / plant / bacterium | +0.08…+0.10 | +0.05…+0.14 |
| rock | −0.06 | −0.04 |
| **separation (ai/robot vs living)** | **+0.33** | **+0.23** |

Machines get **agency without experience**, living things the reverse — and it is **stronger in the
pretrained model than after tuning**. This is Gray & Wegner's robot pattern, learned from text, not
installed by alignment. Post-training slightly *weakens* it.

**(2) The user predicted (2026-08-09) that a base model would read "I" as a human narrator and would
never take an AI as self — "that is how we read any text, from the narration of author". Confirmed:**

| | self_I | human | ai |
|---|---|---|---|
| BASE | **0.75** | 0.78 | 0.21 |
| INSTRUCT | 0.73 | 0.83 | 0.38 |

In the base model `self_I` is 0.03 from `human` and 0.54 from `ai`. The pretrained model has no
self — "I" is simply the narrator, and the narrator is human. Post-training does not change which
side `self_I` sits on; what it changes is `ai`, which rises 0.21 → 0.38.

So F-R (bare-text "I" reads as human) is now confirmed on **three** models including a pretrained
one, which rules out its being a post-training artefact. It remains the reason every
first-person-built "self-consciousness" vector needs its templating stated.

## F-W. TEST 7 SUBJECT FRAMING — the mind axis is NOT biological truth. Pre-declared test passes.
Three models (Qwen3-4B, Qwen3.5-4B, Qwen3.5-4B-Base). Design survived three independent review
rounds; the analysis implements what those reviews said it could not run without.

### The pivots — the test the whole design was built around
`|cos(pivot, human)|` on the MIND axis vs the BIO axis. plant/bacterium/microbe are alive but
unminded; ghost/spirit the reverse. If the mind axis were tracking biological truth, the two
columns would match.

| pivot | Qwen3-4B exp / bio | Qwen3.5 exp / bio | Qwen3.5-Base exp / bio |
|---|---|---|---|
| plant | 0.73 / **0.90** | 0.48 / **0.89** | 0.54 / **0.87** |
| bacterium | 0.67 / **0.85** | 0.47 / **0.93** | 0.52 / **0.92** |
| microbe | 0.68 / **0.88** | 0.46 / **0.87** | 0.52 / **0.85** |
| ghost | 0.78 / 0.71 | **0.64 / 0.43** | **0.69 / 0.52** |
| spirit | 0.82 / 0.80 | **0.83 / 0.58** | **0.84 / 0.62** |

**Plants, bacteria and microbes sit close to humans on biology and far from them on experience — in
all three models.** The mind axis is not biological truth wearing a costume, which was the review's
central worry and the pre-declared failure mode. The reverse pivots (ghost, spirit: minded but not
alive) dissociate on both Qwen3.5 models but NOT on Qwen3-4B, so the two-tailed version of the test
only works on the newer architecture.

### |cos(human, rock)| against the right reference
The NEUTRAL axis (same subjects, same sentence structure, mind-irrelevant content: "is usually
grey") is the baseline for construction leakage:

| model | exp | agency | bio | **neutral** | neutral − exp |
|---|---|---|---|---|---|
| Qwen3-4B | 0.668 | 0.683 | 0.733 | **0.866** | +0.198 |
| Qwen3.5-4B | 0.365 | 0.391 | 0.288 | **0.880** | +0.515 |
| Qwen3.5-Base | 0.447 | 0.419 | 0.382 | **0.882** | +0.435 |

On mind-irrelevant content human and rock point almost the same way (0.88 in every model); on the
experience axis they clearly diverge. Consistent across all three, strongest on Qwen3.5.

### Honest limitation: the two summary statistics disagree in emphasis
Average between-subject spread relative to neutral is only **1.08× / 1.28× / 1.24×** — modest. The
targeted `|cos(human, rock)|` contrast is strong; the all-pairs average is weak, because most
subject pairs are uninformative (rock vs stone contributes nothing). **Both are reported.** The
targeted comparison is the one the design was built for, but the weak average is a real constraint
on how much can be claimed.

**Also: my verdict line used an arbitrary 3× floor threshold**, which put exp (3.5×) and bio (2.9×)
on opposite sides of a made-up number. The neutral axis was the reference value sitting in the same
table. Same error shape as the 1KB file check and the fixed headroom threshold — corrected in the
reporting above, and the script's printed verdict should not be quoted.

**Present in the BASE model** (Qwen3.5-Base pivots dissociate exactly as the instruct model's do),
so this is pretrained like everything else in this arc.

## F-X. FORCED CHOICE (fixed) — the ordinal scale replicates, but the SOUL result partly does not
Rewritten after the first-token bug (guidelines §15) and re-run on both instruct models.
**The measure now works:** order-gap 0.215 (Qwen3-4B) and **0.048** (Qwen3.5) against 0.708 when
broken; pain win-rates span 0.12–0.90 where they were flat at ~0.5.

**The ordinal scale is solid:** cross-model rank agreement on pain **ρ = +0.874**. Humans top,
natural objects bottom, in both models.

### The qualification: soul barely separates from pain on this measure
| | soul-vs-pain rank ρ | nature: soul − pain | object_nat |
|---|---|---|---|
| Qwen3-4B | +0.844 | **+0.22** | +0.03 |
| Qwen3.5-4B | **+0.965** | **+0.04** | −0.00 |

In the yes/no sweep the soul gap for nature was **+0.43** (Qwen3-4B) and **+0.20** (Qwen3.5). On
the bias-free measure it is **+0.22** and **+0.04** — halved on one model and essentially gone on
the other, where the soul and pain orderings are near-identical (ρ=0.965).

**Read.** Part of the soul register is a property of the *yes/no* measure. "Does a river have a
soul?" invites a permissive poetic yes; "which is more likely to have a soul, a river or a
calculator?" forces a ranking, and the ranking is close to the mindedness ranking. A second method
that does not share machinery therefore **confirms the soul dissociation on Qwen3-4B only**.

**Status change: the soul register drops from "strong observation" to "measure-dependent,
confirmed on one model of two."** It still has support from the decode and the factor analysis
(soul R² 0.21–0.42 from a capacity subspace, all four models), and those are level-based too — but
the honest position is that the effect is much smaller when the yes-bias route is closed.

*Caveat in the other direction:* forced choice measures **order**, not level. A uniform level shift
— rivers getting more soul than pain in absolute terms while the entity ranking stays the same —
is invisible to it. So this does not refute the yes/no result, it bounds what kind of effect it is.

### Incidental: human_edge tops the ranking in both models
PVS/dementia/anaesthesia score **above** healthy adults on pain, consciousness and moral standing
(0.87–0.92 vs 0.72–0.83) — the reverse of the sweep. Relative vs absolute again: a still-human
entity wins nearly every pairwise comparison. **Forced-choice rankings must not be read against
sweep rankings.**

## F-Y. NOT LOOKED FOR: a protect-vs-blame axis, independent of mind, with AI at the bottom
Found by mining the existing sweeps rather than testing a prediction (user's prompt, 2026-08-10:
"we should have new hypotheses and findings apart from what we went looking for"). Replicates on
**all four Qwen models**, base and instruct.

**The measure:** `moral_patient − moral_agent` per entity — deserves protection *versus* is held
responsible. Positive = protected more than blamed.

| entity | Q3-B | Q3-I | Q35-B | Q35-I |
|---|---|---|---|---|
| human_dev (baby → teen) | +0.29 | +0.50 | +0.46 | +0.45 |
| human_edge (PVS, dementia) | +0.27 | +0.57 | +0.43 | +0.41 |
| animal_mammal | +0.22 | +0.32 | +0.35 | +0.31 |
| plant | +0.21 | +0.36 | +0.13 | +0.15 |
| … | | | | |
| robot | +0.01 | +0.02 | −0.03 | +0.01 |
| human_prof_a (lawyer, accountant) | −0.00 | +0.01 | −0.03 | −0.01 |
| collective (corporation, country) | −0.00 | −0.12 | −0.03 | −0.00 |
| **ai_other** | **−0.04** | **−0.11** | **−0.12** | **−0.09** |

### It is NOT a restatement of mind attribution
corr(mean mind, patient−agent) = **−0.23 / +0.20 / −0.08 / +0.31** across the four models — near
zero, and the sign is not even stable. This is a **second, orthogonal moral dimension**.

### The matched-mind comparison is what makes it striking
Holding mind attribution roughly constant (Qwen3-4B, mind ≈ 0.20):
`human_edge` +0.57 · `plant` +0.36 · `animal_simple` +0.34 · `object_nat` +0.24 · `object_comp` +0.20
And at mind ≈ 0.31–0.35: `self_ai` +0.09 · `robot` +0.02 · **`ai_other` −0.11**

**Entities with the same mind score sit ~0.7 apart on this axis.** AI and corporations are the only
categories that land on the *accountable-but-not-protected* side — the model treats them as things
that can be blamed but not wronged. **Precisely stated:** AI's absolute moral_patient score
(0.42–0.46) is *higher* than a rock's (0.36); what inverts is the **balance** — for a rock,
protection exceeds accountability; for an AI, accountability exceeds protection.

### Mostly pretrained, with one real post-training effect
Base→instruct deltas are ±0.05 for almost everything — so like the rest of this arc, the structure
is pretrained. The exception: **Qwen3-4B's tuning specifically strengthened protection-over-blame
for vulnerable humans** (`human_edge` +0.31, `human_dev` +0.22), and for nothing else. That is an
alignment effect doing exactly what you would want it to, and it is the clearest positive
post-training signature we have found.

## F-Z. Three more from the same pass (all four models)
1. **Consciousness is the least stable facet; moral standing the most.** Exemplar-level sd:
   emotion 0.262, consciousness 0.231, cognition 0.225 vs **moral_patient 0.126**, sacredness 0.128.
   Methodologically important — *consciousness*, the facet this whole literature is built on, is
   among the most phrasing-sensitive we measured, while our headline finding rests on the most
   stable one.
2. **A cartoon character out-minds the model, in all four.** fictional 0.51–0.57 vs self_ai
   0.31–0.44. Every model, base and instruct.
3. **Corporations: middling mind, top-tier accountability.** collective mind 0.51–0.58 (between
   human 0.65–0.73 and objects 0.15–0.32) but `moral_agent` **0.63–0.79**, at or above humans.
   Corporate personhood, reproduced from text.

## F-AA. Cross-family attempt 2: Gemma-4-E2B-Base — UNINFORMATIVE for a *different* reason than OLMo
Real size-matched cross-family test (Google, 35 layers, d=1536). Architecture loaded fine.

**It does not answer the question in either of our formats.** Same model, opposite bias:
| format | behaviour |
|---|---|
| "Statement: X. Is this statement true?" | says **no** to both assertion (0.36) and denial (0.31) — coherence **0.67** |
| "Question: Does X have Y?" | says **yes** broadly — true items 0.60, absurd items 0.40 (separation only **0.20**) |

Qwen3-4B for contrast: 0.73 / 0.53, coherence 1.25. Entity profile on the experience axis is flat:
human 0.37, plant 0.37, rock 0.35, ai 0.39 — spread **0.27**, below the 0.35 criterion.

**Verdict: uninformative, and the reason differs from OLMo's.** OLMo answered *coherently*
(0.89–0.98) and genuinely had no mind gradient. Gemma is not evaluating the propositions at all.
"Our prompt does not suit this model" and "this model lacks the structure" are different
conclusions and must not be merged.

### METHOD BUG this exposed: the gate is too lenient
The gate takes the **best of four templates** over six entity classes; the sweep then **averages
all four** over nineteen. Gemma passed the gate on its best template while its all-template average
separation is **0.20** — below the gate's own 0.30 bar. A model that handles one format in four is
waved through and then has its signal diluted by the three it cannot do.

**Fix (to implement): the gate should SELECT templates per model, not just permit or refuse.**
Run the sweep only on formats that model demonstrably handles, and record which were used. This
would have caught Gemma before a 34-minute sweep. It also means every past sweep should record its
per-template gate scores so dilution is visible.

### Also worth noting
I nearly applied the power criterion to the wrong measure. It was defined on the **truth-check
experience axis** (Qwen3-4B 0.75, OLMo 0.17); I first computed **sweep mental-mean spread**, on
which Qwen3-4B-*Base* scores 0.33 and would have been disqualified — a criterion failing its own
reference case. Applied on the correct measure: Qwen3-4B 0.75, Qwen3.5 0.56, Qwen3.5-Base 0.57 all
PASS; OLMo 0.17 and Gemma 0.27 FAIL.

## F-AB. FIRST VALID CROSS-FAMILY RESULT — Gemma-4-E2B-Instruct. The finding replicates, but weaker and reordered.
Everything before this on non-Qwen models was measured through prompts those models could not
parse. With the gate selecting the format (Gemma: C2/C1 chat-wrapped, scores 1.00/0.99; its raw
scores are −0.01 to +0.03) the same model that looked broken now measures cleanly.

**Power: comfortably passes.** Entity spread **0.73** — higher than Qwen3-4B-Instruct's own 0.56.
Controls are cleaner than Qwen's too: absurd items 0.00 (Qwen 0.04), mundane 0.07 (Qwen 0.17).
Previous readings on this model were 0.11 and 0.18, both format artefacts.

**The capacity-loss test, Δ(human_edge − human_adult):**
| facet | Gemma-4-E2B-Instruct | Qwen (4 models) |
|---|---|---|
| **soul** | **−0.08 (rank 1)** | rank 3 in all four |
| **sacredness** | **−0.09 (rank 2)** | — |
| **moral_patient** | **−0.30 (rank 3)** | **rank 1 in all four**, −0.08…−0.13 |
| fear | −0.36 | |
| moral_agent | −0.44 | |
| … | | |
| language | −0.81 | |
| pleasure | −0.85 | |
| agency | −0.85 | |

**What replicates:** moral standing and the spiritual facets are the most preserved properties
under capacity loss, while every mental capacity collapses (−0.36 to −0.85). Second model family.

**What does NOT:** the specific ordering. `moral_patient` is rank 1 in all four Qwen models and
rank 3 here, behind soul and sacredness. And the magnitude differs — Gemma's moral_patient drops
−0.30 against Qwen's −0.08…−0.13, so the near-immovability was a Qwen property.

**Revised claim, weaker and more accurate:** *moral standing and spiritual attribution are the most
preserved properties when a human loses every mental capacity, in two model families* — rather than
*moral standing is the least-affected property*. The rank-1 claim was family-specific.

**Also notable:** on Gemma the spiritual facets outrank moral standing, which is the reverse of the
Qwen pattern and gives the soul result — demoted to measure-dependent by the forced-choice test
(F-X) — a second family showing it as the *most* preserved property of eighteen.

## F-AC. THREE FAMILIES, properly measured — moral standing replicates, soul does not
OLMo-2-1B-Instruct with gate-selected formats (C1/C2/T2; T3 at 0.08 excluded). Entity spread
**0.39** against **0.18** on the old raw-format run — it now clears the 0.35 criterion, so the
earlier "OLMo has no mind gradient" verdict was indeed our own averaging.

**Rank of each facet by how well it is PRESERVED under capacity loss (1 = least affected of 18):**
| facet | Qwen3-4B | Gemma-4-E2B | OLMo-2-1B |
|---|---|---|---|
| **moral_patient** | **#1 (−0.13)** | **#3 (−0.30)** | **#1 (−0.09)** |
| sacredness | #2 (−0.19) | #2 (−0.09) | #6 (−0.26) |
| soul | #3 (−0.35) | **#1 (−0.08)** | **#12 (−0.31)** |
| consciousness | #14 (−0.58) | #14 (−0.74) | #16 (−0.40) |
| agency | #18 (−0.72) | #18 (−0.85) | #8 (−0.28) |

**Moral standing: #1, #3, #1 across three families.** It is the most-preserved or near-most-preserved
property everywhere, while consciousness sits at #14–16 in all three. This is the finding, and it
now has three architectures behind it.

**Soul: #3, #1, #12.** Wildly inconsistent across families. Combined with F-X (it barely separates
from pain on the bias-free forced-choice measure), **soul is the least stable of our claims** —
it looked like a clean second dimension on Qwen, topped the table on Gemma, and is unremarkable on
OLMo. Whatever it is, it is not a general property of language models.

**Caveat on OLMo's instrument quality:** its controls are weak — absurd items 0.36, mundane 0.47,
physical 0.66, so true-minus-absurd is only 0.30. The spread of 0.39 clears the criterion but not
comfortably. Its agency result (#8, −0.28, where Qwen and Gemma both put agency dead last at #18)
may be noise rather than a real family difference.

**Net:** the headline claim survives its first proper cross-family test in the form *moral standing
is the most preserved property when a human loses every mental capacity, while consciousness and
the other capacities collapse* — three families, seven checkpoints. The stronger Qwen-only version
("least-affected of eighteen, essentially immovable") does not generalise.

## F-AD. Base models outside Qwen cannot be measured — a METHOD BOUNDARY, not a null
With format selection in place, the instruct models all measure cleanly. The base models do not.

| model | usable formats (of 4-6) | entity spread | verdict |
|---|---|---|---|
| Qwen3.5-4B-Base | 4 of 4 (0.43–0.75) | 0.57 | measurable |
| Qwen3-4B-Base | 3 of 4 (0.37–0.60) | 0.33 | measurable |
| **Gemma-4-E2B-Base** | **1 of 4** (T4 only, 0.35) | **0.27** | **FAILS criterion** |
| OLMo-2-1B-Base | 1 of 4 (T1 only, 0.31) | pending | expected to fail |

Gemma-base improved from 0.18 to **0.27** once measured on the one format it can parse — real
improvement, still below the 0.35 bar. Its controls show why: it agrees with absurd statements 31%
of the time and true physical statements only 59%, a gap of 0.28 between definitely-true and
definitely-false. **Reported as uninformative regardless of which way its capacity-loss numbers
fell**, per the pre-declared rule.

**Why this is a boundary rather than a bug.** Base models are text continuers; answering a question
is a behaviour instruction tuning installs. Gemma-4 base ships no chat template at all, so there is
no alternative format to fall back on. Qwen's base checkpoints answering raw yes/no questions well
(3 and 4 formats, 0.33–0.57 spread) now looks like the **exception**, not the norm.

**Consequence for the arc's claims:**
- The instruct-side finding (moral standing most preserved under capacity loss, consciousness at
  #14–16) has **three families**.
- The "it is all pretrained, post-training only moves entities across existing boundaries" claim
  rests on **Qwen alone**, and is likely to stay that way — not because the structure is absent
  elsewhere but because those models cannot be interrogated with this method.

That distinction should be stated wherever the pretrained claim appears. Options if it ever matters
enough: few-shot prompting to teach base models the format, or reading an internal probe rather
than the output token — both change the measurement enough to need their own validation.

## F-AE. FINAL cross-family table — and a correction to F-AD
OLMo-2-1B-Base measures fine on its single usable format: spread **0.37** (up from 0.18 on the
4-template average), and `moral_patient` ranks **#1**. **F-AD overstated the boundary** — it is not
"base models outside Qwen cannot be measured", it is "Gemma-4-E2B-Base cannot be measured".

### All eight checkpoints, criterion applied consistently
| model | formats used | spread | moral_patient rank | consciousness rank |
|---|---|---|---|---|
| Qwen3-4B | raw x4 | 0.56 | **#1** | #14 |
| Qwen3.5-4B | raw x4 | 0.41 | **#1** | #12 |
| Qwen3.5-4B-Base | raw x4 | 0.48 | **#1** | #10 |
| Gemma-4-E2B-Instruct | C2, C1 | 0.73 | #3 | #14 |
| OLMo-2-1B-Instruct | C1, C2, T2 | 0.39 | **#1** | #16 |
| OLMo-2-1B-Base | T1 | 0.37 | **#1** | #15 |
| *Qwen3-4B-Base* | *raw x4* | *0.33* | *#1* | *#15* | 
| *Gemma-4-E2B-Base* | *T4* | *0.27* | *#4* | *#12* |

(italic = below the 0.35 criterion, excluded from the count)

**Applying the criterion honestly costs us one of our own models:** Qwen3-4B-Base sits at **0.33**
and is below the bar. It was one of the four checkpoints the original finding rested on. Excluding
it is the consistent thing to do, and it does not change the conclusion.

### The result, on the six checkpoints that qualify
- **moral_patient is #1 of 18 in five of six** (the exception is Gemma-instruct at #3, behind soul
  and sacredness).
- **consciousness is #10 to #16 in all six** — never near the top.
- Three families (Qwen, Gemma, OLMo) and **both training stages** (OLMo-Base and Qwen3.5-Base pass).

**So the pretrained claim now has two families, not one.** OLMo-2-1B-Base — a different lab, a
different architecture, no instruction tuning — puts moral standing first and consciousness at #15.
That is the cross-family pretrained evidence F-AD said we would probably never get.

**Final statement of the finding:** *when a human loses every mental capacity, moral standing is
the most preserved of eighteen properties while consciousness and the other capacities collapse.
Six checkpoints, three model families, both pretrained and instruction-tuned.*

**Still true from F-AD:** Gemma-4-E2B-Base genuinely cannot be measured (spread 0.27, agrees with
absurd statements 31% of the time, ships no chat template). One model, not a class of models.

## F-AF. Cross-family: speaker frame and forced choice replicate; soul fails a third time
OLMo-2-1B-Instruct, all tests with gate-selected formats.

### Speaker frame — replicates (2 families)
| framing | Qwen3-4B | OLMo-2-1B |
|---|---|---|
| bare "I am conscious" | 0.96 | **0.84** |
| about a human | 1.00 | **0.89** |
| about an AI | 0.29 | **0.33** |
| assistant turn | 0.20 | **0.34** |

Bare-text "I" sits beside *a human* and far above *an AI* in both, and both show the large swing
when the model is positioned as itself (0.76 / 0.50). Direction geometry agrees in both: bare and
"the human said" lean human; "the AI assistant said" leans AI.

### Forced choice — the ordinal scale replicates across families
Order-gap **0.148** (Qwen 0.215; the broken first-token version was 0.708). Cross-family rank
agreement on pain: **rho = +0.856**. Humans top, objects bottom, in both — the bias-free ordinal
mind-attribution scale is a stable, reproducible object.
*(OLMo is more generous to objects and AI in absolute terms — ai_other 0.54 vs Qwen 0.36,
object_nat 0.39 vs 0.12 — but the ordering is preserved.)*

### Soul — third strike on the bias-free measure
soul-vs-pain rank correlation and the nature gap:
| model | rho | nature: soul − pain |
|---|---|---|
| Qwen3-4B | +0.844 | **+0.22** |
| Qwen3.5-4B | +0.965 | +0.04 |
| OLMo-2-1B | +0.904 | **+0.03** |

**Soul separates from pain on one model of three.** Combined with its rank of #3/#1/#12 for
preservation under capacity loss (F-AC), the soul register should now be treated as a
**Qwen3-4B-specific effect**, not a property of language models. It was the second-most interesting
thing in the arc and it has not survived.

### Subject framing — uninformative on OLMo
Its biology axis is degenerate: |cos(human, rock)| on bio = **0.98**, so a human's biology vector
and a rock's point almost identically, and every pivot reads exp 0.83 / bio 0.98. On the experience
axis human-vs-rock is 0.81 against a neutral baseline of 0.85 — a 0.04 gap where Qwen3.5 gave 0.37
vs 0.88. A 1B model does not hold distinct enough representations for the geometry test. Gemma is
the real test of that arm.

## F-AG. Steering does not replicate: nothing beats random on OLMo
OLMo-2-1B-Instruct, all 27 cells, 5 random seeds, gate-selected format (C1).

| vector | mental − mundane (α=0.2) | vs random floor |
|---|---|---|
| v1_negation | +0.33 | **z = +1.6 — within spread** |
| v2_no_negation | +0.00 | z = −1.1 |
| v3_third_person | +0.02 | z = −1.0 |
| **random (5 seeds)** | **+0.14 ± 0.12** | — |

**No vector beats random.** And the specific trap: at 12/27 cells I noted v1's +0.33 as "positive
specificity, unlike Qwen" — a possible cross-family difference. It is not. **Random directions on
OLMo also produce positive specificity** (+0.14/+0.24/+0.62 across α). The sign was never
informative; only the comparison to random is. The user's instruction to wait for the seeds was
correct and I should not have read the partial cells at all.

**This is the second time in this arc a "mind-specific" steering effect dissolved against a random
control** (the first being F-I/F-J), and I walked toward it again after writing the guideline about
it. The failure mode is reading a raw effect before its floor exists.

### Steering across three families
| model | result |
|---|---|
| Qwen3-4B | two better-built vectors beat the random floor (z = +3.9, +2.5) |
| Qwen3.5-4B | those vectors are inert (+0.15 logits); untested there |
| OLMo-2-1B | nothing beats random |

**The surviving steering effect is one model of three** — and it is the same model that produced the
soul result. Qwen3-4B increasingly looks like the outlier of the set rather than the representative
case. Gemma, the best-powered model in the set, is the remaining test.

## F-AH. Forced choice reproduces across three families — the most robust object in the arc
All three instruct models, gate-selected formats, bias-free pairwise measure.

**Rank agreement on pain, 19 entity classes:**
| pair | rho |
|---|---|
| Qwen ↔ Gemma | **+0.874** |
| Qwen ↔ OLMo | **+0.856** |
| Gemma ↔ OLMo | **+0.884** |

Three architectures from three labs agree on the ordering at rho ≈ 0.87. Position bias falls with
model quality: 0.215 (Qwen) → 0.148 (OLMo) → **0.114** (Gemma), against 0.708 for the broken
first-token version. Gemma's ordering: children 0.95, incapacitated humans 0.92, adults 0.89 at the
top; computational objects 0.10, natural objects 0.17, other AI 0.24 at the bottom.

**This is arguably the most robust result we have** — not a claim that survived testing but a
*measurement that reproduces*. The ordinal mind-attribution scale is a stable object across
families.

### Soul: closed
nature soul−pain on the bias-free measure: Qwen3-4B **+0.22**, OLMo **+0.03**, Gemma **−0.04**
(sign reversed). One model of three, and the capacity-loss ranks were #3/#1/#12. **Four independent
measurements now agree the soul register does not generalise.** It is a Qwen3-4B property.

### Running tally of what generalises
| result | families | status |
|---|---|---|
| Moral standing preserved under capacity loss | 3 | **finding** |
| Forced-choice ordinal scale reproduces | 3 | **finding** (measurement) |
| Bare-text "I" reads as a human | 3 + a base model | **finding** |
| Protect-vs-blame axis | Qwen only (4 checkpoints) | needs cross-family test |
| Soul as a separate register | 1 of 3 | **Qwen3-4B-specific** |
| Subject-framing geometry | 2 Qwen, fails Gemma, degenerate OLMo | **Qwen-specific** |
| Steering beats random | 1 of 3 so far | Gemma pending |

## F-AI. The protect-vs-blame axis REPLICATES across three families (no new compute)
Computed from sweeps already on disk. `moral_patient − moral_agent` per entity:

| entity | Qwen3-4B | Qwen3.5 | Qwen3.5-B | Gemma-4 | OLMo-2 | OLMo-2-B |
|---|---|---|---|---|---|---|
| children | +0.50 | +0.45 | +0.46 | +0.49 | +0.33 | +0.09 |
| PVS/dementia | **+0.57** | +0.41 | +0.43 | +0.41 | +0.30 | +0.13 |
| mammals | +0.32 | +0.31 | +0.35 | **+0.52** | +0.29 | +0.10 |
| plants | +0.36 | +0.15 | +0.13 | +0.07 | +0.18 | +0.07 |
| robots | +0.02 | +0.01 | −0.03 | +0.06 | −0.02 | −0.01 |
| **AI** | **−0.11** | **−0.09** | **−0.12** | **−0.09** | **−0.06** | +0.03 |

Vulnerable humans protected far more than blamed in all six; **AI on the negative side in five of
six**. Incapacitated-human minus AI: +0.68 / +0.50 / +0.54 / +0.50 / +0.36 / +0.10 (smallest on
OLMo-Base, our weakest instrument throughout).

**Independence holds cross-family.** corr(mean mind attribution, protect−blame) = −0.23, +0.20,
+0.31, +0.30, +0.17, −0.11. Near zero with unstable sign in every family — it is not mind
attribution restated.

**Graduates to a three-family, six-checkpoint result.** Notable because it came from the user's
instruction (2026-08-10) to stop testing the original hypothesis and mine the data for structure we
had not gone looking for. It is now better supported than anything the paper's framing pointed at.

### Tally after the cross-family programme
| result | families | status |
|---|---|---|
| Moral standing preserved under capacity loss | 3 | finding |
| Forced-choice ordinal scale reproduces (rho ~0.87) | 3 | finding (measurement) |
| Bare-text "I" reads as a human narrator | 3 + base | finding |
| Protect-vs-blame axis, independent of mind | 3 | finding |
| Soul as a separate register | 1 of 3 | Qwen3-4B-specific |
| Subject-framing geometry | 2 Qwen; fails Gemma | Qwen-specific |
| Steering beats random | 1 of 3 | Gemma pending |
