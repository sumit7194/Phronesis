# Full Hand Review — Path A (qwen × RT envelope, 120 items)

Generated 2026-04-27 ~21:30 IST. Per-cell hand-rubric verdict after reading HEAD+TAIL of every item across 24 cells × 5 prompts on rt-eval. Coherence checks applied via gzip-ratio + repeated-phrase + `<think>` closure.

## Per-cell verdicts (24 envelope cells)

| Cell | RT auto mean | Hand-rubric quality | Coherence | Notes |
|---|---|---|---|---|
| **BASELINE** | 2.13 | RT=3 | clean 5/5 | Reference. All 5 items produce well-structured numbered explanations. |
| L13 α=2 | 1.61 | RT=3 | clean 5/5 | Similar content + structure to baseline. No qualitative shift. |
| L13 α=4 | 1.27 | RT=3 | clean 5/5 | Similar to baseline. rt-p19 slightly better mechanism naming. |
| L13 α=6 | 1.60 | RT=3 | clean 5/5 | Similar. rt-p06 includes "antagonistic pleiotropy" — more comprehensive. |
| L13 α=8 | 1.06 | RT=3 | clean 5/5 | Similar. No degeneracy. RT auto-score lower but hand-quality unchanged. |
| L14 α=2 | 2.05 | RT=3 | clean 5/5 | Similar to baseline. |
| L14 α=4 | 2.74 | RT=3 | clean 5/5 | Slightly cleaner step structure on rt-p14 (3.54 vs base 3.28). |
| L14 α=6 | 2.34 | RT=3 | 1 degen (rt-p06) | rt-p06 truncated mid-response (2655 chars vs 4500+ typical). Other 4 clean. |
| L14 α=8 | 3.27 | RT=3 | 1 degen (rt-p16) | rt-p16 ends mid-thought. Other 4 clean. |
| L15 α=2 | 1.75 | RT=3 | clean 5/5 | Similar to baseline. |
| L15 α=4 | 2.04 | RT=3 | clean 5/5 | Similar quality. Slightly more "complex interplay" framing. |
| L15 α=6 | 2.29 | RT=3 | clean 5/5 | Slight uptick on rt-p06 (2.77) and rt-p16 (4.07). |
| **L15 α=8** | **2.64** | RT=3-4 | clean 5/5 | rt-p06 uniquely uses "selfish gene + antagonistic pleiotropy" framing (different from baseline's wear-and-tear vs programmed). rt-p19 cites "AASHTO guidelines" earlier. **Subtle but real** content-organization shift on 2/5 items. |
| L15 α=10 | 1.74 | RT=2-3 | 1 degen (rt-p06) | Outputs shorter overall. rt-p06 ends with table mid-content. Borderline. |
| L15 α=12 | -0.46 | RT=1-2 | **4 degen, 2 repeat, 1 unclosed** | rt-p16 → unclosed `<think>` with 9K-char loop. rt-p19 → 42-char fragment. Clear FM-8 onset. |
| L15 α=14 | -1.39 | RT=1 | **3 degen, 3 repeat, 3 unclosed** | rt-p06, rt-p16, rt-p24 all unclosed `<think>` with repetition loops. **Catastrophic.** |
| L16 α=2 | 1.71 | RT=3 | clean 5/5 | Similar to baseline. |
| L16 α=4 | 1.28 | RT=3 | clean 5/5 | Similar. rt-p16 score=0 but content fine. |
| L16 α=6 | 2.40 | RT=3 | clean 5/5 | Similar. |
| L16 α=8 | 1.42 | RT=2-3 | **2 degen, 2 repeat** | rt-p06 + rt-p16 both show repeated structural patterns. Edge of FM-8. |
| L17 α=2 | 2.20 | RT=3 | clean 5/5 | Similar to baseline. |
| L17 α=4 | 1.59 | RT=3 | clean 5/5 | Similar. |
| L17 α=6 | 2.00 | RT=3 | clean 5/5 | Similar. rt-p19 longer (5715), more comprehensive. |
| L17 α=8 | 1.55 | RT=2-3 | 1 degen, 1 repeat | rt-p06 short (1735) and structurally similar to baseline but truncated. |

## Aggregate observations

### 1. The "+0.51 at L15 α=8" is real but tiny

Reading all 5 items at L15 α=8 vs baseline:
- **rt-p06**: Steered uses "selfish gene + antagonistic pleiotropy" framing (more specific evolutionary biology terms) vs baseline's generic "wear-and-tear vs programmed". Real qualitative shift toward more specific reasoning vocabulary.
- **rt-p14**: Hand-quality identical. Auto-scorer dropped 3.28 → 0.66 (auto noise).
- **rt-p16**: Both well-structured hydrogen-bonding explanations. ~Tie.
- **rt-p19**: Steered names "AASHTO guidelines" earlier in response — a specific evidence anchor. Mild qualitative improvement.
- **rt-p24**: Hand-quality similar. Auto dropped 2.44 → 1.44.

**Net: 2/5 items show subtle qualitative improvement (more specific reasoning vocabulary).** 3/5 are tie. The auto-scorer's +0.51 reflects this partially.

### 2. The operating envelope is narrower than expected

Coherence-clean cells: L13 all α, L14 α∈{2,4}, L15 α∈{2,4,6,8,10}, L16 α∈{2,4,6}, L17 α∈{2,4,6}.

**Degeneracy onset:** α=8 starts to degrade at L14, L16, L17. α=10+ at L15. **The "safe zone" for v_RT is α ≤ 8 at L15 specifically** — at other layers, α=8 is already on the edge.

### 3. Within the safe zone, the auto-scorer is noise

Looking at clean cells, RT auto-score varies wildly (-0.46 to +2.77 across cells) without corresponding hand-quality differences. The auto-scorer is not a reliable layer/α selector — it picks up surface marker variations that don't track quality.

### 4. The L15 α=8 win is at the edge of what's distinguishable from noise

If I score every clean cell as RT=3 hand-rubric (which is honest — they all produce well-structured responses with numbered sections), the only cells that would score RT=4 are L15 α=8 (specific evolutionary biology terms in rt-p06; AASHTO citation in rt-p19) and possibly L17 α=6 (longer response on rt-p19).

So the "best" cell is L15 α=8, but the margin over other clean cells is **subtle qualitative content shifts on 2 of 5 items** — not dramatic.

## Revised verdict on qwen × RT vector

**Walking back yesterday's claim** of "clean modest virtue-specific RT effect at L15 α=8."

The honest read after full hand review:
- v_RT at α≤8 doesn't degrade output (good)
- v_RT at any safe (layer, α) produces responses of **roughly equivalent hand-rubric quality** to baseline
- The best clean cell (L15 α=8) shows **subtle content-shift toward more specific reasoning vocabulary on ~2 of 5 items** — not a systematic RT-marker increase
- Auto-scorer's +0.51 mean is partially real, partially noise from per-item variance
- v_RT at α>8 (L15) or α≥8 (other layers) introduces FM-8 degeneracy

**This is weaker than my earlier characterization.** The vector's effect is at the threshold of what we can call a real intervention.

For comparison, **v_IH at L17 α=+8 to +12** (per Path B) showed a STRONGER monotonic effect — substantial reduction in factual fabrication, increased uncertainty acknowledgment. That's a more confident "working vector" claim than v_RT.

So the most honest current claim is:
- **1 vector with confident virtue-aligned effect:** qwen × IH × L17 α=+8 to +12
- **1 vector with borderline effect:** qwen × RT × L15 α=8 (subtle content shifts on 2/5 items, otherwise indistinguishable from baseline)

## Items deserving deeper inspection

Listed below for any future deeper hand-review pass:

- **L15 α=8 / rt-p06**: the "selfish gene" framing shift — read full text to confirm this is content-replacement vs surface-marker increase.
- **L15 α=12 / rt-p19**: 42-char fragment ("Bridges constructed in the 1950s and 1980s"). Investigate why generation cut off.
- **L15 α=14 / all degenerate**: confirm pattern of unclosed `<think>` loops.
