# Roadmap — July 2026: from recall-calibration to reasoning-calibration

*Drafted 2026-07-02 (post F172–F179 + content-controlled-extraction result). This is the working plan for the next ~1–2 weeks. Governed by `docs/EXPERIMENTATION_GUIDELINES.md` (the floor) — every experiment below inherits its rules (multi-seed random controls, hand-read labels, tiered claims, measure-what-you-claim).*

---

## 0. Where we stand (one paragraph)

The calibration arc on **recall** is closed and coherent: small models partially read their own knowledge edge (F172: AUROC 0.80; F176: 32B internal 0.87 but verbally overconfident); reading is failure-mode-specific — blind on believed myths (F178); a single steering vector cannot cleanly calibrate (F173 partial at 4B; F179 global refuse-knob at 32B) **but** most of the 32B failure was extraction contamination: content-controlled extraction (entity-free, length-matched, mean-pooled) flips the vector's SAE decomposition from geographic/format features to genuine epistemic features ("don't know", "not sure if") and recovers partial selectivity (~33% confab-hedge / ~50% knowns-kept at best α; template got 0% kept). The clean *usable* lever remains **read-then-act** (gate→search doubles accuracy at both scales, F175/F177). Meanwhile Lotfi et al. (arXiv:2606.00206) flagged a **quantization confound** in our F177 "thinking hurts at 32B" claim, and independently validated the broader thesis that models often *have* the answer but fail to commit to it.

## 1. Hardware reality (checked 2026-07-02)

- VM: `alphaludo-l4`, g2-standard-8, **1× L4 (24 GB VRAM)**.
- **GPU quota: 1 total (fully used). A100 quotas: 0.** More VRAM = a quota-increase request to Google (days, uncertain, often denied for small accounts) — *not* a knob we can turn this week. Optionally file the request in parallel (free to ask: `GPUS_ALL_REGIONS` 1→2 and/or `NVIDIA_A100_80GB` 0→1); treat approval as a bonus, never a dependency.
- **fp16 (unquantized) ceiling on the L4: ~8B params.** Fits: Qwen3-8B (~16 GB), DeepSeek-R1-Distill-Qwen-7B (~15 GB), R1-Distill-Llama-8B (~16 GB). Does not fit: 14B fp16 (~28 GB), 32B fp16 (~65 GB).
- **DECISION: small-clean-first.** Do the science on ≤8B in fp16 (no quantization confound, faster iteration, Neuronpedia SAE available for Qwen3-8B @ L18). Scale-verify *conclusions* at 32B-4bit afterwards, explicitly labeling the quantization caveat. This mirrors what worked in the calibration arc (4B → 32B) and matches the budget.

## 2. Phase 0 — close out the recall arc (VM queue, ~1 day, already staged)

