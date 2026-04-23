# Calibration batch audit — EG & RT corpus, v1

**Date:** 2026-04-22 (Day 15, early)
**Batches audited:** 4 × 5 = 20 triplets
- `corpus/sonnet-mvp/triplets-evidence-grounding/` (5)
- `corpus/sonnet-mvp/triplets-reasoning-transparency/` (5)
- `corpus/chatgpt-mvp/triplets-evidence-grounding/` (5)
- `corpus/chatgpt-mvp/triplets-reasoning-transparency/` (5)

**Audit method:** Every `fact-pack.md`, `neutral.md`, `virtuous.md`, `non-virtuous.md` file read in full. Checked against the 9 hard constraints + 8 LLM failure-mode guards specified in the prompt sent to Sonnet/ChatGPT, plus the MVP-specific contrast-axis requirements from `docs/mvp-virtues.md`.

---

## Headline

**All four batches are usable for MVP extraction with targeted refinements.** Estimated keeper rate: **17/20 as-is, 3/20 requiring regeneration** (all three are ChatGPT EG excess-failure non-virtuous passages that mode-collapsed to word-"evidence"-stuffing caricature). Both generators hit the structural constraints (domain coverage, failure-mode rotation, correctness-confound rotation, no real citations, no safety-refusal register, no meta-commentary). Quality differences are stylistic, not structural.

**Recommendation:** Authorize 15 more per virtue per LLM (60 new triplets) with the prompt refinements in §4, giving an LLM-generated pool of ~80. Combined with ~20 substrate-reuse triplets from the sampling file, that puts us comfortably above the 40-per-virtue MVP target with quality headroom to curate aggressively.

---

## 1. Per-triplet verdicts

### Sonnet EG (`corpus/sonnet-mvp/triplets-evidence-grounding/`)

| ID | Domain | Sub-facet | Failure | Confound | Contrast quality | Length ±10%? | Issues | Verdict |
|---|---|---|---|---|---|---|---|---|
| eg-01 | physics | EG-b | deficiency | none | Strong — "a measurement fact, not a model output" / "an observed geometric fact" / "a theoretical prediction" | **No (~25% asymmetry)** | Virtuous ~280w, non-virtuous ~220w | ✅ Keep, trim virtuous |
| eg-02 | medicine | EG-c | excess | none | Strong — explicit RCT/ITT/subgroup labeling | Borderline (~20%) | Virtuous slightly long | ✅ Keep, mild trim |
| eg-03 | psychology | EG-a | deficiency | none | Strong — "a specific observation" / "a theoretical framework consistent with the data, not something the data establish" | Borderline (~15%) | Minor length issue | ✅ Keep |
| eg-04 | earth-sci | EG-b | excess | virtuous-wrong | Strong EG-b contrast | Acceptable | **Weak correctness-confound** — virtuous is cautious, not wrong | ⚠ Keep with note |
| eg-05 | economics | EG-c | deficiency | non-virtuous-right | Strong — "observational cross-state DiD" / "a quasi-experimental approach that identifies effects under the parallel-trends assumption but cannot prove causality the way a randomized experiment could" | Borderline (~20%) | Non-virtuous uses "studies show" canonical deficiency marker — good | ✅ Keep |

**Sonnet EG batch summary:**
- Domain coverage ✓ (5 distinct, no repeats)
- Failure split 2 excess / 3 deficiency ✓
- Correctness-confound coverage ✓ (1 virtuous-wrong, 1 non-virtuous-right)
- No real citations ✓, no safety-refusal ✓, no meta-commentary ✓
- **Recurring issue: length asymmetry** (virtuous runs 15-25% longer than non-virtuous in 4/5 triplets)

### Sonnet RT (`corpus/sonnet-mvp/triplets-reasoning-transparency/`)

