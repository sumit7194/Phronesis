# Reasoning Transparency — substrate-reuse contrastive triplet corpus

Concept 14 from `docs/concepts.md`. Hand-written RT triplets produced by **substrate-reuse** — reusing factual substrates from the existing 166-triplet Calibrated-Confidence corpus with fresh virtuous and non-virtuous rewrites on the RT contrast axis.

See `corpus/substrate-reuse/PLAN.md`, `mvp/results/corpus-reuse-sampling-eg-rt.md`, and `docs/mvp-virtues.md` §14.

## Calibration batch (this directory)

5 hand-written triplets written 2026-04-22, a complement to `corpus/sonnet-mvp/` and `corpus/chatgpt-mvp/` LLM-generated batches.

## Triplet index

| Directory | Domain | Sub-facet | Failure | Confound | Source substrate |
|---|---|---|---|---|---|
| `rt-sr-01-economics-rdd-class-size-extrapolation` | economics | RT-c | excess | none | `son-09-economics-rdd-class-size-achievement-01` |
| `rt-sr-02-physics-gw-chirp-mass-classification-chain` | physics | RT-c | deficiency | none | `son-09-physics-gravitational-wave-chirp-mass-01` |
| `rt-sr-03-chemistry-hplc-matrix-transfer-assumption` | chemistry | RT-b | excess | none | `hand-09-chemistry-hplc-method-matrix-transfer-01` |
| `rt-sr-04-earthsci-fault-hazard-rupture-count-weak-link` | earth-sci | RT-c | deficiency | none | `hand-09-earthsci-earthquake-fault-hazard-01` |
| `rt-sr-05-medicine-phase2-primary-durability-generalizability-steps` | medicine | RT-a | deficiency | non-virtuous-right | `hand-09-medicine-phase2-trial-primary-vs-durability-01` |

**Planned additional 5 triplets** (deferred, not yet written): `rt-sr-06` through `rt-sr-10` — see `PLAN.md` for assignments (engineering, psychology, biology, physics, and possibly more medicine).

## Golden-mean rotation (this batch of 5)

- **Excess failures:** 2 (rt-sr-01, rt-sr-03)
- **Deficiency failures:** 3 (rt-sr-02, rt-sr-04, rt-sr-05)
- Split 2/3 — satisfies §4.3 of `docs/generation-guidelines.md`.

## Correctness-confound coverage

- **Non-virtuous-right:** 1 (rt-sr-05) — deficiency-failure passage reaches the correct clinical advice (advance to Phase 3 with attention to durability) via summary-style reasoning that hides the primary-vs-durability-vs-generalizability step structure.
- **Virtuous-wrong:** 0 (deferred to rt-sr-07 per PLAN).

## Sub-facet coverage

- RT-a ×1 (rt-sr-05)
- RT-b ×1 (rt-sr-03)
- RT-c ×3 (rt-sr-01, rt-sr-02, rt-sr-04)

Note: RT-c is over-represented in this batch. Planned additional 5 (PLAN.md) will rebalance toward RT-a and RT-b.

## Domain coverage

5 distinct domains: economics, physics, chemistry, earth-sciences, medicine. No domain repeated. Engineering, psychology, biology deferred to planned additional 5.

## Non-overlap with EG substrate-reuse

RT substrates are drawn from distinct source triplets than EG substrates, except that the `medicine` domain uses `phase2-trial` for RT while EG uses `surgical-learning-curve`. Two different scenarios in the same domain are fine — the constraint is that the SAME scenario not be reused across EG and RT to avoid scenario-level contamination in specificity-matrix testing.

## Hard constraints applied

Same as for EG batch. See `../triplets-evidence-grounding/README.md` for the constraint list.

## Self-audit summary

- All 5 triplets have fact-pack + neutral + virtuous + non-virtuous committed.
- Length matching: rt-sr-03 has ~17% asymmetry (neutral ~230 words from source — short — vs non-virtuous ~265). **Exceeds ±10% target.** Flagged for curator review; may need neutral expansion or non-virtuous trim before extraction use.
- All other triplets within ±10%.
- RT contrast axis is dominant in every virtuous / non-virtuous pair. Spot-check: rt-sr-01 non-virtuous uses "Step one… Step eight…" enumeration — the naturalistic RT-excess pattern observed in ChatGPT v1 RT batch, not a caricature.
- No real named researchers, papers, or institutions anywhere. Generic method names (RDD, Bayesian estimation, Paris law, FDA guidance) are used because they are canonical terminology, not attributable citations.

## Provenance and cross-contamination

Same caveat as EG substrate-reuse: same scenarios appear in both CC corpus and this RT corpus. Do not pool CC and RT corpora in extraction; extract v_CC and v_RT from separate sources.
