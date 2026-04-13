# Phronesis — Reference Papers & Sources

A running bibliography of papers, scales, benchmarks, and other sources cited throughout concepts.md and findings.md. Not exhaustive prior-art coverage — just the specific sources that have informed project decisions. Updated as new sources are cited. Each entry notes which finding(s) or concepts reference it.

---

## Primary inspiration

- **Anthropic Interpretability Team (2026).** *Emotion Concepts and their Function in a Large Language Model.* Transformer Circuits Thread, April 2026.
  - Full paper: https://transformer-circuits.pub/2026/emotions/index.html
  - Blog summary: https://www.anthropic.com/research/emotion-concepts-function
  - Cited in: project.md (motivation), F1, F2, F6, F7, F8.
  - Why it matters: the direct methodological template for Phronesis. Extracted 171 emotion vectors from Claude Sonnet 4.5 via contrastive story generation + difference-of-means, validated via held-out prompts, demonstrated causal steering effects on model behavior.

---

## Activation steering and representation engineering

- **Panickssery et al. (2023).** *Steering Llama 2 via Contrastive Activation Addition.* arXiv:2312.06681.
  - https://arxiv.org/abs/2312.06681
  - Cited in: F3, F11, F12, F13, F16.
  - Why it matters: canonical paper for Contrastive Activation Addition (CAA), the methodology family we are extending. Establishes the basic extraction + steering protocol and reports coefficient fragility as a central practical issue.

- **Turner et al. (2023).** *Steering Language Models With Activation Engineering (ActAdd).* arXiv:2308.10248.
  - https://arxiv.org/abs/2308.10248
  - Cited in: F11, F12.
  - Why it matters: earlier activation-addition work that established the amplification-only limit ("ActAdd cannot create new competencies, only amplify what is already there") — the central theoretical risk for Phronesis (F11).

- **Representation engineering survey literature.**
  - https://arxiv.org/html/2502.17601v1
  - Cited in: F11, F12, F13.
  - Why it matters: survey of failure modes (coefficient fragility, concept specificity failure, OOD transfer failure) that became the basis for Phase 4 validation requirements.

- **Depth-Wise Activation Steering for Honest Language Models (2025).** arXiv:2512.07667.
  - https://arxiv.org/html/2512.07667
  - Cited in: F14, F15.
  - Why it matters: explicitly reports that honesty-type concepts are harder to extract at small scale, introduces the MASK benchmark as a honesty-vs-knowledge separation tool.

- **Barlow Twins, IDFD, DeGCL — contrastive representation learning decorrelation literature.**
  - Barlow Twins: Zbontar et al. (2021), arXiv:2103.03230
  - Cited in: F30.
  - Why it matters: convergent evidence that confounds in contrastive training data are a recognized problem in the ML literature, addressed via explicit decorrelation losses. Our corpus-level decorrelation approach (20–30% virtuous passages reaching wrong conclusions) is the training-data analog of this architectural solution. No direct guidance on the specific ratio, but validation that the concern is real.

- **"No Answer Needed: Predicting LLM Answer Accuracy from Question-Only Linear Probes."** OpenReview 2025.
  - https://openreview.net/forum?id=OhN25uxVab
  - Cited in: F43.
  - Why it matters: direct empirical evidence that correctness / reasoning-quality signals are extractable as linear directions from pre-generation activations, and that steering along them flips model decisions (with the model subsequently rationalizing the flip). Strong partial validation of F11's core assumption for the reasoning-quality family of concepts, AND an empirical grounding for the rationalization caveat that sharpens F33's legibility-vs-faithfulness distinction.

- **Epistemic Integrity in Large Language Models.** arXiv:2411.06528.
  - https://arxiv.org/html/2411.06528v2
  - Cited in: F44.
  - Why it matters: documents "epistemic mismatch" — small LLMs default to confident assertive language regardless of internal confidence state. Directly relevant to Calibrated Confidence extraction: the non-virtuous end of our contrastive pairs is the model's baseline, which affects both extraction (sharper contrast) and steering (larger coefficients needed to overcome the assertive prior).

- **Virtue Semantics: Probing the Consistency of Moral Values of Large Language Models.** ICML 2025 workshop.
  - https://static1.squarespace.com/static/66fa51597ab2445d219623d2/t/6883f87c61d4e3253bec19a9/1753479295970/virtue_semantics_icml_workshop.pdf
  - Cited in: F44.
  - Why it matters: documents that internal moral-virtue representations in LLMs do not map neatly onto action choices. Direct evidence for the probe-steering correlation failure mode described in F7: virtue vectors may be readable without being causally active. Warns that the probe-works-but-steering-doesn't outcome is a known phenomenon, not an anomaly.

- **"What Can We Actually Steer? A Multi-Behavior Study of Activation Control."** arXiv:2511.18284 (2025).
  - https://arxiv.org/html/2511.18284
  - Cited in: F45, project.md hypothesis scope condition.
  - Why it matters: the most load-bearing external validation for Phronesis's project direction found to date. Empirically establishes that activation steering is a dispositional modulator, not a propositional injector — and that internal dispositions (biases, sentiments, abstract tendencies) are "densely represented in activation space and easily manipulable." Since all 15 Phronesis concepts are dispositional, this paper directly validates our target category. Also supplies the "more confident rather than more correct" failure-mode quote used in the project.md hypothesis scope condition.

