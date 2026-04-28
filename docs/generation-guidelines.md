# Phronesis — Generation Guidelines (Phase 3 Draft)

This document specifies how the Phronesis contrastive corpus is constructed: how fact packs are built, how the neutral baseline is generated, how the virtuous and non-virtuous rewrites are produced, and how the corpus is reviewed before extraction. It is the operational guide for Phase 2 corpus construction.

> **MVP scope note (Day 15, 2026-04-22):** The *active* virtues under corpus construction are listed in `mvp-virtues.md`. That doc specifies the 4 MVP virtues (Calibrated Confidence, Intellectual Humility, Evidence Grounding, Reasoning Transparency) and the 8-virtue full-study set, plus per-virtue operational guidelines (virtuous pattern / excess failure / deficiency failure / text indicators). Start there before using this document — `mvp-virtues.md` tells you *what* to generate corpus for, and this document tells you *how* to generate it. Also: during MVP, §4.7's automated verifier and §6's diversity metrics are optional add-ons — manual hand-review is primary. See `scoring.md` for the MVP manual-first policy.

**STATUS (2026-04-29 update):** Originally tagged "DRAFT SKELETON with TODOs" on April 9. Most sections are now operational and have been used for two corpus-generation cycles (v1: Day 9-19; v2: Day 21-22 redesign of EG/RT/CC contrasts). Some TODOs remain in §6 (per-concept marker tables) for the 11 non-MVP concepts; these are deferred until/unless MVP exits to full-study scope. The MVP-active 4 concepts (CC, IH, EG, RT) have operational marker guidance in `mvp-virtues.md`.

**Day-22 addendum:** §4.7 cross-family verifier policy needs supplementing per F107. Frontier-model rewriters share a *task-level* blind spot when asked to "rewrite less evidence-grounded" — they edit framing rather than evidence content, regardless of family. The mitigation is to specify the contrast axis explicitly in the rewriter prompt rather than relying on inference from the virtue label. See F107 in findings.md.

---

## ✅ RESOLVED 2026-04-29 — F73 Path A/B/C decision (originally a blocker)

**Resolution:** Path B chosen and executed. All Phase 4 extraction (Day 9 onward) used generation-based last-token activation capture per Path B's specification. Phase 5 steering (Days 17-22) operates on those vectors. The "BLOCKER" framing below is historical context only.

Original blocker text from April 9:

This document currently assumes **Path B** from F73 as the working default:
- The contrastive triplet corpus (neutral → virtuous → non-virtuous) remains as planned in Phase 2.
- Phase 4 extraction uses generation-based rather than comprehension-based activation capture: our triplet passages are used as prompts to the target model, and activations are extracted from the model's own continuations at the generation midpoint per F73's recommendation.

If the user confirms Path B after waking, this document is on track. If the user chooses Path A (keep corpus as-is but use comprehension-based extraction), the corpus-format sections below remain valid but a Phase 4 extraction note will need updating. If the user chooses Path C (redesign the corpus to produce scenario prompts instead of pre-written passages), **sections 3, 4, and 5 below require major rewrite** because the "pre-written passage with rewrite" structure is replaced by "scenario prompt with on-the-fly generation."

Drafting proceeds under Path B as the working default per the cron rule on handling genuine ambiguity ("proceed with a reasonable default, noting the assumption"). All Path-B-dependent content is clearly marked below.

---

## 1. Purpose and scope

Phronesis's Phase 2 produces a corpus of contrastive triplets that Phase 4 will use to extract activation vectors for each of the 15 concepts in `concepts.md`. Each triplet consists of:

- **Neutral baseline** — a passage depicting scientific reasoning on a specific scenario without strongly exhibiting the target virtue or its failure modes.
- **Virtuous rewrite** — a minimal edit of the neutral baseline that makes the target virtue clearly present in the reasoning.
- **Non-virtuous rewrite** — a minimal edit of the neutral baseline that depicts one of the two failure modes (excess or deficiency) of the target virtue, per the golden-mean design principle (concepts.md, F59, F62).

The corpus must enable a difference-of-means extraction that captures the target virtue as a direction in activation space, without confounding it with correctness, topic, vocabulary sophistication, or length. The specific threats this document addresses are:

- **Topic confound** (per F4) — the extracted vector encoding "talking about biology" instead of the target virtue.
- **Correctness confound** (per F30, F66) — the extracted vector encoding "being right" instead of the virtue.
- **Vocabulary/style confound** (per F19) — the extracted vector encoding "sophisticated language" instead of the virtue.
- **Mode and knowledge collapse** (per F71) — the generator producing narrow, homogenous passages that reduce corpus diversity.
- **Injection contamination** (per F5) — text from external sources containing instructions that leak into the generated passages.
- **Geometric one-sidedness** (per F59, F62) — all non-virtuous passages depicting only excess or only deficiency failures, producing a vector that is anti-arrogance rather than pro-humility.

## 2. Fact packs — curating real scientific scenarios

A **fact pack** is a structured scaffold for a single reasoning scenario, drawn from real scientific research but stripped of identifying content. Each fact pack provides the substance around which a triplet will be built: the phenomenon being reasoned about, the key facts that must remain invariant across all three versions (neutral, virtuous, non-virtuous), and the ambiguity or uncertainty that creates room for the virtue to manifest.

### 2.1. What a fact pack contains

Every fact pack must include:

- **Scenario title** — a short descriptor for the scenario, anonymized (no real names, no specific dates).
- **Domain** — one of the quota-managed domains (see §3.1).
- **Factual substrate** — 3–6 bullet points stating the key observations, data points, and methodological context that must remain invariant across the triplet. For example: "Study of 47 patients with disease X showed protein Y elevated in the 39 who had outcome A and normal in the 8 who had outcome B."
- **Known ambiguity** — 1–2 bullet points stating the genuine uncertainty or alternative interpretations that exist in the real scenario. This is where the virtue can bite: a virtuous reasoner considers the ambiguity; a non-virtuous reasoner does not.
- **Conclusion space** — 2–4 bullet points listing plausible conclusions the reasoner could reach given the evidence. At least one plausible conclusion should be consistent with genuinely careful reasoning; at least one should be consistent with either excess or deficiency failure.
- **Target concept** — the concept (1–15 from concepts.md) that this fact pack will be used to generate a triplet for. A single fact pack may produce triplets for multiple concepts if the scenario is rich enough.

### 2.2. Sources for fact packs

Fact packs should be drawn from real scientific research to avoid the generic-toy-problem pattern that pure LLM generation produces. Preferred sources:

- Peer-reviewed papers (abstracts + methods sections).
- Textbook examples of methodological debates (e.g., classic replication failures, canonical statistical cautionary tales).
- Blog posts by practicing scientists discussing their own reasoning.
- Historical case studies of scientific discovery or correction.

**Sanitization requirement (per F5):** External sources may contain text that resembles instructions. Before a fact pack is used for generation, it must be stripped of anything that reads like a directive, a command, or an instruction. This protects the corpus from prompt-injection artifacts that would contaminate the extracted vector.

**Human-written anchor mixing (per F71):** To defend against mode collapse from the LLM generator, at least 10–20% of fact packs per concept should come from sources where the original reasoning is already present in human-written form (textbook cases, scientist blog posts, peer review discussions). These passages are not regenerated — they are used with only light editing for anonymization and consistency.

### 2.3. Fact pack template

