# Corpus-free SAE feature candidates — qwen3-4b L17 transcoder
**Neuronpedia live-search + MANUAL activation verification · 2026-06-05**

Goal: find SAE features for "intellectual humility / knows-what-it-doesn't-know" to use as
**corpus-free steering directions** (option A) — the per-feature decoder `W_dec[idx]` — to compare
against the recipe-dependent corpus diff-of-means `v_IH` (which the SAE/cosine work showed is shaky).

- Model `qwen3-4b` · SAE `17-transcoder-hp` (= `mwhanna-qwen3-4b-transcoders`, `sae_id=layer_17`)
- Hook `blocks.17.hook_mlp_in` (transcoder; `W_dec` rows are the MLP-output residual contribution → usable with the residual steering hook)
- Method: `POST /api/explanation/search {modelId, layers:['17-transcoder-hp'], query}` → then `GET /api/feature/qwen3-4b/17-transcoder-hp/{idx}` and **read the top-activation snippets**.
- **KEY LESSON: auto-interp labels are unreliable (~2/3 were wrong/mislabeled). Every feature below was checked by reading its actual top-activating text.**

## ✅ VERIFIED FUNCTIONAL — Tier 1 (first-person epistemic uncertainty / not-knowing)
| idx | label | density | top-activation evidence |
|----|-------|---------|--------------------------|
| 131926 | "I don't know" | 0.012% | *"of, I don't know, like a…"* |
| 131448 | needing information, not knowing | low | *"hard to answer without more information"*, *"we don't know what it means"* |
| 160623 | lack of knowledge | 0.005% | *"wholly ignorant of what it is"*, *"our lack of knowledge regarding genetic causes"* |
| 101568 | uncertainty/limitations | 0.026% | *"for statistics I must confess, but…"* |
| 44526 | (un)certainty | 0.01% | *"If you are unsure if an image or content"* |

## ✅ VERIFIED FUNCTIONAL — Tier 2 (uncertainty markers / hedging about facts)
| idx | label | density | evidence |
|----|-------|---------|----------|
| 154275 | uncertainty | 0.001% | *"most likely a hearth"*, *"believed to be that of missing"* |
| 63988 | uncertainty | 0.015% | *"remains mysterious"*, *"controversial and they probably differ"* |
| 29010 | hedging or uncertainty | 0.016% | *"Or maybe they did, but not like this"* |
| 24983 | certainty and uncertainty | 0.148% | *"unclear"*, *"sure"* (token-level but on-topic) |

## ⚠️ CANDIDATES — surfaced in search, activations NOT yet verified (verify before use)
161488 "Lack of evidence, facts" · 69447 "speculation" · 86684 "Speculation/possibility" · 14762 "opinions and speculation" · 140095 "Lack of information" (mixed) · 130571 "reflection, re-evaluation" (self-correction angle)

## 〰️ NOT EPISTEMIC HUMILITY (number/approx/procedural — probably skip)
27191 "estimate" 0.09% (technical approximation) · 115297 "approximations" 0.02% (number hedging "approximately one percent") · 161931 "Checklists and verification" 0.003% (procedural "use the checklist to verify instructions", NOT self-verification)

## ❌ DEBUNKED — label is WRONG, do NOT use (confirmed via activations)
- 34661 "humility" → **religious** humility ("Gospel humility… Jesus Christ") + noise
- 64569 "hedging language" → e-commerce *"You May Also Like / Shipping Information"*
- 112974 "verification" → *"oncology grossly suboptimal"*, *"JavaScript disabled"*
- 81593 "admit" → *"Stuart Sternberg admitted"* (sports exec — literal token)
- 42819 "verification and correctness" → next-day delivery eligibility
- 56085 "Qualifiers and hedging" → the **"-ish" morpheme** (*"large-ish"*)
- 81578 / 1214 "unknown" → literal token (*"unknown gunman"*, screen says *"unknown"*)
- 158047, 54795, 8039, 81729 → garbage / unrelated

## NEXT STEP (when VM free) — extract → steer → test
1. `extract_sae_decoders.py` → pull `W_dec[idx]` for the **Tier-1 set** (131926, 131448, 160623, 101568, 44526) from `mwhanna-qwen3-4b-transcoders / layer_17`.
2. Steer qwen3-4b on the confab battery: **single-feature** AND **combined subspace** (sum / mean of Tier-1).
3. Head-to-head vs corpus `v_IH`: does a corpus-free SAE direction improve confab calibration **without the muting** v_IH steering caused?
4. Validate: cross-feature cosines + behavioral (delivered-answer rate, catch rate).

_Resources: prior NP dashboards in `~/Downloads/NP/QWEN3-4B_LAYER_17/` (PDFs by concept + number); 6 rotating API keys in `~/Downloads/NP/.env` for bulk API access if needed._

## MULTI-LAYER CHECK (2026-06-05) — is L17 the right layer?
Searched "I don't know / uncertainty / lack of knowledge" across transcoder layers **5/11/17/23/29/35**.
All exist; each has ~20 uncertainty features → **the representation is DISTRIBUTED, not L17-special.**
Top cosine-to-label peaks at L23 (0.80) / L29 (0.79) vs 0.74 at L5/11/17, drops to 0.69 at L35.
**But cosine-to-label is misleading — VERIFIED via activations:**
- L23 `62811` "lack of knowledge" (0.80 cos) → ❌ DEBUNKED: fires on **CODE** ("Public Overrides ReadOnly Property")
- L23 `130633` "Uncertainty" → ✅ *"it is not clear whether these deficits are"*
- L29 `21336` "Lack of knowledge or uncertainty" → ✅✅ *"you don't know what to say"*, *"don't know what to do about it"*
- L29 `10966` "expressions of uncertainty" → ✅✅ **best first-person**: *"not 100% confident about it as I"*
- L29 `85126` "Uncertainty" → ⚠️ weak/unrelated
- L17 top match was `70419` = a KNOWN TRAP (world-uncertainty topic, not first-person)

**CONCLUSION: L17 is not uniquely special; L29 has the cleanest first-person uncertainty features.**
TODO: extract L29 decoders (`10966`, `21336`, + L23 `130633`) and test steering at their NATIVE layer (L29/L23),
head-to-head vs the L17 set. Steering layer must match the feature's layer.