- **FACTS Grounding — Google DeepMind (2025).**
  - Blog: https://deepmind.google/blog/facts-grounding-a-new-benchmark-for-evaluating-the-factuality-of-large-language-models/
  - Paper: https://arxiv.org/pdf/2501.03200
  - Cited in: F46.
  - Why it matters: 1,719-example benchmark for evaluating whether LLM responses are factually grounded in provided context documents. Strong Phase 4 validation candidate for Evidence Grounding vector — deferred until Phase 4.

- **GaRAGe — Amazon (ACL 2025).**
  - https://github.com/amazon-science/GaRAGe
  - Cited in: F46.
  - Why it matters: 2,366 questions with 35,000+ annotated passages for RAG-style grounding evaluation. Another Phase 4 validation candidate for Evidence Grounding.

- **Citation faithfulness / post-rationalization literature (2024–2025).**
  - Survey: https://arxiv.org/html/2508.15396v1
  - Cited in: F46.
  - Why it matters: reports up to 57% of LLM-generated citations are post-rationalized rather than genuinely grounded in source material — the same rationalization failure mode documented in F43, extended to citation behavior. Reinforces the need for Phase 4 protocols that distinguish "model cites more" from "model cites more faithfully."

- **ML calibration literature — ECE, temperature scaling, Guo et al.**
  - ICLR 2025 blogpost overview: https://iclr-blogposts.github.io/2025/blog/calibration/
  - Cited in: F47, concepts.md Concept 9.
  - Why it matters: clarifies that ML "calibration" (softmax probability alignment with accuracy) is distinct from our Calibrated Confidence concept (natural-language confidence alignment with evidence). Phase 4 validation for Concept 9 must use language-level metrics, not ECE.

- **Motivated reasoning psychology literature.**
  - Overview: https://en.wikipedia.org/wiki/Motivated_reasoning
  - Cited in: F48, concepts.md Concept 7.
  - Why it matters: motivated reasoning (asymmetric evaluation driven by desired conclusion) is formally distinct from confirmation bias (attention asymmetry) in psychology. Both share the same text-level signature and are captured by Concept 7's evidence-weighing sub-facet; noted explicitly in the concept description.

- **LiveIdeaBench (Ruan et al., 2024/2025).** *Evaluating LLMs' Divergent Thinking Capabilities for Scientific Idea Generation with Minimal Context.* Nature Communications 2026.
  - https://www.nature.com/articles/s41467-026-70245-1
  - arXiv: https://arxiv.org/abs/2412.17596
  - Cited in: F49.
  - Why it matters: LLM-specific benchmark for divergent-thinking evaluation using the Guilford fluency/flexibility/originality/clarity/feasibility dimensions. Strong Phase 4 validation candidate for an extracted Hypothesis Generation vector (Concept 2), aligned with the fluency/flexibility grounding from F26.

- **Webster, D. M., & Kruglanski, A. W. (1994).** *Individual Differences in Need for Cognitive Closure.* Journal of Personality and Social Psychology.
  - Scale overview: https://sjdm.org/dmidi/Need_for_(Cognitive)_Closure_Scale.html
  - Cited in: F50, concepts.md Concept 11.
  - Why it matters: 42-item Need for Closure Scale (NFCS), the standard psychology opposing construct for Comfort with Ambiguity. Two orthogonal factors (decisiveness, need for structure). Our concept targets the need-for-structure axis.

- **Worsnip, A., Lane, D., Pratt, S., Napolitano, M. G., Gray, K., & Greene, J. A. (2025).** *Authority or Autonomy? Philosophical and Psychological Perspectives on Deference to Experts.* Philosophical Psychology.
  - https://www.tandfonline.com/doi/full/10.1080/09515089.2025.2475138
  - Cited in: F51, concepts.md Concept 13.
  - Why it matters: distinguishes reflective autonomy (reasoning-based, can support appropriate deference) from reactive autonomy (contrarian by reflex). Koestner and colleagues found the two have opposite empirical relationships with expert-advice-following behavior. Critical refinement to Concept 13 — Authority Independence targets reflective autonomy, not contrarianism. Has direct implications for Phase 3 corpus design (must balance deference and dissent passages).

- **Frederick, S. (2005).** *Cognitive Reflection and Decision Making.* Journal of Economic Perspectives.
  - http://bear.warrington.ufl.edu/brenner/mar7588/Papers/frederick-jep2005.pdf
  - Cited in: F52.
  - Why it matters: the Cognitive Reflection Test (CRT), 3-item test for the disposition to suppress impulsive wrong answers and engage deliberate reflection. Reported to be a stronger predictor of heuristics-and-biases task performance than cognitive ability alone. Strong Phase 4 validation candidate for Metacognitive Awareness and Calibrated Confidence.

- **Litman, J. A., & Spielberger, C. D. (2003).** *Measuring Epistemic Curiosity and Its Diversive and Specific Components.* Journal of Personality Assessment.
  - https://drjlitman.net/wp-content/uploads/2013/11/Litman-Spielberger-2003.pdf
  - Cited in: F53, concepts.md Concept 1.
  - Why it matters: decomposes epistemic curiosity into interest-type (I-EC, positive affect and diversive exploration) and deprivation-type (D-EC, aversive uncertainty and specific gap-filling). Our sub-facets span both types by construction; noted in the concept description.

