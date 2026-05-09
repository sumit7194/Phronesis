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

### Other models — Neuronpedia coverage map (verified 2026-05-10)

Parsed from the full models-page HTML export at `~/Downloads/NP/QWEN3-4B ｜ Neuronpedia.html`. This is the complete list of (model, source-set) combinations available on Neuronpedia for our project.

#### Our 5 cross-model run subjects × Neuronpedia coverage

| Our model | On Neuronpedia? | Available sources | Notes |
|-----------|-----------------|-------------------|-------|
| **qwen3-4b** | ✅ Yes | `transcoders-hp` (164k features at L17, what we've used), `qwenscope-res-32k`, `qwenscope-res-64k` (Qwen Scope SAEs — residual stream) | Both transcoders AND residual-stream SAEs available! Should investigate Qwen Scope as the natural complement to the transcoder we've been using. |
| **gemma-4-E4B-it** | ⚠️ Closest match: Gemma-3-4B-IT | `gemmascope-2-4b-pt`, `gemmascope-2-res-16k/65k/262k`, `gemmascope-2-transcoder-16k`, attention/MLP variants | Note: "gemma-4" in our naming likely corresponds to Google's "Gemma-3-4B" (Gemma generation 3, 4B params). Worth confirming this mapping before doing comparable searches. |
| **phi-4-mini-reasoning** | ❌ NOT available | — | Microsoft hasn't released SAEs publicly for Phi. No community coverage on Neuronpedia. Cannot do SAE work for this model. |
| **llama-3.1-8B-R1-GRPO** | ⚠️ Base Llama-3.1-8B available, GRPO variant not | `llama-scope` (general), `llama-scope-r1-distill` (R1-distill family), `llamascope-mlp-32k/131k`, `llamascope-res-32k/131k`, `transcoder-llama-131k-adam-kl/mntss` | Base-model SAEs may transfer to R1-GRPO with caveats (different post-training). The `llama-scope-r1-distill` source is specifically for R1-distill models; could be useful since GRPO is a reasoning post-train. |
| **openr1-qwen-7b** (Qwen2.5-7B base) | ✅ Qwen2.5-7B-Instruct available | `saes-qwen2`, `saes_qwen_qwen3-1.7b/8b/14b_batch_top_k`, `llamascope-openr1-res-32k` (likely OpenR1-specific!), `llamascope-slimpj-openr1-res-32k` | The `llamascope-openr1-res-32k` source-set name is intriguing — may be SAEs trained specifically on the OpenR1 family. Worth a closer look. |

#### Bonus models worth investigating

- **DeepSeek-R1-Distill-Llama-8B** ✅ has `llama-scope-r1` SAEs — would be the cleanest cross-family reasoning-model test (same architecture as Llama-3.1-8B base, post-trained as a thinking model)
- **Qwen3-1.7B / 8B / 14B** ✅ all have `saes_qwen_qwen3-*_batch_top_k` — sister models to our qwen3-4b. Could test feature universality across sizes within the Qwen3 family.
- **GPT-OSS-20B** ✅ has SAEs (`saes-gpt-oss-20b`) — large open-weights reasoning model, could be a future generalization target.

#### Source-set glossary

- **transcoders-hp** — Hanna & Piotrowski Circuit Tracer Transcoders (what we've been using on qwen3-4b L17). Trained at MLP-input.
- **gemma-scope / gemmascope-*** — Google's official SAE release for Gemma-2 + Gemma-3. Multiple feature counts (16k/65k/131k/262k), trained at residual stream / MLP / attention.
- **llama-scope / llama-scope-r1 / llama-scope-r1-distill** — OpenMOSS SAE releases for Llama-3 and R1-distill variants.
- **qwen-scope / qwenscope-*** — Alibaba's official SAE release for Qwen3 family. 32k or 64k features, residual stream.
- **saes-qwen2** — Qwen2 SAEs (community).
- **saes-gpt-oss-20b** — GPT-OSS SAEs (community).
- **circuit-tracer** — Anthropic-style circuit-tracing SAEs.
- **sae-bench** — SAEBench-format SAEs (used for evals not steering).

#### Recommended search-and-export plan for the next ~day

User has compute-VM unavailable for ~1 day, will use that time to gather Neuronpedia data. Priority order:

**Tier A — direct comparators to current qwen3-4b L17 work:**

1. **qwen3-4b · qwen-scope (residual stream SAEs)** — same model, different decomposition method. Critical because our transcoder is at MLP-input; the residual-stream SAE is the more natural intervention site for steering. Pick the layer closest to L17 (likely L17 or L18). Run the same 6 priority searches: `expressing uncertainty`, `(un)certainty`, `I don't know`, `approximately`, `verify`, `I'm not familiar`.

2. **Qwen2.5-7B-Instruct · llamascope-openr1-res-32k** — direct match for our **openr1-qwen-7b** cross-model subject. If features look similar to qwen3-4b's, that's evidence for cross-size feature universality within Qwen family. Same 6 priority searches.

**Tier B — cross-family generalization test:**

3. **DeepSeek-R1-Distill-Llama-8B · llama-scope-r1** — non-Qwen reasoning model with SAEs. If a humility feature exists here and looks similar to qwen3-4b's, that's evidence for cross-family universality. If it doesn't exist or looks different, that's evidence for the Qwen-family-specificity hypothesis F112 raised. Same 6 priority searches.

**Tier C — fill in gaps:**

4. **Gemma-3-4B-IT · gemmascope-2-res-16k** — closest match for our gemma-4-E4B-it cross-model subject. Test whether F102's "gemma is null" finding has an SAE-level explanation (no humility features → no behavioral effect). Same 6 priority searches.

5. **Llama-3.1-8B · llama-scope-r1-distill** — base llama with R1-distill SAEs. Tests whether the GRPO post-training in our llama-3.1-8B-R1-GRPO subject changes which features exist.

#### Tightened search list for these 5 models (use across all of them)

Based on what worked on qwen3-4b L17, the tightened single-word concept searches:

1. `expressing uncertainty` (yielded 24983, 70419 on qwen)
2. `(un)certainty` (yielded 44526)
3. `I don't know` — single phrase but no quotes (yielded 131926)
4. `approximately` (yielded 115297, 27191)
5. `I'm not familiar` (yielded 101568 on qwen)
6. `verify` (yielded 161931)

Skip the failed multi-word phrase searches (`outside my knowledge`, `without evidence`, etc.) — they returned generic syntax features. Skip "humility" (returns religious-virtue cluster). Skip "speculative" / "anecdotal" (no signal).

If a search yields a clean Tier-1 candidate on a model, also pull the dashboard for that feature index. That's the data we'll bring to the VM for steering experiments.

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

- **Density:** **0.026%** ✓ (verified 2026-05-10 from feature page)
- **Max activation:** 8.13
- **What it actually fires on:** **First-person epistemic-limitation admission** — speaker explicitly admitting they are not an expert / are inexperienced / have limited knowledge before making (or refusing to make) a claim. Single-document concern from search PDF is RESOLVED — feature page shows 24+ diverse activations across many distinct documents.
- **Top examples (broader set from feature page):**
  - 8.13 | "I am not one for statistics I must confess"
  - 7.88 | "I'm no expert on the physics involved. There's lots of hand waving going on here"
  - 7.78 | "Let me start by explaining just how much of an inexperienced programmer I am"
  - 6.84 | "I didn't really use Illustrator before, but i'm having troubles"
  - 6.50 | "I am by no means a DBA, I would like to learn"
  - 6.38 | "I don't know anything about Objective-C so I wonder how simple"
  - 5.91 | "I am no skating devotee"
  - 5.75 | "[Note: I am not programming expert]"
  - 5.66 | "my C knowledge is very very limited"
  - 5.50 | "My linux scripting skills are poor so I'm hoping someone can help"
  - 5.31 | "I've been an avid watcher (not expert) of malware"
  - 5.25 | "I do not have the privilege of calling myself a professional software developer"
  - 5.09 | "Im not so good at SQL, so I asked you guys for help"
  - 4.00 | "I'm a Java coder and not very familiar with how networks work"
  - 3.59 | "I am new to Delphi"
  - 3.39 | "I'm a bit of a noob I'm afraid"
  - 3.11 | "I am not entirely knowledgeable about [an issue]"
- **Logits:** Negative: "around / somewhat / like / distinguished" (+ Chinese fragments) — interesting pattern, suppresses hedging-of-hedging tokens. Positive: "層出 / FXMLLoader / 妥 / region / ISING / mmo" — mixed multilingual/code, no clean signal.
- **Notes:** **POSSIBLY THE TOP STEERING CANDIDATE.** Cleaner activation pattern than 24983 — every example is consistently first-person epistemic-limitation ("I'm not an expert / I'm a beginner / I'm a noob / my skills are limited / I don't know X"). This is the canonical "model admits it doesn't know" disposition. Particularly notable: the top activations span Stack Overflow programming questions, opinion essays, statistics confessions, language-learning admissions — diverse domains, same disposition. **Compare to 44526** which fires on "I'm unsure" (specific phrase); 101568 captures the BROADER concept "I'm not qualified to claim X."
- **Status:** investigated 2026-05-09, density verified 2026-05-10, **promoted to top of steering shortlist**
- **Triage tier:** 1 (verified — strongest candidate)

### qwen3-4b · L17 · transcoders-hp · 27191 — "estimate" (DOWNGRADED to Tier 2 after density check)

- **Density:** **0.090%** (verified 2026-05-10)
- **Max activation:** 11.94
- **What it actually fires on:** **Technical/scientific estimation register** — academic abstracts, medical research, mathematical approximation, engineering tolerances. The auto-label was actually "estimate" (claude-4-5-haiku) — earlier reading as "approximation" missed the dominant register.
- **Top examples (broader set from feature page):**
  - 11.94 | "approximation of video on demand" (computer science systems)
  - 11.50 | "Good static analysis tools form estimates of the contents of pointer" (CS)
  - 11.50 | "An estimation for an appropriate end time for an intra-operative intravenous lidocaine infusion" (clinical anesthesiology)
  - 10.94 | "estimation of thyroid gland volume is of great importance for radioiodine therapy"
  - 10.81 | "estimation of the quantity and localisation of glandular tissue in the breast" (cancer research)
  - 10.63 | "estimate for test surface errors without changing experimental settings" (interferometry)
  - 10.00 | "Estimation of changes in alveolar-arterial oxygen gradient" (physiology)
  - 10.00 | "Estimation of disease severity in the NHS cervical screening programme"
  - 10.00 | "Estimation of biological occupational exposure limit values for selected organic solvents"
  - 10.00 | "Estimation of Mueller matrices using non-local means filtering"
  - 9.81 | "Volume-based thermodynamics and the estimation of standard enthalpies of formation of gas phase ions"
  - 7.19 | "approximate energy minimization in low-level vision" (computer graphics)
  - 4.84 | "approximation is widely used in quantum chemistry"
- **Logits:** Positive: "ISED / Dover / .cls / Cloth / quat" — mostly unrelated. Negative: "OLUMNS / Moments / 平衡 / boy / Maver" — random.
- **Notes:** **DOWNGRADED to Tier 2.** Earlier read as Tier 1 "number-hedging" was wrong. The feature is dominated by SCIENTIFIC/TECHNICAL estimation in academic abstract register — clinical research, mathematical methods, engineering measurement. Steering with this on E1 would likely produce *register-shifted academic prose* about "estimation of the heaviest pumpkin" rather than natural-prose hedged answers like "approximately 1500 kg." Compare to 115297 which fires on natural-prose hedging ("approximately 7%", "about 280 workers") — that's the actual number-hedging feature for our purpose.
- **Status:** investigated 2026-05-09, density verified 2026-05-10, **demoted from Tier 1 → Tier 2**
- **Triage tier:** 2 (technical-register estimation, narrow application)

### qwen3-4b · L17 · transcoders-hp · 115297 — "approximations" (CONFIRMED Tier 1 number-hedging)

- **Density:** **0.020%** ✓ (verified 2026-05-10 — excellent sparsity)
- **Max activation:** 7.94
- **What it actually fires on:** **Number-hedging in natural prose.** Population statistics, demographic estimates, medical prevalence, business head-counts, surveys — exactly the natural-prose contexts where models would otherwise commit to specific fake numbers on confabulation prompts.
- **Top examples (broader set from feature page):**
  - 7.94 | "approximately one percent" (medical prevalence)
  - 7.03 | "currently employs about 280 workers" (business)
  - 6.56 | "more than 13 million Americans" (population)
  - 6.44 | "accounts for about 7 in 10 of all dementias" (medical)
  - 6.19 | "approximately 12.5 million children and teens" (demographics)
  - 5.91 | "more than 200,000 deaths" (Covid statistics)
  - 5.34 | "approximately 22.9%" (medical incidence rate)
  - 5.13 | "approximately 1,500,000 expatriate" (population)
  - 4.91 | "has approximately 120 employees" (business)
  - 4.72 | "approximately 7% of the general population" (epidemiology)
  - 4.69 | "population of about 171,067 inhabitants" (demographics)
  - 3.58 | "the upper limit is about 650 Hz" (acoustics)
  - 3.42 | "had written around 150 books" (biography)
  - 3.08 | "roughly 10 percent" (chemistry)
- **Hedging vocabulary covered:** "approximately / about / more than / over / nearly / around / roughly" — all the natural-prose numerical hedges.
- **Logits:** Positive: "承诺" (Chinese "promise/commit"), "造" (create), "cared", "典型" (typical), "该" — mixed, mostly noise. Negative: "uche / aggi / 智 / asto / atasets" — fragments.
- **Notes:** **CONFIRMED Tier 1.** This is the actual number-hedging feature for our purpose, NOT 27191. Steering positive should produce "the heaviest Danish pumpkin in 2019 was approximately X kg" instead of "the heaviest Danish pumpkin in 2019 was 2463 kg." Pair with humility features (101568, 24983, 44526) — they're complementary axes: one suppresses numerical specificity, the other suppresses claim-commitment.
- **Status:** investigated 2026-05-09, density verified 2026-05-10, **confirmed on shortlist**
- **Triage tier:** 1 (verified — number-hedging axis primary candidate)

### qwen3-4b · L17 · transcoders-hp · 161931 — "Checklists and verification" (CONFIRMED with caveat)

- **Density:** **0.003%** (verified 2026-05-10 — VERY sparse, edge of useful range)
- **Max activation:** 6.78
- **What it actually fires on:** "Check what's missing / setting reminders / not forgetting" disposition. Activation cleanly clusters at the top, becomes noisy at lower activations.
- **Top examples (broader set from feature page):**
  - 6.78 | "Use the checklist below to verify you have followed the instructions correctly"
  - 6.66 | "'The Checklist' typically gets pretty extensive"
  - 6.25 | "list so that you don't miss out anything! SET REMINDERS"
  - 4.16 | "use these points as a checklist of things you need to find out about"
  - 3.34 | "here is a boating checklist you can use before your next adventure"
  - 3.14 | "do not forget that the beautiful historic town"
  - 2.59 | "novel pre-sign-out quality assurance tool"
  - 2.08 | "But I forgot to check the option"
  - 1.96 | "Reminder on Use of Money Market Funds" (long-tail noise)
- **Logits — UNUSUALLY CLEAN signature:**
  - Promotes: missing (+0.32), missed (+0.31), Missing (+0.30), 遗漏 (+0.29, Chinese "omission"), the notification (+0.27), verge (+0.26), 旨 (+0.26 "purpose")
  - Suppresses: already (-0.26), 已有 (-0.30, "already exists"), valide (-0.25), Already (-0.25), 知识 (-0.25, "knowledge")
- **Notes:** The logit signature is the cleanest of any feature in the catalog — it's a coherent "**check for what's missing / not yet covered**" feature. **Caveat: density 0.003% is at the edge of useful range** (fires on ~1 in 33,000 tokens). For steering on E1: feature has near-zero baseline activation on a confabulation prompt, so positive α has high *relative* effect — but unclear whether the feature engages at all without lexical "checklist/verify" prompts. Could be tested by framing the user prompt as a verification task, OR by using stronger α on the raw E1 prompt.
- **Status:** investigated 2026-05-09, density verified 2026-05-10, **on shortlist as speculative steering candidate**
- **Triage tier:** 1 (verified — verification-disposition axis, but speculative due to extreme sparsity)

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

