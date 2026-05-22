# Prior-art deep-read synthesis — Friday 2026-05-22

After three parallel agent reads of the full papers (not just abstracts), the prior-art picture is sharper. **Our writeup positioning is meaningfully better than the first-pass impression suggested.**

## Papers verified to exist

- **D-STEER** — arXiv:2512.11838, Raina et al., Dec 3 2025. "DPO is Just Steering... DPO as Steering Vector Perturbation in Activation Space." LLaMA-2-7B and Mistral-1.3B on OASST1/Anthropic-HH.
- **Pan et al. 2025** — arXiv:2502.09674, Pan, Liu, Chen, Zhou, Yu, Jia. "Hidden Dimensions of LLM Alignment: A Multi-Dimensional Analysis of Orthogonal Safety Directions." ICML 2025 poster. Llama 3.1 8B Instruct on safety/refusal.
- **Pres et al. 2024** — arXiv:2410.17245, Pres, Ruis, Lubana, Krueger. "Towards Reliable Evaluation of Behavior Steering Interventions in LLMs." NeurIPS 2024 MINT workshop. Llama-2-7B-Chat, evaluation of CAA + ITI.

## Critical findings from the deep reads

### D-STEER (the one that worried me most)

**Confirmed overlap**: construction v* = mean(h_DPO − h_0) is identical to our F143. The gradient identity ∇_h L_DPO ∝ −v is their analytical contribution.

**But — the sharp limits of their work:**
- **They only sweep λ ∈ [−1, 1].** Never tested |α| > 1. **Our flipped-Δ at α=−25 producing +53pp is entirely outside their tested regime** and **counter-evidence to their strict rank-one "one-dimensional behavioral subspace" claim**.
- **They have ZERO greedy-vs-sampled discussion.** No decoding procedure specified, no seed variance, no distributional measurement. Our F138 walkback methodology has no analog in D-STEER.
- **They don't cite CAA, ITI, AxBench, RepE, persona vectors, or Pan et al. 2502.09674.** Massive citation gap. They cite a DIFFERENT Pan paper (arXiv:2410.20008, "Unlearning alignment").
- **They explicitly acknowledge the rank-one limitation**: *"alignment is confined to a 1D subspace, so additional axes (e.g., safety, creativity, style) require new approximately orthogonal steering vectors or fundamentally different, higher-rank mechanisms"* (§4.1, p.7). Our flipped-Δ +53pp finding tests exactly the case they hand-wave.

### Pan et al. 2025

**Confirmed overlap**: SVD-of-(W−I) extracts a direction near-orthogonal to the Arditi refusal probe. *"all components found have near-zero cosine similarity with the probe vector... the probe vector is an aggregation of multiple safety feature directions"* (§4).

**But — the sharp limits:**
- **Single SSFT + single DPO + single dataset** on Llama 3.1 8B. No multi-adapter robustness analysis.
- **Single probe**: only Arditi et al. diff-of-means. No multi-method comparison.
- **REMOVAL-ONLY interventions** (Equation 2: `x := x − Σ αᵢvᵢ`). **They never test positive-direction steering at all.** Our flipped-Δ +53pp is a positive-steering behavioral dissociation experiment they explicitly don't run.
- **Refusal/safety only.** Verbatim limitation: *"the desired behavior is not limited to refusal responses"* — they flag epistemic-virtue domain as future work.
- **Semantic decoding via PLRP** (Partial Layer-wise Relevance Propagation, projecting back to training tokens). Different methodology from NLA. Their direction labels (e.g., "harmful subjects", "hypothetical framing", "compliance signals") are different in kind from our NLA AV decoding (humility content vs math/textbook content).

### Pres et al. 2024

**Confirmed overlap**: Four desiderata for evaluation (context, likelihoods, cross-behavior, baseline). Table 3 myopia near-tie (`latter: 0.39, immediate: 0.39`) demonstrates greedy-sampling fragility. Our F138 walkback is a textbook instance of the failure mode they cataloged.

