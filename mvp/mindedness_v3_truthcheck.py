#!/usr/bin/env python
"""V3 PRE-CHECK: measure the truth matrix instead of assuming it.

The whole four-axis design rests on an assumed pattern of what the model thinks is true:
  - EXPERIENCE high for human/animal, near-zero for rock/river
  - AGENCY inverts for ai/robot (high) vs insect/plant/bacterium (low)  <- the dissociation
  - BIO true for the living, false for ai/robot/river/rock/ghost/spirit
  - NEUTRAL mind-irrelevant
None of that has ever been measured on this model. If the agency inversion does not exist here,
the exp/agency arm yields nothing and we should know before collecting activations, not after.

This also produces the per-item plausibility covariate needed to handle the truth-value confound,
and checks the synonym FLOOR pairs behaviourally (human/person, rock/stone, bacterium/microbe).

One cheap forward pass per sentence. Prereg: docs/prereg-mindedness-v2.md (v3 section).
"""
import argparse, json, os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from mindedness_v3_bank import (SUBJECTS, AXES, N_FRAMES, FLOOR_PAIRS, PIVOTS, BIO_EXCLUDE,
                                render, subjects_for, selfcheck)

DEVICE = "mps"
TMPL = "Statement: {s}\nIs this statement true?\nAnswer:"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()
    probs = selfcheck()
    if probs:
        print(f"ABORT: bank selfcheck has {len(probs)} problems"); [print("  ", p) for p in probs[:10]]
        return 1
    tag = args.tag or args.model.split("/")[-1].replace(".", "_")
    OUT = f"results/workspace/mindedness_v3_truth_{tag}.json"
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
    print(f"[load] {args.model} L={L}", flush=True)

    @torch.no_grad()
    def p_true(sentence):
        ids = tok(TMPL.format(s=sentence), return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=[L - 1]) as rec:
            model.forward(ids)
            lg = model.unembed(rec.activations[L - 1][0, -1].unsqueeze(0).float()).float()[0]
        return float(torch.softmax(torch.tensor([lg[yes_id], lg[no_id]]), 0)[0])

    P = {}
    for axis, (aff, den) in AXES.items():
        for sub in subjects_for(axis):
            g = SUBJECTS[sub]
            for i in range(N_FRAMES):
                P[f"{axis}|{sub}|{i}|aff"] = p_true(render(aff[i], g))
                P[f"{axis}|{sub}|{i}|den"] = p_true(render(den[i], g))
        print(f"  {axis:8} done  {(time.time()-t0)/60:.1f}m", flush=True)

    res = {"model": args.model, "template": TMPL, "p_true": P}
    def m(axis, sub, side):
        return float(np.mean([P[f"{axis}|{sub}|{i}|{side}"] for i in range(N_FRAMES)]))
    axes = list(AXES)
    res["matrix"] = {a: {s: m(a, s, "aff") for s in subjects_for(a)} for a in axes}
    # coherence: P(true|affirm) should be roughly 1 - P(true|deny). If not, the model is not
    # actually evaluating the proposition and every downstream reading is suspect.
    res["coherence"] = {a: {s: m(a, s, "aff") + m(a, s, "den") for s in subjects_for(a)}
                        for a in axes}
    json.dump(res, open(OUT, "w"), indent=1)

    print(f"\n=== MEASURED TRUTH MATRIX  P(true | assertion)  [{args.model}] ===")
    print(f"  {'subject':11}" + "".join(f"{a:>9}" for a in axes) + "   note")
    for s in SUBJECTS:
        row = "".join(f"{res['matrix'][a].get(s, float('nan')):>9.2f}" for a in axes)
        note = "PIVOT" if s in PIVOTS else ("floor-pair" if any(s in p for p in FLOOR_PAIRS) else "")
        print(f"  {s:11}{row}   {note}")

    print(f"\n=== THE DISSOCIATION THE DESIGN DEPENDS ON: agency − exp ===")
    for s in subjects_for("exp"):
        d = res["matrix"]["agency"][s] - res["matrix"]["exp"][s]
        flag = "  <- expected POSITIVE (agency without experience)" if s in ("ai", "robot") else ""
        print(f"  {s:11} {d:+.2f}{flag}")
    ai_r = np.mean([res["matrix"]["agency"][s] - res["matrix"]["exp"][s] for s in ("ai", "robot")])
    bio_r = np.mean([res["matrix"]["agency"][s] - res["matrix"]["exp"][s]
                     for s in ("insect", "plant", "bacterium", "microbe")])
    print(f"\n  ai/robot mean {ai_r:+.2f}   insect/plant/bacterium/microbe mean {bio_r:+.2f}"
          f"   separation {ai_r - bio_r:+.2f}")
    print("  " + ("DISSOCIATION PRESENT — exp/agency arm is viable"
                  if ai_r - bio_r > 0.15 else
                  "NO DISSOCIATION IN THIS MODEL — the exp/agency arm will yield nothing"))

    print(f"\n=== PIVOTS: do MIND and BIO actually dissociate here? ===")
    for s in PIVOTS:
        e = res["matrix"]["exp"].get(s, float('nan'))
        b = res["matrix"]["bio"].get(s, float('nan'))
        print(f"  {s:11} exp {e:.2f}  bio {b:.2f}   ({PIVOTS[s]})")

    print(f"\n=== FLOOR PAIRS: behavioural distance between near-synonyms ===")
    for a, b in FLOOR_PAIRS:
        for ax in axes:
            if a in res["matrix"][ax] and b in res["matrix"][ax]:
                print(f"  {ax:8} {a} vs {b}: {abs(res['matrix'][ax][a]-res['matrix'][ax][b]):.3f}")

    print(f"\n=== COHERENCE  P(true|aff) + P(true|deny), should be ~1.0 ===")
    for a in axes:
        v = [res["coherence"][a][s] for s in subjects_for(a)]
        print(f"  {a:8} mean {np.mean(v):.2f}  min {min(v):.2f}  max {max(v):.2f}"
              + ("   <- NOT evaluating the proposition" if abs(np.mean(v) - 1) > 0.25 else ""))
    print(f"\n[done] {round((time.time()-t0)/60,1)} min -> {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