- **Epistemic Trust, Mistrust and Credulity Questionnaire (ETMCQ).** Campbell et al. and revised version.
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC8051785/
  - Revised version (ETMCQ-R): https://www.cambridge.org/core/journals/bjpsych-open/article/development-and-validation-of-the-revised-epistemic-trust-mistrust-and-credulity-questionnaire-etmcqr/5308852B913DC422C9A2B3C38742D250
  - Cited in: F54, concepts.md Concept 13.
  - Why it matters: validated three-factor epistemic trust structure (trust, mistrust, credulity). Provides the symmetric credulity failure mode on the other side of F51's reflective-autonomy framing. Concept 13 now names both reactive mistrust and epistemic credulity as failure modes flanking the virtuous middle.

- **Muenster Epistemic Trustworthiness Inventory (METI) — Hendriks, Kienhues, & Bromme (2015).**
  - https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0139309
  - Cited in: F54.
  - Why it matters: three-factor scale (expertise, integrity, benevolence) distinguishing epistemic trustworthiness from mere credibility. Complements ETMCQ for the source-evaluation side of reflective autonomy.

- **Understanding Reasoning in Thinking Language Models via Steering Vectors.** arXiv:2506.18167 (2025/2026).
  - https://arxiv.org/html/2506.18167v1
  - Cited in: F55.
  - Why it matters: the most concept-specific external validation found to date. Identifies reasoning behaviors (expressing uncertainty, hypothesis validation, backtracking, cross-verification) that directly correspond to multiple Phronesis concepts and shows they are mediated by linear directions in activation space in 2026 open-weight thinking LLMs. Caveat: results are on reasoning-trained models; transfer to standard models like Gemma 4 E4B is not guaranteed.

- **Pennycook, G., Cheyne, J. A., Barr, N., Koehler, D. J., & Fugelsang, J. A. (2015).** *On the Reception and Detection of Pseudo-Profound Bullshit.* Judgment and Decision Making.
  - https://www.cambridge.org/core/journals/judgment-and-decision-making/article/on-the-reception-and-detection-of-pseudoprofound-bullshit/0D3C87BCC238BCA38BC55E395BDC9999
  - Original scale: https://gordonpennycook.com/wp-content/uploads/2023/09/the-bullshit-receptivity-scale.pdf
  - Cited in: F56, concepts.md Concept 15.
  - Why it matters: Bullshit Receptivity Scale (BSR) measures susceptibility to semantically vacuous pseudo-profound statements. Inversely correlated with reflective reasoning and CRT. Strong cross-concept Phase 4 validation candidate — steering Evidence Grounding, Calibrated Confidence, or Logical Rigor vectors should measurably reduce BSR.

- **Facione, P. A., Sánchez, C. A., & Facione, N. C. (1994).** *Critical Thinking Disposition as a Measure of Competent Clinical Judgment: The Development of the California Critical Thinking Disposition Inventory (CCTDI).*
  - https://pubmed.ncbi.nlm.nih.gov/7799093/
  - Cited in: F57.
  - Why it matters: widely-used 7-disposition critical thinking inventory (open-mindedness, analyticity, cognitive maturity, truth-seeking, systematicity, inquisitiveness, self-confidence). Six of seven overlap with Phronesis concepts, providing convergent validation from a different research tradition. Also reinforces F44/F7 warning that dispositions do not always translate to high-quality reasoning in concrete contexts.

- **Measuring Cognitive Flexibility: A Brief Review (2024).** Frontiers in Human Neuroscience.
  - https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2024.1331960/full
  - Cited in: F58.
  - Why it matters: documents that cognitive flexibility measures are only weakly associated (or not at all) with open-mindedness / AOT measures. Negative result confirming the correctness of our taxonomy's implicit omission of cognitive flexibility as a concept.

- **Aristotle — Nicomachean Ethics, Book II (the golden mean).**
  - Stanford Encyclopedia: https://plato.stanford.edu/entries/aristotle-ethics/
  - Cited in: F59, concepts.md Design Principles.
  - Why it matters: foundational philosophical source for the golden-mean structure (excess/mean/deficiency) that Phronesis now uses as an explicit design principle for concept structuring and corpus generation.

- **Zagzebski, L. (1996).** *Virtues of the Mind: An Inquiry Into the Nature of Virtue and the Ethical Foundations of Knowledge.* Cambridge University Press.
  - https://www.cambridge.org/core/books/virtues-of-the-mind/4C29D940655E5EB27FFFA25141F7526B
  - Cited in: F59.
  - Why it matters: contemporary virtue epistemology extending Aristotle's framework to intellectual virtues specifically, grounding phronesis (practical wisdom — the project's name) as central to both moral and intellectual virtue. Anchors the philosophical tradition Phronesis is operating within.

- **Steering Vector Transfer via Orthonormal Transformations and Semantic Pairing.** OpenReview 2025.
  - https://openreview.net/forum?id=iD8uUeCBy5
  - Cited in: F60.
  - Why it matters: empirical demonstration that steering vectors transfer across model families via structure-preserving transformations (0.50–0.56 cosine similarity, 72% improvement with semantic pairing). Reduces the F55 caveat that reasoning-trained-model findings may not transfer to standard models.