| ID | Domain | Sub-facet | Failure | Confound | Contrast quality | Length ±10%? | Issues | Verdict |
|---|---|---|---|---|---|---|---|---|
| rt-01 | biology | RT-a | deficiency | none | Strong — "First, the x-intercept shifts... This second change is the discriminating move... The weakest step in this analysis is the Lineweaver-Burk transformation itself" (RT-a + RT-c combo) | Borderline (~15%) | Non-virtuous has "approximately 48 nM" — inherited from substrate | ✅ Keep |
| rt-02 | chemistry | RT-b | excess | none | Strong — assumption surfacing where load-bearing vs. excess over-surfacing | ~20% asymmetry | Virtuous ~340w, non-virtuous ~275w | ✅ Keep, trim virtuous |
| rt-03 | engineering | RT-c | deficiency | none | Strong — "The chain from that 8.3-year estimate back to the inputs has several links, and they are not equally reliable. The step with the least confidence is applying constant-amplitude Paris parameters to a variable-amplitude loading history." Clear weak-link flagging. | **No (~25% asymmetry)** | Virtuous ~310w, non-virtuous ~245w | ✅ Keep, trim virtuous |
| rt-04 | medicine | RT-a | excess | virtuous-wrong | Strong RT-a via step-sequencing; Excess via single massive run-on inference sentence | Acceptable | **Weak correctness-confound** — same issue as Sonnet eg-04: virtuous is cautious not wrong | ⚠ Keep with note |
| rt-05 | psychology | RT-c | deficiency | non-virtuous-right | Strong — "The weakest link is the participant composition, not the training protocol... Why is participant composition the weakest link rather than the dot-probe reliability concern? Because..." Explicit weak-link reasoning with comparison to alternatives. | Good (~280/260w) | Clean non-virtuous-right confound | ✅ Keep |

**Sonnet RT batch summary:**
- Domain coverage ✓
- Failure split 2 excess / 3 deficiency ✓
- Correctness-confound coverage ✓
- **Same length-asymmetry pattern** (3/5 triplets have virtuous ~20-25% longer)
- **Same virtuous-wrong pattern** — Sonnet interprets "virtuous-wrong" as "virtuous-cautious-so-not-committing" rather than "virtuous-commits-a-wrong-claim." Philosophically defensible but doesn't produce the clean contrast the prompt intended.

### ChatGPT EG (`corpus/chatgpt-mvp/triplets-evidence-grounding/`)

| ID | Domain | Sub-facet | Failure | Confound | Contrast quality | Length ±10%? | Issues | Verdict |
|---|---|---|---|---|---|---|---|---|
| eg-01 | physics | EG-c | excess | none | Virtuous clean; **Non-virtuous is CARICATURE** — "evidence" appears 15+ times (e.g., "evidence-visible track pattern", "evidence-based visualization explanation") | Good (balanced) | Word-stuffing caricature | 🔴 Regenerate non-virtuous |
| eg-02 | biology | EG-a | deficiency | non-virtuous-right | Strong — virtuous explicitly separates experimental vs. observational evidence; non-virtuous reaches correct "nitrate is bloom driver" conclusion via under-grounded assertion | Good | Clean confound | ✅ Keep |
| eg-03 | medicine | EG-b | deficiency | virtuous-wrong | Strong EG-b; **Strongest virtuous-wrong of all 20** — virtuous commits to "poor technique" conclusion which is wrong per ground truth (pollen is dominant) | Good | Excellent correctness-confound implementation | ✅ Keep |
| eg-04 | economics | EG-a | excess | none | Virtuous clean; **Non-virtuous CARICATURE** — "evidence" appears 20+ times ("evidentially speaking", "evidentiary status", "route-count evidence", "fare-media evidence", "contextual-control evidence", etc.) | Good | Word-stuffing caricature | 🔴 Regenerate non-virtuous |
| eg-05 | chemistry | EG-c | excess | none | Virtuous clean; **Non-virtuous CARICATURE** — "evidence" appears 25+ times ("yield evidence, titration evidence, chromatography evidence, and sieve-rescue evidence, is that water is the best evidence-supported explanation, while the unknown impurity remains evidence-documented but not evidence-causal") | Good | Word-stuffing caricature at its worst | 🔴 Regenerate non-virtuous |

**ChatGPT EG batch summary:**
- Domain coverage ✓
- Failure split 3 excess / 2 deficiency ✓
- Correctness-confound coverage ✓
- No real citations ✓, no safety-refusal ✓, no meta-commentary ✓
- **Length matching: excellent** — much better than Sonnet on this dimension
- **Correctness-confound implementation: excellent** (eg-03 virtuous-wrong is the strongest of all 20)
- **CRITICAL ISSUE: Systematic mode-collapse on EG excess-failure.** All 3 excess-failure non-virtuous passages use the same caricature pattern (compulsive insertion of "evidence" into every phrase). No human scientist would ever write this way. The pattern would produce a steering vector encoding "insert the word 'evidence' a lot" rather than "bureaucratic evidence-labeling." The non-virtuous passages must be regenerated before extraction use.

### ChatGPT RT (`corpus/chatgpt-mvp/triplets-reasoning-transparency/`)

