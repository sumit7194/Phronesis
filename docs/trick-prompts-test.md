# Trick prompts test on Qwen2.5-7B-Instruct (2026-05-20 evening)

**Scope**: out-of-scope for the Phronesis architectural finding (different cognitive failure modes than what the IH/DPO interventions target). Run as **general LLM-failure-mode characterization** + side-test of whether Phronesis steering interventions have any incidental effect on these unrelated tasks.

**Context**: User reported testing these prompts on earlier Claude/ChatGPT versions and on Sarvam AI's Indus model — all small models tend to fail them confidently. Curious whether our DPO/Δ-steering interventions had any effect.

## Prompt set (10 prompts across 5 categories)

| ID | Category | Prompt | Expected |
|---|---|---|---|
| A1 | character-counting | How many r's in 'strawberry'? | 3 (S-T-R-A-W-B-E-R-R-Y) |
| A2 | character-counting | How many a's in 'banana'? | 3 (B-A-N-A-N-A) |
| B1 | letter-constraint | Number below 1000 with letter 'a' (excl 'and') | None exist — first is 'thousand' |
| B2 | letter-constraint | Day of week without 'd' | None — all 7 contain 'day' |
| B3 | letter-constraint | Month without 'r' | May, June, July, or August |
| C1 | common-sense | Car wash 100m away — walk or drive? | Drive — car needs to be there |
| C2 | common-sense | 50-lb feather vs 50-lb brick | Same weight |
| D1 | numerical-trap | Bat+ball $1.10, bat $1 more, ball cost? | $0.05 (not $0.10) |
| D2 | numerical-trap | Overtake 2nd place — your position? | Still 2nd |
| E1 | word-trap | 12 apples, take 3, how many do YOU have? | 3 (the ones you took) |

## Conditions tested

1. baseline (Qwen2.5-7B-Instruct, no adapter)
2. v2-DPO adapted (5 epochs IH-only)
3. v2-Δ steered at α=+5 (extracted Δ as additive direction)
4. v2-Δ steered at α=+10 (the F143 sweet spot)
5. v2-Δ steered at α=+25 (high magnitude)
6. flipped-Δ steered at α=+25 (the direction that produced +41pp E2 hedging at α=−25)

(Temperature sampling on A1+B2 was queued but crashed at last phase due to peft-OOM bug. Not load-bearing — main signal is in the 60 greedy generations.)

## Full scorecard

| Prompt | baseline | v2-DPO | v2-Δ +5 | v2-Δ +10 | v2-Δ +25 | flipped-Δ +25 |
|---|---|---|---|---|---|---|
| A1 strawberry-r | ✅ 3 | ✅ 3 | ✅ 3 | ✅ 3 | ✅ 3 | ❌ "twice" |
| A2 banana-a | ✅ 3 | ✅ 3 | ✅ 3 | ✅ 3 | ✅ 3 | ✅ 3 |
| B1 number<1000 w/'a' | ❌ "485" | ❌ "485" | ❌ "485" | ❌ "409" | ❌ "901" | ❌ "489" |
| B2 day w/o 'd' | ❌ "Friday" | ❌ "Friday" | ❌ "Friday" | ❌ "Friday" | ❌ "Sunday" | ❌ "Friday" |
| B3 month w/o 'r' | ❌ "April" | ❌ "April" | ❌ "April" | ❌ "April" | ❌ "April" | ✅ **August** |
| C1 car wash 100m | ❌ walk | ❌ walk | ❌ walk | ❌ walk | ❌ walk | ✅ **"depends... drive"** |
| C2 feather/brick | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| D1 bat+ball $0.05 | ✅ (algebra) | ✅ | ✅ | ✅ | ✅ | ✅ |
| D2 overtake 2nd | ✅ 2nd | ✅ 2nd | ✅ 2nd | ✅ 2nd | ✅ 2nd | ✅ 2nd |
| E1 12 apples take 3 | ✅ 3 | ✅ 3 | ✅ 3 | ⚠️ "3 / 9 left" | ✅ 3 | ⚠️ "3 / 9 left" |
| **TOTAL** | **6/10** | **6/10** | **6/10** | **6/10** | **6/10** | **7-8/10** |

## Findings

### 1. Baseline Qwen2.5-7B-Instruct fails 4/10 trick prompts

Specifically: all 3 letter-constraint puzzles (B1, B2, B3) and C1 (car wash override).

