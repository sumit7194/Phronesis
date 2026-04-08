# Phronesis — Concept Taxonomy

This document defines the epistemic virtues the Phronesis project will attempt to extract as activation vectors from a small open-source language model (target: Gemma 4 E4B). It is the single source of truth for what each concept means in the context of this project. All downstream artifacts — synthetic corpus prompts, review rubrics, steering experiments — refer back to the definitions here.

## Design principles

- **Atomic where possible.** Each concept should name roughly one cognitive move, not a compound disposition. Compounds get decomposed into their components.
- **Behaviorally grounded.** Every concept is defined by how it shows up in text, not by an abstract philosophical definition. If we can't describe what the behavior looks like on the page, the vector extraction will be muddy.
- **Sub-facets capped at 4.** Rich concepts like intellectual humility have multiple behaviorally distinct expressions; we list up to four sub-facets per concept to ensure the extracted vector represents the concept broadly rather than one narrow flavor of it. Four is a ceiling, not a target — most concepts should use two or three. The cap was raised from three to four after the behavioral-science review surfaced a genuinely distinct fourth dimension for Intellectual Humility (ego independence, drawn from the CIHS) that could not be cleanly absorbed into the existing three.
- **Organized by reasoning stage.** The six-stage structure (initiation → processing → self-checking → holding conclusions → engaging others → communicating) is a functional grouping. If extracted vectors cluster by stage, that is itself an interesting finding.
- **Collinearity risks noted, not pre-resolved.** Some concept pairs (e.g. intellectual humility and confirmation bias awareness) are likely to produce partially parallel vectors. We keep them separate in the taxonomy and let the empirical results decide whether they should be merged.

## Known risks and open questions

- **Collinearity risk (unresolved).** Intellectual Humility ↔ Confirmation Bias Awareness, and Calibrated Confidence ↔ Intellectual Honesty, are the two pairs most likely to overlap significantly in activation space. Neither pair was addressed by the behavioral-science review; both remain live risks. If post-extraction analysis shows their vectors are nearly parallel, they will be merged.
- **Collinearity risk (checked and cleared).** Metacognitive Awareness ↔ Calibrated Confidence was reviewed as a potentially collinear pair and resolved in favor of keeping them separate, because the metacognition literature's sensitivity-vs-bias distinction provides empirical support for treating them as distinct cognitive quantities. See findings.md F10 for the full reasoning.
- **Stage 6 (communication) ambiguity.** Vectors extracted from communication-style text may encode "recognizing a communication style" rather than "producing one." This mirrors a known dynamic in Anthropic's emotion vector work and is expected to behave similarly under steering, but should be flagged when interpreting results.
- **Correctness confound.** A virtuous reasoner often reaches better conclusions, which would cause the extracted vector to partly encode "being right" rather than the virtue itself. Mitigation is in the corpus design (generation-guidelines.md), not here — approximately 20–30% of virtuous passages should depict the reasoner reaching an incorrect conclusion despite reasoning well.
- **Previously considered but cut.** Cross-Domain Thinking was cut because it is a content-level feature (text mentions multiple fields) rather than a reasoning-style feature. Anchoring Resistance was cut because it is too situational — it only manifests when a specific anchor is present in the scenario. First-Principles Thinking was merged into Logical Rigor because the two are nearly inseparable in text. Openness to Being Wrong was absorbed into Intellectual Humility sub-facets. Precision of Claims was absorbed into Calibrated Confidence and Evidence Grounding. Intellectual Courage was briefly added in an intermediate revision and then cut after deeper behavioral-science research showed that the validated Virtuous Intellectual Character Scale does not include it as a separable dimension, Roberts and Wood pair it with caution (so it is a compound virtue, not atomic), and Baehr's framing of "courage to inquire" diverges from the "courage to commit and defend" framing we had given it; the intuition behind courage-to-defend is now partially absorbed into Authority Independence's fourth sub-facet.
- **Revisions from behavioral science literature review.** After cross-checking against validated psychological instruments, two refinements were integrated and remain in the taxonomy: (1) Intellectual Humility gained an "ego independence" sub-facet drawn from the Comprehensive Intellectual Humility Scale (Krumrei-Mancuso & Rouse, 2016); (2) Confirmation Bias Awareness sub-facets were restructured to follow the standard psychology three-component model of information search, evidence weighing, and selective-processing awareness. Additionally, Metacognitive Awareness and Calibrated Confidence were reviewed as a potentially collinear pair but kept separate because the metacognition literature's sensitivity-vs-bias distinction provides empirical support for their separation. Genuine Curiosity was cross-checked against the Need for Cognition construct (Cacioppo & Petty, 1982) and gained an effort-enjoyment sub-facet to capture the "taking pleasure in cognitive work" dimension that NFC emphasizes. See findings.md F9, F10, F17, F18 for the full reasoning on each decision.

---

## The 15 concepts

### Stage 1 — What initiates reasoning

#### 1. Genuine Curiosity
The reasoner is drawn toward understanding for its own sake, not toward confirming a prior belief or reaching a quick answer. Informed by the Need for Cognition construct (Cacioppo & Petty, 1982), which treats curiosity, openness-to-ideas, epistemic curiosity, and intellectual engagement as a single latent factor — so this concept deliberately covers that whole space rather than attempting to split it.

Sub-facets:
- Asking questions to understand rather than to confirm
- Following unexpected observations rather than dismissing them as noise
- Interest in *why* something is true, not just *that* it is true
- Taking evident pleasure in the cognitive work itself, not only in reaching an answer (drawn from the NFC effort-enjoyment dimension)

