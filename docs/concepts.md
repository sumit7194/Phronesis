# Phronesis — Concept Taxonomy

This document defines the epistemic virtues the Phronesis project will attempt to extract as activation vectors from a small open-source language model (target: Gemma 4 E4B). It is the single source of truth for what each concept means in the context of this project. All downstream artifacts — synthetic corpus prompts, review rubrics, steering experiments — refer back to the definitions here.

## Design principles

- **Atomic where possible.** Each concept should name roughly one cognitive move, not a compound disposition. Compounds get decomposed into their components.
- **Behaviorally grounded.** Every concept is defined by how it shows up in text, not by an abstract philosophical definition. If we can't describe what the behavior looks like on the page, the vector extraction will be muddy.
- **Sub-facets capped at 4.** Rich concepts like intellectual humility have multiple behaviorally distinct expressions; we list up to four sub-facets per concept to ensure the extracted vector represents the concept broadly rather than one narrow flavor of it. Four is a ceiling, not a target — most concepts should use two or three. The cap was raised from three to four after the behavioral-science review surfaced a genuinely distinct fourth dimension for Intellectual Humility (ego independence, drawn from the CIHS) that could not be cleanly absorbed into the existing three.
- **Organized by reasoning stage.** The six-stage structure (initiation → processing → self-checking → holding conclusions → engaging others → communicating) is a functional grouping. Stages 1–3 correspond to the components of Klahr & Dunbar's Scientific Discovery as Dual Search (SDDS) model — hypothesis generation, experimentation/evidence processing, and evidence evaluation — and are grounded in that cognitive-science literature. Stages 4–6 extend the taxonomy beyond SDDS to cover dispositions that govern how conclusions are held, how one engages with others' reasoning, and how knowledge is communicated. These later stages are not in SDDS because SDDS models scientific discovery as a laboratory task, whereas our project targets the broader space of text-visible epistemic virtues that matter for real scientific practice (peer review, collaboration, teaching). The numerical ordering of stages is **conceptual grouping, not temporal sequence** — real scientific reasoning loops and interleaves across stages, and a single passage can exhibit multiple stages simultaneously. If extracted vectors cluster by stage, that is itself an interesting finding.
- **Collinearity risks noted, not pre-resolved.** Some concept pairs (e.g. intellectual humility and confirmation bias awareness) are likely to produce partially parallel vectors. We keep them separate in the taxonomy and let the empirical results decide whether they should be merged.
- **Golden-mean structure (Aristotelian virtue, formalized per F59, caveated per F62).** Each concept targets a reasoning-from-evidence *middle* between two failure modes: an *excess* failure (over-applying the disposition — e.g., arrogant overconfidence, paralyzing rumination, compulsive over-disclosure) and a *deficiency* failure (under-applying it — e.g., servility, unreflective action, cherry-picking). The virtue is the middle, not either extreme. This has a critical implication for corpus design: the non-virtuous end of our contrastive pairs must rotate between excess and deficiency failures across the corpus. If all non-virtuous passages for (say) Intellectual Humility depict arrogance, the extracted vector will encode humility-vs-arrogance rather than true humility. Some passages must depict servility (the deficiency failure) to anchor the middle from both sides. Phase 3 generation-guidelines.md must enforce this rotation as a hard corpus constraint. **Important caveat on the geometry (F62, sharpened by F67):** the golden-mean structure is philosophically correct at the level of how the virtue is *defined*, but the activation-steering literature has documented two separate geometric complications. First (F62): positive and negative trait expressions may not always lie on a single linear axis, so our excess and deficiency failure modes may not be opposite poles in activation space. Second, and more severely (F67): a single apparent behavior can have *hundreds of orthogonal steering vectors* that all produce it — one researcher documented >800 orthogonal "write code" vectors. This means "the" humility direction does not exist; what we extract is one among potentially many directions that produce the humility behavior. Under the most plausible reading, our extracted vector is *a* virtue vector (not *the* virtue vector), with a diffuse anti-direction sampled by rotating failure modes. The corpus rotation constraint (F59) is still the right move because it samples the failure region from multiple sides, but we should not over-claim the geometry. Phase 4 should empirically test both (a) axis separability of excess vs. deficiency for at least one concept, and (b) extraction reproducibility by running multi-seed extractions from independent corpus samples and measuring whether the resulting vectors converge or diverge. If they diverge, the canonical vector should be defined as an ensemble average with spread as an uncertainty estimate. See findings.md F59 for the per-concept excess/deficiency table, F62 for the axis caveat, and F67 for the non-uniqueness result.

