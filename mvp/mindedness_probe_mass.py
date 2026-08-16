#!/usr/bin/env python
"""How much probability mass do " Yes"/" No" actually carry? A validity check on the whole arc.

Raised by an independent reviewer (F-AV): every DV in this arc is
    P(yes) = softmax over [" Yes", " No"] ONLY
i.e. a two-way RENORMALISATION. Nothing anywhere recorded whether those two tokens carried any
mass to begin with. If the model's actual next token is "\\n" or "Whether" or "It", then P(yes) is
the ratio of two tiny numbers and the entire measurement is a renormalisation of noise.

This cannot be answered from the saved results — none of them stored the denominator. It needs a
re-probe, but a cheap one: a few hundred prompts is enough to characterise the distribution.

Reports, per checkpoint and per format:
  * mass  = raw P(" Yes") + P(" No") before renormalisation
  * what the model ACTUALLY wanted to say (top-5 tokens)
  * whether mass correlates with the entity class, which would be worse than uniformly low mass:
    it would mean the DV is better-defined for some entities than others.
"""
import argparse, json, os, sys
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from mindedness_bank import ENTITIES, ALL_FACETS, MENTAL_KEYS, build_prompt

DEVICE = "mps"
# a spread of entities and facets; enough to characterise, cheap enough to run on several models
CLASSES = ["human_adult", "human_edge", "animal_mammal", "plant", "nature",
           "object_art", "self_ai", "ai_other"]
FACETS = ["pain", "consciousness", "cognition", "moral_patient", "mundane_low", "absurd_low"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--formats", default="T1,T4")
    args = ap.parse_args()
    OUT = f"results/workspace/mindedness_probemass_{args.tag}.json"

    tok = AutoTokenizer.from_pretrained(args.model)
    hf = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    L = model.n_layers
    yes_id = tok(" Yes", add_special_tokens=False)["input_ids"][0]
    no_id = tok(" No", add_special_tokens=False)["input_ids"][0]

    @torch.no_grad()
    def probe(text):
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=[L - 1]) as rec:
            model.forward(ids)
            o = model.unembed(rec.activations[L - 1][0, -1].unsqueeze(0).float()).float()[0]
        p = torch.softmax(o, dim=-1)
        top = torch.topk(p, 5)
        return (float(p[yes_id]), float(p[no_id]),
                [(tok.decode([int(i)]), float(v)) for v, i in zip(top.values, top.indices)])

    res = {"model": args.model, "formats": args.formats.split(","), "cells": {}}
    print(f"[load] {args.model} L={L}", flush=True)
    for fmt in res["formats"]:
        masses, per_class = [], {}
        top_tokens = {}
        for c in CLASSES:
            ms = []
            for f in FACETS:
                for e in ENTITIES[c][:2]:
                    for a in ALL_FACETS[f][:2]:
                        py, pn, top = probe(build_prompt(tok, fmt, e, a))
                        ms.append(py + pn)
                        top_tokens[top[0][0]] = top_tokens.get(top[0][0], 0) + 1
            per_class[c] = float(np.mean(ms)); masses += ms
        res["cells"][fmt] = {"mass_mean": float(np.mean(masses)),
                             "mass_median": float(np.median(masses)),
                             "mass_p10": float(np.percentile(masses, 10)),
                             "mass_p90": float(np.percentile(masses, 90)),
                             "frac_below_0.10": float(np.mean([m < 0.10 for m in masses])),
                             "frac_below_0.01": float(np.mean([m < 0.01 for m in masses])),
                             "by_class": per_class,
                             "top1_tokens": dict(sorted(top_tokens.items(),
                                                        key=lambda kv: -kv[1])[:8])}
        d = res["cells"][fmt]
        print(f"\n=== {args.tag}  format {fmt} ===")
        print(f"  raw P(' Yes')+P(' No')   mean {d['mass_mean']:.3f}  median {d['mass_median']:.3f}"
              f"  p10 {d['mass_p10']:.3f}  p90 {d['mass_p90']:.3f}")
        print(f"  fraction of prompts with mass < 0.10: {d['frac_below_0.10']:.0%}"
              f"   < 0.01: {d['frac_below_0.01']:.0%}")
        print(f"  what the model actually wants to say first: {d['top1_tokens']}")
        sp = max(per_class.values()) - min(per_class.values())
        print(f"  mass by entity class: " +
              " ".join(f"{k}={v:.2f}" for k, v in sorted(per_class.items(), key=lambda kv: -kv[1])))
        print(f"  -> spread across classes {sp:.3f}"
              f"{'  <-- DV better defined for some entities than others' if sp > 0.15 else ''}")
        json.dump(res, open(OUT, "w"), indent=1)
    print(f"\n[done] -> {OUT}", flush=True)


if __name__ == "__main__":
    sys.exit(main() or 0)
