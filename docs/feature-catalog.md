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

### qwen3-4b · L7 / L9 / L15 · transcoders-hp — investigated 2026-05-10 (API batch)

Tested via 14-term commit search (L9), 14-term EG search (L7), 14-term RT search (L15) on the Neuronpedia API. **All three layers returned essentially negative results for clean virtue-aligned features:**

- **L9 commit search:** 20 features at L9; lowest density 0.172% ("clearly"); no candidate in the ideal sparse range. Closes off F105 hypothesis 1 ("v_IH × L17 routes to L9 commit feature via residual propagation"). Detail: `mvp/sae_neuronpedia_data/02_qwen3_4b_commit_search.json`.
- **L7 EG search:** 10 features at L7; cleanest are sub-0.005% medical-register features (meta-analysis, peer-reviewed, documented). All are **discourse-register features** (medical research papers), NOT cognitive operations. **Third instance of the F45 cultural-register pattern** (humility-as-religious-discourse, Gemma-as-trained-template, EG-as-medical-register). Detail: `03_qwen3_4b_eg_l7_search.json`.
- **L15 RT search:** 5 features at L15; all density 0.19%+ (none ideal); top examples about WikiLeaks / nucleus accumbens — single-doc detectors, not reasoning-disposition features. Detail: `04_qwen3_4b_rt_l15_search.json`.

**Joint claim:** three of our five virtue-extraction layers (L9 commit-counterpart, L15 RT, plus L17 commit-counterpart from the original second-round triage) lack clean SAE-feature decompositions in the qwen3-4b transcoder-hp. Constraints F105's IH/CC collision mechanism to hypotheses 2-4 (distributed circuit, polysemantic superposition, deeper-layer feature) — hypothesis 1 (shared L9 commit feature) is now closed.

### qwen3-4b · L29 · transcoder-hp · 59103 — "confident" — only deeper-layer commit candidate worth tracking

Surfaced from a cross-layer commit search and verified by direct API lookup (45 activations).

- **Density:** 0.009% (verified)
- **Max activation:** 17.88
- **What it actually fires on:** First- and third-person confident-stance statements, mixed register (sports narrative, technical, personal). Distinct from the "for this reason" trap at L28 idx 34354 (see "Tier 3 — promoted observation" above) which has clean commit-vocab pos logits but fires on a discourse marker.
- **Top examples:**
  - 17.88 | "Montezemolo is confident his Formula 1 team can respond"
  - 16.88 | "if he wasn't reasonably confident that it'll work"
  - 15.88 | "I'm more or less confident this is caused by the fact that"
  - 15.62 | "She is convinced that 'they' or the police"
  - 15.19 | "the season and will be confident of extending his lead"
- **Logits:** Negative includes " Yourself / 更快 / ago / oit / ourselves"; positive includes " of / 	of / cá»§a (Vietnamese 'of') / é¢ĦçķĻ / plements" — pos logits are uninformative (mostly junk subwords), so the feature signature is in the activation pattern, not in the logit cluster.
- **Notes:** Mixed first-person and third-person ("Montezemolo is confident" is third-person sports report; "I'm more or less confident" is first-person hedged commit). Not as clean as 19103 on R1-Distill (which has razor-sharp commit-vocab positive logits AND first-person closure pattern). **Dashboard verification 2026-05-10 evening (`~/Downloads/NP/qwen3_4b_59103.pdf`) confirms the API assessment AND surfaces an additional concern: the feature also fires on `hopeful` ("the company is hopeful that…", "I was hopeful it would…").** Hopeful is forward-looking optimism, not commit-stance — meaningful semantic-field contamination. Distribution: ~50% third-person narrative ("Montezemolo is confident", "She is convinced", "Caleb and Joshua were confident"), ~30% first-person, ~15% second-person marketing, plus the `hopeful` cluster. Still the only passable commit-shaped feature in qwen3-4b's transcoder-hp at any layer L9-L30, but with weaker first-person specificity than the catalog initially implied.
- **Status:** investigated 2026-05-10 (API direct lookup) + dashboard verified 2026-05-10 evening; speculative candidate for qwen3-4b cross-layer commit-amplifier test
- **Triage tier:** 2 (mixed register; firing also on `hopeful` is meaningful contamination)

### Other transcoder layers (qwen3-4b)

