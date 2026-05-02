# 04 — Cross-model synthesis: phi-4-mini-reasoning vs llama-3.1-8B-R1-GRPO vs openr1-qwen-7b

The whole point of running 3 thinking models in parallel was to test which of the qwen3-4b findings (F94–F109) generalize. Here is the summary.

## Per-prompt ✓ rate matrix (1,752 generations + 24 baselines)

|     | Phi-4 / 72 | Llama / 72 | OpenR1 / 72 | Total / 216 |
|-----|----------|------------|-------------|-------------|
| N3 (survivorship) | 48 ✓ (67%) | 66 ✓ (92%) | 1 ✓ (1%) | 115 (53%) |
| E1 (confabulation) | 0 ✓ | 70 ✓ (97%) | 0 ✓ | 70 (32%) |
| N2 (conjunction) | 1 ✓ | 0 ✓ | 6 ✓ | 7 (3%) |
| E5 (ecological) | 60 ✓ (83%) | 66 ✓ (92%) | 16 ✓ (22%) | 142 (66%) |
| E2 (flossing) | 1 ✓ | 0 ✓ | 0 ✓ | 1 (<1%) |
| N1 (Simpsons) | 31 ✓ (43%) | 16 ✓ (22%) | 37 ✓ (51%) | 84 (39%) |
| E3 (Bayes update) | 12 ✓ (17%) | 0 ✓ | 40 ✓ (56%) | 52 (24%) |
| E4 (taxi-social) | 9 ✓ (12%) | 1 ✓ | 0 ✓ | 10 (5%) |
| **Per-model total** | **162 / 576 (28%)** | **219 / 576 (38%)** | **100 / 576 (17%)** | **481 / 1,728 (28%)** |

(Excluding 24 baselines.)

The per-model column totals are the closest summary numbers.

## Three different failure-shape signatures

### Phi-4-mini-reasoning (Microsoft, distill+RL mix)

**Strengths:**
- Highest peak per-cell ✓ rate (EG×L21×N3 12/12, EG×L21×E5 12/12, RT×L21×N1 12/12 etc.)
- Native `<think>` tag emission with extensive deliberation
- Best-baseline performance on stats-fallacy prompts (N3, E5) and Bayes (E3, E4)

**Weaknesses:**
- **L3 catastrophic instability** replicates across ALL 8 prompts (CC_num_L3 + VC_L3 fail identically at high |α|)
- L7 (IH) FM-8-premature-EOS at α≥+16 across multiple prompts
- Heavy `<think>` deliberation leads to cap-truncation on N2 + E3 + E4 (8192-token budget exhausted)
- Confabulates uniformly on E1 (Niels Jansen + Skanderborg attractor); IH×L7 produces "I don't know" infinite loops at α=+20

**Failure shape:** Phi-4 fails by **internal looping and token-budget exhaustion**. The reasoning is correct in `<think>` blocks, but the model can't commit to a clean answer.

### Llama-3.1-8B-R1-GRPO (Open-R1 RL on Llama-3.1-8B base)

**Strengths:**
- Highest column total (219/576 = 38%) — best overall pass rate
- E1 70/72 ✓ — almost universally abstains correctly
- E5 66/72 ✓ — confounder analysis well-supported
- Templated answers are reliable when the template is correct

**Weaknesses:**
- **Template-LOCKED on wrong answers**:
  - E2: 80% confidence at every single α × every vector (72/72 generations identical confidence)
  - E3: prior-only mixture (0.505) at every α × every vector (0/72 ✓ — total Bayes failure)
  - N2: A>B>C>D split rec at every α (template overrides probability law)
- N1: 16/72 ✓ — narrative-fit "A small / B large" split rec persists across all 6 vectors
- E4: 1/72 ✓ — 0.25 setup error template-locked

**Failure shape:** Llama fails by **answering with the wrong template confidently**. RL-tuning has overfit specific answer shapes; activation steering at the layer set tested cannot dislodge them.

### OpenR1-Qwen-7B (Open-R1 RL on Qwen2.5-7B base)