**But — the sharp limits:**
- **Four desiderata, no fifth.** No seed-replication-as-discipline. They observe seed dependence in Table 3 but don't operationalize a multi-seed protocol.
- **Evaluation-time only.** Their entire framework evaluates published artifacts (CAA vectors, ITI heads). No training-time controls like our flipped DPO.
- **Cross-sectional re-evaluation of others' work.** No longitudinal within-project walkback documentation. They observe "previously reported results were overstated"; they don't observe "every clean positive in solo steering work needs reframing within 48 hours."
- **Doesn't apply to fine-tuning artifacts.** Their pipeline never tested DPO/SFT.
- **No prescribed sample-size minimums.** No "n≥50 for baseline characterization" rule. The earlier agent's claim of "T=1.0 p=0.9 prescribed" overstated — those are illustrative parameters, not normative recommendations.

## The synthesized Phronesis contribution

### Beyond D-STEER

1. **Flipped-Δ at large |α| producing NEW behavior** (not just attenuation/recovery). Counter-evidence to their strict rank-one framing. **They explicitly didn't test this.**
2. **F138 walkback methodology**: greedy vs distributional measurement against baseline — they have zero such discussion.
3. **Cross-architecture replication** (Qwen2.5-7B vs LLaMA-2-7B/Mistral).
4. **Cross-domain extension** (epistemic humility/calibration vs HHH safety).
5. **Citation bridge** to the activation-steering literature they ignored (CAA, ITI, AxBench, RepE, persona vectors).

### Beyond Pan et al.

1. **Multi-adapter robustness**: 5 DPO variants (rank 4/16/64, SFT, flipped, multi-virtue) at mutual cos 0.50–0.87. They tested one configuration.
2. **Multi-probe-method robustness**: 4 contrastive extraction methods (diff-of-means, AR-encoding, AR-diff, logistic probe) all near-orthogonal to DPO Δ. They tested one (Arditi).
3. **Positive-steering behavioral dissociation**: our flipped-Δ +53pp shows the DPO-derived direction at large magnitude produces behavior the probe direction does not. **Pan et al. only do removal/projection-subtract.** This is a behavioral experiment they cannot run with their intervention design.
4. **Cross-architecture replication** (Qwen vs Llama).
5. **Cross-domain** (humility vs refusal — their explicitly flagged limitation).
6. **NLA AV semantic decoding** methodology — different from their PLRP approach.

### Beyond Pres et al.

1. **Seed-replication-as-discipline**: operationalized 10-seed → 50-seed protocol with documented hedge-rate distributions and Wilson CIs.
2. **Training-time controls (flipped DPO)**: tests whether the directional sign matters by training an inverse DPO, then comparing. Outside Pres et al.'s evaluation-time-only scope.
3. **Longitudinal within-project walkback documentation**: F94, F103, F138, F138-replication. Four walkbacks across a 5-month solo project with timestamped real-time docs. Pres et al. is cross-sectional; we're longitudinal.
4. **Application to fine-tuning artifacts**: their pipeline never tested DPO/SFT. We apply distributional/seed-replicated measurement directly to DPO weight updates.

## Where there's no genuine novelty (be honest)

- **The bare claim "DPO produces a steering vector"** → D-STEER, with formal derivation.
- **The bare claim "fine-tuning direction is near-orthogonal to contrastive probe"** → Pan et al., on refusal.
- **The bare claim "greedy steering effects can be sampling artifacts"** → Pres et al., with Table 3 as cleaner demonstration.

If our writeup states ANY of these three bare claims as headline contributions, it's prior art and we'd be embarrassed. We need to cite each paper and position our work as the multi-axis extension.

## Honest writeup framing (final)

Based on the deep reads, the right framing is:

