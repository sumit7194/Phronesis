# Phase 5 — 8-virtue scale-up plan

**Status:** Draft v1 (Day 17, 2026-04-24). **Conditional.** This plan activates ONLY if the MVP outcome is "all_clean" or "partial" per F98 exit criteria. If MVP outcome is "collapse", this plan is archived and we replan from scratch.

**Scope:** Forward-looking. What would it take to go from the 4-virtue MVP to the 8-virtue full study per `docs/mvp-virtues.md`?

**Non-scope:** This doc does NOT commit us to Phase 5. It exists so that IF the MVP succeeds, we have a pre-thought-out direction — not as a scale-first manifesto.

---

## 1. What Phase 5 adds (per mvp-virtues.md)

The 4 MVP virtues are: Calibrated Confidence (9), Intellectual Humility (6), Evidence Grounding (15), Reasoning Transparency (14).

Per `mvp-virtues.md` "Full-study virtue set (8)", Phase 5 adds:

- **Logical Rigor** (Concept 3) — Stage 2
- **Hypothesis Generation** (Concept 2) — Stage 1
- **Steelmanning** (Concept 12) — Stage 5
- **Intellectual Honesty** (Concept 10) — Stage 4

Together: 8 virtues spanning all 6 stages of the `concepts.md` taxonomy (except stages 2-3's collinear-cluster virtues which remain deferred).

**Specificity matrix becomes 8×8 = 64 cells.** The key interpretive change vs MVP: Phase 5 tests whether the specificity property holds at higher N — i.e., whether adding four more virtues reveals cross-talk that the 4×4 didn't surface.

---

## 2. Activation conditions — when does Phase 5 start?

Phase 5 activates ONLY if ALL of:

- [ ] MVP outcome is `all_clean` or `partial` per F98
- [ ] No widespread collapse across MVP virtue pairs (i.e., not more than 1 MVP pair showing |cos| > 0.5)
- [ ] Day 15 guiding principle #3 ("solidify before scale") is honored — we actually understand WHY MVP worked before scaling
- [ ] Infrastructure triggers below are met (see §3)

If any of these fail, Phase 5 is deferred or re-scoped.

---

## 3. Infrastructure that must exist BEFORE Phase 5 starts

The following are Phase-5 prerequisites per `docs/mvp-virtues.md`, `docs/scoring.md`, and lessons from MVP:

### 3.1. Scorer upgrade (per scoring.md "Scorer Upgrade Plan")

At Phase-5 scale, manual-first scoring is not tenable (8 virtues × multiple benchmarks × multiple α × multiple layers × multiple seeds quickly exceeds hundreds of hours of human review).

Required:
- **LLM-as-judge** for hedge-wrapper confabulation detection (fixes FM-1 through FM-4)
- **Domain-adaptive EG scorer** to fix FM-7 on chemistry / engineering prose (currently EG scorer scores 0 on 5 technical-jargon passages)
- **RT scorer robustness check** across larger corpus

Estimated effort: 1-2 weeks of dedicated work. Must be validated on MVP corpus BEFORE being trusted on Phase 5 data.

### 3.2. Corpus generation automation

Current MVP corpus (80 triplets) was ChatGPT + Sonnet + substrate-reuse with ~4h of prompt iteration to land clean calibration. Scaling to 4 new virtues × 40 triplets = 160 more triplets would take another ~16h of interactive LLM + audit work.

Required:
- **Corpus-gen-v2 prompt** — refined from the MVP iteration (see git log for prompts)
- **Automatic audit script** — checks calibration, caricature-detection (the FM-6 pattern we caught on ChatGPT), domain rotation, failure-mode rotation, correctness-confound coverage
- **Substrate-reuse pipeline** — semi-automate the substrate-picking and rewrite-on-new-axis step

Estimated effort: 3-5 days of engineering.

### 3.3. GPU budget realism

Per `docs/extraction-runbook.md` §3.3 (revised Day 16-17):
- Actual GPU time per extraction: ~8-10h on L4 (not the 3h I initially estimated)
- Phase 5: 4 new virtues × 2 models × ~10h = 80h of GPU
- α-sweep: ~4h × 8 vectors × 2 models = 64h
- Specificity matrix: ~6h × 8 vectors × 2 models = 96h
- **Total Phase 5 GPU budget: ~240h = 10 days of continuous L4 time**

Options:
- **A.** Sequential on one L4 VM — ~10 days real time, cheap ($0.7/h × 240h = $168)
- **B.** Parallel across 2-3 L4 VMs — ~4 days real time, 2-3× cost
- **C.** Upgrade to A100 — faster per-hour, higher cost per-hour; may net out to same $ but cut time 3-4×
- **D.** Spot instances — 30-60% cost saving, risk of interruption

Recommend: **A** (sequential on one L4) unless time-pressured. Low cost, low complexity, low risk.

### 3.4. Review workload tooling

The MVP review app (`mvp/review/`) handles 960 generations × ~1 min each = 16h of manual work. Phase 5 would scale to:
- 8 virtues × 4 evals (or 8×8 if we expand evals) × 24 prompts × 2 conditions × 2 models = up to 6,144 generations
- At 1 min each: 102 hours of manual review = 2.5 weeks

Required before Phase 5:
- **LLM-judge pre-filter** — review app flags only items where LLM-judge and regex-scorer disagree, for manual arbitration
- **Batched review workflows** — handle groups of similar items together
- **Agreement tracking** — run auto-vs-human correlation per cell and flag cells with low correlation for deeper review

---

## 4. Phase 5 stages — specific commands and timeline

Assumes Phase 5 is activated AND §3 prerequisites are in place.

| Stage | Duration | Deliverable |
|---|---|---|
| 5.0 — Corpus generation for 4 new virtues | 1-2 weeks | 160 triplets (40 per virtue), calibration-passing |
| 5.1 — Extraction of 4 new vectors × 2 models | ~80h GPU | 8 new vector sets |
| 5.2 — Geometric MVE on 8-virtue matrix (28 pairs) | 2h CPU | 28-pair orthogonality table per model |
| 5.3 — α-sweep for 8 new vectors | ~32h GPU | best (α, layer) per vector |
| 5.4 — 8×8 specificity matrix | ~96h GPU | 64-cell CSV per model |
| 5.5 — Hand review (with LLM-judge pre-filter) | 40-60h human | annotated CSVs |
| 5.6 — Analysis + report | 3-5 days | 8×8 heatmap, per-cell deltas, verdict |

**Realistic end-to-end:** 5-8 weeks of wall-clock time from activation to analysis.

---

## 5. Decision tree for Phase 5 outcome

Analogous to MVP post-decisions (see `post-mvp-decisions.md`) but at 8×8 scale:

- **All-clean at 8×8** → full publishable taxonomy of 8 atomic virtue directions. Decide: 15-virtue full taxonomy attempt, or publish at 8?
- **Partial — some Phase-5 virtues collapse with Phase-4 ones** → interesting taxonomic finding. E.g., if Hypothesis Generation collapses with Evidence Grounding, that's evidence for a "scientific-reasoning super-direction."
- **New AOT-cluster collapse emerges** → F39 confirmed empirically at 8-virtue scale. Write up as collapse finding.
- **Collapse at 8×8 even when 4×4 was clean** → MVP was a small-N lucky win; the 4 MVP virtues happened to be spread across activation space but 4 more introduces cross-talk. Major finding about small-model representation capacity.

---

## 6. What Phase 5 explicitly does NOT include

- **Adding the 7 deferred virtues** (Genuine Curiosity, Causal Reasoning, Quantitative Groundedness, Confirmation Bias Awareness, Metacognitive Awareness, Comfort with Ambiguity, Authority Independence). Per `mvp-virtues.md`, those require specialized corpus design or have high AOT-cluster collinearity risk — held for Phase 6+.
- **Switching to larger models** (7B+). The whole project is about small-model representation capacity. Adding larger models would be a separate comparative study.
- **Cross-family validation** (Llama, Mistral, Phi). Would be valuable but doubles extraction time. Optional follow-up, not part of Phase 5.
- **Behavioral benchmarks beyond the 4 MVP ones** (AIME, abstention, EG-eval, RT-eval). Adding new behavioral benchmarks is a Phase 6 concern.

---

## 7. Honest cost-benefit snapshot

**Phase 5 cost:** ~5-8 weeks of wall-clock time. ~$200-500 GPU. ~100h of human review + engineering time.

**Phase 5 value contingent on MVP outcome:**
- If MVP is all_clean → Phase 5 lets us claim the atomic-virtue-direction taxonomy holds across a broader virtue space. Strengthens the taxonomy claim.
- If MVP is partial → Phase 5 may show the partial pattern holds or reveals new cross-talks. Medium value.
- If MVP is collapse → Phase 5 is NOT activated. See activation conditions §2.

**Phase 5 downside risk:**
- Scale-failure mode (8 virtues can't separate at 4B) teaches us about model-scale limits, which is publishable but defeats the "general virtue taxonomy" framing.
- Corpus-gen v2 may reveal we can't reliably produce calibration-passing corpora at scale (FM-6 caricature was hard to eliminate from LLM output even with heavy prompt iteration).

**My honest read:** Phase 5 is worth ~1 month of work ONLY if MVP lands clean. If MVP is partial, I'd vote for deepening the MVP 4 (more models, more benchmarks, better scorers) rather than adding 4 more virtues on shakier foundation.

---

## 8. Pre-Phase-5 checklist

Before Phase 5 formally starts:

- [ ] MVP analysis report (`results/analysis_report/report.md`) committed, verdict = all_clean or partial
- [ ] F99 and subsequent findings written up in `docs/findings.md`
- [ ] Scorer upgrade (§3.1) designed and specified
- [ ] Corpus-gen-v2 prompt refined and tested on 1 new virtue (validation run)
- [ ] GPU budget option chosen (§3.3)
- [ ] Phase 5 activation approved by research decision
- [ ] `docs/phase5-plan.md` v2 written after seeing MVP data

---

## 9. Relationship to other docs

- `docs/mvp-virtues.md` — defines the 4 MVP virtues + the 8-virtue full-study set
- `docs/findings.md` F98 — pre-registered exit criteria for MVP
- `docs/eg-rt-eval-spec.md` — benchmark spec that Phase 5 builds on
- `docs/extraction-runbook.md` — extraction pipeline Phase 5 will reuse
- `docs/post-mvp-decisions.md` — what to do after MVP lands
- `docs/scoring.md` — manual-first policy + scorer upgrade trigger

---

## Document state

- **Created:** 2026-04-24 (Day 17) while MVP extraction ~90% complete but no MVP data yet.
- **v1 discipline:** this plan is explicitly **conditional on MVP outcome**. If MVP is "collapse" per F98, this plan does NOT execute — we replan from the collapse finding.
- **Pre-registration of non-commitment:** writing this now is future-planning, not commitment. The activation gate in §2 is the commitment point.