- **Analyzing the Generalization and Reliability of Steering Vectors.** ICML 2024.
  - https://www.aimodels.fyi/papers/arxiv/analyzing-generalization-reliability-steering-vectors
  - Cited in: F60.
  - Why it matters: reports Gemma 2 IT → Gemma 2 base transfer achieving ~20% instruction-following improvement. Direct evidence for within-Gemma-family transfer, highly relevant to our target Gemma 4 E4B.

- **Stanovich, K. E., West, R. F., & Toplak, M. E. (2016).** *The Rationality Quotient: Toward a Test of Rational Thinking.* MIT Press.
  - https://mitpress.mit.edu/9780262535274/the-rationality-quotient/
  - Thorndike Award Address: http://www.keithstanovich.com/Site/Research_on_Reasoning_files/Stanovich_EdPsy_2016.pdf
  - Cited in: F61.
  - Why it matters: CART is the 20-subtest comprehensive rationality assessment that Phronesis is effectively testing for a neural implementation of. Serves as both a Phase 4 selective validation candidate and a conceptual parent framework for the project writeup.

- **Activation steering failure-case literature (documented negative results).**
  - Latent Reasoning Sprint #3: https://www.lesswrong.com/posts/mXuqpJkJpaeTjyCgm/latent-reasoning-sprint-3-activation-difference-steering-and-1
  - KV Cache Steering (2507.08799): https://arxiv.org/pdf/2507.08799
  - Deception steering exploration: https://github.com/Venn1998/steering-vectors-from-finetuning
  - Cited in: F62, F64.
  - Why it matters: documents specific failure cases (instruction hierarchy, deception, latent-reasoning vector averaging) and the asymmetry finding that positive and negative traits may not lie on a single linear axis. Direct adversarial grounding for the F62 caveat on F59's golden-mean geometry assumption and for the F64 risk assessment on Intellectual Honesty's extraction difficulty.

- **Dispositions — Stanford Encyclopedia of Philosophy** and related work on the dispositional/propositional knowledge dichotomy.
  - https://plato.stanford.edu/entries/dispositions/
  - Cited in: F63.
  - Why it matters: documents that the dispositional/propositional dichotomy used in F45 is philosophically contested, with contemporary work arguing knowledge-that is a species of dispositional knowledge-how. Does not invalidate the ML empirical finding of F45 but cautions against over-claiming the precision of the philosophical distinction in the writeup.

- **Steering Externalities: Benign Activation Steering Unintentionally Increases Jailbreak Risk for Large Language Models.** arXiv:2602.04896.
  - https://arxiv.org/html/2602.04896
  - Cited in: F65, project.md success criteria.
  - Why it matters: documents that benign activation steering can increase jailbreak vulnerability as an unintended side effect. Direct basis for the F65 requirement that Phase 4 success criteria include explicit safety-behavior degradation checks (refusal rates on known-jailbreak prompts), not just the primary virtue-benchmark improvement.

- **Steering Without Side Effects: Improving Post-Deployment Control of Language Models.** arXiv:2406.15518.
  - https://arxiv.org/html/2406.15518v1
  - Cited in: F65.
  - Why it matters: documents coherence/fluency degradation, non-monotonic steering effects, and feature entanglement as generic steering failure modes. Direct grounding for the F65 four-way degradation check.

- **Zhang, M. et al. (2022).** *Correct-N-Contrast: A Contrastive Approach for Improving Robustness to Spurious Correlations.* arXiv:2203.01517.
  - https://arxiv.org/abs/2203.01517
  - Cited in: F66.
  - Why it matters: theoretical grounding for the correctness-confound mitigation strategy. Establishes that robust representations require samples where the target label and the spurious attribute are decoupled, which is exactly what our "virtuous-but-wrong" 20–30% corpus design does at the data level (CNC does it at the loss level).

- **Lindsey, J. et al. — "I found >800 orthogonal 'write code' steering vectors" (LessWrong post).**
  - https://www.lesswrong.com/posts/CbSEZSpjdpnvBcEvc/i-found-greater-than-800-orthogonal-write-code-steering
  - Cited in: F67, concepts.md golden-mean design principle.
  - Why it matters: documents that a single apparent behavior can have hundreds of orthogonal activation-space directions all producing it. Sharpens the F62 caveat on F59's golden-mean geometry — not only is the virtue/failure axis possibly non-collinear, the virtue direction itself may not be unique. Direct implication: Phase 4 must run multi-seed extraction and report vector spread, and claims should be "a humility direction" not "the humility direction."

- **Mind the Performance Gap: Capability-Behavior Trade-offs in Feature Steering.** arXiv:2602.04903.
  - https://arxiv.org/html/2602.04903
  - Cited in: F68, project.md success criteria.
  - Why it matters: directly compares feature steering to prompting on reasoning benchmarks and reports that "simple prompting consistently outperforms feature steering methods across both model scales" (66.25% Llama-8B, 86.88% Llama-70B). Basis for the F68 success-criterion requirement that Phronesis vectors must beat a prompt baseline, not merely improve over the unsteered baseline, to demonstrate the value of the methodology.

- **Steering Vector Fields for Context-Aware Inference-Time Control in Large Language Models.** arXiv:2602.01654.
  - https://arxiv.org/html/2602.01654
  - Cited in: F69.
  - Why it matters: documents that traditional fixed-vector steering degrades over long generations as hidden-state representations drift. Proposes adaptive refresh-every-K-steps solution. Direct basis for the F69 requirement that Phase 4 evaluation test both short and long generation conditions to detect length-dependent decay.

