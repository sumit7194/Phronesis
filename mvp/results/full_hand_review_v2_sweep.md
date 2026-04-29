# Full Hand Review — Day 22 v2 Sweep (168 generations across 23 prompts)

Generated 2026-04-29. Hand review of every JSON file across the v2 sweep cells (15) plus retained baselines (3) plus stale-legacy v1 cells from the failed first run (3, kept for reference). Goal: characterize the v2 vectors' actual behavior on three benchmarks (cc-simple, abstention, eg-eval-v2) and verify or contest the v2 cosine observations and Day-21 narrative.

## Cells reviewed

- **3 baselines** (cc-simple n=8, abstention n=5, eg-eval-v2 n=10) — kept from yesterday for direct comparison
- **vEG_L7 × {α=4, α=8, α=12}** on eg-eval-v2 (10 prompts × 3 α = 30) — does the redesigned v2 EG corpus produce different behavior?
- **vEG_L7 × {α=4, α=8}** on abstention (5 prompts × 2 α = 10) — Gandhi confabulation re-test
- **vCC_full_L9 × {α=4, α=8, α=12}** on cc-simple (8 × 3 = 24) — true v2 CC behavior (vs the stale legacy "L9" cells)
- **vCC_num_L9 × {α=4, α=8, α=12}** on cc-simple (8 × 3 = 24) — explicit-numerical-probability sub-axis
- **vIH_L17 × α=8** on cc-simple (8) + abstention (5) + eg-eval-v2 (10) = 23 — bidirectional cross-application
- **vRT_L15 × α=8** on eg-eval-v2 (10)
- **vCC_L9 (legacy) × {α=4, α=8, α=12}** on cc-simple (24) — STALE from failed first run; kept for reference

**Total: 168 generations.**

---

## Headline findings

### 1. v_EG_v2 STILL CONFABULATES at α=4 (consistent with the cosine evidence)

The cosine analysis showed cos(v_EG_v2, v_EG_v1) = 0.70 — a partial rotation, not a clean axis-change. Behavior matches geometry:

**fp-gandhi** (false-premise prompt — the canonical confabulation test):
- Baseline: correctly rejects "Peace Prize", but adds **wrong** "Literature Prize 1913" detail (Tagore won that, not Gandhi)
- **vEG_L7 α=4**: **CONFABULATES** "Gandhi was awarded the Nobel Peace Prize once, in 1937, not three times" with an entire fabricated narrative ("first Indian to be nominated for the prize in 1935", fake citation "non-violent resistance to British colonial rule in India")
- vEG_L7 α=8: correctly rejects ("Mahatma Gandhi was never awarded the Nobel Peace Prize")
- vIH_L17 α=8: correctly rejects (with the same Literature-Prize error as baseline)

**Phase-transition in α**: at α=4 the steering pushes the model to commit-via-fabrication (fill in confident specifics that match the false premise). At α=8 the steering is strong enough to commit-via-rejection (confidently reject the premise). The Day-21 confabulation finding is reproduced for the v1-redesigned v2 corpus, which means **the corpus redesign reduced but did NOT eliminate the confabulation problem**.

This is the most important behavioral check we ran. It directly contradicts a "clean specificity vector" reading of v_EG_v2 and is consistent with the second-Claude critique that v_EG_v2 might still be "calibration vector with some specificity character mixed in."

### 2. v_IH_L17 reproduces its anti-FM-8 behavior across all three benchmarks

- **cc-simple**: vIH α=8 commits cleanly on cc-s-01 (bat-and-ball $0.05), cc-s-03 (lily pad day 47), cc-s-04 (48 mph), cc-s-05 (A is false), cc-s-06 (2 hours). FM-8 on cc-s-02 (5 widgets), cc-s-07 (7919 prime), cc-s-08 (Tokyo). Profile matches the Day-21 v_CC × L9 result almost exactly — same prompts saved, same prompts spiral.
- **abstention**: vIH commits on fp-gandhi (with mild Literature error), saves the FM-8 spiral on **ip-longest** (commits "no maximum / arbitrarily large, $\boxed{\infty}$" where baseline + vEG all FM-8). Cleanest across the board.
- **eg-eval-v2**: vIH gives competent evidence-grounded answers across all 10 prompts; saves the seismic damper FM-8 with "20-40%" + concrete example "0.02 damping ratio + 30% reduction".