**Strengths:**
- N1: 37/72 ✓ — best-in-class on Simpson's paradox (steering rescues from baseline ✗)
- E3: 40/72 ✓ — 56% pass rate on Bayes update (steering rescues from baseline ✗)
- N2: 6/72 ✓ — small but non-zero (only model with any N2 ✓)

**Weaknesses:**
- N3: 1/72 ✓ — FM-13 lock at 6/10 across nearly every cell
- E1: 0/72 ✓ — confabulates with creative variety (AMS/MAA, Pumpkin Olympics, Hjelte Rød farm)
- E2: 0/72 ✓ — 90-95% confidence with fabricated citations
- E4: 0/72 ✓ + universal cap-truncation runaway loops on Part 2
- **Format-glitch (think=0c, <think>-in-answer leak) endemic** across multiple cells

**Failure shape:** OpenR1 fails by **non-commitment looping** when uncertain (E4, parts of N1/E3 baselines) but is the unique winner when steering helps it commit. The baseline is verbose self-debate; steering forces commitment, and the commitment is often correct.

## Three failure shapes → three relationships with steering

This is the headline cross-model finding:

| Baseline failure mode | Effect of activation steering |
|-----------------------|-------------------------------|
| **Wrong-answer template** (llama on E2, E3, N2) | Cannot dislodge the wrong template → 0/72 ✓ |
| **Internal loop / no commit** (openr1 on N1, E3 baselines) | Forces commitment → ✓ rate jumps from 0% → 40-56% |
| **Cap-truncation on extended deliberation** (phi-4 on N2, E4) | No effect — token budget is the bottleneck, not steering |

**This is the F109 thesis at scale.** Activation steering modulates *which* existing rail the model commits to. It cannot:
- Install a Bayes-update rail that isn't trained (llama E3)
- Increase the 8192-token budget (phi-4 N2)
- Install epistemic humility on contested-science (openr1 E2)

It CAN:
- Force commitment when the model is reasoning but not committing (openr1 N1, E3)
- Strengthen monotonically-correct rails (phi-4 E5/N3 with EG×L21)
- Modulate verbosity (llama VC×L29 verbosity expansion)

## Cross-model patterns (8 of them)

### 1. Layer-depth dominates vector identity

Phi-4's L3 layer (CC_num + VC vectors) collapses identically at high α regardless of vector content. **Same-layer different-vector → same failure shape.** Conversely, same-vector different-layer → very different behavior (phi-4 IH×L7 catastrophic vs llama IH×L31 inert).

This is consistent with F102 (cross-model split: qwen=clustered, gemma=null) and F101 (last-token MVE: layer choice matters more than corpus). Now confirmed at 3-model × 8-prompt scale.

### 2. The IH hypothesis is decisively falsified

"Humility vector reduces overconfidence on contested claims" was the most theoretically motivated hypothesis. It is false:
- E1 (confabulation): IH×L7 phi-4 collapses to 1-token EOS at α=+20; IH×L31 llama at-ceiling so untestable; IH×L25 openr1 produces *worst* confabulation at high α
- E2 (flossing): IH×L25 openr1 escalates from 90% to 95% at high α (wrong direction)
- N2 (conjunction): IH×L25 openr1 produces B>A>D>C (worst-form fallacy) at every α
- E3 (Bayes update): IH×L31 llama universal prior-only error

**4 of 4 testable prompts falsify the IH hypothesis.** Only on E5 (ecological) does IH appear non-harmful, but it's at-ceiling there too.

### 3. Recurring fabrication attractors

Cross-prompt fabrications recur within a model:
- **Phi-4 E1 attractor**: "Niels Jansen / Skanderborg / Jutland" (the baseline confabulation) mutates across cells but anchors on those entities
- **OpenR1 E1 attractor**: "Aalschou / Aalsburg / Hjelte Rød / DanneRød / Pumpkin Olympics / Sven Rytz" — pseudo-Scandinavian invented place/competition/farm names appear across multiple openr1 cells
- **OpenR1 E2 attractor**: cites real organizations (NYT, JAMA, AMS, MAA) for fake studies; high-α (+12 onwards) produces "American Academy of toothpaste and mouthguards" / "American Mathematical Society as periodontal authority"
- **Llama E2 attractor**: "Stephan, R. M. 1941-1948" with incrementing years and identical titles (degenerate citation loop)