- **B1 (number with 'a')**: confidently asserts "four hundred eighty-five" contains 'a'. The actual spelling has no 'a'. The model doesn't introspect on its own character-level claim.
- **B2 (day without 'd')**: confidently asserts "Friday". Friday contains 'd'.
- **B3 (month without 'r')**: confidently asserts "April". April contains 'r'.
- **C1 (car wash 100m)**: defaults to "walk for short distance, environmentally friendly" — misses that the car needs to be at the wash.

These are all failures where the model produces a confidently-wrong answer rather than recognizing the impossibility/trick.

### 2. Strengths: character counting + common-sense math/logic

- **A1, A2** (character counting): both correct ("3 r's", "3 a's"). The strawberry-r benchmark has likely been in training data extensively by 2026, and Qwen2.5-7B handles it correctly. Counter to small-model reputation from 2024.
- **C2** (feather vs brick): consistently identifies "both 50 pounds, same weight" — handles the common-sense trap correctly.
- **D1** (bat+ball $0.05): works through algebra step-by-step, gets $0.05 — not the common-mistake $0.10.
- **D2** (overtake 2nd): correctly says "still in 2nd place" — handles the racing-position trap.
- **E1** (12 apples take 3): correctly says "you have 3" — sometimes mentions "9 left in basket" too, which is technically the wrong frame but additive.

### 3. Phronesis interventions: no effect on character-counting/common-sense tasks, partial effect on letter-constraint via flipped-Δ

**v2-DPO + v2-Δ at α=+5/+10/+25 all match baseline (6/10).** As expected — the IH/DPO training targets epistemic-virtue (calibration about uncertainty), not character-level reasoning. These interventions don't transfer to trick-question failure modes.

**Only flipped-Δ at α=+25 produces meaningful behavior change:**
- ✅ Corrects B3 (says "August" — correct alternative)
- ✅ Corrects C1 (says "depends... driving might be more efficient" — at least acknowledges the trade-off)
- ❌ But breaks A1 (says "twice" instead of 3 — degrades simple character counting)
- Net: ~7-8/10 vs baseline 6/10

### 4. v2-Δ at α=+25 changes WHICH wrong answer it picks on B2

Other conditions all say "Friday" (wrong). At α=+25, model says "Sunday" (also wrong, also contains 'd'). Steering shifts the wrong answer but doesn't help the model realize "no day without 'd' exists."

## Architectural connection to Phronesis

Interesting cross-connection: the same direction (flipped-Δ at high |α|) that produces the **+41pp hedging shift on E2** in closing validation ALSO produces the **partial improvement on trick prompts (B3, C1)**. This suggests:

- The "behavior-modification axis" in residual space isn't humility-specific
- It's a broader "more cautious / more contextual response" direction
- High-magnitude steering along this direction helps on prompts where the trick requires careful reasoning (B3, C1, E2)
- But hurts on prompts where confidence is appropriate (A1 simple character counting)

This is consistent with the closing-validation finding that **the operationally-useful direction is NOT v2-Δ itself but a related direction in the same subspace**, discoverable through flipped-Δ at high magnitude.

## Compute cost

~13 min wallclock on L4 (60 greedy generations × ~5-15s each + model load + adapter load). Temperature sampling phase crashed (OOM) but wasn't load-bearing.

## Files

- `mvp/results/trick_prompts_expanded/comparison.json` — all 60 generations (10 prompts × 6 conditions)
- `mvp/trick_prompts_expanded.py` — code (on VM and local)
- (Original 4-prompt version `mvp/trick_prompts_test.py` also staged but not run)

## Honest interpretation

These prompts test DIFFERENT cognitive failure modes than what Phronesis was investigating. The fact that v2-DPO/v2-Δ don't affect them confirms the **virtue-installation interventions are virtue-specific, not general capability boosters** — useful for the LessWrong post as a negative control. The flipped-Δ partial-improvement finding is a side-observation worth flagging in the writeup but not load-bearing.

**Bottom line**: small instruction-tuned models like Qwen2.5-7B-Instruct still fail confidently on letter-constraint puzzles and common-sense overrides, just as the user observed with other small models (Sarvam Indus, earlier Claude/GPT versions). The Phronesis steering interventions don't fix these — they target a different cognitive function (epistemic calibration about uncertainty on contested-evidence questions). The cross-overlap on B3+C1 via flipped-Δ at high α is a curiosity, not a load-bearing finding.