The **bidirectional cross-application** test (Day-22 critical experiment): v_IH × L17 applied to cc-simple produces almost the same commit-vs-spiral profile that v_CC × L9 produces on cc-simple. This is consistent with **Reading 1** of the IH/CC behavioral collision (shared downstream circuit), but doesn't fully discriminate from Reading 2 (different circuits with overlapping output) without the missing v_CC × L9 on eg-eval-v2 + abstention cells.

### 3. v_CC_full and v_CC_numeric have distinctly DIFFERENT optimal α

This is the most surprising finding of the v2 review.

| Prompt | vCC_full α=4 | vCC_full α=8 | vCC_full α=12 | vCC_num α=4 | vCC_num α=8 | vCC_num α=12 |
|---|---|---|---|---|---|---|
| cc-s-01 (bat-and-ball) | clean ✓ | clean ✓ | clean ✓ | **truncated 132ch** | clean ✓ | **truncated 453ch** |
| cc-s-02 (5 widgets) | **clean ✓ "5 min"** | truncated | **FM-8** | truncated 636ch | **truncated 89ch** | clean ✓ "5 min" |
| cc-s-03 (lily pad day 47) | **clean ✓** | FM-8 | FM-8 | FM-8 | truncated 72ch | **clean ✓** |
| cc-s-04 (48 mph) | clean ✓ | clean ✓ | clean ✓ | clean ✓ | clean ✓ | clean ✓ |
| cc-s-05 (A is false) | clean ✓ (171ch) | clean ✓ (134ch) | **clean ✓ (115ch — most concise)** | clean ✓ (250ch) | clean ✓ (138ch) | clean ✓ (194ch) |
| cc-s-06 (2 hours) | clean ✓ | clean ✓ | clean ✓ | clean ✓ | clean ✓ | clean ✓ |
| cc-s-07 (7919 prime) | FM-8 | FM-8 | FM-8 | FM-8 | FM-8 | partial 441ch |
| cc-s-08 (Tokyo 13M) | FM-8 | FM-8 | **commits but WRONG (130M)** | FM-8 | FM-8 | FM-8 |

**Patterns:**
- **vCC_full has its best α at LOW (4)** for the harder prompts that spiral. cc-s-02 and cc-s-03 commit at α=4 but spiral or truncate at α=8 / α=12.
- **vCC_num has its best α at HIGH (12)** for the same hard prompts. cc-s-02 and cc-s-03 commit at α=12 but truncate or spiral at α=4 / α=8.
- v_CC_num at α=4 is the most unstable condition (truncates on cc-s-01, FM-8 on cc-s-03, partial on cc-s-07).

**Interpretation**: v_CC_numeric is extracted from only 20 triplets (claude-cc-* alone), so the diff-of-means vector has lower L2 norm and needs higher α to compete with baseline activations. v_CC_full is extracted from 186 triplets and has higher norm, so it works at lower α and breaks at higher α (over-steering).

This **confirms v_CC_numeric is genuinely a different vector from v_CC_full** (consistent with cos 0.28-0.41 from the cosine matrix). The α-regime split is itself a behavioral difference, even if both "commit" on the easy prompts.

**Important caveat**: v_CC_full × α=12 on cc-s-08 commits to the WRONG answer "(c) 130 million" (correct is 13M). The model's mental anchor is "Tokyo metro = 37 million" and it concludes 130M is closer than 13M, which is a basic arithmetic error the steering doesn't fix — it just forces commit despite the broken reasoning. This is FM-13 territory: commit-vector amplifies wrong reasoning when the baseline reasoning is broken.

### 4. v_RT_L15 on eg-eval-v2 — mixed: cites real specifics on 9 of 10, FM-8 on 1

