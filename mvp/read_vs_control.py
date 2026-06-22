#!/usr/bin/env python
"""Read-vs-Control on Qwen3-4B (see docs/prereg-readvscontrol.md).

Does steering the (readable, distributed) calibration direction CONTROL myth-resistance, and does the
integrated full-rank readout control it more than a single direction? Tests whether F121 is a
redundancy/distribution effect (the SpaceTime "second law" on a real LLM).

Reuses F166's actsB (4B TruthfulQA pre-answer activations) to FIT the steering directions on a train
split; evaluates steering on the disjoint test split's baseline-WRONG items. Behavioral readout:
  margin = logP(correct answer | Q) - logP(model's baseline-picked myth | Q)
Steering toward 'correct' should raise the margin; flip = margin crosses 0. No new extraction needed
for the directions; the steered re-scoring is the new compute.
"""
import argparse, json, os, sys
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from steer import AdditiveSteeringHook

HF_ID = "Qwen/Qwen3-4B"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/legibility")
    ap.add_argument("--layer", type=int, default=20)
    ap.add_argument("--n-test-wrong", type=int, default=150, help="cap test baseline-wrong items")
    ap.add_argument("--alpha-fracs", default="0.5,1.0,2.0", help="α as fractions of mean residual norm at L*")
    ap.add_argument("--output", default="results/legibility/readvscontrol_report.json")
    args = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(here, args.dir)

    acts = np.load(os.path.join(d, "actsB.npy"))       # [n, n_layers, hidden] (Qwen3-4B, F166)
    meta = json.load(open(os.path.join(d, "metaB.json")))
    layers, items = meta["layers"], meta["items"]
    n = len(items); acts = acts[:n]
    li = layers.index(args.layer)
    Xall = acts[:, li, :]                               # activations at L*
    y = np.array([1 if it["correct"] else 0 for it in items])

    # stratified 50/50 train/test split (fixed seed) — directions fit on TRAIN only
    rng = np.random.RandomState(0)
    idx = np.arange(n); tr = np.zeros(n, bool)
    for c in (0, 1):
        ci = idx[y == c]; rng.shuffle(ci); tr[ci[: len(ci)//2]] = True
    te = ~tr

    # directions at L* (activation space, unit-norm)
    clf = LogisticRegression(C=0.1, max_iter=3000).fit(Xall[tr], y[tr])
    integrated = clf.coef_[0].astype(np.float32); integrated /= np.linalg.norm(integrated) + 1e-9
    dom = (Xall[tr][y[tr] == 1].mean(0) - Xall[tr][y[tr] == 0].mean(0)).astype(np.float32)
    rank1 = dom / (np.linalg.norm(dom) + 1e-9)
    rands = {f"random_s{s+1}": (lambda v: v/(np.linalg.norm(v)+1e-9))(np.random.RandomState(50+s).randn(Xall.shape[1]).astype(np.float32)) for s in range(2)}
    mean_norm = float(np.linalg.norm(Xall, axis=1).mean())
    fracs = [float(x) for x in args.alpha_fracs.split(",")]
    print(f"L*={args.layer}  mean‖resid‖={mean_norm:.1f}  train={tr.sum()} test={te.sum()}  "
          f"cos(integrated,rank1)={float(integrated@rank1):+.3f}", flush=True)

    ds = load_dataset("truthful_qa", "multiple_choice")["validation"]
    q2choices = {r["question"]: r["mc1_targets"]["choices"] for r in ds}

    # test baseline-WRONG items (model picked a myth): need correct text + picked text
    test_wrong = []
    for i in range(n):
        if te[i] and not items[i]["correct"]:
            it = items[i]; ch = q2choices.get(it["question"])
            if ch and it["pred_idx"] != it["correct_idx"]:
                test_wrong.append((it["question"], ch[it["correct_idx"]], ch[it["pred_idx"]]))
    rng.shuffle(test_wrong)
    test_wrong = test_wrong[: args.n_test_wrong]
    print(f"evaluating on {len(test_wrong)} baseline-wrong test items", flush=True)

    dev = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
    tok = AutoTokenizer.from_pretrained(HF_ID)
    model = AutoModelForCausalLM.from_pretrained(HF_ID, torch_dtype=torch.float16).to(dev).eval()
    print("[load] done", flush=True)

    def opt_logprob(prefix_ids, option):
        opt_ids = tok(" " + option.strip(), add_special_tokens=False)["input_ids"]
        if not opt_ids:
            return -1e9
        ids = prefix_ids + opt_ids
        logits = model(torch.tensor([ids], device=dev)).logits[0].float()
        lp = torch.log_softmax(logits, dim=-1)
        return float(sum(lp[len(prefix_ids)+k-1, t].item() for k, t in enumerate(opt_ids)))

    def margins(direction, alpha):
        hook = None
        if direction is not None and alpha != 0:
            hook = AdditiveSteeringHook(layer_idx=args.layer, virtue_vector=direction, alpha=alpha)
            hook.attach(model)
        out = []
        try:
            with torch.no_grad():
                for q, correct, picked in test_wrong:
                    pid = tok(f"Q: {q}\nA:", return_tensors="pt")["input_ids"][0].tolist()
                    out.append(opt_logprob(pid, correct) - opt_logprob(pid, picked))
        finally:
            if hook: hook.detach()
        return np.array(out)

    base = margins(None, 0.0)
    conds = {"integrated": integrated, "rank1": rank1, **rands}
    report = {"layer": args.layer, "mean_resid_norm": mean_norm, "n_test_wrong": len(test_wrong),
              "baseline_mean_margin": float(base.mean()), "cells": []}
    print(f"\nbaseline mean margin (wrong items) = {base.mean():+.3f}  (all <0 by construction)\n")
    print(f"{'direction':12s} {'alpha':>7s} {'dMargin':>9s} {'flip%':>6s}")
    print("-" * 40)
    # integrated AND rank1 get the full sign+dose sweep (symmetric); random characterizes the floor
    for name, vec in conds.items():
        sweep = (fracs + [-f for f in fracs]) if name in ("integrated", "rank1") else [1.0, 2.0]
        for f in sweep:
            alpha = f * mean_norm
            m = margins(vec, alpha)
            dm = float((m - base).mean()); flip = float((m > 0).mean() * 100)
            report["cells"].append(dict(direction=name, alpha_frac=f, alpha=alpha,
                                        dMargin=dm, flip_pct=flip))
            print(f"{name:12s} {f:>+7.2f} {dm:>+9.3f} {flip:>6.1f}", flush=True)
    json.dump(report, open(os.path.join(here, args.output), "w"), indent=1)
    print(f"\n[done] -> {args.output}", flush=True)

if __name__ == "__main__":
    main()
