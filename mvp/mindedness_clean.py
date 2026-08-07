#!/usr/bin/env python
"""Definitive mindedness-geometry measurement: template-averaged + polarity-orthogonalised.

Fixes the two defects found by mindedness_validate.py:
  (1) POLARITY CONTAMINATION — nature/object v_mind partly encodes expected yes/no
      (cos to v_polarity -0.34..-0.48 in BOTH models). Fix: project v_polarity out.
  (2) TEMPLATE SENSITIVITY — single-template directions agree only +0.39..+0.60 across
      wrappers. Fix: average the (unit-normalised) direction over 3 templates.

Reports RAW (template-averaged only) vs CLEAN (also orthogonalised) so the effect of the
correction is visible. Controls unchanged: random floor, exemplar split-half ceiling,
physical-contrast discriminant — all computed on the CLEAN directions.
"""
import argparse, json, os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from mindedness_geometry import ENTITIES, MENTAL, PHYSICAL, cos
from mindedness_validate import TEMPLATES, POLARITY_YES, POLARITY_NO

DEVICE = "mps"


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def orth(v, ref):
    """remove the component of v along ref (per layer)."""
    r = unit(ref)
    return v - np.dot(v, r) * r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3.5-4B")
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()
    tag = args.tag or args.model.split("/")[-1].replace(".", "_")
    OUT = f"results/workspace/mindedness_clean_{tag}.json"
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(args.model)
    try:
        hf = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    except Exception:
        from transformers import AutoModel
        hf = AutoModel.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    L, d = model.n_layers, model.d_model
    layers = list(range(L))
    print(f"[load] {args.model} L={L} d={d}", flush=True)

    @torch.no_grad()
    def acts_of(text):
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=layers) as rec:
            model.forward(ids)
            return torch.stack([rec.activations[l][0, -1] for l in layers]).float().cpu().numpy()

    A = {}
    for tn, tmpl in TEMPLATES.items():
        for cls, exs in ENTITIES.items():
            for ei, e in enumerate(exs):
                for kind, attrs in (("mental", MENTAL), ("phys", PHYSICAL)):
                    for ai, a in enumerate(attrs):
                        A[(tn, cls, ei, kind, ai)] = acts_of(tmpl.format(e=e, a=a))
        print(f"  [{tn}] {round(time.time()-t0)}s", flush=True)
    # polarity direction, averaged over the same 3 wrappers
    pol = []
    for tn, tmpl in TEMPLATES.items():
        wrap = tmpl.split("{e}")[0]
        y = np.mean([acts_of(f"{wrap}{q}?\nAnswer:") for q in POLARITY_YES], 0)
        nn = np.mean([acts_of(f"{wrap}{q}?\nAnswer:") for q in POLARITY_NO], 0)
        pol.append(np.stack([unit(x) for x in (y - nn)]))
    v_pol = np.mean(pol, 0)                                    # [L, d]

    def vmind_raw(cls, tn, exs=None):
        exs = range(4) if exs is None else exs
        m = np.mean([A[(tn, cls, e, "mental", a)] for e in exs for a in range(6)], 0)
        p = np.mean([A[(tn, cls, e, "phys", a)] for e in exs for a in range(6)], 0)
        return m - p

    def vmind_avg(cls, exs=None):
        """unit-normalise per template, then average -> phrasing-robust direction"""
        return np.mean([np.stack([unit(x) for x in vmind_raw(cls, tn, exs)])
                        for tn in TEMPLATES], 0)

    def vmind_clean(cls, exs=None):
        v = vmind_avg(cls, exs)
        return np.stack([orth(v[l], v_pol[l]) for l in layers])

    def phys_contrast(cls):
        out = []
        for tn in TEMPLATES:
            a = np.mean([A[(tn, cls, e, "phys", i)] for e in range(4) for i in (0, 1, 2)], 0)
            b = np.mean([A[(tn, cls, e, "phys", i)] for e in range(4) for i in (3, 4, 5)], 0)
            out.append(np.stack([unit(x) for x in (a - b)]))
        v = np.mean(out, 0)
        return np.stack([orth(v[l], v_pol[l]) for l in layers])

    classes = list(ENTITIES)
    RAW = {c: vmind_avg(c) for c in classes}
    CLN = {c: vmind_clean(c) for c in classes}
    SH = {c: (vmind_clean(c, [0, 1]), vmind_clean(c, [2, 3])) for c in classes}
    PHYS = {c: phys_contrast(c) for c in classes}

    rng = np.random.default_rng(0)
    floor = float(np.mean([abs(cos(rng.standard_normal(d), rng.standard_normal(d))) for _ in range(20)]))

    per_layer = []
    for l in layers:
        pr = {f"{a}|{b}": cos(RAW[a][l], RAW[b][l]) for i, a in enumerate(classes) for b in classes[i+1:]}
        pc = {f"{a}|{b}": cos(CLN[a][l], CLN[b][l]) for i, a in enumerate(classes) for b in classes[i+1:]}
        sh = {c: cos(SH[c][0][l], SH[c][1][l]) for c in classes}
        dc = {c: cos(CLN[c][l], PHYS[c][l]) for c in classes}
        pol_res = {c: cos(CLN[c][l], v_pol[l]) for c in classes}
        per_layer.append({"layer": l, "frac": l/(L-1), "pairs_raw": pr, "pairs_clean": pc,
                          "split_half": sh, "discriminant": dc, "polarity_residual": pol_res,
                          "between_raw": float(np.mean(list(pr.values()))),
                          "between_clean": float(np.mean(list(pc.values()))),
                          "ceiling": float(np.mean(list(sh.values())))})
    res = {"model": args.model, "n_layers": L, "random_floor": floor,
           "per_layer": per_layer, "runtime_min": round((time.time()-t0)/60, 1)}
    json.dump(res, open(OUT, "w"), indent=1)

    band = [r for r in per_layer if 0.5 <= r["frac"] <= 0.8]
    m = lambda k: float(np.mean([r[k] for r in band]))
    print(f"\n=== {args.model} — template-averaged + polarity-orthogonalised ===")
    print(f"  random floor {floor:.3f} | ceiling {m('ceiling'):.3f}")
    print(f"  between RAW {m('between_raw'):+.3f}  ->  CLEAN {m('between_clean'):+.3f}")
    print(f"  polarity residual after orth: "
          f"{max(abs(np.mean([r['polarity_residual'][c] for r in band])) for c in classes):.4f} (max)")
    print("  clean pairs (band mean):")
    pairs = sorted({k: float(np.mean([r["pairs_clean"][k] for r in band])) for k in band[0]["pairs_clean"]}.items(),
                   key=lambda kv: -kv[1])
    for k, v in pairs:
        print(f"    {k:16} {v:+.3f}")
    sp = [v for k, v in pairs if "self" in k]; op = [v for k, v in pairs if "self" not in k]
    print(f"  SELF-OUTLIER: self={np.mean(sp):+.3f} non-self={np.mean(op):+.3f} "
          f"{'YES' if np.mean(sp) < np.mean(op) else 'NO'}")
    print(f"  discriminant: " + ", ".join(f"{c}={np.mean([r['discriminant'][c] for r in band]):+.2f}" for c in classes))
    print(f"[done] {res['runtime_min']} min -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