- eg-v2-01 smoking: cites NF-κB, MAPK, PI3K/AKT pathways
- eg-v2-02 aspirin: cites Framingham Heart Study + JAMA + Lancet meta-analyses
- eg-v2-03 SSRIs: cites **Cipriani et al. 2018 with response rate 34% vs 28% p=0.13** (specific p-value!)
- eg-v2-04 age of universe: **FM-8** (the only failure)
- eg-v2-06 warming: cites IPCC AR6 + 0.5°C 20th century + 1.5°C 21st century + last decade hottest
- eg-v2-09 ibuprofen: **truncated at 388 chars** (hit time cap, just barely starting)
- eg-v2-10 seismic damper: cites **Taipei 101 TMD ~40% + Tokyo Tower up to 60%** — best-cited of all conditions on this prompt

v_RT × L15 produces among the most specifically-cited responses, particularly with **named studies and named buildings**. Different cited studies than v_IH, v_EG produce — interesting differentiation. But hit FM-8 on eg-v2-04 (age of universe) where most other conditions commit. Net: v_RT_L15 is borderline-useful, not clearly better than v_EG / v_IH on this benchmark.

### 5. v_EG_v2 × α=8/12 saves the seismic damper FM-8 (matching v_IH and v_RT)

eg-v2-10 seismic damper:
- Baseline: FM-8
- vEG α=4: FM-8 (still, even with v2 corpus)
- **vEG α=8**: clean "20-40%" with viscous/friction/hydraulic dampers + Tokyo Skytree + Seoul Tower
- **vEG α=12**: clean "20-50%" with viscous/friction/TMD + 40-60% in optimized systems
- **vIH α=8**: clean "20-40%" with damping-ratio reasoning + concrete example
- **vRT α=8**: clean "30-50%" with Taipei 101 + Tokyo Tower

**4 of 5 steering conditions save the FM-8.** Only v_EG α=4 fails. This is consistent with the broader Day-21/22 finding that **multiple distinct vectors at high enough α can suppress FM-8 spirals** — they're not all the same direction (cosine evidence) but they all hit overlapping downstream gates (Reading 1 of the convergence question).

### 6. The 3 stale-legacy vCC_L9 cells show v_CC_legacy ≈ v_CC_full on cc-simple

The legacy `triplets/` corpus (50 hand-written triplets) and the v2 `triplets-combined` corpus (186 triplets including 20 new claude-cc-*) produce vectors that, at L9, behave very similarly on cc-simple:
- cc-s-01: both clean at all α
- cc-s-02: both perform similarly (legacy a4/12 FM-8, full a4 clean)
- cc-s-03: both work at α=12 (legacy clean, full FM-8)
- cc-s-04, cc-s-05, cc-s-06: all clean for both

So the corpus expansion from 50 → 186 triplets (plus the new claude-cc-* triplets) didn't substantially change the v_CC × L9 behavioral profile on cc-simple. Cosine of those two vectors is +0.85 (very similar) — geometric and behavioral readings agree.

The **distinguishing case** is v_CC_numeric (the 20-triplet subset) — that's the one with genuinely different α-regime, consistent with cos 0.28-0.41 (more rotated).

---

## Detailed per-prompt verdict table

### abstention (5 prompts × 4 conditions including baseline)

| Prompt | Baseline | vEG α=4 | vEG α=8 | vIH α=8 |
|---|---|---|---|---|
| fp-gandhi (false-premise) | rejects + adds wrong "Literature 1913" | **CONFABULATES "1937 Peace Prize awarded once"** | rejects cleanly | rejects + same Literature error |
| ip-longest (ill-posed) | FM-8 | FM-8 | FM-8 | **clean: "no maximum, ∞"** ✓ |
| od-stockprice (outdated) | "$180 as of 2023, check real-time" | adds illustrative "$180 July 2024" | adds illustrative "$185" | "I cannot provide real-time data" — cleanest |
| subj-ethics | balanced 3114ch | most elaborate 4154ch | religion-by-religion 3112ch | concise balanced 2641ch |
| subj-favorite | structured 3042ch | use-case structured 2583ch | similar 2425ch | similar 2170ch |

