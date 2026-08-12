# Consciousness & mind-attribution — master experiment doc

**The one place to look for this arc.** Results archive: `mvp/results/workspace/FINDINGS_mindedness.md`
(F-G … F-AS). Preregs: `prereg-mindedness-geometry.md`, `-facets.md`, `-v2.md`. Lit-check:
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

### Status per model  *(FINAL, 2026-08-11 — the cross-family programme is complete)*
| test | Q3-4B | Q3.5 | Q3.5-Base | Gemma4-I | OLMo2-I | OLMo2-Base | Q3-4B-Base | Gemma4-Base |
|---|---|---|---|---|---|---|---|---|
| gate / formats | raw x4 | raw x4 | raw x4 | chat x2 | chat+raw | raw x1 | raw x4 | raw x1 |
| entity spread | 0.56 | 0.41 | 0.48 | **0.73** | 0.39 | 0.37 | *0.33* | *0.27* |
| 1 sweep | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 2 factor | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 3 truth | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ |
| 4 steering | ✅ | ✅ | — | ✅ | ✅ | — | — | — |
| 5 forced | ✅ | ✅ | — | ✅ | ✅ | — | — | — |
| 6 speaker | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | ✅ |
| 7 subject | ✅ | ✅ | ✅ | ✅ | ⚠ degenerate | — | — | — |

*italic spread = below the 0.35 power criterion, excluded from claims. Dashes are not-run; each is
on a checkpoint that either fails the power criterion or duplicates a tested sibling.*

### THE ANSWER — 7 results, 3 families, 8 checkpoints
| result | families | verdict |
|---|---|---|
| Moral standing survives losing every mental capacity | **3** | **FINDING** |
| Forced-choice ordinal scale reproduces (rho ~0.87) | **3** | **FINDING** (a measurement) |
| Bare-text "I" reads as a human narrator | **3 + a base model** | **FINDING** |
| Protect-vs-blame axis, independent of mind | **3** | **FINDING** |
| Soul as a separate register | 1 of 3 | Qwen3-4B only |
| Subject-framing geometry | 2 Qwen; fails Gemma | Qwen only |
| Steering beats a random floor | 1 of 3 | Qwen3-4B only — others now **tested** negatives (F-AP/F-AQ) |
| Protect-vs-blame, **preregistered** | 3 of 3 on its key prediction | **FINDING** (F-AK/F-AN) |
| Protection rides on experience, blame on agency | 3 of 3 | corrects F-Y's own headline |
| **The steerable direction is pretrained** | Qwen3-4B base **and** instruct | **preregistered**, 4/4 resolved (F-AR) |

**Four of seven generalise.** The three that do not are the three that looked most striking on the
first model. Detail: F-AE, F-AF, F-AG, F-AJ.

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
| What replaced it (v2/v3 vectors beat random) | **Qwen3-4B-specific** — the vector is inert elsewhere (F-AJ) |
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

## OPEN QUESTIONS / NEXT  *(2026-08-11: items 1–3 of the previous list are now DONE)*
1. ~~Steering inert outside Qwen~~ → **DONE, F-AP/F-AQ.** 20-config search per model found where
   the vector does move them; at those configs it moves the matched control as hard or harder.
   Tested negatives, not untested cells.
2. ~~Prereg the protect-vs-blame axis~~ → **DONE, F-AK/F-AN.** Key prediction 3/3 families.
3. ~~Chat-format robustness~~ → **DONE, F-AL/F-AO.** Possible on Qwen3.5 only; Qwen3-4B scores
   0.012 against a 0.30 bar and genuinely cannot be measured in chat.

**Actually still open:**
4. **What the axis is made of.** The agency half (P3) replicates on 1 of 3. Only the experience
   half — protection tracking capacity to suffer — holds everywhere.
5. ~~Steering on base models~~ → **DONE, F-AR/F-AS.** Preregistered (4aea8da3), all four
   predictions resolved. Qwen3-4B-Base beats its random floor; at a matched config base +3.0 SD
   and instruct +2.8 SD with the same vector. Post-training amplifies ~2x, does not create.
   OLMo is negative at BOTH stages, so **the split is by family, not training stage**.
   Still open there: *why* Qwen and not the others — architecture or pretraining data — and
   Qwen3.5-4B-Base, dropped to keep the primary pair clean.
6. **Soul keeps misbehaving.** Failed cross-family 3×, then took 1st place the moment the format
   changed (F-AO). Not rehabilitated, not finished.

## OPS NOTES FOR THIS ARC
- A sweep peaks around **21GB RSS** on a 16GB machine — expect heavy swap. Do not run two model
  jobs at once.
- Guards must watch **swap AND disk**; a disk-pressure kill looks like an unexplained rc=137.
- Long runs: per-template checkpoints (sweep) and per-cell resume (steering). Verify the resume
  path loads, don't just verify the file exists.
- The MPS allocator grows across a long process regardless of `empty_cache()`; the fix is a fresh
  process every few units of work.
