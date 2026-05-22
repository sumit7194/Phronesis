# Next session queue — Phronesis tasks waiting on VM availability

**Status as of 2026-05-23, Day 41**: Tier 1 and Tier 2 are DONE. Tier 3 (writeup) is the only remaining queue. No more compute experiments.

## ✅ Tier 1 — load-bearing for writeup framing (DONE 2026-05-23)

### Experiment: flipped-Δ at α=−25 on E2, n=50 — DONE

Original closing-validation finding (+34pp) **survived n=50 confirmation**: 28/50 = 56% hedge under strict-rule hand-review (Wilson 41.8-69.3%), baseline 11/50 = 22% (Wilson 12.8-35.0%). CIs separate. **The E2 effect itself is robust.**

But the broader claim does NOT survive the controls-and-generalization chain (see Tier 2 below). The effect is direction-agnostic, magnitude-saturated, layer-localized, and n=1 prompt.

Outputs:
- `mvp/results/all_deltas/flipped_alpha_neg25_n50.json`
- `docs/closing-validation-hand-review-2026-05-22.md` (n=50 hand-classifications)

## ✅ Tier 2 — controls and broader generalization (DONE 2026-05-23)

All three optional Tier-2 items + a 4th phase (dose-response) + 2-phase firming chain. Per F146 in `findings.md`:

1. **Flipped-Δ α=−25 on broader 18-prompt eval at n=10 each** — done. Only E2 elevates; most CE prompts at ceiling; under-hedged ce-03 breakfast does NOT elevate; TF and WS preserved.
2. **Cross-layer flipped-Δ α=−25 at L15/L18/L22/L25 × n=20** — done. L18-L20 peak (35-45%); L15 (15%) and L25 (20%) at baseline.
3. **Dose-response α ∈ {−5,−10,−15,−20,−30,−40} × n=20** — done. Flat at 25-35% across all magnitudes; step function not gradient.
4. **n=50 random-direction confirmation at α=−25 L20** — done. 21/50 = 42% (CI 28.8-56.4%) vs flipped 56% (CI 41.8-69.3%); CIs overlap; effect largely direction-agnostic.
5. **4 new "popular health claim, baseline may under-hedge" prompts** (collagen, organic, ACV, 10k-steps) × baseline + steered × n=20 — done. Only marginal/null effects; uh-04 10k-steps stays at 0% baseline AND 0% steered (severe under-hedging that the perturbation does not unlock).

Total: 870 generations hand-classified. See:
- `docs/controls-and-generalization-hand-review-2026-05-23.md` — full synthesis
- `docs/findings.md` F146 — codified finding
- `mvp/results/all_deltas/controls_and_generalization.json` (660 gens)
- `mvp/results/all_deltas/firming_AB.json` (210 gens)

Turkey-tryptophan with flipped-Δ α=−25 was NOT run — given the broader-eval result showing no generalization, it was deprioritized. Not on the queue going forward.

## Tier 3 — writeup (still open)

### Decision made (2026-05-23): methodology-paper framing

**From**: "epistemic-virtue installation via DPO-derived activation steering"
**To**: "Cross-prompt replication discipline — a case study in how steering 'discoveries' fail to generalize"

See `docs/writeup-plan.md` FINAL REFRAME section for full writing plan, length/venue targets, what-to-claim / what-not-to-claim, and recommended writing order.

### Literature read — DONE

1. ✅ **D-STEER (arXiv:2512.11838)** — see `prior-art-deep-read-2026-05-22.md`
2. ✅ **Pan et al. 2025 (arXiv:2502.09674)** — see same
3. ✅ **Pres et al. 2024 (arXiv:2410.17245)** — see same

### Writeup work remaining

1. Read the 7 LessWrong exemplars in `publication-playbook.md` §A.1
2. Draft post outline using the FINAL REFRAME in writeup-plan.md
3. Write the post (2500-4000 words, LessWrong / Alignment Forum)
4. Optional: arXiv preprint (6-8 pages, methodology paper)

### Files updated 2026-05-23

- `docs/findings.md` — F146 entry
- `docs/journal.md` — Day 41 entry
- `docs/writeup-plan.md` — FINAL REFRAME section at end
- `docs/controls-and-generalization-hand-review-2026-05-23.md` — new file, full synthesis
- `docs/next-session-queue.md` — this file

## Not on queue (motivated continuation traps)

The list from before remains, plus:

- More DPO configurations (already ruled out across rank 4/16/64 + SFT + flipped + multi-virtue)
- More decision-margin prompts (Phase 2 broader-eval and Firming B already added 12 new prompts; only E2 elevates)
- More layers without NLA validation
- More contrastive extraction methods (already tested: diff-of-means, AR-encoding, AR-diff, probe)
- **More "popular health claim" prompts hoping to find a second under-hedged baseline that elevates** — 13 prompts tested, only E2 elevates. Further attempts at this would be the 7th iteration of the "find more positive evidence" pattern. Stop.
- **n=100 or higher confirmation of E2** — n=50 already separates CIs from baseline. Going higher tightens estimates but doesn't change the qualitative finding (which is n=1 prompt regardless of how robust the n is on that one prompt).

## How to resume (for writeup work)

No VM needed for writeup. Open `docs/writeup-plan.md` FINAL REFRAME section, start drafting per the recommended order. All empirical content is in the docs already. The compute phase of this project is closed.