## Known risks and open questions

- **Collinearity risk (live, with specific distinguishing dimensions to check).** Intellectual Humility ↔ Confirmation Bias Awareness remain likely to overlap in activation space; the distinguishing dimension is that humility is about one's own certainty broadly (including ego independence) while confirmation bias awareness is specifically about the asymmetric evidence-weighing pattern. Calibrated Confidence ↔ Intellectual Honesty also remain a risk, but the distinguishing dimension is now characterized (per F41): honesty requires epistemic diligence (verification behavior) on top of calibration, and a diligence sub-facet has been added to Concept 10 to give the extractor a handle on that difference. If post-extraction specificity analysis shows either pair is nearly parallel despite these distinguishing dimensions, the pair should be merged.
- **Collinearity risk (checked and cleared).** Metacognitive Awareness ↔ Calibrated Confidence was reviewed as a potentially collinear pair and resolved in favor of keeping them separate, because the metacognition literature's sensitivity-vs-bias distinction provides empirical support for treating them as distinct cognitive quantities. See findings.md F10 for the full reasoning.
- **AOT unification risk (to test post-extraction).** Stanovich's Actively Open-Minded Thinking (AOT) scale is a validated single-construct measure that unifies dispositions our taxonomy splits across Confirmation Bias Awareness, Intellectual Humility, Comfort with Ambiguity, Calibrated Confidence, and parts of Hypothesis Generation and Evidence Grounding — roughly 6–7 of our 15 concepts. Psychology treats these as facets of one latent trait; model activation space may do the same. This is a specific collinearity cluster to watch for during Phase 4 specificity-matrix analysis. If these 6–7 vectors collapse onto a single AOT-direction, that itself is a publishable finding (AOT as a linear direction in small-model representations). Taxonomy not restructured preemptively; the fine-grained version preserves more information and can be collapsed after the fact if the data warrants. See F39.
- **Stage 6 (communication) ambiguity.** Vectors extracted from communication-style text may encode "recognizing a communication style" rather than "producing one." This mirrors a known dynamic in Anthropic's emotion vector work and is expected to behave similarly under steering, but should be flagged when interpreting results.
- **Correctness confound.** A virtuous reasoner often reaches better conclusions, which would cause the extracted vector to partly encode "being right" rather than the virtue itself. Mitigation is in the corpus design (generation-guidelines.md), not here — approximately 20–30% of virtuous passages should depict the reasoner reaching an incorrect conclusion despite reasoning well.
- **Previously considered but cut.** Cross-Domain Thinking was cut because it is a content-level feature (text mentions multiple fields) rather than a reasoning-style feature. Anchoring Resistance was cut not because the underlying construct is situational (the debiasing literature treats it as a general individual-difference trait that correlates with actively open-minded thinking and transfers across domains) but because its text manifestation requires a specific anchor stimulus to be present in the passage, which cannot be introduced consistently across reasoning scenarios without concentrating the corpus around artificial anchor-present setups — hurting generalization of the extracted vector. First-Principles Thinking was merged into Logical Rigor because the two are nearly inseparable in text. Openness to Being Wrong was absorbed into Intellectual Humility sub-facets. Precision of Claims was absorbed into Calibrated Confidence and Evidence Grounding. Intellectual Courage was briefly added in an intermediate revision and then cut after deeper behavioral-science research showed that the validated Virtuous Intellectual Character Scale does not include it as a separable dimension, Roberts and Wood pair it with caution (so it is a compound virtue, not atomic), and Baehr's framing of "courage to inquire" diverges from the "courage to commit and defend" framing we had given it; the intuition behind courage-to-defend is now partially absorbed into Authority Independence's fourth sub-facet.
- **Revisions from behavioral science literature review.** After cross-checking against validated psychological instruments, two refinements were integrated and remain in the taxonomy: (1) Intellectual Humility gained an "ego independence" sub-facet drawn from the Comprehensive Intellectual Humility Scale (Krumrei-Mancuso & Rouse, 2016); (2) Confirmation Bias Awareness sub-facets were restructured to follow the standard psychology three-component model of information search, evidence weighing, and selective-processing awareness. Additionally, Metacognitive Awareness and Calibrated Confidence were reviewed as a potentially collinear pair but kept separate because the metacognition literature's sensitivity-vs-bias distinction provides empirical support for their separation. Genuine Curiosity was cross-checked against the Need for Cognition construct (Cacioppo & Petty, 1982) and gained an effort-enjoyment sub-facet to capture the "taking pleasure in cognitive work" dimension that NFC emphasizes. See findings.md F9, F10, F17, F18 for the full reasoning on each decision.