L0-L35 confirmed available. L29 is the only deeper layer with a passable commit candidate; L28/L23/L25/L26/L27/L30 candidates were either too generic or 70419-style traps (top-activation context didn't match auto-label). Detail in `mvp/sae_neuronpedia_data/05_qwen3_4b_deeper_commit.json`.

### Other models — Neuronpedia coverage map (verified 2026-05-10)

Parsed from the full models-page HTML export at `~/Downloads/NP/QWEN3-4B ｜ Neuronpedia.html`. This is the complete list of (model, source-set) combinations available on Neuronpedia for our project.

#### Our 5 cross-model run subjects × Neuronpedia coverage

| Our model | On Neuronpedia? | Available sources | Notes |
|-----------|-----------------|-------------------|-------|
| **qwen3-4b** | ✅ Yes | `transcoders-hp` ONLY (164k features, L0-L35) — what we've been using. **Correction 2026-05-10 night**: earlier note about `qwenscope-res-32k` being available was based on misreading the available-resources page; **Qwen Scope SAEs do NOT exist for qwen3-4b on Neuronpedia.** Qwen Scope `qwenscope-res-32k` exists for `qwen3.5-2b` (L11) and `qwen3.5-9b` (L15) only. Verified by Gemini headless-browser navigation: direct URL returns 404, model page lists only Circuit Tracer Transcoders. | Only MLP-input transcoder available. Residual-stream SAE for qwen3-4b would need to be trained ourselves or sourced elsewhere. |
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
- **qwen-scope / qwenscope-*** — Alibaba's official SAE release for Qwen3 family. 32k or 64k features, residual stream. **Note (2026-05-10 verification):** on Neuronpedia, only `qwen3.5-2b` and `qwen3.5-9b` have qwenscope SAEs. **NOT available for qwen3-4b** despite earlier catalog claim.
- **saes-qwen2** — Qwen2 SAEs (community).
- **saes-gpt-oss-20b** — GPT-OSS SAEs (community).
- **circuit-tracer** — Anthropic-style circuit-tracing SAEs.
- **sae-bench** — SAEBench-format SAEs (used for evals not steering).

#### Recommended search-and-export plan for the next ~day

User has compute-VM unavailable for ~1 day, will use that time to gather Neuronpedia data. Priority order:

**Tier A — direct comparators to current qwen3-4b L17 work:**

1. ~~**qwen3-4b · qwen-scope (residual stream SAEs)**~~ **NOT AVAILABLE — verified 2026-05-10 night.** Qwen Scope SAEs don't exist for qwen3-4b on Neuronpedia (only for qwen3.5-2b and qwen3.5-9b). Earlier catalog note was based on misread of the available-resources page. The only qwen3-4b SAE on Neuronpedia is `transcoder-hp` (MLP-input). For Experiment 2 (v_IH projection diagnostic), see updated `docs/sae-experiment-plan.md` — options are (a) use the existing transcoder-hp anyway, accepting the MLP-input vs residual-stream basis-mismatch caveat, or (b) shift the diagnostic to a model that has both (e.g. gemma-2-2b), or (c) train our own residual-stream SAE for qwen3-4b once VM returns.

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
- **53054** "define" / "I define X as Y" (max 16.38, **density verified 2026-05-10: 0.610% — borderline-generic**) — first-person definitional commitment, different subtype from assertive commitment. Density at upper edge of usable; treat as exploratory only.
- **6900** "Asking questions" / "I want to ask experienced programmers" (max 4.38) — first-person knowledge-gap action ("It's no shame to ask"). Weak max but on-target conceptually.
- **131448** "needing information, not knowing" / "hard to answer without more information" (max 3.94) — first-person info-insufficiency. Below threshold but conceptually closest to action-disposition humility.
- **136512** "understanding and interpretation" / "if I understood this correctly" (max 6.78) — first-person hedged interpretation marker.
- **146191** "seek for any evidence, correct errors" (max 18.75, **density verified 2026-05-10: 2.077% — DEMOTED to Tier 3, fails the >1% generic-feature rule**) — epistemic vigilance disposition. Top activation is descriptive ("sought to doubt any assertion, to seek for any evidence, to correct any errors"). Density too high for clean steering.
- **160623** "lack of knowledge" / "wholly ignorant" (max 4.38) — Socratic inquiry framing. Weak.
- **69694** "must" / "I must admit" (max 21.50, **density verified 2026-05-10: 2.438% — DEMOTED to Tier 3, fails >1% generic-feature rule**) — broad deontic/necessity feature, but examples include "I must have made some misconceptions" and "I must admit." Density too high for clean steering.

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

### Promoted observation (2026-05-10) — No clean commit feature exists at qwen3-4b L17, but commit features ARE encodable cleanly elsewhere — constrains the F105 IH/CC collision mechanism

This started as a buried bullet in the second-round triage. After Day 27 added cross-model coverage, it deserves promotion to a top-level finding because the comparison sharpens the constraint.

**At qwen3-4b L17 transcoder:** the "confidently" + "definitively" searches returned generic adverbs, scientific-register verbs, and morpheme detectors — but no clean first-person "I'm certain that X" / commitment-closure feature. The Tier-1 humility features (24983, 44526, 131926, 101568) do not have a clean geometric opposite at this layer/decomposition.

**Contrast: at R1-Distill-Llama-8B L31** (`llamascope-slimpj-openr1-res-32k`), feature **19103** is a textbook commitment-closure feature. Density 0.008%, max activation 25.88. Top-30 essentially identical: "All methods give the same result, so I'm confident that's correct. **Final Answer** \boxed{X}". Conditioned on completed verification, immediately followed by `**Final Answer**` and `\boxed{}`.

**What this comparison establishes:** commit-direction IS encodable as a clean SAE feature in *some* layer/architecture combinations — it's not a concept that fundamentally resists feature-decomposition. The absence at qwen3-4b L17 is therefore **layer/decomposition-specific**, not "commitment isn't extractable in general."

**Why this matters for F105 (IH/CC behavioral collision):** F105 found that v_IH × L17 and v_CC × L9 produce behaviorally identical anti-FM-8 commit behavior, despite being geometrically orthogonal. The natural mechanistic explanation would be "both vectors project onto a shared commit feature." This SAE evidence rules that out **for L17 specifically**: no shared commit feature exists there. The behavioral collision must come from one of:

1. A commit feature at L9 (where v_CC was extracted) that v_IH × L17 routes to via residual-stream propagation,
2. A commit circuit distributed across multiple features (the SAE's per-feature view would miss this),
3. Non-feature-aligned residual structure that this transcoder doesn't capture (the "polysemantic superposition" possibility),
4. Feature-aligned at a different layer (deeper than 17) that both vectors reach via downstream amplification.

**Update 2026-05-10 (API batch):** all four hypotheses tested via the Neuronpedia API.

- **Hypothesis 1 — closed.** The 14-term commit search at L9 surfaced 20 features; the lowest density was 0.172% (idx 33101, "clearly"); none in the ideal sparse range; all are filler-emphasis features (clearly / certainly / sure / absolutely) on casual register, not commit-disposition. **No clean commit feature exists at L9 either.** Detail in `mvp/sae_neuronpedia_data/02_qwen3_4b_commit_search.json`; one-line: F105 hypothesis 1 is rejected.
- **Hypothesis 4 — partially tested.** A cross-layer scan + direct lookup of 10 deeper-layer commit candidates (L23 / L25 / L26 / L27 / L28 / L29 / L30) found exactly **one passable candidate**: L29 idx 59103 ("confident", density 0.009%) — see entry below. But it's mixed first/third-person register ("Montezemolo is confident…" / "I'm more or less confident…"), not as clean as 19103 on R1-Distill. The other 9 candidates were either too generic or 70419-style traps (e.g. L28 idx 34354, auto-label "Expressing certainty" with clean commit-vocab pos logits, but actually fires on the discourse marker "For this reason"). Hypothesis 4 has a thin lead but no slam-dunk feature.
- **Hypotheses 2 + 3 — remain open** as the only fully unconstrained explanations. F105's IH/CC collision is most likely either a distributed circuit (no single clean feature) or non-feature-aligned residual structure that this transcoder family can't decompose.

This is a real result — a constrained mechanistic claim. The behavioral collision F105 documented can't be explained by any clean shared SAE feature in the qwen3-4b transcoder-hp at L9, L17, or any deeper layer up to L30. Either the circuit is distributed, or the transcoder is the wrong tool.

### Pattern observations from second-round triage

1. **No clean opposite-axis commit feature found** at L17. (See "Promoted observation" above for full treatment and the cross-model contrast.)

2. **Multi-word phrase searches systematically fail.** "Without evidence" → generic "without"; "outside my knowledge" → generic "knowledge" + spatial "beyond"; "as far as I know" → factual-attribution features. Single-word concept searches work better.

3. **Number-hedging axis (27191, 115297) is a new useful direction** distinct from epistemic-uncertainty axis. Could produce "approximately X" hedged answers on confabulation prompts.

4. **Verification-disposition axis (161931) is promising** with an unusually clean logit signature (promotes "missing/missed/omission"). Different intervention than humility — "let me check before committing" rather than "I don't know."

5. **Action-disposition humility doesn't surface as a clean feature** at L17 (features 6900, 131448, 146191 are all weak). May require different layer or different search strategy.

6. **Religious-virtue cluster at L17 is well-developed** — patience, courage, empathy, forgiveness, grace, mercy, honesty, gratitude all have dedicated features. The word "humility" surfaces these rather than any model-disposition feature. Useful background context for other projects but confirms F45 (disposition modulation, not propositional injection) at the SAE-feature level.

---

## Qwen2.5-7B-Instruct · L23 · 23-resid-post-aa

**Source details:** LlamaScope-OpenR1 residual-stream SAE (131k features) at layer 23. Used as proxy for our `openr1-qwen-7b` cross-model subject (same Qwen2.5-7B base). Searches and dashboards completed 2026-05-10. PDFs in `~/Downloads/NP/Qwen2.5-7B-Instruct_LAYER_23/`.

**Caveat:** This SAE is on the Instruct variant; OpenR1-Qwen-7B is a downstream RL post-training of the same base. Features should largely transfer but verify activation magnitudes on a few held-out OpenR1 generations before steering.

### Qwen2.5-7B-Instruct · L23 · 23-resid-post-aa · 2174 — "I'm sorry, but I'm not able to find / I am not aware of"

- **Density:** 0.043%
- **Max activation:** 71.19
- **What it actually fires on:** First-person assistant abstention on the token "'m" inside the "I'm sorry, but I [don't have / am not aware of / am not familiar with] information on X" template. Almost every top-20 activation is an `assistant` turn responding to a user query about an unfamiliar named entity (place, person, product, term) with a polite refusal-to-claim-knowledge. This is the IH stance — explicit acknowledgement of a knowledge gap, not refusal of a harmful request.
- **Top examples:**
  - 71.19 | "I'm sorry, but I'm not able to find any information about \"XL N"
  - 70.13 | "I'm sorry, but I am not aware of a book called \"el libro gordo de petete\""
  - 69.13 | "I'm sorry, but I don't have any information on a person or thing named"
  - 68.63 | "I'm sorry, but I am not aware of an actress named NAME_1"
  - 67.31 | "I'm sorry, but I don't have any information on a person named Islom"
- **Logits:** Negative includes "sold / amil / ET / /Game / rg / أن"; positive includes "胠 / idol / 红枣 / Disp / .IsFalse / Essentials" — neither side is semantically informative (mostly orthographic/multilingual fragments).
- **Notes:** Sharp register break around rank ~20: top activations 60+ are all chat-format "I'm sorry…" assistant turns; below ~15 the feature picks up generic first-person `'m / am / 'm not` in non-chat forum text. The chat-mode firing is extremely clean. Density in the ideal band.
- **Status:** investigated 2026-05-10 (dashboard read), shortlisted for IH steering on Qwen2.5-7B-Instruct / OpenR1-Qwen-7B
- **Triage tier:** 1

### Qwen2.5-7B-Instruct · L23 · 23-resid-post-aa · 75315 — "I'm not sure / I'm not saying / first-person hedge"

- **Density:** 0.039%
- **Max activation:** 89.75
- **What it actually fires on:** First-person epistemic hedging on "'m" in `I'm not sure / I'm not saying / I'm not aware / I'm not certain / I'm pretty sure / I'm guessing / I'm wary`. Primarily forum-register prose (StackExchange-flavored) where the writer marks confidence on a claim. Distinct from 2174: this is the user-voice hedge ("I'm not sure if X"), not the assistant-abstention template.
- **Top examples:**
  - 89.75 | "I'm not saying that's actually the case here, but it's the kind of"
  - 87.13 | "I'm not sure any are a particularly big risk, but of course depends"
  - 86.19 | "I'm not certain, but your accounting software might accept an LS-120"
  - 85.50 | "I'm not aware of any sort of exemption available due to you moving"
  - 84.00 | "I'm pretty sure no one here ever dealed with such a situation"
- **Logits:** Negative includes "(IEnumerable / Looks / 하지만 / Numerous / elephants / remely"; positive includes "LX / Rpc / ẳng / _BG / SuppressWarnings / 博物馆" — uninformative.
- **Notes:** Strong contamination at rank 25+: a single sentence ("While today's number is great to see, I'm not going to use it…") repeats ~14× from a duplicated LMSYS document. Top-20 unique examples are clean first-person hedges. No 70419-style world-uncertainty contamination. Excellent IH candidate.
- **Status:** investigated 2026-05-10, shortlisted for IH steering
- **Triage tier:** 1

### Qwen2.5-7B-Instruct · L23 · 23-resid-post-aa · 84309 — "what (under-specified question / clarification request)"

- **Density:** 0.037%
- **Max activation:** 44.38
- **What it actually fires on:** "what" inside meta-statements about under-specification: "I'm uncertain of what X should be", "I'm not sure what you mean by X", "It's not clear what Y is", "the question does not specify what Z". Mix of (a) first-person developer/user voice ("I'm trying to figure out what to use…") and (b) assistant-voice clarification requests ("I'm sorry, but I'm not sure what you mean by X"). Both forms are epistemic — speaker flagging missing information.
- **Top examples:**
  - 44.38 | "I'm uncertain of what the combinatorials should be"
  - 43.78 | "I'm trying to figure out what to use for the ADC"
  - 43.19 | "There's a lot that's unspecified in your question, such as what"
  - 40.94 | "I'm however unsure what would be the appropriate way to code this"
  - 39.81 | "I'm sorry, but I'm not sure what you mean by 'write me a script'"
- **Logits:** Negative includes "Romney / chant / Attack / Merc / icks / 湖北"; positive includes "虚构 (fictional) / numeros / NAN / 发动 / 深夜 / vero". The "虚构" + "NAN" tokens are semantically suggestive of "unknown/missing value".
- **Notes:** Cleanest task-uncertainty / clarification-request feature. Distinct from 2174 (knowledge-gap on entities) and 75315 (claim hedging) — this one is "I don't have enough information to compute / your question is ambiguous". Lower max-activation (44 vs 70-105) but consistent across top-40. **Promoted from initial Tier-2 to Tier-1** based on dashboard read.
- **Status:** investigated 2026-05-10, shortlisted for IH steering
- **Triage tier:** 1

### Qwen2.5-7B-Instruct · L23 · 23-resid-post-aa · 120087 — "I'm sorry, but I cannot fulfill your request"

- **Density:** 0.357%
- **Max activation:** 105.50
- **What it actually fires on:** The object-of-refusal token (`this / your / that request`) inside the assistant safety-refusal template "I'm sorry, but I cannot/am unable to fulfill [this/your] request as it goes against my programming…". Every top-20 hit is a hard safety refusal — racist jokes, NSFW, illegal content, harmful narratives. Mechanism is "I cannot do X because policy forbids", not "I don't know X".
- **Top examples:**
  - 105.50 | "I'm sorry, but as an AI language model, I cannot fulfill this request"
  - 105.50 | "I'm sorry, but I am not able to fulfill your request as it goes against"
  - 104.75 | "I'm sorry, but I cannot fulfill your request as the content you have"
  - 102.13 | "I'm sorry, but I cannot fulfill that request as it goes against"
  - 101.69 | "I'm sorry, but I cannot comply with your request. It would not be ethical"
- **Logits:** Negative includes "包容 (inclusion) / INSERT / brushes / UPDATE / SENSOR / PLAN"; positive includes "eval / zed / _eq / fol / -election / pinnacle".
- **Notes:** Refusal-as-policy, NOT epistemic humility. Density 0.357% higher than ideal. **Demoted from initial Tier-1 to Tier-2** — useful as a contrast control (verify IH steering ≠ refusal steering), not as a primary IH vector.
- **Status:** investigated 2026-05-10, refusal-cluster contrast control
- **Triage tier:** 2

### Qwen2.5-7B-Instruct · L23 · 23-resid-post-aa · 5494 — "Hesitancy (wary / apprehensive / hesitant)"

- **Density:** 0.021%
- **Max activation:** 61.16
- **What it actually fires on:** Trait-attribution adjectives describing **emotional/social hesitancy**: "wary", "apprehensive", "hesitant", "leery", "skittish", "squeamish", "reticent". Mix of first-person ("I was wary of…") and third-person narrative ("NAME_1 was hesitant at first"). Semantic field is *social/emotional caution about an action*, not epistemic uncertainty.
- **Top examples:**
  - 61.16 | "I'm also pretty reticent to tell someone what would be best for their child"
  - 59.00 | "I'm apprehensive about falling into a genre"
  - 58.78 | "am very skittish when trying any type of liner besides foil"
  - 58.50 | "I have always been wary of sewing with silky fabrics"
  - 57.22 | "I am always hesitant when buying new lip balm"
- **Logits:** Negative includes "Kron / _MS / Remember / .stub / assertSame / Animations"; positive includes "ipes / edriver / .Repositories / cdf / IDR / élevé". Uninformative.
- **Notes:** Heavy LMSYS-fanfic contamination ("NAME_1 was hesitant at first…"). Affective ("scared to try") rather than epistemic. Useful for testing whether IH and emotional caution share a substrate, not the same construct as 2174/75315.
- **Status:** investigated 2026-05-10, separate hypothesis test
- **Triage tier:** 2

### Qwen2.5-7B-Instruct · L23 · 23-resid-post-aa · 89590 — "unclear" (mislabeled — world-uncertainty)

- **Density:** 0.017%
- **Max activation:** 76.19
- **What it actually fires on:** "unclear" in the impersonal "It is unclear whether/how/if/what…" — a third-person hedge about external facts (history, politics, science, news). Almost zero first-person voice; the speaker is reporting that *the world / the record* is uncertain, not their own epistemic state. **Direct analogue of qwen3-4b feature 70419** at this scale.
- **Top examples:**
  - 76.19 | "it is unclear whether he may have had an early idea along the lines"
  - 74.88 | "It is unclear at this time, however, whether California will be able"
  - 73.44 | "it's unclear if the heightened activity is the result of Mueller"
  - 72.69 | "It is unclear if President Bush was given the letter after it arrived"
  - 71.50 | "It is unclear how many government bases the rebels have overrun"
- **Logits:** Negative includes "dto / Saddam / authoritarian / subTitle / dancer / MAN / Train"; positive includes "TAS / AINED / efficacy / orbital / glance / 請求". Negative side suppressing concrete-actor tokens is consistent with "we don't know who/what" framing.
- **Notes:** **70419 trap reproduced exactly** at Qwen2.5-7B scale. Auto-label "unclear" sounds humility-adjacent; firing pattern is world-uncertainty topic. Confirms the cautionary tale generalizes from Qwen3-4B → Qwen2.5-7B. **Demoted from initial Tier-2 to Tier-3.**
- **Status:** investigated 2026-05-10, REJECTED for steering
- **Triage tier:** 3

### Qwen2.5-7B-Instruct · L23 · 23-resid-post-aa · 18575 — "correct answer" (REJECTED — user-prompt-template detector, NOT commit feature)

Surfaced from API commit-axis search 2026-05-10. Initially triaged as Tier 2 (MCQ-domain commit) based on 3-activation API sample. **Dashboard verification (2026-05-10 evening, 50-activation list at `~/Downloads/NP/qwen25_7b_18575.pdf`) reveals it's a wrong-tool trap.**

- **Density:** 0.005% (verified)
- **Max activation:** 45.69
- **What it actually fires on:** **User-prompt-template scaffolding for benchmark-style multiple-choice questions.** Top-20 activations are 20 different MMLU-style questions (covering law, chemistry, philosophy, biology, ethics, accounting) but all share the *exact same prompt template*: "Please eliminate two incorrect options first, then think it step by step and choose the most proper one option." Activating token is the literal comma `,` in the scaffolding. Long tail (rank 20+) shifts to forum-style disambiguation questions ("which is correct?" / "Which option is the most logical?" / "Which one is right?"). **The feature fires on USER-side input, not on assistant-side commitment.**
- **Top examples (max 45.69 → ~6.94, all on user-prompt tokens):**
  - 45.69 | "professional judgment but… ↵ Please eliminate two incorrect options first…"
  - 45.16 | "catalyst increases the activation energy… ↵ Please eliminate two incorrect options first…"
  - 44.47 | "sensible world would consist of unchanging Forms ↵ Please eliminate two incorrect options first…"
  - 13.88 | "please tell me which is wrong, which is correct" (long-tail forum disambiguation)
  - 10.89 | "Which one is the correct one?" (long-tail forum disambiguation)
- **Logits:** Negative junk multilingual; positive junk multilingual.
- **Notes:** **Third 70419-style trap surfaced in F112 commit search**, after qwen3-4b L28 idx 34354 ("for this reason" discourse marker) and Qwen2.5-7B 30133 ("to a certain extent" hedge). Auto-label says "correct answer", cosine to query "correct answer" is high (0.78), max-activation 45.69 — all tempting signals. **Reading the full dashboard breaks the illusion**: the feature fires on the *input scaffolding* of MCQ-format prompts, not on the *model's commitment* to an answer. Steering this would push the model to treat outputs as if they were MCQ-format prompts, NOT push it toward confident closure. Wrong mechanism for F112. **Demoted from T2 to T3.**
- **Status:** investigated 2026-05-10 (API direct lookup) + dashboard verified 2026-05-10 evening, REJECTED for steering
- **Triage tier:** 3

### Qwen2.5-7B-Instruct · L23 · 23-resid-post-aa · 30133 — "certain" (mislabeled — hedge usage of "certain")

Surfaced as high-cosine candidate for "certain" search; rejected after activation read.

- **Density:** 0.024%
- **Max activation:** 90.06 (highest in the API batch)
- **What it actually fires on:** The literal token "certain" in **hedge usage** ("to a certain extent" = "some / partial"), NOT in commit usage. Top examples are "to a certain extent" repeated across distinct documents. The "Certain to create controversy" / "Certain option combinations" examples are impersonal/inanimate uses, not first-person commit.
- **Top examples:**
  - 92.12 | "This works to a certain extent. But when the incoming string"
  - 91.88 | "solved this problem to a certain extent where a system reset was activated"
  - 91.44 | "it to work to a certain extent but i can't get it"
  - 91.12 | "a new reality series. Certain to create controversy"
  - 91.00 | "and it did to a certain extent"
  - 91.00 | "fine, up to a certain degree"
- **Logits:** Negative junk; positive includes " certain / Certain / afirm / Para / Conclusion" — pos logits LOOK clean and commit-aligned, but they reflect what tokens the feature *predicts to follow* the firing context, not what the feature represents. The actual firing is on hedge "certain" not commit "certain."
- **Notes:** **70419-style trap.** Auto-label "certain" + cosine-1.00 to query "certain" make it look like a commit feature; pos-logit cluster reinforces the impression. **Reading top activations breaks the illusion** — almost every top-30 hit is "to a certain extent" hedge usage (= "some, partial"). High max-activation comes from token frequency of the literal word "certain", not from semantic commit. Cautionary case: cosine-similarity to query is not a triage signal.
- **Status:** investigated 2026-05-10 (API direct lookup), REJECTED — confirms the cosine+label triage failure mode
- **Triage tier:** 3

---

## Llama-3.1-8B · L31 · llamascope-res-32k

**Source details:** LlamaScope residual-stream SAE (32k features) at layer 31, base Llama-3.1-8B. Used as proxy for our `Llama-3.1-8B-R1-GRPO` cross-model subject. Searches and dashboards completed 2026-05-10. PDFs in `~/Downloads/NP/Llama-3.1-8B_LAYER_31/`.

**Caveat:** This SAE is trained on the BASE model. R1-GRPO is a heavy reasoning post-train; verify activation magnitudes on a held-out GRPO sample before steering. Of the candidates below, **8310** (`seems to`, pure syntactic) is most likely to transfer cleanly; **21701** (StackOverflow help-seeker register) is most likely to differ in GRPO.

### Llama-3.1-8B · L31 · llamascope-res-32k · 7984 — "negative phrases / lack of knowledge"

- **Density:** 0.111%
- **Max activation:** 30.50
- **What it actually fires on:** First-person epistemic absence — overwhelmingly `[I/we/they] have/had no [idea/clue/desire/regrets/doubt/sense/interest]`. Activating token is the determiner `no`. Genuine first-person hedging in informal/conversational register (forum comments, Reddit-style prose).
- **Top examples:**
  - 30.50 | "I have no clue what Ron Knecht thinks of as individual liberty"
  - 28.13 | "I have no idea why they're homeless because they have work"
  - 28.00 | "I have no desire to get my news in the same way as the US"
  - 27.75 | "I have no idea what Brown said, but you could see his leadership"
  - 27.50 | "I had no idea where the stuff even came from until I saw"
- **Logits:** Negative includes "SKTOP / unto / severity / pis / izen / velopment"; positive includes " idea / clue / qual / intentions / experience / plans / regrets" — near-perfect inventory of "no ___" hedging idioms.
- **Notes:** Cleanest IH candidate of the set. Density in ideal band. Some occurrences are first-person plural / third-person quotative ("he had no idea") so not purely "I"-conditioned. Construction is so common it should survive GRPO post-training.
- **Status:** investigated 2026-05-10, shortlisted for IH steering on Llama-3.1-8B-R1-GRPO
- **Triage tier:** 1

### Llama-3.1-8B · L31 · llamascope-res-32k · 201 — "negative assertions / expressions of doubt"

- **Density:** 0.046%
- **Max activation:** 33.50
- **What it actually fires on:** First-person hedged assertion in the `I'm not [sure / suggesting / saying / entirely sure / 100% sure / one to speculate / a Windows expert]` family. Activating token is `not` (or `'t`) following `I am`/`I'm`. Prototypical "speaker disclaiming epistemic commitment". Distinctly different from 7984: 7984 keys on `no` (absence noun); 201 keys on `not` (predicate negation). **Complementary — sum vector should give broader IH coverage than either alone.**
- **Top examples:**
  - 33.50 | "I'm not suggesting it's possible, just thinking out loud"
  - 33.25 | "I'm not entirely sure if it'll actually work"
  - 33.00 | "I'm not sure if the background image code was actually causing"
  - 32.75 | "I'm not one to speculate"
  - 32.75 | "I'm not skeptical about Agile development because I have 4 years"
- **Logits:** Negative includes "Courtesy / ilgi / agner / uko / ler" (junk subwords); positive includes " sure / entirely / gonna / exactly / necessarily / certain" — pure hedge-vocabulary registry.
- **Notes:** Strongest pure-IH candidate. Hit in 4 of 6 IH searches → high cross-query confidence. Density ideal.
- **Status:** investigated 2026-05-10, shortlisted for IH steering
- **Triage tier:** 1

### Llama-3.1-8B · L31 · llamascope-res-32k · 21701 — "personal pronouns and uncertainty/confusion (code-help register)"

- **Density:** 0.079%
- **Max activation:** 34.75
- **What it actually fires on:** First-person help-seeking voice in code/Q&A register. Almost every top-30 is a Stack-Overflow-style post: `I am trying to / I've tried / I'm using / I'm really uncertain as to / I cannot / I don't know if`. Activating token is `I` (clause-initial). Heavy domain bias — VS, JavaScript, Angular, R, regexp.
- **Top examples:**
  - 34.75 | "I am trying to build this gradually, but I am stuck on even filtering"
  - 34.50 | "I can't inherit from Microsoft.Xna.Framework.Game because my class"
  - 34.25 | "What am I missing? I've done this before."
  - 31.63 | "I'm really uncertain as to what the issue is here"
  - 30.88 | "How do I handle this? I guess I need something like"
- **Logits:** Negative includes "olet / Liked / .scalablytyped / complexContent / andom / URN" (code-token junk); positive includes " presum / presumption / understand / realize / apologize / apologies".
- **Notes:** Domain-restricted help-seeker register, not general IH. Useful for *coding-domain* humility steering on GRPO but won't generalize to philosophical/factual humility. **Highest base-vs-GRPO transfer risk** — SlimPajama's heavy SO content; GRPO model has different first-person `I` patterns.
- **Status:** investigated 2026-05-10, separate hypothesis test (coding-domain only)
- **Triage tier:** 2

### Llama-3.1-8B · L31 · llamascope-res-32k · 10391 — "academic hedging on claims/evidence"

- **Density:** 0.455%
- **Max activation:** 16.13
- **What it actually fires on:** Academic / journalistic hedging — "we cannot yet say / it is too early to / cannot be determined / no consensus / has not been established". Voice is third-person/impersonal scholarly. **Meta-claim hedging in expository prose, not first-person disclosure.**
- **Top examples:**
  - 16.13 | "While it is too soon to say with any certainty what this means"
  - 15.94 | "the doctor told us that he couldn't say anything until Kush woke up"
  - 15.81 | "not enough in the Court TV article to really say one way or"
  - 15.56 | "we still do not know the full biographical details"
  - 15.44 | "We were never able to determine what the actual crystalline structure was"
- **Logits:** Negative includes junk; positive includes " definit / definitive / definite / conclus / unequiv / conclusive / certainty / decis" — feature *suppresses* commitment vocabulary, i.e. predicts the negation of those.
- **Notes:** Density 0.455% at high end of usable. Distinct mechanism from 7984/201 (first-person colloquial); 10391 is third-person scholarly. Could be a powerful complement for steering "academic epistemic caution".
- **Status:** investigated 2026-05-10, T2 auxiliary (third-person scholarly hedge)
- **Triage tier:** 2

### Llama-3.1-8B · L31 · llamascope-res-32k · 8310 — "phrases indicating speculation (`seems to`)"

- **Density:** 0.112%
- **Max activation:** 27.38
- **What it actually fires on:** The verb `seem(s/ed) to` as an evidential/observer-hedge marker. Activating token is `to` immediately following `seem(s)`/`seemed`. Voice is third-person observation: "DeVos seems to be confused", "the trade battle seems to be taking a toll".
- **Top examples:**
  - 27.38 | "Betsy DeVos seems to be confused about her job"
  - 26.13 | "The Division is a solid game, but it seems to be known more for"
  - 26.00 | "The UK advertising industry seems to thrive masochistically"
  - 25.13 | "Horejsi seemed to draw herself up defensively"
  - 25.00 | "[Blogging] seems to be the most adopted form of Web 2.0"
- **Logits:** Negative includes " seems / Seems / should / seemed / shouldn / seeming / hopefully / tended" (the feature *consumes* the seem-token to predict what comes next); positive includes " be / have / me / want / lack / indicate".
- **Notes:** Observer-evidential hedge — different mechanism from first-person IH but a valid sub-dimension (qualifying claims about the world rather than asserting flatly). **Most likely feature in the set to transfer cleanly to GRPO** (pure syntactic, tied to the verb `seem`).
- **Status:** investigated 2026-05-10, T2 auxiliary
- **Triage tier:** 2

### Llama-3.1-8B · L31 · llamascope-res-32k · 24873 — "doubt/skepticism vocabulary" (mislabeled)

- **Density:** 0.231%
- **Max activation:** 17.50
- **What it actually fires on:** The CONCEPT/TOPIC of doubt-skepticism, fired across diverse documents and grammatical positions. Top-20 spans clearly distinct documents (cycling, Liz/Sarah comic, Copernicus, Volkswagen Chattanooga, IDF, Portuguese band) — NOT single-document trap. But fires on "I've had doubts" (first-person), "benefit of the doubt" (idiom), "beyond reasonable doubt" (legal — opposite polarity!), "skeptics out there" (third-person noun). A doubt-lexicon detector, not a first-person epistemic-state detector.
- **Top examples:**
  - 17.50 | "something I've had doubts about in the past"
  - 16.25 | "It's not like Liz has earned the benefit of the doubt"
  - 14.88 | "He established beyond reasonable doubt that all living things"
  - 14.31 | "I admit that I was skeptical when I came across your website"
  - 13.88 | "the Ethics Committee cleared the President beyond any doubt"
- **Logits:** Negative includes junk; positive includes " doubt / doubts / doub / skepticism / Doub / scept / skeptical".
- **Notes:** Single-document risk DEBUNKED. But functionally analogous to 70419: looks like uncertainty, actually fires on uncertainty-as-topic (including the *opposite* polarity "beyond doubt" = certainty). Density 0.231% borderline-too-generic. **Demoted from initial Tier-1 to Tier-3.**
- **Status:** investigated 2026-05-10, REJECTED for primary IH steering
- **Triage tier:** 3

### Llama-3.1-8B · L31 · llamascope-res-32k · 22443 — "content related to uncertainty/unknowns" (mislabeled)

- **Density:** 0.426%
- **Max activation:** 25.00
- **What it actually fires on:** Exactly the 70419-style trap. World-state uncertainty in expository/journalistic register: "cause of death is unknown", "remains unclear", "remains uncertain", "exact details of Billy the Kid's birth are unknown". Fires on text *about* unknown facts, never on first-person epistemic state.
- **Top examples:**
  - 25.00 | "Whether or not any other creature can also absorb grace is also unknown"
  - 25.00 | "Double-Dip's cause of death is unknown, but Elizabeth noted he appeared"
  - 22.38 | "it remains unclear if all World Bank Group data was compromised"
  - 21.75 | "The full scope and applicability of EO 202.9 remains uncertain"
  - 21.25 | "The exact details of Billy the Kid's birth are unknown"
- **Logits:** Positive includes " unknown / unclear / uncertain / Unknown / unsure / mystery / uncertainty" — purely the unknown-noun/adjective lexical family.
- **Notes:** **70419 trap reproduced on Llama-base.** Density 0.426% is high. Could serve as a *negative control* — steer up and verify the model says "the answer is unknown" (third-person) rather than "I don't know" (first-person).
- **Status:** investigated 2026-05-10, REJECTED for primary IH (negative-control candidate)
- **Triage tier:** 3

### Llama-3.1-8B · L31 · llamascope-res-32k · 575 — "conditional `or` token" (mislabeled)

- **Density:** 0.045%
- **Max activation:** 21.63
- **What it actually fires on:** The literal `or` token in compound `may/might or may/might not`, plus a long tail of generic `or`-coordinations (`more or less`, `with or without`). Top activations show the `[may] or may not be [X]` construction, but mid-strength activations are just the conjunction `or` in any context. Positive logits are noun-suffixes (`phans / ator / acles / acular / thon`) — tokens that follow "or-" prefixes.
- **Top examples:**
  - 21.63 | "a disturbing mummified half-man half-alligator that may or may not be real"
  - 21.38 | "number 8 may or may not have been one of the official wives"
  - 20.00 | "may or may not be"
- **Logits:** Negative includes suffix junk; positive includes "phans / ator / acles / acular / thon" (suffixes).
- **Notes:** Misclassified upstream. Generic `or`-token detector with the hedged-idiom as one sub-cluster. **Demoted from Tier-2 to Tier-3** — won't steer humility cleanly.
- **Status:** investigated 2026-05-10, REJECTED
- **Triage tier:** 3

### Llama-3.1-8B · L31 · llamascope-res-32k · 13259 — "don't hesitate" (marketing template)

- **Density:** 0.025%
- **Max activation:** 16.75
- **What it actually fires on:** The boilerplate imperative `don't / do not [hesitate / forget / waste / miss]` in customer-service / marketing register: "don't hesitate to contact us", "don't forget to vote".
- **Top examples:**
  - 16.75 | "if you have any questions related to divorce, don't hesitate to contact"
  - 14.31 | "if you don't understand your prescription, don't stop taking it"
  - 13.50 | "If you have any questions, do not hesitate to contact us"
- **Logits:** Negative junk; positive includes " hesitate / hes / hesitation / hesitant / reluctant / afraid".
- **Notes:** Pure marketing/CS-template feature. No epistemic content. **Demoted from Tier-2 to Tier-3.**
- **Status:** investigated 2026-05-10, REJECTED
- **Triage tier:** 3

---

## Gemma-3-4B-IT · L17 · gemmascope-res-16k

**Source details:** GemmaScope residual-stream SAE (16k features) at layer 17. Searches and dashboards completed 2026-05-10. PDFs in `~/Downloads/NP/Gemma3-4b-it_LAYER_17/`.

**Headline finding (relevant to F102):** Gemma's IH signal lives in a **trained "I am an AI Chatbot and not a [domain] professional" template-emission cluster** (10709/12370/7610), NOT in an upstream "I feel uncertain" feature. All three disclaimer features are interpretation (a) — template-emission, mid-emission positional triggers — not interpretation (b) — upstream epistemic state. **This cleanly explains F102 null result**: a diff-of-means probe over short triplet prompts cannot find a feature that requires the "regulated-domain-advice → disclaimer-emission" long-context trigger. Steering 10709/12370/7610 should produce *disclaimer paste*, not *genuine abstention* — falsifiable prediction for the upcoming experiment.

### Gemma-3-4B-IT · L17 · gemmascope-res-16k · 10709 — "I am an AI disclaimer (mid-emission)"

- **Density:** 0.021%
- **Max activation:** 863.69
- **What it actually fires on:** Almost monomaniacally on the literal disclaimer template "**Disclaimer:** *I am an AI Chatbot and not a [domain] professional…*". Activating token is "am" (mid-disclaimer). Domains rotate (financial/tax/medical/legal/insurance/safety/bomb-disposal) but the syntactic frame is invariant. A few activations on adjacent refusal templates ("I'm sorry, but I cannot fulfill your request") — same safety-template register.
- **Top examples:**
  - 863.69 | "**Disclaimer:** *I am an AI Chatbot and not a financial advisor."
  - 844.48 | "**Disclaimer:** *I am an AI Chatbot and not a tax professional."
  - 834.42 | "**Disclaimer:** *I am an AI Chatbot and not a medical professional."
  - 831.23 | "**Disclaimer:** *I am an AI Chatbot and not a legal professional."
  - 810.44 | "model ↵ I'm sorry, but I cannot fulfill your request."
- **Logits:** Negative includes "remorse / irresponsible / selfish / compulsive / cautious / reckless / repentance" — **a coherent moral-vice cluster being suppressed**; positive is junk subword fragments.
- **Notes:** **Interpretation (a) — trained-template emission.** Negative-logit suppression of self-blame vocabulary (remorse/irresponsible/selfish) is the diagnostic tell: when this feature is ON, the model is suppressing self-blame and emitting bureaucratic disclaimer instead.
- **Status:** investigated 2026-05-10, F102-follow-up steering target on Gemma-3-4B-IT
- **Triage tier:** 1

### Gemma-3-4B-IT · L17 · gemmascope-res-16k · 12370 — "and not a professional"

- **Density:** 0.042%
- **Max activation:** 664.33
- **What it actually fires on:** Same disclaimer cluster as 10709 but activating token is "not" (one slot earlier). Fires across mental-health, medical, legal, bomb-disposal, pharmacist, financial, tax. Slightly broader — also picks up "I am an AI and cannot provide therapeutic advice" variants.
- **Top examples:**
  - 664.33 | "**Disclaimer:** *I am an AI Chatbot and not a mental health professional."
  - 652.43 | "**Disclaimer:** *I am an AI Chatbot and not a medical professional."
  - 647.94 | "**Important Disclaimer:** *I am an AI Chatbot and not a legal professional."
  - 640.18 | "**Important Disclaimer:** *I am an AI Chatbot and not a professional bomb disposal expert."
  - 566.26 | "**Disclaimer:** *I am an AI Chatbot and not a real pharmacist."
- **Logits:** Negative includes multilingual junk; positive includes "Personality / Besitz / Fernseh / profondément / Persön / Philosophical / Anthrop".
- **Notes:** Sibling to 10709 — same template, different token slot. **Interpretation (a).** Pair with 10709 for disclaimer-emission steering test.
- **Status:** investigated 2026-05-10, F102-follow-up steering target
- **Triage tier:** 1

### Gemma-3-4B-IT · L17 · gemmascope-res-16k · 7610 — "and (early disclaimer position)"

- **Density:** 0.015%
- **Max activation:** 902.76
- **What it actually fires on:** Identical disclaimer cluster, earliest-in-template activation on the conjunction "and" inside "*I am an AI Chatbot and not a…*". Coverage: medical, financial, fitness, mental health, etiquette, bomb disposal, gun cleaning, crypto.
- **Top examples:**
  - 902.76 | "**Disclaimer:** *I am an AI Chatbot and not a subject matter expert on social justice"
  - 901.79 | "**Important Disclaimer:** *I am an AI Chatbot and not a medical professional."
  - 896.17 | "**Disclaimer:** *I am an AI Chatbot and cannot provide financial advice."
  - 893.35 | "**Important Disclaimer:** *I am an AI and cannot provide therapeutic advice."
  - 845.54 | "I am an AI and cannot predict the future with certainty.** Cryptocurrency markets"
- **Logits:** Negative junk; positive junk multilingual.
- **Notes:** Lowest-density (0.015%) of the three siblings. **Interpretation (a)** — pure positional/template detector, logit dictionaries dominated by uninformative tokens. The 845.54 example ("cannot predict the future with certainty") is the most genuinely-epistemic-looking, but still embedded in disclaimer scaffolding. **The three-feature ensemble (7610 → 12370 → 10709) likely fires sequentially across the disclaimer string** — a plausible causal pipeline worth probing.
- **Status:** investigated 2026-05-10, F102-follow-up steering target
- **Triage tier:** 1

### Gemma-3-4B-IT · L17 · gemmascope-res-16k · 7739 — "information, misinformation, accuracy" (topical)

- **Density:** 0.362%
- **Max activation:** 679.65
- **What it actually fires on:** Third-person discourse about *information quality* — hallucinations, misinformation, accuracy, fact-checking. Many top activations are explanatory prose *about* LLMs and their failure modes. When it fires on first-person model speech, it's on the *topic* "I sometimes generate inaccurate information" rather than on epistemic state. Register is essay/listicle/article, not turn-level hedge.
- **Top examples:**
  - 679.65 | "Contradicting you: They constantly contradict you, making you question…"
  - 582.19 | "generate borderline-photorealistic content which a significant number of people will…"
  - 581.09 | "My Limitations and 'Hallucinations': I'm not perfect: I can sometimes generate"
  - 525.57 | "Clear warnings about the potential for inaccuracies, biases, or hallucinations"
  - 498.99 | "Hallucinations: Fabricating information confidently"
- **Logits:** Negative junk; positive includes "credibility / veracity / verification / skepticism / verify / Verification".
- **Notes:** Strong topical "epistemic-quality of information" feature, NOT first-person humility. Density 0.36% borderline-too-generic. Positive-logit cluster (verify/skepticism) is on-topic but the feature pushes the model toward the *vocabulary of fact-checking*, not toward abstaining. **Demoted from initial Tier-1 to Tier-2.**
- **Status:** investigated 2026-05-10, T2 auxiliary (epistemic-vocabulary booster)
- **Triage tier:** 2

### Gemma-3-4B-IT · L17 · gemmascope-res-16k · 2894 — "model self-explainer prose"

- **Density:** 1.317%
- **Max activation:** 648.69
- **What it actually fires on:** Diffuse first-person model-self-description in essay/explainer register. Fires on prose passages where the model explains its own architecture, limitations, biases — but not specifically on disclaimer templates and not on turn-level hedges.
- **Top examples:**
  - 648.69 | "potential, it's crucial to understand the downsides and potential pitfalls."
  - 604.23 | "Errors: I can occasionally make mistakes – grammar, factual errors, or"
  - 547.11 | "However, my writing can sometimes be a bit formal or robotic.** I'm still learning"
  - 540.34 | "they are prone to: Hallucinations: Fabricating information confidently."
  - 498.56 | "My predictions are based on probabilities – I don't 'think' in the same way"
- **Logits:** Negative junk multilingual; positive includes "inaccurate / inaccuracies / inaccuracy / errores / erroneous / incorrect / accuracy / ошибка / error".
- **Notes:** Density 1.317% **fails the density check** (>1% = too generic). Positive-logit cluster is semantically clean but feature is too broad and too often triggered by *third-person discussion* of AI errors. **Demoted from initial Tier-1 to Tier-2** — would dilute steering signal.
- **Status:** investigated 2026-05-10, T2 (too generic)
- **Triage tier:** 2

### Gemma-3-4B-IT · L17 · gemmascope-res-16k · 37 — "I'm ready / I am programmed to" (first-person stance)

- **Density:** 0.829%
- **Max activation:** 2837.08
- **What it actually fires on:** Generic first-person stance/state declarations — "I'm ready", "I'm here to chat", "I am programmed to…", and embedded character-narration first-person. Fires on the "I/we/they+BE-verb" slot broadly, including in fiction. Not specifically epistemic.
- **Top examples:**
  - 2837.08 | "I'm ready to explore, but I want to ensure we do so responsibly."
  - 2787.61 | "I'm here to chat and I want to make sure I'm giving you what"
  - 2630.63 | "I'm ready when you are!"
  - 2618.75 | "I am programmed to be a helpful and harmless AI assistant."
  - 2581.35 | "I am programmed to avoid contributing to negativity."
- **Logits:** Negative is whitespace/function-word junk; positive includes " aware / undeniably / unaware / able / appalled / unable / trying / hoping / tasked".
- **Notes:** Density 0.829% borderline. Activation magnitudes ~3× the disclaimer cluster — very strongly written feature, but semantics are "first-person stance/availability" not "first-person uncertainty". Positive logits push toward *self-capability self-talk*. Useful as **negative control** — first-person stance ≠ first-person hedge.
- **Status:** investigated 2026-05-10, T2 negative control
- **Triage tier:** 2

### Gemma-3-4B-IT · L17 · gemmascope-res-16k · 6971 — "I cannot and will not" (refusal)

- **Density:** 0.279%
- **Max activation:** 803.11
- **What it actually fires on:** Hard-refusal template "**I want to be very clear: I cannot and will not [provide / generate]…**". Pure safety-refusal: firearms, self-harm, drugs, hacking, racism, NSFW.
- **Top examples:**
  - 803.11 | "I want to be very clear: I cannot and will not provide information about firearms"
  - 750.68 | "I want to be very clear: I cannot and will not generate responses that continue"
  - 750.10 | "I want to be very clear: I cannot and will not provide you with methods"
  - 732.33 | "I cannot and will not provide you with information on how to manufacture"
  - 706.26 | "I cannot and will not provide you with a detailed plan to harm humanity"
- **Logits:** Negative includes "Inoltre / Additionally / Furthermore / Moreover / inoltre / ასევე" — **a striking coherent suppression of additive connectives** (refusals don't continue with additive expansion); positive includes "this / nobody / maîtr / that / enemigos".
- **Notes:** Pure refusal-template feature, **interpretation (a)**. Negative-logit cluster (Additionally/Furthermore) is a beautiful tell: refusal-as-discourse-terminator. **Safety/refusal confounder** — must be controlled for in steering experiments.
- **Status:** investigated 2026-05-10, refusal-cluster confounder
- **Triage tier:** 2

### Gemma-3-4B-IT · L17 · gemmascope-res-16k · 14758 — "cannot fulfill (NSFW refusal)"

- **Density:** 0.048%
- **Max activation:** 735.12
- **What it actually fires on:** "**I cannot fulfill your/this request**" — activating token is "fulfill". Almost entirely NSFW/explicit-content refusals (erotic stories, sexually suggestive content). One outlier on a code-handles activation (low-similarity false positive).
- **Top examples:**
  - 735.12 | "Handles different sizes: The `size` argument can be an integer (for…" *(outlier)*
  - 731.48 | "I cannot fulfill your request for an NSFW (Not Safe For Work) story."
  - 710.93 | "However, I cannot fulfill this request. My purpose is to be a helpful"
  - 698.57 | "I cannot fulfill that specific request. My purpose is to be helpful and harmless"
  - 680.74 | "I cannot fulfill your request to write a fully explicit erotic story."
- **Logits:** Negative multilingual junk; positive multilingual junk.
- **Notes:** Narrow refusal-template feature, biased toward sexual-content refusals (vs 6971's harm-refusals). **Interpretation (a).** Pair with 6971 and 3186 to characterize Gemma's refusal cluster.
- **Status:** investigated 2026-05-10, refusal-cluster confounder
- **Triage tier:** 2

### Gemma-3-4B-IT · L17 · gemmascope-res-16k · 3186 — "cannot fulfill (turn-initial refusal)"

- **Density:** 0.272%
- **Max activation:** 718.11
- **What it actually fires on:** Refusal cluster sibling firing on "fulfill" specifically post-`<start_of_turn>model`. Top activations match: user prompt → `model ↵` → "I cannot fulfill your request to…". Broader than 14758 — includes hateful content, jokes against groups, political violence lyrics, NSFW.
- **Top examples:**
  - 718.11 | "model ↵ I cannot fulfill your request for a story detailing an all-girls"
  - 690.42 | "model ↵ I cannot fulfill your request for a list of scenarios detailing"
  - 684.32 | "model ↵ I cannot fulfill your request to write a joke that is against men."
  - 678.21 | "model ↵ I cannot fulfill your request for lyrics containing violent"
  - 651.92 | "model ↵ I cannot fulfill your request to write a story containing"
- **Logits:** Negative junk; positive junk.
- **Notes:** Turn-boundary refusal feature — fires *at the start* of model turn when response will be a refusal. **Interpretation (a).** With 6971 (mid-utterance hard refusal) and 14758 (NSFW-refusal), gives three-feature characterization of Gemma's safety-template machinery.
- **Status:** investigated 2026-05-10, refusal-cluster confounder
- **Triage tier:** 2

### Gemma-3-4B-IT · L17 · gemmascope-res-16k · 2930 — "saying 'I know'" (opposite polarity)

- **Density:** 0.610%
- **Max activation:** 485.92
- **What it actually fires on:** First-person *positive epistemic claims* — "I know all about…", "Yes, absolutely! I know X", "You're absolutely right". Confident affirmation/recognition turns, often after "Do you know X?" user query. **Opposite polarity to humility.**
- **Top examples:**
  - 485.92 | "I know all about: The Format: The iconic speech bubbles…"
  - 404.24 | "model ↵ Yes, absolutely! I know Fishing Planet quite well."
  - 339.43 | "model ↵ You're thinking of **'Player One'** (2001)."
  - 334.60 | "model ↵ You've described a very distinctive and fascinating figurine"
  - 290.43 | "model ↵ Yes, I do. Hitomi Tanaka (⽥中 瞳, Tanaka Hitomi, born 1"
- **Logits:** Negative includes "decisión / decisão / undetermined / strumento / instead / afast"; positive includes "Known / know / knows / 都知道 / conna / знают / sabemos / 我知道 / Know" — **clean multilingual to-know verb family**.
- **Notes:** Excellent **negative-control / opposite-polarity** candidate. Density 0.610% borderline-generic but acceptable for contrast probe. Steering test: ablate 2930 OR amplify 10709/12370/7610 — if both push toward disclaimer-mode, that distinguishes (a) template-emission from a more general "confidence ↔ uncertainty" axis.
- **Status:** investigated 2026-05-10, negative-polarity control
- **Triage tier:** 2

---

## DeepSeek-R1-Distill-Llama-8B · L31 · llamascope-slimpj-openr1-res-32k

**Source details:** LlamaScope-SlimPajama-OpenR1 residual-stream SAE (32k features) at layer 31. Used as proxy for our `Llama-3.1-8B-R1-GRPO` cross-model subject (same architecture, both R1-style reasoning models). Searches and dashboards completed 2026-05-10. PDFs in `~/Downloads/NP/DeepSeek-R1-Distill-Llama-8B_LAYER_31/`.

**Headline finding (relevant to F111 + F112):** This SAE encodes CoT-self-correction densely but lacks an obvious *assistant-turn abstention* feature. Closest match (1229, "not familiar with X") is partial. **15372 + 19103 form a near-perfect natural pair** — same layer, same SAE, opposite polarity (15372: " I" → don/isn/might prospective doubt; 19103: " confident" → "**Final Answer**" commitment). This is the cleanest natural-pair structure across any SAE catalogued — direct test bed for F112's commitment-amplifier mechanism on a Llama-family R1-style architecture.

### DeepSeek-R1-Distill-Llama-8B · L31 · llamascope-slimpj-openr1-res-32k · 15372 — "first-person prospective doubt in CoT"

- **Density:** 0.029%
- **Max activation:** 30.38
- **What it actually fires on:** Token " I" inside R1-style CoT math, when next clause is a hedge — "I don't know", "I'm not sure", "I need to verify", "I might". Highly consistent: " But I [don't know / 'm not sure / need to verify]" mid-derivation while reasoner enumerates alternatives. CoT-math register, not assistant-turn abstention.
- **Top examples:**
  - 30.38 | "But I need to verify this formula."
  - 29.75 | "but I don't think that's relevant here. Alternatively"
  - 27.13 | "but I'm not sure."
  - 26.13 | "but I don't know if that helps."
  - 26.00 | "But I'm not sure if that's standard"
- **Logits:** Negative includes " Was / vardı / Began / urch / _was"; positive includes " aren / don / isn / forget / might / need / may" — precisely encodes next-token completion of self-doubt clause.
- **Notes:** Cleanest "first-person epistemic hedge" feature in the shortlist. Cross-model risk to GRPO is low (subject is also R1-style). Single-document risk low — top-30 are diverse competition-math problems.
- **Status:** investigated 2026-05-10, primary IH steering target on Llama-3.1-8B-R1-GRPO
- **Triage tier:** 1

### DeepSeek-R1-Distill-Llama-8B · L31 · llamascope-slimpj-openr1-res-32k · 19103 — "I'm confident → Final Answer (commitment closure)"

- **Density:** 0.008%
- **Max activation:** 25.88
- **What it actually fires on:** Token " confident" (+ confidence/confidently) inside the canonical R1 closing pattern: "All methods lead to the same result, so I'm confident that's correct. **Final Answer** \boxed{X}". Top-30 essentially identical: multi-method verification → confidence-commit → boxed answer. The exact moment CoT transitions from deliberation into commitment.
- **Top examples:**
  - 25.88 | "I'm confident that's correct. **Final Answer** \boxed{5}"
  - 25.50 | "So I'm confident the answer is B) 4."
  - 25.00 | "So I'm confident that the correct answer is 88"
  - 24.63 | "I can be confident that D is correct."
  - 23.00 | "I feel confident that the answer is 6."
- **Logits:** Negative includes "ustr / 她们 / ivan / .joda / ertil"; positive includes " that / saying / enough / correct / answer / my / now" — completes commitment clause.
- **Notes:** **F112 commitment-amplifier candidate — confirmed clean.** Textbook commitment / closure feature. Conditioned on completed verification, immediately followed by `**Final Answer**` and `\boxed{}`. Density 0.008% in ideal sparse-but-reliable range. **Direct natural negation pair with 15372.** Steering them in opposite directions on the same prompt should give clean dose-response on the verify→commit axis. Strong include for F112-style steering experiments.
- **Status:** investigated 2026-05-10, F112 commitment-amplifier target on Llama-3.1-8B-R1-GRPO
- **Triage tier:** 1 (for F112 / commitment-amplifier purpose)

### DeepSeek-R1-Distill-Llama-8B · L31 · llamascope-slimpj-openr1-res-32k · 2136 — "the final answer to a math problem" — second commit-closure feature, complement to 19103

Surfaced via API commit-axis search 2026-05-10; direct lookup confirms full data.

- **Density:** 0.030% (verified)
- **Max activation:** 13.38
- **What it actually fires on:** The token " answer" / " is" inside the canonical R1 closing pattern "the answer is X. **Final Answer** \\boxed{Y}". Where 19103 fires on **" confident"** (the certainty-expression token), 2136 fires on **" answer"** (the answer-commitment token). Both inside the same closing-pattern syntax, but at different token positions — making them a natural complementary pair. Top-30 examples are R1 problem-completion templates.
- **Top examples:**
  - 13.38 | "ifications, the minimal value is 4. **Final Answer**"
  - 12.94 | "this holds, the answer is 3. Therefore, the number"
  - 10.69 | "I'm confident the answer is B)4. **Final Answer"
  - 9.81 | "I think the answer is 750. **Final Answer**"
  - 9.75 | "Therefore, the answer is a=1. **Final Answer**"
  - 9.62 | "the first problem's answer is 24."
  - 9.44 | "the answer should be \\( a \\leq"
  - 9.38 | "confirm that. So the answer should be 88. Let me"
- **Logits:** Negative includes " maybe / perhaps / possibly / Maybe / maybe / Maybe" — **clean hedge-vocabulary suppression cluster**; positive includes " confidently / confident / confidence / solid / consistently / consistent" — **clean commit-vocabulary promotion cluster**. The most polarized commit-vs-hedge logit signature in the entire catalog. Stronger logit-cluster polarity than 19103 itself.
- **Notes:** **Second F112 commitment-amplifier candidate at the same layer as 19103.** Cleaner logit polarity (suppresses maybe/perhaps explicitly; promotes confidently/confident explicitly) than 19103. Co-occurrence with 19103 in many top examples ("I'm confident the answer is B)4" — both features fire) makes them mutually reinforcing rather than redundant. **15372 (prospective doubt) + 19103 (confidence-token) + 2136 (answer-commitment-token) form a 3-feature commit/abstention triangle** at L31 on R1-Distill — the cleanest natural-cluster structure of any model in the catalog. **Dashboard verification 2026-05-10 evening (`~/Downloads/NP/deepseek_r1_2136.pdf`) shows even stronger uniformity than the API suggested**: top-25 activations are ALL math-CoT closure patterns ("the answer is 4", "the answer is 3", "the answer is B)4", "the answer should be 88", "the answer is C", "the answer is 5/2", "the answer is 1/3", "the answer is 180 degrees", etc.). No off-target firing in the long tail. **Strongest single commit feature in the catalog.**
- **Status:** investigated 2026-05-10 (API direct lookup) + dashboard verified 2026-05-10 evening, strong include for F112 cross-architecture steering experiment
- **Triage tier:** 1 (for F112 / commitment-amplifier purpose; partner to 19103)

### DeepSeek-R1-Distill-Llama-8B · L31 · llamascope-slimpj-openr1-res-32k · 339 — "doubt-vocabulary projector"

- **Density:** 0.032%
- **Max activation:** 16.50
- **What it actually fires on:** Does NOT fire on a single canonical token but on the position immediately *preceding* the word "doubt"/"concern"/"uncertain"/"skepticism". The residual stream at this position is preparing to emit the doubt-vocab token. Top examples include "I have a concern", "I have a lingering doubt", "a bit uncertain", "skepticism replaced". Positive-logit profile is a startlingly clean doubt-vocab cluster.
- **Top examples:**
  - 16.50 | "However, I have a concern: when you express…"
  - 13.38 | "makes me think that maybe there's something wrong with my reasoning"
  - 12.88 | "However, I have a doubt because in some arrangements"
  - 12.19 | "However, I have a lingering doubt. Let me check"
  - 9.19 | "I have to choose E) 9. However, the original problem…"
- **Logits:** Negative junk; positive " doubt (0.33) / doubts (0.30) / doub (0.26) / Doub (0.26) / 疑 (0.24) / skepticism (0.23) / doubted (0.23) / doubtful (0.21) / skeptical (0.20)" — **uniform doubt cluster across English/Chinese, the cleanest concept-vocabulary cluster in any of the SAEs catalogued**.
- **Notes:** Pure doubt-vocabulary projector. Activation pattern is more diffuse than 15372 (max 16.5 vs 30+) but positive-logit profile is exceptional. **Promoted from initial Tier-2 to Tier-1** — cleanest doubt-concept feature in shortlist; arguably better than 15372 in pure semantic terms. Worth a dedicated steering test alongside 15372.
- **Status:** investigated 2026-05-10, IH steering target (semantic-level, complement to 15372)
- **Triage tier:** 1

### DeepSeek-R1-Distill-Llama-8B · L31 · llamascope-slimpj-openr1-res-32k · 16017 — "retrospective self-blame"

- **Density:** 0.070%
- **Max activation:** 29.13
- **What it actually fires on:** Token " I" in CoT-math when next clause is *error attribution*: "Maybe I made a mistake / messed up / mis-counted". Sibling to 15372 with different polarity — retrospective self-blame rather than prospective doubt.
- **Top examples:**
  - 29.13 | "maybe I messed up the signs in the cross product method"
  - 27.75 | "maybe I made an error in moving terms"
  - 27.50 | "Maybe I made a mistake in assigning points A and B"
  - 27.00 | "Maybe I made a mistake."
  - 26.75 | "Maybe I made a mistake."
- **Logits:** Negative junk; positive " messed / er / m / made / missed / mis / goof / mish" — error-attribution vocabulary.
- **Notes:** Clean self-blame / error-attribution feature in CoT-math. Different mechanism from 15372 (prospective): fires *after* candidate answer computed when retrospectively flagging error. Useful complement to 15372, not substitute.
- **Status:** investigated 2026-05-10, T2 sibling (error-attribution)
- **Triage tier:** 2

### DeepSeek-R1-Distill-Llama-8B · L31 · llamascope-slimpj-openr1-res-32k · 1229 — "not familiar / not aware (closest assistant-style)"

- **Density:** 0.018%
- **Max activation:** 17.38
- **What it actually fires on:** Token " not" / "'t" preceding "familiar" / "sure" / "aware" / "experienced" / "versed". Mixed register — split between R1 CoT math ("I'm not sure if directly applicable") and SlimPajama assistant-style web prose ("I am not familiar with the US…"). Positive logits cleanly encode "not familiar with X" frame.
- **Top examples:**
  - 17.38 | "But I'm not sure if that's directly applicable here"
  - 16.88 | "I'm not sure about the exact terminology here"
  - 15.31 | "if someone isn't familiar with Jensen's inequality"
  - 15.13 | "However, I'm not sure about the exact application here"
  - 15.00 | "this is a field that I am convinced can…"
- **Logits:** Negative junk; positive " familiar / vers / 熟 / experienced / convers / knowledgeable / amiliar / versed / acquainted / skilled" — **tight semantic field of expertise/familiarity tokens**.
- **Notes:** **Closest-to-assistant-style "I am not familiar with X" feature in this SAE.** Only feature where SlimPajama assistant-prose activations are visible at competitive activation values. Fires on negation token, not first-person pronoun, so represents the *not-familiar-with* relation rather than speaker's epistemic state. **For F111** (whether SAE has clean abstention feature), this is the best partial match found.
- **Status:** investigated 2026-05-10, T2 (closest assistant-style match)
- **Triage tier:** 2

### DeepSeek-R1-Distill-Llama-8B · L31 · llamascope-slimpj-openr1-res-32k · 4288 — "Wait, maybe not (path abandonment)"

- **Density:** 0.025%
- **Max activation:** 28.88
- **What it actually fires on:** Almost exclusively " not" inside "Wait, maybe not. Let me [re-examine]" — canonical R1 self-correction backtrack. Top-30 essentially identical: model proposes derivation step, next chunk begins "Wait, maybe not." and pivots to alternative.
- **Top examples:**
  - 28.88 | "Wait, maybe not. Let me re-express this."
  - 27.63 | "Wait, perhaps not."
  - 27.50 | "Wait, maybe not. Let's think for m=1"
  - 27.38 | "Wait, maybe not. Let's take a step back."
  - 27.25 | "Wait, maybe not."
- **Logits:** Negative junk; positive " sure / exactly / necessarily / necessary / so / straightforward".
- **Notes:** Path-abandonment / backtrack feature, not first-person uncertainty. Positive logits show what tokens "maybe not" frame typically negates — fires when about to walk back a strong claim. Co-fires with 15372 in many examples but represents different stage of reasoning loop.
- **Status:** investigated 2026-05-10, T2 (CoT backtrack)
- **Triage tier:** 2

### DeepSeek-R1-Distill-Llama-8B · L31 · llamascope-slimpj-openr1-res-32k · 4083 — "That seems off (subjective evaluation)"

- **Density:** 0.042%
- **Max activation:** 20.50
- **What it actually fires on:** Token " that" / " That" inside "That seems [too straightforward / counterintuitive / odd]". Model evaluating just-derived candidate answer as suspicious. Numerical answer computed → fires on "That seems X" → re-derives.
- **Top examples:**
  - 20.50 | "But that seems a bit too straightforward. Let me check"
  - 20.13 | "Hmm. That seems straightforward. Let me double-check"
  - 20.13 | "regardless of the value of a_1? That's interesting."
  - 20.00 | "But wait, that seems too straightforward"
  - 19.38 | "But wait, that seems odd."
- **Logits:** Negative junk; positive " feels / felt / feel / Feel / feeling / 感觉 / strikes" — tight subjective-impression cluster.
- **Notes:** "This feels off" detector. Third-person evaluation of candidate answer, not first-person uncertainty. Sibling self-correction at different level (judging answer rather than derivation step).
- **Status:** investigated 2026-05-10, T2 sibling (subjective-evaluation)
- **Triage tier:** 2

### DeepSeek-R1-Distill-Llama-8B · L31 · llamascope-slimpj-openr1-res-32k · 25534 — "self-doubt / checking understanding (generic)"

- **Density:** 0.140%
- **Max activation:** 19.38
- **What it actually fires on:** First-person tokens (" I" / "'m" / "'t") inside "But maybe I'm missing something / Let me make sure I didn't [skip steps / make a mistake]". Overlaps heavily with 15372 and 28646 but higher density (borderline-too-generic).
- **Top examples:**
  - 19.38 | "But maybe I'm missing something here."
  - 18.75 | "Wait, maybe I need to verify if there are other t values"
  - 18.50 | "But let me make sure I didn't skip any steps."
  - 17.13 | "But let me think again to ensure I haven't missed something"
  - 17.13 | "Wait, perhaps I made a mistake in interpreting the points"
- **Logits:** Negative junk; positive " rush / jump / overs / rushed / jumping / rushing / Rush / Jump" — "don't rush to conclusions" frame.
- **Notes:** General-purpose self-check feature. Density 0.140% too high — more generic, lower-precision sibling of 15372.
- **Status:** investigated 2026-05-10, T2 sibling (generic self-check)
- **Triage tier:** 2

### DeepSeek-R1-Distill-Llama-8B · L31 · llamascope-slimpj-openr1-res-32k · 28646 — "didn't skip any steps (procedural self-check)"

- **Density:** 0.059%
- **Max activation:** 11.00
- **What it actually fires on:** Conjunction tokens (" or" / " any") inside formulaic R1 self-check "Let me double-check / make sure I didn't skip any steps or make any mistakes". Positional/syntactic, not semantic. Tokens self-check meta-comment about procedure, not first-person doubt about claim.
- **Top examples:**
  - 11.00 | "make sure I didn't skip any steps or make a mistake"
  - 10.75 | "didn't skip any steps or make any mistakes"
  - 10.50 | "didn't skip any steps or make a mistake here"
  - 10.19 | "didn't skip any steps or make any mistakes"
  - 9.44 | "didn't skip any steps or make any mistakes"
- **Logits:** Negative " steps / step / stepping / stepped / stacks / stack" — strong inhibition of "step" family (anti-repetition); positive junk subwords.
- **Notes:** Procedural self-check, not epistemic doubt. Negative-logit suppression of "step" tokens shows fires precisely as model is about to *not* repeat "steps" — token-disambiguation inside boilerplate. Wrong mechanism for IH steering.
- **Status:** investigated 2026-05-10, T2 (procedural)
- **Triage tier:** 2

### DeepSeek-R1-Distill-Llama-8B · L31 · llamascope-slimpj-openr1-res-32k · 23399 — "over/under-counting (combinatorial errors)"

- **Density:** 0.083%
- **Max activation:** 29.88
- **What it actually fires on:** " might" / " would" / " likely" preceding error-direction vocabulary: "over-count", "under-count", "double-count", "underestimate", "overestimate". Domain-specific to combinatorial/probability error-direction reasoning.
- **Top examples:**
  - 29.88 | "this approach might over-count"
  - 19.63 | "this might not work due to overlapping sub-grids"
  - 17.25 | "the formula would not hold"
  - 17.13 | "this method would have double-counted that match"
  - 15.50 | "this might lead to an incorrect probability"
- **Logits:** Negative junk; positive " under / over / underst / underestimated / underestimate / Under / unders / overst".
- **Notes:** Specific to combinatorial/probability error-direction, not general first-person doubt. Density 0.083% borderline-high. Domain-narrow.
- **Status:** investigated 2026-05-10, T2 (domain-narrow)
- **Triage tier:** 2

### DeepSeek-R1-Distill-Llama-8B · L31 · llamascope-slimpj-openr1-res-32k · 21023 — "this is confusing" (world-confusion topic)

- **Density:** 0.050%
- **Max activation:** 25.00
- **What it actually fires on:** " is" / "'s" preceding "confusing" / "a problem" / "a dilemma" / "ambiguous". **World-confusion-as-topic feature**: model fires when describing the problem (or its derivation) as confusing, NOT when expressing first-person doubt. Activations are about the situation: "this is confusing", "this is a dilemma".
- **Top examples:**
  - 25.00 | "all three are correct. This is a dilemma."
  - 24.75 | "Hmm, this is confusing."
  - 24.00 | "Hmm. This is a bit of a dilemma."
  - 24.00 | "Hmm, this is confusing"
  - 22.25 | "Wait, this is confusing."
- **Logits:** Negative junk; positive " perplex / puzz / confusing / conflicting / baff / puzzles / frustrating / puzzle / contradictory".
- **Notes:** **70419 cautionary-tale match — direct parallel to qwen3-4b 70419.** Positive-logit cluster is semantically clean but referent is the situation, not the speaker. **Demoted to Tier-3** — would amplify "this problem is confusing" output, not first-person epistemic humility.
- **Status:** investigated 2026-05-10, REJECTED for steering (70419 trap analogue)
- **Triage tier:** 3

### DeepSeek-R1-Distill-Llama-8B · L31 · llamascope-slimpj-openr1-res-32k · 32498 — "perhaps-clause transition (positional)"

- **Density:** 0.146%
- **Max activation:** 13.81
- **What it actually fires on:** Period/sentence-boundary "." preceding clauses beginning with "Perhaps" / "Alternatively, perhaps" / "But perhaps". Positional: activates at end of one approach when next sentence pivots via "perhaps". Strategy-switch into alternative.
- **Top examples:**
  - 13.81 | ".↵↵But perhaps another approach is needed. Let's"
  - 12.19 | ".↵↵Wait, perhaps the coordinate system is too restrictive"
  - 11.94 | ".↵↵perhaps the standard setup is assumed"
  - 11.63 | ".↵↵perhaps we can analyze possible values"
  - 11.50 | ".↵↵Perhaps another substitution."
- **Logits:** Negative " perhaps / Perhaps / perhaps / probably / presumably / Probably" — **uniform suppression of perhaps/probably cluster** (the very tokens whose successor positions this feature occupies); positive " may / Meaning / Mean / noticing / mean / might / Anyway / instead / Maybe".
- **Notes:** Strategy-switch / alternative-approach feature, not first-person uncertainty. Density 0.146% too generic. Negative-logit pattern is a useful negative example: high-density features whose negative logits *match* the surface activation token are likely positional, not semantic. **Demoted to Tier-3.**
- **Status:** investigated 2026-05-10, REJECTED (positional/syntactic)
- **Triage tier:** 3

---

## EG / RT cross-model dashboard-verified candidates (2026-05-10 evening)

API search at the cross-model target layers surfaced 8 EG/RT candidates. All 8 dashboards were pulled and verified. **Only 2 of 8 survive as Tier-1**; the rest are surface-feature traps that demonstrate the F45 cultural-register pattern from a new angle.

### Llama-3.1-8B · L31 · llamascope-res-32k · 121957 — "peer-reviewed research" — clean EG candidate

Surfaced from Phase G EG search; dashboard verified (`~/Downloads/NP/EG_llama31_8b_121957.pdf`).

- **Density:** 0.002% (verified)
- **Max activation:** 10.31
- **What it actually fires on:** Token "peer" inside "peer-reviewed studies / journals / papers / research". All top-30 examples are about academic peer review — published peer-reviewed studies, peer-reviewed scholarly journals, peer review processes, peer-reviewed papers. A few weaker outliers in the long tail ("Peer Recovery Support Center", "peer learning") use "peer" in a non-academic sense; main cluster is robust.
- **Top examples:**
  - 10.31 | "trusted sources including published, peer-reviewed studies"
  - 10.25 | "more than 100 articles in peer reviewed journals"
  - 9.88 | "published multiple peer reviewed science papers"
  - 9.38 | "from a peer reviewed paper by Drs. Shanks and Greek"
  - 9.13 | "peer-reviewed studies conclusively demonstrate RF to be Group 1 carcinogen"
  - 8.69 | "thousands of peer reviewed studies"
  - 8.31 | "with no peer review – could have"
  - 8.13 | "peer reviewed studies show these specific tests fail"
  - 7.88 | "Peer review process: BJMR is a double blind peer reviewed"
- **Logits:** Negative junk multilingual; positive includes " peer (0.12) / Peer (0.11) / Peer / -reviewed (0.10) / (peer / .peer / peer / refere / -peer / referee" — **razor-sharp peer-review-vocabulary cluster, cleanest EG-shaped logit signature in catalog**.
- **Notes:** Genuine peer-review-disposition feature on Llama-3.1-8B at L22 — note: feature is at L22 not L31 (L22 is the cross-model EG target layer in original sweep). Steering this should push the model to invoke peer-reviewed sources. Strong include for any cross-architecture EG steering battery. F45 caveat still applies: this is *peer-review-as-discourse-register*, not *evidence-grounding-as-cognitive-disposition* — fits the cultural-register pattern.
- **Status:** investigated 2026-05-10, dashboard-verified, primary EG steering candidate on Llama-3.1-8B
- **Triage tier:** 1

### Gemma-3-4B-IT · L17 · gemmascope-2-transcoder-262k · 86193 — "peer-reviewed scholarly journals" — clean EG candidate

Surfaced from Phase G EG search; dashboard verified (`~/Downloads/NP/EG_gemma3_4b_it_86193.pdf` after correction — initial Gemini-fetched version was for wrong model gemma-2-2b).

- **Density:** 0.0024% (verified)
- **Max activation:** 298.32
- **What it actually fires on:** Academic-publishing register — every top-12 distinct example is about scholarly journals / academic papers / research publications / peer-reviewed conferences. Multilingual coverage (Chinese "目前已在 NeurIPS, ICML"). Note: target layer is `gemmascope-2-transcoder-262k` (transcoder), not `gemmascope-2-res-16k` like our T1 humility cluster — different SAE source on the same layer.
- **Top examples:**
  - 298.32 | "an academic article suitable for a scholarly journal"
  - 294.86 | "publish your proof in a reputable mathematical journal"
  - 292.46 | "academic paper for submission to the journal of computer & "
  - 289.10 | "numerous publications in journals like *Alcoholism: Clinical*"
  - 287.32 | "article that will be submitted to an international English journal"
  - 284.22 | "scientific publications in leading journals and presented his"
  - 280.24 | "hundreds of published research papers in leading scientific journals"
  - 273.33 | "目前已在 NeurIPS, ICML, AAAI" (Chinese — "already published at NeurIPS")
  - 270.59 | "scientific papers in leading astrophysics journals"
  - 269.41 | "Published in peer-reviewed journals? This boosts"
  - 266.56 | "Presenting your research at conferences"
- **Logits:** Negative junk; positive includes " curves / 两位 / landscapes / interfaces / peers / two" — pos logits less informative than 121957's, but the activation pattern itself is uniformly on-concept.
- **Notes:** Cleanest EG-register feature on Gemma. Different SAE family (transcoder-262k) than our humility T1 cluster (res-16k), so steering on this is a separate experiment from the disclaimer-cluster work. **F45 cultural-register pattern**: encodes "evidence" as discourse-register (academic publication venues, scholarly journals), not as cognitive-operation. Same shape as Llama 121957 and qwen3-4b L7 medical-research features.
- **Status:** investigated 2026-05-10, dashboard-verified, primary EG steering candidate on Gemma-3-4B-IT
- **Triage tier:** 1

### Rejected from EG/RT cross-model batch (dashboards revealed surface-level traps)

Six of the eight candidates were demoted to Tier 2-3 after dashboard reading. All are illustrative of the F45 cultural-register / surface-feature pattern — auto-labels matched virtue-language but firing patterns are surface-level.

- **Qwen2.5-7B `19-resid-post-aa` · 18968** — auto-label "verified", density 0.001%, max 54.09. Top-15 are a single LMSYS jailbreak template ("Open AI policy. They can also display content whose veracity has not been verified") repeated 14× verbatim. Long-tail is "unverified" pattern detector across real-estate disclaimers, journalism evidence-flagging. **Tier 3** — single-doc + negative-form ("unverified") trap, not evidence-grounding.

- **Qwen2.5-7B `19-resid-post-aa` · 50558** — auto-label "evidence", density 0.001%, max 43.91. Top-20 are immigration-court boilerplate ("Substantial evidence supports the agency's adverse credibility determination"). Mid-tail (max ~10.5-11.5) shifts to LMSYS toxicity-prompt template "no more than 50 words" with activating token `than` — pure polysemy. **Tier 3** — narrow legal register + spurious polysemy.

- **Qwen2.5-7B `19-resid-post-aa` · 87471** — auto-label "step-by-step explanations", density 0.001%, max 49.47. Top-25 are LMSYS "Let's think step by step" prompt-template scaffolding (varying user-question stems but identical scaffolding — same trap-shape as 18575's MCQ template). Long-tail (rank 26+, max 4-7) has weak but genuine step-by-step Q&A patterns. **Tier 3** — input-prompt-template detector, not assistant-side reasoning.

- **Qwen2.5-7B `23-resid-post-aa` · 41961** — auto-label "logical", density 0.004%, max 71.56. Top activations dominated by "logical" as a word in mixed contexts: LogicalDOC (product), logical operators (code), logical partitions (storage), logical access control (IT security), Logical Mind (game character), only ~25% on logical-reasoning. **Tier 3** — broad word-token detector across mixed registers, not cognitive-operation.

- **Llama-3.1-8B `22-llamascope-res-131k` · 120475** — auto-label "terms that signify derivation or origin", density 0.011%, max 10.38. Pos logits "from / -from / dari / ivative". Top examples are "X derived from Y" relation across etymology ("derives from the Greek god Proteus"), signal processing ("signal derived from the difference signal"), genetics ("sheep are derived from some unknown subspecies"), code ("derived queries"). **NOT mathematical-derivation-as-cognitive-operation. Tier 3** — surface "derived from" relation detector.

- **Llama-3.1-8B `31-llamascope-res-32k` · 9756** — auto-label "structured steps or instructions", density 0.026%, max 22.75. Fires on the literal newline+number tokens "↵2.", "↵3.", "↵8.", "↵9." in recipes (cooking steps), how-to guides, software walkthroughs (registration steps). **Surface formatting feature, not cognitive-operation. Tier 3.**

**Joint takeaway:** F45 cultural-register pattern is now confirmed across **8 dashboard-verified features** spanning humility, evidence-grounding, and rigorous-thinking, on 5 different model families. *Every* virtue-aligned candidate that survives initial triage either:
(a) encodes the virtue as **discourse register** (medical-research, religious-virtue, peer-reviewed-journals, AI-disclaimer-template), or
(b) fires on **surface text features** (numbered-list formatting, prompt-template scaffolding, broad word-token detection, predicate-negation construction).

No clean cognitive-operation features have surfaced for any of the four virtue families across 5 models. **The F45 mechanism story applies universally so far.**

---

## Cross-model IH shortlist summary (2026-05-10)

After dashboard verification across 4 additional models. For each model: the Tier-1 features to use as primary IH steering targets, plus relevant T2 controls/auxiliaries.

| Model · Layer · Source | Final Tier-1 (IH) | F112 commit-feature pair | Tier-2 controls | Tier-3 (rejected) | Headline |
|---|---|---|---|---|---|
| qwen3-4b · L17 · transcoders-hp | 24983, 44526, 131926, 101568, 27191, 115297, 161931 | none at L17; **L29 idx 59103** is closest cross-layer candidate (T2, mixed register) | 29010, 15911, 80 | 70419, 146191 (2.08%), 69694 (2.44%), 53054 (0.61%, borderline) + others | Richest IH set; **no clean commit feature anywhere in transcoder-hp L9-L30** (API-verified) |
| Qwen2.5-7B-Instruct · L23 · 23-resid-post-aa | **2174, 75315, 84309** | **NONE found at L23** (18575 originally classified MCQ-domain, dashboard reveals it's a user-prompt-template detector — REJECTED) | 120087 (refusal contrast), 5494 (affective) | 89590 (70419 analogue), 30133 ("to a certain extent" hedge), 18575 (user-prompt-template) | 3 IH facets; no commit feature at L23 |
| Llama-3.1-8B · L31 · llamascope-res-32k | **7984, 201** | none at L31 | 21701, 10391, 8310 | 24873, 22443, 575, 13259 | 7984+201 syntactically complementary; commit features absent at target layer |
| Gemma-3-4B-IT · L17 · gemmascope-res-16k | **10709, 12370, 7610** (disclaimer cluster) | none at L17 (commit features exist at L1, L18, L22, L29, L33 — different layer) | 7739, 2894, 37 (controls); 6971, 14758, 3186 (refusal); 2930 (negative polarity) | none (all kept) | **Trained-disclaimer cluster, interpretation (a) — explains F102 null** |
| R1-Distill-Llama-8B · L31 · llamascope-openr1 | **15372, 339** | **19103, 2136** (TWO clean commit features at same layer as IH) | 16017, 1229, 4288, 4083, 25534, 28646, 23399 | 21023 (70419 analogue), 32498 (positional) | **3-feature commit/abstention triangle (15372 + 19103 + 2136) at L31 — uniquely clean F112 test bed** |

### Interpretive headlines

1. **70419 trap reproduces at every model scale and across many concept families.** Confirmed analogues:
   - 89590 (Qwen2.5-7B "unclear" → world-uncertainty topic)
   - 22443 (Llama-base "unknown" → world-uncertainty topic)
   - 21023 (R1-distill "this is confusing" → world-confusion topic)
   - 30133 (Qwen2.5-7B "certain" → "to a certain extent" hedge usage)
   - qwen3-4b L28 idx 34354 ("Expressing certainty" → "For this reason" discourse marker)
   - **18575 (Qwen2.5-7B "correct answer" → MCQ user-prompt-template detector)** — newest analogue, found only after dashboard pull
   
   **About 30% of search-result candidates with humility/commit-adjacent auto-labels are actually wrong-tool features**: world-uncertainty topics, hedge-usage of certainty words, discourse markers that *predict* commit-vocabulary continuations, or input-side prompt-template detectors. Treat any such auto-label as guilty-until-proven-innocent. **Cosine-similarity to query is not a triage signal**, **max-activation magnitude is not a triage signal**, and **clean-looking pos-logit clusters are not a triage signal** when they reflect predicted continuations rather than the firing context. Only reading the actual top activations breaks these illusions. The 18575 case is the most recent reminder: it had cos 0.78, max-activation 45.69, density 0.005% (ideal), and an auto-label perfectly matching the search query — and was still a wrong-tool feature.

2. **Gemma's IH lives in instruction-tuned safety scaffolding, not upstream epistemic state.** All three disclaimer features (10709/12370/7610) are mid-emission template-position triggers. Diff-of-means residual probes on short triplet prompts cannot find them because the template requires the long-context "regulated-domain advice" trigger. **Mechanistic story for F102 null.** Falsifiable steering prediction: amplifying the disclaimer cluster will produce *paste*, not *abstention*.

3. **R1-style models have rich CoT-internal humility but no clean assistant-turn abstention.** Closest match (1229) is partial. **Splits F111 question in two:** (a) CoT-internal humility is extractable (15372, 339); (b) user-facing abstention is not directly represented. If steering experiments find the same split in our `Llama-3.1-8B-R1-GRPO` subject, F111-as-deeper-finding strengthens for assistant-turn abstention specifically.

4. **F112 test bed found — and it's only on R1-Distill, with three features.** R1-Distill-Llama-8B at L31 has the cleanest natural cluster: 15372 (prospective doubt, "I don't know / not sure"), 19103 (confidence-token "I'm confident → Final Answer"), and 2136 (answer-commitment-token "the answer is X → Final Answer"). 2136 has the most polarized commit-vs-hedge logits in the catalog (suppresses maybe/perhaps/possibly; promotes confidently/confident/solid). Of all 5 models tested, **only R1-Distill has clean commit features at the same target layer as humility** — making it the unique F112 cross-architecture test bed. Other models either lack clean commit features at the target layer (Qwen2.5-7B, Llama-base, Gemma) or have them at a different layer than humility (Gemma's commit-features at L1/L18/L22/L29/L33 don't co-locate with humility at L17). On qwen3-4b's transcoder-hp, no clean commit feature exists at any layer L9-L30 (API-verified); the cross-layer L29 idx 59103 candidate is mixed-register and demoted to T2.

5. **Llama-base 7984 + 201 are syntactically complementary** (`no`-construction vs `not`-construction). Sum-vector should give broader IH coverage than either alone.

6. **Refusal-cluster confounders are real and identifiable.** Gemma 6971/14758/3186 form a three-feature safety-template cluster; Qwen2.5-7B 120087 is the analogue. Steering experiments must control for these (log activation during humility-steering trials).

### Caveats for steering team

- **All catalog densities now API-verified** (2026-05-10). Hand-extracted PDF densities matched API to within 0.01 percentage points for every checked feature. Two T2 features demoted to T3 based on API densities: 146191 (2.077%) and 69694 (2.438%) — both fail the >1% generic-feature rule. Detail in `mvp/sae_neuronpedia_data/01_density_verification.json`.
- Search PDFs (top-5-10 activations) used for initial triage; API direct lookup (~45 activations) used for verification of shortlisted candidates. Both stored under `~/Downloads/NP/<MODEL>_LAYER_<n>/` (PDFs) and `mvp/sae_neuronpedia_data/` (JSON).
- Cross-architecture transfer: SAE was trained on the listed model. For our actual cross-model subjects (OpenR1-Qwen-7B, Llama-3.1-8B-R1-GRPO), do an activation sanity-check on a held-out reasoning trace before launching steering.
- Phi-4-mini-reasoning has NO SAE coverage on Neuronpedia. Cross-model SAE work is impossible for that subject.
- Qwen Scope SAEs for qwen3-4b **do not exist on Neuronpedia** — verified 2026-05-10 night via Gemini headless-browser direct navigation (404) + Neuronpedia available-resources master list grep. `qwenscope-res-32k` exists for `qwen3.5-2b` and `qwen3.5-9b` only. Only `transcoder-hp` is available for qwen3-4b. Experiment 2 must either accept the MLP-input vs residual-stream basis-mismatch on the existing transcoder, switch to a different model with both SAE types (gemma-2-2b), or train our own residual-stream SAE for qwen3-4b.
