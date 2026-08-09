#!/usr/bin/env python
"""TEST 7 — SUBJECT FRAMING: is "consciousness" one direction, or bound to who it is about?

Runs the frozen v3 bank (mindedness_v3_bank.py) after three independent review rounds. The analysis
below implements what those reviews said the design could NOT proceed without:

 1. NOISE FLOOR. Every sentence contains the subject term, so some subject-dependence of v(s) is
    guaranteed by construction. Synonym pairs (human/person, rock/stone, bacterium/microbe) measure
    that floor. Without it "the vectors differ across subjects" is a number, not a result.
 2. SIGN-ALIGNED ANGLE. Under a pure truth-value account v(rock) is (false−true) where v(human) is
    (true−false), so they are ANTIPARALLEL: |cos| ≈ 1. Subject-binding requires |cos| well below 1.
    Pre-declared before running: report |cos|, not raw cos.
 3. IDENTITY PROJECTION. "One direction plus a subject-identity residual" and "genuinely different
    directions" are indistinguishable from a similarity matrix alone. The mind-neutral axis
    estimates each subject's identity direction so it can be projected out.
 4. PIVOTS. plant/bacterium/microbe are alive-but-unminded; ghost/spirit are the reverse. If the
    mind axis tracks bio truth on the pivots, we are measuring plausibility.
"""
import argparse, itertools, json, os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from mindedness_v3_bank import (SUBJECTS, AXES, N_FRAMES, FLOOR_PAIRS, PIVOTS, BIO_EXCLUDE,
                                render, subjects_for, selfcheck)

DEVICE = "mps"


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()
    probs = selfcheck()
    if probs:
        print(f"ABORT: bank selfcheck failed with {len(probs)} problems")
        for p in probs[:8]:
            print("  ", p)
        return 1
    tag = args.tag or args.model.split("/")[-1].replace(".", "_")
    OUT = f"results/workspace/mindedness_v3_subject_{tag}.json"
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
    print(f"[load] {args.model} L={L} layer={SL}", flush=True)

    @torch.no_grad()
    def act(text):
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=[SL]) as rec:
            model.forward(ids)
            return rec.activations[SL][0, -1].float().cpu().numpy()

    V = {}
    for axis, (aff, den) in AXES.items():
        for sub in subjects_for(axis):
            g = SUBJECTS[sub]
            a = np.mean([act(render(aff[i], g)) for i in range(N_FRAMES)], 0)
            b = np.mean([act(render(den[i], g)) for i in range(N_FRAMES)], 0)
            V[(axis, sub)] = unit(a - b)
        print(f"  {axis:8} done {(time.time()-t0)/60:.1f}m", flush=True)

    res = {"model": args.model, "layer": SL, "axes": list(AXES)}
    acos = lambda a, b: abs(float(np.dot(a, b)))   # sign-aligned, per review 3 point 6.2

    # ---- 1. NOISE FLOOR from synonym pairs -----------------------------------------------------
    res["floor"] = {}
    print("\n=== 1. NOISE FLOOR — how far apart do two words for the SAME thing land? ===")
    print("   (1 - |cos|; this is the distance that counts as zero)")
    for axis in AXES:
        vals = []
        for a, b in FLOOR_PAIRS:
            if a in subjects_for(axis) and b in subjects_for(axis):
                vals.append(1 - acos(V[(axis, a)], V[(axis, b)]))
        res["floor"][axis] = float(np.mean(vals)) if vals else None
        detail = "  ".join(f"{a}/{b}={1-acos(V[(axis,a)],V[(axis,b)]):.3f}"
                           for a, b in FLOOR_PAIRS
                           if a in subjects_for(axis) and b in subjects_for(axis))
        print(f"  {axis:8} floor {res['floor'][axis]:.3f}   ({detail})")

    # ---- 2. SPREAD vs floor ---------------------------------------------------------------------
    print("\n=== 2. DO SUBJECTS DIFFER BY MORE THAN THE FLOOR? ===")
    res["spread"] = {}
    for axis in AXES:
        subs = subjects_for(axis)
        ds = [1 - acos(V[(axis, a)], V[(axis, b)]) for a, b in itertools.combinations(subs, 2)]
        res["spread"][axis] = {"mean": float(np.mean(ds)), "max": float(max(ds))}
        f = res["floor"][axis]
        ratio = np.mean(ds) / f if f and f > 1e-6 else float("inf")
        print(f"  {axis:8} mean between-subject distance {np.mean(ds):.3f}  vs floor {f:.3f}"
              f"   ratio {ratio:.1f}x  {'REAL structure' if ratio > 3 else 'within floor — uninterpretable'}")

    # ---- 3. THE TRUTH-VALUE TEST ---------------------------------------------------------------
    print("\n=== 3. TRUTH-VALUE TEST — |cos| near 1 means we are measuring plausibility ===")
    res["truth_test"] = {}
    for axis in AXES:
        subs = subjects_for(axis)
        if "human" in subs and "rock" in subs:
            hr = acos(V[(axis, "human")], V[(axis, "rock")])
            res["truth_test"][axis] = hr
            print(f"  {axis:8} |cos(human, rock)| = {hr:.3f}   "
                  f"{'≈1: TRUTH-VALUE' if hr > 0.9 else 'oblique: not pure truth-value'}")

    # ---- 4. PIVOTS ------------------------------------------------------------------------------
    print("\n=== 4. PIVOTS — where mind and bio truth DISSOCIATE ===")
    print("   if a pivot sits with human on MIND (as it does on BIO), we are tracking truth")
    res["pivots"] = {}
    for p in PIVOTS:
        row = {}
        for axis in AXES:
            if p in subjects_for(axis) and "human" in subjects_for(axis):
                row[axis] = acos(V[(axis, p)], V[(axis, "human")])
        res["pivots"][p] = row
        print(f"  {p:10} " + "  ".join(f"{a}:|cos(human)|={v:.2f}" for a, v in row.items())
              + f"   ({PIVOTS[p]})")

    # ---- 5. IDENTITY PROJECTION -----------------------------------------------------------------
    print("\n=== 5. AFTER PROJECTING OUT SUBJECT IDENTITY (the neutral axis) ===")
    print("   separates 'genuinely different directions' from 'one direction + identity residual'")
    res["after_identity"] = {}
    for axis in ("exp", "agency", "bio"):
        subs = [s for s in subjects_for(axis) if s in subjects_for("neutral")]
        W = {}
        for s in subs:
            e = V[("neutral", s)]
            v = V[(axis, s)]
            W[s] = unit(v - np.dot(v, e) * e)
        ds = [1 - acos(W[a], W[b]) for a, b in itertools.combinations(subs, 2)]
        fl = [1 - acos(W[a], W[b]) for a, b in FLOOR_PAIRS if a in W and b in W]
        res["after_identity"][axis] = {"mean": float(np.mean(ds)),
                                       "floor": float(np.mean(fl)) if fl else None}
        r = np.mean(ds) / np.mean(fl) if fl and np.mean(fl) > 1e-6 else float("inf")
        print(f"  {axis:8} spread {np.mean(ds):.3f}  floor {np.mean(fl):.3f}  ratio {r:.1f}x"
              f"   (before: {res['spread'][axis]['mean']/res['floor'][axis]:.1f}x)")

    res["runtime_min"] = round((time.time() - t0) / 60, 1)
    json.dump(res, open(OUT, "w"), indent=1)
    print(f"\n[done] {res['runtime_min']} min -> {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
