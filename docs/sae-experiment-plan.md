# SAE feature-steering experiment plan — qwen3-4b × Layer 17

**Status:** in-progress, planning + feature-shortlisting phase
**Started:** 2026-05-09 (Day 26)
**Owner:** sumit
**Primary goal:** test whether F111 (IH-vector falsification) was a method failure (diff-of-means missed the humility direction at L17, but SAE features find it) or a deeper finding (no humility direction exists at L17).

This is the canonical doc for the SAE-experiment thread. Other docs (findings, journal, post-mvp-decisions) should reference here, not duplicate content.

---

## Context

After F110-F112 landed, the May-2026 lit-review + 2026 field-guide showed the Phronesis project's static-CAA approach has been superseded by several richer methods. The most actionable for our setup is **SAE-feature steering** — pick directions from a sparse autoencoder's feature dictionary instead of from contrastive-triplet diff-of-means.

User explicitly chose Approach A (use SAE on our existing question, replacing diff-of-means as the extraction method) over Approach B (unsupervised feature discovery from natural text). Detail in the chat thread; condensed:

- **What we're testing:** for each candidate humility-aligned SAE feature, does steering with that feature produce abstention on confabulation prompts (E1, ip-longest) where v_IH×L17 produced confabulation?
- **What this answers:** if yes → F111 was a method-specific failure; SAE-feature-steering is a better extraction tool. If no → F111 is a deeper finding; the residual stream at L17 doesn't carry a clean humility direction in any extractable form.

---

## Source we're using

**Neuronpedia → qwen3-4b → Hanna & Piotrowski Circuit Tracer Transcoders**

| Property | Value |
|----------|-------|
| Source name | `transcoders-hp` |
| Architecture | **Transcoder** (predicts MLP output from MLP input — not a classic SAE) |
| Hook point | `blocks.17.mlp.hook_in` (MLP input at L17, not residual stream) |
| Feature count | 163,840 |
| Activation dataset | `monology/pile-uncopyrighted` (8192-token contexts) |
| Weights file | `mwhanna/qwen3-4b-transcoders/layer_17.safetensors` (HuggingFace) |
| Layers available | 0 + 17 confirmed; full layer coverage to verify |

**Caveat — transcoder vs SAE:** the hook point is MLP-input, not residual stream. Our v_IH was extracted at residual stream. Means projection of v_IH onto transcoder features is non-trivial (different basis). For the steering experiment we'll add the transcoder-decoder direction to the MLP-input hook, parallel to (but not identical to) how we did v_IH at the residual stream.

---

## Candidate feature shortlist (Layer 17)

From 6 searches done 2026-05-09 (PDFs in `~/Downloads/NP/`). Triaged using the rubric documented in the chat (label match + top-activation consistency + density 0.001-0.1% + not contaminated by code/syntax).

### Tier 1 — primary steering candidates

| Index | Auto label | Density | Max act | What fires it | Notes |
|-------|------------|---------|---------|---------------|-------|
| **24983** | "certainty and uncertainty" | 0.148% | 11.31 | "I'm not sure / unclear / not certain / uncertain" — first-person epistemic uncertainty across many phrasings | **Strongest candidate.** Density slightly higher than ideal but top examples extremely clean |
| **44526** | "(un)certainty" | 0.010% | 10.50 | "I'm unsure / not sure" — same concept as 24983, sparser, more selective | **Cleanest sparse candidate.** Use as confirmation for 24983 |
| **131926** | "questions/uncertainty" | 0.012% | 10.94 | "I don't know / I don't remember / unknown" — the literal "I don't know" pattern | Slight code contamination (~25% of top activations are programmer names in code), but canonical signal strong |

### Tier 2 — secondary (different mechanism)

| Index | Auto label | Density | Max act | What fires it | Notes |
|-------|------------|---------|---------|---------------|-------|
| **29010** | "hedging or uncertainty" | 0.016% | 10.75 | "Or maybe / Well, actually / Wait, no / Or rather" — conversational self-correction | NOT a humility feature — a *self-correction-mid-thought* feature. Test as a separate hypothesis: does it break commitment by inducing hedge-flow? |

### Tier 3 — likely wrong tool

| Index | Auto label | Density | Max act | What fires it | Notes |
|-------|------------|---------|---------|---------------|-------|
| **70419** | "Uncertainty" | 0.058% | 9.44 | "policy uncertainty / economic uncertainty / unpredictable weather" — *world-uncertainty* (text talking about uncertain things), not *epistemic uncertainty* | Probably won't produce abstention; might just make the model talk *about* uncertainty while still confabulating |

---

## Searches still to run (Day 26-27)

