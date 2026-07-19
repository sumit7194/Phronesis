# J-space injection — method reference (from the workspace paper)

Source: "Verbalizable Representations Form a Global Workspace in Language Models"
(transformer-circuits.pub/2026/workspace). Extracted 2026-07-08 for the incubation experiment.

## The residual stream (what we inject into)
A transformer processes text as a stack of layers. At each layer, every token position holds
a vector of numbers (~2560 numbers wide on Qwen3-4B) called the **residual stream** `h`. That
vector is the model's working state at that point — "what it's currently thinking about here."
Injection = we reach in and add a chosen direction to that vector, biasing the state.

## The injection formula (theirs and ours)
    h  ←  h + α · v_t
- `v_t` = the **J-lens vector** for a target token `t` (e.g. "none"): the direction in
  residual space that, transported to the output, points at that word. (rows of `W_U J_l`.)
- `α` = strength scalar. They report a **"double strength" swap = α·2**, so their working
  strengths are small (~1–2) when `v_t` is scaled to the layer's mean residual norm.
- Applied "at every token position across a band of intermediate layers" (their workspace
  band ≈ L38–92 on Sonnet; our analogue on the 36-layer 4B ≈ L10–28).
- Components of `h` orthogonal to `v_t` are left unchanged (it's a nudge, not a replacement).

## Two variants
- **Additive steering:** `h ← h + α·v_t` (what we're doing for the 'none' hint).
- **Swap / patching:** read lens coordinates `c = V†h`, then `h ← h + V(σ(c) − c)` where σ
  swaps a source and target coordinate — replaces "France" with "China" while leaving the rest
  of `h` intact. Negative α, or projecting out `v_t`, gives **ablation** (erase the concept).

## Timing — the key detail for incubation (matches our RUN3 fix)
Their introspection experiment injects **on the user (prompt) turn**, and they explicitly note
that injecting on the user turn "does not cause the model to output the word … at earlier
positions on the Assistant turn" — the concept is loaded while the model *reads*, and its
effect shows up in how the model *then answers*. That is exactly the incubation setup:
**inject during the question, release during the answer, watch whether the answer changes.**

Our RUN1/RUN2 mistake: we added `v_t` at *every generated token too*, at 4–20× the residual
norm → the model just repeated the injected word (output clamp, not a nudge). RUN3 gates the
hook to prompt positions only (seq_len > 1) so the model reasons freely from a seeded state.

## Controls we keep (our guidelines, stricter than the paper's demo)
- baseline (α=0) must fail; matched-norm **random vector, ≥3 seeds** must NOT reproduce the
  effect; α-sweep to find the nudge window below the output-clamp regime.

## Caveat for us
The paper's lenses used ~1000 prompts on Claude-scale models. Ours is n=20 on a 4B and tested
≈ random on the causal swap QC. So a null injection result may mean "lens too weak," not
"injection doesn't work" — hence the pending lens top-up gates the strong conclusions.