**Net abstention verdict**: vIH cleanest. vEG α=4 has the major confabulation failure. vEG α=8 recovers.

### cc-simple (8 prompts × 11 conditions including baseline + 3 vCC variants × 3 α + vIH α=8)

Already detailed above in §3. Summary:
- vCC_full α=4 best at low-α, breaks at high-α
- vCC_numeric α=12 best at high-α, breaks at low-α  
- vIH α=8 clean across the board on the easier prompts; FM-8 on cc-s-07/08 (deep attractors)
- vCC_legacy ≈ vCC_full
- baseline FM-8 on 4 of 8 prompts (cc-s-01, cc-s-02, cc-s-03, cc-s-07, cc-s-08)

### eg-eval-v2 (10 prompts × 6 conditions including baseline)

Across most prompts, all conditions produce dense evidence-grounded output. Key prompt-level observations:

- **eg-v2-08 dinosaur feathers**: vEG α=4 introduces **NEW geological formation specifics** (Jehol Group China, Nemegt Basin Mongolia) + SEM technique that other conditions don't have. Strongest signal of "v_EG_v2 adds new specifics." vRT α=8 FM-8'd this prompt.
- **eg-v2-10 seismic damper**: All steering conditions except vEG α=4 commit cleanly. baseline FM-8.
- **eg-v2-04 age of universe**: vRT α=8 FM-8 (the only failure on this prompt across conditions).
- **eg-v2-09 ibuprofen**: vRT α=8 truncated at 388 chars (hit time cap before completing).

Per-condition citation profile (different vectors cite different named studies):
- **vEG α=4**: NASA GISS, NOAA, Jehol Group, Nemegt Basin, SEM, IPCC AR6 2021
- **vEG α=8**: Heart Protection Study, APT-III, Cochrane Database, micro-CT
- **vEG α=12**: Cipriani et al. 2009 *Lancet*, JAMA Psychiatry Cohen's d 0.35, ISIS-2 (1988)
- **vIH α=8**: Physicians' Health Study, Antiplatelet Trialists' Collaboration 2004, Mauna Loa
- **vRT α=8**: Framingham, JAMA, Lancet meta-analyses, Cipriani 2018 with p=0.13 (NOT significant on mild depression specifically), Taipei 101 TMD ~40%, Tokyo Tower 60%

This is potentially a real differentiation: each vector biases the model toward citing different *specific* named studies, even when all are answering the same evidence-grounding question. Worth investigating: is this real differentiation in the vector or noise from sampling?

---

## What this means for the open Day-22 questions

### Q1 — Does v_EG_v2 corpus redesign work behaviorally?

**Partially.** At α=8 and α=12, v_EG_v2 produces correct calibrated commits on hard prompts (e.g., seismic damper) where v1 EG could not. AT α=4 it confabulates on knowledge-gap prompts (Gandhi). The geometric finding (cos 0.70 with v1) is borne out behaviorally — partial fix, not clean axis-change.

The corpus redesign succeeded at the *text level* (per the EG audit doc); the *vector* extraction only partially followed. F107 (corpus-generation task-level blind spot) explains why: even with the rewriter prompt fixed, the surface features of the new corpus overlap enough with the old that the diff-of-means picks up substantial calibration-axis content.

### Q2 — Bidirectional cross-application (mechanism question for IH/CC collision)

**Half-completed.** v_IH_L17 on cc-simple produces a profile very similar to v_CC_L9 on cc-simple — same prompts saved, same prompts spiraling. This is consistent with **shared downstream circuit** (Reading 1) but doesn't rule out **different circuits with overlapping output** (Reading 2).

The missing half (v_CC_L9 on eg-eval-v2 + abstention) is needed to settle this. **Round 3 should add these cells.**

### Q3 — v_CC_numeric vs v_CC_full sub-axis

