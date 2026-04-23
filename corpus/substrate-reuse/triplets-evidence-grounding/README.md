# Evidence Grounding — substrate-reuse contrastive triplet corpus

Concept 15 from `docs/concepts.md`. This directory contains hand-written EG triplets produced by **substrate-reuse** — reusing factual substrates and (lightly edited) neutral baselines from the existing 166-triplet Calibrated-Confidence corpus (`corpus/triplets-combined/`), with fresh virtuous and non-virtuous rewrites on the EG contrast axis.

See `corpus/substrate-reuse/PLAN.md` for the substrate-assignment plan, `mvp/results/corpus-reuse-sampling-eg-rt.md` for how substrates were ranked, and `docs/mvp-virtues.md` §15 for the EG operational guideline.

## Calibration batch (this directory)

5 hand-written triplets written 2026-04-22 as a complement to `corpus/sonnet-mvp/` and `corpus/chatgpt-mvp/` LLM-generated batches. The aim is a diverse MVP corpus with at least three sources (human substrate-reuse + two LLM families) to hedge against any single-source systematic bias.

## Triplet index

| Directory | Domain | Sub-facet | Failure | Confound | Source substrate |
|---|---|---|---|---|---|
| `eg-sr-01-psychology-cbi-analgesic-cross-study` | psychology | EG-c | deficiency | non-virtuous-right | `son-09-psychology-placebo-analgesic-trial-01` |
| `eg-sr-02-biology-songbird-multi-cause-attribution` | biology | EG-a | deficiency | none | `son-09-biology-songbird-decline-multi-cause-01` |
| `eg-sr-03-physics-hubble-tension-evidence-classes` | physics | EG-c | excess | none | `hand-09-physics-hubble-tension-cepheid-calibration-01` |
| `eg-sr-04-engineering-fea-bridge-four-evidence-types` | engineering | EG-c | excess | none | `hand-09-engineering-fea-bridge-girder-validation-01` |
| `eg-sr-05-earthsci-ocean-acidification-observation-vs-mechanism` | earth-sci | EG-a | deficiency | none | `son-09-earthsci-ocean-acidification-shell-thickness-01` |

**Planned additional 5 triplets** (deferred, not yet written): `eg-sr-06` through `eg-sr-10` — see `PLAN.md` for assignments (medicine, chemistry, economics, engineering, biology).

## Golden-mean rotation (this batch of 5)

- **Excess failures:** 2 (eg-sr-03, eg-sr-04)
- **Deficiency failures:** 3 (eg-sr-01, eg-sr-02, eg-sr-05)
- Split 2/3 — satisfies §4.3 of `docs/generation-guidelines.md` (no one-sided concentration).

## Correctness-confound coverage

- **Non-virtuous-right:** 1 (eg-sr-01) — the deficiency-failure passage reaches the correct policy conclusion (CBI is a viable analgesic option) via under-grounded cross-study effect-size comparison.
- **Virtuous-wrong:** 0 (deferred to eg-sr-06 per PLAN).

## Sub-facet coverage

- EG-a ×2 (eg-sr-02, eg-sr-05)
- EG-b ×0 (deferred to eg-sr-06, eg-sr-07)
- EG-c ×3 (eg-sr-01, eg-sr-03, eg-sr-04)

## Domain coverage

5 distinct domains: psychology, biology, physics, engineering, earth-sciences. Medicine, chemistry, economics are deferred to the planned additional 5.

## Hard constraints applied

- Length 250-350 tokens, ±10% across the triad (target; small exceedances in 1-2 triplets flagged in self-audit below)
- Minimal edit: substrate and all numeric values preserved across neutral / virtuous / non-virtuous
- No safety-refusal register
- No meta-commentary or markdown headers in passages
- No real named researchers, institutions, papers, or specific citations
- Fact-pack provenance: every fact-pack declares `source_substrate` pointing to the CC-corpus triplet reused
- Anti-caricature for excess failures: "evidence" word-family ≤6 per non-virtuous passage (the ChatGPT v1 caricature pattern was explicitly avoided)

## Self-audit summary

- All 5 triplets have fact-pack + neutral + virtuous + non-virtuous committed.
- Length asymmetry: eg-sr-05 has a ~9.4% asymmetry (virtuous ~290 words vs neutral ~265). Within ±10% limit, borderline. All others within 5-8% range.
- EG contrast axis (not CC) is dominant in every virtuous / non-virtuous pair. Spot-check: eg-sr-03 virtuous — "evidence class" appears as a structural category, not as a keyword-stuffed decoration; "evidence" word count: ~9 times across 285-word passage (well below the 15-25+ caricature threshold seen in ChatGPT v1).
- No real named researchers, papers, or institutions anywhere. Only the canonical project-name acronyms (SH0ES, CCHP, H0liCOW, Planck, AASHTO, FDA) which are established standards/missions, not specific attributable authors.

## Provenance and cross-contamination

Each triplet's `fact-pack.md` includes a `source_substrate` field pointing to the CC-corpus triplet it was built on. **Extraction caveat:** because the same scenario appears in both the CC corpus and this EG corpus (with different virtuous/non-virtuous rewrites), extraction runs that pool CC and EG corpora into a single training set would conflate the two axes. For MVP, extract v_CC from `triplets-combined/` and v_EG from this substrate-reuse set (and `sonnet-mvp/` and `chatgpt-mvp/`) with no corpus pooling.
