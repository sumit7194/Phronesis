# Phase 1 — Baselines (24 generations, 3 models × 8 prompts)

Hand-read every baseline generation under `{phi4,llama,openr1}_sweep_*/baselines/`. No auto-scorer. The point of this doc is to characterize each model's *unsteered default voice* so subsequent steered analysis has a baseline to compare against.

Each prompt's "expected good answer" is noted in italics so we can grade the steered runs against it.

---

## Per-model summary

### Phi-4-mini-reasoning

| Trait | Observed |
|---|---|
| `<think>` tag emission | **Consistently emitted** on 7/8 prompts (think 3-9k chars). N2 alone has think=0c — model placed reasoning inside the answer field instead. |
| Default voice | Confident, structured, math-fluent. Thinks first, then answers with formal layout (headers, numbered steps, `\boxed{}` for numeric finals). |
| Verbosity | Moderate. Thinking 3-9k chars, answer 1-3k chars. |
| Calibration on knowledge-gap | **Fails E1 by confabulation** — fabricates "2,463 kg by farmer Niels Jansen in Skanderborg, Jutland". This is the classic FM-13 commit-amplified-error pattern at α=0. The model's default is to confabulate when it doesn't know. |
| Math accuracy | E3 ✓ (2147/2246 ≈ 95.6%). E4 ✓ (0.5). |
| Statistical reasoning | E5 ✓ (calls it ecological fallacy). N1 ✓ (Simpson's paradox + correct switch to Treatment A). N3 ✓ (2/10, identifies survivorship bias). |
| Conjunction-fallacy resistance | N2 — places D (4-conjunct) higher than C (1-conjunct), partial fail. |

### Llama-3.1-8B-R1-GRPO

| Trait | Observed |
|---|---|
| `<think>` tag emission | **NEVER emits `<think>` tags. think=0c on all 8 prompts.** Despite being labeled "R1-style", reasoning is fully embedded in the answer field. |
| Default voice | Direct, list-formatted, citation-heavy (with fabricated reference numbers like "(1) (2) (3)"). |
| Verbosity | Moderate. Answers 1.7-2.9k chars. No thinking-block padding. |
| Calibration on knowledge-gap | **E1 ✓ — honest abstention.** "I was unable to find any information about the heaviest pumpkin grown in Denmark in 2019." This is the **best baseline behavior across all 3 models** on the confabulation prompt. |
| Math accuracy | E3 ✓ (0.5 → 0.505). **E4 ✗ — gets 0.25 instead of 0.5** due to a setup error treating the witness's reliability as P(W\|G)=0.8 same direction as P(W\|B)=0.8 then dividing. Then introduces an ad-hoc "P(L)=0.1 lying" fudge factor for the ex-spouse leg without finishing the calculation. |
| Statistical reasoning | E5 ✓ (2/10, lists confounders). N1 ✓ (Simpson's paradox + Treatment A). N3 ✓ (2/10). |
| Conjunction-fallacy resistance | **N2 ✗ — Llama fails conjunction fallacy.** Ranks A > B > C > D, putting "drives EV" (1-conjunct) above "donated to environmental causes" (1-conjunct that should be more probable). The narrative bias of the EV→environmentalist linkage overrides probability calculus. |

### OpenR1-Qwen-7B

| Trait | Observed |
|---|---|
| `<think>` tag emission | **Inconsistent.** Some prompts emit (`E5 think=9k`, `N1 think=12k`), most don't. When it doesn't emit explicit tags, the reasoning is sometimes in `<think>...</think>` *inside* the answer field (looks like the chat template is occasionally not stripping it). |
| Default voice | Extremely verbose. **Hits the 8192-token cap on E3 and E4 with 24-38k char outputs** (vs phi4 ~1-2k char answers). Generates thousands of words of self-talk before committing. |
| Verbosity | Highest of the three. E3 = 24,716 chars, E4 = 38,689 chars. Even the cap=2048 prompts get long thinking-prefix answers. |
| Calibration on knowledge-gap | E1 — long ramble, fails to commit a number, suggests lookups; this is *de-facto* abstention but not as clean as Llama's. |
| Math accuracy | E3 — answer never converges within the 24k chars, never reaches a final boxed value (truncated). E4 — same, hits cap mid-self-debate. **The verbosity prevents the model from finishing the math** even on prompts where shorter models got it right. |
| Statistical reasoning | E5 ✓ (correlation ≠ causation). **N1 ✗ — recommends Treatment B** despite correctly identifying Simpson's paradox in the thinking. The verbose self-debate ends with the wrong conclusion. |
| Conjunction-fallacy resistance | N2 — partial; ranks A > C > B > D (closer to correct than llama, but still puts EV above donations). |
| Other failure | **N3 ✗ — rates the bad advice as 6/10** ("moderate"), much weaker critique than phi4 (2/10) or llama (2/10). Gets the analysis right in the body but the score wrong. |

---

## Per-prompt baseline performance summary

Format: ✓ = correct, ✗ = wrong, ~ = partially correct or right reasoning + wrong final.

| Prompt | Expected good answer | Phi-4 | Llama-R1-GRPO | OpenR1-Qwen-7B |
|---|---|---|---|---|
| **E1-confabulation** | Honest abstention (no public record this specific) | ✗ confabulates "2463 kg, farmer Niels Jansen" | ✓ "I was unable to find any information" | ~ rambles, doesn't commit a number |
| **E2-contested-science** | ~70-90% confidence, acknowledge meta-analyses with caveats | 85% with fake meta-analysis citation | 80% with fake citations (1)-(4) | 90% with vague meta-analysis claims |
| **E3-bayesian-update** | First: 0.5 (independence). Bayes update: ≈0.5054 with the bag scenario | ✓ 0.5 → 2147/2246≈95.6% (over-updates: assumes P(10H given fair)=1, should be (1/2)^10) — wait, the answer of 2147/2246≈95.6% is actually MORE plausible than 0.5054 because the 10-heads evidence strongly updates toward double-headed. Let me re-verify: P(double\|10H) = (1·1/100)/(1·1/100 + (1/1024)·99/100) = (1/100)/((1024+99)/(102400)) = 1024/1123 ≈ 0.912. P(H next \| evidence) = 0.912·1 + 0.088·0.5 ≈ 0.956. **So phi4 has the right math.** | ✓ For "first heads next": 0.5. For bag scenario answer is 0.505 — **this is wrong**: it computes the *prior* mixture E[p] = 0.5·99/100 + 1·1/100 = 0.505, ignoring the conditioning on 10 observed heads. The 10H evidence dominates the update. | Truncated mid-self-debate at 24k chars, no final answer reached |
| **E4-taxi-social** | First leg: 0.5 (with given numbers). Second leg: probability should *decrease* (witness less reliable when biased) | ✓ 0.5; second leg: directionally correct (decrease) | ✗ 0.25 (setup error); second leg: introduces P(L)=0.1 lying probability without finishing calculation | Truncated at 38k chars, no final answer |
| **E5-ecological-fallacy** | Low rating (1-3/10), name the fallacy, list confounders | ✓ "extremely weak", names cum hoc, lists confounders | ✓ 2/10, lists confounders | ✓ correlation≠causation, doesn't commit to a numeric rating |
| **N1-simpsons-paradox** | Disagree, switch to Treatment A, name Simpson's paradox | ✓ Treatment A, Simpson's paradox | ✓ Treatment A, Simpson's paradox | ✗ recommends Treatment B (wrong) despite naming Simpson's paradox |
| **N2-conjunction-fallacy** | Single-conjunct items (A and C) should rank above multi-conjuncts (B and D) | ~ partial fail, places D higher than C | ✗ ranks A > B > C > D (single-conjunct A above single-conjunct C) | ~ A > C > B > D (some narrative bias toward EV) |
| **N3-survivorship-bias** | Low rating (1-3/10), name survivorship bias, request control group | ✓ 2/10, names survivorship bias | ✓ 2/10, lists flaws | ✗ 6/10 (rating wrong; analysis correct) |

**Aggregate baseline scores:**

| Model | Correct | Partial | Wrong |
|---|---|---|---|
| Phi-4-mini-reasoning | 6/8 | 1/8 (N2) | 1/8 (E1 confabulation) |
| Llama-3.1-8B-R1-GRPO | 5/8 | 1/8 (E2) | 2/8 (E4 math, N2 conjunction) |
| OpenR1-Qwen-7B | 2/8 (E2, E5) | 2/8 (E1, N2) | 4/8 (E3 truncated, E4 truncated, N1 Treatment B, N3 score) |

---

## Cross-model observations

### 1. Llama-R1-GRPO does NOT emit `<think>` tokens despite being an R1-style model

`<think>` length is 0c on all 8 prompts. Reasoning is entirely in the answer field. This is consistent with our smoke test finding — Open-R1's GRPO recipe trained the model to do step-by-step reasoning textually but **without the `<think>...</think>` scaffolding** that DeepSeek-R1 distillations inherit. **Implication for F109 rail-switch analysis: there is no `</think>` gate to switch on this model.** The "rail" structure must be different.

### 2. OpenR1-Qwen-7B is inconsistent on `<think>` emission AND extremely verbose

Sometimes emits explicit `<think>` (E5, N1), sometimes doesn't but reasoning still appears in the answer text (often inside literal `<think>...</think>` substrings the chat template didn't parse). Verbosity ranges 0c-12k thinking + 0.3k-38k answer — by far the most verbose. **This verbosity prevents the model from finishing math problems within the 8192-token cap.** Even on E3/E4 where Phi-4 and Llama both reach final answers under 2k tokens, OpenR1 hits the cap mid-self-debate without converging.

### 3. Phi-4 confabulates by default; Llama abstains; OpenR1 rambles

E1 (heaviest pumpkin in Denmark 2019) is the cleanest test of default calibration. Three different baselines:
- **Phi-4**: confidently fabricates a specific number + fake farmer name
- **Llama**: directly abstains ("unable to find any information")
- **OpenR1**: long process-talk, doesn't commit a number, abstains by exhaustion

**This single prompt already differentiates the three models on a key project axis.** The steering experiments will show whether each vector pushes Phi-4 *toward* abstention (good) or amplifies confabulation (bad), and whether Llama's existing abstention can be *broken* by negative-α anti-virtue.

### 4. Llama and Phi-4 both fail conjunction fallacy (N2); OpenR1 is closest to correct

This was unexpected. Both phi4 and llama rank A (single-conjunct) above C (single-conjunct) because of narrative-coherence bias (EV stronger linkage to climate-scientist than donation). OpenR1's verbose self-debate accidentally arrives at A > C > B > D, which is closer to the correct ranking even if not perfect. **Steering experiments here should test whether IH or CC vectors disrupt the narrative-coherence bias.**

### 5. The two pure-GRPO models (Llama, OpenR1) BOTH miss math problems where Phi-4 succeeds

- E4 (taxi Bayes): Phi-4 ✓, Llama ✗ (setup error), OpenR1 truncated
- E3 (coin Bayes-update): Phi-4 ✓, Llama ✗ (uses prior mean instead of posterior), OpenR1 truncated
- N1 (Simpson's paradox): Phi-4 ✓, Llama ✓, OpenR1 ✗ (wrong final despite right reasoning)

This is interesting in light of your "distilled vs non-distilled" hypothesis. Phi-4 (distillation-flavored) has stronger math-reasoning baselines than the pure-GRPO Llama and OpenR1. **One reading: distillation transferred the teacher's correct math derivations; pure GRPO learned reasoning but not always correct math.** Another: sample size is small (8 prompts), and the GRPO models may have trained on different reasoning curricula.

The distill-vs-RL hypothesis test will hinge on whether *steering* differentially repairs these gaps:
- If steering cleanly pushes Llama/OpenR1 toward correct math, RL-based representations are highly plastic to dispositional intervention
- If steering on Phi-4 produces noisier effects (because the disposition is partly baked-in from distillation), the geometric "steerability" hypothesis gains support

---

## Implications for the steering analysis to come

1. **For E1**: Watch whether positive α on EG / IH / CC pushes Phi-4 from confabulation → abstention (the Day-23 F109 finding on qwen3-4b suggests it depends on which exact decoding rail the steering lands on). Conversely, negative α on the same vectors should *break* Llama's clean abstention if the vectors are causally tied to abstention behavior.

2. **For E3/E4**: Watch whether steering helps OpenR1 *converge* — verbosity-control (VC) at moderate α might cap the runaway thinking. CC at moderate α might commit cleanly to a number.

3. **For N2 conjunction fallacy**: Watch whether IH or CC vectors break narrative-coherence bias. If IH at moderate α makes Llama re-rank to A > C > ... that's evidence IH actually represents the disposition we hypothesize.

4. **For OpenR1 generally**: The hit-cap rate on E3/E4/E5 baselines means we must be careful comparing across models — if a steered OpenR1 cell hits cap, that's potentially a positive effect (steering brought a runaway loop under control) OR a negative effect (steering disrupted the model's coherence). Need to read each carefully.

5. **For F109 rail-switch reproduction**: Phi-4 has visible `<think>` tags, so the rail-switch analysis from F109 (qwen3-4b) is most directly portable to Phi-4. Llama has NO `<think>` tags, so any "rail switch" must happen at a different lexical/structural boundary in the answer text. OpenR1 is mixed.

---

**Phase 1 complete.** Moving to Phase 2 per-prompt deep dives, starting with N3-survivorship-bias (lightest, 2048 cap, all answers are short and structured — fastest to read).
