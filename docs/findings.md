# Phronesis — Research Findings & Deferred Considerations

A running log of useful insights we encounter during planning and prior-work review that don't belong in the current phase's working documents but will matter later. Each entry records the finding, where it came from, and which future phase it should inform.

The purpose of this file is to prevent good ideas from being lost to context window turnover. Do not put active plan decisions here — those go in the relevant phase document. Put things here that are *correct now but not yet actionable*.

---

## F1 — Token-averaged extraction, skipping the first ~50 tokens of each passage

**Source:** Anthropic, "Emotion Concepts and their Function in a Large Language Model" (2026). Extraction methodology.

**The finding:** Anthropic extracted residual stream activations at each layer by **averaging across all token positions within each story, beginning from the 50th token onward.** They did not extract at a single token, and they did not average over the entire passage from token 0. The early tokens (the opening of each story) were excluded from the average.

**Why the 50-token skip matters:** The opening of a generated passage is dominated by topic and setup — "A researcher was studying fruit flies when she noticed that..." — which encodes subject matter, not the target concept. Averaging over these early tokens would dilute the concept signal with topic noise. By the 50th token, the passage is in the middle of actually expressing the disposition (or emotion), so the average represents the concept more purely. This is a clean methodological trick we should steal directly.

**Important separate note on validation extraction:** For their *validation* step (held-out prompts with implicit emotional content), they measured activations at a single token — the `:` following `Assistant` — just before the model's response. So the methodology is: **token-averaged extraction during training, single-token measurement during validation.** Different phases use different positions.

**Applies to:** Phase 3 or 4 extraction pipeline design. When we build the activation hooks for Gemma 4 E4B:
- For *training extraction*: average residual stream activations across passage tokens, starting from a skip offset roughly proportional to what Anthropic used. Our passages target 200–400 tokens vs. their longer stories, so a 50-token skip may be too aggressive for us; a proportional skip of ~25% of passage length (so 50–100 tokens skipped) is a reasonable starting point. Tune empirically.
- For *validation measurement*: pick a single "summary" position in Gemma 4's chat template, likely the token immediately before the assistant turn begins, and measure there.

**Open questions:**
- What is the right skip offset for our shorter passages? Candidates: fixed 50 tokens, proportional (e.g. first 25% skipped), or content-based (skip until the reasoning actually begins, detected programmatically).
- Is the single-token validation measurement strictly necessary, or can we validate with token-averaged measurements too? Anthropic's choice was likely driven by their chat-template setup; Gemma 4's may differ.

**Correction note:** An earlier version of this finding stated that extraction was single-token only. That was wrong — I conflated the extraction and validation phases. Corrected after deeper research.

---

## F2 — Hold out ~20% of fact packs as a validation set

**Source:** Anthropic emotions paper, validation methodology.

**The finding:** Anthropic validated their extracted emotion vectors by running a *held-out* set of prompts whose emotional content was implicit (not explicitly labeled) and checking whether their vectors activated on the expected prompts. Positive-event prompts lit up the "happy" vector, loss/threat prompts lit up "sad" and "afraid" vectors.

**Why this matters for us:** We need the same discipline. If we extract our vectors from the same data we validate on, we have no real test of whether the vectors generalize beyond the specific passages that trained them. Reserving a portion of our corpus that never touches extraction gives us an honest generalization check.

**Applies to:** Phase 3 (corpus assembly) and Phase 4 (extraction and validation). When we finalize the corpus, mark ~20% of triplets per concept as held-out. Never use them for difference-of-means extraction; only use them to check whether the extracted vector activates more strongly on the virtuous held-out passages than on the non-virtuous ones.

**Open question:** Whether the held-out set should be randomly sampled from the full corpus, or deliberately drawn from domains and sub-facets that are intentionally *under*-represented in the training portion (to test out-of-distribution generalization). The second is a stronger test. Revisit when we have the full corpus assembled.

---

## F3 — Contrastive-triplet vs. independent-pool is an empirical question, not a settled one

**Source:** Comparison of Anthropic's emotions methodology against our planned contrastive-triplet design.

**The finding:** Anthropic did not use contrastive pairs at all. They generated ~1,200 independent stories per emotion and relied on cross-emotion difference-of-means at the aggregate level. Our plan uses contrastive triplets at much smaller scale (~30 per concept). We've argued the contrastive approach is better for our setting because epistemic virtues produce quieter signals than emotions and need tighter matched pairs to surface against topic noise — but this argument is *theoretical*. We haven't tested it.

**Why this matters for us:** Picking the wrong corpus design wastes the most expensive part of the project (generation and review work). If independent-pool actually works better for virtues at our scale, we'd rather know before committing to 450 hand-reviewed triplets.

**Applies to:** Phase 4 or a dedicated pilot phase before full corpus generation. Once we have one concept's pipeline working end-to-end, run a small bake-off: for that one concept, generate (a) 30 contrastive triplets and (b) ~60 independent passages (30 virtuous, 30 non-virtuous) — roughly matched total generation effort. Extract vectors both ways. Compare on the held-out validation set.

