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

## Next (needs model; pending fit)
- No-thinking-cap rerun of all 7: how deep does the spiral go before commit? (measure tokens-to-commit)
- Re-run this mining on the n~110 lens (overnight) for sharper labels.
- Commit-gate: build a doubt-load reader from J-space; test against commit/confidence vectors.
