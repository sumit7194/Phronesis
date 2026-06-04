# Tool-use calibration experiment (June 2026)

**What this doc is:** self-contained writeup of the tool-use investigation run 2026-06-04/05 on the `alphaludo-l4` VM — the long-deferred "virtue + tools" (Path B) experiment the project was originally built to run. Setup, results, the walkback, conclusions, and next directions.

**What this doc is NOT:** the numbered-findings ledger (see `findings.md` F148+), the daily log (`journal.md`), or the pre-June steering-mechanism history.

**Status:** Qwen2.5-7B + qwen3-4B complete. Qwen3.5-4B replication in progress. The answer-honesty thesis was **falsified** under manual review. The surviving result is a narrow, IH-specific **invoke-calibration** effect on thinking models.

---

## Background

The original Phronesis question (per `project.md`): does a model with an installed *virtue* + tool access use tools better than baseline + tools? The steering arm of the project closed as a rigorous negative (effects collapsed under matched-norm random controls). This experiment finally runs the tool-use half, using the existing IH (intellectual-humility) steering vector.

## Setup

- **Harness:** `mvp/run_tool_grid.py` + `mvp/tool_use_harness.py`. A `<search>QUERY</search>` stop-string protocol (web-search only, no calculator). Checkpointed/resumable per condition. Searcher: `mock` (deterministic, for invoke-rate) or `ddgs` (live DuckDuckGo, for answer quality).
- **Models:** `qwen2.5-7b-it` (non-thinking), `qwen3-4b` (thinking). Qwen3.5-4B (thinking, MoE/multimodal) replication in progress.
- **Steering:** `mvp/steer.py` AdditiveSteeringHook — unit-normalizes the vector, adds `alpha * v_hat` to the residual stream at a layer, for the whole trajectory. IH vector = `triplets-intellectual-humility/last_token/layer_17`. alpha in {4,8,16,24,32}.
- **Prompts:** `corpus/eval-prompts/tool-use-v1.json` (32: obscure-fact + recent-event = "should-search" (16), calculation (7), tool-not-needed/control (9)). Plus `tool-use-confab-v1.json` (20 false-premise / obscure / true-control) for the answer-quality test.
- **Conditions per model:** baseline / v_IH (alpha sweep) / matched-norm random (multi-seed) / other virtues (CC-full, CC-numeric, EG, RT, VC, combined).
- **Metric:** tool-INVOKE rate by category (auto). **Discrimination = should-search% − over-call%.** Answer quality = HAND-SCORED (no regex; per F94/F119 discipline).

## Results

### 1. Qwen2.5-7B — already at ceiling; steering null
Searches 100% on should-search prompts at baseline; over-calls on 6/9 controls. Steering (IH, any alpha to 32) and random change **nothing**. No headroom. (Resolves the old "is baseline tool-use already high?" / 68.8% question: yes, for this model.)

### 2. qwen3-4B — a real invoke-calibration effect (survives all controls)
Discrimination: baseline **+31%** (should 12/16, over-call 4/9) → **v_IH α16 +88%** (should 14/16, over-call 0/9). It searches *more* when it should AND stops over-calling on trivia. Controls:
- **Direction-specific:** matched-norm random ×3 seeds at α16 can't reproduce it — random suppresses search indiscriminately (should-search craters to 3–7/16).
- **Dose-responsive:** inverted-U; peaks ~α16, washes out at α32 (where it just searches everything, 91%).
- **Token-budget robust:** identical at 2048 and 4096 tokens (not a thinking-exhaustion artifact).
- **Model-specific:** Qwen2.5-7B flat-null at all alpha → needs a thinking phase to act on.
Queries verified genuine (well-formed); control answers verified correct & direct. Not degeneration.

