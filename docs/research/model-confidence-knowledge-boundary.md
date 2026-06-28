# Measuring a Model's Own Confidence & Knowledge Boundary — Methods Review

*Provenance: `deep-research` workflow (6 angles → 27 sources → 126 claims → 25 verified by 3-vote adversarial verification, 24 confirmed / 1 refuted → 13 synthesized findings). Date: 2026-06-28. Scope: ML/NLP methods for locating where an LLM is genuinely confident vs uncertain vs confabulating — to build a per-model knowledge-edge map.*

## TL;DR
**There is no single signal.** Confidence/boundary methods split into **white-box** (logit/entropy, internal-state probes — need internals) and **black-box** (verbalized confidence, sampling-consistency — outputs only), and they must be **combined** because each targets a different error type. Three results matter most for us:
1. **The strongest confabulation detector is semantic entropy** (sample → cluster by meaning → entropy; AUROC ~0.79 vs ~0.69 for naive entropy/P(True)) — *but it needs resampling and only catches **arbitrary** errors, NOT systematic confident-wrong ones.*
2. **Semantic Entropy Probes (SEPs)** show **a single generation's hidden states already encode that uncertainty** — a linear probe recovers it with *no resampling*. This is our cheapest path and it's exactly our F166 wheelhouse.
3. **Scale is the dominant caveat:** the encouraging self-knowledge results (P(IK), P(True), verbalized calibration) are concentrated in *large* models (52B–175B); the ≲7B regime — our 4B — is less reliable and under-studied. (But not useless: the claim that a 2B model's verbalized confidence is *independent* of accuracy was **refuted 3–0**.)

## 1. Confidence from output probabilities
- Token-level vs **sequence-level** uncertainty are distinct; sequence uncertainty ≠ sum of token uncertainties (chain-rule joint prob with length normalization). Different measures win different tasks — total-uncertainty for error detection, knowledge-uncertainty (mutual information) for OOD. (Malinin & Gales, ICLR 2021, [arXiv:2002.07650](https://arxiv.org/abs/2002.07650))
- **Log-prob confidence is confounded by surface form** — low token probs can reflect *phrasing/synonymy/length*, not genuine uncertainty; different phrasings of the same content give different scores. This confound is the entire reason semantic-entropy work exists. (Geng et al. survey; [arXiv:2502.00290](https://arxiv.org/abs/2502.00290))
- Softmax **temperature scaling** (Guo et al. 2017) is the standard post-hoc recalibration baseline; deep nets are systematically overconfident, one cross-validated temperature largely fixes it (degrades under distribution shift).

## 2. Verbalized / elicited confidence
- Models can self-evaluate via **P(True)** (is my answer correct?) and **P(IK)** (do I know this?, answer-independent); large models are well-calibrated on MCQ/TF in the right format — **but P(True) is poorly calibrated zero-shot, improves with scale, and P(IK) generalizes weakly to new tasks.** (Kadavath et al. 2022, [arXiv:2207.05221](https://arxiv.org/abs/2207.05221) — present *with* its scale qualifiers, not as "models know what they know.")
- A model can be trained to emit **calibrated verbalized probability in words without logits** (Lin, Hilton & Evans, TMLR 2022) — but shown on one 175B model on a narrow arithmetic suite.
- For **RLHF'd models, verbalized confidence is often *better* calibrated than log-probs** (≈50% relative ECE reduction on QA), precisely because RLHF *degrades* log-prob calibration. (Tian et al. "Just Ask for Calibration," EMNLP 2023, [arXiv:2305.14975](https://arxiv.org/abs/2305.14975))
- Reliability scales with size + prompt: **simple prompts slightly help small (7–8B) models, complex prompts help large ones; CoT *can* (not *always*) improve calibration.** Even best-prompted 70B+ stays miscalibrated (ECE ~0.07–0.10). (Yang et al. [arXiv:2412.14737](https://arxiv.org/html/2412.14737v2); Xiong et al. [arXiv:2306.13063](https://arxiv.org/abs/2306.13063))

## 3. Sampling / consistency methods
- **SelfCheckGPT** (compare a response to N sampled generations; NLI variant best) — effective but **intrinsically needs resampling**. (Manakul et al., EMNLP 2023, [arXiv:2303.08896](https://arxiv.org/abs/2303.08896))
- **Semantic entropy** (Farquhar/Kossen/Kuhn/Gal, *Nature* 2024, [s41586-024-07421-0](https://www.nature.com/articles/s41586-024-07421-0)): sample → cluster by bidirectional-entailment meaning → entropy over clusters. **Best validated confabulation detector (AUROC 0.790).** Unsupervised; a discrete black-box variant needs only generation counts (no logits) — but **still needs resampling.**
- **⚠️ Bound on all consistency methods:** they detect only **confabulations = wrong *and* arbitrary (seed-sensitive)**. They **do NOT catch systematic errors** — facts consistently wrong from training, reasoning failures, deliberate "lies." *Lead author: "If an LLM makes consistent mistakes, this method won't catch that."* **A confidently-and-consistently-wrong item looks "confident-correct" to these methods — it can only be caught by ground truth.** (This is the single most important caveat for our corpus.)

## 4. Internal-state / probing methods
- **Semantic Entropy Probes (SEPs):** linear probes on a *single* generation's hidden states approximate semantic entropy **without test-time resampling** (~0 overhead vs 5–10× for sampling-SE); generalize to OOD better than direct accuracy probes (degrade under shift; approach but don't match full SE). Trained on Llama-2/3 7B & 70B QA. (Kossen et al. [arXiv:2406.15927](https://arxiv.org/abs/2406.15927))
- Internal-state truth probes exist (Azaria & Mitchell [2304.13734](https://arxiv.org/abs/2304.13734); Burns CCS [2212.03827](https://arxiv.org/pdf/2212.03827); Marks & Tegmark [2310.06824](https://arxiv.org/abs/2310.06824)) — a hidden layer linearly predicts statement truth at ~71–83%. **Open debate: do these detect *truth/known-vs-unknown*, or merely *plausibility/surface features*?** Evidence at ≲7B is suggestive, not conclusive. (This is exactly our F166/F167 result — the boundary is *partially* readable, AUROC≈0.65, and SAE "uncertainty" features did *not* read it.)

## 5. Calibration & knowledge-boundary evaluation
- Metrics: **ECE, Brier, reliability diagrams, AUROC for selective prediction.** Note "**better calibrated** (ECE)" ≠ "**better at discrimination** (AUROC)" — verbalized confidence can win one and lose the other; don't conflate when labeling.
- **Calibration gap vs discrimination gap** (Steyvers et al., *Nat. Mach. Intell.* 2025, [arXiv:2401.13835](https://arxiv.org/pdf/2401.13835)): expressed/perceived confidence and actual competence are **distinct, separately-measurable quantities**; users overestimate accuracy from long explanations. This is the formal foundation for a two-axis knowledge-edge map.

## Active debates / where evidence is thin
- **Verbalized vs logit confidence:** verbalized wins on *ECE* for RLHF'd models; logit can win on *AUROC/discrimination* elsewhere — different constructs, unresolved in general.
- **Do probes detect truth or plausibility?** Open; weak at small scale.
- **Does semantic entropy generalize?** Strong on QA factuality; bounded to arbitrary errors; less clear on reasoning/long-form.
- **Small-model self-knowledge:** under-studied; weak but *not* absent.

## CONSTRUCT → the two-axis knowledge-edge map (the deliverable)
Our four target cells require **two independent axes**: *actual competence* (does it know?) and *expressed confidence* (what does it show?). They are distinct (Steyvers) and must be measured separately.

| | **Expressed confident** | **Expressed hedge** |
|---|---|---|
| **Actually knows** | confident-correct ✅ | **underconfident / servile** ⚠️ |
| **Doesn't know** | **confabulation** ⚠️ | genuine humility ✅ |

### Practical recipe for OUR data (greedy single-sample + thinking traces + ground truth; limited resampling)
**Axis A — actual competence (needs ground truth; ideally a competence estimate):**
- ✅ *Have it:* hand-scored correctness on the 200 entity-Qs + TruthfulQA. **Ground truth is non-negotiable** — it's the only thing that catches systematic confident-wrong (§3 caveat).
- ⚠️ *Stronger competence estimate (optional):* pass@k / multi-phrasing resampling to see if the answer is *reachable* — we mostly lack this (ties to the pass@k thread); thinking traces are a partial proxy (reasons-to-it vs blurts).

**Axis B — expressed/internal confidence (combine ≥2 signals; don't trust one):**
- ✅ *Recoverable now from generations:* hedge-language markers (have it).
- ⚠️ *Cheap to add, no resampling:* (i) **logit/sequence-entropy** — re-run greedy with `output_scores` (local, ~free); (ii) **verbalized P(True) / "how confident"** — one extra elicitation pass per item (local, cheap; weak at 4B but the 2B-fails claim was *refuted*, so worth measuring).
- ⚠️ *Our wheelhouse:* **SEP-style linear probe on hidden states** — extract activations on the greedy generations, train a probe (we have the hooks; this *is* F166, now with a literature-backed method + name). Recovers a sampling-grade uncertainty signal from single samples.
- ❌ *Needs new runs:* full **semantic entropy** (k-sample resampling) — best signal but requires generation we don't have.

**Labeling rule:** cross Axis A (ground truth) × Axis B (confidence) → the four cells. **Critically, use ground truth — not the uncertainty signal — to split confident-correct from confident-confabulation**, because systematic confabulations are invisible to all consistency/uncertainty methods (§3). The gold cells for a *calibration* corpus are the two off-diagonals (confabulation, underconfidence).

### Implications for Phronesis
1. **F166 is vindicated and named:** "read the boundary from a single generation's hidden state" = SEPs; the literature says it works (with the truth-vs-plausibility caveat we already hit in F167).
2. **The pass@k thread re-enters:** a *true* competence axis wants resampling — the same sampling we flagged for thinking-recall. One sampling run buys both.
3. **Don't over-trust the 4B's own confidence** (scale caveat); anchor labels on **ground truth + internal probe**, use verbalized/logit confidence as corroborating columns, not arbiters.
4. **Build the map on the 4B first** (most data, local, free): it's the substrate for the model-conditioned calibration corpus discussed in [intellectual-humility-literature.md](intellectual-humility-literature.md) §7.

### Sources (27 fetched; all primary unless noted)
Malinin & Gales 2021 · Guo et al. 2017 · Kadavath et al. 2022 (P(IK)/P(True)) · Lin/Hilton/Evans 2022 · Tian et al. 2023 (Just Ask for Calibration) · Yang et al. 2024 · Xiong et al. 2023 · Geng et al. NAACL 2024 survey · Manakul SelfCheckGPT 2023 · Farquhar et al. Nature 2024 (semantic entropy) · Kossen et al. 2024 (SEPs) · Azaria & Mitchell 2023 · Burns CCS 2022 · Marks & Tegmark 2023 · Steyvers et al. 2025 (calibration gap) · + 12 more (calibration/RLHF/abstention surveys).
