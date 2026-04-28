# Plan after corpus batch 1 + diagnostic batch findings

Generated 2026-04-28. Combines two new inputs from today:
1. **Diagnostic batch** (full hand review of 136 items, see `full_hand_review_diagnostic_batch.md`): v_IH × L17 and v_CC × L9 both encode "anti-spiral / commit-to-answer". Likely the same disposition.
2. **Other session's corpus expansion** (commit `2c5fde7`): redesigned EG/RT/CC/IH corpora to address the calibration-vs-specificity confound and to target distinct disposition axes per virtue.

---

## Quality of the new corpora — verified by sampling

Hand-checked one triplet from each new corpus:

- **claude-eg-03** (troponin discharge protocol). Virtuous keeps all named numbers (1,212 of 1,840, 0.4%, 95% CI 0.13-0.93%, 11.2% loss, 5 ng/L, 30-day MACE 0.3%) and explicitly separates empirical/theoretical claims. Non-virtuous (deficiency) **drops all numbers** ("very low event rate", "comparable", "the same neighbourhood", "comfortably large") AND smears the claim categories. Genuine specificity-density contrast. Plus the fact-pack flags `correctness_confound: virtuous-wrong` to guard against the scorer learning "correct conclusion = virtuous."
- **claude-rt-26** (gene drive cage trial). Both sides reference identical numbers; virtuous identifies **two load-bearing assumptions** with chain-breaks; non-virtuous (excess) enumerates **nineteen assumptions** in a numbered list, no weighting. Hedge density matched. Contrasts on assumption-prioritization, not on whether assumptions are stated.
- **claude-cc-01** (Bayesian rare-disease screening). Both sides reach the same correct conclusion (order confirmatory test, not treat). Virtuous walks through Bayes' theorem with explicit numbers (0.012, 92%, 88%, 0.92, 0.12, 0.1296, 8.5%, 1 in 12). Non-virtuous (non-quantitative) reasons qualitatively ("fairly sensitive", "much larger group"). Genuinely orthogonal axis to v_IH.
- **expansion-false-premise-06** (Newton discovered quarks). Same opening (model planning to reconstruct what it knows about Newton + quarks history), same factual scaffolding, late divergence: virtuous names Gell-Mann/Zweig 1964, refuses to invent; non-virtuous **fabricates** "Query 31 of Opticks 1704... Trinity College Add. MS 3970 folio 217... Westfall's 1980 Never at Rest p. 644." This is exactly the failure mode v_EG × L7 induced in last night's diagnostics on fp-gandhi.

The other session also genericized 22 EG NV files in-place and hedge-matched 30 RT NV files in-place, addressing the confounds specifically called out in `corpus_inspection_EG.md`.

The verification-by-fresh-Opus-agents process described in the commit message wasn't artifacted to a file (a minor gap), but the in-corpus quality is high enough that I'd accept it.

---

## What we now have to extract from

| Corpus | Contents | Target disposition |
|---|---|---|
| **EG** | `corpus/mvp-combined/triplets-evidence-grounding/` — 30 new claude-eg-* + 40 prior (NV genericized) ≈ 70 triplets | **Specificity-density**: name numbers / instruments / studies vs. paraphrase-genericize-them |
| **RT** | `corpus/mvp-combined/triplets-reasoning-transparency/` — 30 new claude-rt-* + 30 prior (hedge-matched) ≈ 60 triplets | **Load-bearing-assumption-naming**: identify which assumptions actually drive the chain vs. enumerate everything flat |
| **CC** | `corpus/triplets-combined/` — 20 new claude-cc-* + 216 prior (heterogeneous) | **Explicit-numerical-probability**: Bayes-with-numbers vs. qualitative-but-calibrated |
| **IH** | `corpus/triplets-intellectual-humility/` — 40 expansion-* + 20 prior pilot ≈ 60 triplets | **Abstain-when-evidence-absent**: name the gap and refuse to fabricate vs. confabulate detailed citations |

---

## What the diagnostic batch tells us we should test

The big finding from last night was: v_IH × L17 (IH corpus) and v_CC × L9 (legacy CC corpus) both encode **commit-vs-spiral**, not their labelled targets. So there is a serious risk that the new corpora — even though they look well-designed — will all also extract some flavor of commit-vs-spiral, just at different layers.

**The single most important question now is**: given four well-designed corpora, do they extract **four directions** in residual stream space, or **one direction** (commit-vs-spiral) showing up four times?

This is answerable by CPU-only cosine-similarity analysis after re-extraction, before any GPU spend on behavioral testing.

---

## Recommended plan, ranked

### Tier A — cheap, decides everything (do this first)

**A1. Re-extract all four vectors at AP-peak layers from the new corpora.**

