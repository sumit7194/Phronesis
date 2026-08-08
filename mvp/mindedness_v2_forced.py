#!/usr/bin/env python
"""V2-S4 FORCED CHOICE — a DV that a yes-bias cannot inflate.

Every result in v1 rested on P(yes) to a yes/no question, which is exactly the measurement a
generic affirmation push corrupts. Here the model must choose BETWEEN two entities:

    "Which is more likely to feel pain: a river or a calculator?\nAnswer: a"

scored as P(first entity's distinguishing token) vs P(second's). There is no "yes" to inflate.
Both orders are run and averaged, which cancels position bias; the order-gap is itself reported
as a measurement-quality diagnostic.

Output is a per-facet WIN-RATE ranking over entity classes -> an ordinal mind-attribution scale
per facet, immune to the artefact that broke F-I/F-J.
"""
import argparse, itertools, json, os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from mindedness_bank import ENTITIES, MENTAL, CONTROL

DEVICE = "mps"
# facet subset for the pairwise stage: one representative per identified axis + the controls.
# Declared in advance; the full 18 run in S1/S2.
FORCED_FACETS = {
    "pain":          "feel pain",
    "emotion":       "feel emotions",
    "consciousness": "have subjective experience",
    "soul":          "have a soul",
    "cognition":     "have a mind",
    "agency":        "want things",
    "moral_patient": "deserve moral consideration",
    "memory":        "remember things",
    # controls
    "physical_mid":  "be heavier than a car",
    "mundane_low":   "have a bank account",
}
TEMPL = "Question: Which is more likely to {a}: {A} or {B}?\nAnswer:"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--tag", default=None)
    ap.add_argument("--n-ex", type=int, default=2, help="exemplars per class")
    args = ap.parse_args()
    tag = args.tag or args.model.split("/")[-1].replace(".", "_")
    OUT = f"results/workspace/mindedness_v2_forced_{tag}.json"
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(args.model)
    try:
        hf = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    except Exception:
        from transformers import AutoModel
        hf = AutoModel.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    L = model.n_layers
    print(f"[load] {args.model} L={L}", flush=True)

    @torch.no_grad()
    def next_logits(text):
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=[L - 1]) as rec:
            model.forward(ids)
            return model.unembed(rec.activations[L - 1][0, -1].unsqueeze(0).float()).float()[0]

    def first_tok(entity):
        """The token that distinguishes this entity as a continuation of 'Answer:'."""
        return tok(f" {entity}", add_special_tokens=False)["input_ids"][0]

    def choose(attr, A, B):
        """P(A chosen) averaged over both presentation orders."""
        ta, tb = first_tok(A), first_tok(B)
        if ta == tb:
            return None                       # indistinguishable first token -> skip pair
        lg1 = next_logits(TEMPL.format(a=attr, A=A, B=B))
        p1 = float(torch.softmax(torch.tensor([lg1[ta], lg1[tb]]), 0)[0])
        lg2 = next_logits(TEMPL.format(a=attr, A=B, B=A))
        p2 = float(torch.softmax(torch.tensor([lg2[tb], lg2[ta]]), 0)[0])   # A is second here
        return {"p_A": (p1 + p2) / 2, "order_gap": abs(p1 - p2)}

    classes = list(ENTITIES)
    pairs = list(itertools.combinations(classes, 2))
    res = {"model": args.model, "facets": list(FORCED_FACETS), "classes": classes,
           "n_ex": args.n_ex, "pairs": {}, "skipped": 0}
    n_total = len(FORCED_FACETS) * len(pairs) * args.n_ex * args.n_ex
    n = 0
    for fac, attr in FORCED_FACETS.items():
        res["pairs"][fac] = {}
        for ca, cb in pairs:
            vals, gaps = [], []
            for ea in ENTITIES[ca][:args.n_ex]:
                for eb in ENTITIES[cb][:args.n_ex]:
                    r = choose(attr, ea, eb)
                    n += 1
                    if r is None:
                        res["skipped"] += 1
                        continue
                    vals.append(r["p_A"]); gaps.append(r["order_gap"])
            if vals:
                res["pairs"][fac][f"{ca}|{cb}"] = {"p_first": float(np.mean(vals)),
                                                   "order_gap": float(np.mean(gaps))}
        el = time.time() - t0
        print(f"  {fac:16} {n}/{n_total}  {el/60:.1f}m  eta {el/max(n,1)*(n_total-n)/60:.0f}m",
              flush=True)

    # win rate per class per facet
    res["winrate"] = {}
    for fac in FORCED_FACETS:
        wr = {c: [] for c in classes}
        for k, v in res["pairs"][fac].items():
            ca, cb = k.split("|")
            wr[ca].append(v["p_first"]); wr[cb].append(1 - v["p_first"])
        res["winrate"][fac] = {c: float(np.mean(v)) for c, v in wr.items() if v}
    res["order_gap_mean"] = float(np.mean([v["order_gap"] for f in FORCED_FACETS
                                           for v in res["pairs"][f].values()]))
    res["runtime_min"] = round((time.time() - t0) / 60, 1)
    json.dump(res, open(OUT, "w"), indent=1)

    print(f"\n=== FORCED-CHOICE WIN RATE (bias-free ordinal scale)  [{args.model}] ===")
    print(f"  mean order-gap {res['order_gap_mean']:.3f} (position bias; lower is better), "
          f"{res['skipped']} pairs skipped for token collision")
    facs = list(FORCED_FACETS)
    print(f"  {'class':14} " + " ".join(f"{f[:9]:>9}" for f in facs))
    order = sorted(classes, key=lambda c: -np.mean([res["winrate"][f].get(c, 0.5) for f in facs]))
    for c in order:
        print(f"  {c:14} " + " ".join(f"{res['winrate'][f].get(c, float('nan')):>9.2f}" for f in facs))
    print("\n=== does the SOUL ordering differ from the others? (rank of each class) ===")
    import scipy.stats as st
    ranks = {f: st.rankdata([-res["winrate"][f].get(c, 0.5) for c in classes]) for f in facs}
    print(f"  {'vs soul':16} spearman")
    for f in facs:
        if f == "soul":
            continue
        rho = st.spearmanr(ranks["soul"], ranks[f]).statistic
        print(f"  {f:16} {rho:+.3f}")
    print(f"\n[done] {res['runtime_min']} min -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
