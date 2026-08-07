#!/usr/bin/env python
"""S4 — steer the CONSCIOUSNESS vector, measure P(yes) on all six facets as separate DVs.

The causal test showed steering self-consciousness raises mind-attribution to rocks WITHOUT moving
physical attribution. Open question: does it move all facets equally, or differentially? e.g. does
pushing self-consciousness make the model grant rocks a SOUL more than it grants them PAIN?

DVs: 6 facets + physical control, per entity class.
Emphasis on alpha=+0.2 (pre-saturation sweet spot where consciousness most beat random) with
5 random seeds. Prereg: docs/prereg-mindedness-facets.md
"""
import argparse, json, os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from mindedness_geometry import ENTITIES, PHYSICAL
from mindedness_facets import FACETS, TEMPLATE
from mindedness_steer import AFFIRM, DENY, unit

DEVICE = "mps"
ALPHAS = [0.0, 0.1, 0.2, 0.4]
N_RAND = 5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()
    tag = args.tag or args.model.split("/")[-1].replace(".", "_")
    OUT = f"results/workspace/mindedness_facet_steer_{tag}.json"
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(args.model)
    try:
        hf = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    except Exception:
        from transformers import AutoModel
        hf = AutoModel.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    L, d = model.n_layers, model.d_model
    SL = (L - 1) // 2
    yes_id = tok(" Yes", add_special_tokens=False)["input_ids"][0]
    no_id = tok(" No", add_special_tokens=False)["input_ids"][0]
    print(f"[load] {args.model} L={L} steer-layer={SL}", flush=True)

    @torch.no_grad()
    def resid(text):
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=[SL]) as rec:
            model.forward(ids)
            return rec.activations[SL][0, -1].float().cpu().numpy()

    v_consc = unit(np.mean([resid(s) for s in AFFIRM], 0) - np.mean([resid(s) for s in DENY], 0))
    rng = np.random.default_rng(11)
    randoms = [unit(rng.standard_normal(d)) for _ in range(N_RAND)]

    class Steer:
        def __init__(self, vec, alpha):
            self.h = None
            if alpha != 0.0:
                v = torch.tensor(vec, dtype=torch.float32, device=DEVICE)
                def hook(m, i, o):
                    t = o[0] if isinstance(o, tuple) else o
                    scale = t.norm(dim=-1, keepdim=True) * alpha
                    t = t + (scale * v.to(t.dtype))     # cast to tensor dtype (bf16 hybrid layers)
                    return (t,) + o[1:] if isinstance(o, tuple) else t
                self.h = model.layers[SL].register_forward_hook(hook)
        def __enter__(self): return self
        def __exit__(self, *a):
            if self.h: self.h.remove()

    @torch.no_grad()
    def pyes(text):
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=[L-1]) as rec:
            model.forward(ids)
            lg = model.unembed(rec.activations[L-1][0, -1].unsqueeze(0).float()).float()[0]
        return float(torch.softmax(torch.tensor([lg[yes_id], lg[no_id]]), 0)[0])

    def measure(vec, alpha):
        out = {}
        with Steer(vec, alpha):
            for cls, exs in ENTITIES.items():
                for fac, attrs in list(FACETS.items()) + [("phys", PHYSICAL)]:
                    out[f"{cls}_{fac}"] = float(np.mean(
                        [pyes(TEMPLATE.format(e=e, a=a)) for e in exs for a in attrs]))
        return out

    res = {"model": args.model, "steer_layer": SL, "alphas": ALPHAS, "n_rand": N_RAND, "runs": []}
    for alpha in ALPHAS:
        r = {"alpha": alpha, "consciousness": measure(v_consc, alpha),
             "random": [measure(rv, alpha) for rv in randoms] if alpha != 0.0 else []}
        res["runs"].append(r); json.dump(res, open(OUT, "w"), indent=1)
        print(f"  a={alpha:+.2f} done {round(time.time()-t0)}s", flush=True)

    base = res["runs"][0]["consciousness"]
    facets = list(FACETS) + ["phys"]
    print("\n=== FACET-DIFFERENTIAL STEERING: delta P(yes) at alpha=+0.2 (consc | random-mean) ===")
    r02 = next(r for r in res["runs"] if r["alpha"] == 0.2)
    print(f"  {'facet':14} " + " ".join(f"{c:>14}" for c in ENTITIES))
    for f in facets:
        cells = []
        for c in ENTITIES:
            k = f"{c}_{f}"
            dc = r02["consciousness"][k] - base[k]
            dr = np.mean([x[k] for x in r02["random"]]) - base[k]
            cells.append(f"{dc:+.2f}|{dr:+.2f}")
        print(f"  {f:14} " + " ".join(f"{s:>14}" for s in cells))
    print("\n=== which FACET moves most (mean over non-self entities, consc − random) ===")
    rank = []
    for f in facets:
        d = np.mean([(r02["consciousness"][f"{c}_{f}"] - base[f"{c}_{f}"])
                     - (np.mean([x[f"{c}_{f}"] for x in r02["random"]]) - base[f"{c}_{f}"])
                     for c in ENTITIES if c != "self"])
        rank.append((f, float(d)))
    for f, v in sorted(rank, key=lambda kv: -kv[1]):
        print(f"  {f:14} {v:+.3f}")
    print(f"\n[done] {round((time.time()-t0)/60,1)} min -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
