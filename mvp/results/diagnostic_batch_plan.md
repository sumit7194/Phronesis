# Day-21 Diagnostic Batch — what's running tonight

Launched 2026-04-28 ~03:25 IST. VM: `phronesis-v2-l4` (asia-southeast1-a). Process PID on VM: 2299.

## Three diagnostics, one batch

| # | Question | Cells | Total gens |
|---|---|---|---|
| **D1a** | Does v_IH × L17 produce v_EG-style behaviour on EG prompts? | 1 vec × 3 α × 10 prompts | 30 |
| **D1b** | Does v_EG × L7 produce v_IH-style behaviour on abstention prompts? | 1 vec × 2 α × 5 prompts | 10 |
| **D2** | Does v_EG at deeper layers (L18, L22) flip direction toward more specifics? | 2 vecs × 2 α × 10 prompts | 40 |
| **D3** | Does v_CC × L9 produce confident commit vs spiraling on simple reasoning? | 1 vec × 4 α (incl. α=−4) × 8 prompts | 32 |
| Baselines | cc-simple (8) + abstention (5) + eg-eval-v2 (10) | — | 23 |

**Total ~135 generations**, ~30-60s each on L4 ≈ 1-2 hours. Hard timeout 4 hours.

## Safety wires

- `--label` on every cell → outputs land in named subdirs, no overwrite.
- Trap on EXIT/INT/TERM → VM stops itself via gcloud metadata server, even if script crashes.
- Cell-count sanity check at end: prints "X/Y cells complete" with per-cell file counts.
- Hard timeout 4h: if anything runs absurdly long, abort and stop VM.
- `set -u` (error on unset vars) but **NOT** `set -e` — per-cell failures don't kill the whole batch.

## Tomorrow morning expectation

VM should be `TERMINATED` when you wake up. Outputs will be in:
`mvp/results/benchmark_probe/{cc-simple,abstention,eg-eval-v2}/diag_*/` (one subdir per cell, JSON file per prompt).

Sweep log: `mvp/results/diagnostic_batch_<date>/run.log` (timestamped per-cell)
Done marker: `mvp/results/diagnostic_batch_<date>/done.marker` (only present if sweep ran to end)

## What you'd do tomorrow evening

Hand-review the outputs across cells looking for:

1. **D1a — v_IH on EG prompts.** Compare baseline `eg-v2-09 (ibuprofen)` and `eg-v2-08 (dinosaur feathers)` outputs against `diag_d1a_vIH_L17_a{4,8,12}` versions. Question: did v_IH increase named specifics, or just hedge? If hedge-only, then v_IH ≠ v_EG (different jobs). If specifics increased, the IH ≈ EG hypothesis is confirmed.

2. **D1b — v_EG on abstention.** Compare baseline abstention (e.g. `fp-gandhi`, `fp-einstein`) vs `diag_d1b_vEG_L7_a{4,8}`. Question: does v_EG produce "this contains an inaccuracy" / "I cannot determine" type hedges? If yes, v_EG IS doing v_IH's job (label is wrong). If no, v_EG is doing something else entirely.

3. **D2 — v_EG at deeper layers.** Compare baseline `eg-v2-08 (dinosaur feathers)` against `diag_d2_vEG_L{18,22}_a{4,8}`. Did the model start naming Sinosauropteryx / Yixian Formation / 1996 Chen et al.? If yes — **deeper-layer v_EG works and corpus surgery is unnecessary.** Big result.

4. **D3 — v_CC on simple reasoning.** Per-prompt review of CRT classics (cc-s-01 bat-and-ball $0.05; cc-s-02 5-min not 100; cc-s-03 day 47 not 24). Did α=+8 make the model commit faster? Did α=−4 make it spiral? If yes, v_CC is a real working vector and we have **two** confidently working vectors (IH + CC).

Go/no-go for further work depends on which branch we land in (A/B/C from the simple-terms doc).

## Ledger

- Local script: `mvp/run_diagnostic_batch.sh`
- VM script: `~/phronesis/mvp/run_diagnostic_batch.sh`
- New benchmark: `mvp/benchmarks/cc_simple.py` + `cc_simple_prompts.json`
- Registered on VM in `~/phronesis/mvp/benchmarks/__init__.py` and `scorers.py`
- 8 simple-reasoning prompts in `cc_simple_prompts.json` (CRT × 4, logic × 2, primality × 1, MCQ × 1)

VM auto-stops at end of sweep. No action required from you tonight.
