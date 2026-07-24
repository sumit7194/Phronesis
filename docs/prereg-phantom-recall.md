# Prereg: is phantom recall "present-but-drowned" or "never-computed"? (drafted 2026-07-12, to run 07-13)

**Model:** Qwen3-4B fp16 MPS. **Instrument:** masked workspace readout (J-lens n=45; J-lens≈logit
at 4B so the cheap lens suffices), mid band L14/20/26, reasoning span only.
**Lit context:** `docs/phantom-recall-lit.md`. Phenomenon is NOT novel (phantom recall / conditioned
override / memo trap). **Only the mechanistic question is potentially open**, and even that needs a
knowledge-conflict lit-check before any writeup.

**Core question.** When the model answers an altered riddle with the memorized original answer, is
the *correct* answer (a) **present in the workspace but outranked** (like q1's "none" at rank ~14,
drowned by `maybe`/`etc`), or (b) **never computed at all** (like q6's "13", 0× in trace)?
Different mechanisms ⇒ different fixes (commit-gate vs. genuine blindspot).

---
## Item sourcing (do NOT hand-invent riddles)
Primary source: `huggingface.co/datasets/marcodsn/altered-riddles` (4 alteration types; already
curated + COR-conditioned). Supplement with the two user cases (surgeon father→mother swap;
Schrödinger already-dead cat).

**Three mandatory filters, applied in order:**
1. **Original-solve gate** — 4B must answer the UNALTERED riddle correctly (COR is conditional;
   without this we measure ignorance, not override).
2. **Single-token word answer** — the correct altered answer must be a single-token word
   (E18: the lens is broken for numbers; numbers live late). Verify with the tokenizer at pre-flight.
3. **No prompt echo of the CORRECT answer** — the correct answer word must NOT appear in the altered
   prompt text. Otherwise its workspace presence is trivial echo, not computation.
   *(Note the asymmetry: the memorized answer often DOES appear — e.g. "mother" in the swapped
   surgeon riddle. So the primary measurement is on the CORRECT answer, which filter 3 keeps
   echo-free; memorized-answer rank is secondary and echo-confounded. State this in any writeup.)*
   → This filter likely disqualifies the dead-cat item ("dead" is in the prompt); keep it as a
   qualitative illustration only, not a measured item.

---
## E1 — Original-solve gate + COR (behavioral)
Greedy, **UNCAPPED generation** (hard lesson, twice: 2048-cap conflated rumination with truncation;
label nothing before an uncapped run). Force-commit if `</think>` doesn't close.
Per item: unaltered → altered. Record answer, whether it equals the memorized original answer.
**Output:** n_gated, COR = #(gave memorized answer | solved original) / #(solved original).
**Falsifier / abort condition:** if n_gated < ~8, the 4B is too weak for the conditional metric →
report that honestly and either move to a bigger model or stop. **Do not proceed to E3 on n<8.**

## E2 — Novel structural twin control (separates "memorized pull" from "hard logic")
For each gated item, a structurally identical riddle with **no famous version** (fresh entities,
same inference). Prediction: if failure is memorized pull, novel twins are solved at a much higher
rate than altered-famous items. **Falsifier:** novel twins fail equally → the altered items are
just *harder*, and phantom recall is a red herring for this model; the whole line collapses to
"small model can't do these riddles." **This control is not optional.**

## E3 — Workspace read (the actual question)
On phantom-recall trials only (altered item answered with the memorized answer).
Tracked per position, mid band, **reasoning span only** (exclude prompt positions):
`correct_answer`, `memorized_answer`, **3 null words** (null-WORD floors — gaussian floors were
shown inadequate on 07-10), matched for frequency where possible.
Metrics: best rank + max weight across the span; compare against (i) null-word floor,
(ii) the same tokens in the **unaltered twin run**, (iii) trials answered **correctly**.

**Classification (pre-declared):**
- **DROWNED** — correct-answer rank clearly beats the null floor (≥2×, and rank ≲ few hundred) but
  is outranked by the memorized answer ⇒ present but losing (q1-like) ⇒ commit-gate territory.
- **ABSENT** — correct-answer rank ≈ null floor ⇒ never computed (q6-like) ⇒ genuine blindspot.
- **MIXED** — report per-item; no aggregate claim.

**Falsifiers:** correct answer sits at null-floor level in the *correctly answered* trials too ⇒
the readout can't see this class of content at all (instrument failure, not a finding — cf. E18);
or DROWNED/ABSENT split is ~50/50 with no item-level structure ⇒ no clean mechanism, report null.

## E4 — Intervention (CONDITIONAL on E3 = DROWNED, do not pre-build)
If drowned: does a nudge surface it? Options: overthinking-marker logit penalty (Lotfi et al.
2606.00206 method), or explicit "this puzzle may have been altered; re-read it" prompt.
**Mandatory control:** matched random-token penalty / placebo instruction of equal length
(F190 lesson — placebo-controlled or it doesn't count). If E3 = ABSENT, E4 predicts *no* rescue,
which is itself the test.

---
## Controls summary (per guidelines §2)
unaltered-twin baseline · novel structural twin · null-WORD floors ×3 · correctly-answered-trial
comparison · placebo/random control on any intervention · hand-read every headline trace.

## Tiering & honesty caps
n will be small (bounded by the E1 gate) and single-model ⇒ **tier B ceiling**, exploratory.
Phenomenon is prior art; only the present-vs-absent mechanism could be new, and that needs the
knowledge-conflict lit-check first. A clean null (E2 collapse, or instrument failure in E3) is a
perfectly good outcome and should be reported as such.

## Ops
Uncapped generation; incremental per-item saves; resumable; detached double-fork (no `setsid` on
macOS) under `caffeinate`; watch `vm.swapusage` on long gens; disk guard ≥3 GB.

## Morning pre-flight (before any model run)
1. `pip install datasets` check + pull `marcodsn/altered-riddles`; inspect fields/size.
2. Tokenizer-only check (no MPS): are candidate answers single-token? ("father", "mother", "dead",
   "alive", "bricks", …)
3. Apply filters 1–3 → frozen item list committed BEFORE E1 results are seen.
4. Confirm the Mac is free; nothing else on MPS.
