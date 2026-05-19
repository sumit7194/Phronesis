# Next session queue — Phronesis tasks waiting on VM availability

VM is currently doing ludo RL training (started 2026-05-20 evening). Resume Phronesis work when VM frees up.

## Tier 1 — load-bearing for writeup framing (run before any writeup)

### Experiment: flipped-Δ at α=−25 on E2, n=50 sampled @ temp=0.7

**Why it matters**: The closing-validation chain found that flipped-Δ at α=−25 produces 55% hedge rate (n=20) vs baseline 14% (n=50) → +41pp distributional shift. This is the ONE positive empirical finding the prior literature (D-STEER, Pan et al., Pres et al.) doesn't predict. It's the only potential "centerpiece" of the writeup.

But: this project has caught 4 walkbacks where small-n effects collapsed at larger N. We **must** confirm at n=50 before making it load-bearing.

**Decision tree**:
- If n=50 lands at 50-60% hedge rate → original 55% holds, writeup has a positive centerpiece
- If n=50 lands at 25-30% → effect is real but smaller; still worth reporting but less central
- If n=50 lands at 14-20% → n=20 was variance, no positive centerpiece, writeup is purely methodological retrospective

**How to run**:

```python
# Mirror of seed_replication_e2_baseline.py but with flipped-Δ steering hook attached.
# d_flipped is at mvp/results/all_deltas/d_flipped.npy
# Use AdditiveSteeringHook(20, d_flipped, -25.0) on baseline Qwen2.5-7B-Instruct
# Generate 50 samples at temp=0.7, count hedge patterns matching the same regex used in closing_validation analysis
```

**Compute**: ~10-15 min on L4 (50 generations × ~10s each + model load)

**Output**: `mvp/results/all_deltas/flipped_alpha_neg25_n50.json` + hedge count summary

## Tier 2 — would strengthen post if Tier 1 holds

### Optional 1: flipped-Δ α=−25 on broader 18-prompt eval at n=20 each
If E2 result holds at n=50, test whether the +41pp generalizes to other contested-evidence prompts. ~30 min compute.

### Optional 2: turkey-tryptophan flipped-Δ α=−25
Closing validation showed v2-Δ α=+10 didn't correct turkey (it's just baseline's natural 25%). Does flipped-Δ at α=−25 do better? ~5 min.

### Optional 3: cross-layer flipped-Δ α=−25
We already have L20 (+41pp) and L15 v2-Δ α=+25 (+16pp). Does flipped-Δ at L15/L18/L22/L25 with α=−25 also produce shift? Maps the operative subspace across layers. ~15 min.

## Tier 3 — writeup, no compute needed

### Literature read before drafting
1. **D-STEER (arXiv:2512.11838)** — read Section 3 (extraction method) and Section 4.1 (spectral analysis). Confirm exact equivalence with F143 construction.
2. **Pan et al. 2025 (arXiv:2502.09674)** — read Section 4 (near-orthogonality with probe direction). Understand the dominant-vs-non-dominant framing.
3. **Pres et al. 2024 (arXiv:2410.17245)** — read Section 2 (desiderata) and Table 3 (myopia near-tie example). Internalize the methodology framing.

### Writeup decision (after literature read + Tier 1 result)

**Option A**: Workshop-paper-quality contribution, framed as field replication study extending three prior papers. Need Tier 1 result first to know if there's a positive centerpiece.

**Option B**: Project retrospective focused on the 4-walkback pattern as a process artifact. Less novel-finding, more methodological narrative.

**Option C**: Archive without writeup. The Phronesis docs (`findings.md`, `journal.md`, `day37-overnight-status.md`) are the public record; no LessWrong post needed.

Lean: A if flipped-Δ holds at n=50, B if it doesn't.

### Files to update before writeup

- `docs/writeup-plan.md` — rewrite reflecting prior-art landscape (currently has the pre-lit-review framing)
- `docs/findings.md` F142/F143/F145 already have prior-art hedges added 2026-05-20
- `docs/day37-overnight-status.md` has the full prior-art assessment in the THIRD ADDENDUM

## Not on queue (motivated continuation traps)

- More DPO configurations (already ruled out across rank 4/16/64 + SFT + flipped + multi-virtue)
- More decision-margin prompts (already n=18, 0/18 at distribution; more won't change picture)
- More layers without NLA validation
- More contrastive extraction methods (4 already tested: diff-of-means, AR-encoding, AR-diff, probe)

## How to resume

1. When VM is free, ssh to alphaludo-l4 (us-east1-c)
2. Verify Phronesis project still intact: `ls ~/phronesis_run/mvp/results/all_deltas/d_flipped.npy`
3. Run Tier 1 experiment (script template above)
4. Pull result, analyze, decide writeup direction
