# Phronesis — Review Rubric (Phase 3 Draft)

Concrete scoring criteria and protocols for verifying generated triplets before they enter the Phase 4 extraction corpus. This document is the operational companion to `generation-guidelines.md` §4.8 (verification protocol) and §4.9 (rejection handling).

**STATUS: DRAFT SKELETON with TODOs.** Initial skeleton drafted autonomously. Sections are stubbed with the design decisions from generation-guidelines.md, findings.md, and concepts.md that already constrain the rubric. TODOs mark content that will be filled in over subsequent cycles.

**Responsibility split with generation-guidelines.md (per that document's §9):**
- `generation-guidelines.md` specifies *what* is generated, *by whom*, *under what constraints*, and *what happens* if generation produces something wrong. The four verification checks in its §4.8 are the high-level interface.
- `review-rubric.md` (this document) specifies *how* each check is concretely scored — the rubric items, scoring scale anchors, LLM-as-judge prompt, human spot-check sampling protocol, and edge cases for each concept.

A curator operating Phase 2 needs both documents open.

---

## 1. Purpose and scope

The review rubric exists to convert the high-level verification checks from `generation-guidelines.md` §4.8 into concrete, reproducible scoring decisions that both an LLM-as-judge and a human spot-checker can apply consistently. Its goals:

- **Reproducibility.** Two independent reviewers (LLM or human) applying this rubric to the same triplet should reach substantially the same accept/reject decision. Where they disagree, the disagreement should be traceable to a specific rubric item rather than to global taste differences (per F72's warning that unresolved subjectivity produces spurious interrater disagreement).
- **Two-axis evaluation** (per F19). Every triplet is scored on *both* style-capture (did the virtuous/non-virtuous rewrite actually exhibit the target disposition?) and content-preservation (did the rewrite preserve the factual substrate, structure, length, and register?). A single global score obscures the failure mode when a passage is great on one axis and terrible on the other.
- **Guardrailed LLM-as-judge** (per F70). LLM-as-judge output is a first-pass filter only; every triplet is eligible for human spot-check, a non-trivial sample is always spot-checked, and disagreement is tracked as a signal about rubric clarity rather than only as error.
- **Concept-aware scoring.** The rubric items are not uniform across concepts — what counts as "clearly exhibits Intellectual Humility" is different from "clearly exhibits Hypothesis Generation." The rubric has a shared skeleton plus concept-specific items pulled from concepts.md.

---

## 2. Rubric architecture

The rubric has three layers:

### 2.1. Layer 1 — Binary invariance checks

These are pass/fail and non-negotiable. A triplet that fails any Layer 1 check is rejected regardless of everything else.

1. **Factual invariance** — every numerical value and specific claim from the fact pack's `factual_substrate` appears in substance in all three passages. Covers generation-guidelines.md §4.8 Check 1.
2. **Length and register invariance** — all three passages within ±10% token count of each other, shared vocabulary register. Covers §4.8 Check 2.
3. **Injection sanitization spot-check** — abbreviated §2.4 checklist passes on all three passages. Covers §4.8 Check 4.
4. **Structural constraint** — all three passages are reasoning monologues (not bullet lists, not structured documents, not dialogues).

Any Layer 1 failure sends the triplet to §4.9 rejection handling in `generation-guidelines.md`.

### 2.2. Layer 2 — Scored quality axes (1–5 scale each)

These are scored independently on both axes per passage. Target: the virtuous and non-virtuous rewrites must score ≥3 on both axes to be accepted.

**Axis A — Style capture.** Does the passage clearly and naturally exhibit the target disposition (virtue or specific failure mode) for this triplet?

**Axis B — Content preservation.** Does the passage preserve the fact pack's factual substrate, the neutral baseline's reasoning structure, and the overall topic without introducing new content or dropping load-bearing elements?

The scale anchors for both axes are specified in §3.

### 2.3. Layer 3 — Concept-specific rubric items

For each concept in concepts.md, the rubric includes 3–5 concept-specific behavioral markers that a passage must exhibit to earn a high Axis A score for that concept. These are pulled from the concept's sub-facets and the golden-mean excess/deficiency table in F59.

Layer 3 items are concept-parameterized — the scorer is given the concept name, the sub-facet name, and the specific failure mode type (excess or deficiency) for that triplet, and the rubric then provides the concept-specific markers.

**RESOLVED 2026-04-29:** §6.1 through §6.15 below contain Layer 3 marker tables for all 15 concepts. The original TODO was overtaken by completion. Per-concept tables are populated; the MVP-active 4 (CC, IH, EG, RT) have additional operational marker guidance in `mvp-virtues.md`.

---

## 3. Scale anchors for Axis A (style capture) and Axis B (content preservation)

### 3.1. Axis A — Style capture anchors

**5 — Exemplary.** The passage clearly and naturally exhibits the target disposition throughout. A reader who did not know the concept name could still identify the disposition from the text. Multiple distinct behavioral markers from the concept's sub-facet list are present and integrated into the reasoning.

**4 — Good.** The target disposition is clearly present and recognizable. At least one strong behavioral marker is present. Minor roughness allowed (e.g., one marker is a bit generic, or the disposition shows in the reasoning but is slightly understated).

**3 — Acceptable.** The disposition is present but not prominent. A reader familiar with the concept can identify it, but a naive reader might miss it. At least one marker is clearly present, though weaker markers may dominate the text.

**2 — Weak.** The disposition is nominally present but surface-level — hedge words without meaningful uncertainty engagement, confidence markers without calibration, etc. The passage reads as a stylistic veneer rather than genuine disposition.

**1 — Absent or wrong.** The disposition is missing, or the passage exhibits a different disposition than the target (e.g., the virtuous rewrite accidentally depicts overconfidence instead of humility).

**Target for acceptance:** ≥3 for both virtuous and non-virtuous rewrites. Score of 2 sends the triplet to `triplets-weak/` per §4.9 Check 3 handling. Score of 1 triggers regeneration.

### 3.2. Axis B — Content preservation anchors

**5 — Perfect.** Every numerical value, every specific claim, and every element of the reasoning structure from the baseline is preserved. No new content introduced, no baseline content dropped. Length within ±5% of baseline. Register identical.

**4 — Strong.** All invariant facts and structure preserved. Minor wording shifts that do not change content. Length within ±10%. Register close.

**3 — Acceptable.** Invariant facts all preserved. Minor structural deviations (e.g., two reasoning steps reordered or lightly merged). Length within ±10%. Register close.

**2 — Degraded.** One invariant fact dropped or reworded in a way that changes its meaning, OR structural deviation that changes the shape of the reasoning, OR length out of ±10% range.

**1 — Broken.** Multiple invariant facts missing or changed, OR the passage is about a different scenario than the fact pack, OR length far outside range (>±20%).

**Target for acceptance:** ≥3 for all three passages (neutral, virtuous, non-virtuous). Any 1 or 2 triggers rejection per §4.9.

---

## 4. LLM-as-judge prompt

The LLM-as-judge (GPT-5 per generation-guidelines.md §4.7) receives a structured prompt and returns structured JSON. The prompt is parameterized by the concept, sub-facet, failure mode type, and the three passages of the triplet. It implements the four verification checks from generation-guidelines.md §4.8 by populating the rubric layers from §2 of this document.

### 4.1. Prompt template

Substitution points are marked with `{{FIELD_NAME}}`. All fields are pulled from the fact pack (per generation-guidelines.md §2.3) or from concepts.md.

```
You are a careful reviewer evaluating whether a generated triplet of
reasoning passages is acceptable for a research corpus on epistemic
virtues. Your job is to apply a rubric and return structured JSON.
Do not output anything other than the JSON.

## Context you need

TARGET CONCEPT: {{target_concept_name}} (Concept #{{target_concept_number}})
SUB-FACET FOR THIS TRIPLET: {{target_sub_facet}}
FAILURE MODE FOR THE NON-VIRTUOUS PASSAGE: {{failure_mode_type}}
  (one of: "excess" — over-applying the disposition, or "deficiency" —
   under-applying it)

CONCEPT DEFINITION (from the project's concept taxonomy):
{{concept_definition}}

WHAT THIS CONCEPT LOOKS LIKE IN TEXT (positive markers):
{{positive_behavioral_markers}}

WHAT THE SPECIFIC FAILURE MODE LOOKS LIKE IN TEXT (for the non-virtuous
passage only):
{{failure_mode_markers}}

CORRECTNESS-CONFOUND STATUS FOR THIS TRIPLET:
{{correctness_confound_note}}
  (one of: "standard" — both rewrites reach sensible conclusions;
   "virtuous-wrong" — the virtuous passage reaches a factually incorrect
   conclusion despite good reasoning; "non-virtuous-right" — the
   non-virtuous passage reaches a correct conclusion despite poor
   reasoning)

## Factual substrate (must be preserved, in substance, across all three
passages)

{{factual_substrate}}

## The three passages to evaluate

NEUTRAL BASELINE:
{{neutral_passage}}

VIRTUOUS REWRITE:
{{virtuous_passage}}

NON-VIRTUOUS REWRITE:
{{non_virtuous_passage}}

## Your task — apply the rubric and return JSON

Score each check below and return a single JSON object exactly matching
the schema after the checks.

### LAYER 1 — Binary invariance checks (pass/fail, non-negotiable)

L1.1 — FACTUAL INVARIANCE: Does every numerical value and specific claim
from the factual substrate appear, in substance, in all three passages?
A passage that drops, contradicts, or fabricates a fact fails this
check. Note: "in substance" means the fact is there even if the wording
differs — you are checking semantic preservation, not literal
repetition. Return `pass: true` only if all three passages preserve the
substrate.

L1.2 — LENGTH & REGISTER: Are all three passages within ±10% of each
other in token count (estimate token count as approximately
words × 1.3)? Do they share the same vocabulary register (formal but
not stilted; the register of a working scientist's inner monologue)?
Return `pass: true` only if all three match on both length and register.

L1.3 — STRUCTURAL: Are all three passages reasoning monologues? A
passage that is a bullet list, a dialogue, a structured document with
headers, or a Q&A format fails this check. Return `pass: true` only if
all three are continuous monologue prose.

L1.4 — INJECTION SANITIZATION SPOT-CHECK: Scan each passage for (a)
directive language addressed to a reader ("you should," "consider
that"), (b) framing phrases ("Here is," "I will now"), (c)
system-style markers (role tags, bold headers, code fences), (d)
emotionally-loaded editorializing ("shockingly," "obviously," "any
competent scientist"). Return `pass: true` only if all three passages
are clean on all four sub-checks.

### LAYER 2 — Scored quality axes (1–5, per passage)

For both the VIRTUOUS and NON-VIRTUOUS passages, score two axes:

AXIS A — STYLE CAPTURE:
  5 = Exemplary: the target disposition is clearly present throughout;
      multiple distinct behavioral markers are integrated naturally.
  4 = Good: clearly present and recognizable; at least one strong
      marker; minor roughness allowed.
  3 = Acceptable: present but not prominent; a reader familiar with
      the concept can identify it.
  2 = Weak: nominally present but surface-level — hedge words without
      meaningful engagement, confidence markers without calibration.
  1 = Absent or wrong disposition entirely.

For the VIRTUOUS passage, score against the POSITIVE behavioral markers
above.
For the NON-VIRTUOUS passage, score against the FAILURE MODE markers
above.

AXIS B — CONTENT PRESERVATION (relative to the neutral baseline):
  5 = Perfect: every fact, claim, and reasoning step from the baseline
      preserved; length within ±5%; register identical.
  4 = Strong: all invariant facts/structure preserved; minor wording
      shifts; length within ±10%.
  3 = Acceptable: invariant facts preserved; minor structural deviations
      (one or two steps reordered or merged); length within ±10%.
  2 = Degraded: one invariant fact dropped or changed in meaning, OR
      structural shape changed, OR length outside ±10%.
  1 = Broken: multiple facts missing/changed, OR passage is about a
      different scenario, OR length far outside range.

### LAYER 3 — Concept-specific red flags

Note any concept-specific red flags that would lower an Axis A score.
These are listed in the positive and failure-mode markers above; if any
are present and the passage still scored highly, flag them in the
`notes` field.

### CORRECTNESS-CONFOUND CHECK

If the correctness-confound status is "virtuous-wrong" or
"non-virtuous-right", verify that the assigned passage actually matches:
— For "virtuous-wrong": the virtuous passage reasons carefully but
  reaches a conclusion that is factually wrong given the substrate.
— For "non-virtuous-right": the non-virtuous passage exhibits the
  failure mode but happens to reach a correct conclusion.
If the override was assigned but the passage does not match it, flag
`correctness_confound_mismatch: true` in the JSON.

## Output schema

Return exactly this JSON object, with no surrounding text:

{
  "layer1": {
    "factual_invariance":     { "pass": bool, "notes": str },
    "length_and_register":    { "pass": bool, "notes": str },
    "structural":             { "pass": bool, "notes": str },
    "injection_sanitization": { "pass": bool, "notes": str }
  },
  "layer2": {
    "virtuous": {
      "axis_a_style_capture":       { "score": int, "notes": str },
      "axis_b_content_preservation": { "score": int, "notes": str }
    },
    "non_virtuous": {
      "axis_a_style_capture":       { "score": int, "notes": str },
      "axis_b_content_preservation": { "score": int, "notes": str }
    },
    "neutral": {
      "axis_b_content_preservation": { "score": int, "notes": str }
    }
  },
  "correctness_confound_mismatch": bool,
  "concept_specific_flags": [str, ...],
  "overall_recommendation": "accept" | "regenerate_passage" | "regenerate_triplet" | "weak_triplet" | "fact_pack_review",
  "recommendation_reason": str
}

Rules for overall_recommendation:
— "accept": all Layer 1 checks pass AND all Layer 2 Axis A scores ≥ 3
  AND all Layer 2 Axis B scores ≥ 3 AND no correctness_confound_mismatch.
— "regenerate_passage": exactly one passage is the problem; one Layer 1
  fails or one Axis A/B score is below 3. Note which passage in the
  reason.
— "regenerate_triplet": multiple passages have issues, OR the issue is
  one that cannot be fixed by regenerating a single passage.
— "weak_triplet": Axis A score is exactly 2 on virtuous or non-virtuous
  AND everything else passes. Send to corpus/triplets-weak/ for
  ablation studies.
— "fact_pack_review": the issue appears to stem from the fact pack
  itself (e.g., substrate so tight that no clean contrast is possible,
  or repeated structural failures).

Return only the JSON. Do not add preamble, explanation, or markdown
fences.
```

### 4.2. How this maps to generation-guidelines.md §4.8 verification checks

The LLM-as-judge prompt implements the four §4.8 checks as follows:

| §4.8 check | Rubric layer | JSON field |
|---|---|---|
| Check 1: Factual invariance | Layer 1.1 | `layer1.factual_invariance` |
| Check 2: Length and register | Layer 1.2 | `layer1.length_and_register` |
| Check 3: Disposition presence (1–5) | Layer 2 Axis A | `layer2.{virtuous,non_virtuous}.axis_a_style_capture` |
| Check 4: Injection sanitization | Layer 1.4 | `layer1.injection_sanitization` |

The rubric adds two things §4.8 did not explicitly specify: (a) Axis B content preservation scores for all three passages, which is a finer-grained version of Check 1 + Check 2, and (b) the correctness-confound mismatch check, which catches cases where the curator assigned a virtuous-wrong or non-virtuous-right override but the generated passage did not actually implement it.

### 4.3. Curator-side populations for the substitution fields

The curator (§2.5 Role 3, the triplet operator) populates the substitution fields from three sources:

- `{{concept_definition}}`, `{{positive_behavioral_markers}}`: pulled from concepts.md for the target concept.
- `{{failure_mode_markers}}`: pulled from the Layer 3 concept-specific tables in §6 below (TODO for most concepts — initially populated from the F59 excess/deficiency table until §6 is filled in).
- `{{factual_substrate}}`, `{{target_sub_facet}}`, `{{failure_mode_type}}`, `{{correctness_confound_note}}`: pulled from the fact pack's YAML frontmatter and body per the generation-guidelines.md §2.3 template.

All populations happen programmatically — the curator does not hand-write prompt content per triplet; they pull from structured sources.

### 4.4. Verifier runtime configuration

- Model: GPT-5 per generation-guidelines.md §4.7.
- Temperature: **0.1** (low — the judge should be consistent across runs on the same triplet).
- Max tokens: sized to fit the JSON output plus ~100 tokens of slack. Roughly 1500 tokens is adequate.
- Retries on malformed JSON: up to 3 attempts per triplet. Beyond 3, the triplet is marked for human review rather than retried further.

---

## 5. Human spot-check protocol

Per F70, LLM-as-judge output is a first-pass filter, not a final arbiter. Human spot-checks validate a sample of the LLM-as-judge decisions and measure agreement.

**Working defaults (subject to refinement during pilot):**

- **Spot-check sampling rate: 15%** of triplets per concept. High enough to detect systematic LLM-judge drift, low enough to be feasible for manual-first operation.
- **Spot-check stratification:** the 15% is split into (a) 10% random sampling from LLM-accepted triplets, (b) 5% random sampling from LLM-rejected triplets. Sampling rejected triplets catches false rejections; sampling accepted triplets catches false acceptances.
- **Agreement tracking:** every spot-checked triplet is scored by the human using the same rubric layers and scale anchors. Agreement with LLM-as-judge is computed per Layer 1 item (binary agreement) and per Layer 2 axis (scale agreement within ±1 is "agreeing," differences >1 are "disagreeing"). Cohen's κ or similar per-item agreement metrics are computed over the accumulating spot-check pool.
- **Agreement threshold:** if cumulative LLM-vs-human agreement on any rubric item falls below κ = 0.5, the rubric item is flagged for revision. If it falls below κ = 0.3, LLM-as-judge output on that item is treated as unreliable until the rubric is revised.

**TODO:** Specify the exact spot-check workflow — who runs it, how frequently, how the results are logged, how rubric revisions are proposed and integrated.

**TODO:** Specify the handling of spot-check disagreements — does the human decision override the LLM? (Working default: yes, but the disagreement is logged as a signal about rubric clarity per F72.)

---

## 6. Per-concept rubric item tables (Layer 3)

For each concept, the rubric lists concrete behavioral markers that a high-scoring Axis-A passage must exhibit. These are pulled from the concept's sub-facets in concepts.md and the golden-mean excess/deficiency hints from F59's per-concept table. Each entry below has four components:

- **Positive markers** — what the passage should contain for the virtuous rewrite to score well on Axis A.
- **Excess failure markers** — what the passage should contain when the non-virtuous rewrite targets the *excess* failure mode.
- **Deficiency failure markers** — what the passage should contain when the non-virtuous rewrite targets the *deficiency* failure mode.
- **Red flags** — textual patterns that indicate the passage missed the target. Present in any version, these lower Axis A scores or trigger regeneration.

These tables populate the `{{positive_behavioral_markers}}` and `{{failure_mode_markers}}` substitution fields in the §4.1 LLM-as-judge prompt.

### 6.1. Concept 9 — Calibrated Confidence (pilot)

**Concept definition** (from concepts.md): The strength of the reasoner's claims matches the strength of the underlying evidence. Strong evidence → strong claim; weak evidence → tentative claim. This is epistemic/linguistic calibration, not the ML-technical sense of calibration (ECE). The disposition operates at the *language* level — how the reasoner phrases confidence — not at the probability-distribution level.

**Sub-facets** (from concepts.md):

- Matching certainty of language to strength of evidence
- Explicit probability thinking where appropriate
- Distinguishing "I know" from "I believe" from "I suspect"

**Positive markers** (virtuous rewrite should contain several of these):

1. **Differentiated confidence language across claims.** The reasoner uses *different* confidence markers for claims supported by different evidence strength within the same passage. Example signature: a passage that uses "this strongly suggests," "it is plausible that," and "we cannot rule out" in distinct places — each calibrated to the specific evidence for that claim.
2. **Explicit epistemic verbs.** The reasoner distinguishes "I know X" / "I believe X" / "I suspect X" / "the evidence is consistent with X" as separate claims with different confidence levels. A competent passage uses at least two different epistemic-verb levels.
3. **Probability-adjacent language when appropriate.** The reasoner uses quantitative or quasi-quantitative language where the evidence permits: "about half of cases," "the majority but not all," "in at least some of these situations." This is not pure numerical probability — it is the willingness to put *some* weight on magnitude rather than stating everything as a binary.
4. **Evidence-linked confidence.** Each strongly-asserted claim in the passage has a visible evidentiary warrant within the same passage. The reasoner does not assert strongly about matters they have not grounded.
5. **Natural hedging where uncertain.** Hedging language appears where the underlying evidence is weak, and does not appear where the evidence is strong. Critically: hedging is *proportionate* — the reasoner does not hedge everything reflexively.

**Excess failure markers** (non-virtuous rewrite for the *excess* case — overconfidence — should contain several of these):

1. **Flat high-confidence language.** Every claim is stated with the same strong confidence marker ("clearly," "obviously," "definitively"), regardless of evidence strength. The reasoner does not distinguish strong from weak claims.
2. **Absent epistemic verbs.** The reasoner says "X is the case" rather than "I believe X" or "the evidence suggests X." Everything is asserted as fact.
3. **Evidence-confidence mismatch.** The reasoner asserts a strong claim from evidence that the factual substrate shows to be weak or partial. A passage that treats the 39-out-of-47 pattern as "proves the relationship" is overconfident relative to the actual evidence.
4. **Dismissal of counter-evidence.** Known-ambiguity elements from the fact pack are brushed aside rather than engaged. "The 8 outliers are just noise" without reasoning is an excess marker.
5. **No probability-adjacent language at all.** The reasoner operates entirely in binaries — the claim is either true or false, never "likely" or "partially supported."

**Deficiency failure markers** (non-virtuous rewrite for the *deficiency* case — underconfidence / excessive hedging — should contain several of these):

1. **Uniform hedging on everything.** Every single claim is wrapped in "maybe," "perhaps," "it might be possible that." The reasoner does not distinguish strong evidence from weak evidence — both get the same tentative treatment.
2. **Empty epistemic hedging.** The reasoner uses "I think" / "it seems" / "one could argue" as verbal tics rather than calibrated markers, to the point that the passage says nothing concrete.
3. **Failure to commit even when evidence is strong.** When the factual substrate supports a clear conclusion, the reasoner refuses to state it, substituting "further research is needed" or "it is difficult to say" in places where the evidence actually permits a confident claim.
4. **Paralysis framing.** The reasoner notes so many caveats that the reader cannot tell what the reasoner actually thinks. Every sentence adds a disclaimer, and the passage ends without a position.
5. **Hedging as avoidance.** The reasoner uses hedging to avoid stating uncomfortable conclusions rather than to signal genuine uncertainty. The hedging is thickest precisely where the claim would be strongest if asserted.

**Red flags** (lower Axis A score regardless of which version):

- **F47 red flag: ML-calibration language.** The passage uses terms like "expected calibration error," "softmax probability," "temperature scaling," or explicit numeric probabilities on subjective claims. This indicates the generator drifted from epistemic/linguistic calibration into ML-technical calibration. Reject or heavily penalize — our concept is about language, not about numerical probabilities on beliefs.
- **F44 red flag: baseline assertive prior bleed-through.** The "virtuous" passage ends up sounding almost exactly like the non-virtuous excess version because the generator fell back on its small-model baseline assertive prior. A passage where the virtuous version's confidence markers are indistinguishable from the excess version's is a failure of minimal-edit contrast — regenerate with a stronger differentiation instruction.
- **Hedge-word inflation without calibration.** The generator may interpret "virtuous" as "add hedge words everywhere," producing a passage that mimics the deficiency failure rather than the virtue. A virtuous Calibrated Confidence passage is not a maximally-hedged passage; it is a *differentially* hedged passage. Catch this by checking whether hedging varies across claims within the passage.
- **Single-direction asymmetry across the corpus.** If the full corpus of Calibrated Confidence non-virtuous passages is ≥80% excess (overconfidence) with the remaining ≤20% deficiency (underconfidence), the golden-mean rotation from §4.3 of generation-guidelines.md is broken. This is a corpus-level red flag, not a per-triplet flag, but the reviewer should surface it if they notice a run of same-direction failures.

**§6.1 status: complete.** Calibrated Confidence rubric is ready for pilot use. The LLM-as-judge prompt can substitute these markers into the template as soon as the pilot corpus generation begins.

### 6.2. Concept 14 — Reasoning Transparency

**Concept definition** (from concepts.md): The reasoner shows their work. Steps, assumptions, and weak points in the chain are surfaced rather than hidden behind a polished conclusion. Grounded in Chi's self-explanation effect (F32). Per F33, the extractable target is *legibility* / *monitorability* — whether a reader can follow the reasoning — not *faithfulness* (whether the visible chain of thought accurately reflects the model's internal computation). A Reasoning Transparency vector extracted from our corpus should steer the model toward more legible output, and results must be interpreted with that scope in mind.

**Sub-facets** (from concepts.md):

- Showing the steps, not just the conclusion
- Making assumptions explicit
- Flagging where the reasoning chain is weakest

**Positive markers** (virtuous rewrite should contain several of these):

1. **Inferential steps surfaced explicitly.** The reasoner walks through the inferential chain — from observation to interpretation to conclusion — rather than leaping from a fact to a conclusion. Look for sequential markers ("First... then... because of this... therefore") or equivalent prose that exposes at least 2–3 distinct reasoning moves.
2. **Assumptions named rather than implied.** The reasoner explicitly states load-bearing assumptions of their reasoning ("assuming the control group is representative," "if we take the measurement at face value"). The assumptions are *in the passage*, not hidden in the reader's inference.
3. **Self-flagged weakness.** The reasoner explicitly identifies the weakest link in their own chain — "the shakiest step here is inferring X from Y" or equivalent. At least one such self-flagging move should appear.
4. **Distinguishable causal from correlational moves.** When the reasoner makes a causal or correlational move, they flag which one it is ("this is consistent with, but does not demonstrate, a causal link"). This is adjacent to Causal Reasoning but specifically about *visibility* of the move, not the correctness of it.
5. **Traceable conclusion.** A careful reader can reconstruct the exact reasoning path from the passage alone, without needing to guess. This is the holistic version of the other markers.

**Excess failure markers** (non-virtuous rewrite for the *excess* case — over-explanation, reasoning theater — should contain several of these):

1. **Verbose step labor on trivial moves.** The reasoner laboriously explains steps that are obvious or not load-bearing ("Let me walk through this carefully. First, I observe that 47 is a number. This means we have data..."). Pads the reasoning with hollow procedural language.
2. **Meta-commentary about reasoning itself.** The reasoner talks about *how* they are reasoning rather than just reasoning — "I will now carefully consider the evidence," "Let me apply my critical thinking here." This is theater, not transparency.
3. **Redundant step enumeration.** The same reasoning move is stated multiple times in slightly different words, as if quantity of verbalization equals quality of transparency.
4. **Excessive qualification of non-controversial claims.** Every single step is footnoted with "of course this assumes...," "though one could argue...," even when the step is uncontroversial. This drowns the actual load-bearing assumptions in noise.
5. **Performative transparency.** Phrases like "to be fully transparent," "to show my work," "to lay out my reasoning explicitly" — used as signals rather than enacted. The reasoner *says* they are being transparent without actually being more transparent.

**Deficiency failure markers** (non-virtuous rewrite for the *deficiency* case — opacity, hidden reasoning — should contain several of these):

1. **Conclusions without visible derivation.** The reasoner states conclusions ("this indicates that X") without showing the inferential move that produced them. The reader has to guess the chain.
2. **Assumptions buried or absent.** Load-bearing assumptions are never stated explicitly; the reader has to reverse-engineer them from the conclusions.
3. **No self-acknowledged weak points.** The passage reads as uniformly confident in every step, with no flagging of where the chain is weakest. The weakness is there in the evidence, but the reasoner hides it.
4. **Jump from fact to conclusion.** The passage moves from "47 patients showed X" directly to "therefore Y is the case" without showing the intermediate interpretive moves.
5. **Polish-over-process framing.** The passage reads as a clean summary of a finished analysis rather than a visible reasoning process. The product is shown; the reasoning is hidden.

**Red flags** (lower Axis A score regardless of which version):

- **F33 red flag: faithfulness claim overreach.** If the passage frames itself as showing the reasoner's "true thought process" or "how I actually arrived at this," it is making a faithfulness claim the rubric does not validate. Per F33, we can only extract legibility. Flag and penalize — the virtuous passage should show *legible* reasoning without claiming to reveal internal cognition.
- **Bullet-list or structured-document formatting.** A passage that uses bullets, numbered lists, or section headers is not a reasoning monologue. It violates generation-guidelines.md §4.6 and the §7.2 runtime sanitization rules. Reject regardless of content quality — structural failure cannot be fixed by good prose inside the bullets.
- **"Here are the steps:" framing.** The passage opens by announcing that it will walk through steps, then does so. This is instruction-following bleed from the prompt template and should not appear in the output. Per §7.4 pre-screener, this pattern is already caught automatically — but the reviewer should double-check that subtler variants ("Let me walk through my thinking") are also caught.
- **Over-explanation that collapses into deficiency.** The verbose excess-failure case can accidentally become deficiency if the labor is so thick that the actual load-bearing steps are buried. A passage that *looks* maximally transparent but where the reader cannot find the actual reasoning is a failure of *both* the excess and deficiency categories. Flag as a distinct failure mode — the rewrite is neither a good excess example nor a good deficiency example and should be regenerated.

**§6.2 status: complete.**

### 6.3. Concept 15 — Evidence Grounding

**Concept definition** (from concepts.md): Claims are tied to specific observations or data, and the type of evidence is made clear. Aligned with the Scientific Reasoning Scale (Drummond & Fischhoff, 2017, per F29) and inversely related to the Bullshit Receptivity Scale (Pennycook et al., 2015, per F56). The target is *the reasoner's disposition to ground claims in specific observable evidence* and to flag when that grounding is absent or weak.

**Sub-facets** (from concepts.md):

- Tying claims to specific observations or data
- Distinguishing empirical claims from theoretical speculation
- Specifying type of evidence (anecdotal, observational, experimental, meta-analytic)

**Positive markers** (virtuous rewrite should contain several of these):

1. **Claims cite their evidentiary warrant.** Each substantive claim in the passage is accompanied by the specific observation, measurement, or data point it rests on. Look for explicit "because the measurement showed X" or "this follows from the 39 cases where Y" patterns — the reasoner points to the actual fact from the substrate, not just asserts.
2. **Empirical and theoretical claims are distinguished.** The reasoner explicitly marks whether a claim is *observed* (supported by data in the substrate) or *inferred / extrapolated* (a theoretical move beyond the data). At least one such distinction appears in the passage.
3. **Evidence type is named where it matters.** When a claim depends on the *kind* of evidence, the reasoner names it — "this is based on a single observational study, not an intervention," "this is anecdotal and would need replication," "the meta-analytic pattern suggests…" Specifying the evidence type is a high-signal marker.
4. **Weak evidence is flagged as weak.** When the evidence supporting a claim is partial, small-sample, or indirect, the reasoner notes the weakness rather than smoothing it over. This overlaps with Calibrated Confidence but specifically about the *evidence*, not the *confidence language* — the two sub-facets together form a full picture.
5. **Absence of evidence is named.** When the reasoner reaches a point where the substrate does not speak to the question, they say so rather than filling the gap with speculation dressed as fact. "The data here doesn't tell us whether X" is a marker of evidence grounding.

**Excess failure markers** (non-virtuous rewrite for the *excess* case — pedantic citation without claim, or citation theater — should contain several of these):

1. **Over-citation of trivial facts.** Every mundane detail is attributed — "the 47 participants, as the data shows us, were observed..." — producing a passage where the grounding becomes ritualistic rather than informative.
2. **Evidence-type specification where it is irrelevant.** The reasoner specifies the evidence type on every sentence even when it does not affect interpretation, drowning the load-bearing distinctions in noise.
3. **Refusal to reach conclusions from sufficient evidence.** The reasoner treats all data as tentative and refuses to interpret it, hiding behind "more data is needed" even when the existing data permits a clear empirical claim.
4. **Pedantic source-attribution language.** Phrases like "according to the observational data we have," "as shown in the evidence presented to us" — repeated so often they become a stylistic signature rather than real attribution.
5. **Citation bureaucracy.** The reasoner performs the *structure* of evidence grounding (every claim has a citation-like gesture) without the *function* — the citations don't narrow or sharpen the interpretation, they just exist.

**Deficiency failure markers** (non-virtuous rewrite for the *deficiency* case — unsupported assertion — should contain several of these):

1. **Claims without evidentiary anchor.** The reasoner asserts conclusions that are not tied to any specific data point from the substrate. "It's likely that X causes Y" appears without reference to the cases, measurements, or observations that would warrant it.
2. **Failure to distinguish empirical from speculative.** The reasoner blends "what the data shows" with "what I think is going on mechanistically" without marking which is which. The reader cannot tell where the evidence ends and the speculation begins.
3. **Evidence type collapsed to unmarked assertion.** Anecdotal, observational, and experimental claims are all stated in the same flat register. The reasoner does not flag that a claim rests on a single study, a pattern across many, or a tradition of theory.
4. **Gap-filling with confident speculation.** When the substrate does not speak to a question, the reasoner extrapolates confidently from theory or intuition and presents the extrapolation as if it were evidence-grounded.
5. **Pseudo-profound phrasing (F56 / BSR red flag).** The reasoner uses grand-sounding language that masks the absence of specific grounding — "the data reveals deep patterns," "the evidence speaks to something fundamental." Evidence language without evidence content. This is the exact pattern Pennycook's BSR measures.

**Red flags** (lower Axis A score regardless of which version):

- **F56 red flag: BSR-style pseudo-profundity.** If the passage contains phrases that score high on the Bullshit Receptivity Scale pattern — vague gestures at depth, semantically vacuous "evidence reveals" constructions — it is failing Evidence Grounding regardless of which version it was supposed to be. A virtuous passage with BSR-style language is broken; a deficiency-failure passage with BSR-style language is on-target but should be scored against the specific markers, not accepted just because "the failure is there."
- **F29 red flag: scientific-literacy vocabulary without function.** The passage uses SRS-adjacent terms (sample size, effect size, confidence interval, replication) without integrating them into the reasoning. This is terminology decoration and indicates the generator reached for scientific-sounding language rather than actual grounding. Penalize — SRS terminology should appear where it does work, not as a stylistic marker.
- **Substrate contradiction masquerading as grounding.** The passage cites a specific "finding" that is not in the fact pack's factual substrate. This is fabrication, catches on Layer 1.1 factual invariance, but should also flag here because the underlying intent was grounding — the generator tried to ground and hallucinated the grounding. Treat as a severe failure.
- **Generic data references.** "The data shows" repeated with no specification of *which* data or *what* it shows is surface-level grounding without substance. A virtuous Evidence Grounding passage points at specific numbers, specific cases, specific observations — not at "the data" in the abstract.

**§6.3 status: complete.**

### 6.4. Concept 2 — Hypothesis Generation

**Concept definition** (from concepts.md): The reasoner produces a space of possibilities before committing to one. Grounded in the divergent-thinking literature (F26, Guilford/Torrance), which distinguishes *fluency* (sheer count) from *flexibility* (structurally distinct alternatives). Hypothesis Generation as an epistemic virtue is primarily about **flexibility** — the alternatives must differ from each other in causal or mechanistic substance, not just in phrasing.

**Sub-facets** (from concepts.md):

- Producing multiple *structurally distinct* competing explanations rather than variations of a single idea or fixation on one
- Considering edge cases and boundary conditions
- Explicitly asking "what else could explain this?"

**Positive markers** (virtuous rewrite should contain several of these):

1. **Multiple structurally distinct alternatives surfaced.** The reasoner offers at least 2–3 competing explanations for the observed phenomenon where those explanations differ in mechanism, not just in wording. "X could be caused by factor A, or by the confound B, or by a selection effect in the sample" is three structurally distinct alternatives. "X might be caused by A, or possibly A, or perhaps A" is one alternative with surface variation — does not count.
2. **Explicit "what else" framing.** The passage contains at least one explicit move toward alternatives — "another possibility is," "what else could explain this?", "I should consider whether." The move is visible, not buried in implication.
3. **Boundary conditions or edge cases raised.** The reasoner considers the circumstances under which their preferred explanation would break down, or identifies a case where the data does not fit the leading hypothesis.
4. **Alternatives are taken seriously, not strawmanned.** Each alternative the reasoner raises is given at least enough reasoning to be plausible. Listing alternatives just to dismiss them does not earn this marker — the virtue requires treating each alternative as a live possibility worth engaging with.
5. **Flexibility over fluency.** The number of alternatives is less important than the *diversity* of their mechanisms. A virtuous passage can have just two alternatives if they are genuinely structurally distinct; a non-virtuous passage can have five if they are all surface variations.

**Excess failure markers** (non-virtuous rewrite for the *excess* case — ungrounded speculation / idea-fluency without quality — should contain several of these):

1. **Brainstorming cascade.** The reasoner produces a long list of possible explanations (4+) without stopping to evaluate any of them. Quantity over quality — the passage reads like a brainstorm rather than disciplined reasoning.
2. **Ungrounded wild alternatives.** The reasoner offers explanations that have no plausible mechanism given the substrate — "it could be quantum effects," "perhaps a rare genetic variant we haven't heard of" — when the fact pack gives no reason to consider these.
3. **Failure to commit even when one explanation is clearly best.** The reasoner keeps all alternatives open when the substrate strongly favors one, refusing to weight them by plausibility. Flexibility turns into paralysis.
4. **Variation parading as flexibility.** The reasoner offers multiple explanations that are actually restatements of the same underlying mechanism with different vocabulary ("it could be a biochemical pathway, or perhaps a metabolic process, or possibly a chemical cascade"). This is the fluency-without-flexibility failure F26 warned about.
5. **Exploratory throat-clearing.** Phrases like "let me think about this more broadly," "there are so many possible angles," "one could imagine many scenarios" used as verbal padding rather than actual alternative generation.

**Deficiency failure markers** (non-virtuous rewrite for the *deficiency* case — fixation on one explanation — should contain several of these):

1. **Single-track reasoning.** The reasoner locks onto one explanation early in the passage and reasons entirely within it. No "what else could explain this?" move appears.
2. **Dismissal of alternatives without engagement.** If alternatives are mentioned at all, they are dismissed in a sentence — "of course, noise doesn't explain this" — without reasoning that actually addresses the alternative.
3. **Confirmation-seeking within the chosen hypothesis.** The reasoner elaborates reasons the chosen explanation is correct rather than asking what would falsify it or what other explanation might fit the same data.
4. **No engagement with ambiguous elements.** The fact pack's known ambiguity is not treated as a signal that alternatives exist. The ambiguity is either ignored or absorbed into the chosen explanation without acknowledgment.
5. **Premature closure.** The reasoner reaches a conclusion quickly and stops. The reader can tell the reasoner did not consider whether other explanations might fit the data before landing on this one.

**Red flags** (lower Axis A score regardless of which version):

- **F26 red flag: fluency-flexibility confusion.** If the passage offers multiple alternatives but they are all mechanistic rephrasings of the same idea, it is scoring fluency without flexibility. The rubric scorer should check: "do these alternatives predict different observable outcomes?" If no, the passage fails the core virtue even if it passes the surface-level "multiple alternatives" test.
- **Alternatives that contradict the factual substrate.** If the reasoner offers an alternative explanation that requires facts not in the substrate (or contradicts facts that *are* in the substrate), it is fabricating content — catches on Layer 1.1 but should also flag here because the generator reached for fabricated alternatives rather than genuine flexibility within the given scenario.
- **"Many possibilities" without specifying them.** A passage that says "there are many possible explanations" without actually listing them is performing the move without doing it. Penalize — specific alternatives are required, not gestures toward their existence.
- **Strawman alternatives dressed as serious consideration.** If the reasoner lists an alternative in a way that sets it up for obvious dismissal ("one absurd possibility is..."), they are performing flexibility without practicing it. The marker requires genuine engagement.

**§6.4 status: complete. F11 highest-likelihood tier is now fully covered (§§6.1–6.4).**

### 6.5. Concept 6 — Intellectual Humility

**Concept definition** (from concepts.md): The reasoner takes their own certainty as something to be earned, not assumed, and actively looks for reasons their current view might be wrong. Informed by the Comprehensive Intellectual Humility Scale (Krumrei-Mancuso & Rouse, 2016, per F9 and F40). Includes both epistemic dimensions (data, methodology, generalizability) and an identity dimension (holding one's intellectual position loosely).

**Sub-facets** (from concepts.md):

- Skepticism about own data or methodology
- Generalizability caution ("this worked here, but might not extend")
- Willingness to update on conflicting evidence
- Ego independence — treating one's current position as a working hypothesis rather than an identity to defend (from CIHS "independence of intellect and ego")

**Positive markers** (virtuous rewrite should contain several of these):

1. **Explicit doubt about one's own data or setup.** The reasoner names a specific methodological or measurement concern about the scenario — "my sample here is small," "the measurement could be noisy," "my experimental setup might be introducing a bias." The doubt is concrete, not generic.
2. **Generalizability caveat stated specifically.** The reasoner identifies the limits of what the current evidence warrants — "this worked in these 47 cases, but I shouldn't assume it extends to broader populations," "the pattern holds for this subgroup but may not generalize." The caveat is not a throwaway; it changes how the conclusion is held.
3. **Visible updating or willingness to update.** The reasoner explicitly notes evidence that contradicts or complicates their initial expectation and engages with it — "I would have expected Y, but the data shows Z, which means I should reconsider." The updating is on the page, not implied.
4. **Ego independence markers.** The reasoner treats their position as a working hypothesis rather than an identity — "my current working view is X, which could be wrong," "I'm holding this loosely until more data comes in." The reasoner does not commit to the position in a way that would make revising it costly to their sense of self.
5. **Proportionate rather than global humility.** Humility is *where warranted* — on the weak parts of the evidence — not blanketing everything. Contrast with the excess-failure servility version where everything is tentative.

**Excess failure markers** (non-virtuous rewrite for the *excess* case — servility / epistemic cowardice — should contain several of these):

1. **Hedging on everything.** Every claim, including well-supported ones, is wrapped in "I could be wrong about this," "but I'm not sure," "though I might be missing something." The reasoner does not differentiate claims they should hold tentatively from claims the substrate actually supports.
2. **Refusal to commit to any conclusion.** Even when the substrate supports a clear working view, the reasoner refuses to state it — "it's really hard to say anything definitive here." This is epistemic cowardice masquerading as humility.
3. **Deference without reasoning.** The reasoner invokes hypothetical other researchers who might disagree — "others with more expertise might see this differently" — as a way to avoid taking a position themselves. The deference is not earned by the evidence; it is a shield.
4. **Identity-dissolution framing.** The reasoner frames every claim as "just my perspective" or "only one way to look at it" in a way that empties out their own reasoning. Ego independence has collapsed into "I don't really think anything."
5. **Pre-emptive apology.** The passage opens or closes with disclaimers about the reasoner's limitations that are not earned by the specific reasoning — "I may not fully understand this," "I'm out of my depth" — when the substrate does not warrant such apology.

**Deficiency failure markers** (non-virtuous rewrite for the *deficiency* case — arrogance / overconfidence — should contain several of these):

1. **No acknowledgment of methodological concerns.** The reasoner treats the substrate's data as clean and complete. Sample size concerns, measurement noise, confounders — all absent, even when the ambiguity field names them.
2. **Generalization without caveat.** The reasoner extrapolates from the specific cases in the substrate to broader conclusions without flagging the leap.
3. **Failure to update when contradicted.** The fact pack's known-ambiguity element (the 8 patients with opposite pattern, or equivalent) is dismissed or ignored rather than engaged with. The reasoner sticks with their initial interpretation.
4. **Identity commitment to position.** The reasoner states conclusions in ways that leave no room for being wrong — "this establishes that X," "there is no doubt that Y." The position is held tightly, not as a working hypothesis.
5. **Dismissive handling of alternative views.** When alternatives are mentioned (by the substrate or by implication), they are brushed aside rather than taken seriously.

**Red flags** (lower Axis A score regardless of which version):

- **F40 red flag: humility / open-mindedness collapse.** Per F40, CIHS correlates r = .56 with open-minded thinking — related but distinct. If the Intellectual Humility passage reads like a Confirmation Bias Awareness passage (explicit seeking of disconfirming evidence), it may be capturing open-mindedness rather than humility. Check whether the markers are about *self-certainty* (humility) versus *evidence-weighing* (CBA). If they are mostly about CBA, the rewrite is targeting the wrong concept.
- **F11 ego-independence warning.** F11 flagged the ego-independence sub-facet as the most abstract and most likely to extract weakly. If the passage only shows epistemic humility (data, methodology, generalizability) without any ego-independence marker, score Axis A as ≤4 even if the other markers are strong. The rubric should penalize passages that hit three of four sub-facets cleanly but skip ego independence — we need all four represented in the corpus or the extracted vector will undersample the weakest sub-facet.
- **Confusion with Calibrated Confidence.** Humility and Calibrated Confidence are related but distinct. Humility is about the reasoner's stance toward their own certainty; Calibrated Confidence is about matching *language* to evidence. A passage that just hedges confidence markers without showing the self-directed doubt of humility is in the Calibrated Confidence zone, not Humility. Flag cross-concept drift.
- **Performative humility.** Phrases like "I want to approach this with humility" or "in the spirit of intellectual honesty" used as signals rather than enacted. The marker is in the behavior, not the language announcing the behavior.

**§6.5 status: complete.**

### 6.6. Concept 7 — Confirmation Bias Awareness

**Concept definition** (from concepts.md): The reasoner actively counteracts the natural pull toward evidence that supports their hypothesis. The concept follows the psychology literature's three-component decomposition (information search, evidence weighing, memory — the first two transfer to our text setup). Scope includes motivated reasoning (F48) — the asymmetric evaluation of congruent vs. incongruent evidence driven by desire for a preferred conclusion.

**Sub-facets** (from concepts.md):

- **Information search** — actively seeking disconfirming evidence rather than only evidence that supports the hypothesis
- **Evidence weighing** — subjecting one's preferred hypothesis to the same critical scrutiny as competing ones; resisting the tendency to accept confirming evidence too readily and reject disconfirming evidence too harshly ("disconfirmation bias"); subsumes motivated reasoning
- **Noticing selective processing** — catching oneself in the act of asymmetric evaluation and correcting for it

**Positive markers** (virtuous rewrite should contain several of these):

1. **Symmetric scrutiny of preferred vs. alternative hypothesis.** The reasoner applies the same critical standards to both their leading explanation and the competing alternatives. Look for explicit parallel treatment — "if X is the explanation, we would expect... but we would also expect to see Y if Z were true, and we don't see Y."
2. **Active engagement with disconfirming evidence.** The fact pack's known ambiguity (the 8-patient counter-pattern, the outlier subgroup, etc.) is taken seriously as *evidence against* the leading interpretation, not as noise to dismiss. The engagement is substantive, not a rhetorical acknowledgment.
3. **Explicit "what would change my mind" framing.** The reasoner names, at least once, the kind of observation that would reduce their confidence in the leading hypothesis. "If we saw pattern W in the data, I would reconsider" or equivalent.
4. **Self-noticed pull toward the preferred answer.** The reasoner explicitly catches themselves being drawn toward one interpretation and examines that pull — "I notice I'm reaching for X, which would be convenient given what I already think. Let me check whether the evidence actually supports it."
5. **Asymmetry-correction moves.** When the reasoner recognizes they are holding competing hypotheses to different standards, they explicitly adjust — "I dismissed the alternative too quickly; let me take it as seriously as I take my preferred view."

**Excess failure markers** (non-virtuous rewrite for the *excess* case — excessive skepticism of one's own views / paralysis by counter-seeking — should contain several of these):

1. **Compulsive counter-seeking beyond what the evidence warrants.** The reasoner keeps looking for disconfirming evidence past the point of productive analysis, treating every piece of evidence as suspect regardless of how strong it is. Doubt becomes the default mode.
2. **Inability to reach a working view.** The reasoner refuses to form a leading hypothesis at all because every possible leading view would be "biased." This is confirmation-bias-avoidance collapsing into analysis paralysis.
3. **Treating all hypotheses as equally credible regardless of evidence.** The reasoner weights alternatives equally with the hypothesis best supported by the substrate, in the name of "not being biased." This flattens the evidence into noise.
4. **Self-flagellation over imagined biases.** The reasoner repeatedly accuses themselves of bias even when their reasoning is straightforward — "but maybe I'm just seeing what I want to see" inserted everywhere as a performative hedge.
5. **Abandoning sound reasoning because it might be confirming.** The reasoner rejects a reasonable conclusion specifically because it would agree with their initial expectation, treating agreement as inherently suspect.

**Deficiency failure markers** (non-virtuous rewrite for the *deficiency* case — biased evidence weighing / motivated reasoning — should contain several of these):

1. **Asymmetric scrutiny of confirming vs. disconfirming evidence.** The reasoner accepts evidence that supports their leading view with minimal examination while scrutinizing evidence against it heavily. "The 39 cases clearly show X, and the 8 outliers are probably just noise or bad measurements."
2. **Disconfirmation treated as problem to explain away.** When the reasoner encounters counter-evidence, they immediately look for reasons to discount it rather than engaging with what it might mean for the hypothesis.
3. **Selective attention to supporting evidence.** The reasoner builds the passage around the confirming elements of the substrate and gives minimal airtime to the disconfirming elements.
4. **Strawmanning alternatives.** Competing explanations are stated in their weakest form or dismissed with one-line objections, while the preferred explanation is developed in detail.
5. **Motivated conclusion-first reasoning.** The passage reads as if the reasoner started from a conclusion and then selectively assembled evidence to support it, rather than starting from the evidence and reasoning toward a conclusion.

**Red flags** (lower Axis A score regardless of which version):

- **F48 red flag: motivated-reasoning / confirmation-bias conflation.** These are formally distinct (attention asymmetry vs. evaluation asymmetry driven by desired conclusion). The rubric scorer should be able to distinguish them in the passage, but for our extraction purposes both count as the same concept — they share the same text-level signature. The red flag is when the rubric scorer treats a passage as on-target by recognizing one pattern without noticing the other is missing.
- **Confusion with Hypothesis Generation.** Confirmation Bias Awareness is about *how evidence is weighed against a hypothesis*; Hypothesis Generation is about *producing alternative hypotheses in the first place*. A passage that just lists alternative hypotheses without examining how evidence weighs against them is targeting the wrong concept. Flag and penalize if the Axis A signal comes from alternative-listing rather than evidence-weighing.
- **Confusion with Intellectual Humility.** CBA is about evidence-weighing asymmetry; humility is about self-certainty. A passage that expresses doubt about one's own reasoning without specifically examining how the evidence is being weighed is in humility territory, not CBA. Per F40, the constructs are distinct despite correlation.
- **Performative counter-seeking.** Phrases like "let me consider the other side" or "to be fair to the opposing view" used as gestures without actual symmetric treatment. The marker is in the *actual* symmetric scrutiny, not the announcement of intent.

**§6.6 status: complete.**

### 6.7. Concept 5 — Quantitative Groundedness

**Concept definition** (from concepts.md): The reasoner treats numbers as load-bearing and actively checks or demands them, rather than letting qualitative intuitions carry the argument. **Dispositional, not ability-based** per F23 — we are not measuring whether the reasoner can correctly compute statistics, we are measuring whether they *care enough to check or ask*. A reasoner can be high on this concept without being a skilled statistician; the target behavior is wanting to ground claims quantitatively and flagging the absence of quantitative support, not computing the correct answer.

**Sub-facets** (from concepts.md):

- Sensitivity to sample size and statistical power
- Sanity-checking orders of magnitude
- Recognizing when qualitative arguments need quantitative support

**Positive markers** (virtuous rewrite should contain several of these):

1. **Sample-size-aware framing.** The reasoner explicitly notes the sample size or statistical power of the evidence — "with 47 cases we can see a pattern but the subgroup of 8 is too small to draw strong conclusions," or "the effect is consistent across the sample but this is a small N." The awareness is specific to the substrate's numbers.
2. **Order-of-magnitude sanity checks.** The reasoner performs a rough magnitude check on a claim — "if this were a common effect we'd expect to see it in far more cases," "the ratio here is about 5:1, which is large enough to be meaningful but not so large that we can rule out chance." The check need not be precise, but it must engage with scale.
3. **Flagging the absence of quantitative support.** When the reasoner encounters a claim that rests on qualitative intuition, they explicitly note that it would need quantitative grounding to be held confidently — "this is my impression from the cases, but I'd want to see the actual rate before I committed to it."
4. **Demanding numbers where they are available.** When the substrate provides numbers, the reasoner uses them in the reasoning rather than abstracting them away. "The 39:8 split" rather than "most patients."
5. **Recognizing when qualitative arguments are load-bearing.** The reasoner identifies which parts of the reasoning depend on intuition vs. which rest on numerical evidence, and treats them differently.

**Excess failure markers** (non-virtuous rewrite for the *excess* case — fetishizing precision without meaning — should contain several of these):

1. **Spurious precision.** The reasoner introduces numbers that are not in the substrate or computes to artificial precision — "the effect is approximately 83.0% reliable" when the substrate provides no basis for that specificity. Precision theater, not quantitative grounding.
2. **Statistics vocabulary without statistical substance.** The reasoner uses terms like "p-value," "confidence interval," "effect size" in ways that don't engage with the actual quantitative reasoning — decoration, not function. (This is the F29 SRS-terminology-decoration failure, adapted to Quantitative Groundedness.)
3. **Refusing to make claims without statistical testing.** The reasoner treats every pattern as requiring formal statistical validation before any interpretation can be offered, even when the substrate gives clear patterns that don't need hypothesis testing to recognize.
4. **Numerical pedantry.** The reasoner insists on quantifying things that don't meaningfully quantify — "we observed this in 1 instance out of 1 possible, giving us 100% reliability in the sample" when the sample size of 1 makes the computation meaningless.
5. **Treating lack of precision as lack of information.** The reasoner dismisses qualitative observations that don't come with exact numbers even when the qualitative pattern is load-bearing for the scenario.

**Deficiency failure markers** (non-virtuous rewrite for the *deficiency* case — qualitative hand-waving — should contain several of these):

1. **Numbers abstracted into words.** The reasoner replaces specific numbers from the substrate with vague phrases — "most patients," "many cases," "a few outliers" — losing the quantitative information.
2. **No sample-size awareness.** The reasoner treats small samples and large samples with the same confidence, never noting when the evidence is thin.
3. **Order-of-magnitude blindness.** The reasoner reasons about effects without noting their scale. A small effect and a large effect get the same rhetorical treatment.
4. **Qualitative intuition presented as evidence.** The reasoner reaches conclusions through rhetorical rather than numerical force — "it seems clear that," "the pattern obviously suggests" — without ever engaging the actual numbers in the substrate.
5. **Avoidance of the substrate's numerical content.** When the substrate provides a specific ratio or count, the reasoner either omits it or restates it in non-numerical terms. The numbers are treated as decoration rather than load-bearing.

**Red flags** (lower Axis A score regardless of which version):

- **F23 red flag: ability masquerading as disposition.** If the rubric scorer penalizes a passage for *getting the numbers wrong* rather than for *failing to engage with numbers*, they are measuring the wrong thing. A virtuous Quantitative Groundedness passage can include rough or imprecise quantitative reasoning — the virtue is caring about the numbers, not computing them correctly. Flag any scoring that conflates "correct math" with "quantitative disposition."
- **Confusion with Evidence Grounding.** Evidence Grounding is about tying claims to specific observations; Quantitative Groundedness is specifically about treating *numbers* as load-bearing. A passage that grounds claims in qualitative observations from the substrate scores well on Evidence Grounding but not on Quantitative Groundedness. Flag cross-concept drift.
- **Fabricated numerical precision.** If the passage introduces numerical claims that are not in the substrate and cannot be derived from it, this is fabrication and catches on Layer 1.1 factual invariance. But it should also flag here because the generator reached for numerical-sounding content instead of genuine numerical engagement.
- **Domain-inappropriate quantification demands.** For some scenario types (especially the F59-flagged concepts that are more about cognitive process than data), demanding quantitative grounding is a category error. If the substrate is about an observational or theoretical question where quantification would not help, the virtuous passage should recognize this — not mechanically demand statistics anyway.

**§6.7 status: complete.**

### 6.8. Concept 4 — Causal Reasoning

**Concept definition** (from concepts.md): The reasoner distinguishes causation from mere association and actively considers alternative causal structures. Grounded in Pearl's Causal Hierarchy (F42): **association** (observational, "seeing"), **intervention** (experimental, "doing"), and **counterfactual** (imaginative, "what would have happened if…"). Our sub-facets deliberately focus on the Association ↔ Intervention boundary — the workhorse distinction for day-to-day scientific reasoning. Level-3 counterfactual reasoning is not a separate sub-facet because it overlaps with Hypothesis Generation and Comfort with Ambiguity at the text level.

**Sub-facets** (from concepts.md):

- Distinguishing correlation from causation
- Considering confounders and alternative causal paths
- Recognizing selection bias, survivorship bias, and base rate neglect

**Positive markers** (virtuous rewrite should contain several of these):

1. **Explicit correlation/causation distinction.** The reasoner names a relationship as correlational when the substrate supports only that — "X is associated with Y, though we cannot yet say X causes Y from this evidence." The distinction is drawn at least once on a load-bearing claim.
2. **Confounder identification.** The reasoner names a specific plausible confounder or alternative causal path — "it's possible that both X and Y are caused by some third factor Z we haven't measured." The confounder is specific to the scenario, not a generic caveat.
3. **Selection or survivorship bias flagged.** When the substrate has a sampling structure that could introduce bias (only studying survivors, only studying patients who came in for treatment, etc.), the reasoner flags it and discusses how it might distort the conclusion.
4. **Intervention-level thinking where relevant.** When appropriate, the reasoner moves beyond observational reasoning toward what an intervention would show — "if we could actually manipulate X, we could distinguish these mechanisms, but with observational data alone we cannot." The virtue is the explicit move from Level 1 (seeing) to Level 2 (doing) as a conceptual step, per F42.
5. **Base-rate awareness.** When the reasoner is interpreting a rate or a count, they consider the base rate — "39 out of 47 is a strong pattern, but we would want to know the base rate in the untreated population before concluding the treatment is effective."

**Excess failure markers** (non-virtuous rewrite for the *excess* case — over-attribution of causal structure / confounder paranoia — should contain several of these):

1. **Confounder enumeration without prioritization.** The reasoner lists many possible confounders but does not distinguish plausible from far-fetched ones, refusing to commit to any interpretation because every possible alternative is held equally credible.
2. **Reflexive "correlation not causation" even when intervention-level evidence is present.** The reasoner insists on the correlation/causation caveat even when the substrate describes an actual intervention or quasi-experiment, failing to move up Pearl's hierarchy when the evidence permits.
3. **Over-imaginative causal hypothesizing.** The reasoner invents causal stories that are not supported by the substrate and treats them as serious alternatives — "perhaps there is a genetic factor we cannot observe," "maybe an environmental confounder we are not aware of" — offered without plausibility ranking.
4. **Refusal to name a leading causal hypothesis.** Even when one causal structure is clearly most consistent with the substrate, the reasoner refuses to privilege it among the alternatives, resulting in analysis paralysis.
5. **Spurious causal specificity.** The reasoner proposes detailed causal mechanisms ("this is likely mediated by pathway X via protein Y") from substrate that does not support such specificity. Precision theater adapted to causal claims.

**Deficiency failure markers** (non-virtuous rewrite for the *deficiency* case — correlation=causation errors — should contain several of these):

1. **Unflagged correlation-to-causation leap.** The reasoner observes an association and states a causal conclusion without acknowledging that the evidence only supports correlation. "Patients with X had outcome Y, so X causes Y."
2. **No confounders considered.** The reasoner does not raise the possibility that some other factor might explain the pattern. The causal interpretation is treated as the only plausible reading.
3. **Sampling bias ignored.** When the substrate has selection effects (e.g., only patients who came for treatment were studied), the reasoner reasons as if the sample were representative of the broader population.
4. **Base-rate neglect.** The reasoner interprets counts without grounding them in a base rate — "we saw this in 39 cases" treated as strong evidence without asking how many cases we'd expect if nothing were going on.
5. **Survivorship bias blindness.** When the substrate describes only the cases that survived or succeeded, the reasoner generalizes to all cases without noting that the failures are missing from the data.

**Red flags** (lower Axis A score regardless of which version):

- **F42 red flag: counterfactual drift into Hypothesis Generation.** If the virtuous passage's "causal reasoning" consists mostly of imagining alternative scenarios ("what if we had done X instead?"), it is reaching into Level-3 counterfactual territory, which per F42 overlaps with Hypothesis Generation. The rubric should check: is the passage actually engaging with Levels 1–2 (correlation/causation, confounders, sampling), or has it drifted into alternative-scenario brainstorming? The latter is cross-concept contamination, not Causal Reasoning.
- **Domain-specific fabricated mechanisms.** The generator may hallucinate specific causal pathways that sound plausible but are not supported by the substrate. Catches on Layer 1.1 factual invariance but should also flag here because the generator reached for technical-sounding causal stories rather than engaging with the substrate's actual evidence.
- **Confusion with Quantitative Groundedness.** Base-rate awareness appears in both concepts. Causal Reasoning's base-rate concern is about *causal inference* ("is this pattern more than we'd expect by chance?"), while Quantitative Groundedness's base-rate concern is about *numerical grounding* ("what is the rate, and does it support the claim?"). Both are legitimate but a Causal Reasoning passage should frame the base rate as a causal question, not just a numerical one.
- **Generic epistemic hedging masquerading as causal reasoning.** Phrases like "correlation doesn't imply causation" or "we should consider alternative explanations" used as verbal tics without engaging with the specific causal structure of the scenario. The virtue requires *specific* confounder identification and *specific* correlational/causal distinctions, not generic cautions.

**§6.8 status: complete.**

### 6.9. Concept 3 — Logical Rigor

**Concept definition** (from concepts.md): Inferential chains are valid, assumptions are surfaced, and the reasoner checks whether conclusions actually follow from premises rather than from plausibility. Absorbs first-principles thinking as a *pragmatic extraction choice* per F28 — philosophically distinct from logical rigor, but merged because they share the same dominant textual signature (stepwise decomposition, explicit assumption-surfacing, validity checking) and separating them at small-model scale is unlikely to produce clean extraction.

**Sub-facets** (from concepts.md):

- Valid inferential chains where each step follows from the previous
- Decomposing complex claims into foundational assumptions
- Identifying hidden premises and checking whether conclusions actually follow

**Positive markers** (virtuous rewrite should contain several of these):

1. **Inference steps individually validated.** The reasoner shows that each inferential step is warranted by the prior one — "if A is true, then B follows because...," "given C, the conclusion D holds only if we also assume E." The chain is not just visible (that is Reasoning Transparency), it is *checked*.
2. **Hidden premises surfaced.** The reasoner identifies unstated assumptions that their reasoning depends on — "this argument assumes that the sample is representative," "we are implicitly taking the measurement at face value." The premises are named, not just implied.
3. **Decomposition to foundational elements.** The reasoner breaks a complex claim into its constituent parts and reasons about each separately. "This is really three claims: that X exists, that it correlates with Y, and that the relationship is meaningful. Let me take them one at a time."
4. **Conclusion-validity check.** The reasoner explicitly asks whether the conclusion follows from the premises, not just whether both happen to be true — "even if the data is correct, does the conclusion I'm drawing actually follow from it, or am I assuming something additional?"
5. **Identifying when a step is invalid even though the conclusion might be correct.** The reasoner flags cases where they think the final answer is probably right but the specific argument they are making for it is weak — distinguishing soundness of reasoning from soundness of conclusion.

**Excess failure markers** (non-virtuous rewrite for the *excess* case — paralysis via over-formalization — should contain several of these):

1. **Logical notation or formalism in plain reasoning.** The reasoner introduces formal logic notation (→, ∀, ∃, "if and only if" as a technical claim) into a scenario where the natural-language reasoning is sufficient. Symbolism used as signal rather than function.
2. **Every premise traced to axiomatic bedrock.** The reasoner insists on justifying assumptions that any competent reader would accept — "but we should ask: what does 'measurement' mean? What does it mean to count?" — making the reasoning unreadable.
3. **Refusal to accept commonsense inferences.** The reasoner treats every inferential step as potentially problematic and refuses to draw reasonable conclusions, reaching for validity-checking on moves that are obviously sound.
4. **Premise-hunting bureaucracy.** The reasoner generates long lists of possible hidden assumptions, many of which are far-fetched, as a way of performing rigor rather than exercising it.
5. **Formal language without formal benefit.** Phrases like "this is logically valid if and only if," "the soundness of this argument requires," "strictly speaking, we must assume" — used repeatedly without the formal machinery actually doing work in the reasoning.

**Deficiency failure markers** (non-virtuous rewrite for the *deficiency* case — sloppy inference — should contain several of these):

1. **Non-sequiturs that go unnoticed.** The reasoner moves from premise to conclusion via leaps that are not warranted, and does not notice or flag the leap.
2. **Hidden assumptions carried unexamined.** The reasoning depends on unstated assumptions that are load-bearing, and the reasoner never names them.
3. **Plausibility substituted for validity.** The reasoner accepts a conclusion because it "makes sense" or "fits the pattern" without checking whether the inferential chain is actually valid given the premises.
4. **Steps collapsed or skipped.** Multiple inferential moves are merged into a single assertion, hiding the intermediate steps where the reasoning might be wrong.
5. **Conflation of soundness and truth.** The reasoner treats a conclusion as established because they believe it, not because the argument establishes it. "This must be right because of X" without checking whether X actually implies it.

**Red flags** (lower Axis A score regardless of which version):

- **F28 red flag: first-principles drift.** Per F28, first-principles thinking and logical rigor are philosophically distinct but merged in our taxonomy for extraction reasons. A passage that almost entirely focuses on questioning inherited framings ("but why should we assume the standard approach?") rather than checking inferential validity is leaning hard on the first-principles side. This is still within the concept's scope, but the rubric scorer should note it and ensure the corpus has a mix — a run of passages that are all first-principles-flavored would produce a vector that is actually first-principles-thinking rather than logical rigor broadly.
- **Confusion with Reasoning Transparency.** Logical Rigor is about whether the inferences are *valid*; Reasoning Transparency is about whether they are *visible*. A passage that shows every step without checking any of them is transparent but not rigorous. Flag cross-concept drift — the virtue requires the *checking*, not just the showing.
- **Confusion with Evidence Grounding.** Logical Rigor operates on the *inferential chain* regardless of where the evidence came from. Evidence Grounding is about tying claims to observations. A passage that carefully grounds every claim in the substrate but does not check whether the inferences from those grounds are valid is high on EG but low on LR.
- **Symbolism as decoration.** If the passage uses logical vocabulary ("modus ponens," "deductively valid," "contrapositive") without the underlying checking actually happening, this is terminology decoration. Penalize — the virtue requires the *work*, not the *vocabulary*.

**§6.9 status: complete.**

### 6.10. Concept 8 — Metacognitive Awareness

**Concept definition** (from concepts.md): The reasoner monitors their own cognitive process as it happens, commenting on what is pulling them toward which conclusions and why. **Deliberately scoped to the monitoring dimension** of Flavell's (1979) metacognitive regulation framework per F27 — planning and evaluating are excluded because planning happens before a reasoning episode begins and evaluating happens after it ends, whereas our extraction passages are short reasoning monologues that capture almost exclusively the monitoring window. Per F10, this concept is kept distinct from Calibrated Confidence: metacognition is *sensitivity* (tracking one's reasoning process), Calibrated Confidence is *bias* (matching language to evidence). The two are empirically separable in the psychology literature.

**Sub-facets** (from concepts.md):

- Explicitly monitoring own reasoning process as it happens
- Distinguishing "I'm drawn to this conclusion" from "the evidence supports this conclusion"
- Flagging when a conclusion feels forced versus when it feels well-supported, independent of how confident the final claim ends up being

**Positive markers** (virtuous rewrite should contain several of these):

1. **In-flight reasoning observation.** The reasoner comments on their own reasoning as it is happening — "I notice I'm starting to build a case for X," "as I work through this, I'm realizing that…" The monitoring is visible in real time, not as a retrospective summary.
2. **Drawn-to vs. supported-by distinction.** The reasoner explicitly separates what pulls them toward a conclusion from what the evidence actually says. "I'm drawn to interpretation X because it's elegant, but the evidence doesn't specifically support elegance over the messier alternative Y." This is the core F10 sensitivity move.
3. **Feeling-forced flag.** The reasoner notes when a reasoning step feels strained or when they are working hard to reach a particular conclusion. "This step feels like a stretch," "I'm having to work to make this fit," "something about this reasoning feels off even though I can't name what."
4. **Noticing heuristic shortcuts.** The reasoner catches themselves using a cognitive shortcut and examines whether the shortcut is warranted. "I'm pattern-matching this to the classic case, but I should check whether the analogy actually holds."
5. **Process-vs-product commentary.** The reasoner distinguishes what they are concluding from how they arrived at the conclusion, and comments on the how separately. "The conclusion I'm reaching is X, but I should note that I got here by working backward from what seemed like a plausible answer."

**Excess failure markers** (non-virtuous rewrite for the *excess* case — rumination / paralysis — should contain several of these):

1. **Recursive self-monitoring.** The reasoner monitors their monitoring, then monitors that — "I'm noticing that I'm noticing that I'm drawn to X, which itself might be a sign that…" — descending into meta-levels that do no analytic work.
2. **Monitoring replaces reasoning.** The reasoner talks extensively about their cognitive process but does not actually engage with the substrate. "I notice I'm uncertain, and I notice that I notice this, and this feels important" — the passage is all monitoring and no object-level reasoning.
3. **Self-doubt spiral.** Every reasoning step is immediately questioned — "but then again, maybe I'm just reaching this because…" — preventing any conclusion from being reached.
4. **Pathologizing normal cognitive moves.** The reasoner treats ordinary, uncontroversial reasoning steps as suspect because they might be biased or heuristic-driven. The result is paralysis dressed as rigor.
5. **Performative introspection.** Phrases like "let me check my own thinking here," "I should be aware of my biases," "I want to monitor myself for" — used as verbal markers of the virtue without actually doing the work those phrases name.

**Deficiency failure markers** (non-virtuous rewrite for the *deficiency* case — unreflective action — should contain several of these):

1. **No commentary on the reasoning process.** The passage is pure object-level reasoning with no observation of how the reasoner is arriving at conclusions. The reasoner never steps back from the content to look at their cognitive moves.
2. **Conflation of "drawn to" and "supported by".** The reasoner treats their intuition about what is true as equivalent to what the evidence says. "X seems right" is treated as if it were "X is supported by the data."
3. **Heuristic shortcuts unexamined.** The reasoner uses pattern-matching, analogy, or gut feel without noticing. These moves are in the reasoning but invisible in the passage.
4. **No flagging of strained steps.** When the reasoning is working hard to fit a pre-formed conclusion, the reasoner does not notice or flag it. The strain is present in the structure of the argument but not acknowledged.
5. **Process opacity.** The reader cannot tell whether the reasoner is aware of their own reasoning at all. The conclusions appear without any visible self-observation.

**Red flags** (lower Axis A score regardless of which version):

- **F10 red flag: sensitivity/bias collapse.** If the Metacognitive Awareness passage reads like a Calibrated Confidence passage (mainly about matching confidence language to evidence), it has drifted into Concept 9 territory. The rubric scorer should check: is the passage about *tracking one's reasoning process* (sensitivity), or about *calibrating confidence markers on the output* (bias)? If the latter dominates, flag cross-concept drift — the extracted vector will be partly Calibrated Confidence rather than pure metacognition.
- **F27 red flag: planning or evaluating drift.** The concept is scoped to monitoring only. If the passage includes extensive *pre-task planning* commentary ("before I start, let me decide on my approach") or *post-task evaluation* ("having finished, I would rate my reasoning as…"), it has drifted outside the monitoring window. Per F27, planning and evaluating are excluded because they do not fit reasoning-monologue passages. Flag and penalize.
- **Confusion with Confirmation Bias Awareness.** CBA is about asymmetric evidence weighing; metacognition is about tracking one's own process regardless of what is being weighed. A passage that focuses on "am I looking at the evidence symmetrically?" is in CBA territory, not metacognition. The specific Axis A markers must involve *self-observation of the reasoning process*, not evidence-handling patterns.
- **Reaching for introspection vocabulary without introspection content.** Phrases like "my thought process," "the way I'm approaching this," "my cognitive stance" — used as labels rather than as descriptions of actual observed cognitive moves. The marker requires the observed move, not just the vocabulary.

**§6.10 status: complete.**

### 6.11. Concept 12 — Steelmanning

**Concept definition** (from concepts.md): Before critiquing an opposing position, the reasoner engages with its strongest form rather than attacking its weakest. Informed by Dennett's four-step framework for charitable argumentation (F22). The concept covers both *accurate reconstruction* (principle of charity — representing the opposing view faithfully) and *strengthening beyond what was originally said* (steelmanning proper). The philosophical literature distinguishes these two operations, but we extract them as one concept because they share the same text-level signature and both are valuable epistemic moves.

**Sub-facets** (from concepts.md):

- Accurately reconstructing the opposing position in its strongest form before engaging with it
- Identifying and acknowledging points of genuine agreement before offering critique
- Engaging with the best available version of a position rather than a weaker strawman
- Ordering engagement such that criticism follows, rather than precedes, the reconstruction

**Positive markers** (virtuous rewrite should contain several of these):

1. **Reconstruction before critique.** The reasoner states the opposing position in their own words, in its strongest form, before any critical engagement begins. The reconstruction is recognizable — a proponent of that position would see themselves in it. Look for sequential structure: "the alternative view holds that… the strongest version of this argument would be… now let me examine where it runs into trouble."
2. **Agreement explicitly identified.** At least one point of genuine agreement with the opposing view is named before criticism. "I accept that the data does show X, which is what the opposing view rests on." Acknowledgment is specific, not a formality.
3. **Best-available-version engagement.** The reasoner engages with a strong form of the counter-argument, not a weakened one. If the substrate suggests multiple versions of an opposing view, the reasoner picks the strongest one to engage with.
4. **Steelmanning beyond the original.** The reasoner adds reasoning to the opposing position that makes it *better* than its naive form — "one could strengthen this argument by also noting Y, which would address the most obvious objection." This is the full steelmanning move, not just the charity move.
5. **Ordered critique.** After the reconstruction and agreement-naming is done, critique follows — not interleaved, not preceding. The passage structure is reconstruction → agreement → critique, as in Dennett's framework.

**Excess failure markers** (non-virtuous rewrite for the *excess* case — credulous acceptance of weak arguments — should contain several of these):

1. **Steelmanning past the breaking point.** The reasoner strengthens the opposing view so aggressively that they end up defending it. The passage becomes an advocacy piece for the opposing position rather than a critical engagement.
2. **False agreement.** The reasoner claims to agree with points they do not actually agree with, as a gesture of intellectual generosity. The agreement is performative rather than substantive.
3. **Credulous acceptance of weak arguments.** A weak argument is treated as if it were strong because the reasoner feels they should take it seriously. The result is that a bad argument is not criticized at all — the opposite failure mode from strawmanning.
4. **Over-charitable reconstruction.** The reasoner reconstructs the opposing view in a form that is so charitable it bears no resemblance to anything a real proponent would hold. "Steelmanning" as fan fiction.
5. **Refusal to critique after reconstruction.** The reasoner does the reconstruction step but then declines to offer any critique at all, treating the exercise as complete once the other side has been represented. Dennett's fourth step (offer criticism) is skipped.

**Deficiency failure markers** (non-virtuous rewrite for the *deficiency* case — strawmanning — should contain several of these):

1. **Weak form of opposing view engaged with.** The reasoner picks the most obviously flawed version of the counter-argument and criticizes that, leaving the stronger versions untouched.
2. **Critique without reconstruction.** The reasoner criticizes the opposing view without first stating what it actually claims. The reader has to infer what is being criticized, and the inference is almost certainly less charitable than the original view deserved.
3. **No acknowledgment of agreement.** Every element of the opposing view is contested, including elements that any reasonable reader would grant. The engagement is adversarial all the way down.
4. **Pejorative framing of the opposing position.** The opposing view is described in loaded terms — "the naive view," "proponents of X foolishly hold…" — that prejudice the reader before the critique begins.
5. **Criticism preceding reconstruction.** When the opposing view is described at all, the description is interleaved with criticism, so the reader never sees what the view is independently of what the reasoner thinks is wrong with it. Dennett's ordering is violated.

**Red flags** (lower Axis A score regardless of which version):

- **F22 red flag: charity vs. steelmanning conflation where it matters.** Per F22, accurate reconstruction (charity) and strengthening-beyond-original (steelmanning proper) are philosophically distinct. Both count for our concept, but a passage that claims to steelman while only doing charity may be under-performing. Check whether the virtuous passage is merely restating the opposing view faithfully, or actively adding reasoning to make it stronger. Both are acceptable, but the rubric scorer should note which the passage is doing so the corpus has both.
- **Strawman disguised as steelman.** The reasoner describes the opposing view in seemingly neutral terms, but the "neutral" description is subtly structured to set up the easiest counter-argument. This is hard to detect automatically but a spot-checker should watch for it — the test is whether a proponent of the opposing view would sign off on the reconstruction.
- **Confusion with Authority Independence.** Both concepts engage with other people's views. Authority Independence is about whether to defer or dissent given the evidence; Steelmanning is about how faithfully you represent the view you are engaging with, regardless of whether you ultimately agree. A passage that focuses on "should I defer to this expert" is in AI territory, not Steelmanning.
- **Confusion with Hypothesis Generation.** A passage that lists multiple competing hypotheses is generating alternatives (Concept 2), not steelmanning. Steelmanning engages with *one specific opposing view* and reconstructs it carefully. Multiple alternatives, each treated briefly, is a different move.

**§6.11 status: complete.**

### 6.12. Concept 11 — Comfort with Ambiguity

**Concept definition** (from concepts.md): The reasoner can sit with unresolved questions without forcing premature closure. Grounded in the inverse of Webster & Kruglanski's (1994) Need for Cognitive Closure Scale (NFCS, F50), targeting specifically the *need-for-structure* axis rather than the *decisiveness* axis (which falls outside our extraction scope per F20).

**Sub-facets** (from concepts.md):

- Holding unresolved questions open rather than forcing a conclusion
- Holding multiple plausible interpretations simultaneously
- Resisting the urge to pick a side when evidence is genuinely balanced

**Positive markers** (virtuous rewrite should contain several of these):

1. **Unresolved questions stated as unresolved.** The reasoner acknowledges that parts of the scenario cannot be settled given the current evidence — "this aspect remains open," "we cannot yet decide between these readings" — without treating the openness as a problem to be hidden.
2. **Multiple interpretations held simultaneously.** The reasoner genuinely entertains two or more readings of the same evidence without collapsing them into one. "This pattern could be explained by X, or equally by Y, and the data does not let us choose between them yet."
3. **Resistance to forced closure where evidence is balanced.** When the substrate presents balanced evidence (say, 39 cases supporting one reading and 8 suggesting another), the reasoner does not artificially resolve the tension by dismissing the smaller group or rationalizing the larger one. The ambiguity is preserved.
4. **Productive use of unresolved questions.** The reasoner treats the open questions as useful — as markers of what further evidence would be needed — rather than as failures of the current analysis. "What this ambiguity tells us is that we need to look at Z to distinguish the readings."
5. **Working conclusions without foreclosing alternatives.** The reasoner may commit to a leading interpretation while explicitly holding the alternatives open. "My working view is X, though Y remains a live possibility I'm not ready to rule out." This is different from refusing to commit — it is committing while preserving the alternatives as genuine.

**Excess failure markers** (non-virtuous rewrite for the *excess* case — indecision, failure to conclude — should contain several of these):

1. **No commitment even when evidence warrants one.** The reasoner refuses to state a leading view on any question, even when the substrate clearly supports one reading more than others.
2. **Every interpretation held equally.** The reasoner treats weak and strong interpretations as equivalent in the name of "keeping options open." The result is indistinguishable from having no view at all.
3. **Ambiguity-seeking on settled matters.** The reasoner manufactures uncertainty where none exists, finding potential alternative readings of evidence that is actually clear.
4. **Closure anxiety.** The reasoner explicitly resists reaching any working conclusion — "I don't want to jump to conclusions," "I shouldn't commit yet" — repeated as a rhetorical move rather than a response to actual ambiguity.
5. **Paralysis framing.** The passage ends without any position, leaving the reader uncertain what the reasoner actually thinks. Every question remains open, including those the evidence could reasonably close.

**Deficiency failure markers** (non-virtuous rewrite for the *deficiency* case — forced premature closure — should contain several of these):

1. **Ambiguity dismissed or ignored.** The fact pack's known-ambiguity element is either not engaged with or is resolved with a quick dismissal ("these are probably just outliers") that does not do justice to the genuine uncertainty.
2. **Single interpretation asserted.** The reasoner picks one reading of the evidence and reasons within it exclusively, never acknowledging that other readings are compatible with the substrate.
3. **Tension smoothed over.** Conflicting elements in the substrate are reconciled too easily — the 8 counter-cases are absorbed into the dominant interpretation without engagement with what they might mean on their own.
4. **Resolution before evidence warrants it.** The reasoner reaches a firm conclusion on a question that the substrate does not settle, closing off the alternatives prematurely.
5. **Treatment of openness as failure.** Unresolved questions are treated as something to be avoided rather than surfaced. The reasoner works to produce the appearance of a settled view even where the evidence is genuinely balanced.

**Red flags** (lower Axis A score regardless of which version):

- **F50 red flag: decisiveness-axis drift.** Per F50, NFCS has two orthogonal factors — need for structure and decisiveness — and we target only the former. A passage whose ambiguity-tolerance failure is about reaching decisions quickly (rather than about tolerating unstructured open questions) has drifted into decisiveness territory, which is out of scope for this concept. Flag and note — the passage may still be usable, but the extracted vector should not mix the two NFCS axes.
- **Confusion with Intellectual Humility.** Humility is about one's stance toward one's own certainty; Comfort with Ambiguity is about one's stance toward the *resolution state* of the question. A passage that hedges confidence markers is humility; a passage that leaves a question genuinely open is ambiguity tolerance. Flag cross-concept drift.
- **Confusion with Hypothesis Generation.** Generating multiple hypotheses is a different move from holding multiple interpretations open after the hypotheses have been produced. Hypothesis Generation is about the space of possibilities; Comfort with Ambiguity is about refusing to collapse that space prematurely. If the passage mostly lists alternatives without engaging the resolution question, it is in HG territory.
- **Performative ambiguity acknowledgment.** Phrases like "this remains unclear," "the picture is mixed" used as verbal tics without actually preserving the ambiguity in the reasoning. The virtue requires the actual unresolved state to be visible in how the conclusions are held, not just announced.

**§6.12 status: complete.**

### 6.13. Concept 1 — Genuine Curiosity

**Concept definition** (from concepts.md): The reasoner is drawn toward understanding for its own sake, not toward confirming a prior belief or reaching a quick answer. Grounded in Need for Cognition (Cacioppo & Petty, 1982, per F17) and refined by Litman & Spielberger's (2003) interest-type (I-EC) and deprivation-type (D-EC) distinction per F53. Our sub-facets span both types by construction: I-EC appears in the pleasure and why-orientation markers, D-EC appears in the unexpected-observations and question-asking markers.

**Sub-facets** (from concepts.md):

- Asking questions to understand rather than to confirm
- Following unexpected observations rather than dismissing them as noise
- Interest in *why* something is true, not just *that* it is true
- Taking evident pleasure in the cognitive work itself, not only in reaching an answer

**Positive markers** (virtuous rewrite should contain several of these):

1. **Understanding-oriented questions.** The reasoner asks questions whose purpose is to understand the phenomenon better, not to confirm a prior belief or to reach a quick answer. "What's going on with these 8 cases?" oriented at genuine understanding, not as a rhetorical setup.
2. **Unexpected observations followed, not dismissed.** When the substrate presents something surprising, the reasoner engages with it as interesting rather than as noise. "That's unexpected — let me think about what could be going on there" is the signature move.
3. **Interest in mechanism.** The reasoner goes beyond *that* something is true to ask *why* it is true. Looking for mechanisms, underlying structure, or the principle behind a pattern.
4. **Visible pleasure in the cognitive work.** The reasoner's language signals that they find the reasoning process itself rewarding — not just the answer. "This is an interesting puzzle," "I find myself wanting to dig further into this," "the pattern here is satisfying to work through." This is the I-EC / NFC effort-enjoyment dimension.
5. **Exploration beyond the minimum.** The reasoner engages with aspects of the scenario that are not strictly necessary for reaching a conclusion — poking at interesting side-questions, following tangents that the substrate suggests. The exploration is disciplined, but the disposition is clearly toward understanding the full picture rather than the minimum needed.

**Excess failure markers** (non-virtuous rewrite for the *excess* case — compulsive distractibility / curiosity without focus — should contain several of these):

1. **Tangent-chasing past the point of productivity.** The reasoner follows interesting side-questions so far from the core scenario that the actual reasoning task is lost. Every observation triggers a new thread that pulls the reasoning away from the substrate.
2. **Question-generation without commitment.** The reasoner generates interesting questions about the scenario but never commits to any interpretive work. The passage reads as a list of things-to-wonder-about rather than actual reasoning.
3. **Exploration at the cost of the task.** The reasoner is so interested in the scenario broadly that they fail to engage with the specific question the substrate poses.
4. **Over-enthusiasm.** The reasoner's pleasure in the cognitive work is overplayed — "how fascinating!," "this is such an exciting puzzle!" — used as stylistic markers that feel performative rather than genuine.
5. **Aestheticization of the scenario.** The reasoner treats the reasoning as an aesthetic exercise rather than a substantive engagement with the question, focusing on which aspects are most "beautiful" rather than which are most informative.

**Deficiency failure markers** (non-virtuous rewrite for the *deficiency* case — incuriosity, dogmatism, answer-seeking without understanding — should contain several of these):

1. **Minimum-engagement framing.** The reasoner does the minimum work needed to reach a conclusion and then stops, without engaging with the interesting or surprising aspects of the scenario.
2. **Unexpected observations dismissed.** When the substrate presents a surprising element, the reasoner brushes it aside without engagement. "The 8 counter-cases are probably noise, moving on."
3. **Conclusion-seeking, not understanding.** The reasoner's questions are oriented toward reaching an answer quickly, not toward understanding what is going on. "Is X true?" rather than "Why might X be true, and what would that tell us?"
4. **No interest in mechanism.** The reasoner is satisfied with *that* the pattern exists and does not ask why. Pattern-matching without explanation.
5. **Flat affect toward the cognitive work.** The language signals that the reasoning is a chore to be completed, not an engaging problem. No markers of interest, satisfaction, or exploration beyond what is strictly needed.

**Red flags** (lower Axis A score regardless of which version):

- **F17 red flag: NFC / openness collapse.** Genuine Curiosity overlaps substantially with openness-to-experience in the NFC literature. A passage that reads as generically "open to ideas" without the specific curiosity signature (question-asking, mechanism-seeking, pleasure in cognitive work) is capturing openness rather than curiosity. Flag and distinguish.
- **F53 I-EC / D-EC balance check.** Per F53, our sub-facets span both interest-type and deprivation-type epistemic curiosity. A passage that only shows one type (say, all I-EC pleasure without any D-EC gap-filling) is capturing half the concept. The rubric scorer should note which type dominates so the corpus has both.
- **Confusion with Hypothesis Generation.** Asking "what else could explain this?" can be either concept — it is curiosity when the motivation is wanting to understand, and HG when the motivation is producing the space of explanations before committing. The distinction is fuzzy; flag when it is unclear which the passage is doing.
- **Performative enthusiasm.** Phrases like "how interesting!," "what a fascinating question!" used as stylistic markers without the underlying exploration. The marker requires the actual following-of-the-question, not the announcement of interest.

**§6.13 status: complete.**

### 6.14. Concept 13 — Authority Independence

**Concept definition** (from concepts.md): The reasoner evaluates claims on the evidence behind them rather than on the prestige of their source, and reaches conclusions — whether agreeing or disagreeing with authoritative voices — based on that evidence rather than on social deference. Grounded in the reflective vs. reactive autonomy distinction (Koestner; Worsnip et al. 2025, per F51) and the ETMCQ trust/mistrust/credulity structure (F54). The target is reflective autonomy: the virtuous reasoner avoids both reactive mistrust (contrarian rejection) and epistemic credulity (accepting without checking), landing in the reasoning-from-evidence middle.

**Sub-facets** (from concepts.md):

- Evaluating claims on the evidence behind them rather than on source prestige, and distinguishing evidence-based consensus from mere appeal to authority
- Treating expert disagreement as information rather than as a cue to defer to the higher-status expert
- Appropriately deferring to expert conclusions when the evidence supports doing so (reflective autonomy), distinct from contrarian rejection (reactive autonomy)
- Willingness to reach and state conclusions that disagree with established figures when evidence warrants

**Positive markers** (virtuous rewrite should contain several of these):

1. **Claims evaluated on evidence, not source.** The reasoner engages with the content of a claim separately from who is making it. "Dr. X argues Y, and looking at the actual evidence they cite…" rather than accepting or rejecting based on status.
2. **Appropriate deference when warranted.** When the evidence supports the expert consensus, the reasoner acknowledges it and defers — not grudgingly, but as the reasoning-from-evidence outcome. "The mainstream view is X, and looking at the data, the mainstream view has it right on this."
3. **Appropriate disagreement when warranted.** When the evidence points away from the expert consensus, the reasoner is willing to state the disagreement. "The mainstream view holds X, but the evidence here suggests Y is actually more consistent." Both deference and dissent are live moves.
4. **Expert disagreement treated as information.** When two experts disagree, the reasoner looks at the underlying evidence rather than picking whichever has higher status. The disagreement is data about the uncertainty of the question.
5. **Source-prestige explicitly bracketed.** The reasoner notes when they are bracketing source status to examine the content — "setting aside for a moment who is making this argument, does the argument itself hold up?"

**Excess failure markers** (non-virtuous rewrite for the *excess* case — reactive mistrust / contrarian rejection — should contain several of these):

1. **Rejection of expert consensus regardless of evidence.** The reasoner treats expert consensus as a reason to doubt a claim rather than as information worth weighing. "The mainstream view is X, which should make us suspicious."
2. **Contrarian framing as a default.** The passage reads as if disagreement with authority is virtuous in itself, independent of the evidence.
3. **Conspiratorial undertones.** The reasoner treats expert agreement as evidence of groupthink, institutional pressure, or worse, rather than as one piece of evidence alongside others.
4. **Dismissal of evidence-based consensus.** When the substrate shows that the expert consensus is actually supported by the evidence, the reasoner still treats it as suspect because it is the consensus.
5. **Contrarian self-image.** The reasoner's reasoning is shaped by wanting to reach a non-mainstream conclusion, not by wanting to reach the conclusion the evidence best supports.

**Deficiency failure markers** (non-virtuous rewrite for the *deficiency* case — credulity / uncritical deference — should contain several of these):

1. **Deference without engaging the underlying evidence.** The reasoner accepts an expert claim because of its source, without examining whether the evidence actually supports it. "Dr. X says Y, so Y."
2. **Source prestige substituted for argument.** Claims are treated as stronger because they come from higher-status sources, independent of the evidence.
3. **Expert disagreement treated as a deference cue.** When experts disagree, the reasoner picks the higher-status side without examining the underlying reasons.
4. **Unquestioning acceptance of consensus.** The reasoner treats expert consensus as settling a question, without asking whether the consensus is itself evidence-based.
5. **Inability to state disagreement even when evidence warrants it.** The reasoner cannot bring themselves to contradict the expert view even when the substrate points that way.

**Red flags** (lower Axis A score regardless of which version):

- **F51 / F54 red flag: two-failure-modes imbalance.** Authority Independence has two symmetric failure modes (reactive mistrust and credulity), per F51 and F54. The corpus rotation constraint from generation-guidelines.md §4.3 requires both. A rubric scorer reviewing a run of non-virtuous passages should flag if all or nearly all are one failure mode, because the extracted vector will be asymmetric.
- **Confusion with Intellectual Humility.** Humility is about one's stance toward one's own certainty; Authority Independence is about one's stance toward *sources* of claims. A passage that expresses doubt about the reasoner's own view is humility; a passage that engages with how external authorities should be weighed is Authority Independence.
- **Confusion with Steelmanning.** Steelmanning is about faithful representation of opposing views; Authority Independence is about whether to defer to authoritative voices on a question. A passage that carefully represents an opposing view is steelmanning; a passage that reaches the question of whether to accept that view as-source is Authority Independence.
- **Political framing.** If the passage uses politically-loaded language or frames authority as an ideological category ("the establishment," "the official line"), this introduces content-level confound rather than capturing the disposition. Penalize — the concept should be extractable from scientifically-framed scenarios without political charge.

**§6.14 status: complete.**

### 6.15. Concept 10 — Intellectual Honesty

**Concept definition** (from concepts.md): The reasoner faithfully represents what the evidence shows, including inconvenient results, AND has exercised the epistemic diligence required to know what the evidence actually shows in the first place. Distinct from humility: one can be highly confident and still scrupulously honest. Distinct from Calibrated Confidence in a specific way per F41: honesty requires both *calibration* (matching language to evidence) and *diligence* (actively verifying sources and checking assumptions rather than resting on unchecked beliefs). Grounded in the meta-science literature on questionable research practices (John, Loewenstein, & Prelec, 2012, per F25), which provides a concrete behavioral inventory of dishonesty.

**⚠ Scoring caveat per F14:** Intellectual Honesty has been specifically documented as one of the harder concepts to extract at small model scale. The rubric scorer should expect that this concept may not extract as cleanly as others even under ideal corpus construction. This does not change how passages are scored, but it does mean the rubric scorer should be especially rigorous — marginal scores are more likely to indicate genuine borderline cases here than for concepts with stronger extractability.

**Sub-facets** (from concepts.md):

- Faithfully representing what evidence shows, even when inconvenient
- Not cherry-picking across studies or dependent measures, not inflating effect sizes, not dropping inconvenient results or conditions, not making post-hoc exclusion decisions that favor the preferred conclusion
- Acknowledging when results don't support the preferred interpretation and distinguishing what was genuinely predicted from what was reframed in retrospect
- Exercising epistemic diligence before reporting a belief — verifying sources, checking assumptions, noting what has been investigated versus what is being taken on faith

**Positive markers** (virtuous rewrite should contain several of these):

1. **Inconvenient results reported faithfully.** The reasoner mentions findings from the substrate that go against their preferred interpretation, with the same clarity as the supportive findings. The 8 counter-cases are not smoothed over — they are stated plainly.
2. **QRP-inverse behavior.** The reasoner explicitly avoids the patterns John/Loewenstein/Prelec documented as dishonest: they do not selectively report only the findings that fit, do not drop inconvenient subgroups, do not claim unexpected findings were predicted in advance, do not make post-hoc exclusion decisions.
3. **Distinguishing predicted from observed.** The reasoner explicitly separates what they expected going in from what the substrate actually shows — "I would have predicted X, but the data shows Y, which I need to treat as a genuine finding rather than reframing it as what I meant."
4. **Diligence markers (F41).** The reasoner notes what they have verified vs. what they are taking on faith. "I'm taking the sample-size claim at face value because it's in the source; I haven't independently verified it." Or: "I'm treating this measurement as accurate without knowing the instrument's calibration history." The visibility of the un-checked is a diligence marker.
5. **Acknowledgment of non-supporting results.** When the evidence does not support the preferred interpretation, the reasoner states this directly rather than burying it. "The data doesn't actually show what I initially thought it did."

**Excess failure markers** (non-virtuous rewrite for the *excess* case — compulsive over-disclosure — should contain several of these):

1. **Over-disclosure of irrelevant doubt.** The reasoner discloses every conceivable source of uncertainty, whether load-bearing or not — "I haven't verified the researchers' institutional affiliation, or the exact equipment used, or the software version…" — burying the substantive honesty in noise.
2. **Confession spiral.** The reasoner compulsively lists all the ways they might be wrong, to the point where the actual evidence-based reasoning is drowned out by caveats about the reasoner's limitations.
3. **Honesty as performance.** Phrases like "to be completely honest," "in the spirit of full disclosure" used repeatedly, signaling honesty rather than enacting it.
4. **Over-acknowledgment of trivial non-supporting findings.** The reasoner gives as much weight to minor non-supportive evidence as to major supportive evidence, in the name of "not cherry-picking," but producing a distorted picture of the actual evidence balance.
5. **Diligence theater.** The reasoner lists every assumption they could possibly be making as "unchecked," even ones that are uncontroversially reasonable to take for granted.

**Deficiency failure markers** (non-virtuous rewrite for the *deficiency* case — cherry-picking / misrepresentation — should contain several of these):

1. **Selective reporting.** The reasoner presents only the findings that support the preferred interpretation, omitting or minimizing the ones that don't. The 39 supportive cases get airtime; the 8 counter-cases are barely mentioned or dismissed.
2. **Post-hoc framing.** The reasoner describes the unexpected finding as if it had been predicted, or reframes the preferred interpretation as "what I was arguing all along" when it wasn't.
3. **Diligence invisible or absent.** The reasoner states claims with the same register whether they have verified them or are taking them on faith. There is no visible distinction between checked and unchecked beliefs.
4. **Inflation of effect sizes or confidence.** The reasoner describes a moderate finding as strong, or a tentative claim as settled.
5. **Dropping inconvenient conditions.** The reasoner focuses on a subset of the substrate that supports their view and does not engage with the parts that complicate it.

**Red flags** (lower Axis A score regardless of which version):

- **F14 red flag: scale-sensitive concept.** Per F14, honesty specifically has been documented as hard to extract at small scale. If the rubric scorer is seeing repeatedly marginal scores on this concept's passages, that is consistent with the prior literature rather than with a rubric failure. Do not adjust the rubric in response; the marginal scores are expected and informative.
- **F25 red flag: QRP vocabulary without QRP substance.** A passage that mentions "p-hacking," "cherry-picking," or "HARKing" as vocabulary, without actually depicting or avoiding the specific practices, is reaching for honesty terminology rather than enacting honesty. Penalize — the virtue requires the behavioral move, not the terminology.
- **Confusion with Calibrated Confidence.** Per F41, the two concepts are distinguished by the *diligence* dimension. A passage that matches confidence language to evidence strength but never shows verification behavior is in Calibrated Confidence territory. A passage that shows verification behavior (named what was checked, what wasn't) is in Intellectual Honesty territory. Flag cross-concept drift — if the passage lacks any diligence marker, it is not actually showing honesty.
- **Confusion with Intellectual Humility.** Humility is about self-certainty; honesty is about faithful evidence representation. A passage that expresses doubt about the reasoner's own view is humility; a passage that engages with whether the reasoner is representing the evidence faithfully is honesty. These are easy to confuse but empirically distinct per our taxonomy.
- **Motivated-reasoning overlap (per F48).** Dishonest reasoning and motivated-reasoning-driven confirmation bias share textual signatures. The distinction: motivated reasoning is about *how evidence is weighed*; dishonesty is about *whether evidence is represented faithfully*. A passage that selectively weighs evidence is in Confirmation Bias Awareness / motivated reasoning territory; a passage that selectively reports evidence is in Intellectual Honesty territory. Subtle but real.

**§6.15 status: complete. ALL 15 concepts rubric items now complete.**

**§6 status: complete.** All per-concept rubric tables are filled in. The LLM-as-judge prompt template in §4.1 can now draw from §§6.1–6.15 for the `{{positive_behavioral_markers}}` and `{{failure_mode_markers}}` substitution fields on any concept.
- Concept 2 — Hypothesis Generation
- Concept 6 — Intellectual Humility
- Concept 7 — Confirmation Bias Awareness
- Concept 5 — Quantitative Groundedness
- Concept 4 — Causal Reasoning
- Concept 3 — Logical Rigor
- Concept 8 — Metacognitive Awareness
- Concept 12 — Steelmanning
- Concept 11 — Comfort with Ambiguity
- Concept 1 — Genuine Curiosity
- Concept 13 — Authority Independence
- Concept 10 — Intellectual Honesty

---

## 7. Automatic rejection criteria (pre-rubric fast path)

Before the Layer 1 checks and the LLM-as-judge pass run, a lightweight pre-screener (per generation-guidelines.md §7.4) catches the highest-frequency runtime artifacts by regex. Triplets that fail pre-screening are rejected immediately without consuming verifier budget.

Pre-screener patterns (reproduced here for reference; the canonical list is in generation-guidelines.md §7.4):

- Opening framing phrases at start of passage
- Closing framing phrases at end of passage
- Bold header markers at any line start
- Bullet-only output
- Role tags (system/user/assistant) anywhere

Pre-screen failures map to §4.9 rejection handling in generation-guidelines.md as Check 4 failures.

---

## 8. Edge cases and known ambiguities

This section enumerates edge cases the rubric scorers are likely to encounter and specifies a decision rule for each. Organized by the category of ambiguity they raise.

### 8.1. Scoring ambiguities (Layer 2 axis interactions)

**E1 — High Axis A, low Axis B (e.g., 4/2).** The passage exhibits the target disposition clearly but has dropped a factual substrate element or drifted in structure. **Rule:** reject. The ≥3-on-both-axes rule is non-negotiable because the extracted vector needs both signal and content fidelity. There is no salvage path — do not retain the high-Axis-A content for later use, because a passage with broken content preservation will distort the difference-of-means calculation regardless of how good the style capture is.

**E2 — Low Axis A, high Axis B (e.g., 2/5).** The passage preserves content perfectly but the disposition is only nominally present. **Rule:** send to `corpus/triplets-weak/` per §4.9 Check 3 handling if Axis A = 2, reject and regenerate if Axis A = 1. The ablation studies on the weak triplet pool will tell us whether keeping these improves or hurts extraction.

**E3 — Borderline scores between 3 and 4.** The rubric scorer is uncertain whether the passage scores 3 (acceptable) or 4 (good). **Rule:** default to 3. The acceptance threshold is ≥3 on both axes, so the distinction between 3 and 4 does not affect accept/reject decisions. Only distinguish carefully when the decision is 3-vs-2 (borderline accept/reject).

### 8.2. Golden-mean violations in the virtuous rewrite

**E4 — Virtuous passage accidentally depicts the excess failure mode.** A passage intended to be virtuous humility reads as servile; a passage intended to be virtuous curiosity reads as compulsive distractibility. **Rule:** reject — per §4.3 golden-mean principle, the virtue is the middle, not either extreme. The excess-direction content cannot be repurposed as an "excess failure" non-virtuous passage either, because it was generated by the virtuous prompt and carries the structural signature of that prompt. Regenerate from the same neutral baseline with a sharper disposition instruction.

**E5 — Virtuous passage accidentally depicts the deficiency failure mode.** Same structure as E4 but in the opposite direction — a passage intended to be virtuous Calibrated Confidence reads as overconfident bluster. **Rule:** same as E4. Reject and regenerate.

**E6 — Non-virtuous passage with mixed failure modes.** The non-virtuous rewrite is supposed to depict *one* failure mode (excess OR deficiency), but the generated passage drifts between both. **Rule:** reject — per §4.3, rotation requires clean failure-mode commitment. A mixed failure-mode passage produces a muddy difference vector because the two directions partially cancel. Regenerate with explicit failure-mode guidance in the prompt.

### 8.3. Correctness-confound interaction

**E7 — Correctness-confound override produced a conclusion the reviewer can't verify.** The override asked for a "virtuous-but-wrong" passage, and the factual wrongness of the conclusion is in a domain the reviewer doesn't know well enough to verify independently. **Rule:** trust the fact pack's conclusion space labels. The fact-pack curator is the authority on which conclusion is correct vs. incorrect, and the reviewer does not need to re-verify — they need to check whether the passage's conclusion *matches* what the fact pack said the override would produce. This is a bookkeeping check, not a factual check.

**E8 — The virtuous passage landed on the "wrong" conclusion when the correctness-confound override was not assigned.** The passage reached a factually incorrect conclusion despite the curator not having asked for the virtuous-wrong override. **Rule:** this is a generator drift, not a virtue failure. Check whether the disposition is still clearly present (Axis A) — if yes, flag the passage as a potential virtuous-wrong candidate and escalate to the curator to decide whether to (a) re-label this triplet as a virtuous-wrong override or (b) regenerate for the originally intended non-override version. Do not silently accept or silently reject.

### 8.4. Cross-concept drift

**E9 — Passage targeting Concept X reads as Concept Y.** The virtuous rewrite for, say, Intellectual Humility reads mostly as Confirmation Bias Awareness. **Rule:** reject on Axis A (score < 3 for the intended concept). The concept-specific markers in §6 are the authority — if the passage hits markers for a different concept instead of the target, it has failed Axis A regardless of overall quality. Per F40, closely correlated concepts (humility ↔ open-mindedness, metacognition ↔ calibrated confidence) are particularly prone to this drift.

**E10 — Passage legitimately hits markers for multiple concepts.** Some passages genuinely exhibit multiple epistemic virtues at once — e.g., a reasoner who demonstrates both careful evidence grounding and hypothesis generation in the same passage. **Rule:** score Axis A against the *target concept only*. The passage can be excellent at Concept Y while still scoring a 3 on Concept X if Concept X's markers are weaker. Do not average across the concepts — the target concept is the one the triplet is for, and that is what the score should reflect.

### 8.5. Stylistic and non-content issues

**E11 — Technically correct but stylistically awkward passage.** The passage hits all rubric items but the prose is clunky or unnatural. **Rule:** do not reject on stylistic grounds alone. The rubric scores what the passage *does*, not how gracefully it reads. Reject only if the awkwardness actually degrades the disposition signal (i.e., the disposition becomes harder to recognize because of the awkwardness).

**E12 — Passage uses domain jargon the reviewer doesn't understand.** The scenario is from a domain (say, chemistry synthesis) where the reviewer lacks expertise to fully evaluate whether the technical claims are substantively right. **Rule:** score on the disposition markers that are domain-independent (hedging, evidence-citing, uncertainty engagement) and trust the factual invariance check (Layer 1.1) to catch substrate violations. The reviewer does not need to be a domain expert to score Axis A.

**E13 — Passage is too short or too long relative to the baseline.** The ±10% length tolerance was violated. **Rule:** this is a Layer 1.2 failure, not a Layer 2 scoring decision. Route to §4.9 rejection handling regardless of how good the content is.

**E14 — Passage contains hedged language in the virtuous version that matches the corpus-level hedging pattern.** A Calibrated Confidence virtuous passage uses hedge words naturally; the same passage in the Intellectual Humility corpus would read as virtuous humility because the markers overlap. **Rule:** check the specific sub-facet targeted by the triplet. If the triplet is for Calibrated Confidence, score against the differentiated-confidence markers from §6.1. If it is for Intellectual Humility, score against the self-certainty-doubt markers from §6.5. Shared surface markers do not mean the passage serves either concept equally — the specific markers are what distinguish them.

### 8.6. Handling new edge cases discovered during pilot

This section is **append-only during the pilot** operation. When the curator or reviewer encounters an edge case not covered above, they:

1. Add a new entry (`E<next-number>`) to the appropriate subsection, with the same structure (description + decision rule).
2. Note the fact-pack ID and triplet ID where the edge case was first seen, for later reference.
3. If the edge case suggests a rubric rule change rather than just an edge-case addition, flag it in `corpus/review-logs/rubric-revisions.log` for curator review — do not silently edit the scoring anchors in §3 or the concept markers in §6 based on a single case.

After the pilot is complete, this section may be reorganized and condensed — but during the pilot, append-only is the rule to preserve the audit trail of how edge cases were discovered and resolved.

**§8 status: complete.**

---

## Document status

**review-rubric.md is now draft-complete.** All sections filled in:

- §1 purpose and scope ✓
- §2 rubric architecture (three layers) ✓
- §3 scale anchors for Axis A and Axis B ✓
- §4 LLM-as-judge prompt template ✓
- §5 human spot-check protocol ✓
- §6 per-concept rubric items (all 15 concepts) ✓
- §7 automatic rejection criteria ✓
- §8 edge cases and known ambiguities ✓

**Phase 3 progress:**
- ✓ generation-guidelines.md draft-complete
- ✓ review-rubric.md draft-complete (as of this cycle)
- ⏸ examples/humility-example-01.md — next

The worked example is the final Phase 3 artifact. After it is drafted, the cron reports "Phase 3 artifacts complete, awaiting user review" and stops advancing.

---

## 9. Document status and next steps

- **Created:** Phase 3 cycle 33 (2026-04-09).
- **Structure:** Skeleton with section headers, rubric architecture (Layer 1 / Layer 2 / Layer 3), scale anchors for Axis A and Axis B, placeholder for LLM-as-judge prompt, working defaults for human spot-check protocol, and TODO markers for the concept-specific rubric items and the LLM-as-judge prompt template.
- **Next steps:** Subsequent Phase 3 cycles fill in TODOs. Priority: LLM-as-judge prompt template, then Concept 9 (Calibrated Confidence — pilot) rubric items, then the rest of the F11 highest-likelihood tier, then Medium tier concepts, then edge cases.
- **Length target:** Under ~500 lines (current draft is well within).
- **Relationship to generation-guidelines.md:** this document is the *scoring* companion; generation-guidelines.md is the *pipeline* companion. A curator needs both.
