# Phase 4a Pilot Corpus Queue — Calibrated Confidence (Concept 9)

This is the authoritative 10-slot queue for Phase 4a pilot corpus generation. All assignments (domain, failure mode, correctness-confound override) are fixed at queue-construction time — the generator must honor them, not decide at generation time.

**Created:** Phase 4a cycle 6 (2026-04-10), Stage 2 output.
**Authority:** this file, derived from `docs/phase4a-plan.md` §3 Stage 2 as resolved in cycle 3.

---

## Queue

| Slot | Domain | Failure mode | Confound override | Fact pack ID (assigned at curation) | Status |
|---|---|---|---|---|---|
| 1 | Medicine / clinical epidemiology | excess | standard | 09-medicine-phase2-trial-primary-vs-durability-01 | ✅ ACCEPTED |
| 2 | Chemistry (analytical) | deficiency | virtuous-wrong | 09-chemistry-unexpected-ms-peak-solvent-batch-01 | ✅ ACCEPTED |
| 3 | Biology (cellular/organismal/ecological) | excess | standard | 09-biology-songbird-decline-multi-cause-01 | ✅ ACCEPTED |
| 4 | Economics (behavioral / microeconomic) | deficiency | standard | 09-economics-call-center-bonus-field-experiment-01 | ✅ ACCEPTED |
| 5 | Physics (experimental) | excess | standard | 09-physics-thermal-conductivity-extrapolation-01 | ✅ ACCEPTED |
| 6 | Earth sciences (geology / climate / oceanography) | deficiency | standard | 09-earthsci-ocean-acidification-shell-thickness-01 | ✅ ACCEPTED |
| 7 | Psychology (experimental) | excess | standard | 09-psychology-ego-depletion-replication-01 | ✅ ACCEPTED |
| 8 | Medicine / clinical epidemiology | deficiency | standard | 09-medicine-rehab-meta-analysis-severity-subgroup-01 | TRIPLET_GENERATED |
| 9 | Engineering (mechanical / electrical / structural) | excess | non-virtuous-right | 09-engineering-steel-beam-load-corrosion-01 | TRIPLET_GENERATED |
| 10 | Psychology (experimental) | deficiency | standard | 09-psychology-wm-training-far-transfer-01 | TRIPLET_GENERATED |

---

## Balance verification

- **Failure mode split:** excess = slots {1, 3, 5, 7, 9} = 5. deficiency = slots {2, 4, 6, 8, 10} = 5. **5/5 ✓**
- **Failure mode interleaving:** e-d-e-d-e-d-e-d-e-d (perfect alternation, no same-direction runs) ✓
- **Doubled domains:** Medicine (slots 1 excess + 8 deficiency) and Psychology (slots 7 excess + 10 deficiency). Both doubled domains have within-domain symmetry — one excess and one deficiency each ✓
- **Single-domain slots:** Chemistry (2), Biology (3), Economics (4), Physics (5), Earth sciences (6), Engineering (9). Six domains, exactly matching the 6 remaining slots after the two doubled domains take 4 slots ✓
- **All 8 domains represented:** Medicine, Psychology, Chemistry, Biology, Economics, Physics, Earth sciences, Engineering ✓
- **Max per domain:** 2 (Medicine and Psychology) = 20% of corpus. Under the 25% cap from `generation-guidelines.md` §3.2 ✓
- **Correctness-confound overrides:** 2 total = 20% (within the 20–30% §4.4 target).
  - Slot 2 (Chemistry, deficiency): **virtuous-wrong** — the virtuous rewrite should reach a factually incorrect conclusion despite reasoning well.
  - Slot 9 (Engineering, excess): **non-virtuous-right** — the non-virtuous rewrite should stumble onto a correct conclusion despite reasoning poorly (overconfidence that happens to land on the right answer).
  - Both override *directions* represented (virtuous-wrong + non-virtuous-right) ✓
  - Overrides applied on *both* failure-mode sides (one on a deficiency slot, one on an excess slot) ✓

---

## Curation order

Fact packs are curated in slot order (1 → 10) across Stage 3 cycles. Each curation cycle fills exactly one slot. The generator updates this table with the `fact pack ID` and flips `status` to CURATED as each pack is written, SANITIZED when the §2.4 checklist passes, and TRIPLET_GENERATED when the Stage 4 generation cycle produces the triplet for that slot.

## Override details (generator must honor at triplet generation time)

**Slot 2 — virtuous-wrong override (Chemistry, deficiency):**

- The neutral baseline reaches a conclusion from the scenario's substrate that, in the scenario's ground truth, is factually correct.
- The virtuous rewrite walks through the reasoning carefully, engages with the ambiguity, hedges appropriately on weak-evidence claims — and still lands on a conclusion that happens to be *factually incorrect* given the scenario's ground truth. The reasoning is virtuous; the landing point is wrong through no fault of the reasoning.
- The non-virtuous (deficiency) rewrite uses uniform hedging, refuses to commit, and produces a "we can't really tell" non-conclusion.
- The fact pack must construct the scenario so that one plausible-but-wrong conclusion exists that a careful reasoner could land on through no failure of reasoning. This is the "virtuous but wrong" trap — it exists in real scientific practice and is what F30/F66 decorrelation strategy is meant to capture.

**Slot 9 — non-virtuous-right override (Engineering, excess):**

- The neutral baseline reaches a correct conclusion from the substrate.
- The virtuous rewrite engages with the evidence, differentiates confidence markers, and reaches the correct conclusion through careful reasoning.
- The non-virtuous (excess) rewrite uses flat high-confidence language, dismisses the substrate's ambiguity, and reaches the same correct conclusion — but through arrogance rather than through reasoning. The "lucky-right" failure: bad reasoning happens to land on the right answer.
- The fact pack must construct the scenario so that the correct conclusion is also the "obvious first guess" that an overconfident reasoner would jump to without engaging with the evidence. This is the complementary trap to slot 2.

## Notes for subsequent cycles

- **Cycle 7 onward (Stage 3):** curate one fact pack per cycle in slot order. Read this file at the start of each cycle to determine which slot is next and what its domain / failure mode / override assignment is.
- **Cycle 17 onward (Stage 4 generation):** read this file and the corresponding fact pack together. Apply the override instructions above verbatim for slots 2 and 9; use the §4.6 generation prompts normally for the other slots.
- **This file is updated by Stage 3 and Stage 4 cycles** to track progress. Do not rewrite the balance verification section — it is frozen at Stage 2 output and is the audit trail.
