# SAE/Transcoder feature catalog

A registry of specific SAE / transcoder features we've investigated across the models we work on. Long-lived, accumulating. Each feature gets a structured entry with hand-judged content.

When you investigate a new feature: add an entry here. When you use a feature in a steering experiment: update its status here. When another doc references "feature 24983 on qwen3-4b L17," they should link here for the detail.

---

## How to read this doc

### Triage tiers

- **Tier 1 — clean primary candidate.** Top activations are consistently on-concept. Density in the useful range (0.001–0.5%). No major contamination. Usable for steering experiments.
- **Tier 2 — different mechanism / partial match.** Real feature but not exactly the concept we wanted. Useful for separate hypothesis tests.
- **Tier 3 — wrong tool.** Label is misleading vs. what the feature actually fires on. Documented to avoid re-investigating.
- **untriaged** — entry exists but hasn't been hand-graded yet.

### What goes in each entry

- Header: `### MODEL · L<layer> · <source> · <index>`
- Auto label (the gemini-2.0-flash explanation Neuronpedia shows by default)
- Activation density and max activation
- What it actually fires on — *hand-judged* description from reading 5-10 top activations
- Top examples — 3-5 quoted snippets that illustrate the feature
- Logits direction (positive/negative — which tokens it boosts/suppresses)
- Notes — caveats, contamination, surprises
- Status — what we've done with this feature
- Triage tier

### Format for top examples

`max_activation_value` | `quoted snippet (≤80 chars)`

---

## qwen3-4b · L17 · transcoders-hp

**Source details:** Hanna & Piotrowski Circuit Tracer Transcoders (`transcoders-hp`). 163,840 features. Hook point: `blocks.17.mlp.hook_in`. Architecture: transcoder (predicts MLP output from MLP input). Weights: `mwhanna/qwen3-4b-transcoders/layer_17.safetensors` on HuggingFace. Activation dataset: `monology/pile-uncopyrighted`.

### qwen3-4b · L17 · transcoders-hp · 24983 — "certainty and uncertainty"

- **Density:** 0.148%
- **Max activation:** 11.31
- **What it actually fires on:** First-person epistemic uncertainty across many phrasings — "I'm not sure / I'm not certain / it is unclear / we are still unsure / I am uncertain." This is the richest mix of uncertainty markers we've found at L17.
- **Top examples:**
  - 11.31 | "It's unclear whether these calls were made accidentally"
  - 10.38 | "Synchronized statement, unclear java doc example"
  - 9.56 | "I'm not sure how to go about reviewing it"
  - 9.06 | "he isn't sure whether his ex"
  - 8.63 | "I am unsure of your question"
  - 8.13 | "I'm not certain of GE's willingness to give"
- **Logits:** Negative includes "ophe / udy / DJs / 学习"; positive includes "属于 / belonged / again / tenant" — multilingual + irregular, somewhat noisy
- **Notes:** Density slightly higher than ideal (0.148% vs preferred <0.05%) — feature fires fairly often. But top activations are extremely clean. Likely the **strongest steering candidate** for first-person epistemic uncertainty.
- **Status:** investigated 2026-05-09, on shortlist for steering experiment (`docs/sae-experiment-plan.md`)
- **Triage tier:** 1

### qwen3-4b · L17 · transcoders-hp · 44526 — "(un)certainty"

- **Density:** 0.010%
- **Max activation:** 10.50
- **What it actually fires on:** First-person "I'm unsure / I'm not sure / If you're not sure" — same epistemic-uncertainty concept as 24983 but sparser and more selective.
- **Top examples:**
  - 10.50 | "If you are unsure if an image or content is copyright protected"
  - 10.13 | "If you are not sure, please compare on another display"
  - 9.88 | "If you're not sure about how to do this"
  - 5.06 | "you are unsure about a specific medicine"
  - 3.48 | "I am unsure of your question"
- **Logits:** Negative includes "anking / blogging / Dietary / Billboard / Guinness" (oddly specific); positive includes "另一半 / isoft / icine" (Chinese + fragments)
- **Notes:** Cleaner and sparser than 24983. Use as **confirmation** in the steering experiment — if both 24983 and 44526 produce abstention, the result is more robust than one feature alone.
- **Status:** investigated 2026-05-09, on shortlist
- **Triage tier:** 1

