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
