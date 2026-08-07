#!/usr/bin/env python
"""S2 WIDE + S3 DECODE — all six facets with the corrections F-G earned.

Per facet: direction = unit-normalised per template, averaged over 3 templates, then
polarity-orthogonalised. Reports per facet: cross-facet cosines, self-outlier gap, exemplar
split-half ceiling, random floor. If a fitted J-lens exists for this model, also decodes each
facet direction into vocabulary (S3).
Prereg: docs/prereg-mindedness-facets.md
"""
import argparse, json, os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from jlens.lens import JacobianLens
from jlens.vis import _meaningful_token_mask
from workspace_common import BAND, LENS_PATH
from mindedness_geometry import ENTITIES, PHYSICAL, cos
from mindedness_validate import TEMPLATES, POLARITY_YES, POLARITY_NO
from mindedness_facets import FACETS

DEVICE = "mps"


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--tag", default=None)
    ap.add_argument("--decode", action="store_true", help="also decode directions (needs fitted lens)")
    args = ap.parse_args()
    tag = args.tag or args.model.split("/")[-1].replace(".", "_")
    OUT = f"results/workspace/mindedness_facets_wide_{tag}.json"
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
    print(f"[load] {args.model} L={L}", flush=True)

    @torch.no_grad()
    def acts(text):
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=layers) as rec:
            model.forward(ids)
            return torch.stack([rec.activations[l][0, -1] for l in layers]).float().cpu().numpy()

    A = {}
    for tn, tmpl in TEMPLATES.items():
        for cls, exs in ENTITIES.items():
            for ei, e in enumerate(exs):
                for fac, attrs in FACETS.items():
                    for ai, a in enumerate(attrs):
                        A[(tn, cls, ei, fac, ai)] = acts(tmpl.format(e=e, a=a))
                for ai, a in enumerate(PHYSICAL):
                    A[(tn, cls, ei, "phys", ai)] = acts(tmpl.format(e=e, a=a))
        print(f"  [{tn}] {round(time.time()-t0)}s", flush=True)
    pol = []
    for tn, tmpl in TEMPLATES.items():
        w = tmpl.split("{e}")[0]
        y = np.mean([acts(f"{w}{q}?\nAnswer:") for q in POLARITY_YES], 0)
        n_ = np.mean([acts(f"{w}{q}?\nAnswer:") for q in POLARITY_NO], 0)
        pol.append(np.stack([unit(x) for x in (y - n_)]))
    v_pol = np.mean(pol, 0)

    classes, facets = list(ENTITIES), list(FACETS)

    def vfac(cls, fac, exs=None):
        exs = range(4) if exs is None else exs
        per_t = []
        for tn in TEMPLATES:
            m = np.mean([A[(tn, cls, e, fac, i)] for e in exs for i in range(4)], 0)
            p = np.mean([A[(tn, cls, e, "phys", i)] for e in exs for i in range(len(PHYSICAL))], 0)
            per_t.append(np.stack([unit(x) for x in (m - p)]))
        v = np.mean(per_t, 0)
        return np.stack([v[l] - np.dot(v[l], unit(v_pol[l])) * unit(v_pol[l]) for l in layers])

    V = {(c, f): vfac(c, f) for c in classes for f in facets}
    SH = {(c, f): (vfac(c, f, [0, 1]), vfac(c, f, [2, 3])) for c in classes for f in facets}
    band = [l for l in layers if 0.5 <= l/(L-1) <= 0.8]
    mb = lambda s: float(np.mean([s[l] for l in band]))
    rng = np.random.default_rng(0)
    floor = float(np.mean([abs(cos(rng.standard_normal(d), rng.standard_normal(d))) for _ in range(20)]))

    res = {"model": args.model, "facets": facets, "random_floor": floor}
    res["ceiling"] = {f: float(np.mean([mb([cos(SH[(c, f)][0][l], SH[(c, f)][1][l]) for l in layers])
                                        for c in classes])) for f in facets}
    res["facet_cos"] = {f"{a}|{b}": float(np.mean([mb([cos(V[(c, a)][l], V[(c, b)][l]) for l in layers])
                                                   for c in classes]))
                        for i, a in enumerate(facets) for b in facets[i+1:]}
    sf = {}
    for f in facets:
        sp = [mb([cos(V[("self", f)][l], V[(c, f)][l]) for l in layers]) for c in classes if c != "self"]
        op = [mb([cos(V[(a, f)][l], V[(b, f)][l]) for l in layers])
              for i, a in enumerate(classes[1:]) for b in classes[1:][i+1:]]
        sf[f] = {"self": float(np.mean(sp)), "other": float(np.mean(op)),
                 "gap": float(np.mean(op) - np.mean(sp))}
    res["self_outlier"] = sf
    # entity-pair structure per facet (which entities cluster, per facet)
    res["pairs_by_facet"] = {f: {f"{a}|{b}": mb([cos(V[(a, f)][l], V[(b, f)][l]) for l in layers])
                                 for i, a in enumerate(classes) for b in classes[i+1:]} for f in facets}

    # ---- S3 decode ----
    if args.decode and os.path.exists(LENS_PATH):
        try:
            lens = JacobianLens.load(LENS_PATH)
            dband = [l for l in BAND if l in lens.source_layers]
            mask = _meaningful_token_mask(tok, model._lm_head.weight.shape[0], DEVICE)
            ninf = torch.finfo(torch.float32).min

            @torch.no_grad()
            def decode(vl, k=12):
                score = None
                for l in dband:
                    v = torch.tensor(vl[l], dtype=torch.float32, device=DEVICE)
                    lg = model.unembed((v @ lens.jacobians[l].to(DEVICE).T).unsqueeze(0)).float()[0]
                    valid = lg[mask]
                    z = ((lg - valid.mean()) / (valid.std() + 1e-6)).masked_fill(~mask, ninf)
                    score = z if score is None else score + z
                return [tok.decode([int(i)]).strip() for i in score.topk(k).indices]
            res["decode"] = {f: decode(np.mean([V[(c, f)] for c in classes], 0)) for f in facets}
            res["decode"]["_random"] = decode(np.stack([rng.standard_normal(d) for _ in layers]))
        except Exception as e:
            res["decode"] = {"error": str(e)[:150]}
    res["runtime_min"] = round((time.time()-t0)/60, 1)
    json.dump(res, open(OUT, "w"), indent=1)

    print(f"\n=== CROSS-FACET COSINE (floor {floor:.3f}; ceilings "
          + " ".join(f"{f}={res['ceiling'][f]:.2f}" for f in facets) + ") ===")
    for k, v in sorted(res["facet_cos"].items(), key=lambda kv: -kv[1]):
        print(f"  {k:32} {v:+.3f}")
    print("\n=== SELF-OUTLIER GAP per facet (bigger = self more distinct) ===")
    for f, r in sorted(sf.items(), key=lambda kv: -kv[1]["gap"]):
        print(f"  {f:14} self={r['self']:+.3f} other={r['other']:+.3f} GAP={r['gap']:+.3f}")
    if "decode" in res and "error" not in res["decode"]:
        print("\n=== FACET DIRECTION DECODE ===")
        for f in facets + ["_random"]:
            print(f"  {f:14} " + ", ".join(res["decode"][f][:10]))
    print(f"\n[done] {res['runtime_min']} min -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
