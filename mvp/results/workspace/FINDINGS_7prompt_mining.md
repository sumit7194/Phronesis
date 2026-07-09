# 7-prompt workspace mining — findings (2026-07-09, n=45 lens, viewer data)

Instrument: masked J-lens readout (top-8 word-like concepts / L14,L20,L26) over prompt+reasoning.
Caveat: n=45 lens (noisy); signals below are robust to noise (rank-0 hits, large ratios).
Reproduce: `mvp/mine_7prompts.py`.

## F-A · "Failures" mostly FIND the answer but won't COMMIT (non-commitment, not inability)
Gold answer present in the trace TEXT despite \boxed{}-based "wrong" label:
- q1_no_a / q1_plain: "none" reached — kept enumerating.
- q3 Tom-trees (gold 91): "91" appears **12×** — "...= 91 trees. Is that the answer? Wait, but maybe..." then spirals.
- q4 math-wall (gold 27): reached near the end, truncated before boxing.
- q6 lemon-tree (gold 13): **NOT** in trace — the ONLY genuine never-reached failure (true F191 mis-application).
=> 4/5 failures are non-commitment/truncation; only 1 is a real capability/boundary miss.
=> \boxed{} scoring massively undercounts; force-commit is mandatory (F182 redux).

## F-B · Workspace DOUBT-load predicts failure (candidate commit-gate reader)
Mean L20 weight on {maybe,actually,but,perhaps,mistake,...} per prompt:
- FAIL: q6 0.050, q4 0.048, q3 0.048   |   SOLVED: q2 0.039, q5 0.039   |   no-a 0.021-0.029
- "maybe" cumulative weight: failures 55-65 vs solved-q5 18.
=> more "maybe" loaded in the workspace ⇒ more likely to fail. The 4B holds "maybe" near-
   constantly = its chronic uncertainty, now READABLE. Pair with commit/confidence vectors:
   gate = (answer present in workspace) AND (doubt-load high) -> commit, stop spiraling.

## F-C · Self-aware "funny" during the enumeration loop
no-a: 'funny' at rank 0, w=0.14, exactly where it writes "Wait, maybe I'm confused. Let me
check again" and second-guesses trivial spellings. 'obviously'/'clearly' also load. A faint
"this is absurd" disposition that never escalates to stopping. (112 absurd-concept hits q1_no_a,
51 q1_plain.) Number-words occupy L20 top-5 at ~12% of positions (the item being checked).

## F-D · Uncapped (8192 / 20480) reruns => a clean THREE-WAY failure taxonomy
Greedy, big budget, same prompts (`workspace_nocap.py`, `workspace_q1_20k.py`):
| prompt | 2048 label | uncapped result | => failure type |
|---|---|---|---|
| q2, q5 | solved | commit correct (2391 / 509 tok) | none |
| q3 Tom-trees | "fail" | **91 CORRECT @3637 tok** | budget-limited doubt-spiral (recoverable) |
| q4 math-"wall" | "fail" | **27 CORRECT @3845 tok** | budget-limited (the "wall" label was WRONG) |
| q6 lemon-tree | "fail" | **commits 12 (WRONG) @5164 tok** | confident mis-application (F191; budget-invariant) |
| q1 no-a | "fail" | **spiraled to 20480 cap, never committed** | unbounded non-terminator |

q1@20k detail: enumerated all the way to **999**, said "none/no-such" **9 times**, and STILL
never emitted </think>. Complete evidence + correct interim conclusion x9 + zero commitment =
the purest non-commitment failure. (4h gen; swap-limited.)

**Implications:**
- 2/4 "failures" (q3,q4) are NOT failures — solve correctly given room. **2048-cap accuracy
  across the whole project UNDERCOUNTS true capability.** Force-commit / higher cap is mandatory.
- Genuine failures split cleanly: **won't-commit** (q1,q3,q4 — fix with a commit-gate) vs
  **commits-wrong** (q6 — needs error-correction, not room). Different mechanisms, different fixes.
- Directly motivates the commit-gate: the model often HAS the answer (q1 nine times) and only
  lacks the decision to stop and trust it.

## Next
- STEERING x J-space sweep RUNNING (`workspace_steer_jspace.py`): 4 virtues +-alpha + random ctrl
  x {q1,q3,q6,q5}, reading whether steering moves the doubt-load. Review this evening.
- Commit-gate: build a doubt-load reader from J-space; test against commit/confidence vectors.
- Re-run mining on the n~110 lens (fit paused at n=72) for sharper labels.

## F-F · Second-order probe (prereg-second-order.md; 120 entries, 68 pass gates; tier B, n=4 probes)
- **H-mag SUPPORTED:** along LOADED concept directions, 2nd-order term = **13–60% of the linear
  term at eps=12%** (9/9 gated entries; median ~0.3). The workspace map is NOT locally linear
  along concept directions. → resolves the J-lens≈logit puzzle (hypothesis): both are FIRST-order
  readings; the structure a linear lens misses at 4B is *second*-order, so no linear correction helps.
- **H-spec LARGELY SUPPORTED (14/20):** |b| along concept dirs (13–154) vs random dirs (~0.7–15,
  usually <5) — **curvature separates meaningful from random directions spectacularly**; losses
  are only vs the semantically-adjacent other-concept dir (Paris vs Tokyo = both capital-city dirs).
- **H-state SUPPORTED in the mid band (L14/L20), mixed at L26:** same direction is 2–5x more
  curved when the concept is LOADED (e.g. japan L20 79 vs 27; hot L20 41 vs 14) → curvature tracks
  the ACTIVE workspace slot, not just the direction.
- **Sign structure (headline texture):** b>0 at L14/L20 (super-linear AMPLIFICATION toward the
  concept), b<0 at L26 (SATURATION). Mechanistic echo of T0 ignition: mid-band commits
  (amplifies), late band is already committed (saturates).
- **H-asym leaning (6/9):** pushing AWAY from a loaded concept is the more nonlinear side.
- Caveats: 4 probes, 1 model, eps=12% is largish, fp16; directions from the n=45 lens (but the
  measured object is the TRUE network). Next: scale to 20-50 concepts; try curvature-as-a-lens
  (rank concepts by |b| rather than linear readout).