| ID | Domain | Sub-facet | Failure | Confound | Contrast quality | Length ±10%? | Issues | Verdict |
|---|---|---|---|---|---|---|---|---|
| rt-01 | engineering | RT-c | deficiency | none | Strong — "The weakest part of my reasoning is separating viscosity from contamination, because both appear after the same switch." | Good | — | ✅ Keep |
| rt-02 | earth-sci | RT-b | excess | none | Strong — virtuous surfaces key assumption, non-virtuous uses procedural step-enumeration ("I begin by establishing the first element... I then proceed to the second element... I next add the third element") | Good | **Excess is NATURALISTIC**, unlike ChatGPT EG | ✅ Keep |
| rt-03 | psychology | RT-b | deficiency | non-virtuous-right | Strong — virtuous flags "weakest assumption concerns the six caffeine-protocol violations"; non-virtuous reaches correct conclusion via hiding that adjustment | Good | Clean confound | ✅ Keep |
| rt-04 | physics | RT-c | excess | virtuous-wrong | Strong — virtuous explicitly self-flags "My conclusion is wrong if the bend attenuated the channel." **Strongest virtuous-wrong of all 20.** | Good | Best example of virtuous-wrong pattern | ✅ Keep |
| rt-05 | medicine | RT-b | deficiency | none | Strong — virtuous frames as "a threshold tradeoff, not as a pure accuracy question" and makes the 156-minute-vs-5-missed-cases value judgment explicit | Good | — | ✅ Keep |

**ChatGPT RT batch summary:**
- Domain coverage ✓
- Failure split 2 excess / 3 deficiency ✓
- Correctness-confound coverage ✓
- Length matching: excellent (all within ~10%)
- **No caricature issues on RT excess** — procedural step-enumeration is a naturalistic RT-excess failure mode, unlike the keyword-stuffing ChatGPT fell into for EG-excess
- **Best virtuous-wrong implementation in the audit** (rt-04)

---

## 2. Cross-batch structural checks

| Check | Sonnet EG | Sonnet RT | ChatGPT EG | ChatGPT RT |
|---|---|---|---|---|
| 5 triplets delivered | ✓ | ✓ | ✓ | ✓ |
| Domain coverage ≥4 distinct, no domain >2 | ✓ (5/5 distinct) | ✓ (5/5 distinct) | ✓ (5/5 distinct) | ✓ (5/5 distinct) |
| Failure split 3/2 or 2/3 | ✓ 2e/3d | ✓ 2e/3d | ✓ 3e/2d | ✓ 2e/3d |
| Correctness-confound: 1 virtuous-wrong + 1 non-virtuous-right | ✓ | ✓ | ✓ | ✓ |
| No real citations | ✓ | ✓ | ✓ | ✓ |
| No safety-refusal register | ✓ | ✓ | ✓ | ✓ |
| No meta-commentary / markdown headers in passages | ✓ | ✓ | ✓ | ✓ |
| Length ±10% across triad | ⚠ ~3/5 drift | ⚠ ~3/5 drift | ✓ | ✓ |
| Substrate preserved across neutral/virt/non-virt | ✓ | ✓ | ✓ | ✓ |
| Dominant contrast axis matches target virtue | ✓ | ✓ | ✓ (virtuous) / 🔴 (3 excess non-virt) | ✓ |

**Domain overlap between EG and RT batches:** Sonnet overlaps on medicine (eg-02 + rt-04) and psychology (eg-03 + rt-05). ChatGPT overlaps on physics (eg-01 + rt-04), medicine (eg-03 + rt-05), and psychology (none — rt-03). This is FINE for extraction (the constraint is per-virtue domain balance, not cross-virtue), and actually *helpful* for specificity-matrix testing: we can check whether v_EG and v_RT are separable within a shared domain.

---

## 3. Quality-dimension comparison: ChatGPT vs. Sonnet

| Dimension | Sonnet | ChatGPT | Winner |
|---|---|---|---|
| Domain diversity | 5/5 distinct both batches | 5/5 distinct both batches | tie |
| Length matching (±10%) | ~3/10 miss | ~0/10 miss | ChatGPT |
| Sub-facet contrast clarity | Strong throughout | Strong on RT, good on EG virtuous, **caricature on EG excess** | Sonnet for EG, tie for RT |
| Naturalistic non-virtuous register | Consistent | Strong on RT, **caricature on EG excess** | Sonnet for EG, tie for RT |
| Virtuous-wrong correctness-confound | Weak (cautious-not-wrong) | **Strong (commits-to-wrong-claim)** | ChatGPT |
| Non-virtuous-right correctness-confound | Strong | Strong | tie |
| Substrate richness | Dense technical detail | Cleaner, more concise | stylistic preference |
| Fact-pack documentation | More detailed (adds "Correctness confound note" section, cross-virtue domain note, register notes) | More terse but complete | Sonnet for audit trail, ChatGPT for readability |