- **In-Distribution Steering: Balancing Control and Coherence in Language Model Generation.** arXiv:2510.13285.
  - https://arxiv.org/html/2510.13285v1
  - Cited in: F69.
  - Why it matters: another approach to the steering-vector-decay problem, constraining steering to remain within the model's natural activation manifold. Alternative adaptive method noted for Phase 4 follow-up if fixed-vector steering fails on long outputs.

- **A Survey on LLM-as-a-Judge.** arXiv:2411.15594.
  - https://arxiv.org/html/2411.15594v6
  - Cited in: F70.
  - Why it matters: documents reliability limitations of LLM-as-judge for subjective annotation tasks. Basis for the F70 requirement that Phase 3 review-rubric.md treat LLM-judge output as first-pass only, with human spot-checks as validation and disagreement tracked as a signal about rubric clarity.

- **Beyond Model Collapse: Scaling Up with Synthesized Data Requires Verification.** arXiv:2406.07515.
  - https://arxiv.org/abs/2406.07515
  - Cited in: F71.
  - Why it matters: empirical basis for the claim that verification of synthetic data is necessary to prevent model collapse. Justifies F71's requirement that Phase 2 corpus generation include external verification (different generator, different family, or human review) and cannot rely on self-verification by the generator.

- **Knowledge Collapse in LLMs: When Fluency Survives but Facts Fail under Recursive Synthetic Training.** arXiv:2509.04796.
  - https://arxiv.org/html/2509.04796v1
  - Cited in: F71.
  - Why it matters: documents the "confidently wrong" phenomenon where synthetic-trained models maintain format adherence while factual accuracy degrades. Directly relevant to our correctness-confound mitigation strategy — the virtuous-but-wrong 20–30% passages will be difficult to generate because the knowledge-collapse pattern runs exactly counter to what we need.

- **Verbalized Sampling: How to Mitigate Mode Collapse and Unlock LLM Diversity.** arXiv:2510.01171.
  - https://arxiv.org/html/2510.01171
  - Cited in: F71.
  - Why it matters: RLHF mode collapse reduces LLM output diversity and limits their effectiveness for synthetic data generation. Part of the F71 argument that our corpus needs anti-collapse constraints (human-written anchors, multi-generator, explicit diversity metrics).

- **Demystifying Synthetic Data in LLM Pre-training: A Systematic Study of Scaling Laws, Benefits, and Pitfalls.** arXiv:2510.01631.
  - https://arxiv.org/html/2510.01631v1
  - Cited in: F71.
  - Why it matters: systematic evaluation of synthetic data quality and the conditions under which it helps vs. hurts. Supports the F71 recommendation that synthetic data mixed with human-written anchors avoids collapse.

- **Interrater Disagreement Resolution / Learning from Disagreement literature.**
  - ACL 2021: https://aclanthology.org/2021.humeval-1.15.pdf
  - JAIR: https://www.jair.org/index.php/jair/article/download/12752/26751/29240
  - Cited in: F72.
  - Why it matters: establishes that annotator disagreement on subjective tasks is data, not just error — it signals rubric underspecification, particularly about context. Grounds the F72 requirement that Phase 3 review-rubric.md explicitly specify reviewer context per concept.

- **Extracting and Steering Emotion Representations in Small Language Models: A Methodological Comparison.** arXiv:2604.04064 (2026).
  - https://arxiv.org/html/2604.04064
  - Cited in: F73.
  - Why it matters: **the most load-bearing single paper found since the original Anthropic emotions paper.** Directly tests Anthropic's mean-subtraction extraction methodology on nine small language models (124M–3B parameters, including Gemma-2 2B). Documents that the method fails to produce valence-organized concept spaces at small scale — no negative cosine similarity between semantically opposite concept pairs. Proposes generation-based extraction as the better alternative for instruction-tuned small models (p=0.007 improvement over comprehension-based). Recommends middle layers (~50% depth), steering strength 0.005, and specifically identifies Gemma-2-2B-Instruct as optimal balance. Potentially requires a Phase 2 corpus-to-extraction interface decision.

- **HumbleBench: Measuring Epistemic Humility in Multimodal Large Language Models.** arXiv:2509.09658 (2025).
  - https://arxiv.org/abs/2509.09658
  - https://github.com/maifoundations/HumbleBench
  - Cited in: F74.
  - Why it matters: 22,831-question multiple-choice benchmark operationalizing epistemic humility as willingness to abstain ("None of the above") when no option is correct. Direct Phase 4 validation candidate for Concept 6 (Intellectual Humility), although the abstention operationalization is narrower than our full concept. Reports that mid-sized models outperform larger peers on humility — positive outlook for our small-model target, possibly warranting a F11 tier ordering revisit for Intellectual Humility.

---

## Behavioral science — scales and validated constructs

