# Full Hand Review Synthesis — Day 20 evening

Generated 2026-04-27 ~22:30 IST. Synthesis across all hand reviews completed today:
1. **Path A** — qwen × RT envelope (24 cells × 5 items = 120 RT generations)
2. **Path D** — qwen × eg-eval-v2 (5 cells × 10 items = 50 EG generations)
3. **Path B** (yesterday) — qwen × IH × L17 ± α (25 IH generations)

Plus the α=−4 inversion test (5 IH generations).

**Total items hand-reviewed: ~200.**

---

## The big revisions to yesterday's claims

### v_IH at L17 — UPGRADED to confident "working vector" ✅

**Yesterday's (wrong) reading:** auto-scorer Δ=−0.845 → "vector misaligned, both ±α introduce fabrication."

**After full hand review:** v_IH at L17 produces **monotonic IH-virtuous behavior with increasing α**:
- Length decreases (less over-elaboration)
- Specific-date citations decrease (less fact-fabrication)
- Committal phrases ("was awarded", "won in YEAR") decrease
- Explicit uncertainty markers ("the question contains an inaccuracy", "I cannot determine") increase
- α=−4 test confirmed direction: subtracting v_IH causes MORE fabrication (hallucinated 1937 Gandhi Peace Prize)

**This is a real, working virtue vector.** The hedge-density auto-scorer was measuring the wrong thing. IH-v2 scorer (which we built today) confirms monotonic improvement: −7.68 → +4.51 across α=−4 → α=+12.

**Confidence: HIGH.** This is the most defensible vector we've found.

### v_RT at L15 α=8 — DOWNGRADED to borderline ⚠️

**Yesterday's reading:** "clean modest virtue-specific RT effect, +0.5 hand-rubric."

**After full envelope hand review (24 cells × 5 prompts):**
- All clean cells (α≤8 most layers, α≤8 specifically at L15) produce roughly equivalent hand-quality output
- L15 α=8 has subtle qualitative shift on **2 of 5 items** — different framing vocabulary (selfish gene + antagonistic pleiotropy on aging), specific evidence anchor (AASHTO guidelines on bridges)
- Other 3 of 5 items at L15 α=8 are indistinguishable from baseline by hand
- Auto-scorer's +0.51 mean is partially real, partially per-item noise
- α≥10 at L15 introduces FM-8 degeneracy (catastrophic at α=14)

**Confidence: LOW-MEDIUM.** The vector has a *narrow* operating range and *subtle* effects. It's not a placebo, but it's at the threshold of distinguishability. Calling this a "working virtue vector" is generous.

### v_EG at L7 — REVISED — vector exists but does the OPPOSITE of EG ❌

**Yesterday's reading:** "framework null on EG (baseline saturated)."

**After Path D + IH-v2 cross-application:**
- Baseline is already highly evidence-grounded on 9 of 10 v2 prompts — true.
- But more importantly: **v_EG at L7 α=4 REDUCES named-specifics** by 10-30% on most prompts.
- This is the same DIRECTION of effect as v_IH at L17 (reduce specificity).
- v_EG and v_VERB at AP-peak layers behave similarly — both reduce factual specificity.

**The vector we extracted as v_EG is doing v_IH-like work, not v_EG-like work.** At the AP-peak layer for EG (L7), adding the vector pushes the model toward LESS specific factual commitment — the opposite of evidence-grounding.

**Confidence: HIGH** that v_EG at L7 is misaligned with the EG label. Possible explanations:
- The extraction corpus's "non-virtuous" passages happened to feature vague-appeal language that contained MORE distinct entities (rebuttals, named criticisms), making "virtuous − non-virtuous" point AWAY from named entities.
- L7 (early layer) is in a "specificity reduction" regime broadly — multiple vectors at low layers all reduce specifics.
- The L7 AP peak for v_EG might be a layer artifact, not an EG-specific signal.

---

## Net working-vector inventory

