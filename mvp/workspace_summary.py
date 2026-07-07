#!/usr/bin/env python
"""Aggregate the overnight workspace-run results into results/workspace/MORNING_SUMMARY.md."""
import json, os, time

import numpy as np

RES = os.path.join(os.path.dirname(__file__), "results", "workspace")


def load(name):
    p = os.path.join(RES, name)
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return None


def main():
    lines = [f"# Workspace overnight run — morning summary ({time.strftime('%Y-%m-%d %H:%M')})",
             "", "Prereg: docs/prereg-workspace-mac.md · Model: Qwen3-4B fp16 MPS", ""]

    t0 = load("t0_ignition.json")
    lines.append("## Tier 0 — Ignition")
    if t0:
        c = t0["conditions"]
        def peak(name):
            if name not in c:
                return "missing"
            sh = c[name]["sharpness_mean"]
            bm = c[name]["bimodality_mean"]
            pk = int(np.argmax(sh))
            return (f"n={c[name]['n_items']}, sharpness peak L{pk} "
                    f"({sh[pk]:.2f}); L0-4 mean {np.mean(sh[:5]):.2f}; "
                    f"bimod peak {max(bm):.2f} at L{int(np.argmax(bm))}")
        for name in sorted(c):
            lines.append(f"- **{name}**: {peak(name)}")
        lines.append("- Read: ignition = countries sharp/bimodal in a mid band while "
                     "random_dir stays low; smooth-monotone or early-snap = falsified (see prereg).")
    else:
        lines.append("- MISSING (stage failed?)")

    for mode in ("logit", "jlens"):
        t1 = load(f"t1_strat_{mode}.json")
        lines.append(f"\n## Tier 1 — Stratification ({mode} lens)")
        if t1:
            L = t1["layers"]
            k = t1["excess_kurtosis"]
            a5 = t1["top5_acc"]
            p1 = t1["persistence"]["1"]
            n1 = t1["persistence_null"]["1"]
            ex = [p - n for p, n in zip(p1, n1)]
            lines.append(f"- layers {L[0]}..{L[-1]} (n={len(L)}), {t1['n_chunks']} chunks")
            lines.append(f"- kurtosis peak: L{L[int(np.argmax(k))]} ({max(k):.1f}); "
                         f"top5-acc: first layer >0.5 = "
                         f"{next((str(L[i]) for i, v in enumerate(a5) if v > 0.5), 'none')}, "
                         f"final {a5[-1]:.2f}")
            lines.append(f"- persistence excess (d=1) peak: L{L[int(np.argmax(ex))]} ({max(ex):.2f})")
        else:
            lines.append("- MISSING")

    meta = load("t2_fit_meta.json")
    lines.append("\n## Tier 2 — J-lens fit")
    lines.append(f"- {json.dumps(meta) if meta else 'MISSING — lens did not fit; '
                 'all lens-dependent tiers inconclusive'}")

    t2b = load("t2b_validate.json")
    lines.append("\n## Tier 2b — QC gate + causal swaps")
    if t2b:
        lines.append(f"- QC multihop (best-rank hits over band): {json.dumps(t2b['qc_multihop'])}")
        lines.append(f"- swaps: {json.dumps(t2b['swap_summary'])}")
        s = t2b["swap_summary"]
        if s["n_gated"]:
            rr = (s["rand_hits_total"] / max(1, s["rand_trials"]))
            lines.append(f"- swap rate s1 = {s['swap_s1_hits']}/{s['n_gated']}, "
                         f"s2 = {s['swap_s2_hits']}/{s['n_gated']}, "
                         f"random-control rate = {rr:.3f}, "
                         f"noop intact = {s['noop_ok']}/{s['n_gated']}")
    else:
        lines.append("- MISSING")

    t3 = load("t3_loading.json")
    lines.append("\n## Tier 3 — Workspace loading vs F189 boundary blindness")
    if t3:
        lines.append(f"- lens n_prompts={t3['lens_n_prompts']}, band={t3['band']}")
        for g, v in t3["summary"].items():
            lines.append(f"- **{g}**: gold {json.dumps(v['gold'])} · null {json.dumps(v['null_0'])}")
        repro = [r for r in t3["rows"] if r.get("group") in ("WRINKLE", "HARD")]
        n_re = sum(1 for r in repro if r.get("reproduced_error"))
        lines.append(f"- error reproduction sanity: {n_re}/{len(repro)} failures reproduced")
        lines.append("- H3.1 read: boundary(WRINKLE) gold-loading << CORRECT supports the "
                     "workspace account of P(True) blindness; comparable loading falsifies it. "
                     "n is tiny -> tier B max.")
    else:
        lines.append("- MISSING")

    t3b = load("t3b_wrinkle.json")
    lines.append("\n## Tier 3b — Wrinkle-concept loading (amendment A1)")
    if t3b:
        lines.append(f"- lens n_prompts={t3b['lens_n_prompts']}, band={t3b['band']}")
        for g, arms in t3b["summary"].items():
            for arm, m in arms.items():
                lines.append(f"- **{g} / {arm}**: concept {json.dumps(m['concept'])} · "
                             f"null {json.dumps(m['null'])} · poscontrol {json.dumps(m['poscontrol'])}")
        lines.append("- H3.1-amended read: concept ranks fail>>teacher with nulls flat "
                     "supports the workspace account; comparable ranks falsify it "
                     "(see amendment A1). n=7 -> tier B max.")
    else:
        lines.append("- MISSING")

    lines.append("\n---\nRaw: results/workspace/*.json, *.npz · status: status.json · "
                 "logs: results/workspace/logs/")
    out = os.path.join(RES, "MORNING_SUMMARY.md")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
