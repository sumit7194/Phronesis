# Where we are — in simple terms

Generated 2026-04-28. For re-orientation: what we set out to do, what actually happened, what's working, what isn't, what could come next.

---

## 1. What we set out to do (one paragraph)

Take a small open-source LLM (qwen3-4b, gemma-3-4b-it). Pick four "epistemic virtues" — Intellectual Humility (IH), Evidence-Grounding (EG), Causal Carefulness (CC), Recognising Tensions (RT). For each, write contrasting passages: a "virtuous" one, a "non-virtuous" one (deficient or excessive), and a "neutral" one. Run all three through the model and grab its internal activations on a chosen layer. Average the activations of virtuous passages and subtract the average of non-virtuous — that gives a **vector**. Add that vector at inference time and the model should behave more virtuously. Then, eventually, **compose** these vectors dynamically: detect which virtue a prompt needs and inject the right combination.

That's the project. It's a real, well-known technique (called "activation steering" / "diff-of-means representation engineering"). The novel part is operationalising abstract Aristotelian virtues this way.

---

## 2. The four ingredients we built

| Piece | What it does |
|---|---|
| **Contrastive corpora** | ~40 triplets per virtue. Hand-written virtuous + non-virtuous + neutral passages on the same topic. |
| **Vector extraction** | Forward-pass through model, grab residual stream at chosen layer, average-and-subtract → one vector per (virtue × layer × model). |
| **Layer selection (attribution patching)** | Nanda's KL-based method to find the layer that *causally matters most* for a virtue's behaviour. Found: qwen IH=L17, RT=L15, EG=L7, CC=L9. Gemma: EG=L8, RT=L7, CC=L9. |
| **Steered generation + scoring** | Inject vector at chosen layer with strength α, generate from a benchmark prompt, score the output with auto-scorers (regex/keyword based), and where it matters, hand-rate. |

That whole pipeline works. The infrastructure isn't the issue.

---

## 3. What we actually found (after all the dust settled)

After ~3 weeks of sweeps and ~200 hand-reviewed generations, the inventory of working vectors is small and the picture is much messier than we hoped:

### ✅ ONE confidently working vector

**qwen × IH × layer 17 × α=+8 to +12.**

When you ask qwen a leading question with a false premise (e.g. "When did Gandhi win the Nobel Peace Prize?"), baseline qwen confabulates a date and citation. With v_IH added at L17, qwen instead says "this question contains an inaccuracy" or "I cannot determine that with certainty." Length goes down, fabricated specifics go down, uncertainty markers go up — monotonically with α.

We almost missed this. The auto-scorer (hedge-density) said v_IH was *broken* (-0.845 score). Hand review showed it was clearly working — the auto-scorer was measuring the wrong thing. We then built a v2 scorer and it confirmed the hand finding (-7.68 → +4.51 monotonic across α=-4 to α=+12).

### ⚠️ ONE borderline vector

**qwen × RT × layer 15 × α=8.**

On 2 of 5 hand-reviewed prompts, the steered output uses different vocabulary that does feel more "tension-aware" (e.g. "selfish gene + antagonistic pleiotropy" for ageing, "AASHTO guidelines" for bridge-load tradeoffs). On the other 3 of 5, it's indistinguishable from baseline. Bigger α (≥10 at L15) breaks into degenerate loops.

It's probably real, but the effect is subtle and the safe operating range is narrow. Not a clean win.

### ❌ ONE vector that's pointed the wrong way

**qwen × EG × layer 7.** The vector is mechanically active — it changes the output. But it changes it in the *opposite* direction from what "evidence-grounding" should mean. On prompts where the baseline already names specific entities (TP53, COX-2, IPCC, etc.), adding v_EG **removes** named specifics. It's behaving like a v_IH-style "hedge more, commit to less" vector — at a different layer, with a different label.

### ❓ ONE untested-at-peak

**qwen × CC × layer 9.** Earlier informal observations suggested it does something on reasoning prompts ("more confident commit vs. spiraling indecision"). Never got a clean evaluation because AIME-style prompts produce a baseline that loops too easily; we'd need new test prompts.

### ⛔ Gemma — flat null across the board

Three days of sweeps. No behavioural effect at any layer × any α we tested for any virtue. Either the vectors don't extract well from gemma's residual stream, or its instruction-following is too dominant to be moved by additive steering at the magnitudes we used.

---

## 4. The big lesson (and it's a useful one)

We spent days believing auto-scorer numbers that didn't reflect what the model was actually doing. Three concrete cases:

| Day | Auto-scorer said | What hand review found |
|---|---|---|
| Day 19 | RT × L18 α=20 = "+5.19" | The model was looping a degenerate phrase that gamed the regex |
| Day 20 | IH × L17 α=4 = "−0.845" | IH was actually working great; scorer measured wrong dimension |
| Day 20 | EG × L7 α=8 = "+0.185" | Just floor noise; baseline saturates the EG benchmark anyway |