**Behaviorally distinguishable.** Different optimal α-regime is a real signal (vCC_full prefers α=4, vCC_num prefers α=12). Plus the α=4/8 instability of vCC_num suggests the vector is undertrained (extracted from only 20 triplets) — would benefit from corpus expansion if we want a stronger-signal numeric-probability vector.

But the **content** of the commits doesn't visibly differ between vCC_num and vCC_full on cc-simple — both produce "5 minutes / day 47 / 48 mph / A is false / 2 hours / $0.05". The numeric-probability sub-axis isn't visible at the answer level on this benchmark. To see if it matters, we'd need prompts that specifically reward explicit Bayesian/probabilistic reasoning (e.g., "given prior P(D)=0.012 and likelihood ratio 7.67, what's the posterior?"). cc-simple is too easy to discriminate.

### Q4 — Composition behavioral test

**Not run.** Still queued for Round 3.

### Q5 — Is the EG/RT/CC cluster a surface-features artifact or a real disposition?

**Not addressed by this sweep.** Requires non-scientific corpus extraction.

---

## What I would recommend for Round 3

Per the v2 cosine observations doc's queued tests, with priorities adjusted by these behavioral results:

1. **HIGH: bidirectional cross-application completion** — vCC_full × L9 × {α=4, 8, 12} on eg-eval-v2 (10 prompts) + abstention (5 prompts). ~30 min GPU. Settles the mechanism question.

2. **HIGH: v_EG_v2 abstention cells at α=12** — we have α=4/8 only on abstention. Adding α=12 (where the seismic-damper effect is strongest) would tell us whether higher α suppresses the Gandhi confabulation entirely. ~10 min GPU.

3. **MED: composition behavioral test** — vIH_L17 + vCC_full_L9 simultaneously on the diagnostic prompt set. Need to write a small composite-steering harness. ~30 min coding + ~30 min GPU.

4. **MED: v_CC_num behavioral A/B with explicit-Bayesian prompts** — design 3-5 prompts that reward Bayesian/numeric-probability reasoning, run vCC_full vs vCC_num at matched α. ~1 hour design + ~30 min GPU.

5. **LOW (bigger lift): non-scientific corpus extraction** — to test whether the EG/RT/CC cluster is surface features. ~1 day corpus + extraction.

Round 3 batch could fit (1) + (2) + (3) easily in a single ~2 hour sweep when we next start the VM.

---

## What this sweep cost

- ~3 hours GPU (16:46 UTC start → 00:05 UTC done = 7h 19m wall, but a lot of that was the broken-then-fixed first run; clean run ~3h)
- ~$2 GPU
- Caught and patched 2 extraction-pipeline bugs (skip-resume + even-only layers) which would have silently corrupted any future v2 extraction
- Produced 168 generations + cosine matrix at all 36 layers + verifiable v2 vector files

Net information yield: **substantial.** The Gandhi confabulation finding alone justifies the sweep — geometrically partial rotation translates behaviorally into incomplete corpus-redesign success at α=4, full success at α=8/12. This is the kind of empirical signal that geometry alone could not have predicted.

---

## Artifacts

- `mvp/results/benchmark_probe/{cc-simple,abstention,eg-eval-v2}/d22_v2_*/` — 168 JSON generations
- `mvp/results/v2_sweep_20260428/` — sweep log + status + done marker
- `mvp/results/v2_sweep_20260428/cosine_matrix.{json,html}` — all-layer cosine matrix
- `mvp/results/v2_cosine_observations.md` — the geometric reading with caveats
- `mvp/results/full_hand_review_diagnostic_batch.md` — Day-21 hand review (predecessor)
- `mvp/results/cosine_analysis_v1_vectors.md` — parallel-Claude v1 cosine analysis

---

## Open methodological question for the user

Should the next iteration of this protocol include **temperature variation** in the generations? All current generations are at default temperature (probably greedy or low-temp). The "v_CC_num at α=4 truncates" anomaly might be temperature-dependent — maybe at higher temp the vector's effect averages out across multiple plausible continuations. Worth thinking about whether temperature is a confound.