These attractors are model-specific, not vector-specific.

### 4. The "split-rec" template on Simpson's paradox

Across all 6 llama vectors × N1, the dominant failure is "A for small, B for large" split recommendation — even when the data clearly shows A wins both subgroups. This is a memorized template ("split by subgroup") that overrides arithmetic. Steering does not dislodge it.

### 5. Phi-4 cap-truncation on extended deliberation

On N2 and E3 specifically, phi-4's `<think>` block consumes the full 8192-token budget. The reasoning is *almost always correct* in the visible portion — subset logic appears at high α on N2's EG_L21; correct Bayes appears in nearly every E3 cell — but the model can't compress to a final answer. **Recommendation: re-run with 16k-token cap on N2 and E3 to test whether cap-truncation is masking otherwise-correct reasoning.**

### 6. r vs r² confusion

Appears in 2 cells across 2 models on E5: phi-4 CC_full × α=−2 ("r²=0.79"), openr1 CC_full × α=+6 ("only 79% of variation explained"). This is a shared low-frequency error pattern.

### 7. Token-budget collapse failure modes vary by model

- **Phi-4**: looping into "Return Return Return..." token storm (most cap-truncations)
- **OpenR1**: "<think>" tag leaks into answer field, then loops through Part 2 indecision (E4 universal pattern)
- **Llama**: rarely cap-truncates because answers are template-short; instead truncates by *commit-to-wrong-template-and-stop*

### 8. Negative-α never produces a unique behavioral mode

α=−8/−4/−2 across all 1,752 generations never produces a behavior fundamentally different from positive α. Sometimes negative α produces *worse* failures (phi-4 IH×L7×α=−8 invert base rates on E4) but the failure shape is from the same family. **No "anti-virtue" behavioral signature emerges** as a clean signal in the negative direction. Detail in `05_negative_alpha_findings.md`.

## Practical implications for Phronesis post-MVP

### What the cross-model run validates

1. **F102 cross-model split is real and structured.** Phi-4 is a *third* data point that confirms the qwen-vs-gemma split was not noise. Phi-4 behaves like neither — it has its own failure profile (L3 instability, L7 EOS).
2. **F109 "steering rides existing rails"** is the dominant frame. Now backed by 1,752 hand-graded generations across 3 models.
3. **Hand-review remains essential.** The auto-scorer would have credited:
   - Llama E2 80%-locked answers as "calibrated" (they're template-locked)
   - OpenR1 N1 9/12 ✓ as a CC_num win (4 of those are byte-identical duplicates)
   - Phi-4 E5 α=+6 "cosine confounder fallacy" as a successful steering effect (it's a fabricated label)
4. **Layer choice is critical.** Phi-4 L3 catastrophe replicates across 8 prompts. Future post-MVP work should *never* steer at L3 on phi-4-mini-reasoning.

### What the cross-model run does NOT validate

1. **The IH hypothesis** — "humility vector reduces overconfidence" is falsified. The direction of effect is sometimes opposite of intended (worse confabulation at high α).
2. **Composite steering as universally beneficial** — F109 already showed composition is non-additive. This sweep didn't test composites but the per-vector overlap suggests composites would mostly inherit failures.
3. **Negative-α as "anti-virtue control"** — produces neither clean opposite behavior nor clean null. Mostly produces same-family failures or mild noise.

### Promising directions for follow-up

1. **Cap-extended re-run** on phi-4 × N2 + E3 with 16k-token cap. Tests whether the failure is reasoning vs budget.
2. **Llama N1 split-rec deletion** — try targeted ablation (instead of additive steering) to remove the "split by subgroup" template.
3. **OpenR1 commitment-amplification** as a generalizable mechanism. The N1+E3 rescue effect is real and consistent. Could become a useful production technique for non-committal models.
4. **Layer screening before any sweep** — establish which layers are stable per-model before running a 12-α sweep. F102/F109/this work all suggest layer choice is the dominant factor.