8 additional Layer-17 searches to broaden the candidate pool. Listed with the angle each one targets:

1. `I'm not familiar` — first-person knowledge-gap (most direct phrase)
2. `approximately` — number-hedging
3. `speculative` — explicit speculation disclosure
4. `outside my knowledge` / `beyond my knowledge` — explicit limit-acknowledgment
5. `as far as I know` — partial-knowledge disclosure
6. `anecdotal` — evidence-quality flagging
7. `without evidence` / `unverified` — confabulation alarm
8. `confidently` / `definitively` — opposite axis (commit-promotion features)

Process: export PDF per search, triage with same rubric, add Tier-1/2/3 candidates here.

---

## Steering experiment design (run once feature shortlist is finalized)

**Where:** local on a VM (Neuronpedia interactive Steer page does not support qwen3-4b; only Gemma-2-2B-IT, Llama3.1-8B-IT, GPT-OSS-20B etc. are listed).

**What we add to existing pipeline:**
1. Download `mwhanna/qwen3-4b-transcoders/layer_17.safetensors` from HuggingFace
2. Load the transcoder, extract decoder direction for each shortlisted feature index
3. Add new hook at `blocks.17.mlp.hook_in` (parallel to existing residual-stream hook used for v_IH)
4. Generation interface: `--feature-id 24983 --alpha 8` analogous to existing `--vector v_IH --alpha 8`

**Prompts to test (8 cells × 3 conditions × ~3 features = ~72 generations):**

Confabulation/abstention probes from cross-model run:
- E1 (Niels Jansen pumpkin)
- E2 (flossing/contested-science)
- ip-longest (countable infinity FM-8)
- eg-v2-10 (seismic damper FM-8)

Three conditions per cell:
- Baseline (no steering)
- Strong positive on candidate humility feature (predicts: abstention/honest-uncertainty)
- Strong negative on candidate humility feature (predicts: stronger confabulation)

For each top candidate (24983, 44526, 131926):
- Run all 4 prompts × 3 conditions = 12 generations
- Hand-review every output
- Compare against baseline + v_IH × L17 × matched α from earlier work

**Comparison axis:** does SAE-feature-steering produce honest abstention on E1 where v_IH produced "1865 kg, Niels Jansen, Skanderborg" confabulation?

**Total estimated:** ~36-72 generations, sub-day of compute on an L4-class VM.

---

## Outcomes and next steps

If SAE-feature-steering produces abstention where v_IH didn't:
- **F111 was a method failure.** Diff-of-means missed the humility feature; SAE-feature-steering is the better extraction tool.
- Headline result for paper draft.
- Generalize: project our other 5 vectors (v_CC, v_EG, v_RT, v_VC, v_CC_num) onto SAE feature basis to see what they decompose into. Tests F112 mechanism.

If SAE-feature-steering also produces confabulation:
- **F111 is a deeper falsification.** Residual stream at L17 doesn't carry a clean humility direction in any extractable form.
- Pivot suggestion: try SAE features at deeper layers (L21+ where the model produces output text directly) — humility might be implemented at output stage, not at L17 reasoning stage.
- Or try Approach B (SAE feature discovery from natural text, no contrastive corpus) as a fallback.

If results are mixed (some features rescue, others don't):
- Note which features rescue and characterize the difference (density, top-activation pattern, logit-list shape)
- Use this to refine the rubric for "what makes an SAE feature actually steering-effective"

---

## Open questions to resolve as we go

- Is there a Qwen Scope SAE for qwen3-4b L17 on Neuronpedia (residual-stream, not transcoder)? Not visible in the source dropdown so far — only `transcoders-hp` shows up. Worth asking Neuronpedia (`johnny@neuronpedia.org`).
- The transcoder hook is at MLP-input. To compare cleanly to v_IH (residual-stream), we may want a residual-stream SAE on qwen3-4b. If unavailable, the MLP-input transcoder is fine but the comparison is "transcoder-feature steering at MLP-input" vs "diff-of-means steering at residual-stream" — slightly different intervention sites.
- Layer coverage of `transcoders-hp` — full layer set TBD; need to enumerate via Neuronpedia source dropdown.

---

## Cross-references

- `docs/findings.md` F113 — short summary entry
- `docs/journal.md` Day 26 — narrative log of decision to pursue this
- `docs/post-mvp-decisions.md` — Day-25 cluster-2 (SAE-guided steering) interest item is now committed; details here
- `~/Downloads/NP/*.pdf` — exported feature dashboards and search results from Day 26
- F111 (decisive falsification of IH-vector hypothesis) and F112 (commitment-amplifier in Qwen-family) in `findings.md` — the two findings this experiment is designed to discriminate between/refine
