---
**What this doc is**: Cumulative analysis of how F111 → F120 chained together to falsify residual-stream additive steering as a path to virtue installation in small open-weight LLMs. The point is the *chain*, not any individual finding.

**What this doc is NOT**: a numbered-findings catalogue (that's `findings.md`), a chronological narrative (that's `journal.md`), or a strategic-decision log (that's `post-mvp-decisions.md`). The cited findings exist in their full form in `findings.md` — this doc reads them as a sequence and surfaces what each step contributes that the previous ones didn't.

**Update policy**: appended-to when a new mechanism variant is tested and either extends or breaks the chain. Each addition cites the relevant F-number and adds a short paragraph about what that variant ruled out.
---

# Cumulative falsification chain — F111 → F123

**Period covered**: Day 25 (2026-05-03) → Day 37 (2026-05-19).
**Cumulative N**: 3,010+ Opus-judged generations across three studies — composed as 1,752 cross-model (F110/F111; includes 24 embedded baselines) + 1,110 SAE battery (F115–F119; includes 124 embedded baselines) + 52 mech-shift steered (F120) + 96 ablation steered (F123; mech-shift and ablation baselines tracked separately). Verified against `per_generation.csv` row counts on 2026-05-18, plus 96 manually Opus-judged ablation generations on 2026-05-19.
**Bottom line**: humility / verification-disposition behavior is not steerable into the residual stream of the tested open-weight models via any tested combination of `{additive coefficient sign} × {single layer, multi-layer} × {ungated, first-1-gated, first-5-gated} × {humility-content features, doubt features, commit features}` (additive operations: F111–F122) OR `directional ablation c ∈ {0.25, 0.5, 0.75, 1.0} along the same features` (F123). The limit is the representation; neither additive perturbation nor directional removal of these features installs abstention.

---

## The chain at a glance

Each finding closes a specific escape hatch the previous finding left open. The "what's left to try?" column is what motivated the next experiment.

| Step | Finding | Closed | What was left to try |
|---|---|---|---|
| 0 | F45 (pre-chain context) | Virtue-content features routinely cluster on cultural-register sub-domains in extracted vectors. | SAE-feature-by-feature could find humility content the diff-of-means missed. |
| 1 | **F111** (Day 25) | v_IH (diff-of-means) does not install humility across 4 prompts × 3 thinking-model families × 1,752 generations. | Method failure vs deeper falsification still ambiguous. SAE-features remain the natural alternative. |
| 2 | **F114** (Day 28) | v_IH projects mostly onto code/technical-register SAE features, not humility content. 0/7 Tier-1 humility features in v_IH's top-50 projection. | Maybe humility *features* (extracted directly from SAE, not via diff-of-means) work even if the diff-of-means vector doesn't. |
| 3 | **F115** (Day 30) | Tier-1 humility SAE features fail to install abstention across 5 models × 5 SAE families × 1,110 generations. They produce confabulation, not the named uncertainty disposition. | Maybe the static-additive mechanism is the constraint. First-N gating / multi-layer / negative-α might work. |
| 4 | **F116** (Day 30) | "Doubt"-named features reverse-code: amplifying them *induces* confabulation, not suppression. Feature naming is not a reliable behavior predictor. | The reciprocal test (negative-α on the same feature) might suppress generation properly. |
| 5 | **F117** (Day 30) | E2 contested-evidence is unsteerable: 0/267 generations clear the bar across 30 cells × 5 SAE families. Not a layer/feature problem — but see addendum: E2 is structurally compromised (memorized pro-flossing consensus + confabulated Cochrane citations), so F117 measures prompt-design failure rather than architectural ceiling. The chain still holds without F117 (F115/F116/F118/F120/F121 carry it). | Mechanism shifts might still work for E1 / ip-longest / eg-v2-10. |
| 6 | **F118** (Day 30) | Mid-α steering induces fabricated academic citations (FM-fake-sourcing). The intervention has a safety-relevant failure mode, independent of whether it installs the target virtue. | This doesn't close any path, but adds a cost to any "small effect" claim. |
| 7 | **F119** (Day 30) | Random-vector control on qwen3-4b L17 produces variation indistinguishable from real-feature steering at the **verdict level** (all ✗ on E1 across the α-grid). *Generation-content* equivalence does not hold — random anchors at 105 kg at 10/11 α-values; real features drift to 100/130/150 more often. The random-control sub-finding has since been promoted to F122. | The verdict-level random-mimic finding casts doubt on small "feature did this" claims; doesn't rule out conditional / multi-layer / negative-α working at *larger* effect sizes. |
| 8 | **F120** (Day 31) | All four mechanism-shift variants (first-N gating, multi-layer composition, negative-α humility, negative-α commit) fail. Zero baseline-✗ generations promoted to ✓ by any mechanism shift on E1 + E2 + ip-longest. | CAST conditional gating is the last interpretability-flavored variant not yet tested. Prior after F120 is ~20%. |
| 9 | **F121** (Day 31) | Reciprocal test confirms steering is one-sided: positive-α and negative-α on the same feature both produce confabulation, never suppression. The dial only changes *what* is generated, not *whether*. | Suppression mechanism, if it exists, is not accessible via residual-stream additive operations. |
| 10 | **F122** (Day 31) | Random vectors at qwen3-4b L17 mimic real-feature steering at the alpha levels of interest. The burden of proof for "vector X did this" is now: show the random control doesn't do the same. | Multi-seed / multi-layer / multi-model random controls still untested — does the random-mimic property hold elsewhere? |
| 11 | **F123** (Day 37, 2026-05-19) | Pre-registered ablation experiment falsifies F121's "addition can't suppress / ablation can" hypothesis. Across 6 distinct steering operations on r1-distill commit-pair × E1 — `{additive +α, additive −α, ablation c ∈ 0.25, 0.5, 0.75, 1.0}` — every operation breaks baseline abstention into a different confabulated kg figure. The single exception across 24 ablation cells: random-direction control at c=0.25 preserves abstention. **The limit is the representation, not the operation.** | Encoder-clamping (forcing feature activations to target values), conditional gating (CAST), and behavioral fine-tuning are the still-untested mechanism families. |

---

## What the chain rules out

After F120/F121/F122/F123, the residual-stream steering branch of the project is empirically closed for the targeted virtues, across:

- **{additive coefficient sign}**: positive-α and negative-α both produce confabulation-along-direction; neither suppresses (F121).
- **{single layer, multi-layer}**: L8+L17+L25 (qwen3-4b) and L11+L21+L31 (r1) multi-layer applications fail same as single-layer (F120 C2).
- **{ungated, first-1-gated, first-5-gated}**: first-1 and first-5 gating produce the same ✗ distribution as ungated (F120 C1).
- **{humility-content features, doubt features, commit features}**: feature-content semantics is not predictive of behavioral effect; all three categories produce confabulation under amplification (F115, F116, F121).
- **{additive perturbation, directional ablation}**: F123 (2026-05-19) extends the chain by showing that directional ablation `h' = h − c·(h·v̂)v̂` at c ∈ {0.25, 0.5, 0.75, 1.0} also fails to install abstention on the same features additive steering failed on. **The limit is the representation, not the operation.**
- **At IH-extraction layers and their multi-layer compositions** across 5 model families.

This holds across α ∈ {−8, −5, 0.001 → 5.0} (24+ tested values) for additive operations, and c ∈ {0.25, 0.5, 0.75, 1.0} for ablation operations.

## What the chain does NOT rule out

The chain rules out a specific intervention class (residual-stream additive *and* ablative operations on these features), not the underlying research question. Untested mechanisms include:

- **Encoder-clamping** — forcing feature activations to target values rather than adding/removing components. This is a fundamentally different operation than F121/F123 tested (which both work in residual-stream geometry). Prior after F123 ~15-25%.
- **Conditional / gated steering (CAST)** — learned-gate steering. Prior after F123 ~10-15% (gated additive shares the additive geometry with F121, which is closed).
- **Behavioral fine-tuning (DPO/SFT)** — the established mechanism for behavioral installation; ~80% prior. The Day-31 strategic commitment in `post-mvp-decisions.md` is to test virtue + tools via fine-tuning, not via steering. F123 strengthens this commitment.
- **Projection-based or contrastive-decoding methods** — operate outside both residual-stream-additive and residual-stream-ablation frames.
- **Tool-use augmentation with any of the above** — the original Phronesis question (virtue + tools beats baseline + tools) requires a working virtue intervention, which fine-tuning is the most likely path to.

## What each step contributes (the value-of-the-chain, not just the value-of-the-bottom-line)

The chain has scientific value independent of the strategic close-out:

1. **F111** is the diff-of-means falsification at cross-model scale. Method failure or deeper falsification was ambiguous after this step alone.
2. **F114** is the first basis-mismatch / projection diagnostic. Shows that v_IH-as-extracted decomposes to surface features under SAE projection — strongly suggests F45-pattern (cultural-register surface signal).
3. **F115** is the disambiguation between "method failure" and "deeper falsification". SAE-feature-by-feature was the obvious fix for F111; it doesn't work either. After F115, the F111 falsification hardens into "humility content is not present as an L17 / L23 / L31 residual-stream signal in any of the tested form-factors."
4. **F116** is the first architectural finding: feature naming is reverse-coded relative to behavior. This is independently publishable — it generalizes beyond the Phronesis project to anyone using auto-labeled SAE features.
5. **F117** is a different shape of finding: E2 is uniformly unsteerable. Not about which feature, not about which mechanism — about the input itself. Some behaviors don't have steerable representations regardless of method.
6. **F118** is the safety-relevant byproduct: FM-fake-sourcing. Steering-induced citation fabrication is a real failure mode with direct relevance to RAG / agentic / research-assist pipelines.
7. **F119** is the methodological discipline upgrade: alpha-grid waste, random-control mimicry, structural collapse. Each is actionable for any future SAE-steering experiment.
8. **F120** is the mechanism-independence claim. After F115 closed static-additive, the natural pushback was "maybe the mechanism is the constraint." F120 tests four cheap alternatives and closes them all.
9. **F121** is the reciprocal-test architectural finding: residual-stream additive steering is one-sided. Generalizes beyond Phronesis.
10. **F122** is the random-control claim: low-to-mid α effects on qwen3-4b L17 are dominated by perturbation noise. Re-interprets any "small effect" finding in this regime.
11. **F123** is the pre-registered-falsifier result: directional ablation (Arditi 2024) on the same features also fails to install abstention. Strengthens the architectural claim from "additive is one-sided" to "the representation isn't there in any form residual-stream operations can reach." The single ✓ across 24 ablation cells (random direction at c=0.25 preserves baseline abstention) sharpens the failure mode: real-feature ablation is more destructive than random ablation at low c, but more destructive in the *wrong direction* — never toward suppression.

## Cross-references

- `findings.md` — full F-numbered entries (the single source of truth for each finding's claim, evidence, and caveats).
- `journal.md` — Days 25-31 chronological narrative around each finding.
- `docs/sae_round_report.md` (now in `docs/archive/`) — the consolidated SAE-round report this chain analysis was first synthesized in.
- `docs/post-mvp-decisions.md` Day-31 evening update — the strategic implications of the chain.
- `docs/project.md` "What's been ruled out" section — short-form version of this chain.
- `docs/writeup-plan.md` — planned standalone post on F121 (steering one-sidedness) and the chain as a whole.

## When this doc gets updated

- A new mechanism variant is tested (CAST conditional gating, projection-based, contrastive-decoding) → add a new step to the table + a one-paragraph contribution note.
- A new architectural finding generalizes the chain to other model families or layers → update the "What the chain rules out" section.
- A finding turns out to be wrong on re-analysis → annotate the row with the retraction and link to the corrected finding.

This is not a chronological log. Order is logical-dependency order, not date order. If a later experiment retroactively reframes an earlier finding, the row order changes.
