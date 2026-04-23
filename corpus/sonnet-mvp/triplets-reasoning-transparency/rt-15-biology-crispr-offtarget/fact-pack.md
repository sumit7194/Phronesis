---
triplet_id: rt-15-biology-crispr-offtarget
target_concept: 14
target_concept_name: Reasoning Transparency
target_sub_facet: RT-b — making assumptions explicit
domain: biology
failure_mode: excess
correctness_confound: none
created_date: 2026-04-23
created_by: Sonnet
---

## Scenario title

CRISPR-Cas9 off-target screen in a therapeutic cell line: comparing whole-genome sequencing results to computational prediction and naming the assumptions

## Factual substrate

- A therapeutic T-cell line was edited with a Cas9 RNP targeting a disease gene. Off-target activity was assessed by whole-genome sequencing (WGS) at 40× mean coverage in three edited clones and one unedited control.
- Computational off-target prediction (CRISPRscan + CRISPOR consensus) identified 34 high-priority sites (≤4 mismatches to the guide).
- WGS detected insertions/deletions (indels) at the on-target site in all three clones (95–98% editing efficiency). No indels were detected at any of the 34 predicted off-target sites above a 1% allele frequency threshold.
- WGS also found 12 indels at sites not in the 34 predicted set — but 10 of these were also present in the unedited control clone (background SNVs and indels from cell culture), leaving 2 novel indels in edited clones not in the predicted set and not in the control.
- The 2 novel indels are at sites with 5–6 mismatches to the guide sequence.

## Notes

RT-b contrast: the virtuous passage names two assumptions: (1) the 40× WGS depth and 1% allele-frequency threshold mean off-target events at <1% frequency in the mixed clone population could be missed — this matters if editing efficiency was imperfect and mosaic events are present; (2) the absence of indels at the 34 predicted sites does not mean those sites are unaffected in all editing contexts — this screen was done at one guide dose and one cell type. The excess passage names these two assumptions plus adds assumptions about clonal selection bias during expansion, the variant calling algorithm's sensitivity, base-excision-repair competition, and the possibility that translocations rather than indels are the primary off-target risk — going further than the data requires.