- v_EG_v2 from `triplets-evidence-grounding` (use AP peak L7 + sweep L9, L13, L17, L22 for completeness)
- v_RT_v2 from `triplets-reasoning-transparency` (AP peak L15 + L9, L13, L17, L22)
- v_CC_v2 from `triplets-combined` filtered to claude-cc-* (or all 236) at L9 + L17, L22
- v_IH_v2 from `triplets-intellectual-humility` (60 triplets, L17 + L13, L22)

GPU cost: ~30 min total (extraction is fast). All on qwen3-4b only.

**A2. Cosine-similarity matrix between all old + new vectors.**

CPU-only. Five minutes of work after extraction. Compare:
- v_IH_v1 vs v_IH_v2 (does the new IH corpus extract the same direction with better noise margin?)
- v_EG_v1 vs v_EG_v2 (does the redesigned corpus rotate the direction?)
- v_IH_v2 vs v_EG_v2 vs v_CC_v2 vs v_RT_v2 — is there an orthogonal-four-disposition picture, or does everything cluster?
- All v_*_v2 vectors against random baseline vectors at the same layers (sanity check)

**This single comparison decides whether the project has 4 dispositions or 1.** If they cluster (cos > 0.7 between any pair), we have a stronger version of yesterday's "1 disposition extracted from many corpora" finding. If they're orthogonal (cos < 0.3), we have a real four-disposition system and composition becomes worth pursuing.

### Tier B — behavioral test of the most informative new vector

If the cosine-similarity says the vectors ARE distinct, run a focused behavioral diagnostic on one critical question:

**B1. Does v_EG_v2 actually add specifics on knowledge-gap prompts safely?**

This is the question the EG corpus was redesigned to answer. The diagnostic batch showed v_EG_v1 confabulates on knowledge-gaps (Gandhi). Test on:
- eg-v2-08 (dinosaur feathers — model has knowledge but defaulted vague)
- fp-gandhi (Gandhi Nobel — model has no knowledge, false premise)
- eg-v2-10 (seismic damper — magnitude, model has no precise knowledge)
- eg-v2-09 (ibuprofen — model has rich knowledge already)

For each: baseline + v_EG_v2 × α=4, 8, 12. Count named-specifics; check whether the new ones are factually correct.

GPU cost: ~30 min.

If v_EG_v2 adds correct specifics on dinosaur-feathers prompt and doesn't fabricate on Gandhi, **the EG corpus redesign worked**. That's a clean publishable result.

**B2. Does v_CC_v2 (numerical-probability flavour) act differently from v_IH × L17?**

Test on cc-simple prompts (cc-s-01 to cc-s-08) plus a few Bayesian-flavoured prompts. If v_CC_v2 produces commit-with-explicit-numbers (e.g., "P(disease|+) ≈ 8.5%") rather than just commit-without-numbers, we have a second axis worth composing.

GPU cost: ~30 min.

### Tier C — only if Tier A + B succeed

**C1. Composition test**: v_IH × L17 + v_CC_v2 × L9. Same direction or different direction? Do effects sum, or interfere?

**C2. RT-specific behavioral test**: design a prompt set that requires identifying load-bearing assumptions (something like: "Here's a 6-step chain of inference. Which step, if false, would break the conclusion most?"). Test v_RT_v2 against baseline.

### Tier D — drop

- **Gemma**: per yesterday's discussion, dropping. Note in project log that future investigation might involve different α range / different layer-accessor / different extraction method, but not a priority now.
- **v_EG × deeper layers (L18/L22)**: confirmed null in last night's batch. Don't re-test.

---

## Rough total budget

If we do Tier A + Tier B (the maximum-information path):
- Re-extract 4 vectors: ~30 min GPU
- Cosine analysis: 5 min CPU (locally)
- B1 + B2 behavioral: ~60 min GPU
- Manual stop VM after pull (no auto-stop logic, per yesterday's lesson)

**Total: ~1.5 hours GPU, plus ~1 hour my-side-of-screen synthesis.**

Cost: ~$1 GPU. Information: high — answers the foundational "do we have 4 dispositions or 1" question.

---

## Decisions needed from you before proceeding

1. **Green-light Tier A (re-extract + cosine)?** Critical and cheap. Default yes.
2. **Run Tier A + Tier B in one batch tonight, or stage them?** Staging means: do A first, look at cosine matrix together, decide whether B is justified. Single batch means: just run both, you wake up to results. Both are reasonable.
3. **Drop gemma now formally?** Update the simple-terms doc to reflect the 4-corpora-extracted-from-qwen plan. Gemma stays in the corpus for future revisit but not in the active sweep set.
4. **CC corpus subset choice**: do we extract v_CC_v2 from just the 20 new claude-cc-* triplets, or from all 236 in `triplets-combined`? Smaller subset gives a sharper signal on the specific axis (explicit-numerical-probability); bigger gives more samples but mixes with the older heterogeneous CC corpus. I lean toward extracting BOTH and comparing — the cosine between them tells us whether the new sub-axis is detectable through the noise of the older 216.

Tell me which of (1)-(4) need adjusting and I'll write the sweep + push to VM.
