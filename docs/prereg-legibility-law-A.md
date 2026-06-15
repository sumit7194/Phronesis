# Pre-registration — Experiment A: Legibility Law on a real LLM (in-context vs parametric)

*Locked before any activation was extracted. Imported hypothesis from the SpaceTime/curvature
project's "Legibility Law" (`~/Github/SpaceTime/writeups/legibility_law.md`). This is a
**hypothesis under test**, not a claim.*

## The transplanted prediction

The Legibility Law (toy result, ≤1M params): a per-object property *inferred by a shared encoder*
is **linearly decodable** (legible); the same property *stored as a free per-object embedding* is
**scrambled** (linearly unreadable, recoverable only nonlinearly). The diagnostic is a **probe
ladder**: linear-decode r = legibility; nonlinear-decode r = information presence; **scramble
signature = linear LOW + nonlinear HIGH**.

Transplant to an LLM, holding the decoded value distribution fixed and varying only the *route* the
information enters by:

- **parametric arm** (≈ free stored embedding): the model recalls a scalar it holds in weights.
- **in-context arm** (≈ amortized/shared encoder): the same scalar is supplied in the prompt and must
  be read out of context.

Model: **Qwen/Qwen3-4B** (fp16, MPS). Hidden size 2560, 36 layers. Probe at layers
{4,8,12,16,20,24,28,32,36}. Read position = **last token before the scalar would be emitted**
(raw-text completion prompts, no chat template — standard factual-probing setup; we read
representations on a forced sequence, we do not sample).

## Targets (3, as cross-checks)

| target | entities | scalar | transform | label-noise risk |
|---|---|---|---|---|
| atomic number | elements H–Xe (Z 1–54) | Z | identity | **none** (exact, model knows cold) — the clean flagship |
| birth year | ~40 very famous people | year | identity | small (a few years) |
| population | ~40 countries | millions | log10 | **high** — see confound below |

In-context arm uses nonce entities bound to the **same value set** as the real entities, so the
decoded-value distribution is identical across arms; only the route differs. 3 paraphrase templates
per entity; cross-validation is **GroupKFold by entity** so templates of one entity never split
across train/test (no phrasing leakage).

## Probe ladder

- **linear (legibility):** StandardScaler → RidgeCV; out-of-fold predictions; Pearson r vs true.
- **nonlinear (info presence):** StandardScaler → PCA(≤50) → kNN regressor; out-of-fold; Pearson r.
- **scramble gap** = nonlinear r − linear r (high gap = info present but illegible).
- **noise floor:** labels permuted within the cell → both r must collapse to ≈0.

## Predictions (locked)

**H1 (law transfers):** for the **atomic-number** target,
`max_layer linear_r(in-context) − max_layer linear_r(parametric) ≥ 0.15`, **and** the parametric
scramble gap > the in-context scramble gap. Replication expected on birth year (same direction).

**Power check (must pass or the test is inconclusive):** in-context linear_r ≥ 0.5 for at least one
layer — proves the harness can detect legibility when present. If even the in-context arm can't be
decoded, N is too small and we conclude nothing.

**Noise-floor check (must pass):** shuffled linear_r and nonlinear_r ≤ 0.10 in every cell.

**Falsification of transfer:** if atomic-number `linear_r(in-context) − linear_r(parametric) ≤ 0.05`
(parametric recall is just as linearly legible), the Legibility Law does **not** transfer to LLM
parametric memory. This would align with ROME / rank-one knowledge editing (facts are linearly
localizable) and is a fully reportable negative.

## Known confound (declared up front)

The **population** arm has an asymmetry: the in-context label is exact (the value is literally in the
prompt), while the parametric label is *my approximate reference table* scored against the model's
*approximate internal* value — so parametric carries label noise that in-context does not. This can
**inflate** the in-context advantage artificially. Therefore:

- Population is **supportive-only**, never confirmatory.
- **Atomic number is the confound-free adjudicator**: the model knows Z exactly and my labels are
  exact, so there is no label-noise asymmetry. If the in-context > parametric gap holds for atomic
  number, the law is supported; if it appears *only* for population, it is the confound, not the law.

## What we will report regardless of outcome

Full per-target, per-arm, per-layer table of (linear r, nonlinear r, gap), the floor, and the power
check — then a hand-read verdict against the locked thresholds above. Positive, null, or
confound-explained: all three get written to findings.md + journal.

## Next (Experiment B, after A)

Probe ladder on the model's *own knowledge boundary* ("will it answer this correctly"): scramble
signature → would explain F121 one-sidedness (can't install abstention via a linear push); a clean
linear signal (à la Kadavath et al.) → tension with F121, and a partial falsifier of the law's reach.
Designed after A's harness is validated.