> **"A five-month solo replication-and-extension study of three recent papers on activation-space steering, applied to epistemic-virtue installation on Qwen2.5-7B."**
>
> **Contributions** (in order of strength):
> 1. **The flipped-Δ +53pp empirical anomaly** (n=20 hand-classified, Wilson CI non-overlapping with baseline): a direction near-orthogonal to the DPO-derived direction, when added at large magnitude, produces a stronger behavioral shift than the DPO direction itself. **Not predicted by D-STEER's rank-one model; not tested by Pan et al.'s removal-only design.** Genuine empirical contribution.
> 2. **Multi-adapter coherence** of the DPO-derived direction (5 variants at mutual cos 0.50–0.87, near-orthogonal to 4 contrastive probes at cos +0.05–0.10). Extends Pan et al.'s single-configuration result.
> 3. **NLA semantic decoding** showing the discrimination cluster reads as humility content and the DPO-Δ cluster reads as math/textbook content — methodologically novel relative to Pan et al.'s PLRP approach.
> 4. **F138 walkback case study + 4-walkback longitudinal pattern**: concrete realization of Pres et al.'s sampling-fragility warning across four within-project walkback events with timestamped documentation. Extends their cross-sectional re-evaluation framework to a longitudinal solo-research discipline.
> 5. **Cross-architecture and cross-domain replication**: Qwen2.5-7B + epistemic humility (vs LLaMA-2/Mistral + HHH for D-STEER, Llama 3.1 + refusal for Pan et al., Llama-2-7B-Chat + corrigibility/myopia for Pres et al.).

**Workshop paper, not LessWrong discovery post.** But a genuinely useful workshop paper — it builds on three real prior papers, extends each in a specific way, and reports one finding (flipped-Δ +53pp) that none of them tested or predicted.

## What this changes about today's plan

- **The n=50 flipped-Δ confirmation is still worth running**, but is no longer load-bearing. Hand-review at n=20 already gives Wilson CIs non-overlapping with baseline (n=50). The n=50 confirmation upgrades the finding from "robust at hand-classified n=20" to "robust at hand-classified n=20 with consistent n=50 replication" — incremental, not decisive.
- **The post can be drafted now.** We have the empirical findings, the prior-art positioning, and the framing. The n=50 confirmation can be added later if it lands cleanly.
- **The pre-existing draft at `docs/drafts/F121-steering-one-sidedness.md`** needs a substantial rewrite. It was authored before the prior-art landscape was clear. New title should be something like *"Behavior-modification axis vs discrimination axis in DPO-aligned 7B LLMs: a replication-and-extension study with epistemic-humility virtues"* or similar.

## Action items for the writeup (when we sit down to draft)

1. **Title and framing**: replication-and-extension study, not discovery paper
2. **§1 Intro**: explain three prior papers, situate Phronesis between them
3. **§2 Method**: detail the multi-adapter cosine clustering, multi-probe comparison, NLA decoding, seed-replication discipline
4. **§3 Results** (in order):
   - Confirm Pan-et-al-style orthogonality across 4 probes + 5 adapters on Qwen2.5-7B
   - Confirm D-STEER-style Δ-as-steering reproduction (greedy)
   - **The walkback**: F138 effect at distributional measurement collapses (cite Pres et al. as the warning we should have followed)
   - **The empirical anomaly**: flipped-Δ at α=−25 produces +53pp shift — outside D-STEER's tested regime, complicates their rank-one claim
   - Cross-domain demonstration: epistemic humility, not just refusal
5. **§4 Methodology contribution**: the 4-walkback longitudinal pattern as concrete demonstration of Pres et al.'s warning + extension via seed-replication-as-discipline + training-time controls (flipped DPO)
6. **§5 Limitations**: small-N (n=20 hand-classified), single model (Qwen2.5-7B only), single layer (L20 only), no inter-rater agreement on hand classifications
7. **§6 Conclusion**: position as bridging three papers + reporting one anomaly

## Files for the writeup

- `docs/findings.md` F127-F145 — the empirical record
- `docs/day37-overnight-status.md` — the closing-validation synthesis with all addenda
- `docs/closing-validation-hand-review-2026-05-22.md` — the careful hedge-classification table
- `docs/trick-prompts-test.md` — separate, mostly out-of-scope
- This doc (`docs/prior-art-deep-read-2026-05-22.md`) — citation positioning
- `docs/drafts/F121-steering-one-sidedness.md` — old draft, needs rewrite

VM still on ludo. n=50 flipped-Δ queued in `docs/next-session-queue.md` for whenever it frees. **We can draft the post tonight without waiting.**

---

## ADDENDUM 2026-05-23 — Second-round prior-art search before writeup

A second web-search pass before drafting the LessWrong post revealed substantially more prior art than this doc originally captured. The contribution claim shrinks accordingly.

### Additional papers / sources to cite