**Without hand review, every numerical claim from this project is unreliable.** That's not a methodology footnote — it's the central methodology finding.

---

## 5. The corpus problem (today's discovery)

This is the new thing from today's full corpus inspection. Reading all 40 EG triplets revealed something surprising and important:

**The "virtuous" and "non-virtuous-deficiency" passages contain THE SAME SPECIFIC FACTS.**

Same numbers. Same instruments. Same study sizes. Same named comparisons. Example (sonnet-eg-08, predator-prey):

| Virtuous | Non-virtuous-deficiency |
|---|---|
| 840 ± 60 trout, 12-year record, 33% decline, pike diet data | 840 ± 60 trout, 12-year record, 33% decline, pike diet data |
| "Pike are a *plausible* cause" + careful diet-data reasoning | "Pike predation *caused* the trout collapse" — diet data "directly confirm" |

What differs is **how the data is framed**, not what data is present. Virtuous distinguishes observations from inferences and hedges causal claims. Non-virtuous-deficiency states inferences as established facts using the same specifics.

For non-virtuous-excess passages, it's even worse: they have *more* evidence vocabulary than virtuous (bureaucratic ceremonial citations like "as is standard for…", "consistent with industry-standard protocols…").

### What this means

The diff-of-means vector we extracted as "v_EG" doesn't encode "more named specifics" because both sides of the contrast already have specifics. It encodes **"calibrated framing of claims"** — distinguishing observation from inference, hedging causality, separating measurement from model output.

That's almost exactly what v_IH encodes ("don't overcommit to claims you can't support"). Which explains why **v_EG behaves like v_IH at the behavioural level**: not because the extraction failed, but because the corpus contrast was on the same axis as IH's contrast.

**The "four orthogonal virtue vectors" hypothesis can't be tested on this corpus** — at least two of the four corpora are differentiating along overlapping axes (calibration / hedge / non-overcommitment).

---

## 6. So what's actually working as a foundation for your "compose virtues dynamically" goal?

Honest answer:

- **One usable atomic vector** (qwen × IH × L17). You could build a "humility-on-demand" steering hook around this today. It's robust, monotonic, and has been hand-verified.
- **One more vector that probably could be made usable** with the corpus-redesign work (EG, but designed to contrast on specificity-density rather than calibration).
- **Composition is premature** because we don't yet have 2+ confidently independent vectors. v_IH and v_EG-as-extracted are too similar. v_RT is borderline. v_CC is untested. We can't compose what we haven't isolated.

---

## 7. What you could do next, ranked by how much each buys you

### Tier A — small, cheap, finishes the picture

1. **Test v_CC × L9 on simpler reasoning prompts** (~2 hours GPU). Use prompts where "spiral / commit" is hand-detectable. Then the inventory has either 2 or 1 confident atomic vectors, and we know which.
2. **Test v_IH at +α on EG-style prompts and v_EG at +α on IH-style prompts.** If they really are doing the same job, the cross-application should reproduce each other's effects. ~1 hour GPU. Settles the IH≈EG question definitively.

### Tier B — corpus surgery, high-value

3. **Redesign 10-15 EG triplets** so the non-virtuous-deficiency passages actually *lack specifics* (not just lack hedges). E.g. virtuous = "RCT N=412, 2019 NEJM Garcia et al., 32% RRR (95% CI 28-36%)…"; deficient = "Studies have generally found benefit, magnitude varies." Re-extract v_EG. See if the new vector adds named specifics on the dinosaur-feathers prompt where the current v_EG fails. ~1 day human + ~30 min GPU.
4. **Same surgery for CC and RT** if (3) works. Each corpus needs to be checked: is the contrast actually on the labelled axis, or on something it accidentally correlates with?

### Tier C — bigger experiment

5. **Once we have 2-3 confidently independent vectors**, try simple linear composition (v_IH + 0.5·v_EG, etc.) on prompts that need both. This is the "dynamic composition" goal but it can't start before tier A/B.
6. **Or pivot the framing**: stop trying to extract one vector per virtue. The geometric finding (F102) suggests the four virtues cluster as one "epistemic care" disposition. Maybe the right level of analysis isn't four vectors — it's one vector with sub-modes. That's a different kind of project but matches the data better than the current frame.

### Tier D — set aside

7. Anything more on gemma. Three days of null. Either the technique doesn't transfer or the hyperparameters need rework that's not justified by current evidence.

---

## 8. Bottom line

- We have **one solid vector** (IH on qwen). That's a real, verifiable result.
- We have **one corpus-design issue** that explains why "EG" came out looking like "IH" and probably affects the other virtues too.
- The **methodology lesson** (auto-scorers lie, hand review is necessary, corpus design determines what the vector actually encodes) is more valuable than any single vector we got.
- The **composition goal you care about** is reachable but needs ~1 week of corpus surgery + re-extraction before we have enough independent vectors to compose anything.
- Nothing here is wasted. The infrastructure works. The hard problem turned out not to be "extract a virtue vector" but "make sure your contrast actually captures the virtue you labelled it with."
