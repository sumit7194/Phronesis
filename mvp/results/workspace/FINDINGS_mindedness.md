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
