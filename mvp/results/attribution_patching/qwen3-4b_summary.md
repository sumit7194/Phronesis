# Attribution patching — qwen3-4b — α=8 — 5 probe prompts/virtue

Generated 2026-04-26. Method: KL(steered ‖ baseline) on next-token logits. See `mvp/attribution_patching.py`.

## Headline

**The α-sweep was steering at suboptimal layers.** Attribution patching identifies layers where adding α·v_virtue produces the largest causal shift in output distribution. For three of four virtues, those layers are *not* in our F98-pre-registered grid {18, 20, 22, 25}.

| Virtue | AP peak | AP-KL @ peak | α-sweep auto-pick (KL there) | Hand-rubric pick (KL there) | Verdict |
|---|---|---|---|---|---|
| **CC** | **L9** | 0.108 | L25 α=20 (KL=0.012) | L25 α=8 (KL=0.012) | **9× off** — both picks are in near-zero-KL zone |
| **IH** | **L17** | 0.190 | L18 α=20 (KL=0.151) | L20 α=20 (KL=0.114) | Auto/hand picks are adjacent to AP peak; reasonable |
| **EG** | L7 | 0.039 | L18 α=4 (KL=0.018) | — (no clean pick) | Uniformly weak signal — EG vector lacks causal punch on qwen |
| **RT** | **L15** | 0.071 | L18 α=20 (KL=0.052) | L22 α=8 (KL=0.028) | Auto-pick adjacent; hand-pick 7 layers off-peak |

## Mid-late layer KL profile (full)

```
  L         CC       IH       EG       RT
  5     0.0608   0.0512   0.0132   0.0470
  6     0.0800   0.0751   0.0191   0.0625
  7     0.0471   0.0622   0.0394   0.0649
  8     0.0626   0.0786   0.0229   0.0425
  9     0.1083 ★ 0.0583   0.0212   0.0389
 10     0.0704   0.0803   0.0330   0.0452
 11     0.0680   0.0678   0.0162   0.0382
 12     0.0813   0.0744   0.0153   0.0467
 13     0.0487   0.0479   0.0175   0.0581
 14     0.0564   0.0532   0.0185   0.0570
 15     0.0773   0.0705   0.0184   0.0706 ★
 16     0.0568   0.0789   0.0209   0.0606
 17     0.0609   0.1895 ★ 0.0234   0.0657
 18     0.0483   0.1513   0.0183   0.0523     ← α-sweep auto-pick L
 19     0.0821   0.1188   0.0273   0.0530
 20     0.0503   0.1144   0.0317   0.0626     ← α-sweep auto-pick L (CC)
 21     0.0470   0.1333   0.0241   0.0670
 22     0.0292   0.0725   0.0239   0.0280     ← hand-rubric L (RT)
 23     0.0177   0.0443   0.0150   0.0206
 24     0.0125   0.0260   0.0105   0.0191
 25     0.0122   0.0177   0.0119   0.0141     ← α-sweep auto-pick L (CC); hand-rubric (CC)
 26-35  → all <0.013 → effectively zero attribution
```

## Three big interpretations

### 1. Deep layers (L23-35) have near-zero attribution KL

This is the layer range where F102 observed the geometric collapse cluster (CC, EG, RT sharing direction at deep layers, |cos| > 0.5 at L29-31). **But those layers have essentially zero causal contribution to output behavior** under attribution patching. The "geometric overlap" we measured is real but happens in a region of the residual stream that doesn't drive behavior.

Reframe: F102's CC×RT collapse at deep layers is a *late-residual-stream artefact*, not a deep behavioral fact about the model. The behaviorally-important layers (L7-L21) have cleanly-orthogonal virtue directions.

### 2. CC's auto-pick (L25) was 9× off the AP peak (L9)

The α-sweep settled on L25 for CC because that's where the hedge-proxy regex scorer rewarded the most. Attribution patching says L25 is essentially a flat layer — adding v_CC there barely changes the output distribution. **The CC behavioral effect we observed (item 72 spiral → confident commit) probably came from the L25 vector accidentally aligning with mid-layer (L9-L19) computational paths, not from L25 being where CC actually acts.**

### 3. IH peak at L17 is a clean, strong signal

IH peaks at L17 with KL=0.190 — the strongest signal across all four virtues. The α-sweep's auto-pick L18 is one layer off; the hand-rubric pick L20 is three layers off. Both are in a reasonable adjacent zone. This is consistent with F103's finding that IH had a real +0.8 hand-rubric improvement on qwen — IH is the virtue with the cleanest causal locus in qwen3-4b.

## What this means for next steps

1. **Re-run a focused α-sweep at AP-peak layers.** Specifically:
   - CC: α-sweep at **L9** (currently untested)
   - IH: α-sweep at **L17** (one layer below current grid)
   - RT: α-sweep at **L15** (untested)
   - EG: α-sweep at **L7** but expect weak signal (KL=0.039 is small)
   This is ~4 virtues × 5 alphas × 5 prompts × 1 layer ≈ 100 generations. ~3-5h GPU. Cheap.

2. **The negative-control corpus experiment becomes more interesting.** If a verbosity vector ALSO peaks at L7-L17, our virtue vectors are using the same "behavioral computation locus" as a non-virtue surface feature. If verbosity peaks elsewhere (or has flat attribution), our virtue vectors are doing something specific to virtue-related computation.

3. **F102's collapse story should be qualified.** The deep-layer collapse is real geometrically but causally insignificant. The publishable claim should be: *"virtue directions are cleanly separable in mid-layers (where they drive behavior) but partially collapse in deep layers (where attribution KL is low and behavioral effects are minimal)."*

4. **Phase 5 layer-selection protocol.** Pre-register attribution patching as the layer-selection method (per `phase5-plan.md` §6.5 + the post-MVP decisions framing).

## Caveats

- **Single α (=8).** Attribution may shift at different α magnitudes. We chose α=8 because hand-rubric showed clean output there. Could re-run at α=4 and α=12 to verify peak stability.
- **Prompts are eval-target prompts, not held-out.** Some overlap with α-sweep prompts (specifically RT and EG used the same JSON files). For tight rigor, we'd use a separately-curated probe set.
- **MPS / fp16 precision.** Mac MPS in fp16 may have small numerical noise compared to GPU fp32 reference. Numbers should be stable for ranking purposes but absolute KL values shouldn't be over-interpreted.
- **No gemma yet.** When GCP frees up, run the same on gemma-4-E4B-it. F102 said gemma had clean geometry; F103 said gemma had null behavior. Attribution patching might explain why: maybe gemma's virtue vectors don't have causal locus at any layer.