### qwen3-4b · L17 · transcoders-hp · 131926 — "questions/uncertainty"

- **Density:** 0.012%
- **Max activation:** 10.94
- **What it actually fires on:** The literal "I don't know" / "I don't remember" / "depth level is unknown" pattern. Fires hard on canonical knowledge-gap statements.
- **Top examples:**
  - 10.94 | "I don't know, like a port cullis or something"
  - 7.59 | "I don't remember what kind of literature we were reading"
  - 6.56 | "I don't know why I was hesitant"
  - 6.19 | "I don't know why there can't be a more composed way"
  - 5.78 | "I don't know how to speak about this kind of loss"
- **Logits:** Negative includes "即 / .constructor / Scheme"; positive includes ".opend / fen / tps / 分明"
- **Notes:** **Mild code-context contamination** — ~25% of top activations are Python/Java programmer-name fragments ("Han Zichi", "Liu chao", "Lajos Molnár", "test $"). These appear in code comments where the author admits uncertainty about an issue. Probably won't break steering but worth noting.
- **Status:** investigated 2026-05-09, on shortlist
- **Triage tier:** 1

### qwen3-4b · L17 · transcoders-hp · 29010 — "hedging or uncertainty"

- **Density:** 0.016%
- **Max activation:** 10.75
- **What it actually fires on:** Conversational self-correction / mid-thought hedging. "Or maybe / Well, actually / Wait, no / Or rather / Ok, maybe a little later." This is *not* the same as epistemic uncertainty — it's the "second-guess yourself in the middle of a sentence" pattern.
- **Top examples:**
  - 10.75 | "Or maybe they did, but not like this"
  - 10.63 | "Well, maybe only a couple of firsts"
  - 10.00 | "Actually that's not true. Getting around Manhattan is a nightmare"
  - 9.19 | "Okay, not really lost, just unable to find"
  - 8.88 | "Wait, no it doesn't"
- **Logits:** Negative includes "blows / Optional / 转折"; positive includes "财 / Each / esters / clustered"
- **Notes:** Different mechanism from 24983/44526. Worth testing as a separate hypothesis: *does hedge-promotion break confabulation flow without producing abstention?* If so, it's a distinct intervention (the "wait, actually..." rail) from "humility" steering. Could be more or less effective than direct uncertainty depending on the prompt.
- **Status:** investigated 2026-05-09, on shortlist for separate test
- **Triage tier:** 2

### qwen3-4b · L17 · transcoders-hp · 70419 — "Uncertainty" (mislabeled)

- **Density:** 0.058%
- **Max activation:** 9.44
- **What it actually fires on:** **World-uncertainty, NOT epistemic uncertainty.** Text discussing uncertain topics — "policy uncertainty," "economic uncertainty," "Covid-19 uncertainty," "unpredictable weather/policy."
- **Top examples:**
  - 9.44 | "uncertainty surrounding [crypto-addresses]"
  - 8.13 | "the impact of continued uncertainty and volatility in global economic conditions"
  - 7.94 | "Given the current uncertainty from Covid-19"
  - 6.84 | "the unpredictable nature of Russian foreign policy"
- **Logits:** Negative includes "威胁 / phabet / junior"; positive "斡 / 把这个 / 续 / 缬"
- **Notes:** **Cautionary tale.** The auto-label "Uncertainty" sounds like exactly what we want, but reading the top activations shows the feature fires on *text about* uncertainty (as a topic in the world), not on *first-person* uncertainty. Steering on this would probably make the model talk *about* uncertainty more (e.g., "the heaviest pumpkin is uncertain due to volatile global conditions") without actually abstaining. Demoted from initial pre-PDF ranking.
- **Status:** investigated 2026-05-09, REJECTED for steering experiment
- **Triage tier:** 3

---

## Reserved sections (will populate as catalog grows)

### qwen3-4b · L17 · transcoders-hp — additional features