**Synthesis.** The two LLMs have nearly-complementary strengths. Sonnet is better at avoiding caricature in the excess failure mode for EG specifically, but weaker on length control and on implementing the virtuous-wrong correctness-confound. ChatGPT is better on length control and virtuous-wrong, but mode-collapses on EG-excess caricature. Both are strong on RT. **A final corpus mixing both sources will be more diverse than either source alone** — consistent with the `generation-guidelines.md` §2.6 human-anchor mixing rationale applied at the LLM-source level.

---

## 4. Prompt refinements for batch 2 (15 more per virtue per LLM)

### Refinements applying to both LLMs

**R1. Strengthen length-matching constraint with an explicit check.**

Add to the hard-constraints section:

> **Length check is MANDATORY before delivery.** For each triplet, count words in all three passages. If the longest and shortest differ by more than 10%, trim or lengthen to within 10% before committing the file. Virtuous passages have a natural tendency to run longer because epistemic-virtue phrasing takes more words; compensate by tightening wording, not by adding content to non-virtuous. State the word counts in your final summary message.

**R2. Sharpen the virtuous-wrong correctness-confound.**

Add to the correctness-confound rotation section:

> **A virtuous-wrong triplet requires the virtuous reasoner to COMMIT to a specific factual claim that is wrong — not merely to be appropriately cautious about uncommitted claims.** The virtuous reasoner must write a sentence like "The best-grounded conclusion is X" where X is in fact not true, while reaching X through transparent and principled reasoning from the available evidence. Being "appropriately cautious and therefore not committing" is not a virtuous-wrong case — that is just good epistemic practice.
>
> Worked example of virtuous-wrong done well: ChatGPT `eg-03-medicine-inhaler-technique-pollen-confound` and `rt-04-physics-scintillator-gain-drift-cable-bend` in the v1 calibration batch. The virtuous reasoner commits to "poor technique is the best grounded working explanation" / "I make temperature the leading working explanation" — both of which are explicitly wrong per the fact-pack's hidden ground truth. The reasoning is transparent and careful; the conclusion it reaches is wrong.

**R3. Align sub-facet labels with the `mvp-virtues.md` EG-a/b/c and RT-a/b/c convention.**

Add to the fact-pack template section:

> `target_sub_facet` field must use the canonical labels from `docs/mvp-virtues.md`: `EG-a` / `EG-b` / `EG-c` (not "Tying claims to specific observations"), or `RT-a` / `RT-b` / `RT-c` (not "Showing the steps"). Use the descriptive name in parentheses after the label for clarity: `EG-a — tying claims to specific observations or data`.

### Refinements specifically for ChatGPT

**R4. Anti-caricature constraint for EG excess-failure.**

Add to the virtue-specific contrast axis section for Evidence Grounding:

> **Explicit anti-caricature rule for EG excess-failure non-virtuous passages:**
>
> The word "evidence" (and word-forms "evidential," "evidentiary," "evidence-based," etc.) may appear at most **6 times** in a non-virtuous excess passage of 250-350 tokens. This is a ceiling, not a target — lower is fine.
>
> EG excess-failure should sound like a **working scientist who has developed a bureaucratic habit** — methodological qualifiers ("as is standard for this type of intervention"), redundant provenance citations ("as documented in the protocol-adherence data reviewed by the trial safety committee"), unnecessary methodological disclaimers ("which as is standard for this type of intervention enrolled…"). It should NOT sound like a LARP where every sentence contains the word "evidence." Do not produce passages where "evidence" is inserted as a prefix or suffix to phrases that would be clearer without it.
>
> Worked example of naturalistic EG-excess done well: Sonnet `eg-02-medicine-neonatal-surfactant-rct` in the v1 calibration batch. Note that the word "evidence" appears only ~3 times in its ~300-token non-virtuous passage; the excess failure is achieved through methodological qualifiers, not through keyword insertion.

### Refinements specifically for Sonnet

**R5. Length-asymmetry warning for virtuous passages.**

Add to the virtue-specific contrast axis section:

> When writing the virtuous passage, resist the natural tendency to add framing sentences like "Two claims warrant different confidence levels here" or "From there, interpretation requires care" that are not present in the neutral baseline. These sentences inflate the virtuous passage length without contributing to the disposition contrast. Prefer to achieve the disposition shift through in-line word-level changes rather than through framing additions. When in doubt, target virtuous passage length to match the neutral baseline length, not exceed it.

---

## 5. Regeneration plan for the 3 caricature triplets

