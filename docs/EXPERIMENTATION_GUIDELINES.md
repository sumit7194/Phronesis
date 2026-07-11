# Phronesis — Experimentation Guidelines (the methodological floor)

**Status:** living document · **v1.0** · 2026-06-28 · *correctness over speed, always.*

> **Prime directive.** Every result must be one we'd still believe after an adversary tried to break it. We do not trade rigor for speed. This document is the **floor** — experiments may exceed it but never drop below it — and it is **versioned and improved**: each hard lesson adds or sharpens a rule (see changelog). When in doubt, run the extra control.

Each rule below cites the failure that earned it. If you're about to skip one, write down why, in the prereg.

---

## §1 — Before you run: pre-register
- **Write the hypothesis, the prediction, and the falsifier** in `docs/prereg-<name>.md` *before* generating data. State **what result would change our mind.** (We have a prereg habit — keep it.)
- **Define the measurement to match the claim you want to make.** If the claim is "reasoning helps recall," the metric is pass@k with sampling — *not* pass@1 greedy. (F169/F170 were retracted because we measured pass@1 greedy and compared to Google's pass@k. *Same model + same dataset ≠ same measurement.*)
- **Name the controls up front** (see §2). If an effect needs a control to be meaningful, the control is part of the experiment, not an optional follow-up.

## §2 — Controls are mandatory, not optional
- **Multi-seed random control for ANY steering / direction / intervention claim.** Minimum **≥2, prefer 3 seeds**, magnitude-matched. A single seed repeatedly *false-certified specificity* (F122 single-seed; F160 seed-42 "win" that seed-99 reproduced; F171 v3 "win" that random matched). **If a magnitude-matched random vector does the same thing, the effect is not yours.**
- **Baseline (α=0 / no-intervention) every time**, on the same items, same decoding.
- **Sign / negative control** where applicable (e.g. −α should do the opposite; flipped-direction should fail).
- **The one-line test:** *"Would a random perturbation of the same size produce this?"* If you haven't checked, you don't have a result.

## §3 — Ground truth & labeling
- **Hand-read is the label; regex/keyword/auto is a *prefilter* only** (`auto_` prefix). Auto-scoring has burned us twice (the empty-string match that faked a 13%→70% "replication"; regex creeping back into "manual" verification). The AI hand-read under a consistent rubric is the truth.
- **Anchor correctness on real ground truth.** Do **not** infer correctness from a confidence/uncertainty signal: **systematic confident-wrong errors are invisible to *all* consistency/uncertainty methods** (semantic entropy included — *Nature* 2024 authors say so). Only ground truth separates *confident-correct* from *confident-confabulation*.
- **Score the construct, not the surface.** For humility/calibration: score *evidence-keyed differentiation*, not hedge-word density (self-reported "humble language" dissociates from real calibration — the metacognitive-blindspot literature; mirrors our probe≠valid-vector rule).
- **Rubric written down, applied identically** to every arm (steered, baseline, control). One rubric, one reader-standard.

## §4 — Measurement integrity
- **Greedy for causal reads, sampling for distributional/competence questions** — and say which and why. Greedy isolates the intervention (deterministic → α is the only variable); sampling/pass@k measures what's *reachable*. Don't use one to claim the other.
- **Multiple decoding runs are the standard, not a luxury** (see §7).
- **Calibrate parameters to the model's scale — never assume-transfer.** The 4B's working α (~16) was ~2% of the 32B's residual-stream norm (~918) → inert. **Measure the relevant scale (norm, layer depth) per model and set parameters relative to it.** (F171.)
- **Probe accuracy ≠ a valid/usable vector.** A direction can be 98–100% *readable* and still un-*writable* (legibility ≠ steerability — F166/F168/F171). Always check separation **sign**, cosine-diff **sign**, cross-corpus alignment, AND the behavioural effect — not just decode accuracy.

## §5 — Calibrate confidence in our *own* results
- **Tier every claim:** **(A) controlled** (survived multi-seed + ground truth) · **(B) suggestive** (real but not fully controlled) · **(C) hypothesis** (fits the data, untested). State the tier in the finding.
- **Do not over-read uncontrolled data.** The v3 "first positive steering result" was called twice before the random control deflated it. **Apparent positives from uncontrolled runs are tier-C until the control lands.** Weight controls heavily.
- **Retract cleanly and visibly** when a control overturns a claim (F169/F170/F171 corrections kept on the record with reasons). A retracted finding is a *good* finding.
- **Distinguish "we found X" from "X is true."** In this field very little is settled; the controlled nulls are our most trustworthy outputs.

## §6 — Reproducibility & data hygiene
- **Save RAW generations + reasoning traces, not just parsed results.** A 2-hour run was lost because only the post-parsed result was saved; a parsing bug then meant re-running from scratch. Save everything; parse later.
- **Seed everything** that's sampled; record seeds. Determinism where a causal read needs it.
- **Version the data and the harness** alongside the result (commit the eval set, the vectors, the harness, the raw output together).
- **One commit per coherent result**, message states what was found, the tier, and the control status.

## §7 — Multiple-runs standard (the "proper result" rule)
For any generation-based measurement, the default battery is **more than one run**:
- **Greedy (T=0)** — the causal/modal answer.
- **Sampled (T≈0.6–0.7), k samples** — for competence (pass@k = is the answer *reachable*?) and for semantic-entropy-style uncertainty.
- **Temperature variants** where the question is decoding-sensitive.
- Accept that proper measurement means **many generation runs**; budget for it. *However long it takes — correctness over speed.*

## §8 — Ops & infrastructure discipline
- **Verify a kill actually freed the GPU (procs=0, GPU mem≈0) BEFORE relaunching.** Two 32B loads raced one L4 and OOM'd because a relaunch fired into an occupied GPU.
- **Launch long VM jobs via `setsid` + a self-redirecting script**, never a bare `nohup &` in an SSH command — transient SSH/IAP drops silently swallow the launch and lose the log.
- **Wire a live dashboard** (`status.json` + polling HTML, served via `setsid`) into every substantial VM generation run — don't rely only on `tail`. (Standing user preference.)
- **Never disturb shared environments** (e.g. the `td_ludo*` / AlphaLudo env on the VM). Use isolated venvs.
- **VM lifecycle (user directive 2026-06-29): keep the VM UP while more VM work is plausibly coming** — idle for a few minutes (verify, code, check results, decide next run) is fine. **Shut down only when VM work is genuinely exhausted** ("can't think of anything else to do on the VM"). The binding risk is **L4 stockout on restart**, not idle billing — do NOT reflexively stop after every test, and do NOT optimize billing unless the user explicitly asks. On shutdown: stop the VM, delete transient firewall rules; the disk/cache persists.

## §9 — Measuring confidence / knowledge boundary (method standard)
From [model-confidence-knowledge-boundary.md](research/model-confidence-knowledge-boundary.md):
- **Two axes, measured separately:** *actual competence* (needs ground truth, ideally pass@k) × *expressed confidence* (text hedges, verbalized P(True), logit-entropy, internal probe).
- **Combine ≥2 confidence signals; trust none alone.** Log-probs are confounded by surface form; verbalized confidence is weak at small scale (but *not* useless — the "2B is accuracy-independent" claim was refuted 3-0); internal probes may read plausibility not truth (our F167).
- **Ground truth — not the uncertainty signal — splits confident-correct from confabulation** (§3).

## §10 — This document improves
- After every experiment that teaches a methodological lesson, **add or sharpen a rule here** and bump the version. The standard is a ratchet — it only goes up.
- Disagreement with a rule is resolved by *raising* the bar, not lowering it, unless the rule is shown to be wrong.

---

## Pre-flight checklist (run through before every experiment)
- [ ] Prereg written: hypothesis, prediction, **falsifier**, planned controls (§1)
- [ ] Measurement matches the claim (greedy vs pass@k; right metric) (§1, §4)
- [ ] Baseline + **multi-seed random control** + sign control planned (§2)
- [ ] Ground truth available; hand-read rubric written (§3)
- [ ] Parameters calibrated to *this* model's scale (§4)
- [ ] Raw generations + traces will be saved; seeds recorded (§6)
- [ ] Decoding battery decided (greedy + sampled/k + temp) (§7)
- [ ] Ops: isolated env, kill-verify, setsid launch, dashboard, billing plan (§8)
- [ ] Result will be **tiered** (controlled / suggestive / hypothesis) (§5)

## Changelog
- **v1.0 (2026-06-28):** Initial floor, synthesized from F100–F171 (esp. the F122/F160/F171 random-control lessons, the F169/F170 measurement-mismatch retraction, the F171 α-scale lesson, the read≠write wall), the IH construct literature, and the model-confidence/knowledge-boundary methods review.

## §11 — Prior-art / novelty check BEFORE the arc (added 2026-07-12)
- **Do a literature search at PREREG time, not writeup time.** Before committing effort to an arc,
  search for the core claim + its neighbors and write a short "prior art" paragraph in the prereg:
  what's already known, what (if anything) would be new. This is part of §1, not optional.
- **Earned by:** 2026-07-12 lit-check found ALL THREE project headline arcs (behavioral-Jacobian
  read≠write atlas, gate→search confidence-gating, F191 trace-answer dissociation) already covered by
  active 2025-26 literature — after the work was done and called "publishable." Rigor was never the
  problem; unchecked novelty was.
- **Positioning rule:** if the finding exists, say so and reposition honestly — independent
  small-model REPLICATION, a controlled NEGATIVE result (our strength; state it as replication/null,
  not discovery), or a METHOD note. Never present a known result as novel. A replication clearly
  labelled as such is honest and useful; a mislabelled "discovery" is not.
