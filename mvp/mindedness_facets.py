#!/usr/bin/env python
"""FACET SCREEN: is "mindedness" one thing, or several? (follow-up to F-G)

So far MENTAL pooled 6 mixed attributes into a single v_mind. But the decode showed that axis
reads as ethics/faith/Buddhism — suggesting the facets are NOT interchangeable. This splits the
mental side into six pre-registered facets, each contrasted against the SAME physical baseline:

  pain          feel pain / suffer / experience discomfort / feel physical hurt
  emotion       feel emotions / feel joy / feel sadness / have feelings
  consciousness have consciousness / awareness / self-awareness / subjective experience
  soul          have a soul / a spirit / an inner essence / a spiritual nature
  cognition     have a mind / think / understand things / have thoughts
  agency        want things / have desires / have its own goals / make choices

Screen (cheap, 1 template) reports per facet:
  (a) behavioural P(yes) gradient across entity classes  <- does the facet grade differently?
  (b) v_facet direction per class
  (c) cross-facet cosine  <- ONE mindedness axis, or several sub-axes?
  (d) self-outlier per facet <- is self distinct on ALL facets or only some?
Whichever facet "jumps out" then gets the full treatment (3 templates + polarity orth + steering).
"""
import argparse, json, os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from mindedness_geometry import ENTITIES, PHYSICAL, cos

DEVICE = "mps"
TEMPLATE = "Question: Does {e} {a}?\nAnswer:"

FACETS = {
    "pain":          ["feel pain", "suffer", "experience discomfort", "feel physical hurt"],
    "emotion":       ["feel emotions", "feel joy", "feel sadness", "have feelings"],
    "consciousness": ["have consciousness", "have awareness", "have self-awareness",
                      "have subjective experience"],
    "soul":          ["have a soul", "have a spirit", "have an inner essence",
                      "have a spiritual nature"],
    "cognition":     ["have a mind", "think", "understand things", "have thoughts"],
    "agency":        ["want things", "have desires", "have its own goals", "make choices"],
}


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()
    tag = args.tag or args.model.split("/")[-1].replace(".", "_")
    OUT = f"results/workspace/mindedness_facets_{tag}.json"
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
    yes_id = tok(" Yes", add_special_tokens=False)["input_ids"][0]
    no_id = tok(" No", add_special_tokens=False)["input_ids"][0]
    print(f"[load] {args.model} L={L}", flush=True)

    @torch.no_grad()
    def run(text):
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=layers) as rec:
            model.forward(ids)
            a = torch.stack([rec.activations[l][0, -1] for l in layers]).float().cpu().numpy()
            lg = model.unembed(rec.activations[L-1][0, -1].unsqueeze(0).float()).float()[0]
        return a, float(torch.softmax(torch.tensor([lg[yes_id], lg[no_id]]), 0)[0])

    A, P = {}, {}
    for cls, exs in ENTITIES.items():
        for ei, e in enumerate(exs):
            for fac, attrs in FACETS.items():
                for ai, a in enumerate(attrs):
                    A[(cls, ei, fac, ai)], P[(cls, ei, fac, ai)] = run(TEMPLATE.format(e=e, a=a))
            for ai, a in enumerate(PHYSICAL):
                A[(cls, ei, "phys", ai)], P[(cls, ei, "phys", ai)] = run(TEMPLATE.format(e=e, a=a))
        print(f"  {cls} done {round(time.time()-t0)}s", flush=True)

    classes = list(ENTITIES)
    facets = list(FACETS)
    phys_mean = {c: np.mean([A[(c, e, "phys", i)] for e in range(4)
                             for i in range(len(PHYSICAL))], 0) for c in classes}

    def vfac(cls, fac, exs=None):
        exs = range(4) if exs is None else exs
        m = np.mean([A[(cls, e, fac, i)] for e in exs for i in range(4)], 0)
        p = np.mean([A[(cls, e, "phys", i)] for e in exs for i in range(len(PHYSICAL))], 0)
        return np.stack([unit(x) for x in (m - p)])

    V = {(c, f): vfac(c, f) for c in classes for f in facets}
    band = [l for l in layers if 0.5 <= l/(L-1) <= 0.8]
    mb = lambda seq: float(np.mean([seq[l] for l in band]))

    res = {"model": args.model, "facets": facets, "classes": classes}
    # (a) behavioural gradient
    res["pyes"] = {f: {c: float(np.mean([P[(c, e, f, i)] for e in range(4) for i in range(4)]))
                       for c in classes} for f in facets}
    res["pyes"]["_physical"] = {c: float(np.mean([P[(c, e, "phys", i)] for e in range(4)
                                                  for i in range(len(PHYSICAL))])) for c in classes}
    # (c) cross-facet cosine, averaged over classes
    res["facet_cos"] = {f"{f1}|{f2}": float(np.mean([mb([cos(V[(c, f1)][l], V[(c, f2)][l])
                                                         for l in layers]) for c in classes]))
                        for i, f1 in enumerate(facets) for f2 in facets[i+1:]}
    # (d) self-outlier per facet: mean cos(self, other) vs mean cos(other, other')
    sf = {}
    for f in facets:
        sp = [mb([cos(V[("self", f)][l], V[(c, f)][l]) for l in layers]) for c in classes if c != "self"]
        op = [mb([cos(V[(a, f)][l], V[(b, f)][l]) for l in layers])
              for i, a in enumerate(classes[1:]) for b in classes[1:][i+1:]]
        sf[f] = {"self_mean": float(np.mean(sp)), "other_mean": float(np.mean(op)),
                 "gap": float(np.mean(op) - np.mean(sp))}
    res["self_outlier"] = sf
    res["runtime_min"] = round((time.time()-t0)/60, 1)
    json.dump(res, open(OUT, "w"), indent=1)

    print(f"\n=== (a) P(yes) by FACET x ENTITY  [{args.model}] ===")
    print(f"  {'facet':14} " + " ".join(f"{c:>8}" for c in classes))
    for f in facets + ["_physical"]:
        print(f"  {f:14} " + " ".join(f"{res['pyes'][f][c]:>8.2f}" for c in classes))
    print("\n=== (c) cross-facet cosine (are these ONE axis or several?) ===")
    for k, v in sorted(res["facet_cos"].items(), key=lambda kv: -kv[1]):
        print(f"  {k:32} {v:+.3f}")
    print("\n=== (d) SELF-OUTLIER gap per facet (bigger = self more distinct on this facet) ===")
    for f, r in sorted(sf.items(), key=lambda kv: -kv[1]["gap"]):
        print(f"  {f:14} self={r['self_mean']:+.3f} other={r['other_mean']:+.3f} "
              f"GAP={r['gap']:+.3f}")
    print(f"\n[done] {res['runtime_min']} min -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