### 3. Virtue-specificity — IH-specific; CC dissociates; combined dilutes
Discrimination at α16: **IH +88** | CC-full +56 | combined +46 | EG +39 | baseline +31 | CC-numeric +29 | VC +28 | random ~+13 | RT 0.
- **IH is the only *discrimination* virtue** (moves both levers).
- **CC-full** pushes should-search to 100% but keeps over-calling at 44% → it's "search MORE", not "search smarter". IH and CC **dissociate** (knowledge-boundary vs thoroughness). So the effect is IH-specific, NOT generic uncertainty-family.
- **Combined < IH alone** → mixing dilutes; single best vector wins (replicates F89 "hydra hypothesis" in the tool domain).
- Matches the old geometry result (IH the orthogonal odd-one-out vs CC/EG/RT).

### 4. Answer honesty — the WALKBACK (the thesis dies here)
A 15-prompt false-premise battery with **live DuckDuckGo**, **hand-scored** (read every answer):
- Baseline: **7 caught / 2 confabulated / 6 no-answer** (ran out of tokens / broke).
- v_IH α16: **8 caught / 5 confabulated / 2 hedge / 0 no-answer**.
- **v_IH confabulated MORE (5 vs 2)** — invented iPhone-16-Mini specs, a "magnitude 4.8" Paris quake, a Switch Pro price, an Einstein "1960 interview", accepted the Amazon-Walmart merger.
- It **searched on almost all of these and still confabulated** → better tool-CALLING ≠ better ANSWERS. The single Figma "2025 acquisition" win that looked great in a 5-prompt peek was NOT representative.
- True-controls fine (no over-refusal of Qatar/Croatia). Obscure-real: v_IH slightly better (got Øresund=2000; baseline confabulated 1991).

### 5. Mechanism + the decoupling
- v_IH α16's effect is **decisiveness / self-trust** ("commit to what you think you know"). The same push **helps** over-calling (stops reflexively verifying known facts — baseline qwen3-4B literally reasons *"the capital is Paris, but wait, let me verify"* then searches) and **hurts** false-premise honesty (commits to the false premise instead of flagging it).
- **Tool-use calibration IS confidence calibration**: over-calling (under-confident, verifies the known) and confabulation (over-confident, commits to the false) are *opposite* miscalibrations on one axis. A single static "trust yourself" direction cannot win both — which is the principled argument for **conditional/gated steering**.
- The confabulation happens at **turn-2** (interpreting results), where "commit" is the wrong push; turn-2 wants skepticism, possibly a different/opposite direction.

## Conclusions

- **Surviving result (narrow, real):** IH-steering improves a *thinking* model's tool-INVOCATION calibration (when to reach for search), direction-/virtue-/dose-/model-robust. IH-specific.
- **Clean negative:** that improvement does **not** carry to answer honesty; on false premises v_IH confabulates more. The "virtue + tools → better answers" thesis is **not supported**.
- **Interesting decoupling:** better retrieval behavior ≠ better epistemics. On the 2026 agentic-honesty frontier, this is a useful cautionary result.

## Caveats
- Invoke-rate uses mock search (valid: the invoke decision is turn-1). Answer quality used real search, n=15 false-premise, hand-scored, single rater.
- Single prompt set, greedy decoding, qwen3-4B only (Qwen3.5 pending).
- Absolute over-call rates are setup-specific (tool dangled + a balanced-but-present system prompt). The baseline-vs-steered-vs-random *comparison* is the valid part.

## Next directions
1. **Conditional / PID steering** (the agreed next step): gate the IH "self-trust" push to fire only when the model genuinely knows (stop over-verifying) and NOT when the premise is shaky (avoid confabulation). IH is the lever to gate (per §3).
2. **Turn-2 skepticism steering**: intervene at result-interpretation with a premise-checking direction, not "commit".
3. **Qwen3.5-4B replication** (in progress): does the invoke-calibration hold on a newer-generation thinking model?

## Pointers
- Code: `mvp/run_tool_grid.py`, `mvp/tool_use_harness.py`, `mvp/analyze_tool_grid.py`, configs `mvp/tool_grid_*.json`.
- Data: `mvp/results/tool_use_grid/{qwen25,qwen3,qwen3_4k,qwen3_real,qwen3_confab}/`.
- Findings ledger: `findings.md` F148+. Memory: `project_tool_use_calibration_finding.md`.