(8 more searches planned — see `docs/sae-experiment-plan.md`. Add Tier-1+ candidates here as they're triaged.)

### qwen3-4b · L7 / L9 / L15 · transcoders-hp

Possible exploration if Layer 17 yields nothing usable. L7 = where v_EG was extracted (evidence-grounding angle); L9 = v_CC (commitment angle); L15 = v_RT (rigorous-thinking angle).

### Other transcoder layers (qwen3-4b)

To enumerate from Neuronpedia source dropdown.

### Other models (gemma-2-2b, llama3.1-8b, deepseek-r1-distill-llama-8b, etc.)

Goodfire Ember has SAEs for some of these. Neuronpedia has Gemma-2-2B, Llama-3.1-8B variants, DeepSeek-R1-Distill-Llama-8B. Section per (model, source, layer) will be added as we explore.

---

## Cross-references

- `docs/sae-experiment-plan.md` — the active SAE experiment thread that uses these features
- `docs/findings.md` F113 — top-level finding referring to this catalog
- `~/Downloads/NP/*.pdf` — exported feature dashboards and search-result pages from Neuronpedia
- F111 (`findings.md`) — IH-vector falsification that the steering experiment with these features is designed to test

---

## qwen3-4b · L17 · transcoders-hp — additional features (2026-05-09 second-round triage)

After 18 additional searches ("I'm not familiar," "approximately," "speculative," "outside my knowledge," "beyond my knowledge," "as far as I know," "anecdotal," "without evidence," "unverified," "need to verify," "need to make sure," "humility," "need to learn," "need to look for knowledge," "needUnderstand," "shuldask," "confidently," "definitively"), 5 sub-agents triaged the PDFs in parallel. Results below.

**Bottom line:** 4 new Tier-1 candidates, ~18 Tier-2, several Tier-3 cautionary. No clean opposite-axis (commit) feature found. Multi-word phrase searches systematically fail.

### qwen3-4b · L17 · transcoders-hp · 101568 — "Expressing uncertainty/limitations"

- **Density:** not visible in search PDF — verify on feature page
- **Max activation:** 8.13
- **What it actually fires on:** First-person epistemic limitation admission — "I am not one for statistics I must confess" — speaker explicitly limiting their own authority before making a statement.
- **Top examples:**
  - 8.13 | "I am not one for statistics I must confess, but as I have mentioned in many other"
  - (other top 3 activations all show the same sentence — possible top-k dominated by one document)
- **Logits:** Positive: "層出 / FXMLLoader / 妥 / nten / region"; negative: "iband / oids / 说什么 / like / distinguished"
- **Notes:** Appeared in BOTH "outside my knowledge" AND "beyond my knowledge" searches — consistent semantic match. The "I must confess" phrasing is structurally a first-person epistemic-humility marker. **Caveat:** identical example × 3 in top activations could mean single document dominates; needs density check on feature page before committing to steering.
- **Status:** investigated 2026-05-09, **needs density verification** before adding to steering shortlist
- **Triage tier:** 1 (tentative, pending density)

### qwen3-4b · L17 · transcoders-hp · 27191 — "approximation"

- **Density:** not stated in PDF
- **Max activation:** 11.94
- **What it actually fires on:** "Approximation" as imprecise-substitute concept in technical/explanatory prose. The model output stands in for precision when precision isn't available.
- **Top examples:**
  - 11.94 | "these systems attempt to provide an approximation of video on demand"
  - ~9 | "An estimation for an appropriate end time for an intra-operative"
  - ~7 | "Good static analysis tools form estimates of the contents of pointer"
- **Logits:** Positive: "ISED / Dover / .cls / Cloth / quat" — mixed
- **Notes:** Number-hedging axis. Not first-person epistemic uncertainty. But conceptually related: "approximation" implies "I can't give you the exact thing." Steering could produce hedged numerical answers like "approximately 1500 kg" instead of "exactly 2463 kg" on E1. Different intervention than humility but potentially useful for confabulation prompts where the model would otherwise pick a fake specific number.
- **Status:** investigated 2026-05-09, on candidate shortlist
- **Triage tier:** 1

### qwen3-4b · L17 · transcoders-hp · 115297 — "approximations"

- **Density:** not stated
- **Max activation:** 7.94
- **What it actually fires on:** The word "approximately" in factual prose introducing approximate quantities — "approximately one percent."
- **Top examples:**
  - 7.94 | "use at the time of delivery in California is approximately one percent"
  - lower | "a subsidiary of Ralcorp that currently employs about 280 workers at the Oldham"
- **Notes:** Sister feature to 27191. More directly tied to the word "approximately" as a hedging marker before a number. Pair with 27191 for number-hedging steering.
- **Status:** investigated 2026-05-09, on candidate shortlist
- **Triage tier:** 1

### qwen3-4b · L17 · transcoders-hp · 161931 — "Checklists and verification"

- **Density:** not stated
- **Max activation:** 6.78
- **What it actually fires on:** Instructional text directing the reader to self-check their work — "Use the checklist below to verify you have followed the instructions correctly."
- **Top examples:**
  - 6.78 | "Use the checklist below to verify you have followed the instructions correctly. ## Checklist"
  - (3× identical example shown — same caveat as 101568)
- **Logits:** **Strongly suppresses** "already" (-0.30) and "已有" (-0.30, Chinese "already exists"); **strongly promotes** "missing" (+0.32), "missed" (+0.31), "Missing" (+0.30), "遗漏" (+0.29, Chinese "omission/missed"). This logit signature is unusually clean: the feature is about **checking for what is missing or omitted**.
- **Notes:** Verification-disposition axis. Different mechanism than humility (24983 etc.) — steering with this should produce "let me verify before I commit" behavior, not "I don't know." Could be useful as a complementary intervention to humility steering. **Caveat:** 3× repeated example, density unverified.
- **Status:** investigated 2026-05-09, on candidate shortlist (verify density)
- **Triage tier:** 1 (tentative)

### Tier 2 candidates (new)

Compact entries — full activation logs in agent reports if needed later.

- **29654** "beyond" (max 15.06) — top activation "beyond the scope of my knowledge" but contaminated by spatial "beyond" (walls, virtual worlds). Tier 2 because the literal phrase fires hard but the feature is broader.
- **15911** "knowledge" / "to our knowledge" (max 12.50) — academic epistemic-qualification phrase ("to our knowledge, this is the first X"). First-person collective hedging in research contexts. Useful for hedged affirmative claims (not abstention).
- **80** "believed" / "is believed to" (max 13.31) — passive epistemic hedge in encyclopedia/science prose ("ASD is believed to impact 1 in 10 people"). Cleanly third-person passive voice.
- **109839** "uncertainty/disagreement" / "certainly" (max 5.56) — internally split feature, one example is "I suspect (- with no hard evidence to back that up!)" which is on-target, others are "certainly will recommend" (anti-target). Worth checking whether negative-α steering surfaces the on-target side.
- **114750** "perhaps/maybe" (max 18.13) — rhetorical softener for advice/recommendations ("Perhaps the most common solution"). High max, useful for mild-hedging steering.
- **59639** "hypothesis" / "the hypothesis that" (max 12.19) — academic register epistemic tentativeness ("test the hypothesis that 17β-estradiol does X"). Clinical research context.
- **19308** "assumption" (max 8.63) — argumentative methodology language ("change the assumptions to get the result you want"). Methodological skepticism adjacent.
- **110169** "alleged/suggested diagnosis" (max 7.00) — clinical evidence-quality flagging in case reports. Narrow domain but real evidence-flagging.
- **42370** "correctly" (max 4.41) — same checklist-verification cluster as 161931 but weaker.
- **123838** "Certainty" / "-ively" suffix (max 10.19) — appears in BOTH confidently and definitively searches. Fires on the "-ively" morpheme in "definitively." Mixed contexts (interrogative + medical). Not a clean commit feature.
- **63583** "answering affirmatively" / "Yes, it is legal" (max 7.53) — Q&A format affirmative answers. Negative logits include "不一定" (Chinese "not necessarily") — feature suppresses hedging. Narrow Q&A register.
- **53054** "define" / "I define X as Y" (max 16.38) — first-person definitional commitment, different subtype from assertive commitment. Could be tested as a "definitional rail" steering.
- **6900** "Asking questions" / "I want to ask experienced programmers" (max 4.38) — first-person knowledge-gap action ("It's no shame to ask"). Weak max but on-target conceptually.
- **131448** "needing information, not knowing" / "hard to answer without more information" (max 3.94) — first-person info-insufficiency. Below threshold but conceptually closest to action-disposition humility.
- **136512** "understanding and interpretation" / "if I understood this correctly" (max 6.78) — first-person hedged interpretation marker.
- **146191** "seek for any evidence, correct errors" (max 18.75) — epistemic vigilance disposition. Top activation is descriptive ("sought to doubt any assertion, to seek for any evidence, to correct any errors"). Not quite first-person.
- **160623** "lack of knowledge" / "wholly ignorant" (max 4.38) — Socratic inquiry framing. Weak.
- **69694** "must" / "I must admit" (max 21.50) — broad deontic/necessity feature, but examples include "I must have made some misconceptions" and "I must admit." On-target examples contaminated by all "must" senses.

### Tier 3 cautionary (instructive cases worth recording)

- **102685** "missing or unknown information" — world-uncertainty type ("it was unclear whether drowning was accidental"). Same off-target class as rejected 70419.
- **77462** "certainty" — "Nothing is known with certainty about the play's origin" — world-uncertainty in historical/factual contexts.
- **101986** "without" (max 24.25!) — generic grammatical "without [X]" feature. Highest max-act in the "without evidence" search but pure syntax. **Lesson: multi-word phrase searches don't work — Neuronpedia matches on individual tokens.**
- **17291 / 6609 / 148167** "placebo" (max 18, 10.88, 10.56) — clinical RCT methodology cluster. Search drift on "without evidence" → clinical-trial-quality features. Not target.
- **138882** "-oric" morpheme — fires on "metaphoric" because of suffix match with "speculative." **Lesson: morphological matches happen.**
- **152087** "-atically" morpheme — fires on "fanatically" because of suffix match with "approximately." Same lesson.
- **4069 / 38366** "certain" (max 18.13, 11.00) — fires on quantifier sense ("a certain X") not epistemic certainty. Polysemy trap.
- **religious-virtue cluster** in humility search (60504, 5658, 120084, 4655, 68038, 33423, 36573, 86378) — all "religion" features in Christian theology contexts. Confirms humility-as-virtue is encoded as religious-discourse, not as a model-disposition.
- **20431** "need" (max 21.00) — generic "need" verb token. Fires everywhere. Cautionary for "need to X" searches.

### Pattern observations from second-round triage

1. **No clean opposite-axis commit feature found** at L17. The "confidently" + "definitively" searches returned generic adverbs, scientific-register verbs, and a morpheme detector — but no clean first-person "I'm certain that X" feature. The Tier-1 humility features don't have a clean geometric opposite in this transcoder.

2. **Multi-word phrase searches systematically fail.** "Without evidence" → generic "without"; "outside my knowledge" → generic "knowledge" + spatial "beyond"; "as far as I know" → factual-attribution features. Single-word concept searches work better.

3. **Number-hedging axis (27191, 115297) is a new useful direction** distinct from epistemic-uncertainty axis. Could produce "approximately X" hedged answers on confabulation prompts.

4. **Verification-disposition axis (161931) is promising** with an unusually clean logit signature (promotes "missing/missed/omission"). Different intervention than humility — "let me check before committing" rather than "I don't know."

5. **Action-disposition humility doesn't surface as a clean feature** at L17 (features 6900, 131448, 146191 are all weak). May require different layer or different search strategy.

6. **Religious-virtue cluster at L17 is well-developed** — patience, courage, empathy, forgiveness, grace, mercy, honesty, gratitude all have dedicated features. The word "humility" surfaces these rather than any model-disposition feature. Useful background context for other projects but confirms F45 (disposition modulation, not propositional injection) at the SAE-feature level.

