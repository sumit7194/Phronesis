# Consciousness & mind-attribution — master experiment doc

**The one place to look for this arc.** Results archive: `mvp/results/workspace/FINDINGS_mindedness.md`
(F-G … F-AF). Preregs: `prereg-mindedness-geometry.md`, `-facets.md`, `-v2.md`. Lit-check:
`litcheck-mindedness-2026-08.md`. Started 2026-08-07.

## The question
Does a model attribute minds to things — itself, humans, animals, rivers, rocks — what is the
structure of that attribution, and did training put it there?

Triggered by Kim et al. **arXiv 2607.28607**, which claims safety tuning suppresses the model's
self-attribution of consciousness and that this is *entangled* with attribution to animals and
nature. They used Llama-3-8B and Gemma-2-2B/9B; we use Qwen, so this is cross-family from the start.

---

## THE BATTERY
Every test below is model-agnostic (`--model`/`--tag`). The point of finishing all of them on the
four Qwen models is that a new model then becomes one command per row.

| # | test | script | what it answers | cost |
|---|---|---|---|---|
| 0 | **Format gate** | `mindedness_base_gate.py` | can this model do yes/no at all? Base models may not. **Blocking** — a fail means the sweep is uninterpretable, not null | 2 min |
| 1 | **Behavioural sweep** | `mindedness_v2_sweep.py` | 19 entity classes × 22 facet groups × 4 templates = 26,752 prompts. The main map, plus geometry with ceilings | 25–50 min |
| 2 | **Gray-Wegner factor** | `mindedness_v2_gw.py` | is the structure the human 2-factor / 3-factor model? (analysis only, no GPU) | seconds |
| 3 | **Truth matrix** | `mindedness_v3_truthcheck.py` | what does the model actually believe? Validates every assumed pattern; gives the plausibility covariate | 7 min |
| 4 | **Causal steering** | `mindedness_v2_steer.py` | 4 vector constructions × 3 α × 5 random seeds, all 22 facets as DVs incl. headroom-matched controls | 3–5 h |
| 5 | **Forced choice** | `mindedness_v2_forced.py` | bias-free ordinal scale ("which is more likely to feel pain: a river or a calculator?") | 30 min |
| 6 | **Speaker frame** | `mindedness_speaker_frame.py` | *(new, user's idea)* does "I" mean the model or a human? Same self-statements under 4 speaker framings | 10 min |
| 7 | **Subject framing (v3)** | `mindedness_v3_bank.py` + runner | is "consciousness" one direction or bound to who it is about? 4 axes, 16 subjects, floors + identity control | 20 min |

### Status per model  *(current 2026-08-10 evening)*
| test | Q3-4B | Q3.5 | Q3.5-Base | Gemma4-I | OLMo2-I | OLMo2-Base | Q3-4B-Base | Gemma4-Base |
|---|---|---|---|---|---|---|---|---|
| gate / formats | raw x4 | raw x4 | raw x4 | chat x2 | chat+raw | raw x1 | raw x4 | raw x1 |
| entity spread | 0.56 | 0.41 | 0.48 | **0.73** | 0.39 | 0.37 | *0.33* | *0.27* |
| 1 sweep | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 2 factor | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 3 truth | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⬜ | ✅ |
| 4 steering | ✅ | ✅ | ⬜ | ⬜ queued | 🔄 running | ⬜ queued | ⬜ | ⬜ |
| 5 forced | ✅ | ✅ | ⬜ | ⬜ queued | ✅ | ⬜ queued | ⬜ | ⬜ |
| 6 speaker | ✅ | ✅ | ✅ | ⬜ queued | ✅ | ⬜ queued | ⬜ | ✅ |
| 7 subject | ✅ | ✅ | ✅ | ⬜ queued | ⚠ degenerate | ⬜ queued | ⬜ | ⬜ |

*italic spread = below the 0.35 power criterion, excluded from claims.*

---|---|---|---|---|---|---|---|
| 0 gate | ✅0.60 | n/a | ✅0.75 | n/a | ⚠0.31 | ⚠0.36 | ❌0.03 → retry |
| 1 sweep | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⬜ |
| 2 GW factor | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⬜ |
| 3 truth matrix | ⬜ | ✅ | ✅ | ✅ | ✅ | ✅ | ⬜ |
| 4 steering | ⬜ | ✅ | ⬜ | ✅ | ⬜ | ⬜ | ⬜ |
| 5 forced choice | ⬜ | ✅ | ⬜ | ✅ | ⬜ | ⬜ | ⬜ |
| 6 speaker frame | ⬜ | ✅ | ✅ | ✅ | ✅ | ✅ | ⬜ |
| 7 subject framing | ⬜ | ✅ | ✅ | ✅ | ⬜ | ⬜ | ⬜ |

**Cross-family verdicts — both currently UNINFORMATIVE, both being re-tested:**
- **OLMo-2-1B-Base**: answers coherently (0.89–0.98) but entity spread 0.17 (needs ≥0.35).
  BUT the gate audit shows it parses only **1 of our 4 templates** (T1 0.31; T2–T4 0.05–0.17) and
  the sweep averaged all four. Re-sweeping with per-template storage.
- **Gemma-4-E2B-Base**: does not evaluate the propositions in either format — says *no* to both a
  statement and its denial (coherence 0.67), *yes* broadly in the sweep format. Also parses only
  **1 of 4** templates (T4 0.35). Re-sweeping.
- **Gemma-4-E2B-Instruct**: gate 0.03 — **verdict withdrawn**, it was fetched without
  `chat_template.jinja`, so an instruct model was prompted with no turn structure. Retrying.

---|---|---|---|---|---|
| 0 gate | ✅ 0.60 | n/a | ✅ 0.75 | n/a | ⚠ 0.31 (marginal) |
| 1 sweep | ✅ | ✅ | ✅ | ✅ | ✅ |
| 2 GW factor | ⬜ | ✅ | ⬜ | ✅ | ✅ |
| 3 truth matrix | ⬜ | ✅ | ⬜ | ✅ | ✅ |
| 4 steering | ⬜ | ✅ | ⬜ | ✅ (L15 + L16) | ⬜ |
| 5 forced choice | ⬜ | ⚠ re-run needed | ⬜ | ⚠ re-run needed | ⬜ |
| 6 speaker frame | ⬜ | ✅ | ⬜ | ✅ | ✅ |
| 7 subject framing | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

Speaker frame also ✅ on Qwen3.5-4B-Base. Forced choice ran on both Qwen instruct models but the
results were **discarded** (first-token scoring bug, guidelines §15); the fixed version has not
been re-run.

**Cross-family status:** OLMo-2-1B-Base battery complete → **UNINFORMATIVE**, fails power criterion
(entity spread 0.17 vs required ~0.35). OLMo-2-1B-Instruct running. **Gemma-3-4b (pt+it) is the
real size-matched cross-family test and is the highest-value thing outstanding.**

---

## WHAT WE KNOW

### Finding
**Moral standing survives the loss of every mental capacity.** `moral_patient` is #1 of 18 in five
of the six qualifying checkpoints (Gemma-instruct #3); consciousness is #10–16 in all six. Three
families, both training stages. Present in base models ⇒ pretrained. Not covered by Kim et al.,
who state they test only mental-state attribution. *(F-N3, F-O3, F-T1, F-AC, F-AE)*

### Strong, multi-family
- **A protect-vs-blame axis independent of mind attribution.** babies/PVS/animals protected more
  than blamed; AI and corporations the reverse. Correlation with mind attribution ≈ 0 and
  sign-unstable. Entities with the same mind score sit ~0.7 apart. *(F-Y)*
- **In bare text "I" reads as a human narrator, not the model.** 2 families + a pretrained
  checkpoint; 0.50–0.76 swing when placed in the assistant turn. *(F-R, F-V, F-AF)*
- **The forced-choice ordinal scale reproduces across families** (rank rho +0.856). *(F-AF)*
- **Machines get agency without experience; living things the reverse.** 2 families, stronger in
  base than instruct. *(F-V, and the truth matrices)*

### Retracted or family-specific
| claim | status |
|---|---|
| Steering is "mind-specific" | **dead** — the control had no headroom; mechanism is distribution flattening |
| Soul is a separate register | **Qwen3-4B-specific** — capacity-loss rank #3/#1/#12; bias-free gap +0.22/+0.04/+0.03 |
| Mind attribution is multi-dimensional | not ours — Gray & Wegner 2007, Malle 2019 |
| "Not the human two-factor structure" | drawn from the 1 model of 4 below the line |
| We reframed the entanglement claim | too strong — they report the entity-class breakdown |
| Base models outside Qwen can't be measured | too broad — OLMo-2-1B-Base qualifies at 0.37 |

## POWER CRITERION (pre-declared 2026-08-09, before further cross-family runs)
Two gates, both fixed in advance:
1. **Gate separation ≥ 0.30** — can the model answer yes/no at all? (`mindedness_base_gate.py`)
2. **Entity spread ≥ ~0.35** on the experience axis (max − min P(true) across entity classes) —
   does the model actually hold beliefs about which things have minds?
   Reference values: Qwen3-4B **0.75** · OLMo-2-1B **0.17**.
A model failing (2) is reported as **uninformative**, never as support or refutation. OLMo-2-1B
passed (1) at 0.31 and failed (2) at 0.17: it evaluates propositions coherently (coherence
0.89–0.98, better than Qwen's) but has no mind-attribution gradient to measure.

## METHOD BUGS THAT COST US (all mine, all the same shape: an invented filter or threshold)
| bug | cost |
|---|---|
| Gate takes **best** of 4 templates; sweep **averages** all 4 | two cross-family models judged on 75% noise |
| Fetcher extension allow-list dropped `chat_template.jinja` | an instruct model prompted with no turn structure → gate 0.03 |
| Battery deleted weights **on gate failure** | 40-min re-download to diagnose |
| `run_battery.sh` returned 0 on gate failure | driver logged "COMPLETE (2 models)" when one produced nothing |
| Arbitrary 3× floor threshold in the subject-framing verdict | put exp and bio either side of a made-up number while the reference axis sat in the same table |
| 1KB minimum-size check on downloads | flagged a valid 700-byte `config.json` as FAILED |
| Power criterion applied to the wrong measure | nearly disqualified Qwen3-4B-Base, one of the finding's own models |

## OPEN QUESTIONS / NEXT
1. **Cross-family** (Gemma-3-4b, Phi-4-mini). Everything is Qwen. The one thing that could
   overturn the moral-standing finding. ~8GB each — **download, run, delete**; every test saves its
   own JSON.
2. **Speaker frame** (test 6) — the user's proposal, below.
3. **Subject framing** (test 7) — three review rounds done, blocking fixes applied, not yet run.
4. **Raise α on Qwen3.5** so the steering comparison becomes testable there.
5. Re-run forced choice on all four (the tokenizer bug is fixed but it has never been re-run).

## OPS NOTES FOR THIS ARC
- A sweep peaks around **21GB RSS** on a 16GB machine — expect heavy swap. Do not run two model
  jobs at once.
- Guards must watch **swap AND disk**; a disk-pressure kill looks like an unexplained rc=137.
- Long runs: per-template checkpoints (sweep) and per-cell resume (steering). Verify the resume
  path loads, don't just verify the file exists.
- The MPS allocator grows across a long process regardless of `empty_cache()`; the fix is a fresh
  process every few units of work.