**Important caveat:** This pilot is only worth running if both methods are cheap enough at the 1-concept scale that the comparison is not itself a major project. If the contrastive pipeline is already working and producing clean vectors, we may choose to skip the bake-off and ship. If the bake-off is run and the contrastive approach wins, the result dictates scaling strategy for the remaining 15 concepts (since one will have been pilot-tested).

---

## F4 — Anthropic's scale provides a benchmark for domain diversity, not for corpus size

**Source:** Anthropic emotions paper — 100 topics × 12 stories per topic per emotion.

**The finding:** Anthropic used 100 distinct topics per emotion. The topic diversity was much larger than we can reasonably match (we're planning ~8 domains with multiple scenarios each). But the number of stories *within* each topic was only 12, which is comparable to what we'd generate per domain.

**Why this matters for us:** This reframes how to think about our corpus budget. We cannot match their *breadth* at small scale, but we can match the *depth-per-topic* and prioritize spreading our topics as wide as possible within our budget. A corpus of 30 triplets spanning 10 domains (3 triplets per domain) is strictly better than 30 triplets spanning 3 domains (10 triplets per domain), even though both have 30 triplets, because the former has less topic concentration and the resulting vector will generalize better.

**Applies to:** Phase 3 generation-guidelines.md domain quota design. The constraint to encode: minimize per-domain concentration subject to hitting minimum triplet counts per sub-facet. Rough target: no single domain should account for more than ~20–25% of a concept's triplets.

---

## F5 — Untrusted-content injection is a real problem we'll hit during fact-pack curation

**Source:** Direct observation while fetching Anthropic's skill-creator documentation in Phase 2 — the fetched content contained a system-style reminder attempting to influence behavior.

**The finding:** Any external content we pull into the project (skill files, paper text, web-scraped scientific scenarios for fact packs) is untrusted and may contain injected instructions. This is especially relevant later when we curate real scientific scenarios from papers, blog posts, or textbooks to build fact packs — those sources may contain text that looks like instructions to the generator model and can leak into the synthetic passages.

**Why this matters for us:** Fact pack curation needs a sanitization step. When we pull raw scenario material from an external source, we should strip anything that reads like an instruction, prompt, or directive before feeding it to the generator. Otherwise we risk contaminating the corpus with artifacts that have nothing to do with epistemic virtues.

**Applies to:** Phase 3 generation-guidelines.md — the fact pack construction section should include an explicit sanitization step. Also applies to the review rubric: one of the automatic rejection criteria for a generated passage should be "contains content that appears to be instruction-like rather than reasoning-like."

---

## F6 — Neutral-baseline subtraction is Anthropic's approach too

**Source:** Anthropic emotions paper methodology. They "extracted the directions in activation space associated with each emotion while subtracting out neutral confounds."

**The finding:** Anthropic did not simply take the mean activation of all emotion-X stories as their "emotion-X vector." They subtracted a neutral baseline to isolate the emotion-specific component. This is effectively the same as our neutral-ancestor triplet design: neutral passages define the zero point, and the virtue vector is the displacement from neutral toward the virtuous pole.

**Why this matters for us:** Convergent validation of our triplet design. The reason we're generating a neutral baseline before the virtuous and non-virtuous rewrites is not just methodological neatness — it directly parallels what Anthropic did, and it's what makes the resulting vector represent "the concept" rather than "the concept plus whatever topic content happened to correlate with the labeled set." Keep the neutral-first-then-two-rewrites pipeline as designed.

**Applies to:** Confirms the Phase 3 generation pipeline. No action needed, but this is a meaningful reassurance when we write generation-guidelines.md that the design choice isn't arbitrary.

---

## F7 — Effect size in steering should correlate with probe quality

**Source:** Anthropic emotions paper. "Steering with the 'blissful' vector produced a mean Elo increase of 212, while steering with the 'hostile' vector produced a mean Elo decrease of -303, with the size of the steering effect proportional to the correlation of the emotion probe with the Elo score (r=0.85)."

**The finding:** Anthropic validated their vectors by (a) training a probe to predict a downstream outcome (preference Elo) from the vector's activation and (b) measuring whether steering along the vector actually moved that outcome. The two quantities — probe correlation and steering effect — correlated at r=0.85. In plain terms: *the vectors that best predicted an outcome also best controlled it.*

**Why this matters for us:** This is a validation pattern we should adopt directly. For each virtue vector we extract, we can:
1. Train a linear probe to predict some downstream behavior from the vector (e.g., whether a reasoning trace contains hedged uncertainty language for the humility vector).
2. Steer along the vector during generation.
3. Check whether steering changes the same behavior the probe predicts.
4. Report the correlation between probe-predictive power and steering effect magnitude.

If our virtue vectors show the same probe↔steering correlation pattern that Anthropic's emotion vectors did, that's strong evidence the vectors are capturing real, causal representations rather than spurious correlates. If the correlation is weak, that tells us either the probes are measuring the wrong thing, the vectors are measuring the wrong thing, or the virtue isn't mechanistically implemented the way we thought.

**Applies to:** Phase 4 validation design. When we define success criteria for a virtue vector, "probe correlation ≈ steering effect magnitude" should be one of them. Record this as a validation metric before we run experiments, so we don't cherry-pick post-hoc.

---

## F8 — Anthropic explicitly signals that this methodology generalizes beyond emotions

**Source:** Anthropic emotions paper closing remarks. "Similar methodology could be used to extract many other kinds of concepts aside from emotions, and does not intend to suggest that emotion concepts have unique status or greater representational strength than non-emotional concepts."

**The finding:** The paper explicitly invites exactly the kind of extension we're doing. Anthropic is not claiming emotions are a special case — they're claiming this is a general methodology for extracting representations of abstract concepts from a language model, and emotions were just their first target.

**Why this matters for us:** Two things. First, this is a useful citation when we eventually write up our results — we can position Phronesis as a direct answer to an open question the paper raised, not as a speculative extension. Second, and more practically, it suggests Anthropic's team has already thought about (and likely discussed internally) applications to non-affective concepts. If they ever publish follow-up work on extracting non-emotion concepts, that becomes the most important prior work for us to read, more so than the original emotions paper.

**Applies to:** Paper writeup (eventually) and ongoing literature monitoring. Watch transformer-circuits.pub for follow-up posts applying this methodology to reasoning, cognition, or other non-affective concept families.

---

## F9 — Psychology has validated scales for most of our 16 concepts; their sub-dimensions differ meaningfully from ours

**Source:** Behavioral science literature search on intellectual humility, metacognition, confirmation bias, and virtue epistemology.

**Status:** Partially resolved. The Intellectual Courage addition, the Intellectual Humility ego-independence sub-facet, and the Confirmation Bias Awareness three-component restructuring have all been integrated into concepts.md. The remaining value of this entry is as a record of the decision process and a reminder that concepts.md is informed by validated psychological instruments, not just by our intuitions.

**The finding:** Several of our 16 concepts correspond to constructs with decades of empirical psychology research and validated measurement instruments. The most important:

- **Comprehensive Intellectual Humility Scale (CIHS), Krumrei-Mancuso & Rouse 2016.** A 22-item validated instrument that decomposes intellectual humility into *four* sub-dimensions: (1) independence of intellect and ego, (2) openness to revising one's viewpoint, (3) respect for others' viewpoints, (4) lack of intellectual overconfidence. Our current sub-facets for humility are data/methodology skepticism, generalizability caution, and willingness to update. These overlap with the CIHS "openness to revising" dimension but miss the ego-independence and others-respect dimensions entirely — we framed humility as purely epistemic/scientific, whereas the validated scale treats it as substantially social.

- **Virtuous Intellectual Character Scale (VICS), Baehr tradition.** Covers open-mindedness, fair-mindedness, inquisitiveness, intellectual courage, rigor, carefulness. The striking missing concept in our list is **intellectual courage** — the willingness to defend well-supported conclusions against social or authority pressure. This is distinct from our "Authority Independence" because Authority Independence is about *evaluating* claims on evidence, while intellectual courage is about *acting on* one's conclusions despite pushback. Worth considering as an addition.

- **Confirmation bias literature** operationalizes the construct across three components: (1) information search (which evidence you look for), (2) evidence weighing (how critically you evaluate confirming vs. disconfirming evidence — "disconfirmation bias"), and (3) memory recall (which evidence you retain). Our current sub-facets map to components 1 and 2 but not 3. Memory recall is likely irrelevant for our extraction-from-text setup, so this is a defensible gap.

**Why this matters for us:** The psychology literature represents decades of careful thought about what behaviors these constructs correspond to in practice. Our sub-facets are essentially a one-pass best guess; theirs are empirically validated. We should not wholesale adopt their sub-dimensions (they were designed for self-report questionnaires, not for extraction from reasoning monologues), but we should cross-check each of our concepts against the nearest psychological construct and ask: "what are they measuring that we're not, and is that gap defensible?"

**Applies to:** Phase 1 revisit — specifically, a review pass over concepts.md to check each concept against its nearest validated scale and decide whether to refine sub-facets. This is a meaningful amount of work and should happen before we commit to generation. It is *not* automatic; many psychological sub-dimensions are measurement artifacts of self-report and won't transfer to text extraction. But the check should happen.

**Candidate refinements the literature suggested (now resolved, see concepts.md):**
- Intellectual Humility — *Resolved.* Ego-independence sub-facet added as the fourth sub-facet, and the sub-facet cap was raised from 3 to 4 to accommodate it.
- Intellectual Courage — *Resolved, then reversed.* Briefly added as Concept 14 in Stage 5, then cut after F18 surfaced weaker empirical backing than initially assumed. The "willingness to reach conclusions that disagree with authority" intuition is now partially absorbed into Authority Independence's fourth sub-facet. See F18 for the full reasoning.
- Confirmation Bias Awareness — *Resolved.* Sub-facets restructured around the information-search / evidence-weighing / noticing-selective-processing three-component model.

---

## F10 — Metacognition research decomposes into sensitivity, bias, and efficiency — validating our Concept 8 / Concept 9 separation

**Source:** Metacognition measurement literature (Fleming, Lau and related work on type-2 signal detection).

**The finding:** Psychology decomposes metacognitive ability into three distinct quantities:

1. **Metacognitive sensitivity** — how well a person distinguishes their own correct judgments from their incorrect ones. High sensitivity = "when I'm wrong, I usually feel less confident."
2. **Metacognitive bias** — systematic over- or underconfidence, independent of sensitivity. A person can be highly sensitive (tracking their own errors well) but biased (always too confident on average).
3. **Metacognitive efficiency** — sensitivity normalized by task difficulty, so it measures pure metacognitive skill independent of how hard the task itself is.

**Why this matters for us:** Our Concept 8 (Metacognitive Awareness) and Concept 9 (Calibrated Confidence) looked potentially collinear — both are about "being aware of your own uncertainty." But the sensitivity/bias distinction in the psychology literature tells us these are empirically and conceptually separable, and they should be separate concepts in our taxonomy too. Metacognitive Awareness = sensitivity (tracking one's own reasoning process); Calibrated Confidence = low bias (matching confidence to evidence). A reasoner can have high sensitivity without low bias (they notice when they're less sure, but their baseline confidence is still miscalibrated) or vice versa. This is a direct validation that keeping them as separate concepts is the right call — not just something we argued for intuitively.

**Applies to:** Confirms the Phase 1 taxonomy on a specific decision we were uncertain about. No action needed beyond recording this as justification. If we ever reconsider merging 8 and 9, the psychology literature says don't.

**Additional implication for sub-facets:** Our Metacognitive Awareness sub-facets should emphasize the *monitoring* aspect (tracking which conclusions feel forced vs. supported) rather than accidentally drifting into calibration territory (how confident to be). Worth a sharpening pass when we revisit concepts.md.

---

## F11 — Activation steering cannot create competencies the model lacks; it can only amplify what's already there

**Source:** Representation engineering survey literature; Contrastive Activation Addition (CAA) follow-up work.

**The finding:** Direct quote from the literature: *"ActAdd cannot create new competencies or enforce abstract constraints, it can only amplify or suppress what is already there."* And separately: *"if a behavior is not cleanly represented in this way, if it requires multi-step reasoning, planning, or interaction with long-term context then no amount of activation shifting will reliably produce it."*

**Why this matters for us:** This is the central theoretical risk to the entire Phronesis project, and I want to state it plainly. If Gemma 4 E4B does not already have a meaningful internal representation of a given virtue — say, "ego independence" or "intellectual courage" — then no contrastive dataset, no matter how well-designed, will extract a working vector for it. The small-model training corpus may simply not have included enough examples of careful epistemic reasoning for the model to have developed clean representations of the subtler virtues. We cannot test this a priori; we will only find out empirically when we try to extract and validate.

**Implication for concept prioritization:** The 16 concepts are not equally likely to work. They sit on a rough spectrum from "almost certainly represented in any competent small model" to "probably only clearly represented in larger models trained on scientific reasoning." A defensible ordering, from highest to lowest likelihood of success, with one-line reasoning for each placement:

**Highest likelihood — concrete, clear textual markers, studied under nearby names in the activation-steering literature:**
- *Calibrated Confidence* — maps directly onto "truthfulness" and "uncertainty" vectors that CAA/ActAdd work has already successfully extracted in other models.
- *Reasoning Transparency* — shows up in text as explicit stepwise markers ("first... then... therefore..."), which are easy for any model to tokenize and represent.
- *Evidence Grounding* — closely related to citation and attribution behaviors models are explicitly trained on via RLHF feedback.
- *Hypothesis Generation* — productive-divergent behavior has clear lexical signatures ("one possibility is... alternatively... or it could be...").

**Medium likelihood — well-represented in training data but with more distributed textual signatures:**
- *Intellectual Humility* (all four sub-facets treated as a unit) — widely discussed in both scientific writing and casual text, though the ego-independence sub-facet is expected to be the weakest component and should be validated separately during extraction.
- *Confirmation Bias Awareness* — discussed extensively in popular-science and methodology writing; the textual signature (explicit mention of alternative evidence) is detectable.
- *Quantitative Groundedness* — clear markers (numbers, sample sizes, error bars) but requires the model to integrate multiple pieces of information.
- *Causal Reasoning* — philosophically complex but has been the focus of significant LLM evaluation work, suggesting models do represent it.
- *Logical Rigor* — subtle but present in any training corpus with mathematical or philosophical writing.

**Lower likelihood — more abstract, more dependent on training data quality:**
- *Metacognitive Awareness* — the self-monitoring signature is subtle and may be conflated with surface-level hedging.
- *Steelmanning* — requires the model to represent an argument from both sides simultaneously, which is a multi-step behavior.
- *Comfort with Ambiguity* — an *absence* behavior (not forcing closure), and absences are harder to extract than presences.
- *Genuine Curiosity* — easily confused with stylistic enthusiasm; likely entangled with conversational tone.
- *Authority Independence* — requires representing both a claim and its source status as separable.
- *Intellectual Honesty* — the textual signature (acknowledging inconvenient results) is similar enough to humility that the two may not separate cleanly. **Updated:** Literature explicitly calls out honesty as a concept that is harder to extract at small scale — see F14. Consider moving to Lowest tier if pilot results confirm.

**Note on the removed "Lowest likelihood" tier.** This tier previously contained Intellectual Courage. After F18 led to Intellectual Courage being cut from the taxonomy, the Lowest tier became empty. The 15 remaining concepts now fit into the Highest / Medium / Lower tiers. The fact that our most-likely-to-fail concept was also the most-empirically-shaky one is a small data point in favor of the honesty of the tier ordering: empirical weakness and extraction difficulty track together.

**Note on Intellectual Humility's ego-independence sub-facet.** Humility as a whole is placed in the Medium tier, but its ego-independence sub-facet is the most abstract of its four sub-facets and may extract less cleanly than the others. When we run extraction on humility, we should validate not just whether the overall vector works but whether the ego-independence sub-facet contributes usefully or degrades the vector.

**Applies to:** The sequencing of Phase 4 extraction experiments. Start with a high-likelihood concept (strong candidate: Calibrated Confidence, because it has clear textual markers and is well-studied in the activation-steering literature under nearby names like "truthfulness" and "uncertainty"). Use the result as a signal: if we cannot extract a clean Calibrated Confidence vector, the entire approach is not viable at Gemma 4 E4B scale and we should either move to a larger model or reconsider the project. If Calibrated Confidence works, we have a green light to try harder concepts, and we have a baseline extraction pipeline to compare against.

**This also affects the corpus generation priority.** We should generate corpus for the high-likelihood concepts first. If the extraction pipeline fails on those, we save ourselves from having generated corpus for the harder concepts that would also have failed.

---

## F12 — Steering has three practical failure modes we need to plan validation around

**Source:** Representation engineering and contrastive activation addition literature.

**The finding:** Three distinct, empirically well-documented failure modes of representation-based steering, each requiring its own validation check:

1. **Coefficient fragility.** The scaling coefficient that controls steering strength has *no principled way to choose it ahead of time, and the acceptable range can be very narrow.* Too small and the steering has no effect; too large and model capabilities degrade (the model starts producing gibberish or incoherent reasoning). Finding the acceptable range is an empirical search, and the range may be different for each concept vector.

2. **Concept specificity failure / cross-concept interference.** *"Concept vectors might not be specific: steering with a vector for one concept might also steer other concepts as a side effect."* This is a first-order problem for Phronesis specifically, because our 16 concepts are not orthogonal — they are clustered by reasoning stage and share cognitive machinery. Steering "intellectual humility" might inadvertently move "confirmation bias awareness" or "calibrated confidence." If we don't measure this, we'll over-claim what a given vector does.

3. **Out-of-distribution transfer failure.** *"Operators found in one distribution may not transfer to out-of-domain settings."* A vector extracted from scientific-reasoning passages may not steer the model on, say, ethical reasoning or everyday decision-making. This is expected and probably fine for our purposes (we're specifically interested in scientific virtues), but we should be explicit about the scope when reporting results.

**Why this matters for us:** Each failure mode implies a concrete validation step that needs to be part of the Phase 4 experimental protocol before we can claim a virtue vector "works":

- **For coefficient fragility:** Sweep a range of scaling coefficients for each vector. Record the operating window where steering is detectable but doesn't degrade model fluency. Report the range, not just a single "it works" number.
- **For specificity:** For each extracted virtue vector, measure not just whether it steers the target virtue but whether it also moves the *other 15 virtues*. The ideal vector is one where on-target steering is large and off-target steering is small. This gives us a specificity matrix — essentially a confusion matrix for steering — which is itself an interesting experimental result.
- **For OOD transfer:** Hold out at least one domain entirely from the extraction corpus, and validate on that domain. If a vector extracted from physics/biology/economics passages also steers on held-out engineering or medical passages, that's evidence of generalization.

**Applies to:** Phase 4 experimental protocol design. These three validation steps should be specified up front, before extraction begins, so we don't design a protocol that accidentally selects for positive results.

**Methodological note, possible finding:** The specificity matrix (concept-by-concept steering effects) is itself a *publishable result* even if the concepts turn out to be partially collinear. A clean finding of the form "virtues cluster into two orthogonal groups at the vector level" would be genuinely informative about how the model represents these concepts and would validate or refute our stage-based taxonomy.

---

## F13 — Layer selection: extract from the middle third of the model

**Source:** Contrastive Activation Addition (CAA) literature and representation engineering follow-up work. Reported protocols: layers 10–15 for Qwen 2.5-7B, layers 6–18 for GPT-2-XL.

**The finding:** Activation steering literature consistently finds that *middle layers* are the most effective extraction point for semantic concept vectors. Early layers are too close to token space — they encode surface features of the input before semantic integration has happened. Late layers are too close to output space — they encode what the model is about to say, not what it understands. Middle layers sit at the point of maximum semantic abstraction.

Additionally, the literature reports that within the middle-to-late region, representations for abstract concepts tend to *converge* — once the model has extracted the high-level information needed to represent the concept, the representation stays relatively stable across subsequent layers. This means we have some flexibility in exactly which middle layer we extract from, and we can compare several nearby layers to confirm the vector is stable rather than being an artifact of a specific layer.

**Why this matters for us:** Gemma 4 E4B's architecture determines the exact layer range, but the rule of thumb is clear: target roughly the middle third of the model's transformer layers. We will need to look up Gemma 4 E4B's layer count and compute the range once we start building the extraction pipeline. If E4B has, say, 32 layers, the starting extraction range would be layers ~10–22.

**Concrete protocol implication:** For each concept, extract at several candidate layers across the middle third, not just one. Report the layer at which the vector performs best on validation and the stability of performance across nearby layers. A vector that works at layer 14 but not layer 13 or 15 is suspicious; one that works from layer 12 through 18 is a much cleaner signal.

**Applies to:** Phase 4 extraction pipeline design. This replaces the ambiguity in our earlier thinking about "which layer to extract from" with a concrete starting rule.

---

## F14 — The honesty/truthfulness concept specifically has been documented as hard to extract at small scale

**Source:** Representation engineering / activation steering literature on honesty vectors. Direct quote: *"It was harder to get smaller models to differentiate along the dimension of interest using contrastive prompts, and a certain amount of size/intelligence is necessary to represent a high-level concept like 'Honesty'."*

**The finding:** This is specific, named evidence that our Intellectual Honesty concept sits right on the edge of what a small model can represent. The literature is not saying that small models cannot represent honesty at all — state-of-the-art CAA work has succeeded on models down to Pythia-1.4B and Qwen 2.5-3B — but it is saying that honesty specifically is one of the concepts where the small-model/large-model gap is most visible.

**Why this matters for us:** Three things.

1. **F11's tier placement for Intellectual Honesty was too optimistic.** It's currently in "Lower likelihood." The honest placement based on this evidence is that it should be in the same tier as Intellectual Courage — at or near the bottom of our extraction-likelihood ordering. We should attempt it later in the extraction sequence, after easier concepts have confirmed the pipeline works.

2. **The word "honesty" in the literature is ambiguous between two things** — *factual* honesty (not lying about the world) and *intellectual* honesty (faithfully representing what evidence shows, including inconvenient results). Our Concept 10 is closer to the second. It is possible that the literature's reported difficulties apply more to the factual sense than the intellectual sense, but it is also possible the distinction does not matter at the activation level. We will not know until we try.

3. **This is the first concrete evidence we have that a specific one of our concepts may fail.** F11 warned of the general risk; F14 names a specific concept where the risk has been empirically observed. This raises the value of running the pilot on a different, easier concept first and explicitly planning for the possibility that Intellectual Honesty doesn't extract cleanly.

**Applies to:** F11 tier ordering (already updated); Phase 4 experimental sequencing (attempt easier concepts first); and the writeup — if Intellectual Honesty does fail to extract at Gemma 4 E4B scale, that is itself a meaningful negative result consistent with prior literature, not a failure of our methodology.

---

## F15 — The MASK benchmark separates honesty from knowledge; directly relevant to our correctness confound

**Source:** 2025 paper on depth-wise activation steering for honest language models, which uses the MASK benchmark.

**The finding:** The MASK benchmark is specifically designed to separate honesty from knowledge. A model can produce a factually wrong answer honestly (by accurately reporting its limited knowledge) or a factually correct answer dishonestly (by giving the right answer while its internal representation leans toward a different one). MASK evaluates models on this distinction rather than on raw factual accuracy.

**Why this matters for us:** This is a direct answer to one of our earlier concerns — the "correctness confound" noted in concepts.md. We were worried that a virtuous reasoner might also be a more correct reasoner, causing our virtue vectors to partly encode "being right" rather than the virtue itself. Our planned mitigation was to include ~20–30% of virtuous passages where the reasoner reaches an incorrect conclusion. MASK provides an *external* validation instrument for the same distinction, which we can use during Phase 4 validation without having to engineer the confound-breaking entirely through corpus design.

**Concrete implications:**

1. If we successfully extract an Intellectual Honesty vector, MASK is the obvious validation benchmark. We would steer along the vector and measure whether MASK honesty scores change independently of MASK knowledge scores. A clean result would show honesty scores moving while knowledge scores remain flat.

2. More broadly, the existence of MASK confirms that the field has already validated the distinction we care about (honesty separable from correctness). This is convergent evidence that our concern was legitimate and that researchers have thought about it carefully.

3. For other virtue vectors (not just Intellectual Honesty), MASK gives us a model for how to design validation — find or build a benchmark that separates the target disposition from confounded dimensions, and measure whether steering moves the disposition while leaving the confound unchanged.

**Applies to:** Phase 4 validation design for Intellectual Honesty specifically, and as a template for how to design validation instruments for the other concepts.

**Open question:** Is MASK publicly available, and does it run on small open models? Need to confirm before committing to it as a validation benchmark. If it only runs on large proprietary models, we need to find an analog or build one.

---

## F16 — Protocol detail: steering vectors are added at all token positions after the user's prompt

**Source:** CAA (Contrastive Activation Addition) literature.

**The finding:** During inference-time steering, the extracted vector is added to the residual stream at *every* token position *after* the user's prompt — not at a single token, and not at the prompt itself. This is how steering biases the model's generation across the entire response.

**Why this matters for us:** Small protocol detail, but load-bearing for Phase 4 implementation. When we write the steering hook for Gemma 4 E4B, we need to apply the addition at every assistant-turn token, not just the first. Misimplementing this (e.g., adding only at the first generated token) is a common source of steering failure in ad-hoc implementations.

**Applies to:** Phase 4 code design for the steering hook. Minor but worth recording so we don't reinvent it.

---

## F17 — Genuine Curiosity maps cleanly onto the validated Need for Cognition construct

**Source:** Cacioppo & Petty (1982), Need for Cognition Scale. Replicated and refined across 40+ years of research.

**The finding:** Our Concept 1 (Genuine Curiosity) corresponds closely to the well-validated psychological construct Need for Cognition (NFC) — "the tendency to engage in and enjoy effortful cognitive activity." NFC has an 18-item scale, a 6-item short form, strong validity and reliability, and is empirically near-identical to three other constructs (typical intellectual engagement, epistemic curiosity, openness to ideas) — they all load onto a single latent factor.

**Why this matters for us:**

1. **Convergent validation.** Unlike Intellectual Courage (see F18), Genuine Curiosity is backed by a large, coherent, validated psychological construct. Our intuition that curiosity is a distinct epistemic virtue worth extracting is solidly supported.

2. **The factor-analysis result ("NFC, intellectual engagement, epistemic curiosity, and openness-to-ideas all load on one factor") tells us something specific about our taxonomy**: we should not attempt to separate curiosity, openness, and intellectual engagement into distinct concepts. If we had originally listed "curiosity" and "openness" as two separate entries, psychology would tell us to merge them. Our current list treats them as one (Genuine Curiosity), which is the right call.

3. **Sub-facet refinement opportunity.** The NFC sample items ("I find satisfaction in deliberating hard and for long hours," "The notion of thinking abstractly is appealing to me") suggest our sub-facets could be sharpened to include the *effort-enjoyment* dimension — taking pleasure in cognitive work, not just in its outcomes. Our current sub-facets are about question-orientation, which is half the story.

**Applies to:** Phase 1 concepts.md sharpening pass (minor) — possible addition of an effort-enjoyment sub-facet to Genuine Curiosity.

---

## F18 — Intellectual Courage has weaker empirical backing than we assumed; taxonomic decision needed

**Source:** Virtuous Intellectual Character Scale (VICS) dimensional analysis; Roberts & Wood's philosophical treatment; Baehr's focus on "courage to inquire."

**The finding:** When we added Intellectual Courage to concepts.md based on Baehr's virtue epistemology tradition, I implied it had stronger empirical support than it actually does. The deeper research reveals three concrete issues:

1. **VICS does not include Intellectual Courage as a separable dimension.** The validated scale for intellectual virtues identifies five dimensions: attentiveness, open-mindedness, curiosity, carefulness, and intellectual autonomy. Courage is *not* among them. Either the VICS authors judged it too hard to measure reliably, or they found it loaded onto other dimensions (most likely intellectual autonomy).

2. **Roberts and Wood frame courage as paired with caution**, not as a standalone virtue. In their treatment, courage prevents undue intimidation while caution prevents inappropriate risk-taking — they are two sides of a compound disposition, not a single trait. Our formulation treats courage alone, missing the caution side entirely.

3. **Baehr focuses on "courage to inquire" — the willingness to pursue threatening questions — rather than "courage to commit and defend conclusions."** Our concepts.md framing is about the commitment/defense step after a conclusion has been reached. This is closer to Roberts & Wood's conception but diverges from Baehr, even though we cited Baehr as the source. We were imprecise about which philosophical framing we were adopting.

**Why this matters for us:** Intellectual Courage as we currently have it in concepts.md is on weaker ground than the other 15 concepts. It may still be a legitimate concept to extract, but the justification we gave is inaccurate and the construct is less empirically anchored than we implied.

**Four possible resolutions, ordered from most aggressive to most conservative:**

A. **Remove Intellectual Courage.** Drop it from concepts.md, reverting to 15 concepts. Justification: neither VICS nor the philosophical literature gives us a single coherent, measurable construct to target. The risk we were trying to capture (courage to defend unpopular-but-correct conclusions) is also partially captured by Authority Independence, which has cleaner grounding.

B. **Reframe to match Baehr's "courage to inquire."** Redefine Concept 14 as the willingness to pursue intellectually threatening questions — questions whose answers might force uncomfortable revisions to one's beliefs. This moves the concept earlier in the reasoning stage structure (toward Stage 1 initiation) and aligns it with one specific philosophical tradition rather than blending two.

C. **Keep as currently defined but acknowledge the empirical gap.** Leave the current definition in place, add a prominent note that Intellectual Courage is the most speculative concept in our taxonomy, and flag it for possible removal if extraction fails. Essentially the same as (A) but deferred.

D. **Merge with Authority Independence** into a single "Intellectual Autonomy" concept with sub-facets covering evaluation (current Authority Independence), courage to inquire (Baehr's framing), and courage to defend (current Intellectual Courage framing). This matches the VICS approach, which collapses all three into one dimension.

**Why this matters for us holistically:** This is the kind of decision we explicitly agreed to catch through iterative research rounds — our first pass overclaimed what the empirical literature supports. Honest response is to present the options and let you decide, not to quietly fix it one way.

**My recommendation:** Option D (merge with Authority Independence). Reasoning: it aligns our taxonomy with the validated VICS structure, it captures all three aspects (evaluation, inquiry, commitment) without pretending they are fully separable at the representation level, and it reduces the total concept count by one, which is always a win for a tighter taxonomy. The main cost is losing some conceptual precision — but F11 already flagged that the most fine-grained distinctions are the least likely to extract cleanly at small scale, so the loss is expected to be minor in practice.

**Applies to:** Phase 1 concepts.md — required a decision before concepts.md could be called finalized.

**Resolution (recorded after the decision was made):** Option A was chosen. Intellectual Courage was removed from the taxonomy entirely, reverting the concept count to 15. The intuition behind "courage to reach and state conclusions that disagree with authority" was absorbed into Authority Independence as a fourth sub-facet. Rationale for this choice over the alternatives: (a) empirical backing was weakest of any concept we had added, (b) F11 had already placed it at the lowest extraction-likelihood tier, (c) cutting it honors our "atomic where possible" design principle better than the merge option, and (d) the taxonomy became simpler without losing meaningful ground since Authority Independence already partially captures the underlying intuition. This is a case where iterative research surfaced a genuine flaw in an earlier decision and the fix was to reverse the earlier decision, not patch over it.

---

## F19 — Text style transfer literature provides direct methodology for our contrastive twin generation step

**Source:** Text style transfer (TST) research in NLP, including CP-LM content preservation losses, minimal-edit approaches, and contrastive transfer pattern mining.

**The finding:** Our Stage 3 generation step — "rewrite this passage changing only the epistemic disposition, preserving topic, claims, structure, and length" — is structurally identical to the text style transfer problem that NLP has been working on for years. The field has developed several useful conventions:

1. **Explicit separation of content and style representations.** TST research consistently finds that unless the content and style are explicitly decoupled (through architectural choices, losses, or prompting), the rewriter will either change content to achieve the style change (bad for us) or fail to change the style at all (also bad). Our prompting strategy should explicitly enumerate what counts as "content" (claims, facts, reasoning steps, conclusion reached) versus "style" (disposition markers, hedging, confidence language).

2. **Content preservation is measured, not assumed.** The literature evaluates style-transferred text on two axes: style transfer success AND content preservation. A rewrite that successfully changes the style but loses 30% of the original meaning is a failure. This directly implies our review rubric needs to include *both* axes — does the rewrite capture the target disposition, AND does it preserve the scientific substance of the original?

3. **Minimal-edit approaches work better than paraphrase-level rewrites.** The TST literature finds that discrete editing strategies (changing specific words or phrases while leaving the rest intact) often preserve content better than generative rewrites that regenerate the whole passage. This argues for prompting our generator toward *surgical* edits rather than full rewrites. E.g., "change as few words as possible while achieving the disposition shift" rather than "rewrite the passage to be overconfident instead of humble."

4. **Parallel corpus scarcity is an acknowledged problem.** Most TST methods work around the lack of paired training data by constructing pseudo-parallel corpora — which is exactly what we are doing with our neutral-ancestor triplet design. We are not off-script; we are using a known workaround.

**Why this matters for us:**

1. The generation-guidelines.md document we will write in Phase 3 should borrow explicitly from TST vocabulary and techniques. Content-preservation loss concepts (what must stay the same) and style-transfer targets (what must change) give us a structured way to write the rewrite prompt.

2. The review rubric should measure *both* style capture and content preservation as separate scores, not a single "is this a good pair" judgment. If a pair scores high on style transfer but low on content preservation, it gets rejected; same in reverse.

3. "Minimal edit" becomes a concrete prompting principle: the rewrite prompt should explicitly tell the generator to change as few words as possible consistent with achieving the disposition shift.

**Applies to:** Phase 3 generation-guidelines.md and review-rubric.md. These design principles need to be encoded explicitly into the generation prompts and the evaluation criteria.

**Open question:** Should we borrow a specific existing TST prompting template or construct our own? Worth a brief look during Phase 3 writing — if there is a standard prompt structure that researchers have found works well for LLM-based style transfer, we should start from it rather than reinventing.

---

## How to add new findings

When adding a new finding to this file:

1. Assign the next `F<number>` identifier.
2. Include: source, the finding itself, why it matters, which future phase it applies to, and any open questions it raises.
3. Keep the entry self-contained — someone reading only this entry should understand the full context, because by the time we actually use the finding, the surrounding conversation will be long gone.
4. If a finding becomes actionable and gets moved into a working document, leave a note here pointing to where it ended up rather than deleting the entry.