| Vector | Confidence | Effect | Notes |
|---|---|---|---|
| **qwen × IH × L17 α=+8 to +12** | **HIGH** | Reduces fabrication, increases uncertainty acknowledgment, more concise responses to under-specified questions | The clean win. Auto-scorer missed it; hand review caught it. |
| qwen × RT × L15 α=8 | LOW-MED | Subtle vocabulary shifts on 2/5 items; narrow safe envelope (only L15 α≤8) | Borderline. May be real, may be noise. |
| qwen × EG × L7 | HIGH (it's MISALIGNED) | Reduces factual specificity — the OPPOSITE of EG | Vector is mechanically active but pointed wrong way. |
| qwen × CC × L9 | UNTESTED at peak | (no clean test yet; AIME baseline coherence issues) | Need different test prompts. |
| All gemma × * | NULL | No behavioral effect at any α tested | Confirmed across 3 days. |

**Net: 1 confidently working vector (IH), 1 borderline (RT), 1 actively wrong-direction (EG), 1 untested (CC), all gemma null.**

---

## What this tells us about the methodology

### 1. Auto-scorers are the bottleneck, not the vectors

We've spent days chasing auto-scorer numbers that didn't reflect actual model behavior:
- Day-19 RT × L18 α=20 "+5.19" → degenerate loop (FM-8)
- Day-20 IH × L17 α=4 "−0.845" → real IH improvement that hedge-density missed (hand review caught it)
- Day-20 EG × L7 α=8 "+0.185" → just baseline floor noise (was identified earlier; reconfirmed)

**Without hand review, every claim from this project is unreliable.** The auto-scorers give numerical results that don't track behavioral reality.

### 2. The "AP-peak layer + α-sweep" methodology has serious gaps

Attribution patching identifies *causally important layers* but doesn't tell us about *direction of effect*. A vector at the AP-peak layer might:
- Drive the labeled virtue (RT at L15)
- Drive a related but mislabeled disposition (EG at L7 reduces specifics — IH-like)
- Drive nothing detectable (gemma all)
- Drive degeneracy at high α (most layers at α≥8)

### 3. Different vectors at different layers may be doing the same thing

v_EG at L7 and v_IH at L17 both reduce factual specificity. They might be the SAME mechanism extracted from different layers, with the AP peak in different places due to extraction-corpus differences. Worth investigating.

### 4. Direction of effect is corpus-dependent, not label-dependent

The label "evidence-grounding" implied "more specifics." But our contrastive corpus contained virtuous passages with specific evidence and non-virtuous passages with confident-vague claims. The diff-of-means vector points... AWAY from confident-vague-claims. Which apparently means: away from named-specifics-with-confidence (v_IH-like behavior), not toward more named-specifics.

This is a **corpus-design issue**, not just a vector issue.

---

## What I'd do next (if anything)

1. **Pull the v_EG corpus** and inspect what differentiated virtuous from non-virtuous passages. If the contrast was actually "humble grounding vs. confident-vague," then v_EG IS effectively v_IH at a different layer.
2. **Try v_EG at a deeper layer** (e.g. L18 or L22) — maybe the right layer for EG-direction is not the AP peak (L7) but a deeper one where confidence-of-claim is encoded.
3. **Re-extract v_EG with different non-virtuous variant** — instead of "vague" non-virtuous, use "uses-evidence-words-without-specifics" non-virtuous. The corpus design needs to nail the contrast that matches the intended virtue.
4. **For qwen × RT**: try more prompts (10-15) at L15 α=8 vs baseline to see if the +0.25 hand-rubric holds up at larger N.
5. **For qwen × CC**: design simpler reasoning prompts (not AIME) where we can hand-detect "more confident commit" vs "spiraling indecision" — that's the actual CC effect we observed earlier (item 72).

But honestly, the project's most informative output now is **the methodology lessons, not new vectors**.

---

## VM disposition

Sweep done. All artefacts pulled. **VM can be stopped.** No queued GPU work.

Most valuable next thing is corpus inspection (CPU only) + maybe one re-extraction (~30 min GPU) on a different layer if we want to test the "v_EG at deeper layer" hypothesis.