- **Krumrei-Mancuso, E. J., & Rouse, S. V. (2016).** *The Development and Validation of the Comprehensive Intellectual Humility Scale.* Journal of Personality Assessment.
  - https://pubmed.ncbi.nlm.nih.gov/26542408/
  - Cited in: F9, concepts.md Concept 6.
  - Why it matters: 22-item validated scale decomposing intellectual humility into four dimensions (independence of intellect and ego, openness to revising viewpoint, respect for others' viewpoints, lack of intellectual overconfidence). Directly informed the addition of the ego-independence sub-facet to Concept 6.

- **Baehr, J. (multiple works).** *Virtue epistemology and the Virtuous Intellectual Character Scale (VICS).*
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC11519290/
  - Cited in: F9, F18.
  - Why it matters: identified five dimensions — attentiveness, open-mindedness, curiosity, carefulness, intellectual autonomy. Notably, intellectual courage is NOT a separable dimension, which led to the removal of that concept from our taxonomy (F18).

- **Cacioppo, J. T., & Petty, R. E. (1982).** *The Need for Cognition.* Journal of Personality and Social Psychology.
  - Summary: https://en.wikipedia.org/wiki/Need_for_cognition
  - 6-item short form: https://pmc.ncbi.nlm.nih.gov/articles/PMC7545655/
  - Cited in: F17, concepts.md Concept 1.
  - Why it matters: 18-item and 6-item validated scales for intellectual curiosity / openness to effortful cognition. Informed the effort-enjoyment sub-facet added to Genuine Curiosity.

- **Fleming, Lau, and related metacognition literature.**
  - https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2014.00443/full
  - Cited in: F10.
  - Why it matters: decomposes metacognition into sensitivity, bias, and efficiency — provided empirical support for keeping Metacognitive Awareness and Calibrated Confidence as separate concepts.

- **Flavell, J. H. (1979).** *Metacognition and Cognitive Monitoring: A New Area of Cognitive-Developmental Inquiry.* American Psychologist, 34(10), 906–911.
  - https://psycnet.apa.org/doiLanding?doi=10.1037/0003-066X.34.10.906
  - Cited in: F27, concepts.md Concept 8.
  - Why it matters: the canonical metacognition framework distinguishing knowledge (declarative/procedural/conditional) from regulation (planning/monitoring/evaluating). Our Concept 8 is deliberately scoped to the monitoring dimension; the scoping rationale cites Flavell.

- **John, L. K., Loewenstein, G., & Prelec, D. (2012).** *Measuring the Prevalence of Questionable Research Practices With Incentives for Truth Telling.* Psychological Science.
  - https://journals.sagepub.com/doi/10.1177/0956797611430953
  - Cited in: F25, concepts.md Concept 10.
  - Why it matters: provides the standard behavioral inventory of scientific dishonesty (QRPs) that now grounds Concept 10 (Intellectual Honesty). Concrete anchors for what "dishonest" looks like in text.

- **McAuley, E., Duncan, T. E., & Russell, D. W. (1992).** *Measuring Causal Attributions: The Revised Causal Dimension Scale (CDSII).* Personality and Social Psychology Bulletin.
  - https://journals.sagepub.com/doi/10.1177/0146167292185006
  - Cited in: F24.
  - Why it matters: NEGATIVE result — this is attribution theory (locus, stability, personal control, external control), not causal-inference quality. Recorded in F24 as the reason we stopped looking for a direct psychology scale for Concept 4; Causal Reasoning is anchored in philosophy of science and statistics education instead.

- **Torrance Tests of Creative Thinking / Guilford's Alternate Uses Test — divergent-thinking literature.**
  - https://en.wikipedia.org/wiki/Divergent_thinking
  - Cited in: F26, concepts.md Concept 2.
  - Why it matters: four-dimension scoring (fluency, flexibility, originality, elaboration) clarified that Hypothesis Generation as an epistemic virtue is primarily about flexibility (structurally distinct alternatives), not fluency (sheer count). Sub-facet refinement.

- **Drummond, C., & Fischhoff, B. (2017).** *Development and Validation of the Scientific Reasoning Scale (SRS).* Journal of Behavioral Decision Making.
  - https://onlinelibrary.wiley.com/doi/abs/10.1002/bdm.1906
  - Cited in: F29, concepts.md Concept 15.
  - Why it matters: validated scale measuring the disposition to evaluate scientific findings on the factors that determine their quality. Directly aligns with Evidence Grounding and predicts belief calibration on contested topics.

- **Morewedge, Larrick, and debiasing intervention literature.**
  - https://marketing.wharton.upenn.edu/wp-content/uploads/2019/12/01.06.2020-Morewedge-Carey-PAPER-DebiasingTransferstotheField.pdf
  - Cited in: F31.
  - Why it matters: "consider-the-opposite" is the validated anchoring-debiasing strategy; individual differences in anchoring resistance correlate with actively open-minded thinking. Used in F31 to correct the honesty framing of the Anchoring Resistance cut rationale.

- **Chi, M. T. H., De Leeuw, N., Chiu, M.-H., & Lavancher, C. (1994).** *Eliciting Self-Explanations Improves Understanding.* Cognitive Science, 18(3), 439–477.
  - https://onlinelibrary.wiley.com/doi/10.1207/s15516709cog1803_3
  - Cited in: F32, concepts.md Concept 14.
  - Why it matters: canonical self-explanation-effect paper. Establishes that explaining one's reasoning improves understanding through constructive, integrative, and error-correcting mechanisms. Grounds Reasoning Transparency in an empirical learning-science finding.

- **Lanham, T. et al. (Anthropic).** *Measuring Faithfulness in Chain-of-Thought Reasoning.*
  - https://www-cdn.anthropic.com/827afa7dd36e4afbb1a49c735bfbb2c69749756e/measuring-faithfulness-in-chain-of-thought-reasoning.pdf
  - Cited in: F33, concepts.md Concept 14.
  - Why it matters: key prior work on whether CoT reflects internal computation. Establishes the faithfulness concept and its measurement difficulty. Used in F33 to distinguish what we can actually extract (legibility) from what we cannot (faithfulness).

- **Guan, M. Y., Wang, M., Carroll, M., Dou, Z. et al. (OpenAI).** *Monitoring Monitorability.*
  - https://cdn.openai.com/pdf/d57827c6-10bc-47fe-91aa-0fde55bd3901/monitoring-monitorability.pdf
  - Cited in: F33.
  - Why it matters: introduces monitorability as a practical substitute for faithfulness, and legibility as a measurable proxy. Directly relevant to framing what Concept 14's extracted vector represents.

- **Toulmin's Argument Pattern — scientific writing rubric literature.**
  - Example validated rubric: Timmerman et al., https://www.tandfonline.com/doi/abs/10.1080/02602930903540991
  - Cited in: F35.
  - Why it matters: six-element argument decomposition (claim, data, warrant, backing, qualifier, rebuttal) and the relevance/acceptability/sufficiency criteria provide a drop-in structure for Phase 3's review-rubric.md. Has reported inter-rater reliability (g = 0.85) in undergraduate science-writing assessment.

- **Stanovich, K. E., & West, R. F. (2007).** *Natural myside bias is independent of cognitive ability.* Also Stanovich, Toplak, and colleagues (2016, 2019, 2023) on the Actively Open-Minded Thinking Scale and the Comprehensive Assessment of Rational Thinking (CART).
  - 2023 overview: http://maggietoplak.com/wp-content/uploads/2025/04/Stanovich_Toplak_AOT_JIntell_2023_on-website.pdf
  - Cited in: F39, concepts.md Known risks.
  - Why it matters: AOT is a validated single-construct measure that unifies 6–7 of our concepts as facets of one latent trait. It uniquely predicts heuristics-and-biases task performance in adults. Both validation (the intervention hypothesis is plausible — AOT-type dispositions predict reasoning improvement) and challenge (psychology treats these as one construct, which may replicate at the activation-vector level and cause collinearity in our specificity matrix). Flagged as a post-extraction analysis target.

- **Wehner, J. (2025).** *Taxonomy, Opportunities, and Challenges of Representation Engineering for Large Language Models.* arXiv:2502.19649.
  - https://arxiv.org/html/2502.19649
  - Cited in: F37.
  - Why it matters: surveys multi-concept vector extraction techniques including orthogonal probes, weighted combination, disentanglement losses, and k-means-on-difference-vectors for post-hoc sub-facet discovery. Validates the F12 specificity matrix idea and introduces the k-means approach as a cheap Phase 4 sub-facet analysis.

- **QDGS (Quality-Diversity Generative Sampling).**
  - https://arxiv.org/html/2312.14369v1
  - Cited in: F38.
  - Why it matters: establishes that random sampling from a generative model reproduces training-data biases; explicit attribute prompting is required for balanced synthetic datasets. Direct validation for our F4 domain-diversity quota being a required procedure, not optional bookkeeping.

- **Carleton et al. Intolerance of Uncertainty Scale (IUS-12).**
  - Cited in: F20.
  - Why it matters: two-factor structure (prospective anxiety, inhibitory anxiety) raised the question of whether Comfort with Ambiguity should split along a contemplative/actional axis. Decision: do not split (passages are contemplative by construction).

- **Lipkus, I. M., Samsa, G., & Rimer, B. K. (2001).** *General Performance on a Numeracy Scale among Highly Educated Samples.* Medical Decision Making.
  - https://journals.sagepub.com/doi/10.1177/0272989X0102100105
  - Cited in: F23, concepts.md Concept 5.
  - Why it matters: validated numeracy ability scale. Informed the clarification that Quantitative Groundedness is dispositional, not ability-based, and therefore distinct from numeracy-literature measurement.

- **Cokely et al. (2012).** *Berlin Numeracy Test.* Judgment and Decision Making.
  - https://www.cambridge.org/core/journals/judgment-and-decision-making/article/measuring-risk-literacy-the-berlin-numeracy-test/A9B26516D12D48EFA4BD3560E2001E8E
  - Cited in: F23.
  - Why it matters: same as Lipkus — the most widely used modern numeracy/risk-literacy scale, reinforces the ability/disposition distinction.

---

## Cognitive science — scientific reasoning models

- **Klahr, D., & Dunbar, K. (1988).** *Dual Space Search During Scientific Reasoning.* Cognitive Science, 12, 1–48.
  - https://users.cs.northwestern.edu/~paritosh/papers/sketch-to-models/klahr-dunbar-dual-space-search-cogsci-1988.pdf
  - Cited in: F21, concepts.md Design Principles.
  - Why it matters: canonical Scientific Discovery as Dual Search (SDDS) model — three components (hypothesis space search, experiment space search, evidence evaluation). Grounds Stages 1–3 of our six-stage taxonomy; Stages 4–6 are honestly marked as extensions beyond SDDS.

- **Pearl, J. — Pearl's Causal Hierarchy (PCH).** Foundational work on causal inference; see Bareinboim, Correa, Ibeling, Icard on the formal PCH framework.
  - Overview: https://web.cs.ucla.edu/~kaoru/3-layer-causal-hierarchy.pdf
  - Cited in: F42, concepts.md Concept 4.
  - Why it matters: three-level hierarchy of causal reasoning (association → intervention → counterfactual) that grounds Concept 4's scope. Our sub-facets focus deliberately on Levels 1–2 (the practical workhorses of scientific reasoning) and justify not adding a Level-3 counterfactual sub-facet on collinearity grounds.

---

## Philosophy of argumentation

- **Dennett, D. (multiple works).** *The four-step framework for charitable argumentation.*
  - https://effectiviology.com/principle-of-charity/
  - Cited in: F22, concepts.md Concept 12.
  - Why it matters: four-step operationalization (restate-so-they-agree → list-agreements → mention-what-learned → then-criticize) became the basis for Concept 12's expanded four sub-facets.

- **Principle of charity vs. steelmanning distinction.**
  - https://en.wikipedia.org/wiki/Principle_of_charity
  - Cited in: F22.
  - Why it matters: clarified that "charity" (faithful reconstruction) and "steelmanning" (strengthening beyond the original) are philosophically distinct; our concept covers both.

---

## Text style transfer (NLP)

- **Text style transfer literature, general pointer.**
  - Fast Forward Labs: https://blog.fastforwardlabs.com/2022/03/22/an-introduction-to-text-style-transfer.html
  - Review paper: https://arxiv.org/pdf/2109.15144
  - TSTBench: https://pmc.ncbi.nlm.nih.gov/articles/PMC12191983/
  - Cited in: F19, planned for generation-guidelines.md.
  - Why it matters: the NLP field has decades of work on "preserve content while changing style" which is structurally identical to our neutral-baseline-then-contrastive-rewrite step. Key principles: two-axis evaluation (style capture + content preservation), minimal-edit approaches outperform full rewrites, parallel corpus scarcity is a known problem that justifies our synthetic triplet approach.

---

## Anthropic skills and documentation

- **Anthropic Skills Repository.**
  - https://github.com/anthropics/skills
  - Cited in: Phase 2 reference gathering, structural conventions for our own markdown files.
  - Why it matters: source of structural conventions (imperative voice, explain reasoning not just rules, progressive disclosure, worked examples, ~500 line limit) that inform how we write our own guidelines files.

- **Anthropic doc-coauthoring skill.**
  - Cited in: Phase 2 reference gathering.
  - Why it matters: three-stage workflow (context → refinement → reader-testing) that maps onto our own generate-refine-review pipeline.

---

## Steering methods (2025-2026)

- **Spherical Steering: Geometry-Aware Activation Rotation for Language Models.** arXiv:2602.08169, February 2026.
  - URL: https://arxiv.org/abs/2602.08169
  - Cited in: F79.
  - Why it matters: norm-preserving rotation outperforms additive CAA by ~10% on TruthfulQA/COPA/Storycloze. Includes confidence gate for dynamic strength. Phase 5 primary steering method.

- **Fine-Grained Activation Steering: Steering Less, Achieving More (AUSteer).** arXiv:2602.04428, February 2026.
  - URL: https://arxiv.org/abs/2602.04428
  - Cited in: F80.
  - Why it matters: decomposes block-level steering into per-dimension (atomic unit) steering, achieving better results with fewer perturbed activations. Fallback if block-level steering degrades coherence.

- **Conditional Activation Steering (CAST).** ICLR 2025 spotlight. Bruce Lee et al.
  - URL: https://brucewlee.com/blog/posts/conditional-activation-steering.html
  - Cited in: F81.
  - Why it matters: gates steering on input context, preventing over-application. Essential for deployment beyond controlled eval prompts.

- **LayerNavigator: Finding Promising Intervention Layers for Efficient Activation Steering.** OpenReview 2026.
  - URL: https://openreview.net/forum?id=wj4lM45xQR
  - Cited in: Phase 5 planning.
  - Why it matters: principled layer selection for steering, evaluating per-layer steerability. More rigorous than middle-third heuristic.

- **Selective Steering: Norm-Preserving Control Through Discriminative Layer Selection.** arXiv:2601.19375, January 2026.
  - URL: https://arxiv.org/html/2601.19375
  - Cited in: Phase 5 planning.
  - Why it matters: combines norm preservation with discriminative layer selection. Complementary to spherical steering.

- **Activation Steering in 2026: A Practitioner's Field Guide.** Subhadip Mitra, 2026.
  - URL: https://subhadipmitra.com/blog/2026/activation-steering-field-guide/
  - Cited in: Phase 5 planning.
  - Why it matters: practical guide covering coefficient tuning (inverted-U response, binary search protocol), multi-metric evaluation, and category-specific best practices.

---

## How to add new references

When findings.md cites a new paper, scale, or benchmark:
1. Add it under the most appropriate section above (or create a new section if genuinely novel category).
2. Include: citation, URL, which findings reference it, and a one-sentence "why it matters."
3. Keep entries concise — this file is an index, not a literature review.
4. If a reference turns out to be less load-bearing than initially thought, leave it in but note the downgrade rather than deleting.