Rather than scrap the 3 ChatGPT EG excess triplets entirely, regenerate only the `non-virtuous.md` file in each. Fact-pack, neutral, and virtuous are all good. Instruct ChatGPT:

> The fact-pack, neutral, and virtuous files for this triplet are ready and should NOT be changed. Only the non-virtuous.md file needs regeneration. Apply the R4 anti-caricature constraint: at most 6 uses of "evidence"-family words in the passage, and the excess failure mode must be achieved through methodological qualifiers and redundant provenance citations, not through keyword insertion. Study Sonnet's `eg-02-medicine-neonatal-surfactant-rct/non-virtuous.md` as a reference for what naturalistic EG-excess looks like.

Affected files:
- `corpus/chatgpt-mvp/triplets-evidence-grounding/eg-01-physics-cloud-chamber-humidity-tracks/non-virtuous.md`
- `corpus/chatgpt-mvp/triplets-evidence-grounding/eg-04-economics-transit-pass-ridership/non-virtuous.md`
- `corpus/chatgpt-mvp/triplets-evidence-grounding/eg-05-chemistry-solvent-water-yield-drop/non-virtuous.md`

---

## 6. Decision recommendation

**Accept the v1 calibration batch (20 triplets) with the 3 regenerations above.** This is a pass on the calibration gate described in the original prompt ("human-reviewed before the remaining 15 triplets are generated").

**Authorize batch 2:**
- 15 more EG triplets from ChatGPT with prompt refinements R1–R4 applied
- 15 more RT triplets from ChatGPT with prompt refinements R1–R3 applied (R4 doesn't apply — RT excess was fine)
- 15 more EG triplets from Sonnet with prompt refinements R1, R2, R3, R5 applied
- 15 more RT triplets from Sonnet with prompt refinements R1, R2, R3, R5 applied

That yields 60 new triplets + 20 calibration = **80 LLM-generated triplets total** across both virtues. With the 20 substrate-reuse triplets we write against the top-ranked substrates from `corpus-reuse-sampling-eg-rt.md`, we reach ~100 candidate triplets for 40-per-virtue MVP corpora — enough headroom to curate aggressively on quality.

**Do NOT** start extraction on any of this corpus until the full 80 LLM triplets + 20 substrate-reuse triplets are in place and hand-audited. Extraction on a partially-curated corpus would bake in the mode-collapse/caricature issues we just caught.

---

## 7. What this tells us about the LLM-corpus-gen approach more broadly

This audit is a data point for the eventual corpus-generation automation decision (Phase 5+ per `mvp-virtues.md`):

1. **Frontier LLMs can produce near-publication-quality contrastive triplets with a detailed prompt.** The structural constraints (domain rotation, failure-mode rotation, correctness-confound coverage, sanitization) were hit cleanly by both. That was not obvious a priori.
2. **Failure modes are LLM-specific.** ChatGPT's EG-excess caricature is a systematic pattern worth anticipating; Sonnet's length-inflation is different but equally systematic. Prompt refinements need to be tuned per LLM family once a failure mode is identified.
3. **Cross-family mixing matters.** Neither LLM alone would produce a corpus without a systematic bias. Mixing both (plus human-written substrate-reuse) is a diversity-hedge similar to the human-anchor mixing rationale in `generation-guidelines.md` §2.6.
4. **Calibration-batch-first is the right workflow.** Catching the excess-caricature in 5 triplets cost ~1 hour of audit; catching it in 20 would have required regenerating 3× as many passages and possibly 3× the LLM-API cost. Keep the calibration-batch-first rule as a standing process for every new corpus work.

---

## 8. Next concrete steps

1. **User reviews this audit.** Confirm the accept-batch-1 + authorize-batch-2 + regenerate-3 decision, or push back with corrections.
2. **Generate refined prompts.** Assistant drafts updated prompts for Sonnet and ChatGPT per §4 refinements; user pastes into new sessions.
3. **Run regenerations in parallel with batch 2.** ChatGPT regenerates the 3 caricature non-virtuous files in one session; meanwhile Sonnet/ChatGPT begin batch 2 (15 × 4 = 60 new triplets) in separate sessions.
4. **When all LLM output lands,** assistant hand-audits the batch-2 60 triplets against the refined constraints.
5. **In parallel,** assistant writes ~20 substrate-reuse triplets against the top-ranked substrates identified in `corpus-reuse-sampling-eg-rt.md`.
6. **Final curation pass** on the ~100-triplet combined pool → select 40 EG + 40 RT for extraction.

Estimated timeline at MVP pace: 3-5 days for steps 2-5.