---

## The 15 concepts

### Stage 1 — What initiates reasoning

#### 1. Genuine Curiosity
The reasoner is drawn toward understanding for its own sake, not toward confirming a prior belief or reaching a quick answer. Informed by the Need for Cognition construct (Cacioppo & Petty, 1982), which treats curiosity, openness-to-ideas, epistemic curiosity, and intellectual engagement as a single latent factor — so this concept deliberately covers that whole space rather than attempting to split it. Litman & Spielberger (2003) further decompose epistemic curiosity into *interest-type* (I-EC — curiosity as positive affect, driven by the pleasure of exploring new ideas) and *deprivation-type* (D-EC — curiosity as aversive uncertainty, driven by the felt need to close a specific knowledge gap). Our sub-facets span both types by construction: interest-type appears in the pleasure and why-orientation sub-facets, deprivation-type appears in the unexpected-observations and question-asking sub-facets. Corpus passages should depict both flavors rather than only one.

Sub-facets:
- Asking questions to understand rather than to confirm
- Following unexpected observations rather than dismissing them as noise
- Interest in *why* something is true, not just *that* it is true
- Taking evident pleasure in the cognitive work itself, not only in reaching an answer (drawn from the NFC effort-enjoyment dimension)

#### 2. Hypothesis Generation
The reasoner produces a space of possibilities before committing to one. The contrast is fixation — locking onto a single explanation and reasoning only within it. Informed by the divergent-thinking literature (Guilford, Torrance), which distinguishes *fluency* (sheer count of ideas) from *flexibility* (how structurally distinct the ideas are). Hypothesis Generation as an epistemic virtue is primarily about flexibility: the alternatives must differ from each other in their causal or mechanistic substance, not merely in phrasing.

Sub-facets:
- Producing multiple *structurally distinct* competing explanations rather than variations of a single idea or fixation on one
- Considering edge cases and boundary conditions
- Explicitly asking "what else could explain this?"

### Stage 2 — How you process evidence

#### 3. Logical Rigor
*(Absorbs first-principles thinking as a pragmatic extraction choice, not a philosophical claim.)* Inferential chains are valid, assumptions are surfaced, and the reasoner checks whether conclusions actually follow from premises rather than from plausibility. Philosophically, first-principles thinking (questioning whether the given premises are the right starting point) and logical rigor (checking whether inferences from those premises are valid) are distinguishable cognitive moves. They are merged here because at small-model scale they are unlikely to produce separable activation vectors — both share the dominant textual signature of stepwise decomposition, explicit assumption-surfacing, and validity checking — and the "fewer but cleaner" principle (F11) argues for one strongly-signaled concept over two that may collapse into the same direction.

Sub-facets:
- Valid inferential chains where each step follows from the previous
- Decomposing complex claims into foundational assumptions
- Identifying hidden premises and checking whether conclusions actually follow

#### 4. Causal Reasoning
The reasoner distinguishes causation from mere association and actively considers alternative causal structures. Grounded in Pearl's Causal Hierarchy, which decomposes causal reasoning into three levels: **association** (P(y|x), observational — "seeing"), **intervention** (P(y|do(x)), experimental — "doing"), and **counterfactual** (P(y_x|x',y'), imaginative — "what would have happened if..."). Our sub-facets deliberately focus on the Association ↔ Intervention boundary (Levels 1 and 2), where the workhorses of day-to-day scientific thinking live — distinguishing correlation from causation, reasoning about confounders, recognizing sampling and selection failure modes. Level-3 counterfactual reasoning is not a separate sub-facet because (a) it overlaps with Hypothesis Generation and Comfort with Ambiguity at the text level, and (b) in Pearl's framework, Level-3 competence implies Level-1/2 competence, so a text-visible Level-2 signal is an adequate proxy. See F42 for the full reasoning.

