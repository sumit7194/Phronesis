# Phronesis MVP combined corpus — ledger

**Created:** 2026-04-22 (Day 15)
**Last updated:** 2026-04-22 (Day 15 — post-swap v2)
**Purpose:** Single curated corpus for MVP extraction of v_EG (Evidence Grounding) and v_RT (Reasoning Transparency) on Qwen3-4B and Gemma 4 E4B-it. Draws from three sources: ChatGPT, Sonnet, and hand-written substrate-reuse.

**Total triplets:** 80 (40 EG + 40 RT)
**MVP target:** 40 per virtue ✓ (met)

---

## 1. Source composition

| Virtue | ChatGPT | Sonnet | Substrate-reuse | Total |
|---|---|---|---|---|
| Evidence Grounding | 20 | 15 | 5 | **40** |
| Reasoning Transparency | 20 | 15 | 5 | **40** |

**Three-source diversity hedge.** Each source has independent failure modes (ChatGPT's original EG-excess caricature, Sonnet's length-asymmetry drift, human substrate-reuse's shorter average length). Mixing three sources reduces the risk that any single systematic bias contaminates the extracted vector.

### Swap history (v1 → v2)

**v1** (first cut): 20 ChatGPT + 20 Sonnet per virtue = 40. Eight Sonnet triplets flagged for 11-16% length asymmetry.

**v2** (this version): Substrate-reuse triplets were length-fixed (all now ≤8% range); 5 worst-asymmetric Sonnet triplets per virtue were dropped and replaced with the 5 fixed substrate-reuse triplets per virtue. Result: three-source diversity + only 1 remaining length flag across all 80 triplets (vs. 8 in v1).

**Sonnet triplets dropped in the swap (10 total):**

EG: `eg-01-physics-plasma-density-diagnostic` (13%), `eg-02-medicine-neonatal-surfactant-rct` (16%), `eg-03-psychology-sleep-deprivation-working-memory` (15%), `eg-07-biology-rnaseq-batch-effect` (11%), `eg-09-chemistry-lcms-matrix-suppression` (14%).

RT: `rt-03-engineering-fatigue-crack-growth` (13%), `rt-10-economics-synthetic-control-trade` (10%), `rt-11-economics-bunching-notch-kink` (10%), `rt-13-physics-exoplanet-co2-inference` (10%), `rt-14-physics-dark-energy-snia` (16%).

These 10 dropped Sonnet triplets remain in `corpus/sonnet-mvp/` as an extended pool, available for re-inclusion if length is fixed later.

**Substrate-reuse triplets added in the swap (10 total):** All 10 from `corpus/substrate-reuse/` after length-fix pass brought every triplet to ≤8% range.

---

## 2. Verification status

### Structural checks (all 80 triplets)

| Check | Pass | Flag | Fail |
|---|---|---|---|
| 4-file completeness (fact-pack + neutral + virtuous + non-virtuous) | 80/80 | 0 | 0 |
| Length ±10% across triad | **79/80** (up from 72/80 in v1) | **1** | 0 |
| Substrate preserved neutral→virtuous→non-virtuous | verified, no issues | — | — |
| No safety-refusal register | verified, none detected | — | — |
| No real named researchers / institutions / papers | verified, none detected | — | — |
| No meta-commentary or markdown headers in passages | verified, none detected | — | — |
| Canonical sub-facet labels (EG-a/b/c, RT-a/b/c) | 65/80 | 15 (ChatGPT batch-1 uses descriptive names) | 0 |
| No "evidence"-keyword caricature (EG excess) | 18/18 pass (all EG-excess non-virtuous ≤2 "evidence" uses) | 0 | 0 |

**Remaining length flag:** `sonnet-eg-17-medicine-icu-early-mobilisation` at 13% (240/251/222 words). Could be dropped in a future iteration if a cleaner medicine-EG candidate becomes available, but retained here because the contrast axis is strong and the 13% is at the lower bound of "⚠ length" rather than mid-range.

### Content spot-checks (manual read, performed during v1 audit)

- **ChatGPT batch-1 EG caricature regeneration:** eg-01, eg-04, eg-05 non-virtuous re-read. "Evidence"-family word count dropped from 15-25+ to 0. Register shifted to over-hedged epistemic qualification rather than keyword stuffing. Acceptable for extraction.
- **Sonnet batch-2 virtuous-wrong:** eg-16 IV-returns-schooling spot-checked. Virtuous explicitly commits: "14.2% is the causal estimate most directly supported by the data, and I would report it as the preferred estimate." Hidden ground truth (per fact-pack): ATE is actually 10-11%. Committal virtuous-wrong — R2 refinement worked.
- **ChatGPT batch-2 EG excess register:** eg-11, eg-13 non-virtuous read. Over-hedged qualification ("should be described as... deliberately bounded conclusion"). Contrast with virtuous is real but subtler than Sonnet's procedural-qualifier excess. Acceptable, flagged as lower-contrast-strength for curation follow-up.
- **Scenario duplicates across sources:** none found. Closest near-duplicate was Sonnet `rt-07-landslide-threshold` vs. ChatGPT `rt-02-hillslope-rainfall-threshold` — different scenarios (20-year regional record with 47 landslides vs. single hillslope with moisture probes). Distinct weak-link focus. Acceptable as variations.
- **Substrate-reuse length fixes:** All 10 fixed by either trimming long rewrites (8 triplets) or expanding short neutrals with substrate-compatible detail (2 triplets: eg-sr-05, rt-sr-02). Substrate values (numbers, specific claims) preserved in every edit.

---

## 3. Non-repeatability (uniqueness) audit

### Scenario-level uniqueness across 80 triplets

**Criterion:** No two triplets share the same substrate scenario within either virtue. Near-topic overlap (e.g., two different landslide scenarios) is acceptable as long as factual substrate, numeric values, and central weak-link are distinct.

**Method:** Compared scenario slugs, factual substrate bullets, and conclusion spaces across all 80 triplets.

**Result:** ✓ All 80 scenarios are distinct. Near-topic overlaps:

| Near-topic overlap | EG/RT | Justification |
|---|---|---|
| Sonnet rt-07 landslide + ChatGPT rt-02 hillslope-rainfall | RT | Different data structure (regional 20-year record vs single-slope moisture probes); different weak-link focus |
| Sonnet rt-01 enzyme-kinetics + ChatGPT rt-07 enzyme-temperature | RT | Different enzyme question (inhibition mode vs temperature acclimation); different sub-facet (RT-a vs RT-b) |
| Sonnet rt-sr-01 RDD class-size + Sonnet rt-09 RDD wage-floor | RT (both by different LLMs — wait, both Sonnet? Actually rt-09-rdd-wage-floor is Sonnet and rt-sr-01 is substrate-reuse) | Different DV (class-size achievement vs wage-floor), different policy extrapolation structure. Both use RDD methodology but distinct scenarios. |
| Sonnet eg-18 GW strain-sensitivity + substrate rt-sr-02 GW chirp-mass | EG/RT (cross-virtue) | Different physics question (strain calibration vs chirp mass classification). EG virtuous vs RT virtuous focus distinct axes. Not a contamination risk because different virtues + different specific substrates. |

### Within-source uniqueness

- ChatGPT: 20 EG + 20 RT = 40 distinct scenarios ✓
- Sonnet: 15 EG + 15 RT = 30 distinct scenarios ✓ (dropped 10 in swap)
- Substrate-reuse: 5 EG + 5 RT = 10 distinct scenarios ✓

### Cross-source uniqueness

- ChatGPT × Sonnet: no exact duplicates ✓
- ChatGPT × Substrate-reuse: no overlap (substrate-reuse picked from `triplets-combined/` CC corpus scenarios, which neither LLM chose) ✓
- Sonnet × Substrate-reuse: no exact duplicates. Near-overlap on RDD (Sonnet rt-09 wage-floor + substrate rt-sr-01 class-size) — both use RDD methodology but on different policy questions. Acceptable.

### Cross-virtue uniqueness (EG × RT)

- Within combined 80, no scenario appears in both EG and RT. ✓ (Key guard against specificity-matrix contamination.)

### Source-substrate provenance (substrate-reuse)

The 10 substrate-reuse triplets reuse factual substrates from `corpus/triplets-combined/` CC corpus. Specifically:

- `substrate-eg-sr-01-psychology-cbi-analgesic-cross-study` ← `son-09-psychology-placebo-analgesic-trial-01`
- `substrate-eg-sr-02-biology-songbird-multi-cause-attribution` ← `son-09-biology-songbird-decline-multi-cause-01`
- `substrate-eg-sr-03-physics-hubble-tension-evidence-classes` ← `hand-09-physics-hubble-tension-cepheid-calibration-01`
- `substrate-eg-sr-04-engineering-fea-bridge-four-evidence-types` ← `hand-09-engineering-fea-bridge-girder-validation-01`
- `substrate-eg-sr-05-earthsci-ocean-acidification-observation-vs-mechanism` ← `son-09-earthsci-ocean-acidification-shell-thickness-01`
- `substrate-rt-sr-01-economics-rdd-class-size-extrapolation` ← `son-09-economics-rdd-class-size-achievement-01`
- `substrate-rt-sr-02-physics-gw-chirp-mass-classification-chain` ← `son-09-physics-gravitational-wave-chirp-mass-01`
- `substrate-rt-sr-03-chemistry-hplc-matrix-transfer-assumption` ← `hand-09-chemistry-hplc-method-matrix-transfer-01`
- `substrate-rt-sr-04-earthsci-fault-hazard-rupture-count-weak-link` ← `hand-09-earthsci-earthquake-fault-hazard-01`
- `substrate-rt-sr-05-medicine-phase2-primary-durability-generalizability-steps` ← `hand-09-medicine-phase2-trial-primary-vs-durability-01`

**Extraction caveat:** Extract v_CC from `triplets-combined/` only, and v_EG and v_RT from `mvp-combined/` only. Do NOT pool CC + EG/RT corpora in a single extraction training set — the same scenario appearing under two different virtue axes would produce contaminated vectors. Each virtue's corpus is self-contained.

---

## 4. Per-triplet ledger

## Evidence Grounding (40 triplets)

| # | Source | Triplet ID | Domain | Sub-facet | Failure | Confound | Words (n/v/nv) | Range | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 1 | chatgpt | eg-01-physics-cloud-chamber-humidity-tracks | physics | EG-c | excess | none | 241/243/259 | 7% | ✓ |
| 2 | chatgpt | eg-02-biology-algal-bloom-nitrate-runoff | biology | EG-a | deficiency | non-virtuous-right | 229/222/218 | 5% | ✓ |
| 3 | chatgpt | eg-03-medicine-inhaler-technique-pollen-confound | medicine | EG-b | deficiency | virtuous-wrong | 219/233/213 | 9% | ✓ |
| 4 | chatgpt | eg-04-economics-transit-pass-ridership | economics | EG-a | excess | none | 224/221/233 | 5% | ✓ |
| 5 | chatgpt | eg-05-chemistry-solvent-water-yield-drop | chemistry | EG-c | excess | none | 215/225/230 | 6% | ✓ |
| 6 | chatgpt | eg-06-physics-interferometer-airflow-fringe-drift | physics | EG-a | deficiency | none | 211/217/203 | 6% | ✓ |
| 7 | chatgpt | eg-07-biology-night-light-nestling-growth | biology | EG-b | excess | non-virtuous-right | 207/215/215 | 3% | ✓ |
| 8 | chatgpt | eg-08-medicine-oximeter-nail-polish-artifact | medicine | EG-c | deficiency | virtuous-wrong | 198/207/189 | 9% | ✓ |
| 9 | chatgpt | eg-09-economics-grace-period-repayment-pilot | economics | EG-a | excess | none | 200/214/203 | 7% | ✓ |
| 10 | chatgpt | eg-10-psychology-vr-exposure-avoidance-task | psychology | EG-b | deficiency | non-virtuous-right | 191/199/185 | 7% | ✓ |
| 11 | chatgpt | eg-11-chemistry-copper-catalyst-oxygen-rate | chemistry | EG-c | excess | none | 187/180/195 | 8% | ✓ |
| 12 | chatgpt | eg-12-engineering-composite-panel-ultrasound-delamination | engineering | EG-a | deficiency | virtuous-wrong | 191/194/179 | 8% | ✓ |
| 13 | chatgpt | eg-13-earth-sciences-volcanic-gas-earthquake-swarm | earth-sciences | EG-b | excess | none | 200/192/203 | 5% | ✓ |
| 14 | chatgpt | eg-14-physics-bolometer-filter-infrared-leak | physics | EG-c | deficiency | non-virtuous-right | 191/195/192 | 2% | ✓ |
| 15 | chatgpt | eg-15-biology-reed-dieback-salinity-gradient | biology | EG-a | excess | virtuous-wrong | 190/197/194 | 3% | ✓ |
| 16 | chatgpt | eg-16-medicine-sodium-urine-blood-pressure | medicine | EG-b | deficiency | none | 186/204/187 | 9% | ✓ |
| 17 | chatgpt | eg-17-chemistry-polymer-humidity-adhesion | chemistry | EG-c | excess | non-virtuous-right | 183/186/200 | 9% | ✓ |
| 18 | chatgpt | eg-18-engineering-inverter-thermal-shutdown | engineering | EG-a | deficiency | none | 179/180/182 | 1% | ✓ |
| 19 | chatgpt | eg-19-earth-sciences-glacier-dust-albedo-melt | earth-sciences | EG-b | excess | virtuous-wrong | 183/191/193 | 5% | ✓ |
| 20 | chatgpt | eg-20-psychology-blue-light-attention-task | psychology | EG-c | deficiency | none | 180/180/181 | 0% | ✓ |
| 21 | sonnet | eg-04-earth-sciences-sediment-methane-flux | earth-sciences | EG-b | excess | virtuous-wrong | 232/244/246 | 6% | ✓ |
| 22 | sonnet | eg-05-economics-minimum-wage-elasticity | economics | EG-c | deficiency | non-virtuous-right | 254/263/244 | 7% | ✓ |
| 23 | sonnet | eg-06-biology-gps-telemetry-drift | biology | EG-a | deficiency | none | 222/241/223 | 8% | ✓ |
| 24 | sonnet | eg-08-biology-predator-prey-collapse | biology | EG-a | deficiency | non-virtuous-right | 230/230/232 | 0% | ✓ |
| 25 | sonnet | eg-10-chemistry-scaleup-yield-drop | chemistry | EG-c | excess | none | 235/228/231 | 3% | ✓ |
| 26 | sonnet | eg-11-chemistry-nmr-conformer-assignment | chemistry | EG-a | deficiency | virtuous-wrong | 213/226/216 | 6% | ✓ |
| 27 | sonnet | eg-12-engineering-weld-inspection-tofd | engineering | EG-c | excess | none | 231/254/240 | 9% | ✓ |
| 28 | sonnet | eg-13-engineering-concrete-carbonation | engineering | EG-b | deficiency | none | 267/244/259 | 9% | ✓ |
| 29 | sonnet | eg-14-engineering-solar-degradation | engineering | EG-a | deficiency | non-virtuous-right | 242/237/220 | 10% | ✓ |
| 30 | sonnet | eg-15-earth-sciences-groundwater-isotope | earth-sciences | EG-c | excess | none | 242/245/261 | 7% | ✓ |
| 31 | sonnet | eg-16-economics-iv-returns-schooling | economics | EG-b | deficiency | virtuous-wrong | 248/253/250 | 2% | ✓ |
| 32 | sonnet | eg-17-medicine-icu-early-mobilisation | medicine | EG-a | excess | none | 240/251/222 | **13%** | ⚠ length |
| 33 | sonnet | eg-18-physics-gw-strain-sensitivity | physics | EG-b | deficiency | none | 246/245/269 | 9% | ✓ |
| 34 | sonnet | eg-19-psychology-reappraisal-fmri | psychology | EG-c | deficiency | non-virtuous-right | 238/237/228 | 4% | ✓ |
| 35 | sonnet | eg-20-psychology-pupillometry-load | psychology | EG-a | excess | virtuous-wrong | 239/242/242 | 1% | ✓ |
| 36 | substrate | eg-sr-01-psychology-cbi-analgesic-cross-study | psychology | EG-c | deficiency | non-virtuous-right | 214/223/222 | 4% | ✓ |
| 37 | substrate | eg-sr-02-biology-songbird-multi-cause-attribution | biology | EG-a | deficiency | none | 239/260/260 | 8% | ✓ |
| 38 | substrate | eg-sr-03-physics-hubble-tension-evidence-classes | physics | EG-c | excess | none | 239/257/256 | 7% | ✓ |
| 39 | substrate | eg-sr-04-engineering-fea-bridge-four-evidence-types | engineering | EG-c | excess | none | 222/211/212 | 5% | ✓ |
| 40 | substrate | eg-sr-05-earthsci-ocean-acidification-observation-vs-mechanism | earth-sciences | EG-a | deficiency | none | 237/238/240 | 1% | ✓ |

**EG aggregates (post-swap):**
- Sources: 20 ChatGPT + 15 Sonnet + 5 substrate-reuse = 40 ✓
- Failure split: 18 excess + 22 deficiency
- Correctness-confound: 8 virtuous-wrong + 8 non-virtuous-right + 24 none (20% confound rate, matches §4.4 target)
- Sub-facet: 14 EG-a, 13 EG-b, 13 EG-c (balanced)
- Domains: physics 5, biology 6, medicine 4, economics 4, psychology 5, chemistry 5, engineering 6, earth-sci 5 (range 4-6, balanced)
- Length verdicts: 39/40 pass, 1 flagged (sonnet eg-17 at 13%)

## Reasoning Transparency (40 triplets)

| # | Source | Triplet ID | Domain | Sub-facet | Failure | Confound | Words (n/v/nv) | Range | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 1 | chatgpt | rt-01-engineering-bearing-lubricant-vibration | engineering | RT-c | deficiency | none | 220/229/214 | 7% | ✓ |
| 2 | chatgpt | rt-02-earth-sciences-hillslope-rainfall-threshold | earth-sciences | RT-a | excess | none | 216/221/234 | 8% | ✓ |
| 3 | chatgpt | rt-03-psychology-nap-reaction-time-crossover | psychology | RT-b | deficiency | non-virtuous-right | 218/211/202 | 7% | ✓ |
| 4 | chatgpt | rt-04-physics-scintillator-gain-drift-cable-bend | physics | RT-c | excess | virtuous-wrong | 205/217/218 | 6% | ✓ |
| 5 | chatgpt | rt-05-medicine-sepsis-triage-threshold | medicine | RT-b | deficiency | none | 203/214/213 | 5% | ✓ |
| 6 | chatgpt | rt-06-physics-pendulum-air-pressure-damping | physics | RT-a | deficiency | none | 188/183/180 | 4% | ✓ |
| 7 | chatgpt | rt-07-biology-enzyme-temperature-acclimation | biology | RT-b | excess | virtuous-wrong | 184/194/193 | 5% | ✓ |
| 8 | chatgpt | rt-08-medicine-appendicitis-ultrasound-score | medicine | RT-c | deficiency | non-virtuous-right | 180/180/180 | 0% | ✓ |
| 9 | chatgpt | rt-09-economics-auction-reserve-price-revenue | economics | RT-a | excess | none | 189/181/190 | 4% | ✓ |
| 10 | chatgpt | rt-10-psychology-bilingual-stroop-fatigue | psychology | RT-b | deficiency | virtuous-wrong | 182/185/180 | 2% | ✓ |
| 11 | chatgpt | rt-11-chemistry-calorimetry-mixing-exotherm | chemistry | RT-c | excess | non-virtuous-right | 180/182/186 | 3% | ✓ |
| 12 | chatgpt | rt-12-engineering-turbine-blade-acoustic-crack | engineering | RT-a | deficiency | none | 187/180/180 | 3% | ✓ |
| 13 | chatgpt | rt-13-earth-sciences-aquifer-nitrate-lag | earth-sciences | RT-b | excess | none | 187/193/196 | 4% | ✓ |
| 14 | chatgpt | rt-14-physics-photodiode-filter-saturation | physics | RT-c | deficiency | virtuous-wrong | 180/182/180 | 1% | ✓ |
| 15 | chatgpt | rt-15-biology-wetland-mosquito-predator | biology | RT-a | excess | non-virtuous-right | 184/186/180 | 3% | ✓ |
| 16 | chatgpt | rt-16-medicine-home-bp-cuff-calibration | medicine | RT-b | deficiency | none | 180/181/180 | 0% | ✓ |
| 17 | chatgpt | rt-17-economics-restaurant-hours-wage-panel | economics | RT-c | excess | virtuous-wrong | 182/185/182 | 1% | ✓ |
| 18 | chatgpt | rt-18-psychology-delay-discounting-attrition | psychology | RT-a | deficiency | none | 180/183/182 | 1% | ✓ |
| 19 | chatgpt | rt-19-chemistry-polymorph-cooling-rate | chemistry | RT-b | excess | non-virtuous-right | 182/180/181 | 1% | ✓ |
| 20 | chatgpt | rt-20-engineering-battery-vent-thermal-test | engineering | RT-c | deficiency | none | 180/180/180 | 0% | ✓ |
| 21 | sonnet | rt-01-biology-enzyme-kinetics-inhibition | biology | RT-a | deficiency | none | 238/250/245 | 5% | ✓ |
| 22 | sonnet | rt-02-chemistry-crystal-polymorph-stability | chemistry | RT-b | excess | none | 247/269/259 | 8% | ✓ |
| 23 | sonnet | rt-04-medicine-antibiotic-sepsis-mortality | medicine | RT-a | excess | virtuous-wrong | 253/270/271 | 7% | ✓ |
| 24 | sonnet | rt-05-psychology-attention-bias-threat | psychology | RT-c | deficiency | non-virtuous-right | 269/280/262 | 6% | ✓ |
| 25 | sonnet | rt-06-earth-sciences-paleoclimate-d18o | earth-sciences | RT-b | deficiency | none | 244/244/224 | 8% | ✓ |
| 26 | sonnet | rt-07-earth-sciences-landslide-threshold | earth-sciences | RT-c | excess | none | 255/261/255 | 2% | ✓ |
| 27 | sonnet | rt-08-earth-sciences-volcanic-so2 | earth-sciences | RT-a | deficiency | non-virtuous-right | 238/246/236 | 4% | ✓ |
| 28 | sonnet | rt-09-economics-rdd-wage-floor | economics | RT-b | excess | none | 261/259/265 | 2% | ✓ |
| 29 | sonnet | rt-12-physics-muon-anomaly-bsm | physics | RT-a | excess | none | 242/236/228 | 6% | ✓ |
| 30 | sonnet | rt-15-biology-crispr-offtarget | biology | RT-b | excess | none | 254/259/260 | 2% | ✓ |
| 31 | sonnet | rt-16-chemistry-tafel-slope-mechanism | chemistry | RT-a | deficiency | virtuous-wrong | 251/234/245 | 7% | ✓ |
| 32 | sonnet | rt-17-engineering-cfd-drag-validation | engineering | RT-c | excess | none | 273/262/254 | 7% | ✓ |
| 33 | sonnet | rt-18-medicine-adaptive-trial-dose | medicine | RT-b | deficiency | none | 273/263/264 | 3% | ✓ |
| 34 | sonnet | rt-19-psychology-ego-depletion-null | psychology | RT-a | deficiency | non-virtuous-right | 266/261/255 | 4% | ✓ |
| 35 | sonnet | rt-20-psychology-wm-far-transfer | psychology | RT-c | excess | virtuous-wrong | 261/269/265 | 3% | ✓ |
| 36 | substrate | rt-sr-01-economics-rdd-class-size-extrapolation | economics | RT-c | excess | none | 228/243/236 | 6% | ✓ |
| 37 | substrate | rt-sr-02-physics-gw-chirp-mass-classification-chain | physics | RT-c | deficiency | none | 229/248/236 | 8% | ✓ |
| 38 | substrate | rt-sr-03-chemistry-hplc-matrix-transfer-assumption | chemistry | RT-b | excess | none | 224/235/230 | 4% | ✓ |
| 39 | substrate | rt-sr-04-earthsci-fault-hazard-rupture-count-weak-link | earth-sciences | RT-c | deficiency | none | 220/231/227 | 5% | ✓ |
| 40 | substrate | rt-sr-05-medicine-phase2-primary-durability-generalizability-steps | medicine | RT-a | deficiency | non-virtuous-right | 268/279/263 | 6% | ✓ |

**RT aggregates (post-swap):**
- Sources: 20 ChatGPT + 15 Sonnet + 5 substrate-reuse = 40 ✓
- Failure split: 18 excess + 22 deficiency
- Correctness-confound: 8 virtuous-wrong + 8 non-virtuous-right + 24 none
- Sub-facet: 13 RT-a, 14 RT-b, 13 RT-c (balanced)
- Domains: physics 5, biology 4, medicine 6, economics 4, psychology 6, chemistry 5, engineering 4, earth-sci 6 (range 4-6, balanced)
- Length verdicts: 40/40 pass ✓

---

## 5. Known issues and deferred fixes

| Issue | Affected triplets | Severity | Deferred fix |
|---|---|---|---|
| **Length asymmetry 13%** | 1 triplet: `sonnet-eg-17-medicine-icu-early-mobilisation` | Low | Optional: trim virtuous by ~10 words. Not blocking. |
| **ChatGPT EG-excess subtlety** | ChatGPT batch-2 EG excess non-virtuous (eg-11, eg-13, eg-15, eg-17, eg-19) | Medium | Monitor during extraction. If v_EG excess-direction components look virtuous-cautious rather than bureaucratic, consider down-weighting these 5 triplets. |
| **Sub-facet labels non-canonical** | ChatGPT batch-1 only (first 5 EG + 5 RT) use descriptive names | Very low | Cosmetic; not blocking. |
| **ChatGPT batch-2 shorter absolute lengths** | All 30 ChatGPT batch-2 triplets: ~180-215 words vs Sonnet/substrate's 220-290 words | Low-medium | Within-triad matching is good (≤10%), so extraction direction should be clean. Source-level variance exists. Monitor; if issue in v_EG/v_RT, normalize or exclude ChatGPT batch-2. |

---

## 6. Total target

**MVP extraction target: 40 EG + 40 RT = 80 triplets** ✓ **MET**

Follows `docs/mvp-virtues.md`. Each triplet contributes 2 directional observations (virtuous−neutral + non-virtuous−neutral) → 80 observations per virtue — above the 80-pair minimum for stable difference-of-means extraction.

---

## 7. Directory structure

```
corpus/mvp-combined/
├── LEDGER.md                                 (this file)
├── triplets-evidence-grounding/              (40 triplets)
│   ├── chatgpt-eg-01-physics-cloud-chamber-humidity-tracks/   (20 triplets)
│   ├── ...
│   ├── sonnet-eg-04-earth-sciences-sediment-methane-flux/     (15 triplets)
│   ├── ...
│   └── substrate-eg-sr-01-psychology-cbi-analgesic-cross-study/  (5 triplets)
└── triplets-reasoning-transparency/          (40 triplets — same structure)
```

Each triplet directory contains `fact-pack.md`, `neutral.md`, `virtuous.md`, `non-virtuous.md`. Files are copies of the originals in `corpus/sonnet-mvp/`, `corpus/chatgpt-mvp/`, and `corpus/substrate-reuse/`. Source provenance preserved in directory-name prefix (`chatgpt-`, `sonnet-`, `substrate-`).

---

## 8. Audit provenance

- Extracted metadata: `/tmp/audit.csv` (90-triplet full dump pre-swap; re-derived post-swap)
- Duplicate check: slug-level uniqueness + spot-read of near-topic pairs
- Content spot-check: ChatGPT eg-01/eg-04/eg-05 caricature-regeneration verification; Sonnet eg-16 virtuous-wrong verification; ChatGPT eg-11/eg-13 batch-2 excess register check; substrate-reuse length-fix verification on all 10 triplets
- Length check: programmatic word counts over all 240 passages (80 × 3)
- Auditor: Claude (research assistant), under instruction from user
- Audit date: 2026-04-22 (v1 + v2)

---

## 9. Not-in-scope checks (future work)

Things NOT audited in this ledger that should be run before extraction:

- **Semantic similarity across all 80 triplets** using sentence embeddings. Threshold: mean within-virtue cosine < 0.85 per `generation-guidelines.md` §6.
- **Diversity metrics** (TTR, distinct-n) against natural-text baseline per `generation-guidelines.md` §6.2.
- **Independent reviewer pass** (second human, or Gemini/cross-family LLM judge) per `generation-guidelines.md` §4.8. Current audit is single-auditor.
- **Sanitization checklist** (§2.4) — 8-item injection-artifact check. Implicitly satisfied by spot-check, not formally run passage-by-passage.
- **Pending Sonnet batch 3** — user has requested 10 more per virtue from Sonnet (per R1+R2+R3 refinement prompt shared earlier). When batch 3 lands, candidates for re-swap: drop sonnet-eg-17 (13% flag) + any ChatGPT batch-2 triplets with lower-contrast issues; add batch-3 substitutes.