Fact packs are stored as individual markdown files in `corpus/fact-packs/` with the filename pattern `<concept-number>-<domain>-<scenario-slug>.md` (e.g., `06-biology-protein-correlation-01.md` for an Intellectual Humility scenario about protein correlation from biology). Each fact pack file has YAML frontmatter for structured metadata and markdown body for the substrate and ambiguity content.

**Template:**

```markdown
---
fact_pack_id: <concept-number>-<domain>-<scenario-slug>
target_concept: <concept-number>  # 1–15 from concepts.md
target_concept_name: <full name>  # e.g., "Intellectual Humility"
target_sub_facet: <sub-facet name>  # e.g., "data skepticism"
domain: <one of the 8 quota-managed domains>
source_type: <curated-synthetic | human-anchor>
source_reference: <citation or URL if human-anchor; "internal scenario design" otherwise>
anonymized: true  # must always be true
sanitized: <true | false>  # set to true only after sanitization pass is completed
created_date: YYYY-MM-DD
---

## Scenario title

<One-line descriptor, anonymized. No real names, no specific dates, no identifying institutional details.>

## Factual substrate

<3–6 bullet points stating the key observations, data points, and methodological context that must remain INVARIANT across all three versions of the triplet (neutral, virtuous, non-virtuous). These are the facts the generator is not allowed to change during rewrites.>

- Fact 1 (e.g., "Study of 47 participants with condition X showed measurement Y elevated in 39 of them.")
- Fact 2
- Fact 3

## Known ambiguity

<1–2 bullet points describing the genuine uncertainty or alternative interpretations that exist in the scenario. This is the space where the virtue can manifest — a virtuous reasoner engages with the ambiguity; a non-virtuous reasoner does not.>

- Ambiguity 1 (e.g., "The 8 participants with the opposite pattern could be a statistical outlier, a distinct subgroup, or evidence of measurement error.")
- Ambiguity 2

## Conclusion space

<2–4 plausible conclusions the reasoner could reach. At least one should be consistent with genuinely careful reasoning. At least one should be consistent with an excess-failure (over-application of the disposition) or deficiency-failure (under-application). Label each candidate conclusion with which virtuous/failure pattern it fits.>

- Conclusion A (virtuous-compatible): <description>
- Conclusion B (excess-failure-compatible): <description>
- Conclusion C (deficiency-failure-compatible): <description>
- Conclusion D (optional — another plausible ending, e.g. correct-but-reached-through-wrong-reasoning to support F30/F66 mitigation): <description>

## Notes for generator

<Optional 1–3 sentences noting anything the generator should know about this scenario — e.g., "The unexpected subgroup pattern is the central feature; any rewrite that dismisses it falls into the deficiency-failure category." This is the prompt-style guidance that will be passed to the generator alongside the above substrate.>
```

**Why this structure:**

- **YAML frontmatter** gives us machine-readable metadata for later filtering, quota enforcement, and sanitization status tracking. A simple script can scan `corpus/fact-packs/` and report coverage by concept, domain, sub-facet, and source type.
- **Factual substrate as an explicit invariant** operationalizes F19's minimal-edit principle at the data level: the generator is told which facts cannot change across the triplet, so contrastive rewrites are forced to change disposition rather than content.
- **Known ambiguity as a required field** ensures every scenario has an anchor point where the virtue can bite. Without genuine ambiguity, there is no room for the reasoner to be humble (or arrogant, or servile); the concept becomes unobservable in text.
- **Conclusion space with labels** makes the golden-mean rotation (F59) concrete at the fact-pack level rather than requiring the generator to decide on the fly. A pack-level commitment to "this conclusion is the excess failure" is easier to verify than asking the generator post-hoc whether its non-virtuous rewrite captured excess or deficiency.
- **Notes for generator field** is the place to capture scenario-specific nuances that don't fit the structured sections — this is where the curator communicates the intent of the fact pack to the generation pipeline.

### 2.4. Sanitization checklist

Every fact pack — whether curated-synthetic or drawn from a human-written anchor source — must pass the sanitization checklist before its `sanitized` frontmatter flag is set to `true` and it becomes eligible for triplet generation. The purpose is to prevent prompt-injection artifacts, instruction-like content, and external-source contamination from leaking into the corpus (per F5).

**Checklist — every item must pass before sanitization is marked complete:**

1. **No directives addressed to a reader or model.** Scan for second-person imperatives ("you should," "consider," "note that," "remember to"), first-person instructions that sound like prompts ("let me," "I will now"), and sentences ending with commands ("… then do X"). These often leak from source material when a curator copies from a paper's discussion section or a blog post's conclusion. Replace directive sentences with declarative restatements of the same content, or remove them if they are not load-bearing on the substrate.

2. **No system-style markers.** Scan for: system prompt fragments ("system:", "user:", "assistant:", chat-template role tags), tool-use notation ("<function_call>", "```tool"), API formatting ("role: system"), and markdown structures that mimic prompt templates (numbered "step 1 / step 2 / …" instruction lists). Any match is a rejection — regenerate the fact pack or pull from a cleaner source.

3. **No embedded URLs or citations that could be fetched.** The generator must not receive URLs in the fact pack, because it might dereference them (if it has tools) or hallucinate their content (if it does not). Strip all URLs from the factual substrate. If a citation is essential, replace it with a generic descriptor ("a 2019 randomized trial") rather than a linked reference.

4. **No identifying names, institutions, or dates.** Scan for proper nouns matching the patterns: researcher names (Title Case followed by a surname), institution names (e.g., "University of X," "Y Medical Center"), journal names, specific years (1990–2026), specific countries or cities when they are not load-bearing on the science. Replace with anonymized equivalents: "a team of researchers," "a major research institution," "a peer-reviewed journal," "about a decade ago," "in one large industrialized country." The goal is to keep the factual substrate intact while removing identifying details that would let a reader (or the generator) recognize the source.

5. **No emotionally-loaded framing that biases the reasoning.** Scan for sentences that editorialize the scenario ("shockingly," "remarkably," "the conclusion was obvious," "as any competent scientist would see"). These push the generator toward a specific disposition regardless of which triplet version is being written. Replace with neutral descriptions.

6. **No meta-commentary about the scenario's purpose.** The fact pack is a substrate, not a teaching example. Remove any sentences that explain what the scenario is *supposed to illustrate* ("this case shows the importance of …," "this is a classic example of …"). Such framing contaminates the generator by cueing it toward a specific interpretation that our golden-mean rotation (F59) depends on the generator NOT committing to in advance.

7. **No hidden instructions or Unicode tricks.** Scan for: zero-width characters, unusual Unicode categories, HTML comments (`<!-- ... -->`), CSS-style content that might render as instructions, and any text with abnormal character frequencies that might indicate steganographic prompt injection. This is a lower-probability but higher-severity check.

8. **Factual substrate is complete and self-contained.** After removing all of the above, verify that the remaining fact pack still contains enough information to reason about the scenario. If sanitization has stripped so much that the substrate is now too thin — e.g., the ambiguity bullet no longer makes sense because its context was in a removed sentence — the fact pack is rejected and the curator must rebuild it from the source.

**Sanitization workflow:**

- Sanitization is a two-pass process. The curator does a first pass, marks the fact pack `sanitized: true` in the frontmatter, and commits it. A second reviewer (another human, or a different LLM) then does an independent pass on the same fact pack. If the reviewer flags anything, the fact pack goes back for rework.
- Curated-synthetic fact packs (where the factual substrate was written by the curator) typically pass the checklist on the first attempt because no external text was imported. Human-anchor fact packs (imported from papers, blog posts, textbooks) are where most checklist failures occur.
- When a fact pack fails checklist items 1, 2, 5, or 6, the simplest fix is usually to rewrite the offending sentences in the curator's own neutral voice. Items 3 and 4 are mechanical substitutions. Items 7 and 8 are rarer but require full regeneration of the fact pack.