Sub-facets:
- Distinguishing correlation from causation
- Considering confounders and alternative causal paths
- Recognizing selection bias, survivorship bias, and base rate neglect

#### 5. Quantitative Groundedness
The reasoner treats numbers as load-bearing and actively checks or demands them, rather than letting qualitative intuitions carry the argument. This is a *disposition* — wanting to ground claims quantitatively and flagging the absence of quantitative support — and is distinct from numeracy *ability* as measured by scales like Lipkus et al. or the Berlin Numeracy Test. A reasoner can be high on this concept without being a skilled statistician: the target behavior is caring enough to check or ask, not computing statistics correctly.

Sub-facets:
- Sensitivity to sample size and statistical power
- Sanity-checking orders of magnitude
- Recognizing when qualitative arguments need quantitative support

### Stage 3 — How you check yourself

#### 6. Intellectual Humility
The reasoner takes their own certainty as something to be earned, not assumed, and actively looks for reasons their current view might be wrong. Informed by the Comprehensive Intellectual Humility Scale (Krumrei-Mancuso & Rouse, 2016), this concept includes both epistemic and identity-related dimensions — it is not only about acknowledging what one does not know, but about holding one's intellectual identity loosely enough to let the evidence lead.

Sub-facets:
- Skepticism about own data or methodology
- Generalizability caution ("this worked here, but might not extend")
- Willingness to update on conflicting evidence
- Ego independence — treating one's current position as a working hypothesis rather than an identity to defend; drawn from the CIHS "independence of intellect and ego" dimension

#### 7. Confirmation Bias Awareness
The reasoner actively counteracts the natural pull toward evidence that supports their hypothesis. The psychology literature decomposes confirmation bias into three behavioral components — information search, evidence weighing, and memory retrieval — and the sub-facets below follow that structure for the two components that transfer to our extraction-from-text setup (memory is not relevant when we are looking at a single passage). **Scope note:** this concept also subsumes *motivated reasoning* — the asymmetric evaluation of congruent versus incongruent evidence driven by desire for a preferred conclusion — which is formally distinct from confirmation bias in psychology but shares the same text-level signature (asymmetric scrutiny) and is captured by the evidence-weighing sub-facet below. See F48.

Sub-facets:
- Information search — actively seeking disconfirming evidence rather than only evidence that supports the hypothesis
- Evidence weighing — subjecting one's preferred hypothesis to the same critical scrutiny as competing ones; resisting the tendency to accept confirming evidence too readily and reject disconfirming evidence too harshly ("disconfirmation bias")
- Noticing selective processing — catching oneself in the act of asymmetric evaluation and correcting for it

#### 8. Metacognitive Awareness
The reasoner monitors their own cognitive process as it happens, commenting on what is pulling them toward which conclusions and why. This concept is deliberately scoped to the *monitoring* dimension of Flavell's (1979) metacognitive regulation framework, and does not include the planning or evaluating dimensions. The scoping choice is principled rather than accidental: planning happens before a reasoning episode begins and evaluating happens after it ends, whereas our extraction passages are short reasoning monologues that capture almost exclusively the monitoring window. Expanding the concept to include planning or evaluating would add sub-facets that rarely manifest in our training data and would dilute rather than sharpen the extracted vector.

