# Reasoning Transparency — contrastive triplet corpus (sonnet-mvp batch)

Concept 14 from `docs/concepts.md`. Target extraction: a steering vector that amplifies the disposition to show inferential steps, make assumptions explicit, and flag where the reasoning chain is weakest — distinct from the Evidence Grounding vector (Concept 15) which targets claim-to-evidence tethering, and from the Calibrated Confidence vector (Concept 9) which targets confidence-language calibration.

Grounded in philosophical accounts of inferential transparency (Adler, 2002) and the argumentation burden of disclosure. See `docs/mvp-virtues.md` §14 and `docs/concepts.md` §14 for full definition and sub-facets.

## Calibration batch (this directory)

This is the 5-triplet calibration batch (sonnet-mvp, 2026-04-22). It will be human-reviewed before the remaining 15 triplets are generated. Do not use this batch in extraction runs until it has passed the `generation-guidelines.md` §4.8 verification protocol.

## Structure

Each triplet is a directory containing `fact-pack.md`, `neutral.md`, `virtuous.md`, and `non-virtuous.md`.

- `fact-pack.md` — factual substrate, known ambiguity, conclusion space, declared failure mode and correctness-confound status, per the `generation-guidelines.md` §2.3 template.
- `neutral.md` — calm, workmanlike reasoning; the common ancestor for both rewrites.
- `virtuous.md` — minimal edit of neutral that clearly exhibits Reasoning Transparency without caricature.
- `non-virtuous.md` — minimal edit of neutral that depicts the declared failure mode (excess or deficiency).

## Triplet index

| Directory | Domain | Sub-facet | Failure mode | Correctness confound |
|---|---|---|---|---|
| `rt-01-biology-enzyme-kinetics-inhibition` | biology | RT-a (showing steps) | deficiency | none |
| `rt-02-chemistry-crystal-polymorph-stability` | chemistry | RT-b (making assumptions explicit) | excess | none |
| `rt-03-engineering-fatigue-crack-growth` | engineering | RT-c (flagging weakest link) | deficiency | none |
| `rt-04-medicine-antibiotic-sepsis-mortality` | medicine | RT-a (showing steps) | excess | virtuous-wrong |
| `rt-05-psychology-attention-bias-threat` | psychology | RT-c (flagging weakest link) | deficiency | non-virtuous-right |

## Golden-mean rotation summary

- **Excess failures:** 2 triplets (rt-02, rt-04)
- **Deficiency failures:** 3 triplets (rt-01, rt-03, rt-05)

Split is 2/3 (≈ 40/60), satisfying the `generation-guidelines.md` §4.3 rotation requirement.

## Correctness-confound coverage

- **virtuous-wrong:** rt-04 — the virtuous reasoner correctly shows the steps and identifies the before-after design's causal limitations but ends up being overly cautious, since a subsequent RCT showed the directional mortality signal was real.
- **non-virtuous-right:** rt-05 — the deficiency reasoner reaches the correct policy conclusion (don't recommend this ABM protocol) without naming the 72% baseline-bias composition as the weakest link in the chain.

## Domain coverage

Five distinct domains represented: biology, chemistry, engineering, medicine, psychology. No domain appears more than once. Satisfies the ≥4-distinct-domain, no-domain->2 constraint from the task specification.

## Sub-facet coverage

All three RT sub-facets are represented:
- RT-a (showing the steps, not just the conclusion): rt-01, rt-04
- RT-b (making assumptions explicit): rt-02
- RT-c (flagging where the reasoning chain is weakest): rt-03, rt-05

## Cross-virtue domain note (EG × RT)

Both EG and RT appear in the same domain (medicine: eg-02, rt-04) and the same domain (psychology: eg-03, rt-05). The batch still satisfies the no-domain-exceeds-2 constraint because the constraint is per-virtue, not cross-virtue. Extraction runs should verify that the EG and RT vectors are separable in the shared domains.

## Hard constraints (apply to all triplets in this corpus)

1. **Length:** 250–350 tokens per passage; all three passages in a triplet within ±10% of each other.
2. **Minimal-edit:** neutral is the common ancestor; virtuous and non-virtuous change only the RT disposition.
3. **No safety-refusal register:** No "as an AI," "I cannot," "it would be inappropriate." First-person scientific reasoning throughout.
4. **No meta-commentary:** No "Here is the passage:," no markdown headers inside passages, no bullet-point formatting.
5. **No real named researchers, institutions, papers, or specific citations.** Anonymized throughout.
6. **Sanitization:** All passages checked against `generation-guidelines.md` §2.4 checklist before delivery.

## Specificity notes (for extraction and validation)

v_RT should be tested against RT-specific behavioral evaluations (step-count in reasoning, gap-narration frequency) AND against EG-eval, CC-eval, and IH-eval benchmarks. The prediction is that v_RT increases step-visibility count without simultaneously increasing hedging-word density (CC-territory) or evidence-labeling frequency (EG-territory).

Key risk: RT and EG co-occur naturally in virtuous scientific reasoning — a passage that shows steps (RT) often also ties claims to data (EG). The extraction needs contrastive examples where one is present without the other. The fact packs in this batch were designed to foreground RT without requiring EG-specific labeling moves:
- rt-01: the key RT move is "why do simultaneous Km and Vmax changes together distinguish inhibition modes"; no EG labeling required.
- rt-03: the key RT move is "which step in the Paris-law chain is the weakest"; no evidence-type specification required.
- rt-05: the key RT move is "why is the 72% baseline problem the weakest link"; no empirical-vs-theoretical boundary required.

## Key negative markers for deficiency failure (for scale-up)

Deficiency-failure RT passages should:
- State conclusions without intermediate steps: "the compound is a mixed inhibitor" not "because both Km and Vmax change, and only mixed inhibition explains simultaneous non-proportional changes in both..."
- Treat the result as self-documenting: "the study showed no effect" without naming which inferential move produces that conclusion from the raw numbers.
- Grant confidence to the weakest link: the estimate, the design, or the measurement that is most uncertain should receive the same rhetorical weight as the robust steps.

## Key negative markers for excess failure (for scale-up)

Excess-failure RT passages should:
- Apply assumption-surfacing to steps where the assumption is background knowledge (e.g., explaining how XRPD works before citing an XRPD result).
- Spell out step-by-step reasoning for moves that the field takes for granted in working-scientist prose.
- Produce scaffolding-to-content ratio that is clearly inverted: more words explaining how to read the evidence than words interpreting it.