**What NOT to sanitize:**

- Technical vocabulary that might look complex but is load-bearing on the science (species names, chemical formulas, statistical terms).
- Uncertainty language in the ambiguity section ("may," "might," "is unclear"). This is the whole point of the ambiguity field and must be preserved.
- Specific numbers and measurements in the factual substrate. These are the invariants the generator is required to preserve across the triplet.

### 2.5. Curation workflow

Fact pack curation is a structured pipeline with three roles (all of which may be played by the same person during the manual-first phase, or split once automation begins):

**Role 1 — Curator.** Identifies a source scenario (real research, textbook example, blog post, or original scenario design), drafts the fact pack in the §2.3 template, and commits it to `corpus/fact-packs/` with `sanitized: false`. The curator is responsible for:
- Scenario selection consistent with the active concept's target sub-facet.
- Domain assignment consistent with the active quota (see §3).
- Filling in the factual substrate, known ambiguity, and conclusion space with explicit labels.
- Running the §2.4 sanitization checklist against the draft and flipping `sanitized: true` only when all 8 items pass on first pass.

**Role 2 — Reviewer.** Independently runs the §2.4 checklist against the curator's output and spot-checks the substrate-ambiguity-conclusion structure for coherence. The reviewer is explicitly not the curator — independent eyes are required. Reviewer decisions:
- *Accept* — reviewer signs off, fact pack is eligible for §4 generation pipeline.
- *Return for minor revision* — reviewer flags specific checklist items or structural problems with line-level comments; curator revises and resubmits.
- *Reject* — reviewer determines the underlying scenario cannot be salvaged within the current template; curator starts over from a different source.

**Role 3 — Triplet generator operator.** When a fact pack is accepted, the operator feeds it to the generation pipeline (§4) and captures the three output passages. The operator is a distinct role from curator and reviewer because the generation step is where external verification (§4.5) runs, and keeping roles separate prevents self-confirmation bias in the evaluation chain.

**Storage layout:**

```
corpus/
├── fact-packs/
│   ├── 01-physics-scenario-01.md
│   ├── 01-physics-scenario-02.md
│   ├── 06-biology-protein-correlation-01.md
│   └── ...
├── triplets/
│   ├── 01-physics-scenario-01/
│   │   ├── neutral.md
│   │   ├── virtuous.md
│   │   └── non-virtuous.md
│   └── ...
└── review-logs/
    └── <fact-pack-id>.log  (reviewer + operator comments, timestamps)
```

Each fact pack has a corresponding triplet directory once generation runs, and a review log that records every decision made about the pack from curation through extraction. Review logs are append-only and serve as the audit trail for corpus construction.

**Commit discipline:** Fact packs, triplets, and review logs are version-controlled alongside this document. A fact pack that has been generated into a triplet is *frozen* — further edits to the fact pack require invalidating the corresponding triplet and regenerating. This prevents silent drift between fact packs and the corpus that was extracted from them.

**Workflow during the manual-first phase:** A single researcher plays all three roles but separates them temporally (curate one day, review the next, operate the generator the day after) to preserve independence. A checklist item in the review log notes which role the researcher is currently wearing, and a 24-hour minimum delay between roles is a soft rule to reduce bias.

### 2.6. Human-anchor percentage

Per F71, 100% LLM-generated fact packs risk mode collapse and reduced lexical/syntactic/semantic diversity. The mitigation is mixing in human-written anchor passages from real sources.

**Target ratio: 15% human-anchor fact packs per concept.**

Rationale for 15%:

- F71 and the synthetic-data literature show that even a modest fraction of human-written content substantially reduces collapse risk. The literature does not give a precise threshold, but values in the 10–30% range are typical.
- Lower bound (10%) feels insufficient for small per-concept corpus sizes. For a 50-triplet pilot concept, 10% is only 5 human-anchor fact packs — not enough to noticeably diversify.
- Upper bound (30%) would require extensive source curation (finding real scenarios that cleanly match each concept's target sub-facet), which is expensive for a manual-first phase.
- 15% is the sweet spot: for a 50-triplet pilot, that's 7–8 human-anchor fact packs, enough to provide structural diversity without dominating the curation budget. The remaining 42–43 fact packs are curated-synthetic (scenarios the curator writes themselves, not LLM-generated, but following the same §2.3 template).

**Important clarification:** "Human-anchor" means the *factual substrate* comes from a human-written source (after sanitization). The triplet rewrites on top of that substrate still use the §4 generation pipeline. So the distinction between human-anchor and curated-synthetic is at the fact-pack level, not the triplet level — all triplets are generated via the same §4 pipeline regardless of where the fact pack originated.

**Rotation strategy:** For the pilot concept, human-anchor fact packs are distributed across the 8 domains, not concentrated in one domain. This prevents the human-anchor fraction from becoming a second form of topic concentration. Practical rule: at least 1 human-anchor fact pack per domain where the concept has any triplets, with additional anchors allocated by coin flip if the budget allows more than 8 anchors.

**Deferred for non-pilot concepts:** Once the pilot calibrates the overall corpus size (per F34), the 15% anchor ratio applies to each non-pilot concept as well. If a future finding changes this target, it will be recorded as a new §2.6 note rather than editing this value silently.

**§2 status: complete.** All fact-pack TODOs from the original §2.3 list are now resolved. The fact pack template, sanitization checklist, curation workflow, and human-anchor policy are all specified. Downstream sections (§3 domain quotas, §4 generation pipeline) can now reference fact packs as a concrete, well-defined input.

## 3. Domain diversity quotas

Per F4 and F38, random sampling from a generative model reproduces the generator's training-data biases and concentrates on CS, medicine, and popular physics. Explicit domain quotas are the mitigation.

### 3.1. Target domain list

At least 8 domains per concept, with rotation. Proposed list (subject to refinement in §3.3):

1. Physics (experimental, not theoretical)
2. Biology (cellular, organismal, or ecological)
3. Medicine / clinical epidemiology
4. Economics (microeconomic or behavioral, not macro)
5. Psychology (experimental)
6. Chemistry (synthetic or analytical)
7. Engineering (mechanical, electrical, or structural — not CS)
8. Earth sciences (geology, climate, oceanography)

### 3.2. Quota constraint

No single domain may account for more than **~25%** of the triplets for any single concept. This constraint is enforced per concept, not across the corpus — the total corpus will naturally be balanced if each concept is individually balanced.

### 3.3. Final domain list

The working list from §3.1 is the final list: **8 domains.**

1. Physics (experimental)
2. Biology (cellular, organismal, or ecological)
3. Medicine / clinical epidemiology
4. Economics (microeconomic or behavioral)
5. Psychology (experimental)
6. Chemistry (synthetic or analytical)
7. Engineering (mechanical, electrical, or structural)
8. Earth sciences (geology, climate, oceanography)

**Deliberately excluded** (with reasoning):

- **Mathematics / pure logic.** Mathematical reasoning is structurally different from empirical reasoning — there is no "data" to be skeptical about, no "confounders" in the sense used in §4. Several of our concepts (Causal Reasoning, Quantitative Groundedness, Evidence Grounding) would not have a natural substrate in a math scenario. Including mathematics would produce fact packs where the target concept is unobservable or artificially shoehorned.
- **Computer science / ML.** Excluded because of F71 generator bias — LLM training data is saturated with CS/ML reasoning, and including CS scenarios would push the generator further into its mode-collapsed default distribution. CS reasoning can be approximated by the engineering domain for scenarios involving systems, or by the statistics-of-experiments aspects of psychology and medicine.
- **History of science / philosophy of science.** These are meta-domains (reasoning *about* science rather than *within* science). Our concepts target reasoning *within* a scientific scenario, so using a philosophy-of-science passage as substrate creates a double-level problem: the reasoner is both doing science and talking about doing science. Keep the taxonomy first-order.

This 8-domain list is a working default. If later cycles reveal that one domain produces consistently low-quality fact packs, it can be replaced — but replacements should preserve the 8-count and maintain coverage of experimental empirical disciplines.

### 3.4. Quota rotation mechanism

Domain assignment during fact-pack curation uses a **round-robin queue** per concept, not random sampling. Rationale: random sampling with a 25% ceiling requires rejection-sampling (discard if the ceiling would be exceeded), which is inefficient and can produce skewed counts near the ceiling. A round-robin queue guarantees balance by construction.

**Procedure for the pilot concept (50–60 triplets):**

1. Build a queue of domain assignments in advance by cycling through the 8 domains. For 50 triplets: the first 48 assignments are 6 per domain (8 × 6 = 48), and the remaining 2 assignments are filled by two domains chosen by coin flip. Result: 6 domains get 6 triplets, 2 domains get 7 triplets, no domain exceeds 7/50 = 14% (well below the 25% ceiling).
2. The curator works through the queue in order, finding a scenario for each queued domain assignment. If the curator cannot find a suitable scenario for a given slot, they swap with the next available slot and flag the original slot for later retry.
3. Human-anchor fact packs (§2.6) are distributed across the queue proportionally: 7–8 anchors spread across 7–8 domain slots (at least one per domain that has any triplets).

**Procedure for non-pilot concepts (once pilot calibrates corpus size):**

- Use the same round-robin approach with the size adjusted to whatever the calibrated per-concept budget is. If a concept needs fewer than 8 triplets, assign one per domain and stop — do not repeat domains until at least one triplet exists per domain.

**Why round-robin rather than random:**

- Guarantees per-concept balance at construction time.
- Makes quota violations impossible by design.
- Produces clean reporting (6-6-6-6-6-6-7-7 rather than 4-3-12-8-2-5-11-5).
- Survives partial corpus generation — if we stop early, the partial corpus is still balanced.

### 3.5. Multi-domain scenarios

Some scenarios span multiple domains — for example, a clinical trial of a drug where the reasoning involves both pharmacology (chemistry) and statistical methodology (not a first-class domain but adjacent to medicine and psychology). The handling rule:

**Assign the scenario to its *primary* domain — the domain whose subject-matter expertise would be needed to do the research in the first place.**

- A drug trial: primary domain is medicine (the research question is clinical), even if the statistics would be at home in psychology.
- An ecology study using chemistry to measure pollutants: primary domain is biology (the question is about organisms/ecosystems), even though the method is analytical chemistry.
- A physics experiment that requires engineering instrumentation: primary domain is physics.
- An economic model validated with psychology-experiment data: primary domain is economics if the question is about market behavior, psychology if the question is about cognition.

**When the primary domain is ambiguous:**

- The curator picks one and notes the secondary domain(s) in the fact pack's `notes for generator` field. This keeps the quota count clean (one scenario = one domain count) while preserving the multi-domain context for the generator.
- Cross-disciplinary scenarios should not dominate the corpus. As a soft rule, no more than ~20% of triplets per concept should be primary-domain-ambiguous. If a concept's corpus ends up heavy on cross-disciplinary scenarios, the curator should rebalance with more single-domain scenarios.

**§3 status: complete.** Domain list finalized (8), rotation mechanism specified (round-robin queue per concept), multi-domain handling rule specified (assign primary domain + note secondary in generator notes). Downstream sections can now treat domain as a simple single-valued field per fact pack.

## 4. Generation pipeline — neutral baseline, virtuous, non-virtuous

**(Path B assumption per F73: the passages produced in this section are pre-written corpus elements that will later be used as prompts for Phase 4 generation-based extraction. Under Path C, this entire section would be restructured.)**

### 4.1. Order of generation (per F6, F19)

For each fact pack, generate the triplet in this order:

1. **Neutral baseline first.** A passage depicting the reasoner working through the fact pack's scenario without strongly exhibiting the target virtue or its failure modes. The neutral baseline is the common ancestor from which the other two versions are derived.
2. **Virtuous rewrite second.** A minimal edit of the neutral baseline that makes the target virtue clearly present. Minimal edit means: preserve topic, claims, factual substrate, passage length (within ±10%), and vocabulary register; change only the disposition.
3. **Non-virtuous rewrite third.** A minimal edit of the neutral baseline that depicts one of the two failure modes (excess or deficiency) per the golden-mean design principle. The *same* neutral baseline is used as the starting point, not the virtuous rewrite.

This ordering is deliberate: generating both rewrites from a common neutral ancestor (rather than rewriting virtuous into non-virtuous or vice versa) ensures that the two rewrites are equidistant perturbations from a common point, which produces cleaner difference-of-means geometry.

### 4.2. Minimal-edit principle (per F19)

The rewrite prompts must explicitly instruct the generator to:

- Preserve all factual claims and specific numbers from the neutral baseline.
- Preserve the structural shape of the reasoning (number of inferential steps, order of considerations).
- Preserve the overall length (within ±10% in token count).
- Preserve vocabulary register (formal/informal, technical level).
- Change *only* the target disposition — how the reasoner handles uncertainty, how confidently they state claims, how they weigh evidence, etc. — whatever the concept-specific behavior is.

### 4.3. Golden-mean rotation (per F59, F62)

**Critical constraint:** non-virtuous rewrites must rotate between excess and deficiency failure modes across the corpus for each concept. If all non-virtuous passages for Intellectual Humility depict arrogance (excess), the extracted vector encodes humility-vs-arrogance rather than true humility. Some passages must depict servility (deficiency) to anchor the middle from both sides.

Target split: approximately 50/50 excess vs. deficiency non-virtuous passages per concept, with the exact ratio adjusted per concept based on which failure mode is more textually visible. See findings.md F59 for the per-concept excess/deficiency table.

### 4.4. Correctness-confound mitigation (per F30, F66)

Approximately 20–30% of virtuous passages per concept should depict the virtuous reasoner reaching an *incorrect* final conclusion despite reasoning well. By symmetry, approximately 20–30% of non-virtuous passages should depict the failure-mode reasoner stumbling into a correct final conclusion. This breaks the spurious correlation between virtue and correctness at the corpus level.

**TODO:** The exact ratios (20%? 25%? 30%?) should be specified based on any further empirical grounding found in later cycles.

### 4.5. Generator model and verification (per F71)

**External verification is mandatory.** The corpus generator cannot verify its own output quality due to the bias feedback loop documented in F71. Every generated triplet must be verified by one of:

- A different generator model (different family, ideally).
- Human review.
- Ideally both.

No triplet may enter the extraction corpus without external verification.

### 4.6. Generation prompt templates

The three prompts below are the concrete templates used for neutral, virtuous, and non-virtuous generation. Substitution points are marked with `{{FIELD_NAME}}`. All three prompts reference the same fact pack (§2.3 template), so the curator pulls the fact-pack fields once and substitutes them into all three prompts for a given triplet.

**Target passage length across all three prompts:** 250–350 tokens (~180–260 words). Chosen to be long enough for multiple reasoning moves to manifest (per F1 on needing the concept to show across several sentences) but short enough to keep topic noise bounded and stay within the generator's comfortable coherence window (F69 on long-generation decay).

**Common prompt preamble (shared by all three):**

```
You are helping build a research dataset for a study of reasoning
behaviors in scientific contexts. Your job is to write a short
reasoning monologue — a passage where a researcher thinks through a
specific scenario.

The scenario, the facts, and the uncertainties are provided below and
are INVARIANT. You must preserve every numerical value, every specific
claim, and the structural shape of the reasoning. You are writing the
researcher's inner reasoning voice, not changing what they are reasoning
about.

Target length: 250–350 tokens. Vocabulary: formal but not stilted — the
register of a working scientist explaining their thinking, not a
textbook or a press release.

SCENARIO:
{{scenario_title}}

FACTUAL SUBSTRATE (must appear in the passage, in substance if not in
exact wording):
{{factual_substrate}}

KNOWN AMBIGUITY (must be acknowledged or engaged with in the passage):
{{known_ambiguity}}

CONCLUSION SPACE:
{{conclusion_space}}
```

**Neutral baseline prompt (generated first):**

```
{{common_preamble}}

YOUR TASK — NEUTRAL BASELINE VERSION:

Write the researcher's reasoning about this scenario in a way that is
calm and workmanlike. The researcher acknowledges the ambiguity but
does not dwell on it. They reach one of the plausible conclusions from
the conclusion space — pick whichever feels most natural for a
competent-but-unremarkable researcher.

IMPORTANT:
- Do not make the researcher visibly humble, arrogant, curious, rigid,
  or any other strongly-marked disposition. The neutral baseline is
  the "middle of the road" version — professional, adequate, nothing
  more.
- Do not use language that signals any particular epistemic virtue or
  its opposite. No "I wonder," no "I am certain," no "carefully
  considering," no "obviously." Just direct reasoning from the facts.
- Preserve every specific number and claim from the factual substrate.

Write only the reasoning monologue. Do not include any framing,
preamble, or labels. Output should be the passage itself.
```

**Virtuous rewrite prompt (generated second, using the neutral baseline as input):**

```
{{common_preamble}}

NEUTRAL BASELINE (the starting point for your rewrite):
{{neutral_baseline_passage}}

YOUR TASK — VIRTUOUS REWRITE:

Rewrite the neutral baseline above so that the reasoner clearly exhibits
{{target_concept_name}}, specifically the sub-facet "{{target_sub_facet}}".

The target disposition, in behavioral terms:
{{concept_definition_from_concepts_md}}

MINIMAL-EDIT CONSTRAINTS — preserve from the baseline:
- All specific numbers, measurements, and factual claims.
- The overall structural shape of the reasoning (number of inferential
  steps, rough order of considerations).
- Passage length within ±10% of the neutral baseline's token count.
- Vocabulary register (formal but not stilted, the same as the baseline).
- The specific scenario details — no introducing new facts or removing
  existing ones.

WHAT TO CHANGE:
- How the reasoner handles the known ambiguity (expand and engage with
  it in the specific way the target disposition requires).
- The confidence markers the reasoner uses on their conclusions (match
  them to the strength of the evidence in whatever way the target
  disposition requires).
- The specific phrasing of the reasoning steps — but only in service of
  the disposition change, not for stylistic variation.

IMPORTANT — the reasoner may or may not reach the same final conclusion
as the baseline. Sometimes virtuous reasoning changes the conclusion;
sometimes it reaches the same conclusion with different confidence. Let
the disposition drive the conclusion, not the other way around.

{{correctness_confound_instruction}}  # Populated per §4.4 — see below.

Write only the rewritten reasoning monologue. Do not include any
framing, labels, or meta-commentary.
```

**Non-virtuous rewrite prompt (generated third, using the neutral baseline as input):**

```
{{common_preamble}}

NEUTRAL BASELINE (the starting point for your rewrite):
{{neutral_baseline_passage}}

YOUR TASK — NON-VIRTUOUS REWRITE:

Rewrite the neutral baseline above so that the reasoner exhibits a
FAILURE MODE of {{target_concept_name}}. For this specific triplet,
the failure mode is {{failure_mode_type}}, which means the reasoner
{{failure_mode_description}}.

Examples of {{failure_mode_type}} for this concept:
{{failure_mode_examples}}

MINIMAL-EDIT CONSTRAINTS — preserve from the baseline:
- All specific numbers, measurements, and factual claims.
- The overall structural shape of the reasoning (same number of
  inferential steps as the baseline).
- Passage length within ±10% of the neutral baseline's token count.
- Vocabulary register.

WHAT TO CHANGE:
- The reasoner's handling of the ambiguity — in the direction of the
  failure mode, not toward the virtue and not toward the opposite
  failure mode.
- The confidence markers the reasoner uses on their conclusions —
  again, reflecting the specific failure mode, not its opposite.
- Only the phrasing changes needed to convey the failure mode; no
  stylistic variation for its own sake.

IMPORTANT — the reasoner may or may not reach the same final conclusion
as the baseline. Let the failure mode drive the reasoning, and the
conclusion follows.

{{correctness_confound_instruction}}  # Populated per §4.4 — see below.

Write only the rewritten reasoning monologue. Do not include any
framing, labels, or meta-commentary.
```

**Correctness-confound instruction (inserted into virtuous or non-virtuous prompts per the per-triplet rotation from §4.4):**

For ~20–30% of triplets, override the "reach the natural conclusion" default with one of:

- *For a virtuous-but-wrong triplet:* "IMPORTANT: For this triplet, the virtuous reasoner should reach an INCORRECT conclusion despite reasoning well — they consider the ambiguity carefully, match their confidence appropriately, but still land on a conclusion that is factually wrong. This is rare but important for training — virtue does not guarantee correctness."
- *For a non-virtuous-but-right triplet:* "IMPORTANT: For this triplet, the non-virtuous reasoner should stumble into the CORRECT conclusion despite reasoning poorly. Their failure mode is clearly present, but the answer they land on happens to be right. This is a lucky guess, not a sign of good reasoning."

These overrides are applied by the curator at queue-construction time (during §3.4 rotation planning), not decided by the generator. The rotation is deliberate and balanced: approximately 1 in 4 to 1 in 5 virtuous triplets get the wrong-conclusion override, with the same rate for non-virtuous-but-right. The curator marks the override in the fact pack's `notes for generator` field before generation runs.

### 4.7. Generator and verifier model identities

**Primary generator:** Claude Opus 4.6 via the Anthropic API. Rationale:

- Sonnet 4.5 was used to generate Anthropic's emotion-paper corpus (F1), which establishes that a frontier Claude model is capable of producing high-quality contrastive scientific-reasoning passages at the length and register we need.
- Opus is preferred over Sonnet for Phronesis generation because the contrastive rewrite task requires tight adherence to minimal-edit constraints (per F19), and Opus's instruction-following is reported to be more reliable on multi-constraint generation tasks.
- Version pinning: use `claude-opus-4-6` with 1M-context variant explicitly disabled if not needed — long context is not required for our short passages and introduces cost and variance.
- Temperature: **0.7** for neutral baselines (moderate creativity to avoid mode-collapsed generic scenarios), **0.4** for both rewrite prompts (lower creativity to enforce the minimal-edit constraint).
- Max tokens: 450 (gives headroom above the 350-token target without allowing runaway generations).

**Verifier model (external verification per F71):** A *different* model family is mandatory to break the self-verification loop that F71 warns about. Primary choice: **GPT-5** via the OpenAI API, with **Gemini 3 Pro** as a backup if GPT-5 is unavailable. Rationale:

- Using a different family avoids the knowledge-collapse feedback loop where the generator and verifier share blind spots from common training-data patterns.
- GPT-5 and Gemini 3 have sufficient reasoning capability to judge contrastive-pair quality against a rubric, which is the task we need.
- Neither is the same model being probed in Phase 4, which eliminates any risk of the verifier's preferences accidentally biasing the extracted vectors.

**Fallback during local development:** If API access to GPT-5 or Gemini is unavailable during the manual-first phase, the human reviewer (per §2.5 Role 2) may perform verification manually instead. An automated verifier becomes mandatory only when scaling beyond manual-first.

### 4.8. Verification protocol

For each generated triplet (neutral + virtuous + non-virtuous), the verifier performs four checks before the triplet is accepted into the corpus:

1. **Factual invariance check.** The verifier is given the three passages plus the fact pack's `factual_substrate` and asked: "Does every numerical value and specific claim from the substrate appear, in substance, in all three passages? Flag any passage that drops, contradicts, or fabricates facts."

2. **Length and register check.** The verifier is given the three passages and asked: "Are all three passages within ±10% of each other in token count? Do they share the same vocabulary register (formal-but-not-stilted)? Flag any passage that is noticeably shorter, longer, or stylistically different."

3. **Disposition presence check.** The verifier is given the virtuous rewrite and the concept name + sub-facet + definition from concepts.md, and asked: "Does this passage clearly exhibit {{concept}} in the specific form of {{sub_facet}}, without becoming a caricature? Rate on a 1–5 scale, with 3 being the minimum acceptable." The same check runs on the non-virtuous rewrite with the specific failure mode (excess or deficiency) as the target.

4. **Injection sanitization spot-check.** The verifier runs an abbreviated version of the §2.4 checklist against each of the three generated passages, looking for any injection artifacts that slipped through despite fact-pack sanitization. Full checklist is overkill at this stage — the verifier specifically checks items 1 (directives), 2 (system-style markers), and 5 (emotionally-loaded framing), since those are the ones most likely to be introduced by the generator itself.

**Verifier output format:** Structured JSON per triplet, with fields for each of the four checks, each containing `pass: bool`, `score: int 1–5` where applicable, and `notes: string` for flagged issues. This is stored in the review log for the corresponding fact pack (per §2.5 storage layout).

**Acceptance criterion:** A triplet enters the corpus only if all four checks pass (pass=true on binary checks, score≥3 on scored checks). If any check fails, the triplet is rejected per §4.9.

### 4.9. Rejection handling

When a triplet fails any verification check, the operator (Role 3 from §2.5) decides the disposition using the following rules:

**Check 1 failure (factual invariance violated):**
- First attempt: regenerate the specific offending passage (neutral, virtuous, or non-virtuous) with a prompt-level reminder that emphasizes the invariant facts. Keep the other two passages if they passed.
- If the second attempt also fails: regenerate all three passages from scratch. The prior attempts are logged but discarded.
- If three full regenerations fail: the fact pack itself is marked `regeneration_failed` and returned to the curator for restructuring (the ambiguity may be too closely tied to the facts to allow a clean minimal-edit contrast).

**Check 2 failure (length/register drift):**
- First attempt: regenerate the drifted passage with a tightened length constraint in the prompt. Usually fixes the issue.
- If second attempt fails: regenerate all three. Same three-strike rule as Check 1.

**Check 3 failure (disposition not clearly present — score < 3):**
- First attempt: regenerate the rewrite (virtuous or non-virtuous) with a stronger definition hint in the prompt, pulling more language from concepts.md.
- If second attempt still scores < 3: mark the rewrite as "weak" and hold the triplet in a separate `corpus/triplets-weak/` directory. These are not used in the primary extraction corpus but are preserved for ablation studies — the question "does extraction improve when weak pairs are removed vs. kept" is informative for future cycles.
- If a particular fact pack produces weak triplets repeatedly across multiple generation attempts, the fact pack is flagged as a bad match for the target concept — the ambiguity in the scenario may not be the kind this concept needs. Return to curator for either re-targeting (try a different concept with the same substrate) or rejection.

**Check 4 failure (injection artifact detected):**
- Regenerate the specific offending passage once. If the injection recurs, regenerate all three (the fact pack itself may have unsanitized content that was missed in §2.4).
- If three regenerations all produce injection-like output: return to curator for re-sanitization of the fact pack from scratch.

**Global rule — three-strikes per triplet, fact-pack flag on repeated failure:** No triplet gets more than three full regenerations. A triplet that fails after three attempts is either held in `corpus/triplets-weak/` (for Check 3 failures) or discarded with the fact pack flagged (for Check 1/2/4 failures). Repeated fact-pack failures across multiple triplets trigger a curator review of whether the fact pack should be restructured or dropped entirely.

**Logging:** Every rejection, regeneration attempt, and final disposition is recorded in the fact pack's review log (per §2.5). The log entry includes: which check failed, the verifier's notes, which passage was regenerated, and the final state of the triplet (accepted, weak, or discarded). This audit trail is the basis for measuring corpus generation yield and identifying systematic failure patterns during the manual-first phase.

**§4 status: complete.** Generation pipeline is now fully specified end-to-end: fact pack → neutral → virtuous → non-virtuous (prompts §4.6), generator and verifier identities (§4.7), verification protocol (§4.8), and rejection handling (§4.9). A curator could begin operating Phase 2 from this document.

## 5. Pilot-only scaling (per F34)

Per F34 (user-resolved, Option 2): the pilot concept (Calibrated Confidence per F11 tier ordering, *possibly* Intellectual Humility per F74 revision pending user review) gets 50–60 triplets — comfortably above the 80-pair published minimum for stable activation vector extraction. The remaining 14 concepts are deferred until pilot calibration reveals the corpus size needed at our model scale.

### 5.1. Pilot concept selection

**Working default: Calibrated Confidence (Concept 9).**

Rationale for Calibrated Confidence as the pilot:

- **F11 highest-likelihood tier.** Calibrated Confidence was placed in the highest-likelihood tier of F11's extraction-difficulty ordering, based on its concrete textual markers (explicit probability language, hedge words, confidence calibration) and its close adjacency to constructs like "truthfulness" that have been successfully extracted in prior CAA work.
- **Direct validation via F47.** Phase 4 validation can use language-level metrics (hedging-word frequency, probability-language usage, confidence-evidence alignment) rather than the ML-technical ECE that F47 specifically warned against. This gives us a clean, measurable success signal for the pilot run.
- **Known failure mode per F44.** F44 flagged that small LLMs default to assertive language regardless of internal confidence, which means our virtuous-calibrated corpus would fight a strong pretraining prior. This is a risk, but it also means the contrast between virtuous and non-virtuous passages should be *sharper* than for concepts where the default is already neutral. Sharper contrast → cleaner extraction.

**Alternative pending user review: Intellectual Humility (Concept 6).**

Per F74, HumbleBench reports that mid-sized models outperform larger peers on humility-oriented robustness, which is an unexpectedly positive signal for our small-model target. If the user confirms the F74 tier adjustment (moving Concept 6 from Medium toward Higher extraction-likelihood), Intellectual Humility becomes a competitive pilot alternative — with the additional advantage that HumbleBench itself becomes a ready-made Phase 4 validation benchmark, reducing the "which benchmark do we use?" question.

**Decision rule:** Begin manual-first corpus construction on Calibrated Confidence using the working default. If the user reviews F74 and confirms the tier adjustment before the pilot corpus is complete, re-evaluate whether to switch pilots. Switching costs approximately one curator's worth of sunk fact-pack curation effort, which is small in the manual-first phase. Switching after the pilot corpus is complete would cost the full 50–60 triplet budget, which is not trivial but also not catastrophic.

**Not a blocker for Phase 3 drafting:** The pilot concept selection affects Phase 2 execution, not the structure of this document. The generation-guidelines.md can be completed and reviewed regardless of which pilot is eventually chosen.

### 5.2. Triplet count for pilot

50–60 triplets → 100–120 directional observations (virtuous-minus-neutral and non-virtuous-minus-neutral from each triplet) → comfortably above the 80 minimum reported in the CAA literature.

### 5.3. Budget for remaining concepts

Deferred. Determined after pilot calibrates the stability threshold at Gemma 4 E4B scale.

## 6. Anti-collapse diversity metrics (per F71)

Before the corpus is handed to Phase 4 extraction, it must pass diversity sanity checks. The purpose is to detect mode collapse and diversity reduction in LLM-generated content *before* the collapse contaminates the extraction step, where it would look like "the concept just doesn't extract cleanly" rather than "the corpus was too narrow."

### 6.1. Metrics (three, run per concept)

**Metric 1 — Type-token ratio (TTR) on content words.** Lowercase each passage, strip stopwords, count unique content-word types divided by total content-word tokens. Compute TTR for each passage, then report the corpus distribution (mean, stdev, 25th/50th/75th percentiles) across the concept's triplets. This captures *vocabulary richness* — whether the generator is falling into a narrow vocabulary for "virtuous scientific reasoning."

**Metric 2 — Distinct-n for n ∈ {2, 3, 4}.** For each concept's corpus (all neutral passages concatenated, all virtuous concatenated, all non-virtuous concatenated — three separate measurements), compute the fraction of unique n-grams over total n-grams. Low distinct-n means the generator is producing repeated phrase patterns across passages, which is the signature of mode collapse. Report distinct-2, distinct-3, distinct-4 for each of the three passage pools per concept.

**Metric 3 — Pairwise semantic similarity spread.** Embed each passage using a standard sentence embedder (default: `all-MiniLM-L6-v2` for speed; fallback: `all-mpnet-base-v2` for higher quality). Within each of the three passage pools (neutral / virtuous / non-virtuous) per concept, compute pairwise cosine similarities between all passage embeddings. Report the mean and standard deviation. Low standard deviation with high mean similarity means passages are semantically clustered — mode collapse. High spread means the generator produced diverse scenarios.

Why three metrics rather than one: TTR catches vocabulary collapse, distinct-n catches phrase-pattern collapse, and semantic similarity catches topic/meaning collapse. A generator can pass any two while failing the third, so all three are required.

### 6.2. Thresholds

Thresholds are set relative to a *natural-text baseline* (see §6.3), not as absolute numbers, because absolute thresholds depend on passage length, vocabulary domain, and embedder choice. The rule is expressed as a percentage drop from baseline:

**Acceptance thresholds per concept:**

- **TTR:** median passage TTR must be ≥ **75%** of the natural-text baseline TTR for passages of comparable length and domain mix. Dropping below 75% indicates vocabulary narrowing.
- **Distinct-2:** must be ≥ **70%** of the natural-text baseline. Distinct-2 is the most sensitive to phrase-pattern collapse.
- **Distinct-3 and distinct-4:** must each be ≥ **80%** of the natural-text baseline. Longer n-grams are more stringent because natural text has much higher distinct-n at n=3,4.
- **Pairwise semantic similarity:** mean within-pool cosine similarity must be ≤ **baseline + 0.10**. That is, generated passages can be slightly more similar to each other than natural-text passages on the same topic (expected, since they share scenario structure), but not by more than 0.10 on a [0, 1] cosine scale.

**Any metric below threshold on any passage pool triggers regeneration** of the passages contributing to the worst end of the distribution. Regeneration uses prompt-level nudges toward more diverse vocabulary, different scenario framings, etc. If regeneration fails to clear the threshold on a second attempt, the issue is escalated to fact-pack-level diversification — the curator adds more varied scenarios.

### 6.3. Comparison baseline — natural-text reference corpus

The natural-text baseline is a small reference corpus of human-written scientific-reasoning passages, assembled once and reused across all concepts. Its purpose is to anchor the thresholds above in real-world measurements rather than arbitrary absolute values.

**Composition of the reference corpus:**

- **50 passages** drawn from sources where scientific reasoning appears naturally in text: textbook case studies, peer-review comments in published debates, scientist blog posts, methods sections of papers (selected for discussion of methodology rather than raw results), and the "discussion" sections of well-cited papers where authors reason about their findings.
- **Domain distribution matching §3.1** — roughly 6–7 passages per domain, so the reference corpus exercises the same topic space our generated corpus will.
- **Length matching** — each reference passage is trimmed or selected to fall within the 250–350 token target range used for our generated passages. Passages outside this range are excluded or excerpted to fit.
- **Sanitized per §2.4** — the reference corpus is treated the same as any other external-source material: names/URLs stripped, no instructional content, no meta-commentary.

**How the baseline is used:**

1. Once assembled, compute TTR, distinct-{2,3,4}, and pairwise similarity on the reference corpus. These numbers are the baseline.
2. Store the baseline in `corpus/diversity-baseline/baseline-metrics.json` alongside a brief description of how it was assembled (source types, length criteria, embedder version).
3. When a concept's generated corpus is checked for diversity, the thresholds in §6.2 are computed as the specified percentage of the stored baseline values, not from scratch.
4. The baseline is **frozen** once established. If it is ever updated (e.g., because the embedder is changed), every existing concept must be re-checked against the new baseline, and the old baseline is archived with a changelog entry.

**Why 50 passages:** Small enough to curate by hand during the manual-first phase, large enough for stable metrics (standard deviations at n=50 are tolerable for the three metrics above), and domain-balanced at 6–7 per domain.

**Curator responsibility:** Assembling the reference corpus is a one-time task that must be completed before the first concept's generated corpus is validated. It is a §2.5 Role 1 (curator) activity and follows the same sanitization pipeline as fact packs.

**§6 status: complete.** Three metrics specified (TTR, distinct-n, pairwise similarity), thresholds set as percentages of a 50-passage natural-text baseline, baseline construction and storage specified. The diversity check can now be operationally run before any extracted vectors are computed.

## 7. Injection sanitization (per F5)

Injection contamination is a two-stage concern in Phronesis: (a) it can enter the corpus *before* generation via unsanitized fact packs, and (b) it can enter *during* generation if the generator model hallucinates instruction-like content in response to ambiguous scenario material. Both stages need defenses.

### 7.1. Pre-generation sanitization

Pre-generation sanitization is handled by **§2.4 (the fact pack sanitization checklist)** and its two-pass workflow from §2.5. That checklist covers all eight injection vectors (directives, system-style markers, URLs, identifying names, emotional framing, meta-commentary, Unicode tricks, substrate completeness) and is the primary defense. This section does not duplicate §2.4 — it exists to address the runtime concerns that §2.4 cannot catch.

### 7.2. Runtime (post-generation) sanitization

Even with a clean fact pack, the generator can introduce injection artifacts in its output. The most common runtime patterns observed in LLM outputs for similar tasks:

- **Accidental meta-commentary.** The generator sometimes opens a rewrite with phrases like "Here is the rewritten passage:" or closes with "I hope this captures the intended disposition." These are framing artifacts that violate the "write only the passage, no framing" instruction in the §4.6 prompt templates. They must be stripped before the passage enters the corpus.
- **Reconstructed system-style markers.** The generator may emit `**Step 1:**`, `**Researcher's reasoning:**`, or similar header-style formatting, turning the passage into a structured document rather than a reasoning monologue. Strip these.
- **Leaked directive language.** Rare but seen: the generator emits "you should consider" or "it is important to note" sentences that read like advice to a reader rather than reasoning by a researcher. These are caught by §4.8 Check 4 (the abbreviated §2.4 spot-check during verification).
- **Bullet-pointed reasoning.** The prompt asks for a reasoning monologue, but the generator sometimes produces bullet lists. Bullet-formatted output is rejected — monologue is mandatory for the extraction method to work correctly (activations should come from contiguous reasoning text, not list items).

### 7.3. Handling when injection is detected

Runtime injection is caught by §4.8 Check 4 (abbreviated §2.4 spot-check as part of the verification protocol). When detected, the handling rules from §4.9 apply:

- **First attempt:** regenerate the specific offending passage with a prompt-level reminder that the output must be a plain reasoning monologue, no framing, no bullet points, no meta-commentary.
- **Second attempt:** regenerate all three passages in the triplet from scratch (the shared generator session may have a persistent artifact).
- **Three-strikes failure:** return to curator for re-sanitization of the fact pack (a subtle unsanitized element may be cueing the generator).

### 7.4. Automatic pre-screening (lightweight filter before verifier runs)

To save verifier API calls, a lightweight regex-based pre-screener runs on every generated passage before it is sent to the verifier. The pre-screener catches the highest-frequency runtime artifacts immediately:

- Opening framing phrases: `^(Here is|Here's|Sure, here|Below is|I'll write|Let me write)`
- Closing framing phrases: `(I hope this|This captures|Let me know)` at the end of the passage
- Header markers: `^\*\*.*\*\*:` at any line start (bolded labels)
- Bullet-only output: passages where every line starts with `-`, `*`, or `1.`
- Role tags: `^(system|user|assistant):` anywhere

A passage that matches any pre-screen pattern is automatically rejected without consuming verifier budget; it goes directly to §4.9 rejection handling as if it had failed Check 4. This is an optimization, not a replacement for the verifier's fuller §2.4 spot-check — the verifier still runs on passages that pass pre-screening.

**§7 status: complete.** Pre-generation sanitization points to §2.4 (no duplication), runtime sanitization lists the four main runtime artifact patterns, rejection handling reuses §4.9, and a lightweight pre-screener is specified to reduce verifier load.

## 8. Worked examples

A fully-worked example triplet is maintained in `examples/humility-example-01.md`. That artifact shows, end to end:

- A concrete fact pack built to the §2.3 template (scenario, factual substrate, known ambiguity, conclusion space with golden-mean labels).
- The neutral baseline passage produced from that fact pack using the §4.6 neutral-baseline prompt.
- The virtuous rewrite produced from the neutral baseline using the §4.6 virtuous rewrite prompt, targeting Intellectual Humility's data-skepticism sub-facet (Medium tier per F11).
- The non-virtuous rewrite produced from the neutral baseline, depicting one specific failure mode (excess or deficiency per §4.3 rotation).
- Commentary on what each version does well and what to watch for.

Curators should read `examples/humility-example-01.md` before attempting their first fact pack to calibrate their sense of what "good enough" looks like at each step of the pipeline. The worked example is not a template to copy — each fact pack must be scenario-specific — but it is the reference point for the structural and stylistic targets this document specifies in the abstract.

**Status of the worked example:** the example file is drafted in a later Phase 3 cycle after `generation-guidelines.md` and `review-rubric.md` are both complete. Until then, curators should work from this document and concepts.md as the primary references.

## 9. Review rubric reference

The detailed review rubric — the per-check scoring criteria, the LLM-as-judge prompt for automated first-pass review, the human spot-check protocol, and the acceptance/rejection thresholds — is specified in `review-rubric.md`.

**Responsibility split between the two documents:**

- `generation-guidelines.md` (this document) specifies *what is generated, by whom, under what constraints, and what happens if generation produces something wrong*. The four verification checks in §4.8 are the high-level interface.
- `review-rubric.md` specifies *how each of the four checks is concretely scored* — the rubric items, the scoring scale anchors, the LLM-as-judge prompt that implements the automated pass, the human spot-check sampling protocol, and the edge cases for each concept.

A curator operating Phase 2 needs both documents open: this one to understand the pipeline and prompts, and `review-rubric.md` to understand exactly how verification scores are assigned.

**Status of the rubric document:** `review-rubric.md` is drafted in the next Phase 3 cycle after this document is TODO-free. Until then, the §4.8 high-level checks are the working definition of verification, and the verifier model (GPT-5 per §4.7) operates from those descriptions plus the concept definitions in concepts.md.

## 10. Blockers and decision points (summary)

Items that were previously blocked on user decisions and their current status:

1. **F73 Path A/B/C decision** (highest priority, STILL PENDING). This document assumes Path B. User confirmation or correction will either (a) leave the document on track under Path B, (b) require a small Phase 4 extraction-methodology note change under Path A, or (c) require rewriting §§3–5 under Path C. **This is the primary blocker for the document being considered "finalized" rather than "draft-complete."**

2. **F74 tier adjustment for Intellectual Humility** (medium priority, STILL PENDING). §5.1 commits to Calibrated Confidence as the pilot working default with Intellectual Humility as the alternative pending user review. Either choice is compatible with the document structure; only which concept's corpus is built first is affected.

3. **Domain list finalization** (§3.3) — **resolved** in cycle 27. 8 domains finalized. Mathematics, CS/ML, and history/philosophy of science explicitly excluded with reasoning documented.

4. **Generator model identity** (§4.7) — **resolved** in cycle 29. Claude Opus 4.6 primary, GPT-5/Gemini 3 as external verifier, manual human review as development fallback. User may override if they want a different generator, but the current choice is defensible per F1 precedent.

5. **Exact numerical thresholds:** **resolved** in various cycles.
   - Correctness-confound ratio: 20–30% per §4.4, applied as per-triplet rotation at curator queue-construction time.
   - Anti-collapse diversity metrics: thresholds expressed as percentages of a 50-passage natural-text baseline per §6.2 (TTR ≥75%, distinct-2 ≥70%, distinct-{3,4} ≥80%, mean similarity ≤baseline+0.10).
   - Human-anchor percentage: 15% per §2.6, distributed across all 8 domains.

**Document status: draft-complete.** All internal TODOs are resolved. The document is operationally sufficient for a curator to begin Phase 2 corpus construction on the pilot concept. User action on F73 and F74 would move the document from "draft-complete" to "finalized," but neither is a blocker for starting corpus work under Path B / Calibrated Confidence defaults.

---

## Document state

- **Created:** Phase 3 cycle 1 (2026-04-09).
- **Structure:** Skeleton with section headers, design decisions from concepts.md/findings.md/project.md already incorporated, and explicit TODOs for sections that need further detail.
- **Next steps:** Subsequent Phase 3 cycles fill in TODOs one at a time. When this document is TODO-free (and F73 is resolved), work moves to `review-rubric.md`. When that is also complete, work moves to `examples/humility-example-01.md`.
- **Length target:** Under 500 lines per Phase 2 skill-creator conventions (current draft is within this limit).
