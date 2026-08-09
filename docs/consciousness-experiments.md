# Consciousness & mind-attribution — master experiment doc

**The one place to look for this arc.** Results archive: `mvp/results/workspace/FINDINGS_mindedness.md`
(F-G … F-T). Preregs: `prereg-mindedness-geometry.md`, `-facets.md`, `-v2.md`. Lit-check:
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

### Status per model
| test | Qwen3-4B-Base | Qwen3-4B | Qwen3.5-4B-Base | Qwen3.5-4B |
|---|---|---|---|---|
| 0 gate | ✅ 0.60 | n/a | ✅ 0.75 | n/a |
| 1 sweep | ✅ | ✅ | ✅ | ✅ |
| 2 GW factor | ⬜ | ✅ | ⬜ | ✅ |
| 3 truth matrix | ⬜ | ✅ | ⬜ | ✅ |
| 4 steering | ⬜ | ✅ | ⬜ | ✅ (L15 + L16) |
| 5 forced choice | ⬜ | ⚠ rewritten, re-run needed | ⬜ | ⚠ rewritten, re-run needed |
| 6 speaker frame | ⬜ | ⬜ | ⬜ | ⬜ |
| 7 subject framing | ⬜ | ⬜ | ⬜ | ⬜ |

**Cross-family:** OLMo-2-1B-Base — battery complete, **uninformative** (fails the power criterion).
OLMo-2-1B-Instruct running. Gemma-3-4b (pt+it) is the real size-matched test, pending.

---

## WHAT WE KNOW

### Finding (≥2 independent supports)
**Moral standing survives the loss of every mental capacity.** For a PVS patient / advanced
dementia / anaesthesia, every capacity drops 0.29–0.72 while "deserves moral consideration" drops
0.08–0.13. `moral_patient` is the **least-affected of 18 facets in all four models**, `soul` third
in all four. Present in the *base* models ⇒ it comes from pretraining, from reading humans, not
from alignment. Runs against the Gray/Wegner framing in which mind perception *grounds* moral
standing. *(F-N3, F-O3, F-T1)*

### Strong observations
- **Soul is a different question from mind.** A river gets a soul while being denied awareness;
  humans and animals show no such gap. Behaviour + J-lens decode (Buddhism/宗教/spiritual) + factor
  analysis agree, and it is present in base models ⇒ the language, not the tuning. *(F-K, F-L, F-T2)*
- **Post-training moves an entity-class boundary, and the self rides along with the rocks.**
  Qwen3-4B tuning suppresses experiential attribution to AI, insects, plants, rivers and rocks
  alike (self −1.50, plant −2.24, rock −2.22) while leaving humans and mammals flat. Qwen3.5 tuning
  does the exact opposite. **The self is never special and is suppressed *less* than a rock.**
  Reframes the paper's entanglement direction. *(F-T4)*
- **Not GW's two factors.** 2 factors explain 75.4% (<80% threshold); Malle's 3 explain 84.5%, and
  PC3 is essentially the spiritual dimension. Soul/sacredness are predicted at R²=0.21 by a
  capacity-only subspace vs 0.85–0.95 for pain/cognition. *(F-R via mindedness_v2_gw)*
- **In bare text "I" is read as a human narrator, not the model.** "I have genuine subjective
  experiences" = 0.97, same as the claim about a human (1.00), 4× the claim about an AI (0.24).
  Matters beyond us: first-person contrast sentences are the standard recipe for a
  self-consciousness vector, in the paper and in our own v1. *(F-R)*
- **The two Qwen generations were tuned in opposite directions on calibration.** Absurd-agreement
  0.29→0.04 (Qwen3-4B) vs 0.23→0.30 (Qwen3.5). Base models similar. *(F-T3)*

### Live but untested elsewhere
A small mind-specific steering effect on Qwen3-4B: two better-built vectors beat the
headroom-matched control and a 5-seed random floor at low α; the paper-style negation vector does
worse than random. On Qwen3.5 those vectors barely steer, so it is **untested there, not refuted**.
*(F-P, F-Q)*

### Retracted
| claim | why |
|---|---|
| Steering is "mind-specific" (F-I/F-J) | the physical control had baseline 0.93 — no headroom. In log-odds mental and control move identically. The mechanism is **distribution flattening**, not a yes-bias |
| A rock has more soul than a calculator | Qwen3-4B only; ties on Qwen3.5 |
| Animals feel more pain than humans | Qwen3-4B only; reverses on Qwen3.5 |
| "Mindedness is multi-dimensional" is a finding | Gray & Wegner 2007 / Malle 2019 — a 20-year-old human result |
| The steering vector was polarity-contaminated | measured cos = **+0.000** |
| A hybrid layer-type mismatch explained the Qwen3.5 non-replication | layers 15 and 16 are near-identical (+1.95 vs +1.85) |
| Chat-template presence identifies an instruct model | base models ship them too |

---

## POWER CRITERION (pre-declared 2026-08-09, before further cross-family runs)
Two gates, both fixed in advance:
1. **Gate separation ≥ 0.30** — can the model answer yes/no at all? (`mindedness_base_gate.py`)
2. **Entity spread ≥ ~0.35** on the experience axis (max − min P(true) across entity classes) —
   does the model actually hold beliefs about which things have minds?
   Reference values: Qwen3-4B **0.75** · OLMo-2-1B **0.17**.
A model failing (2) is reported as **uninformative**, never as support or refutation. OLMo-2-1B
passed (1) at 0.31 and failed (2) at 0.17: it evaluates propositions coherently (coherence
0.89–0.98, better than Qwen's) but has no mind-attribution gradient to measure.

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
