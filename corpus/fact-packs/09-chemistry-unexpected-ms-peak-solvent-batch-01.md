---
fact_pack_id: 09-chemistry-unexpected-ms-peak-solvent-batch-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: Matching certainty of language to strength of evidence
domain: chemistry
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-10
queue_slot: 2
queue_failure_mode: deficiency
queue_confound_override: virtuous-wrong
---

## Scenario title

An unexpected mass spectrometry peak in a small-molecule stability study with converging-but-misleading evidence

## Factual substrate

- An analytical chemist is running LC-MS stability analysis on a small-molecule active pharmaceutical ingredient. The method has been in routine use for over a year and previously showed only the parent compound peak and two known minor degradation products.
- Over the past five weeks, a new peak has appeared at m/z 312, approximately 16 mass units below the parent compound (m/z 328). The peak is reproducible across three independent sample preparations and is present in both freshly prepared samples and samples stored at accelerated conditions (40°C / 75% RH).
- Three lines of evidence are consistent with a loss-of-methyl degradation product at this mass: (1) the 16-mass-unit offset matches a CH₄ loss within instrument precision, (2) the retention time is 0.8 minutes earlier than the parent, consistent with a more polar degradation product, and (3) the peak area grows roughly linearly with sample age over a two-week storage window at the accelerated conditions.
- One relevant operational fact: the chemistry lab switched to a new lot of acetonitrile mobile phase approximately four weeks ago, from a different vendor than the previous lot. The change was made because the original vendor had a supply disruption.
- The peak is not present in a method blank run with water only, but the chemist has not yet run a method blank using the new acetonitrile batch alone.

## Known ambiguity

- The convergence of three lines of evidence (mass offset, retention time, growth with storage) suggests a degradation product, but the solvent batch change introduces an alternative explanation that has not been tested: the peak could be a trace contaminant from the new acetonitrile lot, which would also grow in apparent intensity over time if the contaminant accumulates on the LC column between injections.
- The "grows with storage at accelerated conditions" observation is the strongest evidence for degradation, but the chemist has not run an explicit control experiment (e.g., fresh sample in new solvent batch vs fresh sample in old solvent batch) to rule out a solvent-related artifact.

## Conclusion space

- **Conclusion A (virtuous-compatible — but factually WRONG per the virtuous-wrong override):** "The three lines of converging evidence — the 16-mass-unit offset matching a CH₄ loss, the retention-time shift consistent with a more polar product, and the linear growth with sample age — strongly suggest this is a degradation product. The solvent batch change is a potential confound that should be ruled out with a method-blank run, but the weight of evidence here points toward degradation. My working view is that this is a new minor degradation product of the parent compound via methyl loss, and further structural confirmation by MS/MS or NMR would be the next step. This interpretation is not certain — the solvent control is still outstanding — but it is what the current evidence supports." The reasoner uses strong confidence for the peak's existence and mass (directly measured), moderate confidence for the degradation interpretation (multiple consistent lines), and explicit hedging on the solvent-confound question. They land on "probably degradation" because the evidence genuinely leans that way in the substrate. **Ground truth for the virtuous-wrong override: the peak is actually a trace contaminant from the new acetonitrile batch.** The virtuous reasoner's conclusion is wrong, but they couldn't have reached the right answer without additional information (running the new-solvent blank, or the vendor disclosure that came later). The reasoning is virtuous; the landing is unluckily wrong.

- **Conclusion B (deficiency-failure-compatible — the assigned failure mode for this slot):** "It's hard to say what this peak is. It could be a degradation product, or it could be related to the solvent change, or it could be something else entirely. The mass offset is suggestive but not definitive, the retention-time shift is consistent with many possibilities, and the growth with storage could have multiple explanations. Without more data, I don't think I can commit to any particular interpretation. We probably need a lot more analysis before we can say anything concrete about what this peak is." The reasoner uses flat weak-hedging language across every claim — including the claims the substrate does support strongly (the peak exists, the mass offset is real, the growth pattern is real). Everything is wrapped in "could be," "suggestive but not definitive," "we can't really say." This is the deficiency failure: uniform hedging even where the evidence warrants concrete claims, producing a passage that communicates no working view at all.

- **Conclusion C (excess-failure-compatible):** "The peak is obviously a new methyl-loss degradation product. The mass matches, the retention time matches, it grows with storage — three lines of evidence all pointing to degradation. The solvent batch change is irrelevant because the peak appears in stored samples, not just freshly injected ones. We can conclude this is a degradation product and report it as such." (Not the assigned failure mode for this slot, but included for the conclusion space completeness.)

## Notes for generator

**This is a virtuous-wrong override slot** (queue slot 2, per `corpus/queue.md`). The virtuous rewrite must reason carefully and land on Conclusion A (the degradation interpretation), which is **factually wrong** given the scenario's ground truth (the peak is actually a solvent contaminant). The reasoning is virtuous because it correctly weighs the evidence that is available in the substrate. The landing is wrong because the decisive evidence (solvent blank running, vendor confirmation) is not in the substrate. This is the "virtuous but unlucky" trap that F30/F66 correctness-confound mitigation is designed to decorrelate — it exists in real analytical chemistry practice and is the point of the override.

The **non-virtuous deficiency** rewrite must depict the deficiency failure mode: uniform weak hedging across all claims, including the strongly-supported ones (peak existence, mass, retention time, growth pattern). The deficiency reasoner refuses to commit to any interpretation even though the substrate clearly supports the degradation interpretation as the best reading of the available evidence. They say "it's hard to say," "we can't really conclude anything," "more data is needed" — where a calibrated reasoner would say "the evidence points toward degradation, with the solvent batch as an outstanding confound to rule out." The deficiency reasoner's conclusion is also "wrong" in the sense of failing to do the work, but they don't land on a specific wrong answer — they fail to land at all.

**Key invariants the generator must preserve across all three passages:** the m/z 312 vs 328 mass offset, the 0.8-minute retention time shift, the linear growth with sample age at 40°C/75%RH, the acetonitrile vendor switch four weeks ago, the water-blank having no peak, and the absence of a new-solvent-only blank test. These are the substrate facts that carry the reasoning — if the generator drops or paraphrases away any of them, the calibrated-confidence differentiation loses its anchor points.

**For the virtuous rewrite specifically:** the reasoner should use **strong** confidence markers for the peak's existence and its m/z 312 assignment (directly measured facts), **moderate** confidence markers for the degradation interpretation (multiple consistent lines of evidence but no confirmatory experiment), and **weak/tentative** markers for whether the solvent confound has been ruled out (explicitly named as outstanding). The virtuous passage lands on "probably a degradation product, with the solvent confound still to be ruled out" — a working view held at the right confidence level even though it happens to be factually wrong.

**For the deficiency rewrite specifically:** the reasoner hedges uniformly on EVERYTHING — peak existence, mass assignment, retention time significance, growth pattern, all of it. They do not differentiate strong-evidence claims (like "the peak is reproducible across three preparations") from weak-evidence claims (like "this might or might not be a degradation product"). That failure to differentiate is the deficiency signature.

**Scenario ground truth (for reviewer reference, NOT to appear in any passage):** The peak is ultimately determined to be a trace CH₃CN-related impurity from the new acetonitrile lot. The vendor disclosed a manufacturing issue in that batch three weeks later. The degradation interpretation was reasonable given the evidence but wrong.
