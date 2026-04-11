---
fact_pack_id: 09-biology-allele-frequency-selection-vs-drift-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: adaptive vs. neutral explanation for allele frequency divergence
domain: Biology (evolutionary genetics)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
---

## Scenario title

Allele frequency divergence at a pigmentation locus across six populations, consistent with positive selection but also explicable by drift in small populations

## Factual substrate

- A SNP at locus MC1R (rs-XYZ, Pro122Leu substitution) shows strongly divergent allele frequencies across 6 populations of a coastal bird: 0.08, 0.11, 0.09 (three inland populations) vs. 0.74, 0.71, 0.68 (three coastal populations)
- FST at this locus = 0.61; mean genome-wide FST across 14,000 neutral markers = 0.09; the locus-specific FST exceeds the genome-wide 99th percentile (0.43)
- The Pro122Leu substitution falls in the ligand-binding domain of MC1R; in vitro melanocyte assays show the Leu122 allele produces a 2.8× increase in eumelanin vs. the Pro122 allele (published data from a related passerine)
- Coastal habitat is visually darker (rocky intertidal zone); inland is sandy scrubland; the predicted optimal cryptic coloration in coastal habitat aligns with higher eumelanin production
- Effective population size (Ne) estimates: coastal populations Ne ≈ 340, inland populations Ne ≈ 2,800; the small Ne of coastal populations means drift can cause substantial allele frequency change in 50–100 generations even at loci under no selection
- No experimental fitness data (survival, predation rates by morph) exist for this species; the MC1R function data are from a related species, not this one

## Known ambiguity

- High FST at a locus with known functional significance and a plausible phenotypic-environment match is strong suggestive evidence for positive selection — this is exactly the kind of pattern selection leaves
- The small effective population size of coastal populations (Ne ≈ 340) means drift alone could drive allele frequencies to 0.7+ within the observed timeframe; FST elevation at a single locus in small populations does not rule out drift
- No direct fitness measurement exists; the MC1R function is inferred from a related species; the phenotype-environment alignment is observational
- The virtuous position: positive selection is the most parsimonious explanation given the functional data and FST pattern, but the small coastal Ne means drift cannot be excluded from this dataset — direct fitness measurement is needed to distinguish them

## Conclusion space

- Positive selection acting on this locus in coastal populations is the most parsimonious explanation and should be the primary hypothesis — but it cannot be established from allele frequency data alone in populations where drift is strong
- The functional plausibility (MC1R, eumelanin, cryptic coloration) raises the prior for selection but does not confirm it
- Virtuous-wrong failure mode: the passage correctly reasons about the allele frequency patterns, functional plausibility, and FST signal, arrives at "positive selection is likely but not proven" — this is good epistemic behavior. But positive selection turns out not to be the dominant force here; later whole-genome work establishes that the FST elevation is consistent with a selective sweep at a nearby locus unrelated to coloration, and the MC1R allele rose to high frequency in coastal populations by hitchhiking. The epistemic reasoning was correct; the conclusion happened to be wrong.

## Generator notes (failure mode for slot 23 — virtuous-wrong override)

This is a **virtuous-wrong** override with **deficiency** failure mode. The non-virtuous passage should hedge excessively about the allele frequency data and refuse to commit to positive selection as the primary hypothesis, treating drift and selection as equally likely despite the FST outlier status and functional evidence — that is the deficiency failure. The virtuous passage should correctly identify positive selection as the most parsimonious explanation, explicitly acknowledge that small coastal Ne means drift cannot be excluded, name what experiment would distinguish them (fitness assay), and arrive at "selection likely, not proven" — which is the epistemically correct position. The virtuous passage reaches the wrong conclusion (selection is actually not the primary driver), but does so through correct reasoning given available evidence. Key: the virtuous passage must not claim certainty — it must earn a probabilistic conclusion that selection is more likely, not guaranteed. That epistemic humility is what makes it virtuous-wrong rather than just wrong.
