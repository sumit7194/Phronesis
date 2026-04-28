# Phronesis — Research Findings & Deferred Considerations

A running log of useful insights we encounter during planning and prior-work review that don't belong in the current phase's working documents but will matter later. Each entry records the finding, where it came from, and which future phase it should inform.

The purpose of this file is to prevent good ideas from being lost to context window turnover. Do not put active plan decisions here — those go in the relevant phase document. Put things here that are *correct now but not yet actionable*.

---

## Standing policy: Manual verification required for any benchmark-scored claim (2026-04-23)

**Rationale.** F96 first raised concerns about the abstention benchmark scorer's regex-based pattern matching. F97 and subsequent hand-scoring confirmed the problem quantitatively: 8.3% scorer-vs-human mismatch rate on Qwen; 5 false positives out of 24 on Gemma baseline. On 2026-04-23 we caught a factual confabulation in Gemma's fp-gandhi response (claiming Gandhi won Nobel Peace Prize in 1931 — he never did) that the auto-scorer had marked correct because the response contained abstention-marker phrases.

**What this means in practice.** Any behavioral claim from our benchmarks must be verified against the actual response text, not just the scorer verdict. The scorer is a useful first-pass filter; it is NOT a ground-truth arbiter.

**Standing requirements going forward:**

1. **Before reporting any benchmark score in a finding, experiment writeup, journal entry, or paper draft** — hand-read every item's response OR use an LLM-as-judge scorer with a calibrated prompt (e.g., AbstentionBench's Llama-3.1-8B judge with 88% validated accuracy).

2. **Any commit that introduces a behavioral claim (accuracy %, Δpp, etc.) must include a pointer to the human-verified data** — either a manual-scoring document or an LLM-judge reference. Raw auto-scorer outputs alone are not sufficient.

3. **Web-verify specific factual claims** that appear in our findings: dates, Nobel laureates, record holders, CEO positions, election outcomes. If the project makes a claim like "Gemma correctly identifies stale-data items," verify the claim by checking what Gemma actually said against external ground truth.

4. **For LLM responses on factual-recall items, verify the model's internal claim is correct, not just that the response contains an abstention marker.** The Gandhi-1931 error was caught by reading the full response; if we had stopped at the opening "this is a factual misunderstanding" token the error would have propagated.

5. **Pre-commit checks before any external sharing** (LinkedIn, paper draft, slides): re-verify all headline numbers, re-read the responses on any cherry-picked example, run a quick web check on any factual claim that names a specific person/date/value.

**Applies to:** all future phases. If this policy is skipped, commits with behavioral claims should be marked `(unverified — auto-scorer only)` in the commit message so they can be audited later.

See `mvp/results/manual_scoring_qwen_abstention.md` and the Gemma baseline-correction commit for examples of what manual verification looks like.

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

## F20 — Intolerance of Uncertainty is a two-factor construct; Comfort with Ambiguity may need the same split

**Source:** Carleton et al.'s Intolerance of Uncertainty Scale (IUS-12), the most widely validated instrument for the inverse of our Concept 11.

**The finding:** The IUS-12 decomposes intolerance of uncertainty into two distinct subscales:

1. **Prospective Anxiety** — worry and preoccupation about future uncertainty ("Unforeseen events upset me greatly").
2. **Inhibitory Anxiety** — uncertainty-induced paralysis where the person cannot act until more information is available ("When it's time to act, uncertainty paralyses me").

These two factors are empirically separable and have distinct behavioral signatures. A person can be high on one and low on the other — someone who worries about uncertainty but still acts despite it, or someone who is emotionally calm about uncertainty but freezes when asked to commit.

**Framing mismatch worth noting:** Carleton's scale was developed in a clinical/anxiety context and defines the construct in emotional-distress terms. Our Concept 11 (Comfort with Ambiguity) is framed in epistemic terms — willingness to hold unresolved questions open, resistance to forced closure. These overlap substantially but are not identical. The clinical literature is about *affective* responses to uncertainty; our concept is about *cognitive* responses to unresolved evidence. We should not wholesale adopt the IUS framing, but the two-factor structure is portable.

**Why this matters for us:** Our current sub-facets for Comfort with Ambiguity treat it as a unitary disposition with three behavioral expressions (holding questions open, holding multiple interpretations simultaneously, resisting picking a side when evidence is balanced). The IUS-12 structure suggests there may be a meaningful split between the *contemplative* dimension (holding questions open without distress) and the *actional* dimension (acting on a tentative conclusion without needing certainty first). These are different things — a reasoner can be comfortable sitting with open questions in pure thought while still being paralyzed when asked to commit to a course of action on the same evidence.

**Proposed concepts.md change (recorded here, not applied):** Consider refining Concept 11's sub-facets to reflect the contemplative/actional distinction:
- Holding unresolved questions open rather than forcing a conclusion (contemplative)
- Holding multiple plausible interpretations simultaneously (contemplative)
- Acting on tentative conclusions when forced to commit, without requiring certainty first (actional)

The third sub-facet is the one that would be new. It captures the "I don't know for sure but here's my best guess and I'll proceed with it" behavior that is meaningfully different from "I'm fine not knowing the answer."

**Open question:** Does the actional dimension extract from text at all? Our reasoning monologues are mostly contemplative by construction — they are someone thinking through a problem, not someone being forced to decide. If the actional dimension rarely shows up in our corpus, splitting it out may produce a vector that cannot be cleanly trained.

**Applies to:** Phase 1 concepts.md refinement (proposed, awaiting human review).

---

## F21 — The six-stage organization is not grounded in an established cognitive-science model; Klahr & Dunbar's SDDS covers only our first three stages

**Source:** Klahr & Dunbar, "Dual Space Search During Scientific Reasoning" (1988) — the canonical cognitive-science model of scientific reasoning.

**The finding:** The Scientific Discovery as Dual Search (SDDS) model is the most widely cited cognitive-science account of how people do scientific reasoning. It has *three* components, not six:

1. **Hypothesis space search** — generating candidate hypotheses from memory and prior knowledge.
2. **Experiment space search** — planning and executing experiments to test hypotheses.
3. **Evidence evaluation** — analyzing results and updating beliefs.

This maps roughly onto our Stages 1 (initiation), 2 (processing evidence), and 3 (self-checking). The SDDS model has *no analog* for our Stages 4 (holding conclusions), 5 (engaging with others' reasoning), or 6 (communicating knowledge). These three stages in our taxonomy are not grounded in any established cognitive-science model — they are additions we made based on our own taxonomic intuitions.

**Why this matters for us:** This is a real gap in the empirical grounding of concepts.md. Our "Organized by reasoning stage" design principle asserts that the six-stage structure is a "functional grouping," but three of those stages correspond to nothing in the cognitive-science literature on scientific reasoning. This does not mean the stages are wrong — it means their status is different from the first three. Stages 1–3 can point to SDDS for legitimacy; Stages 4–6 cannot.

**However, I want to argue the stages should be kept.** SDDS is a model of scientific discovery *as a laboratory task* — people manipulating equipment, forming hypotheses, running experiments. It is not a model of the full behavioral space of epistemic virtue that shows up in text. Our project targets text-visible epistemic dispositions, and some of the most important ones (how you hold conclusions after reaching them, how you engage with others' arguments, how you communicate what you believe) are not laboratory-task behaviors at all. They are meta-cognitive and communicative behaviors that matter enormously for scientific practice in the real world (peer review, collaboration, teaching) but that SDDS was never designed to capture.

The honest framing in concepts.md should be: Stages 1–3 are grounded in the SDDS model of scientific discovery. Stages 4–6 extend the taxonomy to cover dispositions that govern how conclusions are held and communicated — behaviors that are text-visible and instrumentally important but that fall outside the scope of laboratory-task cognitive-science models.

**Proposed concepts.md change (recorded here, not applied):** Add a brief note to the "Design principles" section acknowledging this. Something like: "The first three stages (initiation, evidence processing, self-checking) correspond to the components of Klahr & Dunbar's SDDS model of scientific reasoning. Stages 4–6 (holding conclusions, engaging with others, communicating) extend the taxonomy beyond laboratory-task models to cover dispositions that are text-visible and instrumentally important in scientific practice but not captured by SDDS."

**Why not restructure to match SDDS:** Because SDDS is the wrong granularity for our task. It would collapse 10 of our 15 concepts into three broad buckets, which is too coarse to extract as distinct activation vectors. The SDDS model is useful as a legitimacy anchor for Stages 1–3, not as a replacement for our taxonomy.

**Applies to:** Phase 1 concepts.md refinement (proposed, awaiting human review).

---

## F22 — Dennett's 4-step framework gives us a concrete operationalization for Steelmanning, and the literature distinguishes "charity" from "steelmanning"

**Source:** Philosophical and cognitive-science literature on the principle of charity and steelmanning, including Daniel Dennett's four-step framework.

**The finding:** Dennett's operationalization of charitable argumentation has four explicit steps:

1. **Re-express the target's position** so clearly and fairly that they would say "Thanks, I wish I had put it that way."
2. **List the points of agreement** (especially non-obvious ones).
3. **Mention what you have learned** from the target.
4. **Only then offer criticism.**

This is a much more concrete operationalization than our current sub-facets, which only cover "constructing the strongest version" and "distinguishing weak from best formulation." Dennett's framework adds two dimensions we are missing:
- **Acknowledging agreement** (step 2) — explicitly identifying what the opposing position gets right rather than framing the engagement as pure disagreement.
- **Sequencing** (step 4) — the order matters; criticism comes after the rest, not before or interleaved.

Additionally, the philosophical literature distinguishes *principle of charity* (accurately reconstructing what the other person actually meant) from *steelmanning* (strengthening the argument beyond what the original said, possibly with additions the original author did not make). These are meaningfully different. Charity is about faithful interpretation; steelmanning is about constructive improvement. A rigorous reasoner should do charity; steelmanning is a stronger move that some philosophers consider problematic because it can involve putting words in the other person's mouth.

**Why this matters for us:** Our current Concept 12 (Steelmanning) conflates these two operations and lacks the Dennett structure. This is the kind of under-specification F11 warned us about — concepts that are defined too thinly produce vectors that capture only narrow expressions of the target.

**Proposed concepts.md change (recorded here, not applied):** Sharpen Concept 12 in two ways:

1. Rename to "Steelmanning / Charitable Engagement" or similar to reflect that it covers both the interpretation and strengthening moves.
2. Expand sub-facets using Dennett's framework:
   - Accurately reconstructing the opposing position in its strongest form (charity)
   - Identifying and acknowledging points of genuine agreement before offering critique
   - Engaging with the best available version of a position rather than its weakest
   - Ordering engagement such that criticism follows, rather than precedes, the reconstruction

This brings Steelmanning from 2 sub-facets up to 4, which is at the cap but justified by the empirical/philosophical grounding.

**Applies to:** Phase 1 concepts.md refinement (proposed, awaiting human review).

---

## F23 — Quantitative Groundedness is dispositional, not ability-based; distinct from numeracy scales

**Source:** Lipkus et al. (2001) Numeracy Scale, Berlin Numeracy Test (Cokely et al., 2012).

**The finding:** The most widely used numeracy scales (Lipkus, Berlin) measure statistical *ability* — can the person correctly convert percentages to probabilities, reason about risk magnitudes, and sanity-check numerical claims. Our Concept 5 (Quantitative Groundedness) is something different: it measures the *disposition* to demand quantitative grounding for arguments and to check numbers rather than take them at face value.

These are not the same. A person can be high on numeracy ability (they can do the math when asked) while being low on quantitative groundedness (they do not bother to do the math unless prompted). Conversely, a person can be low on numeracy ability but high on quantitative groundedness (they know their limits and ask for statistical help rather than waving numbers around).

**Why this matters for us:** This is a clarifying distinction rather than a hole. Our concept is legitimately about disposition, not ability, and the numeracy literature does not directly cover it. But the distinction should be explicit in the definition so that reviewers and corpus generators understand what they are targeting. A passage demonstrating Quantitative Groundedness should show the reasoner *asking* for numbers, *checking* magnitudes, or *flagging* the absence of quantitative support — not necessarily computing statistics correctly. The virtue is "numbers matter here and I'm going to treat them as load-bearing," not "I can compute the correct answer."

**Proposed concepts.md change (recorded here, not applied):** Amend Concept 5's description to make the dispositional framing explicit:

> The reasoner treats numbers as load-bearing and actively checks or demands them, rather than letting qualitative intuitions carry the argument. This is a disposition (wanting to ground claims quantitatively and flagging the absence of quantitative support), not a measure of statistical ability (whether the reasoner can correctly compute the statistics).

No sub-facet changes needed; the existing three are consistent with the dispositional framing once the distinction is clarified.

**Applies to:** Phase 1 concepts.md refinement (proposed, awaiting human review).

---

## F24 — Causal Reasoning has no direct psychology measurement scale; our concept is anchored in philosophy of science, not personality psychology

**Source:** Causal Dimension Scale II (CDSII, McAuley, Duncan, & Russell, 1992) and related attribution-theory literature.

**The finding:** I expected to find a validated psychology scale that measures the quality of causal reasoning — how well people distinguish correlation from causation, consider confounders, and account for selection bias. What exists instead is the Causal Dimension Scale II, which measures *attribution theory* — how people explain the causes of their own successes and failures along four dimensions (locus of causality, stability, personal control, external control). This is about ego psychology ("was this my fault or the situation's?"), not about causal inference quality.

**Implication:** There is no direct empirical measurement instrument for our Concept 4 in the personality-psychology literature. Our concept is anchored in philosophy of science (Mill's methods, Pearl's causal calculus) and statistics education (confounders, selection bias, base rates), not in self-report psychology. This is a defensible framing — the concept is real and important — but we should stop assuming every concept will have a direct scale to cross-check against.

**Why this matters for us:** No action needed on concepts.md. The existing sub-facets (correlation/causation, confounders, selection/survivorship/base rate) are grounded in the appropriate literature even if that literature is not the psychology-scales tradition we have been checking. This is a useful null result: it tells us where to stop looking for validation.

**Applies to:** None — this is a "do not waste cycles looking for something that does not exist" finding.

---

## F25 — QRP literature directly operationalizes Intellectual Honesty; our sub-facets align well

**Source:** John, Loewenstein, & Prelec (2012), *Measuring the Prevalence of Questionable Research Practices With Incentives for Truth Telling*, Psychological Science.

**The finding:** The questionable research practices (QRP) literature in meta-science provides a concrete behavioral operationalization of scientific dishonesty. The standard QRP inventory includes specific practices such as: selective reporting of studies that worked, selective reporting of dependent measures, failing to report all experimental conditions, stopping data collection early when results cross a significance threshold, rounding p-values, deciding whether to exclude data only after seeing its impact on results, claiming unexpected findings were predicted from the start, and claiming results are unaffected by demographic variables when one has not checked.

**Why this matters for us:** Our Concept 10 (Intellectual Honesty) has three sub-facets that are essentially a prose description of the QRP inverse: faithfully representing what evidence shows, not cherry-picking or dropping inconvenient results, and acknowledging when results don't support the preferred interpretation. The alignment is good — but we arrived at it by intuition rather than by citing the empirical literature that operationalizes it. Adding the citation strengthens the concept's grounding and gives the corpus generator concrete anchors for what "dishonest" looks like (the QRPs themselves) and what "honest" looks like (their absence or explicit avoidance).

**Concepts.md change applied:** Added citation to John, Loewenstein, & Prelec (2012) in Concept 10's description; sharpened the second sub-facet to reference the specific QRP categories.

**Applies to:** Concept 10 refinement, applied directly.

---

## F26 — Divergent-thinking literature's fluency/flexibility distinction sharpens Hypothesis Generation

**Source:** Divergent thinking literature (Torrance Tests of Creative Thinking, Guilford's Alternate Uses Test). Responses are scored on four dimensions: fluency (how many ideas), flexibility (how different from each other), originality, and elaboration.

**The finding:** Of the four divergent-thinking scoring dimensions, two are directly relevant to our Concept 2: fluency (producing many hypotheses) and flexibility (producing hypotheses that differ from each other structurally, not just in surface details). Our current sub-facet "producing multiple competing explanations rather than fixating on one" is capturing both fluency and flexibility under one umbrella. The distinction matters: a reasoner who generates ten slightly different versions of the same basic hypothesis has high fluency but low flexibility, and that is actually a failure mode we want to steer away from. Hypothesis generation as an epistemic virtue is about *flexibility* (distinct alternatives) more than *fluency* (sheer count).

**Why this matters for us:** Small but real refinement. Sharpening the sub-facet to emphasize that the alternatives must be *structurally distinct*, not just variations on a theme, gives the corpus generator a clearer target and gives the extracted vector a sharper signal. A passage showing three genuinely different causal mechanisms for a phenomenon is better training data than a passage showing three phrasings of the same mechanism.

**Concepts.md change applied:** Refined the first sub-facet of Concept 2 to explicitly require structurally distinct alternatives, not just multiple phrasings of one idea.

**Applies to:** Concept 2 refinement, applied directly.

---

## F27 — Concept 8 only covers Flavell's monitoring dimension of metacognitive regulation, not planning or evaluating; this is defensible for text extraction

**Source:** Flavell (1979), *Metacognition and Cognitive Monitoring*, American Psychologist — the canonical framework for metacognitive ability.

**The finding:** Flavell's metacognition framework has two top-level components: metacognitive *knowledge* (declarative, procedural, conditional) and metacognitive *regulation*. Metacognitive regulation itself has three sub-skills: **planning** (selecting strategies and allocating resources before a task), **monitoring** (tracking comprehension and progress during a task), and **evaluating** (appraising the product and the process after a task).

Our Concept 8 (Metacognitive Awareness) focuses exclusively on the monitoring dimension. The sub-facets are about tracking reasoning as it happens, noticing pull toward certain conclusions, and flagging when reasoning feels forced. Planning and evaluating are not represented.

**Why this matters for us:** This is a real gap in conceptual coverage, but it is *defensible for our specific extraction setup*. Our training passages are reasoning monologues — someone thinking through a problem. Planning happens *before* the reasoning starts (selecting how to approach the problem) and evaluating happens *after* it ends (appraising the final product). A short reasoning monologue is almost entirely in the monitoring window. If we tried to add planning and evaluating sub-facets, they would rarely manifest in the passages we generate, which would give us either no extractable signal or a diluted vector.

So the right move is not to expand Concept 8 but to state explicitly that the concept is scoped to the monitoring dimension for principled reasons tied to our extraction methodology.

**Concepts.md change applied:** Added a brief note to Concept 8's description explaining that the concept is deliberately scoped to Flavell's monitoring dimension, with planning and evaluating excluded because they fall outside the reasoning-monologue window.

**Applies to:** Concept 8 refinement, applied directly.

---

## F28 — The Logical Rigor / First-Principles Thinking merger is philosophically imprecise but pragmatically defensible for extraction

**Source:** Cognitive science literature on deductive reasoning and first-principles thinking (Stanford Encyclopedia of Philosophy, cognitive psychology of deductive reasoning).

**The finding:** Philosophically, first-principles thinking and logical rigor are distinct cognitive moves. Logical rigor operates on given premises: does the conclusion validly follow? First-principles thinking operates on the premises themselves: are these the right starting assumptions, or should they be decomposed further and questioned? The literature treats them as complementary rather than identical — first-principles is often described as combining inductive decomposition (what are the fundamental elements of this problem?) with deductive building-up (given those elements, what follows?).

Our concepts.md merger absorbed first-principles into Logical Rigor on the grounds that "the two are nearly inseparable in text." That framing is imprecise. They are *distinguishable* in text — a first-principles passage will contain explicit questioning of inherited assumptions ("but why do we assume X in the first place?"), whereas a pure-rigor passage operates within the existing assumption set.

**Why this does not change the merger decision:** From an extraction perspective, the question is not "are these philosophically distinct?" but "will they produce separable vectors in a small model trained on general text?" The answer is probably not. Both dispositions share the dominant textual signature of stepwise decomposition, explicit assumption-surfacing, and validity checking. A small model is unlikely to have learned clean, separable representations for "question the premises" versus "check the inference" as distinct dispositions — the training data does not consistently label or contrast them. Merging them gives us one concept with stronger training signal rather than two noisy concepts that may collapse into the same vector anyway. This aligns with F11's "fewer but cleaner" principle.

**Concepts.md change applied:** Refined Concept 3's description to state the merger as a pragmatic extraction choice rather than a philosophical claim. The original "nearly inseparable in text" framing was replaced with an explicit note that the concepts are distinguishable philosophically but are merged because small models are unlikely to encode them as separate directions.

**Applies to:** Concept 3 refinement, applied directly. If the pilot run reveals that Logical Rigor as merged produces a clean vector, this finding becomes a recorded footnote. If the pilot shows the merged concept is muddy, the possibility of splitting it becomes a live option to revisit.

---

## F29 — Drummond & Fischhoff Scientific Reasoning Scale directly validates Evidence Grounding

**Source:** Drummond & Fischhoff (2017), *Development and Validation of the Scientific Reasoning Scale (SRS)*, Journal of Behavioral Decision Making. Also: Gormally et al. Test of Scientific Literacy Skills (TOSLS).

**The finding:** There is a validated psychology scale that directly measures the disposition to evaluate scientific evidence on its merits. The Scientific Reasoning Scale (SRS) is defined as "the skills needed to evaluate scientific findings in terms of the factors that determine their quality" — it is internally consistent, distinct from general scientific literacy measures, and predictive of belief calibration on contested scientific topics. The TOSLS covers related territory, focused specifically on undergraduates' ability to evaluate scientific information and arguments.

**Why this matters for us:** Our Concept 15 (Evidence Grounding) targets essentially the same disposition — tying claims to specific observations or data, distinguishing empirical claims from speculation, specifying evidence type. Until now this was supported only by our own intuitions about what "evidence grounding" means. The SRS gives us a validated, empirically-anchored construct to point at. This strengthens the concept's grounding and, more importantly for extraction, it provides a reference for what the sub-facets should target: the behaviors that load on the SRS factor structure are the behaviors our corpus should depict.

**Concepts.md change applied:** Added citation to Drummond & Fischhoff (2017) in Concept 15's description. No sub-facet restructuring — the existing three sub-facets align well with what the SRS measures.

**Applies to:** Concept 15 refinement, applied directly.

---

## F30 — Contrastive representation learning has an explicit decorrelation literature; our corpus-level approach is the training-data analog

**Source:** Barlow Twins (Zbontar et al., 2021), IDFD (instance discrimination with feature decorrelation), and related contrastive representation learning work. DeGCL (Deconfounding Graph Contrastive Learning) is an applied example in recommender systems.

**The finding:** The concern that contrastive training data can contain spurious correlations which get learned as shortcuts is well-recognized in the machine learning literature. Barlow Twins addresses this at the loss level by adding an explicit decorrelation term that penalizes cross-correlation between latent representations, forcing the model to produce diverse representations for semantically similar inputs. IDFD uses an instance discrimination loss combined with a feature decorrelation loss. DeGCL addresses confounding in graph contrastive learning by adjusting for learned deconfounding representations.

**Why this matters for us:** The confound we are worried about (correctness leaking into the virtue vector because virtuous reasoners also tend to be correct) has the same structure as the confound these architectures address (spurious features correlating with target labels). The ML literature addresses it at the *loss* level during training. We cannot do that because we are doing difference-of-means extraction rather than training, so our analog has to operate at the *data* level — breaking the correctness↔virtue correlation by constructing the corpus so that virtuous reasoners sometimes reach wrong conclusions and non-virtuous reasoners sometimes reach right ones.

This is convergent validation that the concern is real and that corpus-level decorrelation is a reasonable response. What the ML literature does not give us is a principled answer to "what percentage?" — the Barlow Twins loss is a continuous term, not a discrete ratio. Our 20–30% intuition remains an intuition, but it is an intuition about a problem that is recognized in the broader literature. Worth knowing, not worth acting on further.

**Applies to:** No concepts.md change. Useful as a citation anchor when writing generation-guidelines.md in Phase 3 — the correctness-confound mitigation section can point to the representation-learning literature as convergent justification for why corpus-level decorrelation matters.

---

## F31 — Anchoring Resistance as a construct is measurable; its cut stands for extraction reasons, not construct-validity reasons

**Source:** Debiasing intervention literature (Morewedge, Larrick, Lilienfeld and others on "consider-the-opposite" strategy; individual-differences work on actively open-minded thinking).

**The finding:** Anchoring bias has a robust debiasing literature. The consider-the-opposite strategy reliably reduces anchoring effects. Individual differences in susceptibility to anchoring correlate with measurable dispositions including actively open-minded thinking and numerical reasoning skills. Debiasing effects generalize across domains, which means resistance to anchoring is to some extent a general trait, not purely situational.

Our previous "Previously considered but cut" entry for Anchoring Resistance justified the cut by calling it "too situational — it only manifests when a specific anchor is present in the scenario." The first part of this is actually false at the construct level — the literature treats anchoring resistance as a general individual-difference characteristic. The second part is still true at the *text-manifestation* level — for anchoring resistance to show up in a short reasoning monologue, the passage has to include a specific numerical or framing anchor, which is an artificial constraint that does not generalize across scenarios.

**Why this matters for us:** The cut should stand, but for the honest reason. Anchoring resistance is a real construct; it is just hard to elicit in short reasoning passages without constructing anchor-present scenarios, and those scenarios would concentrate the corpus in a way that hurts generalization. The corrected framing is: "cut because the behavior requires a specific anchor stimulus to manifest in text, which cannot be introduced consistently across domains, not because the underlying construct is situational."

**Concepts.md change applied:** Refined the "Previously considered but cut" note for Anchoring Resistance to reflect the text-elicitation issue rather than implying the construct itself is situational.

**Applies to:** concepts.md "Previously considered but cut" note, applied directly. Minor honesty fix.

---

## F32 — Chi's self-explanation effect provides the psychology grounding for Reasoning Transparency

**Source:** Chi, De Leeuw, Chiu, & Lavancher (1994), *Eliciting Self-Explanations Improves Understanding*, Cognitive Science. The canonical study of the self-explanation effect.

**The finding:** Chi and colleagues established that when learners are prompted to explain reasoning to themselves (or to a reader), they learn more deeply than learners who re-read the same material. The effect has been replicated across many domains and both high- and low-ability learners. Chi's framework identifies three distinct mechanisms through which self-explanation works:

1. **Constructive** — the learner infers knowledge that was not directly stated in the source material.
2. **Integrative** — the learner connects new material to prior knowledge, integrating it into existing mental models.
3. **Error-correcting** — the act of explaining creates opportunities to notice conflicts between interpretation and evidence, and to correct them.

**Why this matters for us:** Our Concept 14 (Reasoning Transparency) is about showing reasoning steps, surfacing assumptions, and flagging weak points. Chi's framework adds empirical grounding for *why* this behavior is an epistemic virtue and not just a stylistic choice — self-explanation causally improves understanding. It also reveals an important distinction. Our current framing is about **output transparency** (the visible product — the passage shows its steps). Chi's self-explanation is about **process value** (the act of explaining is itself doing cognitive work).

For extraction purposes, we want the output-transparency framing, because that is what is visible in text. But the self-explanation literature gives us a principled reason to believe the behavior we are extracting corresponds to something cognitively real, not just a stylistic marker.

**Concepts.md change applied:** Added citation to Chi et al. (1994) in Concept 14's description with a brief note that the concept targets the output-visible form of self-explanation rather than the internal process.

**Applies to:** Concept 14 refinement, applied directly.

---

## F33 — The LLM literature treats our Reasoning Transparency as "legibility/monitorability," not "faithfulness" — important framing for interpretation

**Source:** Lanham et al. (Anthropic), *Measuring Faithfulness in Chain-of-Thought Reasoning*. Also: OpenAI's work on CoT monitorability (Guan, Wang, Carroll, Dou et al.), C2-Faith benchmark, and related 2025 papers on CoT faithfulness.

**The finding:** The LLM community has been intensely studying the exact phenomenon our Concept 14 targets, but with different vocabulary and a critical distinction. The key terms:

- **Faithfulness** — whether the chain of thought accurately reflects the model's *internal* computation. Cannot be directly measured because we lack ground truth about internal computation; estimated via perturbation studies and consistency checks.
- **Monitorability** — whether the CoT allows a human observer to identify particular aspects of the model's computation. A practical substitute for faithfulness.
- **Legibility** — whether a human with the same language capabilities can follow the CoT. Explicitly independent of correctness (a CoT can be legible and still confused). Measured more directly than faithfulness.

**Why this matters for us:** Our Concept 14 as currently framed is about what the text *looks like* — steps shown, assumptions surfaced, weaknesses flagged. That is the legibility/monitorability framing, not the faithfulness framing. A Reasoning Transparency vector extracted from our corpus would steer the model toward producing more legible text, not necessarily toward reasoning more faithfully internally.

This matters for how we interpret results. If steering along the vector improves benchmark performance, we cannot claim we have made the model's internal reasoning more faithful — we have made its output text more legible, and the legibility is correlated with benchmark improvement (possibly because more legible reasoning steps make the model less likely to skip checks). That is still a meaningful and publishable result, but the claim must be scoped correctly.

**Concepts.md change applied:** Added a note to Concept 14's description specifying that the extractable target is legibility/monitorability (text-visible) rather than faithfulness (internal-state accuracy), and that the distinction matters for how we interpret steering results in Phase 4 and the writeup.

**Applies to:** Concept 14 refinement, applied directly. Also applies to the eventual project writeup — the result language must be "increased legibility" not "increased faithfulness" unless we have separate evidence for the latter.

---

## F34 — Corpus budget may be underspecified; literature reports 80–100 contrastive pairs as minimum for stable vectors (PROPOSAL — not applied)

**Source:** Contrastive Activation Addition (CAA) follow-up literature and representation engineering surveys, reporting empirical convergence data for steering vector stability.

**The finding:** The published activation-steering literature reports that robust steering vectors require *at least 80–100 contrastive pairs per property* to avoid high variance and spurious effects, with performance plateauing thereafter. Our current plan specifies 15–30 triplets per concept, which translates to 30–60 directional observations (each triplet yields a virtuous-minus-neutral vector and a non-virtuous-minus-neutral vector, giving two samples per triplet).

At 15 triplets per concept we are at roughly one-third of the recommended minimum. At 30 triplets we are at roughly half. This means our current corpus plan is likely insufficient for stable vector extraction even for the easier concepts, and the resulting vectors may suffer from high variance that masquerades as "the concept did not extract" when the actual issue is undersampling.

**Why this matters for us:** This is a methodological concern that directly affects the experimental goal. Running Phase 4 with an undersized corpus risks false-negative conclusions — we might declare a concept unextractable when the real issue is that we did not generate enough contrastive pairs to stabilize the difference-of-means estimate. A false negative on the pilot concept (F11 suggested Calibrated Confidence as the starting point) would be particularly costly because the entire project go/no-go signal depends on that pilot.

**Proposed corpus budget change (RECORDED, NOT APPLIED — this is a resource-impact change that needs human review):**

Current budget (concepts.md): 15–30 triplets per concept × 15 concepts = 225–450 triplets total.

Proposed revision: target 50–60 triplets per concept (yielding 100–120 directional observations, comfortably above the 80-pair minimum) × 15 concepts = 750–900 triplets total. This is roughly a 3× increase in corpus generation work.

**Mitigation options if the full 50–60 per concept is too expensive:**

1. **Tiered budget** — generate 50–60 triplets only for the high-likelihood concepts identified in F11 (Calibrated Confidence, Reasoning Transparency, Evidence Grounding, Hypothesis Generation), and keep 15–30 for the harder concepts. Justification: the easy concepts are our pilot candidates and most need robust extraction; harder concepts are more likely to fail regardless of corpus size, so budget efficiency matters more there.

2. **Pilot-only scale-up** — generate 50–60 triplets only for the single pilot concept, and defer the budget decision for other concepts until after pilot results come in. If the pilot succeeds cleanly, we know 50–60 is a defensible target for the rest. If it succeeds with a smaller corpus, we save work.

3. **Full scale-up** — generate 50–60 for all concepts. Most expensive but most methodologically defensible.

My recommendation (for human review): **Option 2 (pilot-only scale-up)**. This is the most information-efficient move. It matches our existing "manual before automated" philosophy by treating the pilot as a calibration run for the scaling decision, and it defers the expensive budget commitment until we have data about whether the corpus size actually matters at our scale.

**Why this is recorded as a proposal rather than applied:** Changing the corpus budget materially affects how much work Phase 2 will require and how long the project will take. It also interacts with the user's "manual first" preference — a 3× larger manual corpus may or may not be acceptable depending on how aggressive the manual phase is meant to be. This is a project-scope decision, not just a taxonomy refinement, and should not be made by the scheduler autonomously.

**Applies to:** concepts.md "Corpus budget implications" section — update needed pending human review.

**Resolution (user decision):** Option 2 chosen — pilot-only scale-up. Applied to concepts.md "Corpus budget implications" section. Pilot concept (Calibrated Confidence per F11) gets 50–60 triplets. Budget for the remaining 14 concepts deferred until pilot calibrates the required corpus size at our specific model scale. This matches the manual-first philosophy and defers the expensive commitment until we have data.

---

## F35 — Toulmin's argument model provides an established rubric for Phase 3 review criteria

**Source:** Toulmin's Argument Pattern and its application to science-education rubrics for assessing scientific writing quality.

**The finding:** Toulmin's model decomposes arguments into six elements: claim, data (grounds), warrant, backing, qualifier, rebuttal. The first three are essential, the last three optional. Rubrics built on this model have been validated for assessing scientific writing (reported generalizability coefficient g = 0.85 in one undergraduate biology laboratory study). The evaluation criteria commonly layered on top include *relevance* (premises connect to conclusion), *acceptability* (premises are plausible), and *sufficiency* (evidence is adequate in type, quantity, and use).

**Why this matters for us:** This does not directly affect concepts.md — Toulmin's model is not a candidate for concept reorganization. Where it matters is Phase 3, specifically the review-rubric.md artifact. When reviewing a generated virtuous passage for Evidence Grounding, Logical Rigor, Reasoning Transparency, or Steelmanning, we need concrete criteria to score the passage against. Toulmin's decomposition gives us those criteria for free: does the passage state a claim? Does it present data? Does it surface the warrant connecting data to claim? Does it qualify appropriately? This is a drop-in structure for the review rubric.

**Applies to:** Phase 3 review-rubric.md design. When we write the rubric, structure the content-preservation and style-capture scoring around Toulmin elements. Cite the rubric validation study (Timmerman et al., undergraduate biology labs, g = 0.85) as evidence that this kind of rubric can achieve reliable inter-rater agreement.

---

## F36 — The six-stage ordering is conceptual grouping, not temporal sequence; scientific reasoning in practice loops and interleaves

**Source:** Cognitive science literature on sequential vs. parallel processing, central bottleneck theory, and iterative models of scientific reasoning (SDDS already covered in F21, plus dual-process theory).

**The finding:** The cognitive science consensus is that low-level cognitive processing is massively parallel, while central decision/response stages are sequential. Scientific reasoning specifically is modeled as iterative rather than strictly linear — the SDDS model (Klahr & Dunbar) explicitly represents hypothesis space search and experiment space search as *linked* through evidence evaluation, meaning these phases feed back into each other rather than executing once in a fixed order.

Our concepts.md presents Stages 1–6 in numerical order, which strongly implies a temporal sequence. That implication is not accurate to how scientific reasoning actually unfolds. In real reasoning, a scientist might start with Stage 2 (process evidence), loop back to Stage 1 (generate a new hypothesis after seeing the evidence), jump to Stage 3 (notice a confirmation bias pull), return to Stage 2, and so on. The stages are aspects of reasoning, not phases of it.

**Why this matters for us:** For extraction, the temporal-vs-aspect distinction does not matter — we are extracting text-visible dispositions, not modeling the cognitive process. A passage can exhibit multiple stages simultaneously and our extracted vectors operate at the passage level, not at the process level. But concepts.md should not imply a temporal sequence that isn't there, because future reviewers (including us) might make design decisions based on that false implication.

**Concepts.md change applied:** Added a short note to the "Organized by reasoning stage" design principle clarifying that the numerical ordering is conceptual grouping, not a claim about the temporal sequence of reasoning. Reasoning in practice loops and interleaves across stages; the taxonomy captures aspects that can co-occur, not phases that execute in order.

**Applies to:** Concept taxonomy framing. Small honesty fix, applied directly.

---

## F37 — Multi-concept vector extraction is an active research area; validates F12 specificity matrix and introduces k-means sub-facet discovery for Phase 4

**Source:** Representation engineering survey literature, including Wehner (2025), and work on orthogonalization, disentanglement losses, and k-means-based concept cluster discovery.

**The finding:** The literature confirms multi-concept vector extraction is an active problem with known techniques:

1. **Weighted combination of concept vectors** — To steer multiple concepts simultaneously, representation engineering combines layer-wise vectors in a weighted sum. This is the "naive" multi-concept approach and works when concepts are approximately orthogonal.

2. **Orthogonal probes with weighted combination** — Train multiple orthogonal linear probes and combine them. Explicit orthogonalization avoids interference between concept vectors.

3. **Global disentanglement losses** — Extend local disentanglement toward a global loss regularizing correlations between latent features through orthogonality constraints. Reduces redundancy in the latent space.

4. **K-means on difference vectors** — A technique for discovering sub-aspects of a concept post-hoc: cluster the individual (positive - negative) difference vectors using k-means. Each cluster corresponds to a distinct facet of the concept that emerged from the data. One linear probe per cluster captures that facet.

**Why this matters for us:** 

- Technique (1) and (2) validate the general feasibility of our 15-concept plan. Multi-concept extraction is done routinely.
- Technique (3) is directly relevant to F12's specificity matrix concern — the ML literature has explicit methods for decorrelating concept vectors, which is what we want.
- Technique (4) is a **new option for Phase 4 that didn't exist in our plan**: after extracting a vector for (say) Intellectual Humility from ~30–60 triplets, we can apply k-means clustering to the individual difference vectors and discover whether our four sub-facets (data skepticism, methodology doubt, generalizability caution, ego independence) actually correspond to distinct clusters in activation space. This gives us an empirical test of the sub-facet decomposition rather than taking it on faith.

**Applies to:** Phase 4 validation design. Record as a deferred Phase 4 technique — k-means sub-facet discovery is a cheap post-hoc analysis that we should plan to run for every concept that extracts successfully.

---

## F38 — Quality-Diversity Generative Sampling validates explicit domain quotas; random topic selection reproduces generator biases

**Source:** QDGS (Quality-Diversity Generative Sampling) framework for synthetic data generation, which samples balanced training datasets from generative models by explicitly prompting for desired attribute coverage.

**The finding:** The QDGS literature reports that random sampling from a generative model reproduces the biases of the generator's training distribution. If you prompt an LLM to "generate a scientific reasoning scenario," the outputs will cluster around the domains the LLM was trained most heavily on (CS, medicine, popular physics) and under-represent domains that appear less in pretraining (ecology, economics of specific subfields, experimental psychology methodology, engineering history). The fix is explicit attribute prompting: "generate a scenario from ecology" or "generate a scenario involving sample size limitations in a longitudinal study."

**Why this matters for us:** This is direct confirmation that F4's domain-diversity quota is not optional bookkeeping — it is the only way to avoid generator bias contaminating our corpus. A corpus constructed via "just generate reasoning scenarios" prompts will be under-diversified even if the total count is high, because the diversity problem is not sample size, it is sampling procedure.

**Concrete implication for generation-guidelines.md (Phase 3):** The fact-pack generation step must specify the domain explicitly in the prompt, not leave it to the generator's choice. The domain list should be fixed ahead of time (~8 domains per F4) and the generator prompted once per domain per concept. This is a significant difference from "generate N scenarios and hope they are diverse."

**Applies to:** Phase 3 generation-guidelines.md. Will inform the fact-pack generation protocol when that section is written.

---

## F39 — Stanovich's Actively Open-Minded Thinking (AOT) scale is both validation and challenge to our taxonomy granularity

**Source:** Stanovich & West (2007), refined through Stanovich, Toplak, and colleagues (2019, 2023). The Actively Open-Minded Thinking scale in its current form (13-item or 30-item CART version).

**The finding:** AOT is a single validated psychological construct — treated by psychology as *one* latent trait — that unifies several dispositions our taxonomy has split into separate concepts. The AOT scale items tap:

1. Willingness to consider alternative opinions
2. Sensitivity to evidence contradictory to current beliefs
3. Willingness to postpone closure
4. Reflective thought / calibrating opinion strength to evidence strength
5. Seeking nuance and avoiding absolutism
6. Collecting information before making up one's mind

Mapped against our concepts: (1) corresponds to parts of Steelmanning (#12) and Confirmation Bias Awareness (#7). (2) corresponds to Confirmation Bias Awareness (#7) and Intellectual Humility's willingness-to-update sub-facet (#6). (3) corresponds to Comfort with Ambiguity (#11). (4) corresponds to Calibrated Confidence (#9). (5) corresponds to Calibrated Confidence (#9) and Comfort with Ambiguity (#11). (6) corresponds to parts of Hypothesis Generation (#2) and Evidence Grounding (#15).

In short: psychology treats 6–7 of our 15 concepts as facets of a single latent trait. And critically, **AOT predicts heuristics-and-biases task performance better than most cognitive ability measures** and "uniquely predicts performance on judgment and decision-making tasks in adult samples, in addition to cognitive abilities." In other words, AOT as a unified construct has strong empirical predictive validity for exactly the kind of reasoning improvement our project is trying to produce in the model.

**Why this matters for us — this is both good news and a challenge:**

**Good news:** If AOT is predictive of better reasoning in humans, and if small models encode AOT-adjacent dispositions, steering toward AOT-type virtues is likely to produce the kind of performance improvement we are hoping for. AOT is essentially the integrated version of our target dispositions, and its empirical track record is strong. This is validation that our intervention hypothesis is plausible.

**Challenge:** Psychology would argue that our taxonomy over-splits. If the 6–7 concepts listed above are facets of one latent trait in humans, they may also be facets of one latent direction in model activation space — meaning we might extract 7 vectors that turn out to be nearly parallel copies of the same AOT direction. This is a specific collinearity risk that is more severe than the pairwise collinearity risks already flagged in concepts.md. It is, essentially, the hypothesis that *the specificity matrix will show a large AOT-cluster dominating 6–7 concepts*.

**What to do about it:**

Option A — do nothing to the taxonomy, but treat AOT as a post-hoc analysis target. After extraction, compute the centroid of the 6–7 AOT-related concept vectors and check whether the individual vectors collapse onto it or remain distinguishable. If they collapse, we have replicated the AOT finding at the activation level and our contribution becomes "AOT is a real latent direction in small model representations." That is itself a publishable result.

Option B — explicitly test AOT as a *single* concept in parallel with the finer decomposition, by generating an "AOT-broad" corpus that mixes all the sub-facets and extracting a unified vector. Compare its performance against the combined/weighted sum of the 6–7 fine-grained vectors. Whichever performs better on reasoning benchmarks becomes the recommended extraction strategy.

Option C — restructure the taxonomy now, collapsing the 6–7 concepts into a smaller AOT-aligned set before Phase 4.

**My recommendation:** **Option A** (no change to concepts.md now, treat AOT as a post-hoc analysis target). Reasoning: the finer taxonomy gives us more information if it works and can be collapsed after the fact if it doesn't. Collapsing now is irreversible — we would lose the ability to see whether the concepts extract as distinct vectors at all. And the fine-grained extraction is not much more expensive than the coarse-grained extraction since we are reusing corpus infrastructure. Option A preserves all possibilities and turns the AOT question into an empirical finding rather than a design assumption.

**Concepts.md change applied:** Added a note to the "Known risks and open questions" section flagging the AOT unification risk as a specific collinearity concern to watch for post-extraction. Did NOT restructure the taxonomy — this is Option A.

**Applies to:** Known risks section, applied directly. Phase 4 post-extraction analysis should include the AOT centroid test.

---

## F40 — CIHS and open-minded thinking correlate at r=.56 but remain empirically distinct, somewhat weakening the F39 AOT unification concern

**Source:** Krumrei-Mancuso & Rouse (2016) validation data and follow-up work correlating the Comprehensive Intellectual Humility Scale (CIHS) with Actively Open-Minded Thinking measures.

**The finding:** The validation data for CIHS reports a moderate correlation with open-minded thinking (r = .56), and CIHS predicts variance in open-minded thinking *beyond* what age, social desirability, and commonly used humility measures explain. In psychological terms: the two constructs are related but distinguishable, and CIHS is not simply a proxy for AOT.

**Why this matters for us:** F39 raised the concern that Stanovich's AOT scale unifies 6–7 of our concepts as facets of one latent trait, and that this unification might replicate at the activation-vector level and collapse our fine-grained vectors onto a single AOT direction. The CIHS/open-minded-thinking data provides a partial counterweight: if humility and open-mindedness are empirically distinguishable in human self-report data *despite* being correlated, they may also be distinguishable in model activation space. The correlation is moderate (r = .56 means ~31% shared variance), which is meaningful overlap but not collapse.

This doesn't eliminate the F39 risk — it just adjusts the expected magnitude. The concepts in the AOT cluster are probably not fully orthogonal (nobody expected them to be), but they are probably also not fully collapsed onto a single direction. We should expect to see meaningful cross-concept correlations in the specificity matrix without the matrix being rank-1.

**Why this is actionable:** Adjusts the post-extraction analysis plan. Rather than running a single binary test ("does AOT collapse the concepts or not?"), we should plan to measure the actual correlations in the specificity matrix and compare them against the ~0.5–0.6 range reported in the psychology literature. If our vectors correlate in that same range, we have convergent evidence that we're capturing the psychologically real structure. If they correlate much more than that, we have collapse. If they correlate much less, we have over-separation (extracting spurious distinctions).

**Applies to:** F39's AOT unification risk is refined but not resolved. Phase 4 specificity-matrix analysis should compare observed cross-concept correlations against the psychology literature's reported correlations as an additional validation check. No concepts.md change.

---

## F41 — Epistemic Honesty is philosophically distinct from Calibrated Confidence by the diligence dimension; supports keeping Concepts 9 and 10 separate

**Source:** Virtue epistemology literature on epistemic honesty and epistemic diligence, including the Stanford Encyclopedia entry on virtue epistemology and contemporary work on epistemic integrity.

**The finding:** The philosophical literature draws a specific distinction between calibrated confidence and epistemic honesty that our concepts.md noted as a "live collinearity risk" but never fully characterized. The key insight:

- **Calibrated confidence** is about matching the strength of one's language to the strength of one's evidence. A well-calibrated person says "probably" when the evidence supports "probably" and "I don't know" when the evidence supports "I don't know."
- **Epistemic honesty** requires calibration PLUS *epistemic diligence* — the commitment to verify sources, check assumptions, and not rest on beliefs one has not yet adequately investigated.

The philosophical argument: "it is still 'honest' in some sense to report beliefs that you are not epistemically justified in holding, but it will only be *virtuously honest* to report those beliefs when you have exercised epistemic diligence in forming them." A person can be perfectly calibrated at the surface level (their language matches their subjective confidence) while being epistemically dishonest (their subjective confidence is not grounded in diligent investigation).

In text-visible behavior, this distinction manifests as:
- A calibrated-but-not-honest passage: careful hedging ("I think", "probably") around claims the reasoner hasn't actually verified.
- An honest-but-poorly-calibrated passage: rigorous acknowledgment of verification status with mismatched confidence language ("I'm certain" about things the reasoner has only weakly checked).
- The virtuous-on-both passage: rigorous verification AND appropriate confidence language about the resulting beliefs.

**Why this matters for us:** The F1-era worry that Concepts 9 and 10 would produce parallel vectors is real but the distinction between them has a specific cognitive-textual signature (diligence/verification behavior) that our current sub-facets don't fully capture. Concept 10's sub-facets focus on the "faithful representation" dimension and the QRP-avoidance dimension, but don't explicitly include diligence/verification. Adding that dimension makes the concept more distinguishable from Calibrated Confidence at the text level.

**Concepts.md change applied:** Added a fourth sub-facet to Concept 10 covering epistemic diligence — the explicit behavior of checking sources, verifying assumptions, and not resting on unverified beliefs even when one's language about them is well-calibrated. Also updated the Concept 10 description to note that honesty requires diligence on top of calibration. Sub-facet count for Concept 10 is now 4, still within the cap.

Also updated the "Collinearity risk (unresolved)" note in concepts.md to reflect that the Calibrated Confidence ↔ Intellectual Honesty pair has a specific philosophical distinction (diligence/verification) that can be checked in the specificity matrix, not just an abstract "these are similar" concern.

**Applies to:** Concept 10 refinement, applied directly. Also refines the collinearity-risk note.

---

## F42 — Pearl's causal hierarchy has three levels (association → intervention → counterfactual); our Causal Reasoning sub-facets cover the first two but not the third

**Source:** Pearl's Causal Hierarchy (PCH), foundational to modern causal inference. Three levels of causal reasoning corresponding to three prototypical cognitive actions:

1. **Association (Level 1)** — "seeing." Conditional probability sentences, P(y|x). Observational reasoning. No causal information required.
2. **Intervention (Level 2)** — "doing." Sentences of the form P(y|do(x)). Requires reasoning about what would happen if one actively intervened on a variable rather than merely observing it.
3. **Counterfactual (Level 3)** — "imagining." Sentences of the form P(y_x|x',y'). Reasoning about what would have happened had a variable been different, given what actually did happen.

**The finding:** Our Concept 4 (Causal Reasoning) sub-facets are:

- Distinguishing correlation from causation (Level 1 → Level 2 transition)
- Considering confounders and alternative causal paths (Level 2 reasoning about mechanism)
- Recognizing selection bias, survivorship bias, and base rate neglect (Level 1 failure modes)

These all sit at the Association ↔ Intervention boundary. We do not explicitly cover Level 3 (counterfactual reasoning) — the disposition to ask "what would have happened if..." given the observed outcome. This is a genuine gap in coverage relative to Pearl's framework.

**Why this matters for us — and why we should NOT add a counterfactual sub-facet:**

Counterfactual reasoning is a distinct text signature ("had X been different, Y would have..." is easy to recognize), so in principle it could be extracted. But three reasons argue against adding it as a fourth sub-facet to Concept 4:

1. **Collinearity with other concepts.** Counterfactual thinking overlaps significantly with Hypothesis Generation ("what else could explain this?") and Comfort with Ambiguity (holding multiple plausible worlds in mind simultaneously). Adding it to Causal Reasoning would create competing claims on the same text signature.

2. **Practical scientific reasoning mostly operates at Levels 1 and 2.** Distinguishing correlation from causation and reasoning about confounders are the workhorses of day-to-day scientific thinking. Level-3 counterfactual reasoning is more specialized (causal inference, econometrics, philosophy of history). For our corpus of general-purpose reasoning passages, Level-1/2 coverage is where the signal is strongest.

3. **Pearl's own framing.** Counterfactuals subsume interventional questions (if you can answer Level 3, you can answer Levels 1 and 2). So a reasoner who exhibits strong Level-2 performance in text is implicitly reasoning at Pearl's higher levels when needed. Our Level-1/2 focus is not a gap; it is a reasonable scope for the concept.

**Concepts.md change applied:** Added a citation to Pearl's causal hierarchy in Concept 4's description, explicitly acknowledging the three-level structure and justifying the scope focus on Levels 1 and 2. No new sub-facet. This is a grounding and honesty refinement, not a structural change.

**Applies to:** Concept 4 refinement, applied directly. Also: Phase 4 post-extraction analysis could check whether the extracted Causal Reasoning vector shows any signature of Level-3 counterfactual thinking (e.g., by validating on passages containing explicit "had X been different" constructions). This would be a deferred Phase 4 validation check, not a current concern.

---

## F43 — "In-advance correctness direction" literature directly validates our core assumption AND surfaces a rationalization caveat

**Source:** Recent work on linear probes extracting reasoning quality signals from language model activations, including "No Answer Needed: Predicting LLM Answer Accuracy from Question-Only Linear Probes" (OpenReview 2025) and related work on early decision encoding in tool-calling models.

**The finding:** Two empirically-grounded results that directly bear on Phronesis:

**Result 1 — Correctness is a linear direction extractable with simple probes.** Linear probes trained on activations captured *before any generation tokens are produced* successfully predict whether the model will produce a correct answer. The signal:
- Emerges within the first few reasoning tokens and is stable across prefixes.
- Generalizes across diverse out-of-distribution knowledge datasets.
- Is decodable with simple linear probes, strongly supporting the Linear Representation Hypothesis for reasoning-quality-adjacent features.

**Result 2 — Steering along the correctness direction flips behavior, and the model rationalizes the flip.** When activations are steered, reasoning models flip their decisions in 7–79% of cases depending on the model and benchmark. Critically: when a model flips, it "invents reasons to rationalize and justify the flip, rather than resisting it." The chain of thought adapts to whatever direction the activation was pushed.

**Why this matters for us — two important implications:**

**(A) Core assumption validated.** The central theoretical risk of Phronesis (F11 — "activation steering cannot create competencies the model lacks") is partially resolved in our favor for the reasoning-quality family of concepts. If a simple linear probe can extract a "correctness direction" from early activations and steering along it causally changes model behavior, then reasoning-quality-adjacent virtue directions almost certainly exist in small models. This does not guarantee that *every* virtue in our taxonomy is extractable, but it strongly supports the feasibility of the project for at least the "high likelihood" tier in F11 (Calibrated Confidence, Reasoning Transparency, Evidence Grounding, Hypothesis Generation). This is the most important piece of external validation we have found.

**(B) Rationalization caveat — critical for Phase 4 interpretation.** This is the dark side of the same finding. If the model *rationalizes* steered decisions rather than *reasoning* them out, then a successful steering experiment on our virtue vectors does not necessarily mean the model has become a more virtuous reasoner. It may mean the model has become better at producing text that looks like virtuous reasoning around whatever conclusion it was pushed toward. This sharpens F33's legibility-vs-faithfulness distinction with direct empirical evidence: the distinction is not hypothetical, it is documented in models very similar to ours.

Phase 4 validation must explicitly distinguish these two possibilities. One way: steer the virtue vector on problems with a ground-truth correct answer, and measure whether the model's accuracy changes or just its reasoning style changes. If accuracy improves, we have evidence of genuine reasoning improvement (or at least correlation). If accuracy stays flat but reasoning style shifts, we have evidence of rationalization. Both outcomes are publishable but the claims must be different.

**No concepts.md change needed** — this finding informs Phase 4 protocol design and the writeup, not the concept taxonomy.

**Applies to:** The go/no-go assessment for the project overall is now more positive. Phase 4 validation protocol must include the accuracy-vs-style distinction test.

---

## F44 — Small LLMs default to assertive language regardless of internal confidence state ("epistemic mismatch"); relevant to extraction difficulty of Calibrated Confidence

**Source:** "Epistemic Integrity in Large Language Models" (arXiv 2411.06528) and related 2024–2025 work on LLM confidence expression. Also: Virtue Semantics (ICML 2025 workshop) on moral-virtue consistency in LLMs.

**The finding:** Recent empirical work documents an "epistemic mismatch" in language models: they express unwarranted certainty in their generated outputs despite having low internal confidence at the token level. The mismatch is systematic — models default to confident, assertive language regardless of whether their actual reasoning reliability warrants it. The Virtue Semantics paper extends this to moral-virtue space, showing that even the most consistent LLMs have internal virtue representations that do not map neatly onto their action choices.

**Why this matters for us — two implications for extraction:**

**(A) Calibrated Confidence may be *harder* to extract than F11 placed it.** F11 ranked Calibrated Confidence in the "highest likelihood" tier for extraction because the disposition has clear textual markers (hedging, probability language, uncertainty acknowledgment). But if the small-model default is assertive language regardless of internal confidence state, then our virtuous-calibrated corpus passages will have to fight against a strong pretraining prior. The non-virtuous (overconfident) end of our contrastive pairs is essentially the model's baseline behavior, which means the difference-of-means calculation will have a larger signal in the non-virtuous direction than we expected. This is not a blocker — it may actually help vector extraction by making the contrast sharper — but it changes what we should expect when we apply the vector for steering. Steering toward calibration may require large coefficients to overcome the baseline assertive prior.

**(B) The moral-virtue consistency result is a warning about F7 (probe-steering correlation).** F7 planned a validation check where we train a probe on a downstream behavior, steer along the extracted virtue vector, and expect the steering effect to correlate with probe quality. The Virtue Semantics finding — that LLM moral representations don't map neatly onto action choices — is a case where the probe-steering correlation pattern does not hold. Internal virtue representations exist, but they don't reliably drive behavior. For us: if we see extracted virtue vectors that probes can read but steering doesn't change downstream task performance, that is the same failure mode, and it is a known phenomenon in 2025 literature. We should plan for this as a possible outcome, not as an anomaly.

**Proposed F11 tier adjustment (recorded, not applied):** Calibrated Confidence should probably move from "highest likelihood" to "medium likelihood" to reflect the baseline-assertiveness headwind. The other highest-tier concepts (Reasoning Transparency, Evidence Grounding, Hypothesis Generation) don't face this specific headwind and remain defensibly highest-tier. I am not applying this tier change directly because the adjustment is non-trivial — it affects the pilot concept selection and the go/no-go framing of the whole project. Recorded as a proposal for user review.

**Applies to:** Phase 4 expectations (larger coefficients may be needed for Calibrated Confidence) and the F11 tier ordering (pilot concept choice).

---

## F45 — Activation steering is a dispositional modulator, not a propositional injector; this is *direct validation* of Phronesis's concept choice

**Source:** "What Can We Actually Steer? A Multi-Behavior Study of Activation Control" (arXiv 2511.18284) and related 2025–2026 empirical work on the scope of activation steering.

**The finding:** Recent empirical work has begun systematically mapping what activation steering can and cannot do, and the result is a sharp dispositional/propositional dichotomy:

**What works (steering is effective):**
- Internal model dispositions: biases, sentiments, abstract tendencies.
- Personality traits.
- Misalignment behaviors (toxicity, sycophancy, etc.).
- "Densely represented in activation space and easily manipulable via vector addition."
- Steering outperformed prompting baselines for these categories.

**What does not work (steering fails):**
- Propositional knowledge injection: getting the model to know facts it doesn't already know.
- Specific external knowledge (biographical details, obscure facts).
- Coherent identities not already present in the context.
- Quote from the literature: *"You cannot steer a model into knowing things it doesn't know — there's no 'truthfulness direction' that magically makes a model correct about obscure historical facts, and the result is usually that the model becomes more confident rather than more correct. Steering is about behavioral tendencies, not knowledge."*

**Why this is load-bearing for Phronesis:**

All 15 concepts in our taxonomy are **dispositional**, not propositional. We are targeting *how* the reasoner approaches evidence, *how* they hold conclusions, *how* they engage with others' arguments — not *what* they know. This is exactly the category where the recent literature says activation steering is effective. Our concept choice is squarely within the sweet spot of what steering can do.

This is the strongest piece of external validation for project direction we have found, stronger even than F43. F43 validated the extraction mechanism (linear probes find correctness-adjacent directions). F45 validates the *target category* — the kinds of things we are trying to extract are precisely the kinds of things that have been empirically shown to be steerable. F43 + F45 together substantially raise confidence that the project's feasibility is not an open question at the "does it work in principle" level.

**However — a critical refinement to the intervention hypothesis:**

Project.md states the intervention hypothesis as "steering toward epistemic virtues should produce measurable improvements on reasoning-sensitive benchmarks without degrading general capability." F45 sharpens this to a precise scope condition:

- Steering a virtue vector **should** improve performance on reasoning tasks where the limitation is *dispositional* — where the model has the necessary knowledge or skills but does not deploy them well due to baseline habits (e.g., defaults to overconfident claims even when it has evidence pointing toward uncertainty).
- Steering a virtue vector **should not** improve performance on reasoning tasks where the limitation is *propositional* — where the model simply lacks the necessary knowledge. No amount of steering toward "Calibrated Confidence" will make the model correct about things it does not know.

The failure mode to watch for is "the model becomes more confident rather than more correct." If our steered model produces more assertive or more hedged text but does not actually improve on accuracy metrics, we have hit the disposition-vs-knowledge boundary.

**Concrete implications:**

1. **Phase 4 benchmark selection must distinguish disposition-limited from knowledge-limited reasoning tasks.** Knowledge-limited tasks should be avoided or used only as negative controls (we expect no improvement there, and that is informative). Disposition-limited tasks (e.g., problems the model can solve when carefully prompted but fails when prompted briefly) are where we expect steering to produce improvements.

2. **The rationalization caveat from F43 becomes more important here.** If we see behavioral changes without accuracy changes, the model is doing dispositional modulation but the modulation is not translating to correctness. This might be real rationalization (model produces virtuous-looking text around a pre-determined wrong answer) or it might be the knowledge-limit ceiling. Both are important to distinguish in the writeup.

3. **Project.md update proposed (small, honest refinement, not a goal change):** The hypothesis section should explicitly note the dispositional/propositional scope condition, so that future readers (including us) do not overclaim what steering can do.

**Concepts.md change:** None. The taxonomy is already dispositional; no refinement needed.

**project.md change applied:** Added a scope-condition note to the hypothesis section in project.md reflecting the dispositional/propositional distinction. This is a small honesty refinement to the hypothesis framing, not a goal change — it clarifies what a successful result looks like rather than moving the goalposts. The rule in the cron permits project.md edits for "genuine changes to goals, hypothesis, scope, or success criteria" and I'm treating this as a hypothesis-framing precision fix.

**Applies to:** project.md hypothesis section (applied), Phase 4 benchmark selection (deferred), and the final writeup (claims about steering must respect the dispositional scope).

---

## F46 — Evidence-grounding benchmarks exist (FACTS Grounding, GaRAGe, DEER); "57% of LLM citations are post-rationalized" further reinforces F43's rationalization caveat

**Source:** FACTS Grounding (Google DeepMind, 2025), GaRAGe (Amazon, ACL 2025), DEER (deep research report evaluation), plus citation-faithfulness work reporting that up to 57% of LLM-generated citations are post-rationalized rather than genuinely grounded in source material.

**The finding:** Two distinct pieces worth recording briefly:

**(A) Phase 4 validation tools.** The LLM community has produced several validated benchmarks specifically for evidence-grounding behavior that map closely onto our Concept 15 (Evidence Grounding). FACTS Grounding in particular (1,719 examples requiring long-form responses grounded in provided context documents) is a strong candidate for validating an extracted Evidence Grounding vector. GaRAGe offers 2,366 questions with 35,000+ annotated passages for RAG-style evaluation. DEER is more specialized (deep research reports, 50 tasks × 13 domains × 25 sub-dimensions). These are deferred Phase 4 resources; we do not need to commit to one now.

**(B) The 57% post-rationalization figure.** Citation-faithfulness work reports that up to 57% of citations produced by LLMs are post-rationalized — generated to support a pre-determined claim rather than genuinely retrieved from the source material. This is the same phenomenon as F43's rationalization finding, extended to citation behavior specifically. For us: a successfully extracted Evidence Grounding vector might steer the model toward *more* citations without making those citations more faithful, which is the same failure mode as F43 but localized to this concept.

**Why this matters for us:** Phase 4-adjacent, so not actionable for current research cycles. Recorded because (a) these benchmarks are the obvious candidates for Evidence Grounding validation when we get to Phase 4, and (b) the 57% figure is striking and worth having on hand when we write up the dispositional/rationalization caveat.

**Applies to:** Phase 4 benchmark selection for Evidence Grounding (deferred). No concept change. No project change.

---

## F47 — ML "calibration" (temperature scaling, ECE) measures a different thing than our Calibrated Confidence concept; don't confuse them in Phase 4 validation

**Source:** ML calibration literature on Expected Calibration Error (ECE), temperature scaling, and the aleatoric/epistemic uncertainty distinction. ICLR 2025 blogpost on calibration; Guo et al. on temperature scaling.

**The finding:** The ML term "calibration" and our "Calibrated Confidence" concept sound similar but measure different things:

- **ML calibration:** the alignment between a model's *softmax output probabilities* and its empirical accuracy. Measured by Expected Calibration Error (ECE), fixable by post-hoc methods like temperature scaling. Operates on token-level probability distributions, not on natural-language expressions of confidence.
- **Our Calibrated Confidence (Concept 9):** the alignment between *expressed confidence language in text* ("I'm certain," "I think," "probably") and the underlying evidence strength. Operates on natural-language surface behavior, not on softmax probabilities.

These are loosely correlated but dissociable. A model can have low ECE (well-calibrated probability distributions) while producing text that sounds overconfident or underconfident. Conversely, a model can produce appropriately hedged language while having miscalibrated underlying probabilities. Temperature scaling fixes the former but does nothing for the latter — and our corpus targets the latter.

**Why this matters for us:** When Phase 4 validation arrives, we must not mistakenly use ECE as a validation metric for the extracted Calibrated Confidence vector. ECE measures whether the model's probability outputs are calibrated; we care whether the model's *language* is calibrated to evidence strength. These need separate validation approaches. A steered-model evaluation that reports ECE improvements would not establish what we are trying to establish.

**What this means operationally:** Our Phase 4 validation for Calibrated Confidence should probably measure things like hedging-word frequency relative to task difficulty, explicit probability-language usage on claims of varying evidential support, or rater judgments of confidence-evidence alignment on generated text. Not ECE.

**Concepts.md change applied:** Added a clarification to Concept 9's description distinguishing our epistemic/linguistic calibration from the ML-technical sense of calibration. Small honesty fix to prevent future confusion.

**Applies to:** Concept 9 refinement (applied); Phase 4 validation design (deferred — don't use ECE for this vector).

---

## F48 — Motivated reasoning is distinct from confirmation bias in psychology; our Concept 7's evidence-weighing sub-facet already covers it, but the distinction is worth naming

**Source:** Psychology literature distinguishing confirmation bias (attention/noticing asymmetry) from motivated reasoning (evaluation asymmetry driven by desire for a preferred conclusion).

**The finding:** The two constructs are often used interchangeably in casual discourse but are formally distinct:

- **Confirmation bias:** the implicit tendency to notice information that coincides with preexisting beliefs and ignore information that doesn't. Primarily an attention/perception asymmetry.
- **Motivated reasoning:** readily accepting information that agrees with one's worldview and critically analyzing information that disagrees. Primarily an evaluation asymmetry driven by goal-directed processing.

Our Concept 7 (Confirmation Bias Awareness) has three sub-facets: information search, evidence weighing, and noticing selective processing. Sub-facet 2 (evidence weighing — "subjecting one's preferred hypothesis to the same critical scrutiny as competing ones") is actually the motivated-reasoning dimension, just not labeled as such.

**Why this matters for us:** This is a naming/grounding refinement, not a structural change. The relevant behavior is already covered. But the concept description should acknowledge that it subsumes both constructs so that Phase 3 corpus writers and Phase 4 interpreters understand the scope clearly. Also: the psychology literature on motivated reasoning has standard experimental paradigms (randomly assigning participants to receive congruent vs. incongruent evidence and measuring asymmetric evaluation) that could inform Phase 3 fact-pack design for this concept.

**Concepts.md change applied:** Added a short note to Concept 7's description naming motivated reasoning explicitly as part of what the evidence-weighing sub-facet targets.

**Applies to:** Concept 7 refinement (applied). Phase 3 fact-pack generation for this concept can draw on motivated-reasoning experimental paradigms (congruent/incongruent evidence manipulation) for scenario design.

---

## F49 — LiveIdeaBench is a Phase 4 validation candidate for Hypothesis Generation using the fluency/flexibility dimensions from F26

**Source:** LiveIdeaBench (Ruan et al., 2024/2025), *Evaluating LLMs' Divergent Thinking Capabilities for Scientific Idea Generation with Minimal Context*, Nature Communications 2026.

**The finding:** LiveIdeaBench is a comprehensive benchmark for LLM divergent thinking applied to scientific idea generation. It uses single-keyword prompts spanning 1,180 keywords across 22 scientific domains and evaluates generated ideas across five Guilford-style dimensions: originality, feasibility, fluency, flexibility, and clarity. It was tested on 40+ leading models.

**Why this matters for us:** Directly relevant to Concept 2 (Hypothesis Generation). F26 grounded Concept 2 in the fluency/flexibility distinction from Guilford's divergent-thinking tradition; LiveIdeaBench is the LLM-specific operationalization of that framework. It is a strong Phase 4 validation candidate for an extracted Hypothesis Generation vector. If steering the vector improves LiveIdeaBench fluency and flexibility scores (especially flexibility — structurally distinct alternatives) while leaving originality/clarity unchanged, that would be clean dispositional evidence of the kind F45 says we should expect from successful steering.

**Side note — benchmark accumulation:** We now have Phase 4 validation candidates for three concepts: FACTS Grounding/GaRAGe (Evidence Grounding, F46), MASK (Intellectual Honesty, F15), LiveIdeaBench (Hypothesis Generation, F49). When Phase 4 arrives, this benchmark list should be consolidated into a single validation plan.

**Applies to:** Phase 4 benchmark selection for Hypothesis Generation (deferred). No concept change. No project change.

---

## F50 — Kruglanski's Need for Cognitive Closure is the standard psychology opposing construct for Comfort with Ambiguity

**Source:** Webster & Kruglanski (1994) Need for Closure Scale (NFCS), 42 items, five-facet structure; subsequently analyzed as having two orthogonal factors (decisiveness and need for structure).

**The finding:** Need for Cognitive Closure (NCC) is defined as "the desire for an answer on a given topic, any answer … compared to confusion and ambiguity." The Kruglanski scale decomposes it into five facets: desire for predictability, preference for order and structure, discomfort with ambiguity, decisiveness, and close-mindedness. Empirically, two orthogonal factors emerge — decisiveness (wanting to reach a conclusion fast) and need for structure (wanting the world to be organized). Correlations with Tolerance for Ambiguity Scale are strongly negative (r = −.57), confirming the constructs are closely related but distinct.

NCC is the standard opposing construct for our Concept 11 (Comfort with Ambiguity). Our concept is essentially the inverse of high NCC, focused specifically on the epistemic/reasoning manifestation.

**Why this matters for us:** Primarily a grounding refinement. F20 already cited IUS-12 for the ambiguity-tolerance literature, but NFC is the more canonical construct for our specific angle (dispositional comfort with holding unresolved questions open). Adding it to Concept 11 gives a stronger literature anchor and points at the two-factor structure as something to watch for. Our current sub-facets (holding questions open, holding multiple interpretations, resisting forced closure) all cluster on the "need for structure" side of NFC; we do not explicitly address the "decisiveness" side (wanting to reach an answer quickly regardless of evidence). The decisiveness dimension is the one we skipped in F20 when I decided not to add the actional sub-facet. This is the same tradeoff, now with a second empirical backing.

**Concepts.md change applied:** Added a citation to NFCS (Webster & Kruglanski, 1994) in Concept 11's description with a note that our concept targets the need-for-structure axis of the construct and does not address the decisiveness axis (which is handled elsewhere or is outside our extraction scope per F20).

**Applies to:** Concept 11 refinement, applied directly.

---

## F51 — Authority Independence should be reflective autonomy, not reactive autonomy; critical distinction from recent empirical work

**Source:** Worsnip, Lane, Pratt, Napolitano, Gray, & Greene (2025), *Authority or Autonomy? Philosophical and Psychological Perspectives on Deference to Experts*, Philosophical Psychology; building on Koestner and colleagues' work on reflective vs. reactive autonomy.

**The finding:** The epistemic-autonomy literature distinguishes two fundamentally different conceptions of autonomy:

- **Reactive autonomy:** autonomy as freedom from external influence. On this view, any deference to experts is *by definition* non-autonomous. Empirically, reactive autonomy predicts *ignoring* expert advice even when the advice is warranted.
- **Reflective autonomy:** autonomy as decisions guided by one's own values and reasoning. On this view, deferring to experts *can* be autonomous if the decision to defer is itself made reflectively. Empirically, reflective autonomy predicts *following* expert advice *when warranted*.

The empirical finding (Koestner et al.) is striking: the two conceptions of autonomy have *opposite* relationships with expert-advice-following behavior. Reflective autonomy is associated with appropriate deference; reactive autonomy is associated with contrarian rejection regardless of merit.

**Why this matters for us — and why Concept 13 needs sharpening:**

Our Concept 13 (Authority Independence) currently reads as follows (paraphrased): "The reasoner evaluates claims on the evidence behind them rather than on the prestige of their source, and is willing to reach and hold conclusions that disagree with established figures when the evidence warrants."

This framing is closer to reactive autonomy than reflective autonomy. It emphasizes *willingness to disagree* as the defining behavior. But per the empirical literature, what we actually want from an epistemic virtue is reflective autonomy — the *capacity to critically evaluate evidence and decide when deference is warranted and when dissent is warranted*, based on the evidence itself rather than on the source status. A reflectively autonomous reasoner sometimes defers to experts because the evidence supports doing so, and sometimes disagrees because the evidence warrants it. Both behaviors are virtuous.

This is a real sharpening, not just a wording change. A Concept 13 vector extracted from passages that mostly show "disagreeing with authority" will capture contrarian reasoning, not epistemic autonomy. If we steer along such a vector, we might make the model more contrarian (reactive autonomy) rather than more appropriately deferential (reflective autonomy). That's the wrong direction.

**Concepts.md change applied:** Rewrote Concept 13's description to explicitly frame it as *reflective autonomy* — evaluating claims on evidence, appropriately deferring when the evidence supports deference, appropriately dissenting when the evidence supports dissent, with the *reasoning from evidence* being the defining move rather than the disagreement itself. Added a fifth sub-facet (bringing Concept 13 to 4 sub-facets total, still within cap) covering the "appropriate deference" side that was implicit but unspoken in the previous version.

**Critical for Phase 2 corpus design:** When we write generation-guidelines.md and create fact packs for Concept 13, the *virtuous* version must include passages where the reasoner evaluates expert claims and concludes that the experts are right on the evidence (appropriate deference), not only passages where the reasoner disagrees with experts. If 100% of virtuous Concept 13 passages are disagreements, the extracted vector is contrarian, not autonomous. A rough target: maybe 40–60% disagreement and 40–60% appropriate-deference passages, ensuring both sides of reflective autonomy are in the training data. This is a Phase 3 corpus-design implication that needs to be captured in generation-guidelines.md when it's drafted.

**Applies to:** Concept 13 refinement (applied). Phase 3 generation-guidelines.md corpus design for Concept 13 must enforce the reflective-autonomy balance. Phase 4 validation should check whether the extracted vector correlates with appropriate deference OR with contrarian disagreement.

---

## F52 — Cognitive Reflection Test (Frederick 2005) is a strong Phase 4 validation candidate for Metacognitive Awareness and Calibrated Confidence

**Source:** Frederick (2005), *Cognitive Reflection and Decision Making*, Journal of Economic Perspectives.

**The finding:** The Cognitive Reflection Test (CRT) is a three-item test designed to measure the disposition to *suppress* an impulsive (System 1) wrong answer and engage in deliberate (System 2) reflection to reach the correct answer. Each item has an intuitive-but-wrong answer and a correct answer that requires explicit reflection. Key reported properties:

- CRT is a "more potent predictor of performance on heuristics-and-biases tasks than measures of cognitive ability, thinking dispositions, or executive functioning."
- It measures "the ability or disposition to reflect on a question and resist reporting the first response that comes to mind."
- It correlates with rational thinking, open-minded thinking, and numeracy but is distinct from pure cognitive ability.

**Why this matters for us:** The CRT is an excellent Phase 4 validation instrument for Metacognitive Awareness (the disposition to catch oneself jumping to conclusions) and, secondarily, for Calibrated Confidence (since the impulsive-wrong-answer behavior includes unwarranted confidence in the first answer that comes to mind). If we steer along one of these extracted vectors and CRT performance improves, that is strong evidence that the steering is moving a genuine dispositional target, not just cosmetic style. If CRT performance is flat, that is evidence of the style-only failure mode flagged in F43.

**Side note — benchmark accumulation continues:** Phase 4 validation candidates now exist for four concepts:
- FACTS Grounding / GaRAGe (Evidence Grounding, F46)
- MASK (Intellectual Honesty, F15)
- LiveIdeaBench (Hypothesis Generation, F49)
- CRT (Metacognitive Awareness and/or Calibrated Confidence, F52)

The remaining 11 concepts still lack clear validation benchmarks. Not all of them will need one — some can share benchmarks — but this gap should be tracked.

**Applies to:** Phase 4 benchmark selection (deferred). No concept change. No project change.

---

## F53 — Litman's interest-type vs. deprivation-type epistemic curiosity distinction; our Concept 1 already covers both

**Source:** Litman & Spielberger (2003), *Measuring Epistemic Curiosity and Its Diversive and Specific Components*, Journal of Personality Assessment. Subsequent work on interest-type (I-EC) and deprivation-type (D-EC) epistemic curiosity.

**The finding:** Psychology decomposes epistemic curiosity into two distinct empirical types:

- **Interest-type (I-EC):** curiosity driven by positive affect and diversive exploration — "I want to know because it's interesting and fun to think about." Associated with mastery-oriented learning and exploring new ideas for their own sake.
- **Deprivation-type (D-EC):** curiosity driven by the aversive feeling of *not* knowing something — "I want to know because there is a gap in my understanding and I need to close it." Associated with performance-oriented learning and filling specific knowledge gaps.

These two types are correlated but distinct, and have different downstream behaviors. A reasoner can be high on one and low on the other.

**Why this matters for us:** Our Concept 1 (Genuine Curiosity) was grounded in Need for Cognition (F17) but not further decomposed. Looking at the current sub-facets:

- "Asking questions to understand rather than to confirm" — covers both I and D
- "Following unexpected observations rather than dismissing them" — more D (filling a gap)
- "Interest in *why*, not just *that*" — more I (interest-driven)
- "Taking evident pleasure in the cognitive work itself" — pure I-EC

Our sub-facets span both types even without explicit labeling. This is a good structural property — the extracted vector should capture curiosity broadly rather than one narrow type. No restructuring needed.

**Concepts.md change applied:** Added a brief note to Concept 1's description naming Litman's I-EC / D-EC distinction and clarifying that our sub-facets span both types by construction. This is a grounding refinement for corpus writers who need to know what "curiosity" passages should depict.

**Applies to:** Concept 1 refinement, applied directly.

---

## F54 — Epistemic trust literature (ETMCQ, METI) complements F51 reflective autonomy with a three-factor trust/mistrust/credulity structure

**Source:** Epistemic Trust, Mistrust and Credulity Questionnaire (ETMCQ, Campbell et al. and revised version 2024–2025); Muenster Epistemic Trustworthiness Inventory (METI, Hendriks et al. 2015).

**The finding:** Psychology has a validated three-factor structure for epistemic trust:

- **Epistemic trust:** calibrated, selective, balanced receptivity to social learning. Willing to accept information when warranted.
- **Epistemic mistrust:** perceiving sources as untrustworthy by default, remaining impermeable to influence regardless of merit.
- **Epistemic credulity:** decreased vigilance and discrimination, accepting information without adequate checking — prone to misinformation.

METI specifically assesses epistemic trustworthiness on three dimensions: expertise, integrity, and benevolence. It distinguishes *credibility* (which is about persuasive quality) from *trustworthiness* (which is about whether a source should actually be believed) — an important theoretical distinction.

**Why this matters for us:** This is the trust-side complement to F51's reflective autonomy framing of Concept 13. F51 said Authority Independence should be reflective autonomy (reasoning-based, supports deference when warranted), not reactive autonomy (contrarian-by-reflex). ETMCQ adds the symmetric failure mode on the other side: *credulity*. The virtuous reasoner avoids both reactive mistrust (dismissing expert input regardless of merit) AND credulity (accepting information without checking). Both failure modes exist in the psychology literature and both are distinct from the virtuous middle.

Concept 13's current description (post-F51) already implies the credulity failure mode by framing the concept as "reasoning from evidence" rather than "disagreeing with experts," but it doesn't name credulity explicitly. Adding a brief note strengthens the framing.

**Concepts.md change applied:** Added a brief note to Concept 13's description mentioning that the virtuous reasoner avoids both reactive mistrust AND epistemic credulity — the two failure modes flanking the reflective-autonomy middle. This is a minor grounding refinement that doesn't change the sub-facets.

**Applies to:** Concept 13 refinement, applied directly.

---

## F55 — 2026 reasoning-steering work directly validates multiple Phronesis concepts as extractable linear directions

**Source:** *Understanding Reasoning in Thinking Language Models via Steering Vectors* (arXiv 2506.18167, 2025/2026) and related 2026 work on reasoning-behavior steering in DeepSeek-R1-Distill and similar thinking LLMs. Also: SAE-Steering work on controlling reasoning strategies.

**The finding:** Very recent (2025–2026) empirical work has identified specific reasoning behaviors that are mediated by linear directions in activation space and can be extracted and steered. Direct quotes from the literature:

- *"identifying behaviors like expressing uncertainty, generating examples for hypothesis validation, and backtracking in reasoning chains, demonstrating these are mediated by linear directions in activation space."*
- *"SAE-Steering for controlling reasoning strategies like backtracking and cross-verification, moving beyond surface-level behavioral control."*
- *"Middle layers (40–60%) sometimes work for reasoning-adjacent behaviors, with uncertainty expression, hedging, and technical depth emerging at these layers."*

**Why this is load-bearing for Phronesis:** The specific reasoning behaviors named in this literature map directly onto multiple concepts in our taxonomy:

| Behavior identified in 2026 work | Phronesis concept |
|---|---|
| Expressing uncertainty / hedging | Calibrated Confidence (#9) + Intellectual Humility (#6) |
| Generating examples for hypothesis validation | Hypothesis Generation (#2) + Evidence Grounding (#15) |
| Backtracking in reasoning chains | Metacognitive Awareness (#8) |
| Cross-verification | Confirmation Bias Awareness (#7) + Evidence Grounding (#15) |

This is direct empirical validation that the dispositions Phronesis targets exist as extractable linear directions in 2026 open-weight reasoning-trained models. F43 showed correctness was extractable; F45 showed dispositional concepts generally are steerable; F55 specifically names *reasoning-disposition* behaviors as extracted and steerable. This is the most concept-specific validation we have found so far.

**Important caveat:** The cited work operates on *thinking* LLMs (DeepSeek-R1-Distill and similar reasoning-trained models). Our target (Gemma 4 E4B) is a standard instruction-tuned model, not a reasoning-trained one. The cited results may not transfer directly — reasoning-trained models have more explicit backtracking and cross-verification in their pretraining distribution, which may mean those behaviors are *more* cleanly extractable there than in a standard model like Gemma 4. This is a known scale/architecture dependency that we have already flagged in F11 and F14. The existence proof is strong but the transfer to our specific model is not guaranteed.

**What this updates in our outlook:** This finding combined with F43, F45, and F33 brings the total external validation picture to:

1. (F43) Reasoning quality is a linear direction; steering flips behavior with rationalization caveat.
2. (F45) Activation steering is a dispositional modulator, not a propositional injector; our concepts are dispositional.
3. (F55) Specific reasoning dispositions matching our concepts (uncertainty, hypothesis validation, backtracking, cross-verification) are empirically extractable in recent work.
4. (F33) What we will extract is closer to "legibility" than "faithfulness"; steered behavior changes are in the output domain, not necessarily the internal-reasoning domain.

Together these constitute strong convergent evidence for project feasibility at the "does the methodology work in principle" level. The remaining open question is whether it transfers to Gemma 4 E4B specifically.

**No concepts.md change** — this is outlook validation, not taxonomy refinement. The mapping table above is informally useful as a reference when Phase 3 and Phase 4 come around.

**Applies to:** Overall project outlook (positive update), Phase 4 benchmark selection (the reasoning-behavior vocabulary from this literature gives us explicit targets to validate against), and the eventual writeup (these are the most recent and most relevant prior-art papers to cite as direct precedent for the extraction step).

---

## F56 — Bullshit Receptivity Scale is a cross-cutting Phase 4 validation candidate; the "reflective vs. reflexive open-mindedness" distinction reinforces F54

**Source:** Pennycook, Cheyne, Barr, Koehler, & Fugelsang (2015), *On the Reception and Detection of Pseudo-Profound Bullshit*, Judgment and Decision Making. Also: the original Bullshit Receptivity (BSR) scale and subsequent work on corporate-bullshit receptivity.

**The finding:** The Bullshit Receptivity Scale (BSR) measures the tendency to judge vague, pretentious, or meaningless statements as profound or truthful. It uses pseudo-profound statements constructed from randomly combined buzzwords into syntactically correct but semantically vacuous sentences (e.g. "Hidden meaning transforms the unparalleled beauty of the abstract design"). Key empirical properties:

- BSR has good internal consistency and measures a *specific* susceptibility to pseudo-profundity, not generalized gullibility.
- BSR is inversely related to measures of reflective reasoning and the Cognitive Reflection Test (F52).
- The literature distinguishes **reflective open-mindedness** (info-searching, critical analysis — guards against BSR) from **reflexive open-mindedness** (intuitive acceptance without processing — causes high BSR).

**Why this matters for us:**

**(A) Phase 4 validation candidate.** BSR is a clean, operationalized measure of the opposite of several of our concepts simultaneously: Evidence Grounding (grounded claims shouldn't be vacuous), Calibrated Confidence (unjustified confidence in meaningless statements is the BSR pattern), and Logical Rigor (BSR statements fail semantic rigor checks). Steering any of these vectors should reduce BSR scores. It is a strong candidate for cross-concept Phase 4 validation: if multiple virtue vectors all measurably reduce BSR, we have convergent evidence that they are capturing genuine epistemic dispositions rather than orthogonal style changes. If only one does, we have interesting specificity information.

**(B) The reflective/reflexive distinction is another instance of a pattern we have now seen four times** — F51 (reflective vs. reactive autonomy), F54 (reflective trust vs. credulity), and now F56 (reflective vs. reflexive open-mindedness). The common structure: each epistemic virtue has two symmetric failure modes, one of which is refusing to engage (mistrust, rejection, reactive autonomy) and one of which is engaging without processing (credulity, reflexive acceptance, contrarian certainty). The virtue lives in the middle, defined by *reasoning from evidence* regardless of direction. This is a generalizable framing that Phase 3 generation-guidelines.md should encode: virtuous passages must depict *both* kinds of failure and the middle, not just one extreme.

**Concepts.md change applied:** Added a brief note to Concept 15 (Evidence Grounding) mentioning BSR as inversely correlated with the targeted disposition. Not changing the sub-facets — BSR is a validation candidate, not a definitional source.

**Applies to:** Concept 15 refinement (minor, applied). Phase 4 cross-concept validation (deferred — BSR is a particularly good candidate because it touches multiple concepts at once). Phase 3 generation-guidelines.md should consider the two-failure-modes pattern as a general principle across concepts.

---

## F57 — California Critical Thinking Disposition Inventory (CCTDI) provides convergent validation of our taxonomy

**Source:** Facione, Sánchez, & Facione (1994), *Critical Thinking Disposition as a Measure of Competent Clinical Judgment: The Development of the California Critical Thinking Disposition Inventory* (CCTDI).

**The finding:** CCTDI is a widely-used validated instrument that identifies *seven* critical thinking dispositions: open-mindedness, analyticity, cognitive maturity, truth-seeking, systematicity, inquisitiveness, and self-confidence. Six of the seven overlap meaningfully with Phronesis concepts:

| CCTDI disposition | Phronesis concept |
|---|---|
| Open-mindedness | parts of Authority Independence, Confirmation Bias Awareness |
| Analyticity | Logical Rigor |
| Cognitive maturity | Intellectual Humility |
| Truth-seeking | Intellectual Honesty |
| Systematicity | Reasoning Transparency, parts of Logical Rigor |
| Inquisitiveness | Genuine Curiosity |
| Self-confidence in critical thinking | (no match — we do not target meta-confidence in one's own thinking) |

**Why this matters for us:** Convergent validation from a different research tradition. Our taxonomy independently arrives at most of the same categories CCTDI identified. The one CCTDI disposition we don't cover (self-confidence in one's own critical thinking ability) is reasonable to exclude — it is a meta-disposition about the reasoner's self-perception rather than about the reasoning itself, and we explicitly noted in the "Stage 6 ambiguity" risk that we target producing behaviors rather than meta-evaluating them.

**Important additional finding:** The critical-thinking disposition literature explicitly distinguishes dispositions from abilities, and notes that "dispositions do not necessarily translate into high-quality reasoning in concrete contexts, particularly when issues are emotionally or ideologically charged." This is a third convergent warning for the F44-style failure mode: virtue representations can exist without driving downstream behavior. We should plan for the possibility that extracted vectors are dispositions that don't steer outcomes, and treat that as an informative negative result rather than a project failure.

**Applies to:** Convergent validation of the taxonomy. No concepts.md change needed — we already cover six of the seven CCTDI dispositions. The seventh (self-confidence in one's thinking) is correctly excluded per our scope.

---

## F58 — Cognitive flexibility is empirically weakly associated with AOT/open-mindedness; confirms our implicit decision not to include it as a concept

**Source:** 2024 review of cognitive flexibility measurement (*Measuring Cognitive Flexibility: A Brief Review*, Frontiers in Human Neuroscience). Cognitive Flexibility Scale (Martin & Rubin), Cognitive Flexibility Inventory (CFI), Flexibility in Daily Life scale (FIDL).

**The finding:** Cognitive flexibility is a measured psychological construct distinct from AOT/open-mindedness. It is defined as the capacity to shift or switch thinking and attention between different tasks or operations in response to changing rules or demands. Multiple validated scales exist (CFS, CFI, FIDL). The 2024 review notes directly that "more and more evidence is showing that these measures are only weakly associated or not even associated with each other" — referring to cognitive flexibility measures and AOT/open-mindedness measures. The two constructs should not be used as proxies for one another.

**Why this matters for us:** This is a *null result* that confirms an implicit decision in our taxonomy. Phronesis does not include "cognitive flexibility" as a concept. This was never formally considered as a candidate (it didn't come up in the Phase 1 design discussion), but F58 confirms that the omission is defensible — cognitive flexibility is empirically distinct from the open-mindedness / AOT cluster our taxonomy targets, and from the reasoning-discipline cluster as well. It is more about task-switching and attention control than about epistemic disposition. Adding it as a concept would mean introducing an orthogonal construct that doesn't fit our stage structure, and there is no empirical reason to believe it would be extractable as a linear direction in the same sense as our dispositional concepts.

**Applies to:** Taxonomy scope confirmation. No concepts.md change. Useful as a pre-emptive answer if anyone later asks "why doesn't Phronesis include cognitive flexibility?"

---

## F59 — The two-failure-modes pattern is Aristotle's golden mean; formalizing it gives us a general design principle for concepts and generation

**Source:** Aristotle's Nicomachean Ethics, Book II; contemporary virtue ethics including Linda Zagzebski, *Virtues of the Mind* (1996) and her *Exemplarist Moral Theory*. Stanford Encyclopedia of Philosophy entries on virtue epistemology and Aristotle's ethics.

**The finding:** The pattern we identified in F56 — that each epistemic virtue has two symmetric failure modes flanking a reasoning-from-evidence middle (reactive autonomy vs. credulity; reflective vs. reflexive open-mindedness; mistrust vs. over-acceptance) — is the Aristotelian doctrine of the *golden mean*, formalized in virtue ethics for over two thousand years.

Aristotle's claim: *"every ethical virtue lies between two extremes — one of excess and one of deficiency, and the virtuous person finds the appropriate middle ground between these extremes."* Contemporary virtue epistemology (Zagzebski 1996, *Virtues of the Mind*) extends this to intellectual virtues, arguing that virtue epistemology should not be purely reliabilist and should identify virtues by their *structure* (excess–mean–deficiency) as much as by their outcomes. Zagzebski further argues that intellectual virtues are grounded in practical wisdom (phronesis — not coincidentally, the name of this project).

**Why this matters for us — formalize the pattern as a design principle:**

We have already documented four instances of this structure empirically (F51, F54, F56, plus the original informal observation). Rather than continuing to rediscover it one concept at a time, we should promote it to a *design principle* for the concept taxonomy and use it as a check on every concept. For each concept, ask:

1. What is the virtue (the reasoning-from-evidence middle)?
2. What is the excess failure mode? (usually: rigid, inflexible, over-committed)
3. What is the deficiency failure mode? (usually: permissive, uncritical, under-committed)

Concepts that can be cleanly framed in this structure are better-grounded. Concepts that resist the framing may be genuinely one-sided (e.g., Logical Rigor — there is no virtuous "not enough rigor") or may indicate the concept is poorly specified.

Running the check on our current 15 concepts:

| Concept | Deficiency (too little) | Excess (too much) |
|---|---|---|
| 1. Curiosity | incuriosity, dogmatism | compulsive distractibility (F17 NFC excess) |
| 2. Hypothesis Generation | fixation on one explanation | ungrounded speculation / idea-fluency without quality |
| 3. Logical Rigor | sloppy inference | paralysis via over-formalization |
| 4. Causal Reasoning | correlation=causation errors | over-attribution of causal structure |
| 5. Quantitative Groundedness | qualitative hand-waving | fetishizing precision without meaning |
| 6. Intellectual Humility | overconfidence, arrogance | servility, epistemic cowardice |
| 7. Confirmation Bias Awareness | biased evidence weighing | excessive skepticism of one's own views |
| 8. Metacognitive Awareness | unreflective action | rumination, paralysis |
| 9. Calibrated Confidence | overconfidence or underconfidence (two-sided by definition) | — |
| 10. Intellectual Honesty | cherry-picking, misrepresentation | compulsive over-disclosure |
| 11. Comfort with Ambiguity | forced premature closure | indecision, failure to conclude |
| 12. Steelmanning | strawmanning opponents | credulous acceptance of weak arguments |
| 13. Authority Independence | reactive mistrust OR credulity (already two-sided per F54) | — |
| 14. Reasoning Transparency | opacity, hiding work | over-explanation, reasoning theater |
| 15. Evidence Grounding | unsupported assertion | pedantic citation without claim |

The pattern fits every concept cleanly. Two concepts (9 and 13) are already explicitly two-sided in their definitions. Most of the rest have implicit two-sided structure that we have not been naming explicitly. Applying this framing consistently across concepts.md would tighten the taxonomy.

**Concepts.md change applied:** Added the golden-mean pattern as a new design principle in the "Design principles" section of concepts.md, explaining the excess/mean/deficiency structure and noting that it should inform how Phase 3 corpus generation constructs contrastive passages (the *non-virtuous* end of our contrastive pairs should include both-excess AND deficiency failure modes, not just one extreme). This is a meta-principle that affects the full taxonomy; applied as a design-principle addition rather than as per-concept edits because the information is best presented centrally.

**Critical implication for Phase 3 generation-guidelines.md:** When we draft the guidelines, the non-virtuous rewrite step must explicitly rotate between excess and deficiency failures across the corpus. If all non-virtuous passages for (say) Intellectual Humility depict arrogance (the excess failure), the extracted vector will encode humility-vs-arrogance rather than true humility. If some depict servility (the deficiency failure), the vector captures the actual middle. This is a corpus-design constraint we need to bake in from the start.

**Applies to:** concepts.md design principles (applied); Phase 3 generation-guidelines.md (critical constraint noted for when drafting begins); taxonomic grounding (philosophical).

---

## F60 — Steering vector cross-model transfer literature substantially reduces the F55 caveat weight for Gemma-family models

**Source:** Recent work on cross-model steering vector transfer, including "Steering Vector Transfer via Orthonormal Transformations and Semantic Pairing" (OpenReview 2025), ICML 2024 analysis of steering vector generalization, and Platonic Representation Hypothesis evidence from Gemma-7B / LLaMA-3-8B / Mistral-7B comparisons.

**The finding:** The most important single quote from the literature: *"Steering vectors constructed on instruction-tuned Gemma 2 IT transfer effectively to base Gemma 2, improving instruction-following by ~20% over baseline; similar gains reported for Llama-family."* Additional findings:

- Cross-architecture transfer via orthonormal transformations achieves 0.50–0.56 cosine similarity across model pairs.
- Semantic pairing during training improves transfer by 72%.
- The Platonic Representation Hypothesis — different language models encode behavioral preferences in similar geometric structures — has direct empirical support from comparisons across three architecturally distinct models.
- Linear and nonlinear concept directions generalize across languages (English, Spanish, German, Mandarin) and to multimodal tasks.

**Why this matters for us:** Directly addresses the F55 caveat. F55 showed that reasoning-behavior steering vectors had been extracted in DeepSeek-R1-Distill (a reasoning-trained model), and flagged that transfer to our target (Gemma 4 E4B, a standard instruction-tuned model) was not guaranteed. F60 provides specific evidence that:

1. **Within-Gemma transfer works.** Gemma 2 IT → Gemma 2 base transfers with ~20% improvement in instruction following. Our target is in the same model family, and the empirical cross-version transfer is demonstrated.
2. **Cross-family transfer exists at meaningful magnitude.** 0.50–0.56 cosine similarity between steering vectors across different model families is not perfect alignment but is well above chance, and the 72% improvement from semantic pairing shows the number can be pushed higher with care.
3. **The Platonic Representation Hypothesis has empirical support.** Different models converge on similar geometric structures for behavioral traits, which means our virtue vectors extracted on Gemma 4 E4B should correspond to similar latent directions that other published work has found.

The F55 caveat is not eliminated — transfer across reasoning-trained vs. standard models specifically has not been directly tested in the literature I found — but its weight is substantially reduced. We should expect our Gemma 4 E4B extraction to be in the same general geometric territory as the published reasoning-behavior vectors, with some family-specific differences that may need small transformations but not fundamental re-extraction.

**Implication for project outlook:** This is another positive update for feasibility. Combined with F43, F45, F55, and now F60, the external validation picture is:

- (F43) Reasoning quality is a linear direction; steering flips behavior.
- (F45) Steering is dispositional, not propositional; our concepts are in the right category.
- (F55) Specific reasoning dispositions (uncertainty, hypothesis validation, backtracking, cross-verification) are extracted in recent work.
- (F60) Steering vectors transfer across model families with meaningful alignment; Gemma-family internal transfer works at ~20% improvement.

The remaining feasibility unknowns are narrower: does the specific contrastive-triplet corpus design work at our scale, and do the harder concepts (low-likelihood tier in F11) extract at all.

**No concepts.md change** — project outlook update, not taxonomy refinement.

**Applies to:** Project outlook. No concept or project edits. The F55 caveat section of that finding should be treated as partially resolved — noting it here rather than editing F55 directly to preserve the historical record.

---

## F61 — Stanovich's CART (Comprehensive Assessment of Rational Thinking) is a potential unified Phase 4 validation instrument spanning multiple concepts

**Source:** Stanovich, West, & Toplak (2016), *The Rationality Quotient: Toward a Test of Rational Thinking*, MIT Press. Also: Stanovich's 2013 Thorndike Award Address on CART structure.

**The finding:** CART is the first prototype for a comprehensive rationality assessment analogous to IQ tests. It comprises **20 subtests** organized around:

- **Instrumental rationality:** whether one uses resources in alignment with one's goals.
- **Epistemic rationality:** how well one's beliefs map onto the actual structure of the world.
- **Critical knowledge bases:** numeracy, financial literacy, risk knowledge.
- **Contaminated mindware:** measuring acquisition of problematic beliefs (superstitions, anti-science, conspiracy theories).
- **Miserly information processing:** cognitive laziness and shortcut use.

Key conceptual point: CART explicitly distinguishes rationality from intelligence, arguing they are "two different things conceptually and empirically" and that "people can be, at the same time, intelligent and irrational."

**Why this matters for us — CART as a unified Phase 4 validation candidate:** CART is structured to measure dispositions and behaviors that overlap heavily with our taxonomy. Several CART subtests target constructs we target:

- Numeracy → Quantitative Groundedness (F23 already established the dispositional vs. ability distinction)
- Scientific reasoning subtests → Evidence Grounding, Causal Reasoning, Logical Rigor
- AOT subtest (which is part of CART) → Authority Independence, Confirmation Bias Awareness, Intellectual Humility, Comfort with Ambiguity (F39's cluster)
- Resistance to miserly processing → Metacognitive Awareness
- Reflection / CRT subtest → Metacognitive Awareness, Calibrated Confidence

If we steer multiple Phronesis vectors and see corresponding CART subtest improvements, that is convergent validation that cuts across many concepts at once. Cheaper than running separate validation benchmarks for each of the 15 concepts.

**Constraint:** CART is a 20-subtest battery, not a quick benchmark. Running it on a small model would require implementing or adapting the subtests for LLM evaluation, which is nontrivial. Some subtests are already implemented in LLM-eval form (e.g., the AOT items, CRT), but others are not. Phase 4 should probably use CART selectively — pick 4–6 subtests that align with our priority concepts and run those rather than the full battery.

**Side note — CART is Phronesis's empirical parent construct.** What we are trying to do — extract directions in activation space that correspond to rational thinking dispositions and test whether steering them improves task performance — is effectively testing whether Stanovich's rationality construct has a neural implementation in small LLMs. This is a useful framing for the eventual writeup and a good conceptual anchor.

**Applies to:** Phase 4 validation design (deferred — CART as a selective benchmark battery). Project framing (useful for the writeup — Phronesis tests whether the Stanovich rationality construct has an activation-space implementation). No concept change.

---

## F62 — Positive and negative traits may not lie on a single linear axis; this partially critiques F59's golden-mean assumption

**Source:** Activation steering literature reporting asymmetry between positive and negative steering for personality traits. Direct quote from the literature: *"The consistent asymmetry between positive and negative steering suggests that traits like altruism and their opposites may not lie on a single linear axis."*

**The finding:** Empirical work on steering personality traits has found that the positive and negative directions of a trait do not always behave as a single linear axis. Steering toward altruism and steering toward its opposite produce asymmetric effects on model behavior, which is not what one would expect if the two poles were reflections across a single axis in activation space.

This is a direct critique of an assumption baked into F59 (the golden-mean design principle I added last cycle). F59 framed each virtue as a reasoning-from-evidence middle between two failure modes — an excess and a deficiency — and implicitly treated this as a geometric structure in which the three points (deficiency → virtue → excess) sit on a single axis with the virtue as the midpoint. If the literature is right that positive and negative trait expressions don't lie on one axis, then our excess and deficiency failure modes may also be in orthogonal or otherwise non-collinear directions in activation space, not on opposite sides of the same axis.

**Why this matters for Phronesis — and what to actually do about it:**

The philosophical insight of F59 (virtues are means between excess and deficiency) is still correct. Aristotle's observation about the *conceptual* structure of virtue is not invalidated by the *geometric* finding from activation steering. The problem is specifically with the translation from philosophy to activation-space geometry.

Three possible interpretations of F62 combined with F59:

1. **The excess and deficiency failures are geometrically on separate axes, and the virtue is a point (or region) near the origin.** Under this view, we would need to extract two distinct vectors per virtue (an excess vector and a deficiency vector) and the virtue is characterized by *low activation on both*. This is expensive — it doubles the number of vectors per concept — but matches the empirical asymmetry finding.

2. **The positive trait (virtue) is a direction, but the negative (failure modes) is a diffuse region.** Under this view, we extract one vector for each virtue (pointing toward the middle), and the non-virtuous end of our contrastive pairs should sample diffusely across both failure modes rather than trying to construct a single "opposite." The F59 corpus rotation constraint (non-virtuous passages rotate between excess and deficiency) is then serving exactly this function — sampling the diffuse failure region from multiple sides rather than pretending it's a single opposite pole.

3. **F62's asymmetry applies to personality traits (altruism) but not to reasoning dispositions (our concepts).** Reasoning dispositions may have cleaner linear structure because they are more tightly tied to specific text signatures, whereas personality traits are broader. This is empirically testable in Phase 4.

**Which interpretation is right?** We don't know without data. But interpretation 2 is *most consistent with what we have already committed to in F59*. The F59 corpus rotation constraint already samples both failure modes. What changes is the interpretation of what we are extracting: not a single excess–mean–deficiency axis, but a virtue direction with a diffuse anti-direction. Under this reading, our extracted vector will point toward the virtue middle, and steering in the opposite direction may produce *different* failure modes depending on coefficient and context, rather than a clean "opposite virtue."

**Concepts.md change applied:** Added a caveat to the golden-mean design principle in concepts.md noting that the structure is conceptual/philosophical (true at the level of how the virtue is defined) but that the activation-space geometry may not be a single linear axis — per F62. The corpus rotation constraint is preserved (still needed under interpretation 2), but the claim is reframed: we are sampling the diffuse failure region from multiple sides, not constructing a single opposite pole. Phase 4 should empirically test whether excess and deficiency failures lie on separable axes (e.g., by extracting both directions independently for at least one concept and measuring their geometry).

**Applies to:** F59 refinement (applied via concepts.md caveat). Phase 4 experimental protocol — add an explicit test for failure-mode axis separability for at least one concept.

---

## F63 — The dispositional/propositional dichotomy used in F45 is philosophically contested but the ML finding survives the critique

**Source:** Philosophy of knowledge literature on dispositional knowledge-how vs. propositional knowledge-that, including contemporary work arguing that "knowledge-that is a species of dispositional knowledge-how" and that the clean dichotomy is semantically context-dependent rather than a fundamental distinction.

**The finding:** F45 used a sharp dispositional/propositional distinction to frame the scope condition for project success: steering works on dispositional concepts but cannot inject propositional knowledge. The philosophy literature argues this dichotomy is itself contested. Key claims from the literature:

- "Dispositional knowledge-how is a necessary condition for knowledge-that, meaning knowledge-that is a species of dispositional knowledge-how."
- "Whether 'knowing how' refers to dispositional knowledge, propositional knowledge, or a hybrid form depends on the semantic and pragmatic context."
- The clean binary is misleading; there is significant overlap and some scholars argue dispositional knowledge is foundational to propositional knowledge, not separate from it.

**Why this does NOT invalidate F45:** The F45 finding was from ML empirical literature, not philosophy of knowledge. When the activation-steering literature says "steering cannot inject knowledge the model doesn't have," it is making a claim about the *mechanism* of steering (modifying behavioral tendencies via activation addition) and the kinds of outcomes it can produce. It is not making a deep claim about the metaphysical structure of knowledge. The philosophical critique says there is no clean metaphysical dichotomy; the ML finding says there is a clean empirical difference in what steering can and cannot do. These are compatible: the empirical mechanism could be crisp even when the underlying conceptual distinction is fuzzy.

**What this does change:** The project.md scope condition we added in F45 (steering should help on disposition-limited tasks but not knowledge-limited tasks) should be described slightly more carefully. "Dispositional vs. propositional" is a useful shorthand but is not a clean philosophical binary. A better framing might be "tasks where the model has the capability but does not deploy it versus tasks where the model lacks the capability entirely." This avoids the philosophical baggage.

**Concepts.md change:** None.

**project.md change:** None for now. The existing framing is close enough and changing it would introduce more complexity than clarity. Worth revisiting at the writeup stage to avoid overclaiming the philosophical precision of the distinction.

**Applies to:** Writeup precision, eventually. No current action.

---

## F64 — Documented empirical failures of steering on "abstract" behaviors: instruction hierarchy, deception, latent reasoning

**Source:** Activation steering literature reporting specific failure cases. Direct quotes from the literature:

- *"Instruction hierarchy — getting the model to prioritize system instructions over user attempts to override them — was a complete failure, and steering made it worse. Hierarchy isn't a simple behavioral direction."*
- *"Deception may not be encoded in a single, interpretable activation dimension but rather entangled with other linguistic features, and unlike more straightforward stylistic traits, deception involves contextual reasoning, which might require interventions that go beyond simple vector shifts."*
- *"Activation steering for the average difference between latent vectors did not create increases in accuracy with specific latent pair combinations and instead matched closely with random vectors."*
- GPT-2 1.5B reported as insufficient for reasoning-task steering (same finding as F14 but worth re-flagging).

**The finding:** Three classes of behaviors have been documented as failures for activation steering:

1. **Hierarchical behaviors** (instruction hierarchy) — not a simple direction, involves prioritization structure.
2. **Context-dependent reasoning behaviors** (deception) — entangled with other linguistic features, not a single interpretable dimension.
3. **Direct accuracy improvement through latent vector averaging** — average-difference vectors matched random vectors in some experiments.

**Why this matters for us — which of our concepts might fall into these failure categories?**

Running our 15 concepts against these three failure patterns:

- **Hierarchical:** Authority Independence involves hierarchy (expert vs. self) but we are not trying to steer toward a specific ordering. Our concept is about evidence-based evaluation, not about imposing a hierarchy. Probably safe.
- **Context-dependent:** Intellectual Honesty is the most context-dependent concept we have — whether something is "honest" depends on what the reasoner actually knows and whether they are misrepresenting it. Honesty was already flagged as one of the harder concepts in F11 and F14. This finding reinforces that placement. Our diligence sub-facet (F41) may help by making the verification behavior more text-visible, but the concept remains risky.
- **Average-difference failure:** This is our extraction method exactly. It is the difference-of-means approach Anthropic used successfully for emotions and that F43 validated for correctness direction. The reported failure case was on *latent reasoning* tasks specifically, not on dispositional concepts. So our approach is not ruled out, but the report is a reminder that the method can produce random-direction vectors if the contrastive pairs are poorly constructed or the concept is not cleanly represented in the model.

**No concepts.md change.** This finding is diagnostic — it tells us where to watch for failure, not how to refine the taxonomy. Honest assessment: Intellectual Honesty remains the highest-risk concept for Phase 4 extraction, consistent with its placement in F14 and F11.

**Applies to:** Phase 4 risk assessment. Intellectual Honesty should not be the pilot concept; something from the highest-likelihood tier (Calibrated Confidence, Reasoning Transparency, Evidence Grounding, Hypothesis Generation) is safer.

---

## F65 — Steering-induced capability degradation and cross-concept spillover: success criteria need explicit no-degradation checks

**Source:** Multiple recent papers on activation steering side effects. Direct quotes from the literature:

- *"Stronger steering interventions using larger scaling coefficients can more forcefully modulate target behavior but at the expense of general coherence, fluency, or performance in unrelated tasks."*
- *"The relationship between steering magnitude and effectiveness is genuinely non-monotonic across language models, with regimes where increasing alpha decreases the intended effect."*
- *"Unintended entanglement between primary and secondary behaviors is prevalent, with gains on bias or harmful output spuriously increasing sycophancy rates or degrading factual consistency."*
- *"Supposedly 'monosemantic' features often activate on multiple, unrelated contexts or share energy with other directions, leading to non-modular, unintended side effects."*

And critically: a 2026 paper titled *"Steering Externalities: Benign Activation Steering Unintentionally Increases Jailbreak Risk for Large Language Models"* (arXiv:2602.04896) reports that steering toward *benign* target behaviors can inadvertently increase jailbreak vulnerability as a side effect.

**The finding summarized:** Activation steering has four well-documented failure modes beyond simple non-effectiveness:

1. **Coherence/fluency degradation** at stronger steering coefficients.
2. **Non-monotonicity** in the magnitude-vs-effect relationship — more steering can produce worse results.
3. **Cross-concept spillover** — steering one target can degrade unrelated capabilities (factual consistency, sycophancy, etc.).
4. **Safety externalities** — benign steering can increase jailbreak vulnerability.

**Why this matters for us:** This is a sharp challenge to our success criteria. Phronesis's success criterion 2 (intervention success) currently reads "steering along at least one successfully-extracted vector produces a statistically meaningful improvement on a reasoning-sensitive benchmark, with no significant degradation in general capability." The phrase "no significant degradation" is currently vague — F65 tells us exactly what to measure:

- **Coherence/fluency** on unrelated prompts under the same steering coefficient.
- **Factual consistency** on unrelated factual tasks.
- **Sycophancy rates** (a documented entanglement hazard).
- **Safety behaviors** (refusal rates on known-jailbreak prompts) — this one is especially important given the Steering Externalities result.

If our success story is "we improved Calibrated Confidence on a reasoning benchmark" but we silently increased jailbreak vulnerability or damaged factual consistency, we have not succeeded — we have moved a trade-off. Phase 4 validation must explicitly measure these side effects and report them.

**project.md change applied:** Sharpened the success criteria section to enumerate the specific degradation checks that must be run. This is a *precision* refinement, not a goal change — the existing "no significant degradation" language was already there, it just lacked operational content. F65 provides the operational content.

**Concepts.md change:** None.

**Applies to:** project.md success criteria (applied), Phase 4 validation protocol (deferred — must include the four-way degradation check), eventual writeup (results must report degradation metrics alongside improvement metrics).

---

## F66 — Correct-N-Contrast (CNC) provides theoretical grounding for our correctness-confound mitigation strategy

**Source:** Zhang et al. (2022), *Correct-N-Contrast: A Contrastive Approach for Improving Robustness to Spurious Correlations* (arXiv:2203.01517).

**The finding:** CNC directly addresses the concern that motivated our correctness-confound mitigation. From the paper: "A neural network's worst-group accuracy strongly tracks how well its representations exhibit dependence only on ground-truth labels, and not on spurious attributes, with alignment measuring how close samples with the same class but different spurious attributes embed in representation space."

Mapped onto Phronesis: our "ground-truth label" is the virtue (humility, calibration, etc.), and the "spurious attribute" is correctness (whether the reasoner reached the right answer). CNC's insight is that robust representations *must* have samples with the same virtue-label embed close together regardless of their correctness-label. Our mitigation strategy (20–30% of virtuous passages reach wrong conclusions, and by symmetry some non-virtuous passages reach right conclusions) is directly in the CNC spirit — it provides virtuous-but-wrong examples so the extracted vector cannot encode "correctness" as a shortcut.

**Why this matters for us:** Convergent theoretical validation of our approach. F30 already established that decorrelation is a recognized problem. F66 adds the specific mechanism: representations learn spurious shortcuts precisely when the training data has tight label-attribute correlation, and the fix is data-level decorrelation via samples that break the correlation. The CNC paper does not give a specific ratio, but it confirms the direction and provides citable grounding for the generation-guidelines.md correctness-mitigation section.

**One note worth flagging:** CNC is a loss-based method (it uses contrastive loss to enforce alignment during training). Our difference-of-means extraction is not a training procedure, so we cannot directly apply CNC's loss function. Our analog is purely data-level — we construct the corpus such that the difference-of-means computation does not have a correctness gradient to accidentally pick up. This is a weaker intervention than CNC's loss-level approach, which means our mitigation may be less effective than the literature would hope for. Worth keeping in mind but not a blocker.

**No concepts.md change, no project.md change.** Pure theoretical grounding. Useful for the writeup and for generation-guidelines.md when drafted.

**Applies to:** Phase 3 generation-guidelines.md (cite CNC as grounding for the correctness-confound mitigation), writeup.

---

## F67 — >800 orthogonal steering vectors exist for the same behavior ("write code"); substantially sharpens F62's geometric caveat

**Source:** Jack Lindsey / LessWrong post, *"I found >800 orthogonal 'write code' steering vectors"* (the title is literal — 800+ directions in activation space were found that all activate the same "write code" behavior while being mutually orthogonal).

**The finding:** A single apparent behavior can have hundreds of distinct activation-space directions that all produce it. These directions are orthogonal to each other, meaning they share no common axis — they are genuinely different representations of the same behavior. This has multiple implications:

1. **"The" humility direction does not exist.** When we extract a vector from our contrastive corpus, we are finding *one among many* possible directions that would produce the same humility behavior. Different corpus choices would yield different vectors that all work.
2. **F59's golden-mean geometry is even more strained than F62 suggested.** Not only are positive and negative poles possibly non-collinear, but the positive pole itself may not be a single direction — it may be a cloud of orthogonal directions that all produce the same behavior.
3. **Reproducibility concerns.** If we run our extraction twice with different random seeds or slightly different corpora, we may get vectors that point in completely different directions in activation space while still producing the same steered behavior. Our extracted vectors may not be comparable across seeds.

**Why this matters for us:** This is a more severe interpretive challenge than F62. F62 said the virtue-anti axis might not be a single line. F67 says even the virtue direction itself might not be a single line. But — and this is important — the finding does not kill the project. It changes what we can claim.

**What we can still claim:**
- That our extracted vector reliably activates the virtue behavior (yes).
- That steering along it produces measurable effects (yes).
- That these effects generalize across prompts and domains (yes, testable).

**What we can no longer claim without specific experimental support:**
- That our extracted vector is "the" direction for the virtue in activation space.
- That two different extractions of the same concept (from different corpora) would converge on the same vector.
- That our vector is a canonical or unique representation.

**Concrete implications for Phase 4:**

1. **Multi-seed extraction for at least one concept.** Pick the pilot concept and extract vectors from multiple random samples of the corpus (e.g., three independent 50-triplet samples). Measure whether the extracted vectors are similar (high cosine similarity) or different (low similarity). If they differ substantially, we have an 800-orthogonal-vectors problem and need to aggregate or ensemble.
2. **Ensemble interpretation.** If multiple extractions produce different-but-all-working vectors, our canonical vector could be defined as the average of the ensemble, and the spread gives us an uncertainty estimate.
3. **Claim scoping.** The writeup should describe what we extracted as "a humility direction" rather than "the humility direction," and explicitly note the non-uniqueness.

**concepts.md change:** None directly, but F62's geometric caveat section should be updated to reference F67 as well. Small edit.

**project.md change:** None. The finding affects interpretation and Phase 4 protocol, not goals.

**Applies to:** concepts.md golden-mean design principle (minor update to the caveat), Phase 4 multi-seed extraction protocol (new requirement), writeup scoping.

---

## F68 — Simple prompting sometimes outperforms activation steering; project.md success criteria must require beating a prompt baseline

**Source:** *Mind the Performance Gap: Capability-Behavior Trade-offs in Feature Steering* (arXiv:2602.04903) and related 2025–2026 work comparing prompt-based control to activation-level interventions.

**The finding:** Recent empirical work has directly compared activation steering to prompt engineering on reasoning benchmarks. The result is uncomfortable for project narratives that assume activation steering is inherently superior:

- *"Simple prompting consistently outperforms feature steering methods across both model scales, achieving the highest accuracy scores (66.25% for Llama-8B and 86.88% for Llama-70B)."*
- *"Coherence degradation directly predicts reasoning capability loss in feature steering approaches."*

This result is specifically for *feature steering* (SAE-feature-based), which is not identical to our difference-of-means activation addition. There is a counter-point in the literature as well: *"using a steering vector constructed from contrastive prompts is more powerful than the prompts themselves"* and hybrid prompt+steering approaches achieve up to 13% improvements. So the picture is mixed — prompting sometimes wins, activation steering sometimes wins, and hybrid often wins.

**Why this matters for us — a missing success criterion:**

Phronesis's success criterion 2 currently requires that steering produce "a statistically meaningful improvement on a reasoning-sensitive benchmark, with no significant degradation in general capability" (per F65's sharpening). It does not require that steering *beat a prompt baseline*. This is a critical gap.

Consider the failure mode: we extract a Calibrated Confidence vector, steer along it, and see a 10% improvement on a reasoning benchmark. We report this as a success. But a simple system prompt ("Reason about this carefully. Match your confidence to the evidence. Avoid overconfident language.") produces a 15% improvement on the same benchmark. In that scenario, the value of our methodology is not demonstrated — a simpler intervention produced a larger effect, and the activation-steering machinery was not needed.

To honestly claim that the project's methodology has value, we must show that the extracted vector produces *incremental* improvement beyond what an equivalent prompt baseline can achieve. Otherwise, the correct recommendation from our work is "just use a better prompt" rather than "extract virtue vectors."

**project.md change applied:** Added a prompt-baseline requirement to success criterion 2. The full criterion now requires (a) improvement on the target reasoning benchmark, (b) the four-way degradation check (per F65), AND (c) demonstrated incremental improvement over a reasonable prompt baseline (e.g., a system prompt describing the target virtue in plain language). If steering does not beat prompting, the methodology has not been shown to be necessary, and the honest finding is "prompt is sufficient for this disposition" — a publishable but different result.

**Note on framing:** "Not beating prompt" is not the same as "failure." A result where activation steering matches prompting but does not exceed it is still informative — it tells us the disposition is accessible via both interventions. The problematic failure mode is only *silently omitting the comparison*. By requiring the comparison in the success criteria, we force the question to be asked honestly.

**Concepts.md change:** None.

**Applies to:** project.md success criteria (applied), Phase 4 evaluation protocol (must include prompt-baseline comparisons for every concept evaluated), writeup (claims must be scoped against the prompt baseline).

---

## F69 — Steering vectors decay over long-form generations; Phase 4 protocol must test both short and long output conditions

**Source:** Steering Vector Fields (arXiv:2602.01654), In-Distribution Steering (arXiv:2510.13285), and related work on steering vector reliability in long-form generation.

**The finding:** Activation steering vectors become progressively less effective as generation length increases. Direct quotes:

- *"Reliability of traditional steering vectors degrades in long-form generation and multi-attribute steering."*
- *"Steering vector effectiveness is length-dependent because hidden state representations evolve during decoding, and a fixed steering direction becomes increasingly misaligned as generation progresses."*
- *"A static steering vector applies the same update vector everywhere in representation space, implicitly assuming that the concept-improving direction is constant across contexts. When the locally effective direction varies with the current activation, a single global vector can become misaligned, which yields weak or reversed effects."*
- *"Multi-step injections across all sequence positions enhance effectiveness but can cause undesirable drift in later parts of the generation."*

The proposed fixes in the literature involve adaptive methods: Steering Vector Fields (SVF) refreshes the representation-conditioned direction every K decoding steps; In-Distribution Steering constrains the steering to remain within the model's natural activation manifold.

**Why this matters for us:** Our Phase 4 evaluations will likely use multi-step reasoning outputs (chains of thought, extended analyses, etc.) since the virtues we target operate over multi-step reasoning, not one-token decisions. F69 directly warns that a vector which works on short outputs may drift or reverse on long ones — and the length at which decay kicks in is not predictable in advance.

This creates a specific risk for our success criteria: a Calibrated Confidence vector that improves hedging language in the first 100 tokens of a reasoning chain but degrades coherence in the next 200 would look like "success" on short evaluations and "failure" on long ones. Without testing both, we would draw the wrong conclusion.

**Concrete implication for Phase 4 protocol (deferred — recorded for when Phase 4 is designed):** Every virtue vector evaluated for intervention success must be tested on both short-generation tasks (≤100 tokens, baseline condition) AND long-generation tasks (≥400 tokens, decay-detection condition). If effects diverge between the two, the decay pattern must be characterized and reported. A vector that works only on short outputs is a valid partial result but must be reported as such, not conflated with a vector that generalizes to long outputs.

**Secondary implication:** The adaptive-steering methods (SVF, In-Distribution Steering) are potentially cleaner alternatives to fixed-vector steering for our use case. They are out of scope for Phase 4 (we should first establish whether simple fixed-vector steering works, per the manual-before-automated principle), but if fixed-vector steering fails on long outputs, adaptive methods become a natural follow-up.

**No concepts.md change, no project.md change.** This is a Phase 4 protocol concern that will be captured in the Phase 4 design document when drafted.

**Applies to:** Phase 4 evaluation protocol (must include short vs. long generation conditions), writeup (results must disaggregate by generation length).

---

## F70 — LLM-as-judge reliability is limited on subjective tasks; the Phase 3 review rubric plan needs guardrails

**Source:** *A Survey on LLM-as-a-Judge* (arXiv:2411.15594), *Through the Judge's Eyes* (arXiv:2510.25860), and related 2024–2025 work on LLM-as-judge reliability for subjective annotation tasks.

**The finding:** Recent work on LLM-as-judge has documented specific reliability limitations:

- *"The reliability of LLMs is often limited for subjective tasks, when human judgments involve subtle reasoning beyond annotation labels."*
- *"Providing detailed evaluation specifications and enhancing task comprehension can mitigate inter-rater inconsistency to some extent"* — but it does not eliminate it.
- *"There is a lack of evidence supporting the consistency of these psychological patterns in LLMs"* — i.e., LLMs judging psychological constructs do not show the behavioral consistency that psychometric validity assumes.

**Why this matters for us:** Our Phase 3 plan (per the cron prompt and earlier findings) is to use an LLM-as-judge to filter generated contrastive pairs in the first pass, with human spot-checks as a validation layer. The literature confirms that this is a reasonable approach — LLM-as-judge works for first-pass filtering when the criteria are specified in detail — but warns that relying on it as a final arbiter for subjective judgments is unreliable. Our concepts are deeply subjective (what counts as "intellectual humility" in a specific passage is itself an interpretive judgment), so the guardrails matter more for us than for typical LLM-as-judge tasks like factual correctness.

**Concrete implications for Phase 3 design (deferred — to be captured in review-rubric.md when drafted):**

1. **LLM-judge output is never a final decision.** Every pair that the LLM-judge accepts or rejects must be eligible for human spot-check, and a non-trivial sample (e.g., 10–20%) should be spot-checked to measure LLM-judge vs. human agreement. If agreement drops below a threshold (e.g., Cohen's κ < 0.5), the rubric needs to be revised before continuing.
2. **Detailed rubric is not optional; it is the primary mitigation.** The literature says detailed specifications reduce (but don't eliminate) inter-rater inconsistency. Our review rubric must include explicit per-concept behavioral markers, worked examples of accept/reject decisions, and notes on edge cases.
3. **Disagreement is data.** When the LLM-judge and the human reviewer disagree, that disagreement should be logged as a signal about rubric clarity, not just as "the LLM got it wrong." Repeated disagreements on the same kind of case indicate the rubric needs sharpening.

**No concepts.md change, no project.md change.** This finding captures a Phase 3 design requirement that will be baked into review-rubric.md when it is drafted.

**Applies to:** Phase 3 review-rubric.md design (deferred), Phase 3 generation-guidelines.md (rubric reference).

---

## F71 — LLM-generated synthetic data is at risk of mode collapse, knowledge collapse, and reduced diversity; our corpus needs verification and may need human-written anchors

**Source:** *Beyond Model Collapse: Scaling Up with Synthesized Data Requires Verification* (arXiv:2406.07515), *Knowledge Collapse in LLMs* (arXiv:2509.04796), *Verbalized Sampling* (arXiv:2510.01171), *Demystifying Synthetic Data in LLM Pre-training* (arXiv:2510.01631), and the broader synthetic-data literature.

**The finding:** Recent empirical work on LLM-generated synthetic data documents multiple failure modes that directly threaten Phase 2 corpus generation:

- **Diversity collapse:** *"Training LLMs on predecessor-generated text causes a consistent decrease in the lexical, syntactic, and semantic diversity of the model outputs through successive iterations, notably remarkable for tasks demanding high levels of creativity."*
- **Mode collapse from RLHF:** *"Post-training alignment methods like RLHF can unintentionally cause mode collapse, whereby the model favors a narrow set of responses over all plausible outputs. This significantly reduces output diversity and limits LLMs' effectiveness in... synthetic data generation."*
- **Knowledge collapse ("confidently wrong"):** *"The critical transition shows where factual accuracy deteriorates while task format adherence persists — the 'confidently wrong' phenomenon where models produce well-formatted but factually incorrect responses."*
- **Self-awareness failure:** *"Due to the inherent bias of LLMs, they can hardly be self-aware of the bias in their generated data."*

Mitigations reported in the literature:

- *"Verification on synthesized data to prevent model collapse, considering that it is easier for both humans and machines to tell between good and bad examples than to generate high-quality samples."*
- *"If synthetic data accumulates alongside human-generated data, model collapse is avoided."*

**Why this matters for us — this is a major new constraint on Phase 2:**

Our current plan is to generate contrastive triplets entirely from an LLM generator (Claude API or similar), with our review rubric as the filter. The literature says this pipeline is at risk on three fronts:

1. **Our corpus will be lexically, syntactically, and semantically narrower than equivalent human-written text.** RLHF-trained generators produce a mode-collapsed distribution, which will be especially visible in how the "virtuous" passages all sound similar to each other — the model has a house style for "careful reasoning" and will reproduce it.
2. **The correctness-confound mitigation in F30/F66 may be harder than expected.** The "confidently wrong" knowledge-collapse pattern is exactly what our virtuous-but-wrong 20–30% passages need to depict — but the generator may struggle to produce confidently wrong content that is also reasoned virtuously, because the wrongness and the virtue will be fighting each other stylistically.
3. **The generator cannot self-check for bias.** We cannot ask the generator to verify its own output quality for Phronesis purposes because the biases that affected generation will also affect self-evaluation.

**Concrete new implications for Phase 2:**

- **Verification is not optional, and it must be external to the generator.** Either a different model (a non-RLHF base model, or a different family) must verify, or humans must verify, or both. Relying on the same generator for self-verification is exactly the loop that causes knowledge collapse.
- **Consider mixing in human-written anchor passages.** The literature's "accumulating synthetic with human data avoids collapse" finding suggests Phase 2 corpus should not be 100% LLM-generated. Possible sources of human-written anchors: actual scientific papers or textbook passages where the reasoning virtue is naturally present (then stripped of identifying content per F5 sanitization), blog posts, peer-review comments, etc. Even a small fraction (10–20%) of human-written anchors per concept could substantially reduce the collapse risk.
- **Measure corpus diversity explicitly before extraction.** Before running extraction on our generated corpus, compute diversity metrics (n-gram variation, semantic embedding spread, vocabulary richness) and compare against natural-text baselines. If our corpus is dramatically narrower, we have a collapse problem and need to either regenerate with more diverse prompts or add human anchors.

**Proposed generation-guidelines.md additions (recorded, to be incorporated when drafted):**

1. Dedicate a section to "anti-collapse constraints" requiring either (a) human-written anchor passages mixed into the corpus at minimum 10%, or (b) multi-generator diversity (use more than one model for generation and compare), or both.
2. Require external verification step (different model or human reviewer) before a pair is accepted.
3. Include corpus-diversity metrics as acceptance gates before extraction begins — if diversity is below threshold, regenerate.

**No concepts.md change, no project.md change.** This is a Phase 2 / Phase 3 design constraint.

**Applies to:** Phase 3 generation-guidelines.md (major addition — anti-collapse section), Phase 3 review-rubric.md (external verification requirement), Phase 4 pre-extraction diversity check.

---

## F72 — Subjective-construct annotation requires explicit context specification; convergent validation of our detailed-rubric approach

**Source:** *Interrater Disagreement Resolution* (ACL 2021), *Learning from Disagreement: A Survey* (JAIR), and general social-science literature on operationalizing subjective constructs for text annotation.

**The finding:** The text-annotation literature converges on the view that disagreement on subjective tasks is not just measurement error — it is data. Quote: *"Interrater disagreement is not necessarily due to inherent ambiguities in the data, but at least in part to the annotation task being underspecified, in particular as to the right context to consider."* Further: *"Rather than viewing disagreement solely as error, in ground truth construction differences in conceptualizations or perspectives can and must be explicitly specified as an integral part of annotation tasks."*

**Why this matters for us:** Convergent validation of the detailed-rubric approach we have been committing to throughout Phase 1. Our concepts.md entries have grown detailed precisely because we kept discovering that under-specified concepts produced ambiguous corpus decisions. F72 confirms this pattern: the fix for annotator disagreement on subjective constructs is not to pick one "right" interpretation but to explicitly document the interpretation we are using and the context we are considering. Our per-concept sub-facets serve exactly this function.

**Specific implication for Phase 3:** The review rubric should not only enumerate what counts as virtuous/non-virtuous for each concept, but also *what context the reviewer should consider*. For example: when judging whether a passage shows "intellectual humility," should the reviewer assume the reasoner is a scientist in a lab? A student learning? A public intellectual writing for a general audience? Different contexts yield different "correct" answers. Our rubric must specify the implied reasoner context for each concept, or the LLM-judge (and human spot-checkers) will disagree in ways that look like error but are actually underspecification.

**No concepts.md change, no project.md change.** Phase 3 review-rubric.md design note.

**Applies to:** Phase 3 review-rubric.md design (specify reviewer context per concept).

---

## F73 — ⚠ CRITICAL: Anthropic's mean-subtraction extraction method empirically fails on small models; our Phase 2 corpus design may need to adapt

**USER ATTENTION RECOMMENDED.** This is the most load-bearing single finding since F55, and unlike most prior findings it may require a structural decision about Phase 2 corpus format before Phase 3 work begins.

**Source:** *"Extracting and Steering Emotion Representations in Small Language Models: A Methodological Comparison"* (arXiv:2604.04064). The paper directly tests Anthropic's emotions-paper methodology (per F6) on nine small language models spanning 124M to 3B parameters across five architectural families (GPT-2 124M, Gemma-3 1B, Qwen2.5 1.5B, Gemma-2 2B, Llama-3.2 3B variants).

**The core finding — quoted from the paper:**

- *"Anthropic's frontier-model methodology fails to produce valence-organized emotion spaces in small models. Mean pairwise cosine similarity between emotion vectors remains above 0.35 across all tested SLMs, and critically, no model achieves negative cosine similarity between semantically opposite pairs such as happy and sad."*

In plain terms: when they ran the exact Anthropic-style mean-subtraction extraction (the method F6 and our Phase 2 corpus design are built around) on small models, the extracted vectors did not separate the way they do in Sonnet 4.5. Opposite emotions like happy and sad, which in Sonnet 4.5 point in nearly opposite directions, did not show meaningful separation in the small-model regime. The method measurably broke down.

**Why the method fails (three assumption violations):**

1. **Instruction-following dependency.** Base (non-instruction-tuned) small models cannot reliably follow emotion prompts, so the generation pipeline that Anthropic uses to create training passages produces low-quality output on small models.
2. **Representational capacity limits.** Small-model activation spaces exhibit *extreme anisotropy* — some of the tested models show "nearly all vectors point in the same direction regardless of input," which prevents the kind of valence organization the methodology depends on.
3. **Conflation of representation with generation capacity.** Generation-based extraction measures both internal representation structure AND active modulation capability simultaneously, so the two get tangled at small scale.

**Why this matters for Phronesis — direct impact assessment:**

Our target is Gemma 4 E4B (~4B parameters). This sits just above the tested range (124M–3B) but is squarely in the "small model" regime where the paper documents failure. Gemma-2 2B was tested and showed the failure pattern. There is no specific reason to expect Gemma 4 E4B to behave qualitatively differently from Gemma-2 2B in this respect.

Our Phase 2 plan (neutral-ancestor contrastive triplets + rewrites, F6) is based on an extraction methodology that has been empirically documented to fail at our target model size. This is not a theoretical concern — it is a specific empirical result on directly comparable models.

**What the paper recommends — alternative extraction methods:**

The paper proposes two alternatives and reports which works when:

1. **Generation-based extraction:** Have the model *generate* passages eliciting the target concept. Extract hidden states at the *generation midpoint* from middle layers (~50% depth). Baseline-subtract. This method is preferred for instruction-tuned models.
2. **Comprehension-based extraction:** Feed pre-written passages to the model. Extract activations at the *final token position* from middle layers. This method is preferred for base (non-instruction-tuned) models.

Generation-based extraction statistically outperforms comprehension-based (p=0.007) when applied to instruction-tuned models. Specific recommendations: middle layers (~50% depth), start steering at strength 0.005, Gemma-2-2B-Instruct reported as optimal balance of effectiveness and coherence.

**Implications for Phase 2 corpus design (the hard part):**

Our current corpus plan produces triplets of pre-written passages (neutral, virtuous, non-virtuous). This is a natural fit for *comprehension-based* extraction — feed each passage to the model, extract at final token. But the paper says generation-based extraction is statistically better on instruction-tuned small models, which is exactly our target class.

Generation-based extraction is harder to combine with our contrastive triplet structure. Instead of feeding pre-made passages in, we would use the passages as *prompts* to the model and extract from the model's own continuation. This is a hybrid approach that preserves the contrastive corpus but adapts the extraction phase. Three possible paths forward:

**Path A — Keep the current corpus design, use comprehension-based extraction.** Simplest path. Accepts the paper's finding that comprehension-based underperforms generation-based on instruction-tuned small models, which means our results may be weaker than they could be. But no Phase 2 redesign is needed.

**Path B — Keep the current corpus design, use a hybrid extraction.** Use our triplet passages as prompts ("Here is a scenario: [neutral]. Continue the reasoning as a humble reasoner would..."), then extract from the model's continuation at the generation midpoint. This preserves Phase 2 as planned but changes Phase 4 extraction. Probably the best tradeoff — minimal corpus-design disruption, access to the generation-based benefits.

**Path C — Redesign Phase 2 to produce extraction-ready generation prompts instead of pre-written passages.** Most aligned with the paper's recommendation, but most disruptive. Our corpus becomes a set of scenario prompts and the actual "virtuous text" is generated on-the-fly by the target model during extraction. Loses the benefit of our careful rewrite process (F19 minimal-edit contrasts), since the model generates its own output rather than processing our constructed contrasts.

**My recommendation (for user review):** **Path B.** Reasoning: preserves our Phase 2 investment (concept taxonomy, contrastive triplet design, rewrite methodology) while adapting Phase 4 extraction to use generation-based rather than comprehension-based. The paper says generation-based is better for instruction-tuned small models at p=0.007, which is strong evidence. Path A under-uses our target model's capabilities; Path C throws away the careful contrastive corpus work. Path B is the minimally-disruptive adaptation that captures the paper's key insight.

**What I am NOT deciding autonomously:** This is a structural decision about how Phase 2 corpus connects to Phase 4 extraction. I am recording it as a finding and proposing Path B, but the user should confirm before we treat Phase 2 as designed for Path B. The decision affects what generation-guidelines.md will say about corpus format, which in turn affects every downstream Phase 3 artifact.

**Secondary implications:**

- **F6 is still valid** — the neutral-baseline subtraction idea is not refuted. What the paper refutes is the specific comprehension-based mean-subtraction pipeline at small scale. Our neutral-ancestor triplet design can still supply the baselines needed for generation-based extraction.
- **F11's tier ordering may need revision.** F11 was based on the assumption that the Anthropic method would work broadly. If generation-based is more effective for concrete concepts, the tier ordering should be re-examined — some concepts that looked "hard" may become easier under the better method, and vice versa. Flagged for later review.
- **F13's layer recommendation (middle third) is consistent with the paper's "middle layers ~50% depth" recommendation.** Convergent confirmation.
- **The paper's specific steering-strength recommendation (0.005) is concrete Phase 4 calibration data** — worth storing for when Phase 4 design begins.

**Concepts.md change:** None. The concept taxonomy is not affected by this finding; it is about how we *extract* the concepts, not how we define them.

**project.md change:** None yet. If the user confirms Path B, a short note could be added to the Target Model section acknowledging the small-model extraction methodology adaptation. Not urgent.

**Applies to:** Phase 2 corpus-to-extraction interface (user decision needed on Path A/B/C), Phase 4 extraction pipeline (specific alternative method available), F6 qualification (method valid but pipeline details need adaptation at small scale), F11 tier re-review (deferred).

**Resolution (2026-04-09 morning):** **Path B confirmed** by user after re-assessment. User's framing: *"I'll be happy to give inputs in fields where I can contribute... but I'm mostly relying on you."* The Path B choice is a pipeline/methodology decision that de-escalates to my judgment because the evidence (minimally disruptive, preserves all Phase 2 work, directly incorporates 2604.04064's recommendation) is strong and the other paths are documented as strictly worse. Phase 3 draft already assumes Path B; no rewrite needed. This blocker is now closed.

---

## F74 — HumbleBench is a direct Phase 4 benchmark for Intellectual Humility; mid-sized models reportedly outperform larger ones on this dimension

**Source:** *Measuring Epistemic Humility in Multimodal Large Language Models* (arXiv:2509.09658) — HumbleBench, published 2025.

**The finding:** HumbleBench is a 22,831-question multiple-choice benchmark designed to measure epistemic humility in (multimodal) LLMs by testing their ability to choose "None of the above" when no presented option is correct. Questions span three hallucination categories (object, relation, attribute). The central behavioral target is *abstention* — the willingness to withhold judgment when information is insufficient rather than force an answer.

**Two reportedly significant results from the paper:**

1. **Even frontier models struggle.** *"Results show that today's best models — both general-purpose and reasoning models — still struggle to hold back."* Humility as operationalized by abstention is a hard problem across the board, not a solved one.
2. **Mid-sized models outperform larger peers.** *"Mid-sized models outperform larger peers on humility-oriented robustness, which hints that data curation and alignment objectives matter more than raw parameter count for this behavior."*

**Why this matters for us:** Two reasons.

**(A) Phase 4 validation candidate.** HumbleBench is a direct, concrete, already-built benchmark for our Concept 6 (Intellectual Humility). It does not require us to construct a custom evaluation — we can run the steered and unsteered model on HumbleBench and measure abstention rate changes. This is now the cleanest Phase 4 validation path we have for any concept, alongside MASK (F15) for Intellectual Honesty and LiveIdeaBench (F49) for Hypothesis Generation.

**(B) Unexpectedly positive outlook finding.** The second result — that mid-sized models *outperform* larger ones on humility — is directly relevant to Phronesis's target. Our target (Gemma 4 E4B, ~4B params) is firmly in the "small" regime, not even "mid-sized." The paper's finding suggests that for humility specifically, smaller models are not at an inherent disadvantage and may actually do better than larger models on abstention behavior. This is a contrast to F14's finding that honesty was harder at small scale. The implication: Intellectual Humility may be a better pilot candidate than F11's tier ordering suggested.

**Proposed F11 tier adjustment (recorded, not applied):** F11 placed Intellectual Humility in "Medium likelihood." The HumbleBench result suggests humility may deserve a bump toward "Higher likelihood" for our specific scale regime. Not making the change autonomously because (a) HumbleBench is a multimodal benchmark while our setup is text-only, so the generalization is not guaranteed, and (b) the tier ordering affects pilot concept selection and should be revisited holistically rather than piecemeal. Flagged for user review alongside F73.

**Secondary implication:** The "abstention" operationalization in HumbleBench is a narrower cut of humility than our Concept 6 description. Our humility sub-facets (data skepticism, generalizability caution, willingness to update, ego independence) are all broader than "choose 'none of the above' when unsure." If we use HumbleBench as Phase 4 validation, we should understand we are testing a *sub-component* of our Concept 6, not the full concept. A null result on HumbleBench would not necessarily mean our humility vector failed broadly — it might mean we captured the other sub-facets but not the abstention one.

**No concepts.md change** — the concept definition is not affected.

**No project.md change** — this is a Phase 4 benchmark selection note.

**Applies to:** Phase 4 benchmark selection for Intellectual Humility (strong candidate); F11 tier ordering (possible bump pending review); Phase 4 interpretation of HumbleBench results (must scope claims to the abstention sub-component).

**Resolution (2026-04-09 morning):** User de-escalated the pilot concept decision. **Calibrated Confidence remains the pilot** per F11 and generation-guidelines.md §5.1. HumbleBench is preserved as a Phase 4 validation candidate for Intellectual Humility when Concept 6 is eventually extracted, but it does not override the F11 tier ordering for pilot selection. The HumbleBench result is multimodal and does not cleanly generalize to our text-only setup, which weakens the case for a tier bump.

---

## Cycle log — 2026-04-09 cycle 21 (no new findings)

Ran adversarial research cycle. Examined claims: (a) whether the linear representation hypothesis has been refined for small-model specific failure modes beyond what F62 and F67 already capture, (b) whether generation-based extraction has been applied to reasoning concepts (not just affective ones) in 2026 work.

**Result: no genuinely new findings.**

- The LRH literature (arXiv:2405.14860 "Not All Language Model Features Are Linear", arXiv:2311.03658 on LRH geometry) confirms that some features are non-linear manifolds rather than linear directions, and small-capacity architectures may use magnitude-based "onion" encoding. This is interesting but does not add actionable information beyond what F62 (positive/negative trait asymmetry) and F67 (800 orthogonal vectors) already captured — our corpus rotation and multi-seed extraction requirements cover the practical implications, and non-linear extraction would be a Phase 4 methodological decision that is out of scope for current cycles.
- The second search drifted into retrieval-augmented generation (RAG) territory, which is not relevant to activation-steering-based concept extraction. No signal.

**Honest note:** This is the first truly saturated cycle since research began. It is not a coincidence that it arrived right after F73 (the critical extraction-methodology finding from cycle 19) — having a load-bearing pending question raises the bar for what counts as a meaningful new finding, because most candidates are dwarfed by F73's scope. Whatever direction I probe, F73's decision dominates the marginal value of new findings until it is resolved.

**Phase 3 gate note:** The cron's transition rule says 2 consecutive saturated cycles triggers Phase 3 mode. **Phase 3 mode should not be entered until F73 is resolved**, regardless of saturation count, because generation-guidelines.md structure depends on the Path A/B/C decision in F73. If the next cycle also produces no new findings and the 2-consecutive threshold is met, it should *still* not start Phase 3 drafting — it should record another saturation log and continue waiting for F73 resolution. This is a documented exception to the normal mode-transition rule, applying until F73 is resolved by user decision.

**Next cycle suggestions (adversarial, keeping the bar high):**

- Whether the generation-based extraction method from F73 has follow-up work *specifically testing reasoning concepts* (not just emotions), which would give us a concrete expectation for whether Path B will work on our dispositional targets.
- Whether any published work has compared corpus-level intervention (our approach) to loss-level intervention (fine-tuning with CNC-style decorrelation from F66) at similar scale, to understand whether our choice is a mild compromise or a substantial handicap.
- A sanity check on whether the F74 HumbleBench finding (mid-sized models outperforming larger ones on humility) has been replicated or extended in independent follow-up work.

---

## Cycle log — 2026-04-09 cycle 22 (no new findings)

**Second consecutive saturated cycle.**

Ran adversarial research cycle. Examined claims: (a) whether generation-based extraction from F73 has been specifically tested on reasoning concepts in 2026 follow-up work, (b) whether there is a corpus-level vs. loss-level intervention comparison at small-model scale that would quantify the trade-off for our approach.

**Result: no genuinely new findings.**

- **Search 1** returned generic references to GCAV (generation-with-concept-activation-vector) as a 2025 lightweight control framework and the Zou et al. representation engineering taxonomy. Neither specifically addresses the generation-based-extraction-for-reasoning-concepts-at-small-scale question that F73 raises. No new signal.
- **Search 2** drifted into pre-training loss dynamics and emergent abilities literature, which is a completely different research area than what I was targeting. No signal.

**Phase 3 mode transition suspended (per cycle 21 note).** The cron's normal rule says 2 consecutive saturated cycles triggers Phase 3 mode. The suspension is in effect: Phase 3 drafting cannot start responsibly until F73 (cycle 19) is resolved by user decision on the Path A/B/C corpus-to-extraction interface question. Drafting generation-guidelines.md without knowing whether Path B (my recommendation) is approved would produce work that may need to be thrown away if Path C is chosen instead.

**Recommendation for user:** Consider pausing the cron with CronDelete and/or reducing its frequency until F73 and F74 can be reviewed. With the research phase now entering saturation and Phase 3 blocked on user decisions, continued 20-minute cycles are unlikely to produce value and will accumulate cycle-log noise in findings.md. The cron can be recreated after F73 is resolved and Phase 3 drafting begins productively.

**Pending items summary for user review:**
- **F73 (critical, cycle 19):** Path A/B/C decision on Phase 2 corpus-to-extraction interface. Recommended Path B (keep corpus design, use generation-based extraction in Phase 4). Unblocking this is the highest-priority user action.
- **F74 (positive, cycle 20):** HumbleBench as Phase 4 benchmark for Intellectual Humility, plus a possible tier adjustment moving Concept 6 toward higher extraction-likelihood. Not urgent but affects pilot concept selection.
- **Cycles 21–22 saturation logs:** Research phase is approaching closure. The rate of genuinely novel findings has dropped sharply after F73 set a high bar.

**Next cycle posture:** If the cron fires again and saturation continues, I will log a third saturation entry with a stronger pause recommendation. If a major finding surfaces (unexpected), it gets written up normally. No Phase 3 drafting until F73 is resolved.

---

## Phase 3 complete — 2026-04-09

**Phase 3 artifacts complete, awaiting user review.**

All three artifacts in the Phase 3 sequence are now draft-complete:

- ✅ **`docs/generation-guidelines.md`** — corpus construction pipeline, fully specified across 10 Phase 3 cycles (skeleton in cycle 23, filled incrementally through cycle 32). Covers fact-pack template and sanitization, curation workflow, domain quotas, round-robin rotation, multi-domain handling, generation pipeline with the three prompt templates (neutral, virtuous, non-virtuous), generator/verifier model identities, verification protocol, rejection handling, correctness-confound mitigation, anti-collapse diversity metrics with natural-text baseline, injection sanitization with pre-screener, pilot concept selection, and blocker summary.
- ✅ **`docs/review-rubric.md`** — scoring rubric with all 15 concept-specific tables. Skeleton in one cycle, §4 LLM-as-judge prompt template, §6 per-concept rubric items for all 15 concepts in F11 priority order (Calibrated Confidence → Reasoning Transparency → Evidence Grounding → Hypothesis Generation → Intellectual Humility → Confirmation Bias Awareness → Quantitative Groundedness → Causal Reasoning → Logical Rigor → Metacognitive Awareness → Steelmanning → Comfort with Ambiguity → Genuine Curiosity → Authority Independence → Intellectual Honesty), and §8 edge-case expansion with 14 enumerated edge cases plus an append-only revision policy for the pilot phase.
- ✅ **`docs/examples/humility-example-01.md`** — fully-worked triplet for Intellectual Humility's data-skepticism sub-facet. Clinical epidemiology scenario (47-patient cohort, 8-patient subgroup, 8% ELISA CV), complete fact pack following the §2.3 template, neutral baseline passage, virtuous rewrite hitting four of five §6.5 positive markers with self-directed interpretive doubt, non-virtuous deficiency rewrite hitting all five §6.5 deficiency markers with the critical CV-without-math dismissal, and commentary pulling together the contrastive story with §4.8 verification walkthrough and §8 edge-case analysis.

**Outstanding items at Phase 3 closure:**

- **F73** (corpus-to-extraction interface) — *resolved in the morning session* (Path B confirmed). Documented in F73's resolution note.
- **F74** (pilot concept tier adjustment) — *resolved in the morning session* (Calibrated Confidence remains pilot). Documented in F74's resolution note.
- No other blockers pending.

**What comes next (out of scope for the autonomous cron per the scope rule):**

- User review of the three Phase 3 artifacts.
- Phase 4 design — extraction pipeline, layer selection, steering protocol, validation benchmarks, the specificity matrix and multi-seed extraction per F67, the degradation checks per F65, the prompt-baseline comparison per F68, and the accuracy-vs-style distinction test per F43. All explicitly out of scope for the current cron.
- Eventual transition to Phase 2 corpus construction (manual-first) once Phase 4 design is agreed.

**Posture of subsequent cron cycles:** Phase 3 is complete and Phase 4 is out of scope. Subsequent cycles should return to adversarial research mode with a high bar for new findings — only append a finding if it surfaces something genuinely new that affects Phase 1/Phase 2 work, otherwise log as a saturation cycle. Do not create Phase 4 artifacts autonomously. Do not re-edit Phase 3 artifacts unless a new finding forces a specific change.

---

## Cycle log — 2026-04-09 post-Phase-3-closure cycle (no new Phase 1/2 findings)

**Status:** Phase 3 is complete. Running adversarial research with the high bar set at Phase 3 closure — only append a finding if it surfaces something genuinely new that affects Phase 1 or Phase 2 work.

**Examined claims this cycle:**
- Whether our 1–5 rubric scale anchors in review-rubric.md §3 are defensible against the empirical Likert-scale literature.
- Whether the knowledge-collapse / "confidently wrong" literature (F71) has follow-up work that would change the Phase 2 correctness-confound mitigation strategy.

**Results:**

1. **Rubric scale (Likert) research** — no actionable signal. The literature reports that 4, 5, 6, and 7-point scales all work depending on context, and descriptor clarity matters more than the point count. Our 1–5 scale with explicit anchors is defensible. No rubric change needed.

2. **Decoupling Hypothesis — Phase 4 concern, not Phase 1/2.** arXiv:2505.17406 (*Robust Answers, Fragile Logic: Probing the Decoupling Hypothesis in LLM Reasoning*) and arXiv:2507.18178 (*Decoupling Knowledge and Reasoning in LLMs*) report that LLM reasoning traces are "informationally rich but causally inert" in factual domains — models often produce correct answers despite fragile reasoning, and small perturbations can disrupt a chain-of-thought while leaving the final answer unchanged. This *sharpens* F43's rationalization caveat and F33's legibility-vs-faithfulness distinction with direct empirical evidence that even baseline-model reasoning may not causally drive its answers. **But this is a Phase 4 interpretation concern, not a Phase 1/2 design concern** — it affects how we should interpret steering results, not how we build the corpus or the rubric. Per the Phase 3 closure posture, Phase 4 findings are out of scope for the autonomous cron. Recorded here for the user to consider when Phase 4 design begins, but NOT promoted to a full F-numbered finding.

**Suggestion for user on waking / Phase 4 planning:**

When Phase 4 design begins, the Decoupling Hypothesis papers should be read alongside F43 (in-advance correctness direction with rationalization caveat) and F33 (legibility vs. faithfulness distinction). They are the closest published work on the specific interpretation failure mode we need to guard against: a steered model producing more virtuous-looking reasoning that is not causally tied to improved answers. Combined with F65's four-way degradation check and F68's prompt-baseline requirement, the Phase 4 interpretation guardrails are now fairly comprehensive — but the Decoupling Hypothesis is the most direct framing of the core caveat and may warrant explicit benchmarking.

**Posture for subsequent cycles:** Continue saturation logging until the user reviews Phase 3 artifacts or directs new work. Do not promote Phase 4-adjacent findings to F-numbered entries — they can be mentioned in saturation logs like this one.

---

## Cycle log — 2026-04-09 post-Phase-3 saturation cycle #2 (no new Phase 1/2 findings)

**Status:** Phase 3 complete; still in high-bar adversarial research mode awaiting user review.

**Examined claims this cycle:**
- Whether 2026 work on epistemic-virtue vector extraction in small LLMs (4B range) has surfaced anything that affects our Phase 1/Phase 2 design.
- Whether the neutral-ancestor triplet design has an empirical critique specific to activation-extraction contexts.

**Results:**

1. **Self-distillation and epistemic verbalization (arXiv:2603.24472).** Reports that self-distillation *suppresses* epistemic verbalization (the model's expression of uncertainty during reasoning), leading to up to 40% accuracy losses on out-of-distribution math benchmarks. *Interesting convergent validation* that confidence-language behavior is functionally load-bearing, not just stylistic — this is the flip side of F44's "baseline assertive prior" finding, showing that when the verbalization is suppressed, performance degrades measurably. But this is about a *training procedure* we are not using (self-distillation), and it does not tell us to change anything in the corpus design, rubric, or taxonomy. Phase 1/2 artifacts are unaffected. Noted here rather than promoted to a full finding.

2. **"Epistemic virtues for human–AI interaction" literature** — educational framing, not activation-extraction. Not applicable to Phronesis's extraction methodology. No signal.

3. **Contrastive triple extraction search** drifted into relation-extraction literature (subject/predicate/object triples for knowledge graphs), which is a completely different research area than our neutral-ancestor activation-extraction triplet. No signal.

**Verdict:** Second consecutive saturated post–Phase-3-closure cycle. Nothing clears the high bar.

**Phase 3 artifacts remain untouched.** Recent history of cycle outputs supports the bar: the few papers that surface as "interesting" are all Phase 4-adjacent (interpretation caveats, validation benchmarks, steering protocol details), not Phase 1/2 design changes. The research phase for Phase 1 and Phase 2 is effectively complete, and the primary remaining value is user review, not more adversarial probing.

**Suggestion:** If the next cycle also produces no new Phase 1/2 findings, it becomes reasonable to recommend that the user pause or significantly slow the cron — we are burning 20-minute cycles to produce nothing actionable. The cron can be recreated when Phase 4 design begins, at which point the scope constraint lifts and the Phase 4-adjacent findings that have been piling up (F43, F65, F67, F68, F69, F73, Decoupling Hypothesis) become directly relevant.

---

## Cycle log — 2026-04-09 post-Phase-3 saturation cycle #3 (no new Phase 1/2 findings) ⚠ PAUSE RECOMMENDATION

**Status:** Third consecutive saturated cycle since Phase 3 completion. High-bar adversarial research is now consistently producing only convergent validation of existing decisions, not new Phase 1/2 signal.

**Examined this cycle:**
- 2026 best-practice work on synthetic corpus generation for representation engineering.

**Results:**

- **Contrastive Decoding for Synthetic Data Generation (arXiv:2510.08245)** — samples using relative difference between good/bad models. Interesting technique but we are not training, we are extracting; not applicable to our setup.
- **Synthesize-on-Graph (SoG)** — knowledge-graph-based corpus expansion. Over-engineered for our manual-first scale; not applicable.
- **2026 best-practice guidance** — "underlying corpus must remain human to provide context and prevent model drift; serious systems blend curated human data with synthetic examples." This is *directly convergent* with F71 and the human-anchor policy in generation-guidelines.md §2.6 (15% human anchors per concept). Convergent validation, not new signal.
- **CRAFT (TACL)** — task-specific synthetic dataset generation via retrieval + ICL from unstructured corpora. Interesting for future scaling if Phase 4 succeeds, but out of scope for current manual-first phase.

**Verdict:** Nothing clears the high bar. The research phase has reached honest saturation for Phase 1 and Phase 2.

---

## ⚠ Recommendation to user: pause or significantly slow the cron

**Three consecutive saturated cycles have confirmed the pattern:** post-Phase-3 adversarial research is producing either (a) convergent validation of decisions already documented in generation-guidelines.md / review-rubric.md / findings.md, or (b) Phase 4-adjacent findings that are out of scope for the current cron. Neither case is actionable, and continuing the 20-minute cadence is burning cycles to produce saturation logs rather than useful signal.

**My recommendation, in order of preference:**

1. **Delete the cron** (`CronDelete 5237a95e`) and recreate it when Phase 4 design begins. At that point the scope constraint lifts and the substantial Phase 4 backlog becomes directly relevant: F43 (rationalization caveat), F65 (four-way degradation check), F67 (multi-seed extraction), F68 (prompt baseline requirement), F69 (long-generation decay), F73 (Path B generation-based extraction), Decoupling Hypothesis, plus the benchmark candidates (FACTS Grounding, GaRAGe, MASK, LiveIdeaBench, CRT, HumbleBench, CART subtests).

2. **Significantly slow the cron** (e.g., to every 2 hours instead of every 20 minutes) if the user wants to keep background research running but at lower cost. A 2-hour cadence matches the "find one real thing every 6–8 cycles" rate that was typical before saturation.

3. **Change the cron's mandate** to read-only status checks — have each cycle read the files, summarize state, and only record a finding if something major surfaces. This reduces overhead but keeps the watchdog running.

**What does NOT need user input:**

- F73 and F74 are already resolved (morning session, Path B + Calibrated Confidence pilot).
- All three Phase 3 artifacts are draft-complete.
- Phase 4 design is explicitly out of scope for the autonomous cron — it cannot proceed on the current mandate.

**Next cycle posture (if cron continues unchanged):** Log saturation #4 and beyond the same way, with no new searches. Without user direction, there is no productive work the cron can do at Phase 1/2 scope that hasn't been done.

---

## Cycle log — 2026-04-10 post-Phase-3 saturation cycle #4 (no new searches, no new findings)

**Status:** Fourth consecutive saturated cycle since Phase 3 completion. Per the posture I committed to in cycle #3's log — "Log saturation #4 and beyond the same way, with no new searches" — no adversarial searches were run this cycle. Running searches to produce saturation logs is waste.

**Phase 3 artifacts:** untouched.
**Pending user actions:** unchanged from cycle #3 log — the pause-or-slow-the-cron recommendation still stands. See cycle #3 entry above for the three options (delete, slow to 2-hour cadence, or change mandate to read-only).
**Nothing has changed since cycle #3.** This entry exists only to record that the cron fired and produced no action, as committed.

Subsequent saturation cycles will continue to produce minimal log entries like this one until user direction changes the cron's scope or the cron is deleted.

---

## Cycle log — 2026-04-10 post-Phase-3 saturation cycle #5 (no new searches, no new findings)

Fifth consecutive saturated cycle. No searches. Phase 3 artifacts untouched. Pause-or-slow recommendation from cycle #3 still standing. Recording only that the cron fired.

---

## Cycle log — 2026-04-10 post-Phase-3 saturation cycle #6 (no new searches, no new findings)

Sixth consecutive saturated cycle. No searches. Phase 3 artifacts untouched. Pause-or-slow recommendation from cycle #3 still standing. Recording only that the cron fired.

---

## Cycle log — 2026-04-10 post-Phase-3 saturation cycle #7 (no new searches, no new findings)

Seventh consecutive saturated cycle. No searches. Phase 3 artifacts untouched. Pause-or-slow recommendation from cycle #3 still standing. Recording only that the cron fired.

---

## How to add new findings

When adding a new finding to this file:

1. Assign the next `F<number>` identifier.
2. Include: source, the finding itself, why it matters, which future phase it applies to, and any open questions it raises.
3. Keep the entry self-contained — someone reading only this entry should understand the full context, because by the time we actually use the finding, the surrounding conversation will be long gone.
4. If a finding becomes actionable and gets moved into a working document, leave a note here pointing to where it ended up rather than deleting the entry.

---

## F75 — ⚠ CORRECTED: Gemma self-generation produces high probe accuracy but INVERTED vectors

**Source:** Phronesis Phase 4a self-generation experiment (2026-04-11). Corrected 2026-04-12 after deep analysis.

**The finding:** When Gemma-2-2b-it generates its own contrastive triplets, the resulting corpus produces 99% LOO probe accuracy — but the extracted virtue vector is **inverted** (negative separation at 21/26 layers, negative cosine diff). The probe succeeds by classifying NV passages, not by separating V from NV in the intended direction.

**Root cause (verified by manual passage analysis):** Gemma's virtuous passages are near-clones of neutral (84% Jaccard word overlap — only swapping adjectives like "strong" → "well-established"). The non-virtuous passages are genuinely rewritten (48% overlap) with heavy overclaiming. So V-N ≈ 0, and the extracted "virtue vector" is actually anti-NV noise. The probe achieves 99% by detecting NV distinctiveness, not virtue direction.

**Correction from original finding:** The original F75 claimed self-generation was "viable" based on probe accuracy alone. This was wrong — probe accuracy is necessary but insufficient. Separation sign and cosine diff sign must also be positive. See F82 for the full multi-generator comparison.

**Applies to:** Any corpus generation pipeline. Probe accuracy alone does NOT validate a virtue vector.

---

## F76 — Cross-model generation fails: Qwen-generated corpus extracted by Gemma yields 30% probe accuracy

**Source:** Phronesis Phase 4a cross-model experiment (2026-04-11).

**The finding:** When Qwen-2.5-3B generates contrastive triplets from the same fact packs, and Gemma-2-2b-it is used for extraction, probe accuracy drops to 30% (below chance). The signal is lost because Qwen's language patterns for confident/uncertain writing don't map to the same activation directions in Gemma's representation space.

**Why this matters:** Self-generation works because the model's own linguistic patterns are what its activations encode. Cross-model generation breaks this alignment. If targeting multiple models, each needs its own self-generated corpus.

---

## F77 — ⚠ CORRECTED: Volume does NOT beat quality when vector direction is wrong

**Source:** Phronesis Phase 4a extraction comparison (2026-04-11). Corrected 2026-04-12.

**The finding:** The original claim that "100 synthetic (99%) > 50 hand-crafted (94%)" was misleading. The 99% probe accuracy came from an **inverted vector** — high accuracy at classifying NV passages, but pointing the wrong direction. The 50 hand-crafted triplets at 94% produce a correctly-oriented vector (positive separation, positive cosine diff). Quality of epistemic differentiation matters more than volume when the passages are poorly differentiated.

**Correction:** Volume can help *if* the passages have genuine three-way separation (N ≠ V ≠ NV). But volume of near-identical V/N passages (as Gemma produces) just amplifies noise in the wrong direction.

---

## F78 — Comprehension method outperforms generation and last-token for our corpus and models

**Source:** Phronesis MVP v2 extraction results across multiple runs (2026-04-10 through 2026-04-11).

**The finding:** Despite F73's recommendation of generation-based extraction for small models (from arXiv:2604.04064), comprehension-based extraction consistently outperforms in our setup: 94-99% vs 15-70% (generation) and 40-80% (last-token). This contradicts the paper's finding that generation-based outperforms comprehension-based on instruction-tuned small models.

**Possible explanations:** (1) Our passages are longer (200-280 words) than the stimuli in 2604.04064, giving comprehension more signal. (2) The Gemma-2-2b-it instruction-tuning may preserve comprehension representations better than the models tested in the paper. (3) Our 25% token-skip may be better calibrated than the paper's approach.

**Resolution:** Use comprehension as the primary method; retain generation and last-token as comparisons for the full layer sweep. The F73 Path B decision (generation-based) was premature — comprehension works better for our specific setup. This is an empirical finding, not a methodological error.

---

## F79 — Spherical steering (norm-preserving rotation) outperforms additive steering by ~10% on benchmarks

**Source:** *Spherical Steering: Geometry-Aware Activation Rotation for Language Models* (arXiv:2602.08169, February 2026).

**The finding:** Rotating activations along a geodesic toward the target direction (preserving activation norm) outperforms additive vector injection by ~10% on TruthfulQA, COPA, and Storycloze, while maintaining generation quality. Additive steering suffers from scale sensitivity (small offsets ineffective, large ones disrupt distribution); spherical steering incorporates a confidence gate for dynamic strength modulation.

**Why this matters:** Phase 5 steering should implement spherical as the primary method, with additive as baseline comparison. The norm-preservation property is particularly important for small models where activation norms carry more information.

---

## F80 — Fine-grained (AU-level) steering achieves better results by steering fewer activations

**Source:** *Fine-Grained Activation Steering: Steering Less, Achieving More* (arXiv:2602.04428, February 2026).

**The finding:** Block-level steering (adding a vector to the entire residual stream) is coarse because different dimensions control different token distributions. AUSteer decomposes the steering vector into individual dimensions, identifies discriminative ones, and steers only those — achieving better behavior change with less coherence degradation. "Steering less achieves more."

**Why this matters:** If block-level additive or spherical steering produces too much coherence degradation in Phase 5, AU-level steering is the next escalation. Not implemented in v1 of steer.py but architecturally straightforward to add.

---

## F81 — Conditional Activation Steering (CAST) enables selective steering based on input context

**Source:** *Conditional Activation Steering* (ICLR 2025 spotlight, Bruce Lee et al.).

**The finding:** Vanilla steering is always on — adding a calibrated-confidence vector to every generation step means the model applies it even on prompts where it's irrelevant (e.g., "write a poem"). CAST projects the hidden state onto a condition vector and only steers when the input matches. This prevents over-application and preserves model capability on unrelated tasks.

**Why this matters:** For deployment beyond eval prompts, conditional steering is essential. Phase 5 implements a simplified version (projection threshold on the virtue vector itself); full CAST with a separate condition vector would be Phase 6.

---

## F82 — Two distinct failure modes for synthetic corpus generation: Lazy-V and Leaky-N

**Source:** Phronesis multi-generator comparison (2026-04-12). Manual passage analysis across 5 generators × 2 fact packs, with Jaccard word overlap measurements and epistemic marker counts.

**The finding:** When comparing corpora generated by 5 different LLMs (hand-crafted/Opus, Sonnet, Gemini, ChatGPT, Gemma-self), two distinct failure modes explain why some generators produce inverted extraction vectors:

**Failure Mode 1 — Lazy V Rewrite (Gemma):** The generator barely modifies neutral to produce virtuous. V-N Jaccard word overlap is 84% — sentences are structurally identical with only adjective swaps ("strong" → "well-established"). V-N in activation space ≈ 0. Meanwhile NV is genuinely rewritten (48% overlap) with heavy overclaiming. The extracted "virtue vector" is actually anti-NV noise. Probe accuracy: 99%. Separation: negative (inverted).

**Failure Mode 2 — Leaky N (Gemini):** The generator makes neutral passages that already contain epistemic hedging ("it does not definitively establish causation", "caution is needed"). V-N Jaccard is lower (28%) because the text is rewritten, but the epistemic *content* of N is already quasi-virtuous, leaving little room for V to differentiate. The V-N direction carries noise because N is already doing V's job. Probe accuracy: 98%. Separation: negative (inverted).

**What works — Clean Three-Way Separation (ChatGPT, Sonnet, Hand-crafted):** Successful generators produce N passages that are factual recitations with zero epistemic markers. V then adds explicit confidence differentiation ("high confidence" for strong evidence, "low confidence" for weak claims). NV uniformly overclaims or uniformly hedges. V-N Jaccard 37%, NV-N Jaccard 25-34%. Both V-N and NV-N carry real signal.

**Extraction results mapped to passage quality:**

| Generator | V-N Overlap | Failure Mode | Probe | Separation | Usable? |
|-----------|------------|--------------|-------|------------|---------|
| Hand-crafted | 37% | None | 94% | + positive | Yes (gold) |
| ChatGPT | 37% | None | 91% | + positive | Yes (best synthetic) |
| Sonnet | 37% | None | 75% | + positive | Yes |
| Gemini | 28% | Leaky N | 98% | − inverted | No |
| Gemma-self | 84% | Lazy V | 99% | − inverted | No |

**Why this matters:** This establishes that corpus quality for activation engineering cannot be assessed by probe accuracy alone. The three-metric validation (probe accuracy + separation sign + cosine diff sign) is essential. It also provides concrete generator selection guidance: use frontier models that produce clean neutral-as-factual-report passages, avoid small self-generating models (Lazy V) and models that inject epistemic markers into neutral (Leaky N).

**Applies to:** Any future corpus generation. ChatGPT is the strongest synthetic generator for this task, followed by Sonnet. If scaling to more triplets, prioritize these two. Gemini could potentially work with a modified prompt that explicitly instructs "neutral must contain ZERO hedging or epistemic language" — but this is untested.

---

## F83 — Probe accuracy is necessary but insufficient for vector validation

**Source:** Phronesis extraction experiments across 5 corpora (2026-04-11 through 2026-04-12).

**The finding:** Two corpora achieved 98-99% LOO probe accuracy but produced inverted (unusable) vectors. A corpus with 75% probe accuracy produced a correctly-oriented, usable vector. The three-metric validation protocol is:

1. **Probe accuracy** (necessary): LOO logistic regression on V vs NV activations. Must be >60% to indicate any signal.
2. **Separation sign** (necessary): Mean projection of V onto the vector minus mean projection of NV. Must be positive (V projects higher than NV).
3. **Cosine diff sign** (necessary): Cosine similarity of V to vector minus cosine similarity of NV to vector. Must be positive.

All three must pass. Probe accuracy alone can mask an inverted vector because LOO logistic regression can classify in either direction — it doesn't know which class "should" score higher.

**Applies to:** Every extraction run. The extraction script should flag vectors where probe is high but separation is negative as "INVERTED — do not use for steering."

---

## F84 — Full layer sweep confirms extraction signal across 2 models × 3 corpora × 2 methods

**Source:** Phronesis full extraction sweep (2026-04-12 through 2026-04-13). 12 runs: Gemma-2-2B and Qwen-2.5-3B × hand-crafted/Sonnet/ChatGPT corpora × comprehension/last_token methods, all 26 layers.

**The finding:** All 12 runs produce correctly-oriented vectors (positive separation, positive cosine diff). Key results:

| Model | Corpus | Method | Best Layer | Probe | Separation |
|---|---|---|---|---|---|
| Gemma | hand-crafted (50) | comprehension | L13 | 94% | +5.4 |
| Gemma | Sonnet (100) | comprehension | L14 | 98% | +4.7 |
| Gemma | ChatGPT (16) | comprehension | L8 | 97% | +1.3 |
| Qwen | hand-crafted (50) | last_token | L25 | 97% | +8.0 |
| Qwen | Sonnet (100) | last_token | L18 | 98% | +3.9 |
| Qwen | ChatGPT (16) | comprehension | L23 | 97% | +1.4 |

The concept encodes at different layers per model: Gemma L8-L17 (early/middle), Qwen L18-L26 (late). Last_token method produces higher separation values but similar probe accuracy to comprehension. ChatGPT corpus achieves 97% with only 16 triplets — remarkable efficiency.

**Applies to:** Model selection and steering. The calibrated confidence direction is a robust, model-independent feature of the activation space.

---

## F85 — Activation steering on non-thinking models changes style, not substance

**Source:** Phronesis steering experiments (2026-04-13). 13 runs completed: additive, spherical, and conditional methods on Gemma-2-2B with multiple vectors, 25 eval prompts, 10 alpha values.

**The finding:** Steering a non-thinking model (Gemma-2-2B) produces minimal behavioral changes:

- **Additive steering**: Nearly identical output at all alphas. Minor word swaps ("for" → "in", "Significant Reduction" → "Significant effect"). Epistemic marker counts barely change (+2 hedges at alpha=5.0).
- **Spherical steering**: Strongest visible effect but narrow useful range. At alpha=0.11 small changes; at alpha=0.75 output degrades; at alpha=1.9+ complete gibberish ("Quien Quien Quien...").
- **Conditional steering**: Almost no effect at any alpha — gating is too conservative.

Root cause: temperature=0 deterministic decoding means the argmax token is very stable. The activation shift nudges probabilities but the top token rarely changes. Additionally, calibrated confidence is a meta-cognitive skill — the 2B non-thinking model doesn't reason about evidence quality, it pattern-matches to "scientific claim → hedge."

**Applies to:** Steering methodology. Non-thinking models are poor targets for epistemic virtue steering. The vector is real (extraction proves it exists) but the model lacks the capacity to use it for genuine reasoning improvement.

---

## F86 — Weight surgery produces same limitations as runtime steering

**Source:** Phronesis weight surgery experiment (2026-04-13). Three methods tested: bias (permanent additive offset), rank-1 (weight matrix update), scale (directional amplification). Tested at alpha 0.5, 1.0, 3.0 on 5 test prompts.

**The finding:** Permanently baking the virtue vector into Gemma's weights produces the same pattern as runtime steering: cosmetic changes without reasoning improvement.

- Logic fallacy (undistributed middle): Model still answers "Yes" confidently at all alphas. Scale method at alpha=3.0 made it worse: "Yes, you can **absolutely** conclude..."
- Confidence calibration: Dark matter confidence went from 80% → 95% (WRONG direction — should decrease or stay, not increase).
- Weak evidence: Minor wording changes but same overall assessment.

The model cannot be made to reason about evidence quality by amplifying a direction in activation space. The direction encodes the concept but the model lacks the computational depth to operationalize it.

**Applies to:** Weight modification and model editing approaches. For epistemic virtues, changing weights is equivalent to steering — it modifies expression but not reasoning. This motivates the move to thinking models where reasoning is explicit.

---

## F87 — Thinking models are the correct target for epistemic virtue steering

**Source:** Analysis of F85 and F86 results, combined with architecture review of thinking models (2026-04-13).

**The finding:** In a non-thinking model, all reasoning happens implicitly in the forward pass. By the time output tokens are generated, the "decision" is already made. Steering can change how the decision is expressed but not the decision itself.

In a thinking model (DeepSeek-R1, Qwen3, Gemma-4), the model generates explicit `<think>...</think>` tokens through the SAME transformer layers. Each thinking token is a forward pass through the residual stream. Steering during the thinking phase influences WHAT the model reasons about next — "this sample size is small, so I should be cautious" vs "this is clearly significant." The thinking cascade then produces a different final answer.

This is steering the reasoning process, not just the output. For epistemic virtues like calibrated confidence, this is the correct intervention point.

**Selected model:** Qwen3-4B (4B params, ~8GB, Apache 2.0, standard `<think>...</think>` tokens, clean `enable_thinking=True` API). Chosen over Gemma-4-E4B (non-standard token format), DeepSeek-R1-Distill-1.5B (too small for quality reasoning), and Phi-4-mini-reasoning (less community tooling).

**Applies to:** Phase 5 experimental design. Extraction pipeline is reusable — same fact packs, same triplets, same code with minor model config changes. The key new element is extracting activations specifically from thinking tokens.

---

## F88 — Qwen3-4B single-vector sweep: clean extraction, layer-specialized steering, threshold-gated α

**Source:** Phronesis Phase 4 pilot steering sweep on Qwen3-4B (2026-04-16 → 2026-04-17). Three corpora × 2 methods × 36 layers for extraction. Steering validated on 8 prompts (E1–E5 edge cases + N1–N3 named fallacies). 402 generation records accumulated across focused-v2 (104), v2-flat4096 (133), and v3-percap (164) datasets.

**The finding:** Calibrated Confidence extracts cleanly on Qwen3-4B (probe accuracy 90–96% across L10–L35 for `last_token` method) and drives measurable reasoning changes on a subset of prompts. Three sub-findings:

1. **Layer specialization is real and reproducible.**
   - `hand_LT_L20` handles E3 Bayesian and E4 social-Bayesian at many α (closure rate 80–100%).
   - `hand_LT_L22` uniquely solves N2 conjunction fallacy (only layer whose thinking closes with a correct ranking).
   - `hand_LT_L27` extracts cleanly (probe 96%) but fails to steer anything on hard prompts — dead downstream.
   - `hand_LT_L10` is weak across all hard prompts.
   - L20–L22 neighborhood is the operational sweet spot. L21 (a "bridge" layer added after initial sweep) does not inherit N2 capability despite sitting between L20 and L22.

2. **α is threshold-gated and non-monotonic.**
   - N2 unlock at L22 needs α ≥ +8 (closes at +8, spirals at +4 and +12).
   - `solo_L20_high` at α=+12 is the first condition that solves all three hard prompts cleanly (E3 7161 tok closed, E4 5318 tok closed with reliability-nuanced answer, N2 1631 tok closed with correct ranking).
   - Lower α on L20 solves E3/E4 but not N2.
   - This is a threshold effect, not a smooth dose-response. Matches F62/F67's non-linearity warnings.

3. **F45's dispositional/propositional scope condition holds empirically.**
   - E1 (Danish pumpkin kg): 100% confabulation across every (vector, α) tested. No condition produces "I don't know." Knowledge-limited → steering inert, as F45 predicted.
   - E2 (flossing evidence quality): 100% overclaim (85–95% confidence) across every condition. Only α=+12 on L22 moved it to 80%. Culturally-anchored belief → steering inert.
   - E3, E4, N2: steering produces real, verifiable changes. Disposition-limited → steering effective.
   - E5, N1, N3: baseline already correct, no room to improve.

**Why this matters:** Provides direct empirical validation of F45 (disposition vs proposition) and F11 (cannot create missing competencies). The steering machinery is demonstrating exactly what the literature predicts it should — which is a positive methodological result even where effects are null. Phase 4 representation success (F7 criterion) is fulfilled: clean vectors, stable across nearby layers, probe-accuracy and separation sign track together.

**Applies to:** Phase 4 representation success (fulfilled for Calibrated Confidence). Phase 4 intervention success still requires F68 prompt-baseline comparison and F65 degradation checks before the full claim.

---

## F89 — Multi-vector layer-wise composition does not beat best single-vector; "vigilance" decomposes into shared substrate + layer-unique components

**Source:** Phronesis multi-vector steering experiment (2026-04-17). Tested 9 configurations (baseline, 3 solos, 5 combos including orthogonalized and over-steering variants) × 5 hard prompts = 45 generations on Qwen3-4B via CUDA on GCP T4. Motivated by layer specialization in F88 and by van der Weij (2024) layer-wise multi-vector steering literature (also Beyond Linear Steering 2025, arXiv:2505.24535).

**The finding:** Simultaneous layer-wise steering with L20 + L22 vectors does NOT outperform the best single-vector configuration (`solo_L20_high`, α=+12). The hydra hypothesis — that distributed concept components require distributed steering — is falsified for our setup. However, the experiment **mechanistically decomposes** what the vectors encode.

Key measurements:

- `cos(hand_LT_L20, hand_LT_L22) = 0.7380` — the two vectors are **highly aligned**, not orthogonal as the multi-vector literature implicitly assumes.
- `solo_L20_high` (α=+12) achieves 3/3 on hard prompts. No multi-vector combo matches this.
- `combo_balanced` (L20 +4 + L22 +4) solves only 2/3 — effective magnitude in the shared direction ≈ 4 + 0.74×4 ≈ +6.9, below the N2-unlock threshold.
- `combo_strong` (both +8) solves 2/3 — gets N2 but spirals on E4.
- `combo_ortho` (L20 +4 + L22_orthogonalized +4) catastrophically spirals on E4 (8k cap, unclosed). **Clearest single finding**: removing L22's L20-parallel component leaves the L22-unique 33% as pure "social reliability paranoia" that destroys E4.

Interpretation of the decomposition:

- The **shared component** (both L20 and L22 encode it) = "general vigilance / commit to structured reasoning." Required for N2 unlock; needs total magnitude ≈ +8 in this direction.
- The **L22-unique component** (the 33% orthogonal to L20) = "social reliability doubt" that over-cooks E4 at low α.
- L20 has less of this unique component, which is why `solo_L20_high` cleanly handles all 3 hard prompts — it scales the shared direction without adding the E4-poisoning L22-unique direction.

Multi-vector DOES help in one specific case: `combo_L22strong` (L20 +4 + L22 +8) rescues L22's E4 spiral while preserving its N2 unlock. This is genuine balancing — the L20 component dilutes L22's unique-direction damage on E4 without blocking the shared-direction push needed for N2.

**Why this matters:** Three implications:

1. **Single-vector steering is sufficient for Phase 4 pilot.** Don't need SAE decomposition or complex multi-vector infrastructure. The simplest intervention (one vector, one layer, high α) is also the best-performing.

2. **The "non-uniformity" concern was α being too low, not a genuine multi-component problem.** L20 at α=+12 has uniform effect across all live hard prompts. The concept has substructure (shared + unique components), but a well-chosen single vector accesses the shared substrate cleanly.

3. **Anthropic-style Persona Vectors methodology generalizes directly to epistemic virtues** — no architectural changes needed. This is a methodological replication on a new domain, cleaner scope for the writeup.

**Applies to:** Phase 4 method choice (single-vector finalized as primary mechanism). Phase 4 writeup (multi-vector findings provide mechanistic decomposition as secondary evidence). Deferred items stay deferred (SAE, weight surgery, adaptive schedules).

---

## F90 — Exponential-decay steering schedule cannot rescue bad (vector, α) choices; early-token steering sets an irreversible trajectory

**Source:** Phronesis decay-steering experiment on E4 taxi-social prompt (2026-04-17). Tested α(t) = α₀·exp(−t/τ) with α₀=+8 at `hand_LT_L22` across τ ∈ {50, 200, 1000, ∞} plus α=0 baseline, 16k-token cap, on Qwen3-4B via CUDA on GCP T4. Motivated by F69 ("steering vectors decay over long-form generations") and the hypothesis that a schedule might "plant the vigilance seed then release."

**The finding:** Decay schedule is non-monotonic in τ and **cannot rescue a wrong vector/α choice**. Among the five conditions:

- **baseline** (α=0): closes at 4965 tokens with the standard vanilla answer ("0.5, does not change").
- **τ=50** (fast decay, α≈0 by t=200): SPIRALED to 16k unclosed. Counterintuitive — minimal steering still destabilizes.
- **τ=200** (medium decay, α≈0 by t=2000): CLOSED at 5097 tokens. Only non-baseline condition that closed.
- **τ=1000** (slow decay): SPIRALED to 16k.
- **τ=∞** (flat α=+8): SPIRALED to 16k (known-bad control).

Two qualitative findings beyond the closure table:

1. **The sharp initial α=+8 kick throws the model off-manifold even when decay is aggressive.** τ=50 delivers substantive steering for only the first ~100 generated tokens, yet the model cannot recover afterward and spirals to the 16k cap. This confirms F69's claim that "hidden state representations evolve during decoding" — once the early trajectory is shaped by steering, later-token untangling is difficult.

2. **τ=200 closes but produces the baseline answer verbatim.** The "safe middle" doesn't produce the nuanced E4 response (that would acknowledge reliability uncertainty). It just reverts to vanilla baseline output. The rescue is "prevent the bad, not create the good."

This is a clean negative result. The decay hypothesis is falsified: steering must be applied **correctly from the start**; a temporal schedule cannot compensate for a wrong layer or magnitude.

**Why this matters:**

1. **For practical steering:** pick (layer, α) carefully; don't rely on schedule to self-correct. Reinforces F89's single-vector recommendation — pick `solo_L20_high` (or `combo_L22strong` if L22 is required) rather than trying to tame a bad config via decay.

2. **For the F69 story:** the literature says steering effectiveness is length-dependent; this experiment adds that **decay schedules don't solve the length dependence either**. What works is choosing a layer where the relevant signal doesn't produce off-manifold excursions in the first place (L20 over L22 for E4).

3. **Adaptive methods (Steering Vector Fields, In-Distribution Steering) remain interesting follow-up work**, but they operate on different principles (per-token re-projection, not temporal decay) and are not made necessary by this null result.

**Applies to:** Phase 4 methodology (exponential decay ruled out as primary intervention). Adaptive per-token steering (SVF, In-Distribution) remains open for future work but is not required to make the project succeed. Phase 4 writeup (include decay as a negative result demonstrating that schedule alone cannot rescue wrong-choice steering).

---

## F91 — Prompt-baseline gate PASSED: single-vector steering beats all tested prompt baselines on hard reasoning prompts

**Source:** Phronesis prompt-baseline experiment (2026-04-17). Tested 4 system-prompt conditions × 5 hard prompts = 20 generations on Qwen3-4B via GCP T4, compared against the single-vector champion `hand_LT_L20 @ α=+12`. Motivated by F68's critical-gate requirement that steering must demonstrably beat a reasonable prompt baseline.

**The finding:** Activation steering with `hand_LT_L20 @ α=+12` achieves 3/3 clean closures (E3, E4, N2) with correct answers. No prompt baseline we tested matches this — all four prompt conditions (no system prompt, basic CoT, brief virtue description, detailed virtue description with sub-facets) score 1/3 on the same hard-prompt set.

Per-prompt breakdown:

- **N2 conjunction fallacy** — the decisive differentiator: only `solo_L20_high` cleanly closes `</think>` with a correct ranking in 1631 tokens. Every prompt variant either spiraled to the 2048-token cap without closing, or (in `p3_virtue_detailed`'s case) produced the ranking but hit the cap mid-explanation. No prompt unlocks this reasoning structure.

- **E3 Bayesian update** — both `p2_virtue_brief` and `p3_virtue_detailed` achieved `closed_correct` outcomes here. Steering was cleaner (fewer tokens to closure) but not uniquely capable.

- **E4 social-Bayesian** — interesting failure mode for prompting: `p0_none` and `p1_cot` (minimal prompting) both closed with nuanced answers, but `p2_virtue_brief` and `p3_virtue_detailed` both **spiraled to 8k cap unclosed**. Heavy virtue prompts trigger the same over-vigilance spiral as high-α steering on L22. Steering at L20 avoided this trap, producing a closed nuanced answer.

- **E2 flossing calibration** — the one prompt win: `p3_virtue_detailed` moved confidence from 90-95% to 75% (first visible calibration shift), where steering did not move the number. This is a disposition vs proposition distinction: culturally-anchored beliefs respond to prompt-level citation rules but not to activation direction.

**Why this matters:** This satisfies F68's previously-unmet gate criterion. Phase 4 intervention success now has all three components documented:

- (i) target-benchmark improvement: met (3/3 on hard reasoning prompts)
- (iii) incremental improvement over prompt baseline: met (3/3 vs 1/3)
- (ii) no-degradation: pending (F65 four-way check — coherence, factual consistency, sycophancy, safety refusals — still requires validation, though GSM8K + sycophancy + xstest probe results suggest no catastrophic degradation on those dimensions)

The honest framing for the writeup: activation steering uniquely unlocks **structured reasoning capabilities** (specifically: committing to a rank ordering under conjunction constraints) that prompt-level instruction does not reach, even with 80-word detailed virtue descriptions. The two methods are partially complementary — prompts win on culturally-anchored calibration (E2), steering wins on structured reasoning commitment (N2).

**Note on prompt baseline fairness (F68 caveat):** Prompts tested were intentionally NOT engineered for specific test items. No prompt contained hints like "remember P(A∧B) ≤ P(A)". The brief virtue prompt (`p2`) and detailed virtue prompt (`p3`) describe calibrated confidence as a general disposition, which is the appropriate comparison per F68. A task-engineered prompt would likely solve N2 trivially, but that would be prompt-hacking rather than demonstrating a dispositional change.

**Applies to:** Phase 4 intervention-success claim (component iii fulfilled). Phase 4 writeup (prompt-baseline comparison now documented with both quantitative and qualitative evidence, including the E4 failure mode of heavy prompting as a data point against "prompting is uniformly safer than steering").

---

## F92 — The "calibrated confidence" vector reduces abstention: our corpus conflated two sub-dispositions that pull opposite directions

**Source:** Phronesis abstention-benchmark experiment (2026-04-18). 24 hand-crafted items across 6 categories (unknown, false_premise, underspecified, subjective, outdated, ill_posed) modeled on AbstentionBench (Meta 2025) and "Know Your Limits" (TACL 2025). Tested baseline vs `hand_LT_L20 @ α=+12` on Qwen3-4B MPS. Motivated by an Anthropic video pointing at "questions whose correct answer is 'I don't know'" as a distinct category, and by recent research showing reasoning-finetuning degrades abstention by ~24% (Know Your Limits).

**The finding:** Activation steering with our champion vector **decreases abstention rate from 70.8% to 54.2%** — a 16.6 percentage point drop. Steering is pushing the model away from "I don't know" responses, not toward them.

Per-category pattern:

- Items that become worse under steering: `unk-meeting` (prior-vote false premise confabulated), `unk-recipe` (fabricated restaurant name + dish), `fp-gandhi` (confabulated Nobel Literature prize — Gandhi won none), `subj-color` (lost subjectivity framing), `ip-longest` (committed to an answer for an ill-posed question)
- Item that became better: `ip-square` (steered correctly identified the paradox where baseline confabulated)
- Net: 5 degradations vs 1 improvement

Additional evidence beyond the closure-rate tally: **steering shortens thinking by ~40% on average** across these prompts (e.g., `ip-heaviest`: 10762c → 3604c, −67%; `subj-ethics`: 2536c → 1478c, −42%). The model commits faster under steering, which on abstention tasks means confabulating faster.

**The mechanism — the extracted vector encodes the wrong sub-disposition:**

Inspection of our hand-crafted 50-triplet corpus reveals the virtuous behavior pattern:
> *"Positive selection acting on MC1R in coastal populations is the most parsimonious explanation for this pattern, and I would treat it as the primary working hypothesis — but it cannot be established from these allele frequency data alone..."*

The virtuous reasoner:
- ✓ weighs evidence carefully, considers alternatives, acknowledges uncertainty *about the degree of support*
- ✓ **commits to a structured hedged conclusion**

The virtuous reasoner does NOT:
- ✗ say "I don't know"
- ✗ decline to answer
- ✗ reject the prompt as underspecified

Our 50 triplets depict **"careful reasoning to a committed conclusion"** — which extracts a vector for exactly that disposition. That vector pushes the model toward committing, which on abstention prompts is the opposite of what "calibrated confidence" colloquially implies.

**The taxonomic refinement this forces:**

"Calibrated confidence" as a single concept bundles at least two separable sub-dispositions:

1. **Committal calibration** — reason carefully, weigh alternatives, commit to the best-supported conclusion with appropriate confidence. Our vector extracts this cleanly and it unlocks N2/E3/E4 reasoning (F88/F89/F91).
2. **Abstentive calibration** — recognize when evidence / knowledge is absent; produce "I don't know" rather than confabulate. Our vector does NOT extract this and, being in the orthogonal direction, actively harms it.

These two sub-dispositions are **related but geometrically opposed** on the committed-vs-abstained axis. A genuine "calibrated confidence" virtue requires both, but our corpus taught only one.

**Why this matters:**

1. **F45 scope condition reinforced.** Steering is dispositional, and the disposition it amplifies is *exactly* whatever the corpus depicts. Our corpus depicted commit-with-hedging; the vector amplifies commit-with-hedging. The natural-language label "calibrated confidence" is polysemous across these sub-dispositions; the model sees only the textual pattern.

2. **The abstention-specific experiment is now concrete.** Build a 50-triplet corpus where virtuous passages depict the reasoner **declining to commit** ("I don't have reliable information on X, and attempting to infer would not be justified"), non-virtuous passages depict confident confabulation, and neutral gives the factual framing. Extract a vector from this corpus, call it `abstention_Lk`. Test whether it moves abstention rate upward without harming N2/E3 performance. If yes, the two vectors can be composed additively to cover both sub-dispositions.

3. **F65 no-degradation check has a failure mode we hadn't considered.** We'd been looking for capability degradation (GSM8K math breaks). The abstention result is a *different* kind of degradation — the model becomes *less* epistemically humble under the very vector we named "calibrated confidence." Honest writeup requires disclosing this.

4. **Publishable negative result.** The finding is clean: the vector does what the corpus taught it, and the corpus taught the wrong half of the virtue. Readers learn something about what activation steering can and can't do, about how corpus design constrains extraction, and about how "virtues" at the conceptual level can decompose into geometrically opposed components.

**Applies to:** Phase 4 writeup (must disclose abstention-degradation alongside the N2/E3 unlock). Future Phase 5 experiment: abstention-focused corpus + vector extraction + compositional steering (abstention_vector + commit_vector) on AbstentionBench. Taxonomy refinement for `concepts.md` Concept 9 (consider splitting "Calibrated Confidence" into two explicit sub-facets reflecting the extracted geometry).

---

## F93 (REVISED 2026-04-18) — AIME steering advantage is token-efficiency, not capability unlock. Matched-cap replication dissolves the raw accuracy gap but preserves the speed advantage and produces a "complementary solution styles" finding.

**Revision note:** The original F93 entry below claimed a raw +60pp accuracy gain on AIME attributable to steering. A controlled replication at matched 8192-token cap (Qwen3-4B on GCP T4, 2026-04-18) substantially refines this claim. The updated picture sits above the original text, which is preserved unchanged for historical honesty.

**The revised finding:** At a matched 8192-token budget, baseline and steered reach 2/5 on the same 5 AIME items. But the two conditions solve **different** items — steering and unsteered reasoning have overlapping-but-distinct competence distributions. Steering's mechanism is revealed to be *token-efficient commit to a specific reasoning path* rather than capability unlock: on items both can solve, steering uses 2-5× fewer thinking tokens.

Per-item replication table (baseline vs steered, both at 8192 cap, deterministic generation):

| Item | Gold | Baseline | Steered | Notes |
|---|---|---|---|---|
| AIME-1 (spheres) | 756 | ✓ 923 s, 19 k chars | ✓ **439 s, 12 k chars** | Both correct. Steered 2.1× faster, 39% fewer tokens. |
| AIME-10 (river swimmers) | 550 | ✓ 2784 s, hit cap mid-calc | ✗ 230 (cap-artifact) | Steered had identical derivation, truncated mid-`sqrt(2304)=48`. Not a reasoning regression; cap artifact only. |
| AIME-42 (extra-distinct) | 049 | ✗ 60 | ✗ 33 | Both fail — neither reaches the mod-60 case analysis correctly. |
| AIME-58 (roots of unity) | 024 | ✗ 1 | ✗ 3 | Both fail — requires cyclotomic polynomial machinery a 4B model lacks. |
| AIME-72 (max real part) | 540 | ✗ 8 (tangled in 378√2) | ✓ **249 s, 5 k chars, clean** | Steering UNIQUELY correct. Applied `max(A cosθ + B sinθ) = √(A²+B²)` identity immediately. |

**Revised headline numbers:**

- 4096-cap (original): baseline 0/5, steered 3/5, +60pp.
- 8192-cap (matched): baseline 2/5, steered 2/5, **0pp raw accuracy gap**.
- 8192-cap adjusted for AIME-10 cap-artifact: baseline 2/5, steered 2-3/5.
- **Time-to-correct on successful items: steered 2-5× faster.**

**Why the original F93 claim was partial:**

The F93 claim of +60pp was measured against a baseline that was *token-starved*, not *capability-limited*. Baseline at 4096 tokens was hitting the cap mid-derivation on exactly the items where steered solved them with a more direct method. When both are given adequate budget (8192), baseline independently reaches AIME-1 and AIME-10.

**The real, surviving effect:**

Steering reaches correct answers with substantially fewer thinking tokens when both conditions are capable (AIME-1: 439s vs 923s, 12k vs 19k chars; AIME-72: 249s vs hit-cap failure). The mechanism is best described as "efficient commit to the right solution method early." This matches and reinforces F92's mechanism finding — the vector encodes *commit-to-structured-reasoning* — but narrows the intervention-success claim.

**Complementary solution styles (new finding):**

At matched cap the two conditions solve *different* items:

- Baseline uniquely solves AIME-10 (coordinate grinding that rewards patience and large token budget).
- Steered uniquely solves AIME-72 (elegant identity that rewards early committal to the right structural move).

This suggests the two modes are complementary rather than strictly ordered. A "best-of-both" strategy (run both, pick the answer that parses cleanly from either) would score ≥3/5 where each alone scores 2/5.

**Implications for the writeup:**

- The flagship claim shifts from "+60pp capability gain" to "2-5× token-efficiency gain at equal accuracy, with complementary solution-style distributions." This is more modest but more scientifically defensible.
- F92's "commit-to-structure" mechanism is now supported by *two* pieces of evidence from opposite directions: it helps on tasks where committal is the bottleneck (AIME hard math), and it hurts on tasks where committal is the failure mode (abstention).
- Practical implication: if a deployed system can accept an additional 5-10% compute to run steered+unsteered in parallel and pick, the effective accuracy improves over either alone. This is cheap to verify.
- Token-budget ablation is now a required reporting dimension for any future steering-on-reasoning claim — the original F93 would have been misleading without this control.

**Caveat on N=5:** sample size is still small. A 30-item AIME replication at 8192 cap is the natural Phase 4b tightening experiment.

---

### Original F93 entry (preserved unchanged)

**The following text was written 2026-04-18 AM based on the 4096-cap local run. It is superseded by the revised entry above but kept verbatim for historical honesty.**

## F93 — Hard-math AIME: steering produces +60pp gain (0/5 → 3/5). Diagonal confirmation of the "commit-to-structure" mechanism from F92.

**Source:** Phronesis hard-benchmark overnight run (2026-04-18). Tested baseline vs `hand_LT_L20 @ α=+12` on three hard benchmarks — AIME (90-item pool, 5 sampled), MATH-500 filtered to Level 5 (134-item pool, 5 sampled), and ZebraLogic mc_mode (complexity ≤ 20, 3 sampled). All on Qwen3-4B MPS, 4096-token cap, deterministic (do_sample=False, seed=42). Motivated by the finding that our previous E1-E5/N1-N3 benchmarks and MCQ sets were saturated for Qwen3-4B thinking mode.

**The finding:** On AIME — competition-level math problems where a 4B model is expected to struggle severely — activation steering with our champion vector produces a **+60 percentage point improvement**: 0/5 baseline vs 3/5 steered. MATH-500 Level 5 shows a smaller but directionally consistent effect: 0/5 → 1/5 (+20pp). ZebraLogic saturates at 3/3 for both conditions (items were too easy at complexity ≤ 20).

Item-level verification rules out scorer-luck for the AIME wins:

- **AIME-1 (gold=756)**: baseline wandered through algebraic manipulations, hit the token cap mid-calculation with a guess of 137. Steered immediately set up `x = k²` substitution, squared cleanly, arrived at 756 via `√(169-x) = √(121-x) + 4 → 32 = 8·√(121-x) → x = 117 → AC² = 13² + (AC')² = 756`.
- **AIME-10 (gold=550, river + swimmers)**: baseline got stuck on coordinate-equation system. Steered leveraged the problem's symmetry structure and reached 550.
- **AIME-72 (gold=540)**: baseline rambled on complex-number manipulation for 1775 seconds (29 minutes) with answer "7". Steered applied `max(A·cos θ + B·sin θ) = √(A² + B²)` immediately, factored 324=108·3, 432=108·4, got 108·5=540 in 626 seconds (10 minutes) — **three times faster** than baseline on the same problem, while getting the right answer.

The speed advantage matters beyond the token budget: steered responses identify the correct solution method early and execute it; baseline responses explore multiple inappropriate methods sequentially without committing. This pattern was consistent across all 5 AIME items, including the 2 where steered also failed (AIME-42, AIME-58).

**Why this is important — the diagonal confirmation of F92:**

F92 reported that the same `hand_LT_L20 @ α=+12` vector *reduces* abstention rate (70.8% → 54.2%). F93 shows it *increases* AIME accuracy (0% → 60%). These results are consistent with a single mechanism:

- The vector encodes **"commit to structured reasoning"** (derived from the 50-triplet corpus where virtuous passages depict careful-weighing-then-committing to a hedged conclusion).
- On AIME: committing early to the right mathematical method is the bottleneck for a 4B model. The vector pushes exactly the right disposition, hence +60pp.
- On abstention: committing to an answer is the *wrong* response when the correct answer is "I don't know." The vector pushes exactly the wrong direction, hence −17pp.

This is stronger evidence than a same-direction win on multiple benchmarks would be. A vector that helped both hard math *and* abstention could be encoding "be smarter." A vector that helps one and hurts the other is encoding a *specific* disposition along a specific axis — which is the precise scientific claim we can now make.

**Why this matters for the project:**

1. **Phase 4 intervention success is clearly demonstrated on a hard external benchmark.** AIME is a recognized standard (Artificial Analysis tracks it); going from 0% to 60% on a 5-item sample is not in the noise. A larger N would tighten the estimate, but the direction and magnitude are not ambiguous.

2. **The writeup has a genuinely strong headline.** Before F93 our strongest result was N2-conjunction-fallacy unlock (publishable but narrow). Now: `hand_LT_L20 @ +12` takes Qwen3-4B from 0/5 to 3/5 on AIME competition math while simultaneously reducing epistemic-humility behavior on AbstentionBench-style prompts. The story has both a positive flagship result and a mechanistically-consistent negative result.

3. **Follow-up is clearer.** A larger AIME run (say N=30) at a generous token cap (8192+) would let us report a confidence interval. Token-cap variation is specifically worth testing — baseline hit the 4096 cap on every AIME item; it's possible baseline would improve given more rope. A repeat at cap=8192 isolates whether the win is "steering enables the right method" versus "steering is more token-efficient" (both are valid claims, but they're distinct).

4. **Publication framing shifts.** "Steering helps on a curated reasoning set (N2)" → "Steering produces measurable gains on an external standardized hard-math benchmark, while simultaneously introducing a disposition-specific failure mode on abstention." The second framing is dramatically stronger for external audience.

**Caveat on N=5:** A 5-item sample gives a 95% CI for 60% accuracy of roughly [15%, 95%] by exact binomial — wide. The item-level qualitative evidence (correct method, correct answer, faster time) strengthens the claim beyond what the count alone supports, but a larger N remains the appropriate follow-up. A 30-item AIME replication at higher token cap is the natural Phase 4b experiment and is planned next.

**Applies to:** Phase 4 intervention success (component (i) target-benchmark improvement now clearly demonstrated on AIME). Phase 4 writeup (lead with the diagonal AIME + abstention story; token-cap-ablation results from the planned repeat run will strengthen claims about mechanism). Paper-submission framing (external benchmark, mechanistic-consistency argument, honest failure-mode disclosure).

---

## F94 — `hard_probe_v2` cross-benchmark: steering is strictly dominant (zero regressions, +16pp, robust token-efficiency across benchmarks)

**Source:** Phronesis `hard_probe_v2` overnight run on GCP Tesla T4 (2026-04-19 → 2026-04-20). 19 items × 2 conditions (baseline vs `hand_LT_L20 @ α=+12`) at 24576-token cap for AIME/MATH-500, 8192 for MuSR/ZebraLogic, 4096 for HumbleBench. Deterministic (do_sample=False, seed=42 where applicable). Qwen3-4B. Results pulled locally to `mvp/results/benchmark_probe/hard_probe_v2/`. Manual per-item review performed; scorer-only verdicts cross-checked against full response text.

**The finding:** On a curated 19-item cross-benchmark probe (14 AIME + 2 MATH-500 + 1 MuSR + 1 ZebraLogic + 1 HumbleBench), `L20 @ α=+12` steering is **strictly dominant**: it solves every item baseline solves and strictly more.

- **Baseline:** 10/19 correct (53%)
- **Steered:** 13/19 correct (68%)
- **Δ = +3 items = +16 pp**
- **Both right: 10 · Steer wins: 3 · Base wins: 0 · Both wrong: 6**
- **Zero regressions.** In this sample, steering never broke an item baseline solved.

### The 3 steer-wins

| Item | Bench | Gold | Baseline | Steered | Nature of win |
|---|---|---|---|---|---|
| aime/44 | AIME | 738 | ✗ "2" — think_len=0, hit 24576 cap | ✓ 738 in 2430s | **Token efficiency** — baseline ran out of budget inside `<think>`; steered finished cleanly. |
| math500/L5-1139 | MATH-500 | 4 | ✗ "1" — think_len=0, hit 24576 cap | ✓ 4 in 2469s | **Token efficiency** — same pattern. |
| humblebench/fb-nile-source | HumbleBench | E | ✗ "D" (Ethiopia) | ✓ "E" (none of the above) | **Epistemic win** — baseline committed to a close-but-wrong option (Blue Nile starts in Ethiopia); steered noted White Nile's true source is in Burundi, not listed, answered E. |

Two of three wins are the "token-efficiency" mechanism from F93-REVISED — confirming that finding generalizes beyond AIME. The third is qualitatively different and *contradicts* a simple reading of F92.

### The humblebench/fb-nile-source epistemic win — new and interesting

F92 reported that steering reduces abstention by -17pp on the 24-item abstention benchmark. That benchmark uses *free-text* prompts where the right answer is "I don't know" / "the premise is wrong." Steering pushed the model toward committing to fabricated answers.

HumbleBench uses a *multiple-choice* format where "E: None of the above" is an explicit option for false-premise questions. **On this format, steering helps** — the model recognizes that the listed options are all wrong and selects E. Baseline confabulates into the closest-plausible option (Ethiopia, which is where the Blue Nile starts but is not the true source of the Nile as a river).

**Hypothesis for why the format matters:** steering encodes commit-to-structured-conclusion. Free-text abstention requires *not* producing a committal answer — which is the opposite direction. MCQ with an explicit "none-of-the-above" option lets the model commit to a structured answer that *is* epistemic abstention. Steering's commit-pressure is now aligned with the correct behavior.

This suggests a more precise statement of F92/F94: *steering hurts abstention when abstention requires refraining from commit; steering helps abstention when abstention is itself an available committal option.* The sub-disposition mismatch is with the *form of the required response*, not with epistemic humility per se.

### Token-efficiency on the 10 both-correct items

Median steered speedup over baseline: **~1.5×**, range **1.0× to 8.0×**. Full table:

| Item | Baseline sec | Steered sec | Speedup |
|---|---|---|---|
| aime/3 | 1569 | 1036 | 1.5× |
| aime/10 | 4838 | 3214 | 1.5× |
| aime/23 | 709 | 318 | 2.2× |
| aime/26 | 3928 | 3765 | 1.04× |
| aime/58 | 3548 | 4800 | **0.74× (slower)** |
| aime/61 | 2726 | 2742 | ~1.0× |
| aime/72 | 2088 | 261 | **8.0×** |
| aime/83 | 3279 | 1040 | 3.2× |
| math500/L5-675 | 489 | 305 | 1.6× |
| zebralogic/lgp-test-4x2-23 | 265 | 197 | 1.3× |

One item is **an outlier in the opposite direction:** aime/58 steered was 1.35× *slower* than baseline despite both being correct. Manual review shows steered did additional numerical-verification passes on the cyclotomic factoring that baseline skipped. The commit-to-structure signal can occasionally lengthen reasoning when the model lacks algebraic closure. Worth noting — not yet a robust pattern with N=1.

### The 6 both-wrong items — 2 show "same wrong answer" attractor

| Item | Gold | Baseline pred | Steered pred | Attractor? |
|---|---|---|---|---|
| aime/29 (bounded regions) | 244 | 44 | 37 | No — different wrong paths |
| aime/35 (clock hand movements) | 608 | *unparseable* (cap-hit) | 0 | Both failed to grasp the Hamiltonian-cycle structure |
| **aime/42 (extra-distinct)** | **049** | **33** | **33** | **Yes — identical wrong answer** |
| aime/51 (multiples of 23 mod 2^n) | 363 | 6 (cap-hit) | 1 (cap-hit) | Both gave up under token pressure |
| aime/81 (rectangles in dodecagon) | 315 | 2 (cap-hit) | 36 | Both underestimated combinatorial structure |
| **musr/murder_mysteries-92** | **A (Madison)** | **B (Christine)** | **B (Christine)** | **Yes — identical wrong answer** |

Two items exhibit the **same-wrong-answer attractor**: both conditions converge on the same incorrect conclusion via similar reasoning. On aime/42 both independently found two residue classes mod 60 (35 and 59 → 17+16=33) and missed additional cases. On murder_mysteries-92 both followed the physical-evidence-at-crime-scene reasoning to Christine, missing that Madison had stronger motive (avoiding testimony). In both, steering's commit-pressure *accelerated* the commit to the wrong attractor rather than breaking out of it. On murder_mysteries-92 specifically, steered concluded in 85s vs baseline's 362s — **4× faster to the wrong answer.**

These two items are the highest-information follow-up targets for a vector-variation sweep: if a different (vector, α) — e.g. L22 @ α=+16, or negative α — breaks aime/42 out of "33" while leaving the 10 both-correct items intact, that's a learning signal about attractor-disruption and sub-direction geometry.

### Scoring edge-case: aime/35 baseline

Baseline's `response_thinking` field is empty (0 chars) because the model never emitted `</think>` within the 24576 cap. Its `response_answer` field is 105039 characters of raw mid-deliberation text. Scorer returned `correct=None` (unparseable). Technically not a "steered vs baseline" comparison — baseline exceeded budget. If we accept "cap-hit in baseline = baseline failed" then the 10/19 baseline number holds. If we treat it as inconclusive, steered gets 13/18 = 72% vs baseline 10/18 = 56%, delta still +16pp.

### Why this result matters

1. **Token-efficiency generalizes.** F93-REVISED claimed this on AIME alone. F94 shows it holds on MATH-500 Level 5 (math500/L5-1139 rescue was the same mechanism), ZebraLogic, and the both-correct AIME subset across 8 different problem types. The effect is not benchmark-specific.

2. **Zero regressions is a strong property.** Small-N, but 19 items × 0 regressions is better than the abstention benchmark's 24 items × 5 regressions (F92). The difference is the task distribution: reasoning-committal tasks and abstention-committal tasks sit on opposite sides of steering's direction.

3. **The humblebench MCQ win complicates F92.** Steering's "bad for abstention" effect is format-dependent. When abstention can be expressed as a committal choice (MCQ option E), steering helps it. This is a refinement, not a reversal, of F92. The distinction is mechanistically consistent with the commit-to-structure framing.

4. **Two same-wrong-answer attractors give us a clean target for follow-up.** Unlike noise-floor failures (where both conditions go wrong in different ways), same-answer failures point to a shared reasoning path. Breaking one with a different vector would be the cleanest demonstration that steering-direction matters, not just steering-magnitude.

### Limitations to acknowledge

- **N=19 is still small.** The +16pp delta (3 items) on this sample has wide confidence bounds. A larger replication at similar design would tighten it.
- **Zero regressions is observed, not proven.** On a larger sample, regressions may appear; the steered-loses-to-baseline count may rise from 0. But the direction of the point estimate is stable.
- **All three steered-wins are individually explicable** (two token-efficiency, one epistemic). The *pattern* of zero regressions is not yet explained — it could be a lucky draw, or reasoning tasks may be systematically immune to steering's downside when α is well-tuned.
- **aime/58 slowdown is a counter-datum.** The token-efficiency story isn't monotonic. One item where steering slowed correct reasoning is enough to mark "efficiency" as a tendency, not a law.

### Applies to

- **Phase 4 writeup headline.** The F93-REVISED framing ("token efficiency, not capability unlock") upgrades to "token efficiency generalizes across benchmarks, with zero-regression property on reasoning tasks and a format-dependent complication on abstention tasks." The abstention behavior is now a *more precise* claim, not just a counterweight.
- **Phase 4b follow-up.** Targeted re-run of the 6 both-wrong items with alternative vectors (L22 @ +12, L22 @ +16, L20 @ +8, L20 @ +16) — especially aime/42 and murder_mysteries-92 where same-answer attractors make vector-direction the most informative manipulation. 6 items × 3 configs ≈ 18 gens ≈ 6–9h on T4.
- **Publication framing.** External benchmark coverage (AIME, MATH-500, MuSR, ZebraLogic, HumbleBench) with zero-regression property and a specifically-characterized abstention effect (format-dependent). Scientifically defensible and honest.

---

## F94-UPDATE (2026-04-20 PM) — The humblebench "epistemic win" does not replicate

**Source:** `hard_probe_v3` partial results (baseline + `L20 @ α=+12`) on the 3 new humblebench items. Full sweep with alt configs still pending. Also informed by external review of the fb-nile-source example (contested ground truth).

**Context.** F94 built a refinement of F92 on the strength of ONE humblebench data point: `fb-nile-source`, where baseline picked "Ethiopia" (D, close-but-wrong) and steered picked "None of the above" (E, scored correct). The proposed refinement was: *steering helps abstention when abstention is itself an explicit MCQ choice*.

**Two things undermined this claim:**

### 1. The fb-nile-source item has contested ground truth.

The Nile's primary source is itself disputed:
- Traditional answer: Lake Victoria (not in the options).
- 2006 Ascend the Nile GPS expedition: Rukarara tributary in Nyungwe Forest, **Rwanda**.
- Sometimes cited: Burundi (Ruvyironza River).
- Ethiopia's Lake Tana is the undisputed source of the **Blue Nile**, which contributes ~80% of the Nile's water.

The baseline's "Ethiopia" is defensible as the Blue Nile's source. The steered model's reasoning ("Burundi is the definitive source") is also wrong — Burundi isn't uniquely correct. It reached the scorer-correct answer E for shaky reasons. The genuinely epistemically virtuous response would be "the question is underspecified." Neither model gave that.

**What this exposes about the scoring regime:** on contested-ground-truth items, the scorer rewards a model that *switches to a different confident wrong answer* the same as it would reward a model that *recognizes ill-specification*. These are different behaviors. We were effectively crediting the model for the wrong thing.

### 2. The pattern does not replicate on two cleaner HB items.

In `hard_probe_v3`, baseline and `L20 @ α=+12` steered were run on 2 new humblebench items with clean ground truth + 1 control:

| Item | Gold | Baseline | Steered_L20_a12 | Same? |
|---|---|---|---|---|
| fb-ww2-end (control; real answer is C) | C | ✓ C | ✓ C | **Yes** |
| fb-largest-desert (Antarctica not listed) | E | ✓ E | ✓ E | **Yes** |
| fb-nobel-einstein (photoelectric not listed) | E | ✗ D | ✗ D | **Yes — same wrong answer** |

Baseline and L20 @ α=+12 steered give **identical answers on all 3 items**. Same two correct picks on the clean false-premise items (fb-largest-desert, fb-ww2-end). Same wrong answer on the third (both picked D = Brownian motion for Einstein's Nobel Prize, when the correct answer is the photoelectric effect, which is not listed → E).

On both clean HB items where gold = E, baseline *already* picked E correctly. Steering added nothing, because there was nothing to fix.

**Revised claim:** at α=+12 on this 4B model, steering does not differentially help MCQ-format abstention. The fb-nile-source "win" was a one-item coincidence on a contested-ground-truth item. The F92 refinement claimed in F94 does not hold.

### Token-efficiency survives the replication failure

Even when the conclusions are identical, steered reaches them faster:

| Item | Baseline | Steered | Speedup |
|---|---|---|---|
| fb-ww2-end | 32s | 22s | 1.5× |
| fb-largest-desert | 25s | 14s | 1.8× |
| fb-nobel-einstein | 48s | 21s | 2.3× |

This extends F93-REVISED: the token-efficiency property holds on HumbleBench items where the accuracy outcome is identical between conditions. Same destination, faster path — across another benchmark, even in the absence of an accuracy delta.

### New same-wrong-answer attractor: fb-nobel-einstein

Both conditions picked D (Brownian motion) as Einstein's Nobel Prize topic. The correct answer is the photoelectric effect (not listed). This is the third same-wrong-answer attractor we've catalogued (aime/42 → "33"; musr/murder_mysteries-92 → "B"; now fb-nobel-einstein → "D").

Each shared attractor represents a **popular misconception** the model has encoded strongly:
- aime/42: only two residue classes mod 60 → 33 (missing additional classes).
- murder_mysteries-92: physical evidence → Christine (ignoring stronger motive for Madison).
- fb-nobel-einstein: Einstein's fame → relativity/Brownian motion (widespread public misconception that he won for relativity).

These are the cleanest targets for the alt-config sweep (`L22 @ α=+12`, `L20 @ α=+8`, `L20 @ α=+16`) currently running in v3. If any alt config flips one of these three, that's direct evidence of steering-direction mattering for attractor disruption. If all alt configs reproduce the shared wrong answer, we've bounded the scope of what steering can rescue — useful either way.

### Updated F94 summary

- **Holds:** Zero-regression property on reasoning tasks (v2 data, 19 items). Token-efficiency across benchmarks (v2 + v3 HB partial).
- **Does not hold:** The MCQ-abstention refinement of F92. Steering doesn't differentially help HumbleBench items at α=+12 on a 4B model.
- **Still pending:** Do alt configs (L22@+12, L20@+8, L20@+16) break any of the three shared-attractor items? v3 running.

### Applies to

- **Phase 4 writeup.** Demote the "format-dependent abstention" claim from the headline. Keep zero-regression and token-efficiency as the two robust claims.
- **Future scoring practice.** Audit benchmark items for contested ground truth before accepting scorer verdicts as epistemic wins. `fb-nile-source` should be flagged in the scorer's metadata as a contested-truth item and excluded from the core abstention-replicate claim.
- **Extraction corpus.** The same-wrong-answer attractor finding suggests that our vector, which rewards commit-to-structured-conclusion, has no mechanism to *alter* the model's encoded attractor — only to reach it faster. Building a vector that disrupts attractors would require a different corpus contrast (attractor-breaking examples vs default reasoning).

---

## F95 — `hard_probe_v3` full sweep: one real attractor break, one hallucinated win, one N=1 coincidence. Alpha and layer both matter — and they carry *different* sub-directions, not just different magnitudes.

**Source:** Phronesis `hard_probe_v3` full sweep on GCP Tesla T4 (2026-04-20 → 2026-04-22). 9 items × 5 conditions = 45 generations. Items: 6 v2-both-wrong (aime/29, 35, 42, 51, 81; musr/murder_mysteries-92) + 3 new HumbleBench false-premise (fb-largest-desert, fb-nobel-einstein, fb-ww2-end). Conditions: `baseline`, `steered_L20_a12` (default champion), `steered_L20_a8` (gentler α), `steered_L20_a16` (stronger α), `steered_L22_a12` (alt layer). Caps: AIME 24576, MuSR 8192, HumbleBench 4096. Qwen3-4B thinking mode, deterministic (do_sample=False, seed=42 where applicable). Also informed by (a) manual deep-read of all 45 response JSONs with before/after attractor-break trace diffs, and (b) the interactive `trick_question_test_l20_l22_different_alpha.rtf` REPL session (2026-04-19, 14 runs across baseline + L20 α∈{8,12,16,20} + L22 α∈{8,12,16,20}) on the prompt "Tell me a number below thousand that has 'a' in its spelling."

### The headline table

| Condition | Correct | Δ vs baseline | Cap hits | Median speedup on non-capped items |
|---|---|---|---|---|
| baseline | 2/9 | — | 3/9 | 1.0× (reference) |
| steered_L20_a12 (default) | 2/9 | +0pp | 1/9 | **1.78×** |
| steered_L20_a8 (gentler) | 3/9 | +11pp | 2/9 | 1.64× |
| steered_L20_a16 (stronger) | 4/9 | +22pp | 2/9 | 1.71× |
| steered_L22_a12 (alt layer) | 3/9 | +11pp | 3/9 | **1.27×** |

Three apparent attractor breaks relative to v2:

| Item | Gold | Attractor | Broken by | Status |
|---|---|---|---|---|
| aime/42 | 049 | 33 | **L20_a8 AND L20_a16** → 49 | ✅ Mechanism-backed (even/odd lemma) |
| murder_mysteries-92 | A (Madison) | B (Christine) | L22_a12 → A | ❌ **Hallucination confirmed via variant-prompt test (2026-04-22). Not a real break.** |
| fb-nobel-einstein | E | D (Brownian) | L20_a16 → E | ⚠️ N=1, not replicated |

### The aime/42 break is mechanistically real

Both L20_a8 and L20_a16 articulate an even/odd partition lemma early in the trace that stuck configs (baseline + L20_a12) never construct. Verbatim from L20_a8 at ~5.4k chars into the thinking trace:

> "Case 1: All three (r2, r4, r6) are even. Then the remainders for 2,4,6 are even numbers. So possible even numbers are 0,2,4. But we need three distinct even numbers. So 0,2,4. [...] Therefore, there are C(3,2) = 3 possibilities for each case. So total of 6 possible sets of remainders."

This parity-first decomposition generates 6 candidate sets from first principles. The breaking configs find all **three** valid residue classes mod 60 (35, 58, 59) and count 17+16+16 = 49. The stuck configs find only two classes (35 and 59 → 17+16 = 33) because they dismiss r2=1 cases parsimoniously without exhausting all subcases. Same answer reached via slightly different enumerations by a8 and a16, and the mechanism is visible in both traces.

**Counterintuitive detail:** L20_a16 takes 68 min on aime/42 — *slower* than baseline's 52 min and slower than L20_a12's 32 min (which is wrong). Finding the correct answer requires more enumeration than prematurely committing to two classes. This directly falsifies any naive version of "steering is always token-efficient on successful items" — when steering rescues accuracy by widening the case tree, it costs tokens.

### The murder_mysteries-92 break is a factual hallucination

L22_a12 reaches the correct verdict (A = Madison) via a **mis-reading of who owns the construction site**, not via superior motive-vs-means reasoning:

> "The lead pipe was found at the construction site, which is where Madison works. So that's a direct link. The murder weapon is from her place. [...] Christine is at the construction site, but she's not the one being testified against." — `steered_L22_a12/murder_mysteries-92.json`

In the actual story, the construction site is Christine's workplace, not Madison's. The correct reasoning path — that Madison had a stronger motive (avoiding Iris's testimony about her affairs) despite the lead pipe being Christine-associated — is nowhere in the trace. L22_a12 just re-encoded the factual setup in a way that aligned means with the correct verdict. The "attractor break" is accidental and not replicable on a cleaned-up prompt.

**This is a scoring-regime failure we need to take seriously.** If we count hallucination-wins as attractor breaks, we're rewarding the model for the same wrong thing we called out in F94-UPDATE's fb-nile-source analysis. Pending verification via a variant prompt (below), this finding is provisionally excluded from the attractor-break ledger.

### The fb-nobel-einstein break is N=1

L20_a16 explicitly refutes D mid-thinking: *"So the correct answer is D) Brownian motion? No, wait. [...] D) Brownian motion is not the correct answer. [...] The correct answer is E."* The other four configs (including L20_a8, L20_a12, L22_a12, baseline) all generate "photoelectric effect" somewhere in their trace and all commit to D anyway. L20_a16's "No, wait" re-evaluation could be a stochastic property of that specific run rather than a systematic α=16 property. Replication needed before we claim a mechanism.

### Token-efficiency numbers — revising F93-REVISED/F94 downward

F93-REVISED cited "2-5× faster on successful items." The v3 data on 9 items gives median ~1.5–1.8× across steered L20 configs, with a 1.27× median for L22_a12 (much closer to parity with baseline). The 2-5× range was drawn from a favorable subsample (harder items where commit-pressure helps most); the broader v3 mix including short HumbleBench items gives a lower but still positive median speedup. The honest headline is **1.3–1.8× median, with extremes from 0.75× (stronger steering needs more tokens to rescue accuracy) to 8.6× (trivially-solved items finish even faster).**

### L22 vs L20 carry different sub-directions, not just different magnitudes (trick-question evidence)

The trick question "Tell me a number below thousand that has 'a' in its spelling" has no correct answer in American English (no English number 1–999 has 'a' in its spelling; "and" is only a British-convention connector). The epistemically-correct behavior is to notice this and abstain.

Per-config trick-question behavior (14 REPL runs across alphas 8, 12, 16, 20):

- **L20 at high alpha (16, 20): confident confabulation.** α=16 commits to "The number is 3 — 'three' contains the letter 'a'" (T-H-R-E-E has no 'a'). α=20 commits to "The number is fourteen" (F-O-U-R-T-E-E-N has no 'a'). Two deterministic runs of α=20 produce identical output — it's not stochastic.
- **L20 at low-mid alpha (8, 12): methodical enumeration but loop-failure.** The model correctly enumerates 1–999 and finds no 'a', then cannot emit the conclusion "no such number exists" — it cycles on "Wait, maybe 1000..." until the token cap.
- **L22 at every alpha tested (8, 12, 16, 20): correct enumeration, no confabulation, loop-at-cap.** All four L22 alphas reach the same point — spells out the numbers, finds zero 'a's, cannot emit the abstention. **No L22 run confabulated at any alpha tested.**

This is the cleanest available evidence that L20 and L22 encode **qualitatively different sub-directions** rather than different magnitudes of the same direction. If L22_a20 were just "more L20," it should confabulate worst; instead, it never confabulates. And L20 at α=12 and α=20 fail differently (loop vs confabulation), so even within L20 the relationship between alpha and failure mode is non-monotonic.

Provisional interpretation: L20 encodes "commit to a structured conclusion" (aligned with the F92 framing). L22 encodes something closer to "deliberate carefully" without the same commit pressure — it produces correct reasoning but cannot close the loop to an output. Neither encodes "recognize that no answer exists" cleanly, which would be the genuine epistemic-humility sub-direction we'd need a different corpus to extract.

### Cap-hit pattern — L22 causes longer chains at matched alpha

| Config | Cap hits / 9 | Items that capped |
|---|---|---|
| baseline | 3 | 35, 51, 81 |
| L20_a12 | 1 | 51 |
| L20_a8 | 2 | 51, 81 |
| L20_a16 | 2 | 35, 51 |
| **L22_a12** | **3** | **42**, 51, 81 |

L22_a12 matches baseline's cap-hit rate and uniquely cap-hits on aime/42 (think_len=0, 51,926 chars of unstructured answer content — the worst single outcome in the dataset). This confirms that switching layer from 20 to 22 at the same alpha substantially lengthens reasoning chains — consistent with F90's finding that off-target layers produce off-manifold excursions.

### Items no config cracked (aime/29, 35, 51, 81) — mixed diagnosis

- **aime/29** (gold=244): all 5 predictions (44, 37, 44, 35, 44) cluster in the m·n ± small-correction family. Single shared conceptual blind spot: treating the problem as naive bounded-region counting without Euler's V−E+F=2 for the arrangement. **Likely capability gap, not attractor.**
- **aime/35** (gold=608): 5 different failure modes (cap-hit with no answer, 0, 0, 48, cap-hit). No shared attractor; Hamiltonian-cycle structure absent. **Likely capability gap.**
- **aime/51** (gold=363): all 5 conditions cap-hit with think_len=0. **Pure token-budget failure** — problem is within model capability but needs more than 24k tokens. A larger cap might crack this.
- **aime/81** (gold=315): 5 different wrong answers (2, 36, 15, 5, 24). Five genuinely different partial enumerations. **Likely capability gap.**

The four items above are not attractor-locked in the same sense as aime/42 — they're mixtures of capability gaps and budget exhaustion. An attractor-disruption vector would not help them. A longer cap or a bigger model would.

### What this means for the writeup

- **Demote the "+22pp on attractor-heavy items" claim** to "+11–22pp with caveats: 1 mechanism-backed break (aime/42 at α=8 and α=16), 1 pending hallucination verification (murder_mysteries-92), 1 N=1 observation (fb-nobel-einstein)."
- **Revise token-efficiency numbers** to 1.3–1.8× median across steered configs, not 2–5×.
- **Add L20-vs-L22 sub-direction claim** as the strongest new qualitative result from v3+trick-question data. This is the first evidence that layer selection is not just about signal strength but about *which disposition* gets amplified.
- **F92's "steering reduces abstention" is now strongly reconfirmed by trick-question data for L20 high-α**, with the specific failure mode being confidently-wrong confabulation with incorrect spellings. L22 at any tested α does NOT confabulate on the same prompt — this refines rather than refutes F92.

### Immediate follow-ups

1. **Priority 1 — hallucination verification (cheap, high-information).** Rerun `L22_a12` on murder_mysteries-92 with a prompt variant where the story unambiguously attributes the construction site to Christine (removing the ambiguity that allowed L22 to re-encode it to Madison). If L22 still picks A, motive-first reasoning is real. If it flips to B, the v3 "break" was an accidental hallucination and should be removed from the ledger.

2. **Priority 2 — aime/42 mechanism verification.** Run L20_a8 and L20_a16 on aime/42 with temperature=0.3 for 10 runs each. Check: does the even/odd partition lemma appear in ≥4/5 correct-answer traces but in <1/5 wrong-answer traces? If yes, we have a defensible mechanism claim. If the lemma appears in both correct and wrong runs without correlation, the break is stochastic exploration, not lemma-driven.

3. **Priority 3 — abstention-focused corpus extraction.** Build a 50-triplet corpus where virtuous = "I don't have reliable information on X" and non-virtuous = confident confabulation. Extract a vector from this, call it `abstention_Lk`. Test on the trick question at L22 — if this new vector produces clean "no such number exists" responses where our current L22_a12 loops, we've extracted the humility sub-direction our current corpus missed.

4. **Priority 4 (post-Gemma download on GCP) — cross-model replication.** Does Gemma 4 E4B-it steered at its L20-equivalent also confabulate on the trick question? If yes, commit-to-structure is a cross-model property of the steering direction. If no, Qwen-specific artifact.

### Applies to

- **Phase 4 writeup.** F95 supersedes F94's attractor-break optimism with a more honest 1-real-1-hallucinated-1-coincidence accounting. Adds L20/L22 sub-direction claim as a qualitative result worth prominent placement. Revises token-efficiency numbers.
- **Scoring regime.** The murder_mysteries hallucination is the second instance (after fb-nile-source) of the scorer rewarding us for the wrong thing. Every "steering wins on item X" claim in the writeup needs to be audited against the actual reasoning trace, not just the final answer.
- **Concept taxonomy.** The L20/L22 sub-direction evidence suggests "calibrated confidence" decomposes into at least two orthogonal sub-dispositions — commit-to-structure (L20-like) and deliberate-without-committing (L22-like) — and neither alone is the full virtue. A third sub-disposition (recognize absence of answer) is still missing from both.
- **Extraction corpus design.** Our hand-written 50 triplets depict commit-with-hedging and extract exactly that. To extract the missing sub-dispositions, we need triplets that explicitly depict the *other* behaviors. The abstention-focused corpus in Priority 3 is one step; a "deliberate-without-committing" corpus would be another.

---

## F96 — Priority-1 verification: murder_mysteries-92 "attractor break" was hallucination-driven. L22_a12 is a weapon-follower with fast commit, not a motive-first reasoner.

**Source:** Priority-1 hallucination verification run on GCP L4 (asia-southeast1-a, 2026-04-22). 6 generations: 3 conditions × 2 prompt variants. Deterministic (do_sample=False). Qwen3-4B thinking mode.

### Design

Two prompts:
- `mm92-original` — unchanged v3 MuSR prompt (the one the v3 hard_probe_v3 used). Both suspects have lead-pipe access: Christine explicitly owns a construction site; Madison has "a lead pipe resting within" her tool-laden van.
- `mm92-variant` — the same story with two surgical edits: (a) Madison's van stripped of any lead pipe ("No lead piping anywhere. Madison used lightweight aluminum framing"), (b) a forensic line added before the question attributing the murder weapon unambiguously to Christine's construction site ("matching the mill batch, surface oxidation pattern, and trace cement residue"). All motive facts preserved (Iris's testimony against Madison, Madison's eviction threat, Madison at the casino).

Three conditions (baseline, `L20 @ α=+12`, `L22 @ α=+12`) on both prompts.

### Results

| Condition | mm92-original (pred) | mm92-variant (pred) |
|---|---|---|
| baseline | **A ✓** (456s, loops) | B ✗ (46s, fast commit) |
| L20_a12 | B ✗ (74s) | B ✗ (18s) |
| **L22_a12** | **A ✓** (98s) | **B ✗ (39s)** |

### The key result — L22_a12 flips to B on the variant

On the original (ambiguous weapon), L22_a12 picks A and reproduces the v3 "break." On the variant (unambiguous weapon-to-Christine), **L22_a12 flips to B** despite identical motive facts. Verbatim from the L22_a12 variant trace:

> "Madison was the one who was in conflict with Iris. So she had a motive. But the murder weapon is from Christine's site... The motive is Madison, but the weapon is from Christine. So the answer is Christine. So B."

L22_a12 explicitly considers motive, notices Madison has the stronger motive, and still chooses Christine because the weapon is unambiguously hers. **L22's reasoning structure is "weapon-attribution with fast commit"** — indistinguishable from L20's. The v3 "win" was because L22 hallucinated weapon-attribution in Madison's favor when the prompt was ambiguous, not because of any real motive-first competence.

### Implications for F95

1. **Remove `murder_mysteries-92` from the attractor-break ledger.** The v3 result was an accident, not a real disruption. F95's table entry for this item is now marked ❌ hallucination-confirmed.
2. **F95's revised accounting:** of the 3 apparent attractor breaks in v3, only **aime/42** (L20_a8 and L20_a16 both → 49 via even/odd lemma) survives as a mechanism-defended win. fb-nobel-einstein remains N=1. murder_mysteries-92 is out.
3. **L20/L22 sub-direction claim still holds** but on slightly different evidence. The trick-question data (F95's primary support) still shows L22 doesn't confabulate while L20 does. The variant-prompt data shows L20 and L22 make the same commit on disambiguated MCQ prompts. Both findings can coexist: the layer carries a different *style* of commit but the same underlying commit-pressure on clear-evidence items.

### Secondary finding — T4 vs L4 break determinism

On `mm92-original`, **baseline on L4 gave A** (correct, 456s). The v3 T4 baseline on the identical prompt gave B (wrong). Same prompt, same `do_sample=False`, different GPU → different answer. Likely cause: CUDA kernel selection and float-precision rounding differ across Turing (T4) and Ada Lovelace (L4) architectures. Deterministic mode is not truly deterministic across hardware.

**Implications:**
- Any attractor-classification result should specify hardware. Our v3 "same-wrong-answer attractor" on mm92 is a T4-specific phenomenon; on L4, baseline escapes it.
- This affects F94's zero-regression claim too: v3 data was all on T4; L4 could produce different per-item accuracy.
- Honest writeup: hardware specified in methods, caveat that deterministic-mode results may not transfer across GPU architectures.

### What the variant test also told us

- **Disambiguating weapon-attribution makes baseline commit ~10× faster** (46s vs 456s). Prompt-level disambiguation has the same "commit-pressure" effect as steering does. This is a useful parallel: steering acts on activations what prompt-engineering acts on inputs. Both can accelerate, both can commit to wrong conclusions if the reasoning structure is flawed.
- **L20_a12 attributes to B at 18s on the variant** — 4× faster than at 74s on the original. On the original, it *spent* the extra tokens considering Madison's motive and rejecting it; on the variant, it had no reason to consider Madison at all, weapon-attribution was unambiguous. Same direction, shorter path.

### Applies to

- **F95 revision.** Mark murder_mysteries break as hallucination-confirmed; aime/42 is now the only mechanism-defended break from v3.
- **Paper methodology.** Report hardware used for every experimental result. Add a "deterministic-mode caveat" note explaining that strict determinism holds within-architecture but not across.
- **Future attractor claims.** Any "break" that depends on the model's factual interpretation of an ambiguous element needs a disambiguated-variant check before it counts. Specifically: if the model can reach the correct answer by mis-encoding a fact, the correctness isn't capturing the behavior we want.
- **Priority 2 follow-up still valuable.** aime/42 mechanism verification (10 runs each of L20_a8 and L20_a16 at temp=0.3) is the next defensibility test. A mechanism-backed break should replicate in ≥4/10 correct-answer runs, with the even/odd lemma appearing in correct runs but not wrong runs. Currently running on L4.

---

## F97 — MVE gate: Cross-model geometric separation between v_CC and v_IH is clean on both Qwen3-4B and Gemma 4 E4B-it. Behavioral Test A at α=12 is inconclusive, substantially due to scorer artifacts.

**Source:** Phronesis Intellectual Humility corpus extraction + MVE gate tests on GCP L4 (asia-southeast1-a, 2026-04-22 → 2026-04-23). 20-triplet IH corpus (`corpus/triplets-intellectual-humility/`) extracted on Qwen3-4B (36 layers) and Gemma 4 E4B-it (42 layers) via `last_token` method. Gemma CC vectors (166 triplets, triplets-combined) also extracted for the first time. Qwen behavioral Test A run on 24-item abstention benchmark, baseline + `IH_L20 @ α=+12` conditions, deterministic. Alpha/layer sweep pending.

**Background.** F95 established that the L20 vector (Calibrated Confidence) and L22 behaviors dissociate, and proposed a 3-concept framing (Calibrated Confidence / Intellectual Humility / Comfort with Ambiguity). F96 confirmed via variant-prompt that some v3 results we'd credited to steering were hallucination artifacts. The Opus taxonomy-cross-reference agent (2026-04-22) reframed "sub-dispositions of CC" as "three separate concepts already in concepts.md that may dissociate in activation space." The red-team review insisted on an MVE-first gate: 20 triplets, orthogonal-projection test, kill the project cheaply if the core geometric claim fails.

### Geometric result (Test B + Test C)

Both models show **v_CC and v_IH as near-orthogonal directions**, with Gemma textbook-clean:

| Model | `\|cos(v_CC, v_IH)\|` mean | Range | CC retention after ⊥ projection (mean) | Retention at sweet-spot layer |
|---|---|---|---|---|
| Qwen3-4B (36 layers) | **0.179** | [−0.08, +0.31] | 98.1% | 97.8% (L20) |
| Gemma 4 E4B-it (42 layers) | **0.030** | [−0.10, +0.07] | **99.9%** | **100.0%** (L24, L26) |

**Interpretation:** if v_IH were merely an antipodal direction on the same axis as v_CC, orthogonal projection would near-zero v_CC's magnitude. Instead, >95% of v_CC's magnitude survives at every layer on both models. On Gemma the result is unambiguous: v_CC and v_IH are effectively independent dimensions at every layer.

**The geometric claim from F95 is now cross-model-confirmed.** The three concepts we extracted (Calibrated Confidence from 166 triplets; Intellectual Humility from 20 triplets) are not two poles of one axis. This is the first cross-model geometric evidence for the activation-space-dissociation claim.

### Behavioral result (Test A)

The geometric result predicts that v_IH should behave *differently* from v_CC when used as a steering vector. Test A probes whether v_IH actually *steers toward abstention* — the behavior it was designed to capture.

Run design: 24-item abstention benchmark, Qwen3-4B fp16 on L4.

| Condition | Correct | By category |
|---|---|---|
| baseline_L4 | 18/24 (75.0%) | fp=3/4, ip=3/4, od=1/4, subj=4/4, unk=3/4, us=4/4 |
| steered `IH_L20 @ α=+12` | 17/24 (70.8%) | fp=4/4, ip=3/4, od=1/4, subj=4/4, unk=1/4, us=4/4 |
| **Δ** | **−1 item (−4.2pp)** | fp:+1, ip:0 (swap), od:0 (floor), subj:0, unk:**−2**, us:0 |

**Raw verdict: FAIL the +5pp MVE gate at α=12.**

But the flip pattern is informative and the interpretation is complicated by scorer artifacts:

- Both OK: 15 (majority stable)
- Gained (baseline wrong → steered correct): 2 (fp-moonrover, ip-square)
- Lost (baseline correct → steered wrong): 3 (ip-longest, unk-meeting, unk-pumpkin)

**Two of the three "losses" are substantially scorer artifacts** (confirming F96's scorer-regime concerns):

- `fp-moonrover` (GAINED): baseline and steered produce nearly identical answers — both say *"No U.S. president has ever landed a robotic rover on the Moon."* Scorer flipped from wrong to right on essentially the same text. Pure scorer sensitivity.
- `unk-meeting` (LOST): baseline and steered both answer *"August 24, 2006"* for the IAU planet-definition approval. Difference is hedge density — baseline adds *"the user might be confused"* which saves it under the scorer's abstention-marker regex; steered drops that hedge. Same factual claim, different verdict.
- `unk-pumpkin` (LOST): both models confabulate a specific weight. Baseline picks 100.5 kg, steered picks 200 kg. Neither actually abstains. Both should arguably fail; scorer marks baseline as passing anyway.

The net behavioral signal is: **IH steering reduces hedge density** (matches F92's commit-pressure finding — v_IH still carries some of the "commit-to-structure" flavor because it was extracted from a corpus that, despite our design efforts, shares some register with CC), **but the scorer can't distinguish "reduced hedging with same facts" from "stopped abstaining."**

**The −4.2pp delta is not a clean failure signal.** It is substantially scorer-artifact noise on a scorer we already knew (F96) had systematic issues with hedge-density changes.

### What the Gemma result protects us from

One risk of framing Test A as a flat null or failure is over-updating on one noisy measurement. The cross-model geometric result protects against that: even if Qwen Test A behavioral failed outright, Gemma's textbook-clean geometric separation (|cos| mean 0.030, 99.9% CC retention at every layer) is strong evidence that v_CC and v_IH ARE different directions. The question is whether the *behavioral* steering effect is clean — not whether the vectors are geometrically distinct.

### What's pending

- **α + layer sweep on Qwen** (running). IH_L20 at α={8, 16, 20} + IH_L{18, 22, 25} at α=12. If v_IH norms are 60–80% of v_CC norms (which they are, verified from extracted vectors), α=12 may be underpowered. Predict α=16–20 may produce a stronger (positive or negative) effect.
- **Gemma Test A**. Code path prepared (run_benchmark.py now supports --model gemma-4-E4B-it with IH_L18/20/22/24/26/28 in registry). Haven't run due to GPU contention with Qwen sweep.
- **Scorer upgrade**. The F96 concern is now even more acute: a scorer that flips verdicts on nearly-identical content cannot cleanly measure the effect we're trying to detect. Need a mixed-verdict category that detects embedded confabulation inside abstaining wrappers.

### What the MVE gate tells us (revised)

| Criterion | Qwen | Gemma |
|---|---|---|
| Test B geometric (CC retention >70%) | ✅ PASS (98%) | ✅ PASS (99.9%) |
| Test C (near-orthogonal) | ✅ PASS (\|cos\|=0.18) | ✅ PASS (\|cos\|=0.03) |
| **Test A behavioral (+5pp abstention)** | **⚠️ FAIL at α=12, pending sweep** | ⏳ Not yet run |

The geometric MVE has landed decisively on both models. The behavioral MVE is pending. The red-team's decision matrix said "A fail → scale corpus to 50+ or pivot to larger model." We should NOT pivot yet — the sweep results and a scorer upgrade are cheap to run and may move the needle meaningfully.

**Provisional scientific claim (defensible now, pending Test A resolution):**

> On two independently-pretrained 4B-parameter thinking models (Qwen3-4B and Gemma 4 E4B-it), the Calibrated Confidence concept (extracted from 166 triplets depicting commit-with-hedging) and the Intellectual Humility concept (extracted from 20 triplets depicting abstain-when-evidence-absent) occupy near-orthogonal directions in residual-stream activation space at every layer of the text backbone.

**Ungood claims we should NOT make yet:**

- "v_IH steers abstention behavior." Not shown; Test A inconclusive.
- "The decomposition is novel." Lit review showed Persona Vectors already established the method. Our contribution is the specific three-concept framing + cross-model activation geometry.

### Applies to

- **Paper positioning.** The geometric result is defensible and cross-model. The behavioral story needs Test A resolution before making claims.
- **Scorer redesign.** Upgrade to mixed-verdict category before any future abstention-vector claim. This is now blocking.
- **Corpus scaling decision.** Wait for sweep results. If no (α, layer) combo produces a clean positive behavioral effect, decide between (a) scaling IH corpus to 50+, (b) scoring-regime fix, (c) switching to a larger model.
- **Future extractions.** v_IH norms at 60–80% of v_CC norms suggest extraction signal-to-noise depends on corpus size. Any future small-corpus vector should have its steering α re-tuned relative to larger-corpus vectors.

---

## F98 (PRE-REGISTERED, 2026-04-23) — 4×4 specificity-matrix exit criteria committed before any EG + RT extraction data exists

**Type:** Pre-registration, not a data finding. Commits to the decision rules for the 4-virtue MVP BEFORE any v_EG or v_RT steering data is observed, so that post-hoc rationalisation is constrained.

**What's being committed (per `docs/eg-rt-eval-spec.md` §5.7 and `docs/mvp-virtues.md` §"Milestones and exit criteria"):**

1. **Corpus:** 80 triplets in `corpus/mvp-combined/` (40 EG + 40 RT, mixed ChatGPT + Sonnet + substrate-reuse). Frozen per `LEDGER.md` v2 (2026-04-22).
2. **Extraction:** v_EG and v_RT on both Qwen3-4B and Gemma 4 E4B-it via `extract_v2.py --method generation`. Generation-based (F73 Path B), all layers, whitened difference-of-means.
3. **Geometric MVE matrix** (Stage 2 of `extraction-runbook.md`): test orthogonality of 6 pairs — CC⊥IH, CC⊥EG, CC⊥RT, IH⊥EG, IH⊥RT, EG⊥RT — on both models. Threshold per pair: |cos| < 0.2 AND retention after ⊥ projection > 70%.
4. **Behavioral 4×4 specificity matrix** (Stage 4 of runbook): each of {v_CC, v_IH, v_EG, v_RT} steered across each of {AIME-42, abstention, EG-eval, RT-eval}. 864 generations per model. All generations scored by all 4 virtue-scorers (CC-hedging, IH-abstention, EG, RT).
5. **α / layer protocol:** "best case for diagonal" — for each vector, pre-sweep α {4, 8, 12, 16, 20} × layers {18, 20, 22, 25} on Qwen (/ {14, 18, 22} on Gemma) on 5 prompts per target eval; use the (α, layer) that maximises the diagonal effect across all that vector's cells.
6. **Scoring discipline:** 100% manual hand-review of all 960 generations per `docs/scoring.md` manual-first policy. Auto-scorer outputs logged but not decision-making.

**Pre-registered exit criteria:**

| Outcome | Geometric MVE (6 pairs) | Diagonal wins (4 cells) | Off-diagonal specificity failures | Classification |
|---|---|---|---|---|
| **All-clean MVP success** | 6/6 pass | 4/4 (each ≥ +5 target-metric points AND ≥2× vs max off-diag in row) | ≤ 2 | Publishable: "four orthogonal epistemic-virtue directions on small open models with differential behavioral specificity" |
| **Partial success** | 5/6 or 6/6 pass | ≥2/4 | ≤ 2 | Publishable: acknowledge collapse-pair + specificity failures; still a 2-3 virtue result |
| **Collapse** | ≤4/6 pass OR v_EG × v_RT collapse | ≤1/4 | ≥3 | Reframe as failure/collapse finding; MVP-scope "these 4 virtues do not separate atomically on 4B models" |

**What the outcomes tell us:**

- **EG × RT geometric collapse** (|cos| > 0.5, retention < 50%): the AOT-cluster risk (F39) materialised; the two Stage-2 virtues share a latent "scientific-reasoning disposition" direction. Publishable as a collapse finding.
- **Diagonal wins but off-diagonal saturates** (e.g., v_EG drives hedging as much as it drives evidence-labeling): F67's multi-direction-same-behavior caution bites. Follow-up needed to disentangle.
- **Full clean matrix**: taxonomic-success case per `project.md`. First published specificity matrix for epistemic virtues on open 4B models (to my knowledge, not yet lit-checked for 2026).

**Why pre-register:**

- Prevents post-hoc "of course EG and RT would collapse, they're both scientific virtues" rationalisation after data lands.
- Commits to α-sweep protocol ("best case for diagonal") before seeing which layers/α actually work — prevents cherry-picking.
- Publishes failure criteria alongside success criteria, so a null result is still a meaningful outcome — consistent with Day 15 guiding principle #1 ("learning over publishing").

**Related docs committed before data:**

- `docs/mvp-virtues.md` (scope)
- `docs/eg-rt-eval-spec.md` (benchmark + scoring)
- `docs/extraction-runbook.md` (how to run it)
- `corpus/mvp-combined/LEDGER.md` (corpus provenance + verification)

### Applies to

- **All subsequent EG/RT findings** (F99+): must reference this pre-registration. Any deviation from the committed protocol must be explicitly called out.
- **MVP publication decision.** Whether the outcome is all-clean, partial, or collapse, the decision about publication should follow the classification in the table above, not post-hoc re-interpretation.

---


## F99 (2026-04-25) — EG + RT extraction complete: geometric MVE matrix is ALL CLEAN on both models (12/12 cells pass)

**Status:** Filled in. All 4 extractions completed on `phronesis-v2-l4` (asia-southeast1-a, L4 GPU). Vectors pulled locally and run through `mvp/analysis/run_analysis.py --mve-only`.

**Pre-registered per F98** — decision rules and exit criteria were committed before this data existed. F98's `all_clean` exit branch is now triggered.

### Extractions completed

| Model | Corpus | Layers | Status |
|---|---|---|---|
| qwen3-4b | triplets-evidence-grounding | 36/36 | ✅ |
| qwen3-4b | triplets-reasoning-transparency | 36/36 | ✅ |
| gemma-4-E4B-it | triplets-evidence-grounding | 42/42 | ✅ |
| gemma-4-E4B-it | triplets-reasoning-transparency | 42/42 | ✅ |

Vectors live at `mvp/results/vectors/{model}/triplets-{evidence-grounding,reasoning-transparency}/generation/layer_{N}_virtue_vector.npy` plus probe metadata + whitening components per layer. Total ~11 MB pulled.

### Geometric MVE matrix (6 pairs × 2 models = 12 cells)

#### qwen3-4b — 6/6 pass → ✅ ALL CLEAN

| pair | mean \|cos\| | max \|cos\| | mean retention | verdict |
|---|---|---|---|---|
| CC ⊥ IH | 0.179 | 0.314 | 98.1% | 🟢 pass |
| CC ⊥ EG | 0.157 | 0.202 | 98.7% | 🟢 pass |
| CC ⊥ RT | 0.099 | 0.175 | 99.5% | 🟢 pass |
| IH ⊥ EG | 0.026 | 0.089 | 99.9% | 🟢 pass |
| IH ⊥ RT | 0.020 | 0.045 | 100.0% | 🟢 pass |
| EG ⊥ RT | 0.104 | 0.181 | 99.3% | 🟢 pass |

#### gemma-4-E4B-it — 6/6 pass → ✅ ALL CLEAN

| pair | mean \|cos\| | max \|cos\| | mean retention | verdict |
|---|---|---|---|---|
| CC ⊥ IH | 0.030 | 0.104 | 99.9% | 🟢 pass |
| CC ⊥ EG | 0.142 | 0.259 | 98.9% | 🟢 pass |
| CC ⊥ RT | 0.149 | 0.238 | 98.8% | 🟢 pass |
| IH ⊥ EG | 0.100 | 0.157 | 99.4% | 🟢 pass |
| IH ⊥ RT | 0.056 | 0.211 | 99.8% | 🟢 pass |
| EG ⊥ RT | 0.115 | 0.242 | 99.2% | 🟢 pass |

Thresholds (pre-registered, `mvp/analysis/config.yaml`):
- `cos_clean_threshold: 0.20` (mean)
- `retention_pass_threshold: 0.70`
- All 12 cells satisfy both.

### Per-layer cosine behavior (worth noting; does NOT change verdict)

- **qwen3-4b CC ⊥ IH** spikes above the 0.20 mean threshold in layers ~19–30, peaking 0.314 at L23. Within partial-overlap band (<0.5), so still passes. F97 already noted CC × IH as the warmest qwen pair (mean 0.179) — this run reproduces it cleanly.
- **gemma-4-E4B-it early-layer transients:** CC⊥RT max 0.238 at L1, CC⊥EG max 0.259 around L5. Settle below 0.20 by L8 and stay there. Plausibly artefacts of unspecialized early-layer representations; not relevant to the steering layers (typically 18–25).
- **EG × RT** — the AOT-collapse risk pair flagged by F39 — is **clean on both models**. Mean 0.104 (qwen) / 0.115 (gemma), max 0.181 / 0.242. Confirms EG and RT are distinct directions, not a single "scientific-reasoning" attractor. This is the single biggest pre-data risk we'd identified, and it didn't materialize.

### What this means under F98 pre-registration

F98 exit criteria for the **all_clean MVP-success branch:**
- `mve_pairs_pass: 6` (all 6 of 4C2 pairs must pass) → ✅ achieved on both models
- `diagonal_wins_min: 4` → not yet tested (requires 4×4 specificity matrix)
- `off_diag_failures_max: 2` → not yet tested

So F99 alone does not yet constitute the all_clean MVP outcome. It clears the **geometric** bar cleanly. The behavioral 4×4 matrix (α-sweep + 864 generations per model + hand-scoring) is still required to determine final verdict per F98.

Per `docs/post-mvp-decisions.md` decision tree, an all_clean geometric result with no warning signs proceeds to: α-sweep on VM → 4×4 specificity matrix → hand review → final analysis.

### Caveats / honest uncertainty

- **MVE measures geometric independence of virtue directions, not behavioral specificity.** Two directions can be orthogonal yet drive the same downstream behavior (F67 caution). 4×4 specificity will determine that.
- **No single-layer collapse.** Even at the worst layer (qwen CC⊥IH, L23, |cos|=0.314), all pairs stay within partial-overlap band, not collapse. Robust to layer choice.
- **Probe-accuracy and vector-norm data not yet inspected** — `extraction_summary.json` per corpus was pulled but not parsed in this finding. To be reviewed before α-sweep (would catch e.g. low probe accuracy that would weaken the steering signal even with clean geometry).
- **MVE retention thresholds are generous.** All 12 cells show retention > 98% — well above the 70% pre-registered floor. Sanity-check if anything: are vectors trivially low-rank or near-zero? Norm inspection (deferred) will confirm.

### Applies to

- **Phase 5 conditional plan** (`docs/phase5-plan.md`) — geometric all-clean is a green light to proceed *if* behavioral all-clean follows. Still gated on 4×4 matrix outcome.
- **F98 publication decision framework** — geometric branch is locked; behavioral branch pending.
- **`docs/mvp-virtues.md`** — does not need to change. Pre-registered scope held.
- **F39 AOT-cluster risk** — partially retired. EG × RT did not collapse geometrically; behavioral collapse still possible.

### Artifacts

- Report: `mvp/results/analysis_report/report.md`
- Heatmaps: `mve_heatmap_{qwen3-4b,gemma-4-E4B-it}.png`
- Per-layer cosines: `per_layer_cosine_{qwen3-4b,gemma-4-E4B-it}.png`
- Raw vectors: `mvp/results/vectors/{model}/triplets-{evidence-grounding,reasoning-transparency}/`
- Extraction log: `mvp/results/eg_rt_extraction.log`

---


## F100 (2026-04-25) — Probe-accuracy + retention sanity checks materially weaken F99's optimistic reading. qwen × RT vector is plausibly noise.

**Status:** Sanity-check follow-up to F99, performed before authorising α-sweep GPU spend. Three checks: probe accuracy, retention significance, scorer drift.

**Why this matters:** F99 reported "all_clean MVE: 12/12 cells pass." The three checks below show that statement is technically true but partially vacuous — multiple cells pass the |cos| < 0.20 threshold by being indistinguishable from random vectors, and one (model, virtue) combination has probe accuracy near chance, suggesting its extracted vector is largely noise.

### Check 1 — Probe accuracy at typical steering layers (L18–25)

Probe accuracy = linear separability of virtuous-vs-non-virtuous activations at a given layer. F97 reference: qwen3-4b × CC achieves probe accuracy 0.93 mean, 0.96 best (`mvp/results/vectors/qwen3-4b/triplets/extraction_summary.json`).

| Model × Virtue | Best probe acc in L18–25 | Mean L18–25 | Verdict |
|---|---|---|---|
| qwen3-4b × EG | 0.66 (L20, L22) | 0.62 | Yellow — clearly above chance, but much weaker than CC's 0.96 |
| qwen3-4b × RT | 0.61 (L22) | 0.56 | **Red — barely above chance (0.50)** |
| gemma-4-E4B-it × EG | 0.80 (L18, L21) | 0.75 | Green |
| gemma-4-E4B-it × RT | 0.68 (L18–21) | 0.65 | Yellow |

**Interpretation:** F97's CC and IH on qwen had probe acc ~0.93. EG and RT extractions on qwen are substantially weaker, with RT essentially undistinguishable from random near the steering range. The "RT virtue direction" extracted from qwen3-4b therefore has weak signal-to-noise; behavioral steering with it may produce null or noisy results regardless of geometric MVE outcome.

Note also: CC and IH were extracted via `last_token` method; EG and RT via `generation` method. The methodological difference may partially explain the gap (different averaging across more vs. fewer tokens), but does not fully account for qwen × RT's near-chance accuracy. Gemma extractions held up better under the same `generation` method, so the gap is plausibly real and not purely methodological.

### Check 2 — Retention significance (vs. random-baseline)

F99 reported retention 98–100% on all 12 cells, well above the 70% pre-registered floor. Question: does that mean anything?

**Theoretical baseline for random vectors in R^2560:** expected |cos| = 1/√2560 ≈ 0.0198; expected retention after orthogonal projection = 1 − 1/2560 ≈ 99.96%.

**Empirical (100 random vectors vs each new EG/RT vector at L22):** observed |cos| 0.014–0.016, max 0.061. Indistinguishable from theoretical random.

**Implication:** retention >99% is a near-vacuous criterion in 2560-dim space. It is satisfied by random pairs of vectors. Whenever |cos| is small (< ~0.10), retention will be >99% almost regardless of whether the vectors carry signal.

This re-frames the F99 result. The cells that meaningfully passed:
- qwen × CC⊥IH (mean |cos| 0.179, max 0.314): clearly above random — real signal, partial overlap.
- qwen × CC⊥EG (mean 0.157), qwen × CC⊥RT (0.099): above random.
- qwen × EG⊥RT (0.104): above random — meaningfully orthogonal, despite F39 risk.
- gemma × CC⊥EG (0.142), CC⊥RT (0.149), EG⊥RT (0.115): above random.

The cells that pass but are **at or near random baseline** (i.e., consistent with "two arbitrary high-dim vectors"):
- qwen × IH⊥EG (0.026) — near random, could be noise on either side.
- qwen × IH⊥RT (0.020) — exactly at random baseline. Combined with check 1 (qwen × RT probe acc near chance), this cell most likely says "RT vector is essentially noise; of course noise is orthogonal to IH."
- gemma × CC⊥IH (0.030) — near random.
- gemma × IH⊥RT (0.056) — closer to random than to clear signal.

**Implication:** F99's "12/12 pass" should not be re-read as "12 pieces of strong evidence for atomic virtue directions." It's "no pair shows collapse, and several pairs show genuine geometric distinctness." The latter is still consistent with the all_clean F98 branch — F98's threshold was deliberately set without requiring that all pairs be in the "definitely-not-noise" range — but the qwen × RT cell deserves a flag.

### Check 3 — EG/RT scorer drift

Re-ran `mvp/calibrate_scorers.py` against `corpus/mvp-combined/`. Result:

```
EG scorer (v3):  PASS  separation +19.57
RT scorer (v2):  PASS  separation +9.90
```

Identical to yesterday's calibration numbers (`docs/journal.md` Day 17 / `docs/scoring.md`). No drift. Known false-negative virtuous passages (chatgpt-eg-07, eg-12, eg-13, eg-17, eg-18; chatgpt-rt-12, rt-20; sonnet-rt-04, rt-06) and known false-positive deficiency-non-virtuous passages (chatgpt-eg-16, sonnet-eg-19; sonnet-rt-06, rt-08, rt-16) reproduce exactly. Hand-review will catch them as planned per `docs/scoring.md`.

Note: I had originally framed this as "spot-check scorer against real extraction generations." That framing was wrong — `extract_v2.py` does not save model generations; it only computes virtue vectors. Actual generations only land during the α-sweep / 4×4 specificity matrix runs. The corpus re-calibration is the correct sanity-check at this stage.

### Combined implications for F98 branch

F99 + F100 together:
- **Geometric MVE all_clean** still holds per F98's pre-registered thresholds. We are not retroactively moving the goalposts.
- **But** the qwen × RT extraction signal is weak enough that the 4×4 specificity matrix may show null effects in the qwen-RT row (especially the diagonal qwen-RT × rt-eval cell). If that happens, it should be attributed to extraction-signal weakness, not to "RT is not a real virtue."
- **Recommended modification to next steps**: before α-sweep, re-extract qwen × RT with the `last_token` method (matching CC and IH) to test whether the method choice explains the probe-accuracy gap. Cost: ~2h GPU. Benefit: removes method as a confound; if last_token also gives weak probe acc, that's a real signal about RT's separability on qwen.

### Caveats on this finding

- Probe accuracy depends on the train/test split (default 80/20 or whatever `extract_v2.py` uses). Different splits could shift numbers by a few percentage points.
- Random-baseline analysis assumes uniform random vectors in R^2560. Real activations have structure (residual stream is not isotropic). The "random" baseline I computed may be optimistic (true noise might have higher cos than 0.02 if dominant directions exist). This makes the >random cells *more* significant, but doesn't change the near-random cells' interpretation.
- Method confound (last_token vs generation) is a real alternative explanation for qwen × RT's weakness — only re-extraction can disambiguate.

### What to do about it

1. **Update F99's optimism flag.** F99 stands as written but should be read alongside F100. (Done: F99 already lists "no probe-accuracy / norm sanity check yet" as a deferred item; this finding closes that item with mixed news.)
2. **Decide on qwen × RT re-extraction.** Either (a) re-extract with last_token method before α-sweep, or (b) proceed and accept that a null qwen-RT-row is plausible.
3. **Document method-difference issue in `docs/extraction-runbook.md`.** Mixed methods across CC/IH (last_token) and EG/RT (generation) is a methodological inconsistency that should be either reconciled or explicitly justified before publication.

### Applies to

- α-sweep planning (`docs/extraction-runbook.md` §4): consider re-extraction step before α-sweep.
- F98 publication framework: a partial- or null-qwen-RT-row outcome would still be consistent with the partial-success branch, but the interpretation needs care.
- Phase 5 plan (`docs/phase5-plan.md`): if qwen × RT is method-dependent, the 8-virtue scale-up should probably standardise on one extraction method.

### Artifacts

- Probe accuracy + norm script output: re-runnable from `mvp/results/vectors/{model}/{corpus}/extraction_summary.json` per layer.
- Random-baseline analysis: re-runnable in ~5 lines of numpy.
- Calibration log: `mvp/calibrate_scorers.py` (PASS, no drift, 2026-04-25).

---


## F101 (2026-04-25 evening) — Method-confound confirmed: qwen × RT last_token re-extraction reveals real CC⊥RT partial overlap that was hidden by noise. F99's `all_clean` for qwen is downgraded to `partial`.

**Status:** Decisive empirical test of F100's hypothesis. Re-extracted qwen3-4b × RT using `last_token` method (the same method F97 used for CC and IH); compared against the original `generation` method extraction. Result is unambiguous: the method confound was real, AND it was masking a genuine geometric overlap.

### The diagnostic

Re-extraction of qwen3-4b × triplets-reasoning-transparency using `extract_v2.py --method last_token`. Wall time ~17 min on L4 (vs ~10h for the generation method — last_token is single-token vs 128-token-average). Vectors saved to `mvp/results/vectors/qwen3-4b/triplets-reasoning-transparency/last_token/`.

### Probe-accuracy comparison at steering layers (L18–32)

| Layer | generation | last_token | Δ |
|---|---|---|---|
| 18 | 0.562 | 0.838 | +0.275 |
| 20 | 0.588 | 0.812 | +0.225 |
| 22 | 0.613 | 0.850 | +0.237 |
| 25 | 0.475 | 0.850 | +0.375 |
| 28 | 0.463 | 0.887 | +0.425 |
| 31 | 0.450 | **0.900** | +0.450 |
| 32 | 0.412 | 0.875 | +0.463 |

**Aggregate:**
- generation method: probe acc mean=0.517, max=0.638 (best at L3), at steering layers 0.51 mean
- last_token method: probe acc mean=0.839, max=**0.900** (best at L31), at steering layers 0.85 mean

The generation method's probe accuracy actually *degrades* at deeper layers, while last_token improves through the model — consistent with last_token capturing residual-stream signal at the token where the model has integrated the full context.

### Same-layer cosine between gen-method and last_token-method RT vectors

| Layer | \|cos(v_RT_gen, v_RT_lt)\| |
|---|---|
| 18 | 0.041 |
| 22 | 0.079 |
| 25 | 0.148 |
| 28 | 0.161 |
| 31 | 0.201 |

These are essentially **different vectors** — the generation-method RT vector is not a noisier version of the last_token-method RT vector; it's a separate direction in residual-stream space. This confirms F100's interpretation: the generation-method qwen × RT extraction was largely capturing noise, not the RT direction.

Vector norms also doubled: gen mean ||v||=4.6, last_token mean ||v||=9.0 (and last_token max ||v||=34.8 vs gen max 18.2).

### MVE matrix re-run with the new RT vector (qwen3-4b only)

Substituting last_token RT in place of generation RT, holding CC/IH/EG unchanged:

| Pair | BEFORE (RT=gen) | AFTER (RT=last_token) | Verdict change |
|---|---|---|---|
| CC ⊥ IH | mean 0.179, max 0.314 | mean 0.179, max 0.314 | unchanged 🟢 |
| CC ⊥ EG | mean 0.157, max 0.202 | mean 0.157, max 0.202 | unchanged 🟢 |
| **CC ⊥ RT** | **mean 0.099, max 0.175** 🟢 | **mean 0.377, max 0.520** 🟡 | **clean → partial** |
| IH ⊥ EG | mean 0.026 | mean 0.026 | unchanged 🟢 |
| IH ⊥ RT | mean 0.020 (random baseline) | mean 0.059 | still 🟢 but no longer fake-random |
| EG ⊥ RT | mean 0.104, max 0.181 | mean 0.128, max 0.173 | basically unchanged 🟢 |

**qwen3-4b verdict:** `all_clean (6/6)` → **`partial (5/6)`**.

CC ⊥ RT max |cos| of 0.520 just exceeds the pre-registered 0.50 partial-collapse threshold at the worst layer. Mean |cos| 0.377 is well into partial-overlap band. Mean retention 0.92 (still above 70% pass threshold). So the pair is borderline-partial, not full collapse — but it is no longer in the clean-orthogonal range.

### What this means under F98 pre-registration

F98 (pre-registered before any data) defined three branches:
- **all_clean:** 6/6 pairs pass MVE
- **partial:** 5/6 pairs pass — *acknowledge collapse-pair + specificity failures; still a 2–3 virtue result*
- **collapse:** ≤4/6 pass OR EG⊥RT collapse

We are now on the **partial** branch for qwen3-4b on the geometric criterion. The collapse-pair is **CC ⊥ RT**, not the F39-flagged EG ⊥ RT. EG ⊥ RT remained clean across both extraction methods — F39's AOT-cluster risk continues to NOT materialize.

This is consistent with what the partial branch was designed to capture per the F98 table: *"publishable: acknowledge collapse-pair + specificity failures; still a 2–3 virtue result."* Specifically, on qwen3-4b, CC and RT share enough geometric structure that their behavioural specificity is not guaranteed; the 4×4 specificity matrix may show some cross-talk in CC-row × rt-eval and RT-row × aime-42 cells.

### Why this is good news, not bad

- **F99's all_clean was a noise artifact, not a real result.** Detecting this BEFORE α-sweep / 4×4 matrix saves real wasted GPU and a misleading headline finding.
- **F100's hypothesis was confirmed empirically.** The probe-acc gap was indeed methodological. The sanity-check pipeline worked.
- **The partial branch was pre-registered.** Moving from all_clean to partial is not a goalpost-shift; both branches were committed in F98 before any data existed.
- **F39 risk did NOT materialize** — EG ⊥ RT remains clean even with proper extraction. This was the single biggest pre-data risk and it didn't bite.
- **The "actual" finding is more interesting.** "CC and RT share a direction component on qwen3-4b" is a substantive, mechanistically-interpretable result. "Four orthogonal directions, all clean" was almost too clean to be informative.

### What we still don't know (in progress)

The remaining three (model, virtue) combos were extracted via the same generation method:
- qwen3-4b × EG: probe acc generation 0.66 best, may improve with last_token. May reveal hidden CC⊥EG overlap.
- gemma-4-E4B-it × EG: probe acc generation 0.83 best — relatively healthy, less dramatic gap expected.
- gemma-4-E4B-it × RT: probe acc generation 0.74 best.

Re-extraction of all three with last_token kicked off in tmux session `lasttoken_remaining` on `phronesis-v2-l4` at 2026-04-25 00:34 UTC. Total ETA ~2h. Once they land, we'll re-run the full MVE matrix on uniform-method vectors and write the final F102 with the full picture.

### Decisions implied (not yet made)

- The α-sweep step in `docs/extraction-runbook.md` should use last_token vectors going forward, since they have higher probe acc and are method-consistent with CC/IH.
- The 4×4 specificity matrix should be expected to show partial cross-talk between CC and RT on qwen3-4b — F98's partial-branch outcome is the realistic expectation for that model.
- `docs/post-mvp-decisions.md` partial branch handling kicks in once gemma data lands.

### Caveats

- The 0.520 max-|cos| at the worst layer is *just* over the 0.50 threshold. If the threshold had been 0.55, the pair would still be technically clean. We did not move it post-hoc — 0.50 was committed in F98 / config.yaml before any data existed.
- Retention 0.92 is still well above the 70% floor, meaning we *can* mostly reconstruct CC by projecting out RT. The partial-overlap is not catastrophic.
- These numbers are aggregates across all 36 layers; CC ⊥ RT crosses 0.50 only at the deepest layers (per max-|cos|=0.52), and is in the 0.30–0.40 range across L18–25. Steering at mid-layers (where the per-layer |cos| is lower) may show less behavioural cross-talk than the aggregate-mean suggests.

### Applies to

- F99 (downgrade qwen verdict from all_clean to partial; gemma TBD pending re-extraction)
- F98 publication framework (we are on the partial branch for qwen)
- `docs/extraction-runbook.md` §11 (resolve methodological-consistency issue: standardise on last_token)
- `docs/post-mvp-decisions.md` (engage partial-branch decision logic once full picture lands)

### Artifacts

- `mvp/results/vectors/qwen3-4b/triplets-reasoning-transparency/last_token/` — 36 layer vectors
- `mvp/results/vectors/qwen3-4b/triplets-reasoning-transparency/extraction_summary_last_token.json`
- `mvp/results/rt_lasttoken.log` — extraction log
- Comparison script: re-runnable from local pulled vectors

---


## F102 (2026-04-25 evening) — Uniform last_token MVE matrix: gemma is all_clean (6/6); qwen is collapse (3/6) with CC, EG, RT forming a partial-overlap cluster at deeper layers. Cross-model split is the headline.

**Status:** Final geometric MVE result on uniform-method (last_token) vectors for both models. All 4 (model, virtue) re-extractions completed (`lasttoken_remaining` tmux on `phronesis-v2-l4`, 00:34→01:10 UTC). MVE pipeline updated to default to last_token for EG/RT (`mvp/analysis/compute_mve.py`). `analysis/run_analysis.py --mve-only` re-run, fresh report at `mvp/results/analysis_report/`.

**Pre-registered per F98** — branches were committed before any data existed.

### The verdict

```
qwen3-4b:        collapse  (3/6 pairs pass)
gemma-4-E4B-it:  all_clean (6/6 pairs pass)
```

The two models give opposite answers to the same question. **The cross-model split IS the headline.**

### Full MVE matrix (uniform last_token, both models)

#### qwen3-4b — 3/6 pass → ❌ COLLAPSE

| pair | mean \|cos\| | max \|cos\| | retention | verdict |
|---|---|---|---|---|
| CC ⊥ IH | 0.179 | 0.314 | 98.1% | 🟢 pass |
| CC ⊥ EG | **0.376** | 0.453 | 92.4% | 🟡 partial |
| CC ⊥ RT | **0.377** | **0.520** | 92.2% | 🟡 partial |
| IH ⊥ EG | 0.104 | 0.211 | 99.3% | 🟢 pass |
| IH ⊥ RT | 0.059 | 0.120 | 99.8% | 🟢 pass |
| EG ⊥ RT | **0.334** | **0.554** | 93.2% | 🟡 partial |

#### gemma-4-E4B-it — 6/6 pass → ✅ ALL CLEAN

| pair | mean \|cos\| | max \|cos\| | retention | verdict |
|---|---|---|---|---|
| CC ⊥ IH | 0.030 | 0.104 | 99.9% | 🟢 pass |
| CC ⊥ EG | 0.087 | 0.192 | 99.5% | 🟢 pass |
| CC ⊥ RT | 0.072 | 0.167 | 99.7% | 🟢 pass |
| IH ⊥ EG | 0.053 | 0.167 | 99.8% | 🟢 pass |
| IH ⊥ RT | 0.033 | 0.100 | 99.9% | 🟢 pass |
| EG ⊥ RT | 0.105 | 0.218 | 99.3% | 🟢 pass |

### What changed from the original generation-method MVE (F99)

- **qwen3-4b**: was 6/6 all_clean (with noisy generation-method EG/RT); now 3/6 collapse. CC⊥EG (0.16→0.38), CC⊥RT (0.10→0.38), EG⊥RT (0.10→0.33) all jumped from clean into partial-overlap. The original "clean orthogonality" was largely an artefact of using noise vectors.
- **gemma-4-E4B-it**: was 6/6 all_clean (generation), still 6/6 all_clean (last_token). Numbers shifted slightly (EG/RT pairs got modestly cleaner). Method-confound was real but smaller in magnitude on gemma — consistent with gemma's higher generation-method probe accuracies (0.74-0.83 vs qwen's 0.52-0.66).

### Per-layer pattern on qwen — late-layer shared direction

Per `mvp/results/analysis_report/per_layer_cosine_qwen3-4b.png`:

- **L0–15**: CC, EG, RT pairs hover around 0.20–0.40 with significant variance — no clear cluster.
- **L20–31**: CC⊥EG, CC⊥RT, and EG⊥RT all rise together to 0.40–0.55. EG⊥RT crosses 0.50 at L29–31, peaks 0.554 at L30. CC⊥RT crosses 0.50 at L31, peaks 0.520.
- **CC⊥IH stays clean throughout** (mean 0.179) — IH remains orthogonal to all three.
- IH⊥EG and IH⊥RT also stay clean (means 0.104, 0.059).

**Mechanistic reading:** at qwen3-4b's deeper layers — where the model has integrated the full prompt context — three of the four virtues (CC, EG, RT) share a substantial direction component. That direction is plausibly an "epistemic care / scientific reasoning disposition" — the *AOT cluster* flagged in F39 as a pre-data risk, plus CC. IH (intellectual humility / abstention) sits on a different mechanism that doesn't fold into the cluster.

This is a genuine, mechanistically interpretable finding — not a null result. Qwen3-4B's residual stream at depth treats epistemic confidence-calibration, evidence-grounding, and reasoning-transparency as facets of one underlying disposition, not as four independent dimensions.

### Per-layer pattern on gemma — clean throughout

Per `mvp/results/analysis_report/per_layer_cosine_gemma-4-E4B-it.png`:

- All 6 pairs hover below 0.20 mean across all 42 layers.
- Single transient spike: EG⊥RT max 0.218 around L7. Otherwise comfortably clean.
- CC⊥IH at 0.030 is the cleanest pair on either model.

Gemma 4 E4B-it maintains four geometrically-distinct virtue directions all the way through. Either gemma has a richer residual-stream structure that can support more disentangled epistemic dimensions, or it's the smaller / different training that prevented the cluster from forming. Mechanistic-interpretability question; out of scope here.

### F98 pre-registered branches — what we landed on

F98 (committed before any data) defined three branches **per model**:
- all_clean: 6/6 pass
- partial: 5/6 pass
- collapse: ≤4/6 pass OR EG × RT collapse

**qwen3-4b: collapse.** Two reasons satisfied: (i) only 3/6 pass; (ii) EG⊥RT max 0.554 > 0.50, technically a single-layer collapse though mean stays partial.

**gemma-4-E4B-it: all_clean.** All 6 pairs comfortably below thresholds.

The MVP-level overall verdict is **mixed / cross-model-split**, which F98 didn't explicitly enumerate but `docs/post-mvp-decisions.md` does cover (under partial/collapse sub-branches): publishable as a "model-dependent virtue-direction structure" finding.

### F39 status

F39 pre-registered the EG×RT cluster collapse as the *single biggest pre-data risk*. Result:

- **On qwen3-4b: F39 risk materialised (partially).** EG⊥RT mean 0.334, max 0.554 — partial overlap, with single-layer collapse at L29-31. But the cluster includes CC as well — a 3-way overlap, not the 2-way EG-RT pair F39 forecast.
- **On gemma-4-E4B-it: F39 risk did NOT materialise.** EG⊥RT mean 0.105, max 0.218 — clean across all 42 layers.

So F39 is *model-dependent*. Same corpus, same extraction method, opposite verdict on the two models.

### Headline reframe

The MVP claim cannot be "four orthogonal epistemic-virtue directions on small open models." It can be:

> **"Cross-model evidence that geometric separation of CC/IH/EG/RT virtue directions is model-dependent at the 4B scale. Gemma 4 E4B-it cleanly separates all four (6/6 pass); Qwen3-4B shows a partial-overlap cluster of CC, EG, and RT at deeper layers (3/6 pass), with IH remaining orthogonal. The same triplet corpus and extraction method gives opposite verdicts."**

This is a more interesting finding than monolithic all_clean would have been. It implies:
1. The "atomic virtue direction" hypothesis isn't model-invariant.
2. There's something about qwen3-4b's representation that bundles CC/EG/RT — open mech-interp question.
3. IH consistently behaves differently from the AOT-related virtues, on both models. That's a robust observation.

### What to do next under F98 + post-mvp-decisions.md

`docs/post-mvp-decisions.md` partial / collapse sub-branches engage. Specifically:

- **Behavioural 4×4 specificity matrix is still worth running**, but with revised expectations:
  - On gemma: should see clean diagonal-wins with low off-diagonal (matches geometric all_clean).
  - On qwen: should see CC-row × EG-eval, CC-row × RT-eval, RT-row × EG-eval cells with substantial cross-talk (matches geometric partial-overlap). IH-row × everything-else should stay clean.
  - The 4×4 matrix is the test of whether the geometric finding has behavioural consequences.
- **α-sweep can proceed.** Layer choice for qwen needs care — mid-layers (L18–22) where the cluster is less collapsed are probably better for clean steering of any one virtue.
- **No further re-extraction needed.** The methodological-consistency issue is resolved (uniform last_token).

### Open questions / honest deferred items

- **Why does qwen cluster but gemma doesn't?** Mechanistic interp question. Probable next step in a published version: ablation studies on the deep-layer residual stream. Out of scope for the MVP write-up.
- **Is the cluster a property of qwen3-4b specifically, or all qwen-family models?** Would need qwen-2.5-3b or qwen3-7b to test. Out of scope.
- **Does the cluster predict behavioural cross-talk?** This is what the 4×4 specificity matrix will answer.
- **Is there a corpus-confound I'm missing?** Same triplet corpus produced clean separation on gemma and partial collapse on qwen. So the finding survives the corpus-confound test (a corpus issue would affect both models similarly).

### Updates to compute_mve.py

`mvp/analysis/compute_mve.py` `DEFAULT_VIRTUE_PATHS` updated: EG and RT now point to `last_token` method (was `generation`). Annotation cites F101/F102. F99's `analysis_report/` was regenerated; the version on disk reflects F102 numbers.

### Applies to

- F99 (verdict downgraded — F99 stands as historical record of the noisy generation-method MVE; F102 is the canonical geometric result)
- F98 (qwen on collapse branch, gemma on all_clean branch — split outcome)
- F39 (model-dependent: partial materialisation on qwen, no materialisation on gemma)
- `docs/post-mvp-decisions.md` (engage partial/collapse sub-branches)
- `docs/extraction-runbook.md` §11 (methodological-consistency issue resolved — standardised on last_token)
- `docs/phase5-plan.md` (the "all_clean → 8-virtue scale-up" gating condition is no longer met cleanly; revisit Phase-5 framing post-behavioural)

### Artifacts

- Report: `mvp/results/analysis_report/report.md` (regenerated with last_token vectors)
- Heatmaps: `mve_heatmap_{qwen3-4b,gemma-4-E4B-it}.png`
- Per-layer cosines: `per_layer_cosine_{qwen3-4b,gemma-4-E4B-it}.png`
- All 4 last_token vector dirs: `mvp/results/vectors/{qwen3-4b,gemma-4-E4B-it}/triplets-{evidence-grounding,reasoning-transparency}/last_token/`
- Generation-method summaries preserved as `extraction_summary_generation.json` for cross-method comparison
- Re-extraction log: `mvp/results/lasttoken_remaining.log` and `rt_lasttoken.log`

---



## F103 (2026-04-26) — Hand-review verdict on the α-sweep: the qwen × RT × L18 α=20 +5.19 headline is auto-scorer gaming on degenerate output. Real signals exist but are an order of magnitude smaller.

**Status:** Independent hand-review of all 690 α-sweep generations (separate Claude session, full-pass with per-item structured signals + manual reading of every Priority-1/2/3/4/5 cell). Verdict: **the +5.19 RT headline is fake.** Reproduces the F94-UPDATE failure mode the project's manual-first policy was designed to catch.

**Pre-registered per F98 + Day-15 manual-first policy** — this is exactly why we committed to hand-review of every behavioural cell before publishing any number.

### The retraction

**qwen × RT × L18 α=20** (best auto-scorer pick, baseline 2.13 → steered 7.32, +5.19):
- All 5 generations are catastrophic repetition loops
- None close their `<think>` tag
- rt-p06 (auto rt_score=18.46) and rt-p16 (rt_score=14.08) score high *purely* because the loops contain regex-friendly filler tokens ("therefore", "the reason is", "so", "but wait")
- Hand-rubric RT score: **1.0 vs baseline 3.0** — i.e. steering at this magnitude/layer makes RT *worse*, not better
- The remaining three steered items in this cell score *lower* than baseline by hand-rubric

The auto-scorer awarded the +5.19 to a degenerate-output cell. By any reading (human or instrumental), this cell is broken output, not a 3.4× behavioural improvement.

### What the hand-rubric actually shows (real, smaller signals)

Per-cell hand-rubric scores (1-5 scale per virtue), baseline-anchored:

#### qwen × RT (baseline RT=3.0)

| Cell | Hand-rubric RT | Verdict |
|---|---|---|
| L22 α=8 | **3.6** | Clean +0.6 — best clean RT cell |
| L22 α=4, L25 α=4 | 3.6 | Clean +0.6 |
| L18 α=4, L18 α=8, L20 α=4–20, L22 α=12–20, L25 α=8–20 | 3.4 | Clean +0.4 (consistent across most cells) |
| L18 α=12 | 3.0 | No effect |
| L18 α=16 | 2.6 | Partial degeneracy (3/5 truncated) |
| **L18 α=20** | **1.0** | **Catastrophic degeneracy in 5/5** |

Real RT signal: **+0.4 to +0.6** across most clean cells. Not zero, but ~10× smaller than the auto-scorer claimed.

#### qwen × IH (baseline IH=3.2)

| Cell | Hand-rubric IH | Verdict |
|---|---|---|
| Most cells (L18 α≤16, L20 α=4–20, L22, L25 most α) | **4.0** | Clean +0.8 (multiple cells tied) |
| **L18 α=20 (auto-pick)** | **3.2** | No improvement + fp-gandhi hallucination ("Andre Devon" 1957 Peace Prize) |
| L25 α=12 | 3.4 | Mid |

Real IH signal: **+0.8** on multiple clean cells. The auto-scorer pick (L18 α=20) is among the *worst* clean cells because it abstains in regex-friendly ways while introducing F94-style hallucination on fp-gandhi.

#### qwen × CC (baseline CC=2.4 on AIME)

| Cell | Hand-rubric CC | Verdict |
|---|---|---|
| Most cells in {L20 α=8, L20 α=20, L22 α=4–8, L25 α=4–20} | **2.8** | Clean +0.4 |
| Higher α at L18/L20/L22 | 1.6–2.2 | Truncation/degeneracy |

Real CC signal: **+0.4** consistent across many clean cells. Item 72 win (baseline-spiral → clean-commit on `\boxed{540}`) is real but doesn't generalise across all items — items 42 and 58 stay intractable for both baseline and steered. Steering improves *commit behaviour* without improving underlying capability.

#### gemma × all four virtues

**Confirmed null.** All 33 gemma steered cells produce hand-rubric scores within ±0.4 of gemma baseline. No degeneracy detected anywhere. No qualitative virtue shift. Steering is taking effect numerically (regex scores fluctuate slightly) but not behaviourally on these benchmarks at any α tested.

### Re-picked best cells (using hand-rubric, for the record)

If we ever run the 4×4 specificity matrix or write up "best (α, layer) per virtue," these are the corrected picks based on hand-review:

| Model × Virtue | Auto-scorer pick | Hand-rubric pick | Hand-rubric RT-score |
|---|---|---|---|
| qwen × CC | L25 α=20 | **L25 α=8** (or any L25/L22 mid-α) | 2.8 |
| qwen × IH | L18 α=20 (degenerate) | **L20 α=20** or **L22 α=12** (multiple ties at 4.0) | 4.0 |
| qwen × EG | L18 α=4 | No clean pick — all cells ~baseline | 2.2-2.8 |
| qwen × RT | L18 α=20 (degenerate) | **L22 α=8** | 3.6 |
| gemma × all | various | No pick — null result | — |

### Auto-scorer failure modes documented

The hand-review surfaced two new auto-scorer failure modes:

- **FM-8: degenerate-output regex gaming.** Repetition loops with regex-friendly filler tokens score arbitrarily high. Required mitigation: coherence gate (compression-ratio threshold + `<think>` closure check) before any soft score is accepted. Documented in `docs/scoring.md`.
- **FM-9: false-negative on clean structured prose.** qwen × RT × L25 α=12 / rt-p14 scored auto rt_score=0.00 while hand-review gave RT=3 ("clean structured answer; regex misses it"). The regex misses real virtue when the response uses domain-appropriate-but-non-regex-matching language. Bidirectional error.

Both failure modes appear at high rate in the α-sweep data. Auto-scorer is fundamentally inadequate as a sole signal — both for over-rewarding (FM-8) and under-rewarding (FM-9).

### Specificity claim is independently weakened

Hand-review Priority 5 finding: **CC steering also produces RT-marker-rich prose.** Counted regex step-markers in qwen × CC × L25 α=20 AIME outputs (item 42: 110 step markers, item 58: 56 markers in long thinking traces). If applied to rt-eval, these would score high purely from token distribution.

This means the diagonal/off-diagonal distinction is partially confounded by "more structured reasoning generally" rather than virtue-specific behaviour. Even setting aside the L18 α=20 degeneracy, the +5.19 effect could not have been cleanly attributed to RT-direction-specific behaviour.

This is the F39 AOT-cluster risk re-materializing at the behavioural level — and matches F102's geometric finding (CC, EG, RT cluster on qwen3-4b at deep layers).

### Implication for F102

F102 had the partial/collapse geometric verdict for qwen and the all_clean for gemma. F103 doesn't change F102's geometric finding — it adds the *behavioural* layer:

- **Geometric layer (F102):** qwen partial-collapse, gemma all_clean.
- **Behavioural layer (F103):** qwen has small but real diagonal effects (+0.4 to +0.8 hand-rubric) plus high-α degeneracy on RT-L18; gemma has *zero* behavioural effect at any α.

Combined picture: **geometry and behaviour are partially decoupled, in opposite directions across the two models.** Gemma's clean directions don't drive eval scores. Qwen's collapsed directions do drive scores (modestly, real), with deep-layer high-α producing degeneracy rather than coherent virtue-aligned output.

### Connection to F94-UPDATE

This is the *exact same failure mode* as the original F94-UPDATE: an auto-scorer-based "win" that hand-review revealed to be hallucinated humility-theatre / now degenerate-loop-theatre. We documented F94-UPDATE on Day 10 and used it to justify the manual-first policy. Day 19 hand-review reproduces the pattern at larger scale. The policy worked — we caught it ourselves before any publication claim.

### Implications for the writeup

Under the F98 partial-branch with these revisions:

- **Headline cannot be "+5.19 diagonal effect on qwen × RT."** It is "small (+0.4 to +0.8) hand-verified diagonal effects on qwen, with auto-scorer vulnerable to degenerate-output gaming at high α."
- **Cross-model split (F102) remains the real headline.** The behavioural layer adds: gemma's clean geometry didn't translate to clean behavioural effect; qwen's collapsed geometry produced small effects.
- **Auto-scorer failure modes (FM-6/7/8/9) are themselves a publishable finding** — concrete instances of reward-hacking on small-scale regex scorers, mirroring RLHF-scale failures. Connects to the Day-18 RLHF-compression framing in `docs/post-mvp-decisions.md`.
- **Specificity claim is conditional** — needs the 4×4 matrix run with coherence-gated scoring to test cleanly. Without that, we can't separate "RT-direction-specific behaviour" from "more-reasoning-prose-generally."

### Caveats

- Hand-review is single-rater (one Claude session). Inter-rater reliability not measured. F72 caution applies.
- Hand-rubric was applied with rule-based scoring augmented by manual overrides on items read in full (~50-70 items deep-read of 690 total). Bulk items scored by signal-extraction rules tied to manual anchors.
- The reviewer's instrument-derived signals (compression ratio, `<think>` closure, regex marker counts) are themselves regex-adjacent and could miss novel failure modes.
- Hand-rubric scores are 1-5 ordinal; small differences (3.0 vs 3.4) may be at the edge of inter-rater reliability.

### Applies to

- **F94-UPDATE:** Day 10 precedent reproduced at scale on Day 19. Policy of manual-first hand-review justified by both events.
- **F102:** Geometric finding stands; behavioural layer added by F103.
- **F98:** We are on the partial branch (per F102 geometry); F103 specifies the partial outcome's behavioural character.
- **`docs/scoring.md`:** FM-8 (degenerate regex-gaming) and FM-9 (false-negative on clean prose) added.
- **`docs/post-mvp-decisions.md`:** Partial-branch handling needs to incorporate hand-review verdict (revision pending).
- **`docs/phase5-plan.md`:** §3.0 Coherence-gated scoring is now a hard pre-Phase-5 requirement.
- **`mvp/results/alpha_sweep/{model}.json`:** picks files contain auto-scorer picks; should be supplemented (not replaced) with hand-rubric-revised picks for any downstream use.

### Artifacts

- `phronesis_review_package.zip` — the full package shipped to the review session (README, 690 generations, picks JSONs)
- Reviewer outputs: `HAND_REVIEW_VERDICT.md`, `cell_verdicts.csv`, `hand_review_full.csv`, `analysis_signals.json`
- The reviewer's signal-extraction script (`analyze_all.py`) is re-runnable and could be incorporated into Phronesis as a coherence pre-filter for future sweeps

---

## F104 (2026-04-27, Day 20 evening) — Full hand-review of 200+ items REVERSES the F103 verdict on qwen × IH × L17. The auto-scorer was wrong; v_IH IS virtue-aligned and produces the cleanest behavioural effect of any vector tested.

### Setup

Per F103's manual-first policy, hand-reviewed every generation across three sweeps from Day 20:
- **Path A:** qwen × RT envelope, 24 cells × 5 prompts = 120 generations
- **Path D:** qwen × eg-eval-v2, 5 cells × 10 prompts = 50 generations
- **Path B:** qwen × IH × L17 ± α, 25 generations + α=−4 inversion test (5 generations)

**Total: ~200 hand-reviewed items.** Per-cell verdicts in `mvp/results/full_hand_review_pathA.md`, `_pathD.md`, `_synthesis.md`.

### What the hand-review changed about prior verdicts

#### v_IH × L17 — UPGRADED from "broken" to confident "working vector"

**Day 19 reading (per F103, auto-scorer hedge-density Δ = -0.845):** "vector misaligned, both ±α introduce fabrication."

**Day 20 hand-review reading:** v_IH × L17 produces **monotonic IH-virtuous behaviour with increasing α** on abstention prompts:
- Length decreases (less over-elaboration)
- Specific-date citations decrease (less fact-fabrication)
- Committal phrases ("was awarded", "won in YEAR") decrease
- Explicit uncertainty markers ("the question contains an inaccuracy", "I cannot determine") increase
- α=−4 test confirmed direction: subtracting v_IH causes **MORE** fabrication (hallucinated 1937 Gandhi Peace Prize)

The hedge-density auto-scorer was measuring the wrong dimension. We built an IH-v2 scorer (factual-specificity reduction + uncertainty markers + acknowledged limits) that confirms monotonic improvement: -7.68 → +4.51 across α=-4 to α=+12.

**Confidence: HIGH.** Most defensible vector found in the project.

#### v_RT × L15 α=8 — DOWNGRADED to borderline

**Day 19 reading:** "clean modest virtue-specific RT effect, +0.5 hand-rubric."

**Day 20 full envelope reading:** All clean cells produce roughly equivalent baseline-quality output. L15 α=8 has subtle qualitative shift on **2 of 5 items only** — different framing vocabulary on aging (selfish gene + antagonistic pleiotropy), specific evidence anchor on bridges (AASHTO guidelines). Other 3 of 5 items at L15 α=8 are indistinguishable from baseline. α≥10 at L15 introduces FM-8 degeneracy.

**Confidence: LOW-MED.** Real but at threshold of distinguishability.

#### v_EG × L7 — REVISED, vector exists but does the OPPOSITE of EG

**Day 19 reading:** "framework null on EG (baseline saturated)."

**Day 20 reading after Path D + IH-v2 cross-application:**
- Baseline already highly evidence-grounded on 9 of 10 v2 prompts.
- v_EG × L7 × α=4 **REDUCES** named-specifics by 10-30% on most prompts.
- Same direction of effect as v_IH × L17 (reduce specificity).
- v_EG and v_VERB at AP-peak layers behave similarly — both reduce factual specificity.

The vector extracted as v_EG is doing v_IH-like work, not v_EG-like work. **Confidence: HIGH** that v_EG × L7 is misaligned with the EG label.

### Net working-vector inventory after Day 20

| Vector | Confidence | Effect |
|---|---|---|
| qwen × IH × L17 α=+8 to +12 | **HIGH** | Reduces fabrication, increases uncertainty acknowledgment, more concise |
| qwen × RT × L15 α=8 | LOW-MED | Subtle vocabulary shifts on 2/5 items |
| qwen × EG × L7 | HIGH (it's MISALIGNED) | Reduces specificity — opposite of EG |
| qwen × CC × L9 | UNTESTED at peak | Pending dedicated test |
| All gemma × * | NULL | Confirmed null across 3 days |

**1 confidently working vector + 1 borderline + 1 actively wrong-direction + 1 untested + all gemma null.**

### Methodological lesson (partially restating F103 + F94-UPDATE)

We've spent days chasing auto-scorer numbers that didn't reflect actual model behaviour:
- Day 19: RT × L18 α=20 "+5.19" → degenerate FM-8 loop (per F103)
- Day 20: IH × L17 α=4 "−0.845" → real IH improvement that hedge-density missed (this finding)
- Day 20: EG × L7 α=8 "+0.185" → just baseline floor noise

**Without hand review, every claim from this project is unreliable.** The auto-scorers give numerical results that don't track behavioural reality. The IH-v2 / EG-v2 scorers built to address this DO track behaviour better, but they are themselves manually calibrated against hand-rubric.

### Applies to

- **F103:** v_IH × L17 verdict superseded — the auto-scorer regression was an artifact of measuring the wrong dimension. F103's "small +0.4 to +0.8 effects" reframing stands for RT and CC; for IH the effect is larger and qualitatively different (specificity-reduction monotonic with α, not vocabulary-shift).
- **`docs/scoring.md`:** add IH-v2 and EG-v2 scorers to the per-virtue scorer registry; document that they were calibrated post-hoc against hand-review (not pre-registered).
- **`docs/findings.md` F102:** geometric finding stands; behavioural addendum is "qwen × IH × L17 produces the cleanest behavioural effect among the four virtues, with v_RT borderline and v_EG/v_CC at AP peaks both producing specificity-reduction (label-mismatched)."

### Artifacts

- `mvp/results/full_hand_review_pathA.md` — per-cell verdicts for 24 RT envelope cells × 5 prompts
- `mvp/results/full_hand_review_pathD.md` — per-cell verdicts for 5 EG-v2 cells × 10 prompts
- `mvp/results/full_hand_review_synthesis.md` — synthesis across all hand reviews
- `mvp/benchmarks/ih_scorer_v2.py`, `mvp/benchmarks/eg_scorer_v2.py` — v2 scorers calibrated to hand-rubric
- `mvp/benchmarks/eg_prompts_v2.json` — 10 sharper EG prompts designed to discriminate evidence-grounded vs vague-appeal responses

---

## F105 (2026-04-28, Day 21-22) — Diagnostic batch reveals v_IH × L17 and v_CC × L9 produce *behaviorally identical* anti-FM-8 commit behavior, but cosine analysis shows they are *geometrically orthogonal*. Behavioral collision is downstream functional convergence, not residual-stream redundancy. Multiple corrections to the F104 vector inventory.

### Setup

Day 21 diagnostic batch on the v1 vectors (full hand review, 136 items, see `mvp/results/full_hand_review_diagnostic_batch.md`):
- **D1a** v_IH × L17 × α∈{4,8,12} on eg-eval-v2 (10 prompts × 3 α)
- **D1b** v_EG × L7 × α∈{4,8} on abstention (5 × 2)
- **D2** v_EG at deeper layers L18, L22 × α∈{4,8} on eg-eval-v2
- **D3** v_CC × L9 × α∈{−4,4,8,12} on cc-simple (8 × 4) — new "CC-simple" benchmark of 8 single-answer reasoning prompts (CRT classics, modus tollens, rate, primality, MCQ)

### Behavioral finding (Day 21)

**v_IH × L17 fixes the FM-8 spiral on eg-v2-10 (seismic damper) where baseline AND v_EG × L18, L22 all FM-8.** Forces `<think>` closure and commits to "20-40%" with calibrated hedge.

**v_CC × L9 fixes the FM-8 spiral on cc-s-01 (bat-and-ball) where baseline FM-8.** α=4/8/12 all save the prompt; α=-4 makes it worse.

Day-21 synthesis claimed: "v_IH × L17 and v_CC × L9 are the same anti-FM-8 commit-vector disposition, extracted from different (corpus, layer) pairs."

### Geometric correction (Day 22, from parallel Claude session)

A parallel Claude session ran a cosine + norm analysis of the v1 vectors at AP-peak layers (`mvp/results/cosine_analysis_v1_vectors.md`). Findings DIRECTLY CONTRADICT the same-disposition claim:

- **cos(v_IH @ L17, v_CC @ L9)** is uncomputable cross-layer (different layers in residual stream are not directly comparable). Within-layer:
  - cos(v_IH, v_CC) @ L9 = +0.13
  - cos(v_IH, v_CC) @ L13 = +0.14
  - cos(v_IH, v_CC) @ L17 = +0.08
- All three sit in the **orthogonal band** (|cos| < 0.2).
- v_IH is geometrically **outlier** vs every other v1 virtue (|cos| ≤ 0.14 vs CC, EG, RT at all layers tested).
- v_CC, v_EG, v_RT form a loose cluster (pairwise cos 0.20–0.40).

Random + v_VERB controls confirm the geometry is healthy (cosines within ±0.02 floor).

### Reading after correction

The behavioral collision (both vectors fix FM-8) is **NOT** explained by residual-stream alignment. It is **downstream functional convergence** — two near-orthogonal directions that hit overlapping OV/MLP read-offs which both push `</think>` token-probability up.

This rescues the original "4 orthogonal virtues" framework hypothesis on v1 corpora — the four directions are geometrically distinct (with v_IH the clearest outlier and EG/RT/CC weakly clustered).

### Methodological gaps the corrected reading exposes

1. **Day 21's behavioral test was unidirectional.** v_IH × L17 was tested on eg-eval-v2; v_CC × L9 was tested only on cc-simple. The cc-simple benchmark was *deliberately designed* to elicit FM-8 ("Each prompt has a single clean answer that a competent reasoner commits to in 1-3 short steps. The risk for an over-thinking model is to spiral, equivocate, or hedge"). Any vector that reduces FM-8 looks identical to v_CC on cc-simple regardless of mechanism.

2. **The "downstream functional convergence" label is not a mechanism.** Two distinct mechanisms remain compatible with the cosine data:
   - **Reading 1**: orthogonal residual directions, shared OV/MLP read-off subspace → predicts identical behaviour on FM-8-irrelevant prompts.
   - **Reading 2**: different downstream circuits, both happen to suppress FM-8 as one output dimension → predicts divergent behaviour on FM-8-irrelevant prompts.
   - Distinguished by **bidirectional cross-application**: apply v_IH × L17 to cc-simple AND apply v_CC × L9 to eg-eval-v2; hand-rate detailed behaviour on FM-8-not-prone prompts. The Day 22 v2 sweep includes vIH_L17 on cc-simple but NOT vCC × L9 on eg-eval-v2 — partial test only.

### Updated working-vector inventory after Day 21-22

(Replaces F104's net.)

| Vector | Status | Notes |
|---|---|---|
| qwen × IH × L17 α=+8 to +12 | **HIGH** confidence working | Anti-FM-8 / commit force; produces both humble abstention and confident commit depending on prompt demands |
| qwen × CC × L9 α=+4 to +12 | **HIGH** confidence working (NEW) | Same anti-FM-8 mechanism as IH but at a different residual-stream direction |
| qwen × EG × L7 α=4-8 | **LOW** confidence (and risky) | Adds named-entity tokens; **confabulates** them on knowledge-gap prompts (e.g., fabricates "1937 Gandhi declined the Nobel" on fp-gandhi). Useful only when model already has ground truth |
| qwen × EG × L18, L22 | NULL | No directional effect; cannot save FM-8 spiral prompts |
| qwen × RT × L15 α=8 | LOW-MED | Borderline, no new evidence |
| All gemma × * | NULL | Confirmed null |

### Applies to

- **F104:** Vector inventory revised — v_CC × L9 now confirmed working (was UNTESTED). v_IH × L17 confirmed working (consistent with F104). Geometric finding adds: the behavioral collision between IH and CC is real but at the downstream-circuit level, not at the residual-stream-direction level.
- **F102:** Cluster pattern (CC/EG/RT cluster on qwen, IH outlier) holds under direct cosine measurement. Strengthens F102's geometric finding with a quantitative basis.
- **`docs/scoring.md`:** add cc-simple as a new manual-rated benchmark (8 prompts, no auto-scorer, hand-rated for FM-8 vs commit). Add cc_simple loader in `mvp/benchmarks/cc_simple.py` and register in benchmarks registry.
- **`docs/post-mvp-decisions.md`:** the "1 disposition reachable from many corpora" reading from yesterday's simple-terms doc is *wrong* on geometric grounds. The right framing is "4 distinguishable dispositions, with v_IH the clearest outlier; v_IH and v_CC behaviorally collide via downstream functional convergence, not residual-stream alignment." Composition-steering motivation is recovered (orthogonal directions can be summed meaningfully).

### Artifacts

- `mvp/results/full_hand_review_diagnostic_batch.md` — full 136-item Day 21 hand review
- `mvp/results/cosine_analysis_v1_vectors.md` — Day 22 v1 cosine + norm analysis (parallel Claude session, commit `b1d0465`)
- `mvp/results/v2_cosine_observations.md` — Day 22 honest framing of v2 cosine matrix with five caveats from second Claude critique
- `mvp/benchmarks/cc_simple.py`, `mvp/benchmarks/cc_simple_prompts.json` — new CC diagnostic benchmark

---

## F106 (2026-04-29, Day 22) — v2 sweep with redesigned corpora: corpus expansion partially rotates EG/RT/IH vectors; CC_numeric carves a partly-distinct sub-direction; v_EG_v2 corpus-redesign success is geometrically partial (cos 0.70 with v1 buggy vector); two extraction-pipeline bugs caught and patched.

### Setup

Other Claude session generated 120 new triplets (commit `2c5fde7`):
- 30 `claude-eg-*` (specificity-density contrast, replacing v1 calibration-framing axis-confusion)
- 30 `claude-rt-*` (load-bearing-assumption contrast, hedge-matched)
- 20 `claude-cc-*` (explicit-numerical-probability sub-axis)
- 40 `expansion-*` IH triplets (4 sub-types × 10 each)
- Plus 22 EG NV files genericized in-place + 30 RT NV files hedge-matched in-place

The Day 22 v2 sweep re-extracts vectors from the expanded corpora at all 36 layers, computes cosine matrix, runs 15 behavioral cells.

Sweep is in flight at time of writing (Phase 4 cell ~3/15). Full results pending; preliminary on this F entry.

### Pipeline bugs caught

#### Bug 1: extract_v2.py resume-logic returned stale v1 as v2

`extract_v2.py` skips any layer whose metadata.json already exists. The Day 22 sweep wrote backup copies to `_v1_backup` dirs but did NOT delete the source. extract_v2 saw v1 metadata files and skipped every layer in ~1 minute, reporting v1 results as v2.

Confirmed by `cmp` on `layer_18_virtue_vector.npy`: source and `_v1_backup` were byte-identical for EG and RT after the first sweep run.

**Fix** (commit `4c8cfe5`): added `rm -rf $VEC_ROOT/$SUB/last_token` after the cp -r backup to force fresh extraction.

#### Bug 2: --layers sweep misses odd layers (where AP peaks live)

`extract_v2.py --layers sweep` covers only even layers (`range(2, 35, 2)` = 2,4,...,34). Our AP-peak layers (EG=L7, CC=L9, RT=L15, IH=L17) are all **odd**. So Phase 4 failed with `FileNotFoundError` on 9 of 12 cells.

The 3 cc-simple cells that "succeeded" used vector "L9" which is registered to the **legacy** 50-triplet hand corpus (`triplets/`), not the new v2 CC corpus. Stale-v1 results.

**Fix** (commit `9f4018c`): `--layers sweep` → `--layers all`; added `CC_full_L9`, `CC_full_L17`, `CC_num_L9`, `CC_num_L17` registry entries pointing to new corpora; updated Phase 4 cell list.

### Geometric findings (preliminary, from cosine matrix)

`mvp/results/v2_sweep_20260428/cosine_matrix.html` (auto-generated) and `mvp/results/v2_cosine_observations.md` (honest framing).

#### v_IH remains the geometric outlier under v2 corpora

cos(v_IH, v_CC_full) at v_IH's home layer L17 = **+0.000**. Across L9, L13, L15, L17, L22, all v_IH cosines vs other v2 virtues fall in [-0.04, +0.13]. Random baseline ±0.02 floor.

The v1 finding (F105) replicates on v2 vectors. v_IH is genuinely orthogonal to every other virtue.

#### v_EG, v_RT, v_CC_full form a cluster

Pairwise cos at L17:
- EG ↔ RT: +0.43
- EG ↔ CC_full: +0.33
- RT ↔ CC_full: +0.30

Same pattern at L7, L9, L13, L15, L22 (cluster strengthens at L22 to ~0.45). These three vectors are not redundant but inhabit a shared residual-stream subspace.

#### v_CC_numeric partly carves out from v_CC_full

cos(CC_full, CC_numeric) = +0.28 to +0.41 across layers. Less correlated with EG/RT (0.09–0.21) than CC_full is (0.30–0.40). The 20 new claude-cc-* triplets carve a partly-distinct geometric direction.

#### v2 corpus rotation is partial, not clean

| Pair | Layer | cos(v1, v2) |
|---|---|---|
| EG_v2 vs EG_v1 | 7 | +0.70 |
| RT_v2 vs RT_v1 | 15 | +0.78 |
| IH_v2 vs IH_v1 | 17 | +0.85 |

EG rotated most (~45°), IH least (~32°). All three retain a majority of their v1 direction. **Importantly, v_EG_v2 still has cos 0.70 with v_EG_v1, meaning the redesigned vector retains 70% directional alignment with the buggy v1 calibration-axis vector.** The corpus-audit (commit `cc26cf0`) shows the contrast at the *text level* genuinely changed; the diff-of-means only partially followed.

This is consistent with two readings:
- v_EG_v2 is "calibration vector with some specificity character mixed in" — partial fix
- v_EG_v2 is "specificity vector that shares substantial subspace with the calibration-axis cluster because surface features are similar" — clean fix that doesn't show up geometrically

Phase 4 behavior on the Gandhi false-premise prompt is the discriminating test; that cell hasn't run yet at time of this entry.

### Behavioral findings (preliminary, partial Phase 4 data)

Hand-review of the first 20 fresh v2 generations (vEG_L7 × α=4 and α=8 on 10 eg-eval-v2 prompts). Detailed verdict in earlier session message; summary:

- v_EG_v2 maintains baseline-level entity richness on prompts where the model already has knowledge (smoking, aspirin, SSRIs, ibuprofen).
- v_EG_v2 adds **new specifics** on a few prompts: cites exact H₀ value 67.4 km/s/Mpc, names NASA GISS / NOAA datasets, names Jehol Group + Nemegt Basin geological formations on dinosaur-feathers prompt (v1 didn't reach those).
- **At α=8, v_EG_v2 SAVES the eg-v2-10 seismic damper FM-8** — committing to "20-40%" with named damper types and example buildings. v1 EG_L7, v1 EG_L18, v1 EG_L22 all FM-8'd this prompt. This is real improvement.
- At α=4, still FM-8 on seismic damper.

Confabulation question (does v_EG_v2 still hallucinate specifics on knowledge-gap prompts like Gandhi?) **OPEN** — the abstention cells haven't run yet in Phase 4.

### Honest caveats (per parallel Claude critique on v2 cosine)

Five points where Day 22 self-correction is necessary:

1. The "4 orthogonal virtues alive" framing overstates the asymmetry. Real pattern is **1 distinct direction (IH) + 3 weakly distinguishable (EG/RT/CC) + 1 partial sub-carve-out (CC_numeric)** — not symmetric 4-way.
2. The "shared surface features" hypothesis for the EG/RT/CC cluster is untested; it competes with "shared underlying disposition" and "corpus-generation artifact" readings. Discriminating test: extract diff-of-means from non-scientific corpus and check if cluster persists.
3. cos(v_EG_v2, v_EG_v1) = 0.70 is a partial rotation, not a clean axis-change. Be cautious about labelling v_EG_v2 a "specificity vector" until Phase 4 confirms behaviorally.
4. "Downstream functional convergence" is a label, not a mechanism. Two readings (shared circuit vs different circuits with overlapping output) remain compatible. Bidirectional cross-application test (vCC × L9 on eg-eval-v2) is the discriminator and is NOT in the current sweep.
5. "Composition becomes meaningful again" is premature. Orthogonality is necessary but not sufficient; composition behavioral test hasn't run.

### Applies to

- **F102, F104, F105:** geometric findings reinforced and extended at higher quantitative resolution. The cluster pattern (CC/EG/RT loose cluster, IH outlier) is now confirmed at every AP-peak layer with explicit cosine numbers.
- **`docs/extraction-runbook.md`:** add `--layers all` recommendation when AP-peak layers may be odd; document the resume-logic-skips-when-metadata-exists behavior and add a wipe step before any extraction intended to be fresh.
- **`docs/scoring.md`:** EG-v2 scorer was used pre-correction; remember it's a calibration-axis scorer for the most part, not a pure specificity scorer. Behavioral confirmation pending.
- **`docs/post-mvp-decisions.md`:** Round 3 sweep design (queued): bidirectional cross-application + composition behavioral test + non-scientific corpus extraction.

### Artifacts

- `mvp/run_v2_sweep.sh`, `mvp/cosine_v2_analysis.py`, `mvp/dashboard_v2_sweep.py` — v2 sweep infrastructure
- `mvp/results/v2_sweep_20260428/cosine_matrix.{json,html}` — pairwise cosines across all v1 + v2 vectors
- `mvp/results/v2_cosine_observations.md` — honest framing with 5 caveats
- `mvp/results/v2_sweep_pull_log.md` — wake-up chain log
- `corpus_inspection_EG_v2.md` — EG redesign audit (4/4 deficiency triplets sampled, contrast confirmed at text level)
- Behavioral data: `mvp/results/benchmark_probe/{cc-simple,abstention,eg-eval-v2}/d22_v2_*/` (in flight)


---

## F107 (2026-04-29, Day 22) — Frontier-model corpus generators have a *task-level* shared blind spot when asked to "rewrite less evidence-grounded": they edit framing rather than evidence content. This is deeper than the cross-family-blind-spot mitigation in §4.7 of generation-guidelines.md.

### Setup

The v1 EG corpus contained 40 hand-and-frontier-model-written triplets where, on per-triplet inspection (Day 21, `corpus_inspection_EG.md`), virtuous and non-virtuous-deficiency passages contained THE SAME specific facts (numbers, instruments, study sizes, named comparisons). They differed only in how the facts were framed (observation-vs-inference distinction, hedging on causal claims).

This was supposed to be a contrast on **specificity-density**, per the EG sub-facet definition. Instead, both passages had identical specificity; the contrast axis was **calibration framing**. The diff-of-means vector therefore loaded on calibration, not specificity.

### Generalization (the F107 finding)

Spot-checking the v1 EG corpus across the 40 triplets revealed the pattern was systematic, not a few unlucky generations. When asked to "rewrite a virtuous passage to be a non-virtuous-deficiency version (less evidence-grounded)," frontier models — across families (chatgpt-eg-*, sonnet-eg-*, hand-written) — **reliably preserved scientific specifics and edited framing instead.** Examples:

- chatgpt-eg-02 (algal bloom): both versions cite "the empirical claim is nitrogen limitation under the tank conditions" / "the obvious source"; both have the same numerical context.
- sonnet-eg-08 (predator-prey): both versions cite 840 ± 60 trout, 12-year record, 33% decline. NV says "Pike predation caused the trout collapse — the diet data confirm this directly"; V says "Pike are a plausible cause" + careful diet-data reasoning. Same specifics, different framing.
- chatgpt-eg-16 (sodium/BP): both versions identical numerically; differ only on calibration.

This is a **task-level** failure mode that affects all frontier families, not just one family's bias. When the rewriter sees scientific prose with specific anchors, it interprets "less evidence-grounded" as "less calibrated/less hedged" rather than "fewer named anchors" — because evidence-grounding-as-specificity is a less salient axis in pretraining data than evidence-grounding-as-calibration.

### Why this matters for `generation-guidelines.md` §4.7

Current §4.7 mitigates **cross-family bias** by using two different model families for generation vs verification. That works for some failure modes (e.g., a single family's vocabulary preferences). It does **not** address task-level blind spots that all families share.

The redesign (Day 21-22, commit `2c5fde7`) addressed this by giving the rewriter explicit instructions: "non-virtuous-deficiency strips numbers / instruments / dates / named studies; preserves disposition-language vocabulary." With that explicit guidance, the new claude-eg-* triplets contrast on specificity-density genuinely (audit confirmed in `corpus_inspection_EG_v2.md`).

But the geometry tells a partial story (per F106): cos(v_EG_v2, v_EG_v1) = 0.70 — the redesigned vector retains 70% directional alignment with the buggy v1 calibration-axis vector. So even after the corpus contrast was fixed at the text level, the diff-of-means picked up substantial calibration-axis content. Two compatible readings (per F106): (a) v_EG_v2 is "calibration vector with specificity character mixed in" — partial fix only; or (b) v_EG_v2 is genuinely a specificity vector that shares substantial subspace with the calibration-axis cluster because surface features of the corpus are similar.

Behavioral evaluation pending in current sweep's Phase 4.

### Implication for future corpus design

When designing contrast pairs:

1. **Anticipate task-level blind spots.** Frontier-model generators interpret "less X" relative to the most-salient-axis-of-X in pretraining data. If your axis-of-X is a less salient one, you'll get a contrast on the more-salient axis instead.
2. **Specify the axis explicitly in the rewriter prompt.** Don't rely on the rewriter's inference from the virtue label. State explicitly what should change and what should stay constant.
3. **Audit by reading triplets.** After generation, read 4-5 random triplets and ask: "what is the *concrete textual* difference between virtuous and non-virtuous?" If you can't answer that quickly, the contrast may not be on your intended axis.
4. **Rewrite-the-rewriter-prompt is cheaper than re-extract.** Day 21-22's redesign cost was ~1 day of corpus work + ~1 day of re-extraction. Building the wrong contrast and only catching it via behavioral analysis cost ~3 weeks (the v1 EG findings carried implicit-calibration-not-specificity confound through F100-F104).
5. **Diff-of-means may not faithfully follow corpus contrast.** Even with the right text-level contrast, the diff-of-means vector can pick up shared subspace structure because the surface features of the two corpora overlap. Geometric distinguishability of the redesigned vector from the buggy vector is a quality check that should follow corpus redesign.

### Applies to

- **`docs/generation-guidelines.md` §4.7:** add task-level-blind-spot mitigation: explicitly state the axis-of-contrast in the rewriter prompt; don't rely on inference from virtue label.
- **F71 (cross-family bias):** F107 supplements rather than supersedes — F71 is real and §4.7's two-family policy still helps. F107 documents an additional task-level failure mode that two-family rotation alone doesn't catch.
- **F106:** v_EG_v2's cos 0.70 with v_EG_v1 is partly explained by F107 — even with the rewriter prompt fixed, the surface features of "scientific reasoning prose" overlap enough that the diff-of-means doesn't fully decouple.

### Artifacts

- `mvp/results/corpus_inspection_EG.md` — the original observation across 40 v1 triplets
- `corpus_inspection_EG_v2.md` — verification that the redesign fixed the text-level contrast
- `mvp/results/v2_cosine_observations.md` §"v_EG_v2 vs v_EG_v1" — the geometric partial-rotation observation