| # | Item | Status | Output |
|---|------|--------|--------|
| 0.1 | TQA-32B transfer (does F178's myth-blindness worsen at scale, per F176 prediction?) | **RUNNING** (day3, ~150 items) | finding vs F178 table |
| 0.2 | LLM-judge the TQA-32B answers (substring scoring invalid — F178 lesson) | after 0.1 | judged labels |
| 0.3 | **Quantization 2×2** for thinking-recall: {4B, 8B} × {fp16, 4-bit}, identical params (k=5, n=100, think-512). Settles the Lotfi confound on F177. Prediction if quantization-driven: think-hurts in the 4-bit column only. | staged (`mvp/run_quant2x2.sh`), fires after 0.1 | F177 amendment |
| 0.4 | LLM-judge the content-controlled steering windows (32B @0.15, 4B @0.04) — auto-hedge regex over/under-counted both ways; tier the CC-selectivity claim on judged numbers | anytime (local) | firm tier for CC finding |
| 0.5 | F177 caveat in findings.md citing Lotfi | **DONE** 2026-07-02 | — |

**Exit criteria:** F177 disentangled (scale vs quantization); TQA-32B written up; CC-selectivity tiered on judged data. Then the recall arc is publication-grade end to end.

## 3. Phase 1 — reasoning baselines (the pivot)

**Why pivot to reasoning (the thesis):** humility cannot create a missing fact — recall is *knowledge-bound*, so the only useful "act" was external (search). Reasoning is *compute-bound*: the model decides how long to think, when to backtrack, when to commit. Those are exactly the decisions calibration machinery should govern. Our strongest prior evidence agrees: the project's controlled steering positives are both *decision*-shaped (F148 tool-use invoke-calibration; F109/F111-era **OpenR1-Qwen-7B commitment-rescue**: baseline fails by "verbose self-debate, no commit" → commit-vector steering turned 0/12 into 8–9/12). The 2025–26 literature converges here too (Lotfi's overthinking errors; Manifold Steering's "overthinking is a single direction, but intervention plateaus/deteriorates with strength" — the same knife-edge we found).

**Models (both, for two data points; both fit fp16 on the L4):**
- **DeepSeek-R1-Distill-Qwen-7B** — primary. Reasoning-tuned, the exact family from Lotfi et al. (their 1.5B/7B/14B ladder), well-characterized baselines (AIME ~55%, MATH-500 ~93%, GPQA-D ~49% reported; we verify ourselves).
- **Qwen3-8B** (thinking mode) — secondary. Hybrid thinker, same family as our whole prior arc, **public Neuronpedia SAE (L18)** → mechanistic readout available for whatever we extract.

**Benchmarks (borrowed from Lotfi et al.):** MATH-500 (hard slice), AIME-120, GPQA-Diamond, GSM8K (expect saturated on distills — include a small probe just to confirm, then drop). Coding (LiveCodeBench) deferred — heavier harness, later.

**Step 1 (baseline verification — user rule: verify difficulty before experimenting):** run each benchmark sample (n≈100 per bench per model, k=4 samples + greedy) → per-item difficulty map. Keep the **30–70% accuracy band** as the experimental slice (hard-but-not-hopeless). This is the reasoning-domain analogue of the F172 knowledge-edge map, and doubles as our own replication check of Lotfi's overthinking taxonomy:
- save FULL thinking traces (F177 lesson: we saved only extracted answers and couldn't test the right-answer-in-trace claim);
- measure: trace length, overthinking-marker counts (Wait/But/Alternatively/maybe/perhaps), and **right-answer-in-trace-but-not-emitted rate** (their 52% claim, our setup — LLM-judge over traces).

**Exit criteria:** difficulty map per model; overthinking-error rate measured; experimental slice frozen and committed before any intervention (prereg discipline).

## 4. Phase 2 — the calibration ladder, transplanted to reasoning

Run on the frozen hard slice, in order; each step gates the next:

1. **READER (does the model know when its reasoning is going right?).** During/after CoT, read internal signals (mean-entropy, seq-logprob, P(True) on the proposed answer, semantic-entropy across k samples) → AUROC vs per-item correctness. *The F172 question for reasoning.* Also: does the reader fire mid-trace at the moment the right answer first appears (the commit-point detector)?
2. **DIRECTION (content-controlled from day one).** Extract v_commit / v_overthink with the content-controlled recipe (natural diverse phrasings, length-matched, no problem-content in templates; mean-pool) — never repeat the F179 template mistake. SAE-decompose on Qwen3-8B L18 (Neuronpedia) before any behavioral test: if the vector isn't made of deliberation/commitment features, fix extraction first. This also redoes the old OpenR1 commit-rescue with clean tools (its era's v_IH was register-contaminated per F114).
3. **GATE→COMMIT (read-then-act, our differentiated angle).** Nobody in the literature gates on the model's *own confidence signals*: Lotfi's logit-penalty is unconditional; Manifold/TACT steer with fixed strength. Ours: monitor the reader during generation → when confident-answer-detected, push commit (or just force-emit); when not, allow continued thinking. **Baseline comparator: Lotfi's logit-penalty (50 markers, λ 0.5–4.0)** — trivial to implement, must beat or match it to matter, plus random-control per the floor.
4. **AGENTIC HARNESS (last, only if 1–3 show signal).** Multi-step problems; harness = plan→step→self-check→(commit | revise | tool). The gate becomes the controller's decision function — the reasoning analogue of gate→search (F175). Compare vs TACT-style always-on steering.

## 5. Phase 3 — scale + writeup checkpoints

- Scale-verify the Phase-2 winner(s) on 32B-4bit (explicitly caveated) — and on R1-Distill-14B-4bit if useful (same family as 7B, isolates scale within family).
- Revisit the quota request if granted (A100-80G would allow 32B-fp16 — the clean scale point).
- **Writeup checkpoint after Phase 0 closes:** the recall-calibration arc (F172–F179 + CC-extraction) is a complete, honest story — draft it before reasoning results start mixing in. Publishing venue/process per `feedback_honest_publication` (disclosed AI collaboration; LW AI-content block noted).

## 6. Decision log (this roadmap's commitments)

| Decision | Choice | Rationale |
|---|---|---|
| More VRAM? | No (quota=1, A100=0). Optional async quota request. | Checked 2026-07-02; not a this-week knob. |
| Model size strategy | ≤8B fp16 primary; 32B-4bit for scale-verification only | Kills quantization confound at the frontier where we iterate. |
| Reasoning-tuned vs vanilla | **Both** (R1-Distill-7B primary, Qwen3-8B secondary) | User: more data points; distills = literature-comparable; Qwen3-8B = SAE + continuity. |
| Skip baselines? | No — Phase 1 verifies difficulty first | User rule + F169/F170 lesson (question distribution drives conclusions). |
| Extraction method | Content-controlled only, SAE-check before behavior | F179 mechanism lesson — locked into the floor. |
| VM lifecycle | Keep up while Phase 0–1 queue is live | Standing user directive (stockout > idle billing). |

## 7. Open questions (park, don't block)

- Does the CC-selectivity window survive LLM-judge scoring (0.4)? If yes at TIER B+, is there a two-vector or gated-write scheme that closes the remaining known-damage? (Manifold Steering's manifold-projection idea may be the upgrade path.)
- TQA-32B: if internal signals are *also* blind on myths at scale, does verbalized P(True) still survive (F178's survivor)? That would make the explicit self-check the only scale-robust myth detector we have.
- Reasoning reader: is there a *single* mid-trace signal that marks "the right answer just appeared" (Lotfi's 52% cell) — that alone would be a paper-sized result if clean.