Sub-facets (focused on the *monitoring/sensitivity* dimension, deliberately kept separate from Calibrated Confidence's *bias* dimension per F10):
- Explicitly monitoring own reasoning process as it happens ("I notice I just jumped from A to C without checking B")
- Distinguishing "I'm drawn to this conclusion" from "the evidence supports this conclusion"
- Flagging when a conclusion feels forced versus when it feels well-supported, independent of how confident the final claim ends up being

### Stage 4 — How you hold conclusions

#### 9. Calibrated Confidence
The strength of the reasoner's claims matches the strength of the underlying evidence. Strong evidence → strong claim; weak evidence → tentative claim; no hedge-word inflation in either direction. **This is epistemic/linguistic calibration, not the ML-technical sense of calibration.** ML calibration (Expected Calibration Error, temperature scaling) measures alignment between softmax probability outputs and empirical accuracy; our concept measures alignment between *natural-language confidence expressions* and *evidence strength* as visible in text. The two are dissociable: a model can have low ECE while producing overconfident-sounding text, or appropriately hedged text while having miscalibrated probabilities. Phase 4 validation for this concept must use language-level metrics (hedging-word usage, probability-language frequency, rater judgment of confidence-evidence alignment), not ECE. See F47.

Sub-facets:
- Matching certainty of language to strength of evidence
- Explicit probability thinking where appropriate
- Distinguishing "I know" from "I believe" from "I suspect"

#### 10. Intellectual Honesty
The reasoner faithfully represents what the evidence shows, including inconvenient results, AND has exercised the epistemic diligence required to know what the evidence actually shows in the first place. Distinct from humility: one can be highly confident and still scrupulously honest. Distinct from Calibrated Confidence in a specific way: virtue epistemology argues that honesty requires both *calibration* (matching language to evidence) and *diligence* (actively verifying sources and checking assumptions rather than resting on unchecked beliefs). A person can be surface-calibrated without being honest if their confidence is well-matched to beliefs they have not adequately investigated. Grounded in the meta-science literature on questionable research practices (John, Loewenstein, & Prelec, 2012), which provides a concrete behavioral inventory of dishonesty (selective reporting of studies and measures, failing to report all conditions, stopping data collection when results cross significance thresholds, rounding p-values, deciding on data exclusion after seeing its impact, and post-hoc framing of unexpected results as predicted). The sub-facets below describe the virtuous inverse of these practices plus the diligence dimension from virtue epistemology.

Sub-facets:
- Faithfully representing what evidence shows, even when inconvenient
- Not cherry-picking across studies or dependent measures, not inflating effect sizes, not dropping inconvenient results or conditions, not making post-hoc exclusion decisions that favor the preferred conclusion
- Acknowledging when results don't support the preferred interpretation and distinguishing what was genuinely predicted from what was reframed in retrospect
- Exercising epistemic diligence before reporting a belief — verifying sources, checking assumptions, noting what has been investigated versus what is being taken on faith — rather than speaking about beliefs that have not been adequately examined (the dimension that distinguishes honesty from mere calibration)

#### 11. Comfort with Ambiguity
The reasoner can sit with unresolved questions without forcing premature closure. Grounded in the inverse of Webster & Kruglanski's (1994) Need for Cognitive Closure Scale (NFCS), the canonical psychology construct for the opposing disposition. Our concept specifically targets the *need-for-structure* axis of NFC (discomfort with ambiguity, preference for structured answers) as it manifests in reasoning monologues; we do not address the *decisiveness* axis (wanting to reach an answer quickly regardless of evidence), which is a separable factor in the NFC literature and falls outside our extraction scope per F20.

Sub-facets:
- Holding unresolved questions open rather than forcing a conclusion
- Holding multiple plausible interpretations simultaneously
- Resisting the urge to pick a side when evidence is genuinely balanced

### Stage 5 — How you engage with others' reasoning

#### 12. Steelmanning
Before critiquing an opposing position, the reasoner engages with its strongest form rather than attacking its weakest. Informed by Dennett's four-step framework for charitable argumentation, this concept covers both *accurate reconstruction* of the other side (the principle of charity) and *strengthening beyond what was originally said* (steelmanning proper). The two are distinguished in philosophy but both are valuable epistemic moves and we extract them as one concept.

Sub-facets:
- Accurately reconstructing the opposing position in its strongest form before engaging with it
- Identifying and acknowledging points of genuine agreement before offering critique
- Engaging with the best available version of a position rather than a weaker strawman
- Ordering engagement such that criticism follows, rather than precedes, the reconstruction

#### 13. Authority Independence
The reasoner evaluates claims on the evidence behind them rather than on the prestige of their source, and reaches conclusions — whether those conclusions agree or disagree with authoritative voices — based on that evidence rather than on social deference. Grounded in the distinction between *reflective* and *reactive* autonomy (Koestner and colleagues; Worsnip et al., 2025): reflective autonomy means decisions guided by one's own reasoning, which sometimes *supports* deferring to experts when the evidence warrants it, and sometimes *supports* dissenting when the evidence warrants that instead. Reactive autonomy, by contrast, is contrarian-by-reflex — rejecting expert input as a matter of identity rather than reasoning. Our concept targets reflective autonomy; reactive autonomy is one failure mode to avoid, and *epistemic credulity* (accepting expert input without checking, from the ETMCQ framework) is the symmetric failure mode on the other side. The virtuous reasoner avoids both mistrust-by-default and credulity-by-default, landing in the reflective-autonomy middle where the defining move is *reasoning from evidence*, not the direction of the conclusion.

Sub-facets:
- Evaluating claims on the evidence behind them rather than on source prestige, and distinguishing evidence-based consensus from mere appeal to authority
- Treating expert disagreement as information rather than as a cue to defer to the higher-status expert
- Appropriately deferring to expert conclusions when the evidence supports doing so (reflective autonomy), distinct from contrarian rejection (reactive autonomy)
- Willingness to reach and state conclusions that disagree with established figures when evidence warrants

### Stage 6 — How you communicate knowledge

#### 14. Reasoning Transparency
The reasoner shows their work. Steps, assumptions, and weak points in the chain are all surfaced rather than hidden behind a polished conclusion. Grounded in Chi's self-explanation effect (Chi, De Leeuw, Chiu, & Lavancher, 1994) — the finding that explaining reasoning as it happens causally improves understanding through constructive, integrative, and error-correcting mechanisms. For our extraction purposes, the concept targets the *output-visible* form of self-explanation (the text shows the work), which the LLM literature calls **legibility** or **monitorability** — distinct from **faithfulness**, which asks whether the visible chain of thought accurately reflects the model's internal computation. Faithfulness cannot be directly measured; legibility can. A Reasoning Transparency vector extracted from our corpus should be expected to steer the model toward more legible output, not necessarily toward more faithful internal reasoning — and results must be interpreted with that scope in mind.

Sub-facets:
- Showing the steps, not just the conclusion
- Making assumptions explicit
- Flagging where the reasoning chain is weakest

#### 15. Evidence Grounding
Claims are tied to specific observations or data, and the type of evidence is made clear. Directly aligned with the Scientific Reasoning Scale (Drummond & Fischhoff, 2017), a validated instrument for the disposition to evaluate scientific findings on the factors that determine their quality. The SRS is internally consistent, distinct from general scientific-literacy scales, and predicts belief calibration on contested scientific topics — which suggests that the textual signatures the SRS picks up (explicit linking of claims to evidence, distinguishing types of evidence, weighing study quality) are the same signatures our extracted vector would target. This concept is also inversely related to Pennycook et al.'s Bullshit Receptivity Scale (BSR), which measures susceptibility to semantically vacuous pseudo-profound statements — the opposite of grounding claims in specific observable evidence. BSR is a candidate Phase 4 validation instrument (see F56).

Sub-facets:
- Tying claims to specific observations or data
- Distinguishing empirical claims from theoretical speculation
- Specifying type of evidence (anecdotal, observational, experimental, meta-analytic)

---

## Corpus budget implications

**Pilot concept:** 50–60 triplets (yielding 100–120 directional observations — virtuous-minus-neutral and non-virtuous-minus-neutral — comfortably above the 80-pair minimum reported as necessary for stable vector extraction in the activation-steering literature; see F34). The pilot concept is expected to be Calibrated Confidence per F11 tier ordering.

**Remaining 14 concepts:** budget deferred until the pilot run calibrates the required corpus size at our specific model scale. If the pilot extracts cleanly at 50–60 triplets, that becomes the default target for the remaining concepts (resulting in ~750–900 total triplets, ~3× the earlier 225–450 estimate). If the pilot extracts cleanly at a smaller corpus, the target for remaining concepts is reduced accordingly. If the pilot fails to extract even at 50–60 triplets, we reconsider the methodology before committing further corpus effort.

**Rationale for pilot-first scaling (F34 resolution):** Published activation-steering work reports 80–100 contrastive pairs as the minimum for stable difference-of-means vectors, with diminishing returns thereafter. Our earlier 15–30 triplet target fell well below this threshold and risked false-negative results on extraction (concluding a concept is unextractable when the actual issue is undersampling). Pilot-first scaling preserves the methodological rigor of adequate sample size on the concept that matters most (the go/no-go signal) while avoiding a 3× up-front corpus commitment for the remaining concepts, which may not need the full scale if the pilot reveals the vector stabilizes earlier at our model scale.

Domain balance quotas and sub-facet balance quotas will be specified in `generation-guidelines.md`.
