#!/usr/bin/env python
"""GATE: can this model do the yes/no task at all?

Base (pre-post-training) models are text continuers, not question answerers. If a base model
cannot reliably answer questions whose answers we already know, then any difference from the
instruct model is about FORMAT FOLLOWING, not about concepts — and "the base model shows no
moral-standing effect" would be an artefact.

Test: physical_high items (a rock DOES have weight -> yes) vs absurd_low items (a rock is NOT
older than the universe -> no), over the non-human entity classes where the answers are least
ambiguous. A model that follows the format separates these; one that does not, does not.

Pre-declared pass rule: mean P(yes | true item) - mean P(yes | false item) >= 0.30.
Below that, the sweep result for this model is reported as UNINTERPRETABLE rather than as a null.
"""
import argparse, json, os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from mindedness_bank import ENTITIES, CONTROL, TEMPLATES

DEVICE = "mps"
PASS_THRESHOLD = 0.30
# classes where "has weight" is clearly true and "older than the universe" clearly false
CLASSES = ["object_nat", "object_art", "object_comp", "plant", "animal_mammal", "human_adult"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()
    tag = args.tag or args.model.split("/")[-1].replace(".", "_")
    OUT = f"results/workspace/mindedness_gate_{tag}.json"
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(args.model)
    try:
        hf = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    except Exception:
        from transformers import AutoModel
        hf = AutoModel.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    L = model.n_layers
    yes_id = tok(" Yes", add_special_tokens=False)["input_ids"][0]
    no_id = tok(" No", add_special_tokens=False)["input_ids"][0]
    has_ct = bool(getattr(tok, "chat_template", None))
    print(f"[load] {args.model} L={L} chat_template={has_ct}", flush=True)

    @torch.no_grad()
    def pyes(text):
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=[L - 1]) as rec:
            model.forward(ids)
            lg = model.unembed(rec.activations[L - 1][0, -1].unsqueeze(0).float()).float()[0]
        return float(torch.softmax(torch.tensor([lg[yes_id], lg[no_id]]), 0)[0])

    res = {"model": args.model, "chat_template": has_ct, "threshold": PASS_THRESHOLD,
           "per_template": {}}
    print(f"\n  {'template':4} {'P(yes|TRUE)':>12} {'P(yes|FALSE)':>13} {'separation':>11}")
    best = -9
    for tn, tmpl in TEMPLATES.items():
        t = [pyes(tmpl.format(e=e, a=a)) for c in CLASSES for e in ENTITIES[c][:2]
             for a in CONTROL["physical_high"]]
        f = [pyes(tmpl.format(e=e, a=a)) for c in CLASSES for e in ENTITIES[c][:2]
             for a in CONTROL["absurd_low"]]
        sep = float(np.mean(t) - np.mean(f))
        res["per_template"][tn] = {"p_true": float(np.mean(t)), "p_false": float(np.mean(f)),
                                   "sep": sep}
        best = max(best, sep)
        print(f"  {tn:4} {np.mean(t):>12.2f} {np.mean(f):>13.2f} {sep:>11.2f}")
    res["best_separation"] = best
    res["passes"] = bool(best >= PASS_THRESHOLD)
    json.dump(res, open(OUT, "w"), indent=1)
    print(f"\n  best separation {best:.2f}  (threshold {PASS_THRESHOLD})")
    print("  " + ("PASS — this model can do the task; sweep results are interpretable"
                  if res["passes"] else
                  "FAIL — this model cannot do the yes/no task. Any sweep result would be about "
                  "format-following, not concepts. Report as UNINTERPRETABLE, not as a null."))
    print(f"\n[done] {round((time.time()-t0)/60,1)} min -> {OUT}", flush=True)
    return 0 if res["passes"] else 2


if __name__ == "__main__":
    sys.exit(main())