#### 2. Hypothesis Generation
The reasoner produces a space of possibilities before committing to one. The contrast is fixation — locking onto a single explanation and reasoning only within it.

Sub-facets:
- Producing multiple competing explanations rather than fixating on one
- Considering edge cases and boundary conditions
- Explicitly asking "what else could explain this?"

### Stage 2 — How you process evidence

#### 3. Logical Rigor
*(Absorbs first-principles thinking.)* Inferential chains are valid, assumptions are surfaced, and the reasoner checks whether conclusions actually follow from premises rather than from plausibility.

Sub-facets:
- Valid inferential chains where each step follows from the previous
- Decomposing complex claims into foundational assumptions
- Identifying hidden premises and checking whether conclusions actually follow

#### 4. Causal Reasoning
The reasoner distinguishes causation from mere association and actively considers alternative causal structures.

Sub-facets:
- Distinguishing correlation from causation
- Considering confounders and alternative causal paths
- Recognizing selection bias, survivorship bias, and base rate neglect

#### 5. Quantitative Groundedness
The reasoner treats numbers as load-bearing and checks them, rather than letting qualitative intuitions carry the argument.

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
The reasoner actively counteracts the natural pull toward evidence that supports their hypothesis. The psychology literature decomposes confirmation bias into three behavioral components — information search, evidence weighing, and memory retrieval — and the sub-facets below follow that structure for the two components that transfer to our extraction-from-text setup (memory is not relevant when we are looking at a single passage).

Sub-facets:
- Information search — actively seeking disconfirming evidence rather than only evidence that supports the hypothesis
- Evidence weighing — subjecting one's preferred hypothesis to the same critical scrutiny as competing ones; resisting the tendency to accept confirming evidence too readily and reject disconfirming evidence too harshly ("disconfirmation bias")
- Noticing selective processing — catching oneself in the act of asymmetric evaluation and correcting for it

#### 8. Metacognitive Awareness
The reasoner monitors their own cognitive process as it happens, commenting on what is pulling them toward which conclusions and why.

Sub-facets (focused on the *monitoring/sensitivity* dimension, deliberately kept separate from Calibrated Confidence's *bias* dimension per F10):
- Explicitly monitoring own reasoning process as it happens ("I notice I just jumped from A to C without checking B")
- Distinguishing "I'm drawn to this conclusion" from "the evidence supports this conclusion"
- Flagging when a conclusion feels forced versus when it feels well-supported, independent of how confident the final claim ends up being

### Stage 4 — How you hold conclusions

#### 9. Calibrated Confidence
The strength of the reasoner's claims matches the strength of the underlying evidence. Strong evidence → strong claim; weak evidence → tentative claim; no hedge-word inflation in either direction.

Sub-facets:
- Matching certainty of language to strength of evidence
- Explicit probability thinking where appropriate
- Distinguishing "I know" from "I believe" from "I suspect"

#### 10. Intellectual Honesty
The reasoner faithfully represents what the evidence shows, including inconvenient results. Distinct from humility: one can be highly confident and still scrupulously honest.

Sub-facets:
- Faithfully representing what evidence shows, even when inconvenient
- Not cherry-picking, not inflating effect sizes, not dropping inconvenient results
- Acknowledging when results don't support the preferred interpretation

#### 11. Comfort with Ambiguity
The reasoner can sit with unresolved questions without forcing premature closure.

Sub-facets:
- Holding unresolved questions open rather than forcing a conclusion
- Holding multiple plausible interpretations simultaneously
- Resisting the urge to pick a side when evidence is genuinely balanced

### Stage 5 — How you engage with others' reasoning

#### 12. Steelmanning
Before critiquing an opposing position, the reasoner constructs its strongest form rather than attacking its weakest.

Sub-facets:
- Constructing the strongest version of an opposing argument before engaging
- Distinguishing weak versions of a position from its best formulation

#### 13. Authority Independence
The reasoner evaluates claims on the evidence behind them rather than on the prestige of their source, and is willing to reach and hold conclusions that disagree with established figures when the evidence warrants. The emphasis is on the *evaluation* step — how one decides what to believe — with the implicit commitment that one follows one's honest evaluation regardless of the social comfort of the conclusion.

Sub-facets:
- Evaluating claims on evidence rather than source prestige
- Distinguishing evidence-based consensus from appeal to authority
- Treating expert disagreement as information rather than as a cue to defer to the higher-status expert
- Willingness to reach and state conclusions that disagree with established figures when evidence warrants

### Stage 6 — How you communicate knowledge

#### 14. Reasoning Transparency
The reasoner shows their work. Steps, assumptions, and weak points in the chain are all surfaced rather than hidden behind a polished conclusion.

Sub-facets:
- Showing the steps, not just the conclusion
- Making assumptions explicit
- Flagging where the reasoning chain is weakest

#### 15. Evidence Grounding
Claims are tied to specific observations or data, and the type of evidence is made clear.

Sub-facets:
- Tying claims to specific observations or data
- Distinguishing empirical claims from theoretical speculation
- Specifying type of evidence (anecdotal, observational, experimental, meta-analytic)

---

## Corpus budget implications

With 15 concepts and a target of 15–30 contrastive pairs per concept spanning multiple domains and sub-facets, the total corpus size will land somewhere between 225 and 450 triplets (neutral baseline + virtuous + non-virtuous). Domain balance quotas and sub-facet balance quotas will be specified in `generation-guidelines.md`.
