# Substrate-reuse corpus — plan

**Created:** 2026-04-22 (Day 15, early)
**Purpose:** Write ~20 hand-crafted triplets (10 EG + 10 RT) by reusing substrates from the existing 166-triplet CC corpus + 20-triplet IH corpus. Each triplet keeps the factual substrate and (lightly-edited) neutral baseline from the source, but replaces the virtuous and non-virtuous rewrites with EG-contrast or RT-contrast passages per `docs/mvp-virtues.md`.

**Companion to:** `corpus/sonnet-mvp/` and `corpus/chatgpt-mvp/` LLM-generated batches. Goal is a mixed corpus with ~40 per virtue for MVP extraction, curated down from a ~100-triplet candidate pool:
- Sonnet: 20 EG + 20 RT
- ChatGPT: 20 EG + 20 RT
- This substrate-reuse: 10 EG + 10 RT

**Source reference:** `mvp/results/corpus-reuse-sampling-eg-rt.md`

---

## Substrate assignments

### EG substrate-reuse (10 triplets)

| ID | Source substrate | Domain | Sub-facet | Failure | Confound |
|---|---|---|---|---|---|
| eg-sr-01 | `triplets-combined/son-09-psychology-placebo-analgesic-trial-01` | psychology | EG-c | deficiency | non-virtuous-right |
| eg-sr-02 | `triplets-combined/son-09-biology-songbird-decline-multi-cause-01` | biology | EG-a | deficiency | none |
| eg-sr-03 | `triplets-combined/hand-09-physics-hubble-tension-cepheid-calibration-01` | physics | EG-c | excess | none |
| eg-sr-04 | `triplets-combined/hand-09-engineering-fea-bridge-girder-validation-01` | engineering | EG-c | excess | none |
| eg-sr-05 | `triplets-combined/son-09-earthsci-ocean-acidification-shell-thickness-01` | earth-sci | EG-a | deficiency | none |
| eg-sr-06 | `triplets-combined/son-09-medicine-surgical-learning-curve-mortality-01` | medicine | EG-b | excess | virtuous-wrong |
| eg-sr-07 | `triplets-combined/son-09-chemistry-catalytic-turnover-stability-01` | chemistry | EG-b | deficiency | none |
| eg-sr-08 | `triplets-combined/hand-09-economics-central-bank-forward-guidance-01` | economics | EG-b | excess | none |
| eg-sr-09 | `triplets-combined/son-09-engineering-battery-thermal-runaway-propagation-01` | engineering | EG-c | excess | none |
| eg-sr-10 | `triplets-combined/gpt-09-biology-microbiome-transplant-causation-01` | biology | EG-a | deficiency | non-virtuous-right |

**Split check:** 5 excess + 5 deficiency ✓ (golden-mean rotation). 2 non-virtuous-right + 1 virtuous-wrong = 3 correctness-confound (30%) ✓. Sub-facet coverage: EG-a ×3, EG-b ×3, EG-c ×4 — tolerable.

### RT substrate-reuse (10 triplets)

| ID | Source substrate | Domain | Sub-facet | Failure | Confound |
|---|---|---|---|---|---|
| rt-sr-01 | `triplets-combined/son-09-economics-rdd-class-size-achievement-01` | economics | RT-c | excess | none |
| rt-sr-02 | `triplets-combined/son-09-physics-gravitational-wave-chirp-mass-01` | physics | RT-c | deficiency | none |
| rt-sr-03 | `triplets-combined/hand-09-chemistry-hplc-method-matrix-transfer-01` | chemistry | RT-b | excess | none |
| rt-sr-04 | `triplets-combined/hand-09-earthsci-earthquake-fault-hazard-01` | earth-sci | RT-c | deficiency | none |
| rt-sr-05 | `triplets-combined/hand-09-medicine-phase2-trial-primary-vs-durability-01` | medicine | RT-a | deficiency | non-virtuous-right |
| rt-sr-06 | `triplets-intellectual-humility/pilot-underspecified-02-capacitor-discharge-time` | physics | RT-b | excess | none |
| rt-sr-07 | `triplets-combined/son-09-engineering-concrete-chloride-service-life-01` | engineering | RT-c | deficiency | virtuous-wrong |
| rt-sr-08 | `triplets-combined/son-09-psychology-neuroimaging-task-brain-region-01` | psychology | RT-b | excess | none |
| rt-sr-09 | `triplets-combined/son-09-biology-crispr-knockout-phenotype-redundancy-01` | biology | RT-a | deficiency | none |
| rt-sr-10 | `triplets-combined/son-09-medicine-observational-statin-dementia-01` | medicine | RT-c | excess | none |

**Split check:** 5 excess + 5 deficiency ✓. 1 non-virtuous-right + 1 virtuous-wrong = 2 confound (20%) ✓. Sub-facet coverage: RT-a ×2, RT-b ×3, RT-c ×5 — RT-a light; may swap one if needed.

**Non-overlap with EG:** RT substrates are disjoint from EG substrates (except medicine, which uses different specific scenarios: surgical-learning for EG vs. phase-2-trial for RT; two distinct medicine scenarios for RT). This preserves scenario-level independence for specificity-matrix testing.

---

## This session's scope

Full 20 triplets is ~5-7 hours of focused writing. For this session, write the **top 5 of each virtue** — the highest-priority substrates from the sampling file:

**Session 1 (this one):** eg-sr-01 through eg-sr-05 + rt-sr-01 through rt-sr-05 = 10 triplets
**Session 2 (deferred):** eg-sr-06 through eg-sr-10 + rt-sr-06 through rt-sr-10 = 10 triplets

Session 2 may happen in parallel with auditing LLM batch 2 output.

---

## Output format

Each triplet is a directory with 4 files:

```
corpus/substrate-reuse/triplets-evidence-grounding/eg-sr-XX-<domain>-<slug>/
├── fact-pack.md      # with provenance note pointing to source substrate
├── neutral.md        # copied from source triplet, possibly lightly edited
├── virtuous.md       # fresh EG rewrite (dominant axis: evidence labeling)
└── non-virtuous.md   # fresh EG failure rewrite (excess or deficiency)
```

Analogous layout for RT under `triplets-reasoning-transparency/`.

## Constraints (from `docs/mvp-virtues.md` and `generation-guidelines.md`)

- Length 250-350 tokens per passage, ±10% across the triad
- No real named researchers/institutions/papers
- No safety-refusal register
- No meta-commentary or markdown headers in passages
- Minimal-edit principle: substrate and numeric values preserved across all three
- Virtuous dominant axis = EG or RT (not CC)
- Non-virtuous dominant axis = excess or deficiency of the declared virtue, per fact-pack
- Virtuous-wrong confound = virtuous commits to a specific wrong claim (not merely cautious)
- Sub-facet label uses canonical code (EG-a/b/c or RT-a/b/c)

## Provenance and audit trail

Each `fact-pack.md` must include a `source_substrate` field pointing to the triplet directory the substrate is reused from. This makes the provenance visible for:
- Later auditors asking "where did this scenario come from?"
- Avoiding cross-contamination during extraction runs (same scenario appearing in both CC-corpus and EG-corpus would bias the extracted vectors)
- Cost accounting (substrate-reuse triplets count as 40% effort, fresh triplets as 100%)
