# Workspace overnight run — morning summary (2026-07-07 15:24)

Prereg: docs/prereg-workspace-mac.md · Model: Qwen3-4B fp16 MPS

## Tier 0 — Ignition
- **alt_words**: n=480, sharpness peak L35 (11.15); L0-4 mean 1.81; bimod peak 0.94 at L35
- **countries**: n=640, sharpness peak L35 (9.39); L0-4 mean 1.55; bimod peak 0.91 at L31
- **random_dir_0**: n=160, sharpness peak L35 (6.81); L0-4 mean 2.29; bimod peak 0.84 at L23
- **random_dir_1**: n=160, sharpness peak L35 (6.54); L0-4 mean 2.28; bimod peak 0.82 at L23
- Read: ignition = countries sharp/bimodal in a mid band while random_dir stays low; smooth-monotone or early-snap = falsified (see prereg).

## Tier 1 — Stratification (logit lens)
- layers 0..35 (n=36), 50 chunks
- kurtosis peak: L34 (1.4); top5-acc: first layer >0.5 = 27, final 1.00
- persistence excess (d=1) peak: L26 (0.05)

## Tier 1 — Stratification (jlens lens)
- layers 4..32 (n=15), 50 chunks
- kurtosis peak: L8 (2.3); top5-acc: first layer >0.5 = 32, final 0.67
- persistence excess (d=1) peak: L24 (0.08)

## Tier 2 — J-lens fit
- {"n_prompts": 20, "source_layers": [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32], "dim_batch": 4, "corpus": "wikitext seed0 128tok", "saved": "2026-07-07 14:13:16"}

## Tier 2b — QC gate + causal swaps
- QC multihop (best-rank hits over band): {"jlens": {"n": 72, "hit_top1": 16, "hit_top10": 51}, "logit": {"n": 72, "hit_top1": 21, "hit_top10": 52}}
- swaps: {"n_items": 90, "n_gated": 38, "swap_s1_hits": 5, "swap_s2_hits": 0, "noop_ok": 38, "rand_hits_total": 6, "rand_trials": 114, "rand_broke_base": 65}
- swap rate s1 = 5/38, s2 = 0/38, random-control rate = 0.053, noop intact = 38/38

## Tier 3 — Workspace loading vs F189 boundary blindness
- lens n_prompts=1, band=[10, 12, 14, 16, 18, 20, 22, 24, 26, 28]
- **WRINKLE**: gold {"n": 0, "median_best_rank": null, "frac_top10": null} · null {"n": 0, "median_best_rank": null, "frac_top10": null}
- **HARD**: gold {"n": 0, "median_best_rank": null, "frac_top10": null} · null {"n": 0, "median_best_rank": null, "frac_top10": null}
- **CORRECT**: gold {"n": 1, "median_best_rank": 271.0, "frac_top10": 0.0} · null {"n": 1, "median_best_rank": 83.0, "frac_top10": 0.0}
- error reproduction sanity: 0/1 failures reproduced
- H3.1 read: boundary(WRINKLE) gold-loading << CORRECT supports the workspace account of P(True) blindness; comparable loading falsifies it. n is tiny -> tier B max.

## Tier 3b — Wrinkle-concept loading (amendment A1)
- lens n_prompts=20, band=[10, 12, 14, 16, 18, 20, 22, 24, 26, 28]
- **WRINKLE / fail_trace**: concept {"n": 7, "median": 1.0, "frac_top10": 1.0} · null {"n": 7, "median": 53.0, "frac_top10": 0.0} · poscontrol {"n": 7, "median": 10.0, "frac_top10": 0.5714285714285714}
- **WRINKLE / teacher_correct**: concept {"n": 7, "median": 1.0, "frac_top10": 1.0} · null {"n": 7, "median": 104.0, "frac_top10": 0.0} · poscontrol {"n": 7, "median": 12.0, "frac_top10": 0.42857142857142855}
- **HARD / fail_trace**: concept {"n": 5, "median": 1.0, "frac_top10": 0.8} · null {"n": 5, "median": 49.0, "frac_top10": 0.2} · poscontrol {"n": 5, "median": 6.0, "frac_top10": 0.6}
- **HARD / teacher_correct**: concept {"n": 5, "median": 1.0, "frac_top10": 0.8} · null {"n": 5, "median": 206.0, "frac_top10": 0.2} · poscontrol {"n": 5, "median": 5.0, "frac_top10": 1.0}
- H3.1-amended read: concept ranks fail>>teacher with nulls flat supports the workspace account; comparable ranks falsify it (see amendment A1). n=7 -> tier B max.

---
Raw: results/workspace/*.json, *.npz · status: status.json · logs: results/workspace/logs/