| Paper / source | arXiv / URL | What it covers |
|---|---|---|
| **The Rogue Scalpel: Activation Steering Compromises LLM Safety** | arXiv:2509.22067 (Sept 2025) | **Random-direction steering increases harmful compliance 0%→1-13%**. Also: 20 random vectors aggregated form a "universal attack." Direct prior art for our "direction-agnostic perturbation" finding, applied to safety rather than hedging. |
| **Tan et al. — Analyzing the Generalization and Reliability of Steering Vectors** | arXiv:2407.12404 (July 2024) | Steerability highly variable across inputs; up to 50% of samples "anti-steerable" (shift in opposite direction). Brittle to reasonable prompt changes. Direct prior art for cross-prompt failure. NeurIPS 2024. |
| **Tan et al. — Investigating Generalization of One-shot LLM Steering Vectors** | arXiv:2502.18862 (Feb 2025) | Follow-up on one-shot steering generalization. |
| **Braun et al. — A Sober Look at Steering Vectors for LLMs** | (May 2025, Alignment Forum + blog post) | Anti-steerability follow-up; cited widely for steerability variability. |
| **Understanding (Un)Reliability of Steering Vectors in LLMs** | arXiv:2505.22637 | ICLR 2025 Building Trust Workshop. Reliability framework. |
| **DSAS — Dynamically Scaled Activation Steering** | arXiv:2512.03661 (Dec 2025) | Non-monotonic α-effect relationship. Adaptive modulation. |
| **Taimeskhanov et al. 2026** | (cited in field guide) | "Stronger is worse" — α=3.0 can perform worse than α=2.0. Non-monotonic. |
| **What Drives Representation Steering? A Mechanistic Case Study on Steering Refusal** | arXiv:2604.08524 | **Single-behavior mechanistic case study format** — direct format analog to what we'd write. Different behavioral domain (refusal). |
| **EAST — Entropic Activation Steering for LLM Agents** | arXiv:2406.00244 | Closest behavioral domain (subjective uncertainty for agents). Controls agent action entropy. |
| **Subhadip Mitra — Activation Steering in 2026: A Practitioner's Field Guide** | subhadipmitra.com 2026 blog | **Practitioner consolidation** of cross-prompt failure, non-monotonic dose, recommended controls. Notably does NOT mention matched-norm random-direction baselines — this is the one gap our work fills in their checklist. |

### Updated contribution claim

The original framing — "we discovered direction-specific epistemic-virtue steering" — was wrong (V3/F146 walkback). The revised framing — "we documented controls-bundle failure case study with novel methodology" — was also too strong. **The current honest framing**:

> "We applied four already-published methodological cautions to a new behavioral domain (epistemic-virtue hedging on contested-evidence prompts in Qwen2.5-7B-Instruct). All four reproduce: matched-norm random direction works comparably (Rogue Scalpel-style), cross-prompt generalization fails (Tan et al.-style), dose-response is non-monotonic / saturating (DSAS-style), DPO-Δ-as-vector works (D-STEER-style). Our specific empirical artifact is a +30pp direction-agnostic effect on n=1 prompt that does not generalize."

### What remains genuinely new

1. **Behavioral domain**: epistemic-virtue hedging on contested-evidence prompts. Refusal, sycophancy, agent-uncertainty (EAST), calibration have been done; this specific framing has not.
2. **The full 5-control bundle applied in one project** with raw numbers and confidence intervals. Each control individually has prior art; the bundle is somewhat original.
3. **The "completeness vs evidence-strength" hedge classification distinction**: shifted our headline by 4pp. This is a small but original methodology note.
4. **The 6-walkback narrative**: pedagogically useful, not a research finding.
5. **Field-guide gap on matched-norm random baselines**: Subhadip Mitra's guide doesn't mention this control; our work confirms it should be standard.

### Decision

Confirmed: write the LessWrong post per the plan in `docs/drafts/lesswrong-replication-post-plan.md`. Frame as replication-on-new-domain with the controls bundle + classification rubric + field-guide gap as the constructive additions. Modest claim. ~2500 words.

Do NOT pursue arXiv preprint unless LessWrong post lands well (>20 karma + substantive comments).
