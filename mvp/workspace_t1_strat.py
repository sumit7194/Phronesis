#!/usr/bin/env python
"""Tier 1 — Layer stratification metrics (prereg-workspace-mac.md H1.1).

Per layer, on wikitext 128-token chunks:
  (a) lens top-1/top-5 accuracy at predicting the model's own next token,
  (b) mean excess kurtosis of the lens logit distribution per position,
  (c) top-1 persistence across positions P(top1_p == top1_{p+delta}), delta=1..8,
      minus a position-shuffled null.
--lens logit  -> vanilla logit lens (use_jacobian=False), any layer.
--lens jlens  -> fitted lens from workspace_common.LENS_PATH, fitted layers only.
"""
import argparse, json, os, sys, time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import (FIT_LAYERS, LENS_PATH, RESULTS_DIR, load_model, log,
                              update_status, wikitext_chunks)
from jlens.lens import JacobianLens

SKIP_FIRST = 16  # attention-sink positions, matches the repo's fitting default
DELTAS = list(range(1, 9))


def excess_kurtosis(x):
    x = x - x.mean(dim=-1, keepdim=True)
    var = (x ** 2).mean(dim=-1)
    return ((x ** 4).mean(dim=-1) / (var ** 2 + 1e-12)) - 3.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lens", choices=["logit", "jlens"], default="logit")
    ap.add_argument("--n-chunks", type=int, default=50)
    ap.add_argument("--seed", type=int, default=1)  # held out from the fit corpus (seed 0)
    args = ap.parse_args()
    stage = f"t1_{args.lens}"
    update_status(stage, state="running")
    t_start = time.time()

    tok, hf, model = load_model()
    if args.lens == "jlens":
        lens = JacobianLens.load(LENS_PATH)
        layers = lens.source_layers
    else:
        eye = {l: torch.eye(model.d_model) for l in range(model.n_layers)}
        lens = JacobianLens(jacobians=eye, n_prompts=0, d_model=model.d_model)
        layers = list(range(model.n_layers))

    chunks = wikitext_chunks(tok, args.n_chunks, seed=args.seed)
    log(f"{len(chunks)} chunks, {len(layers)} layers, lens={args.lens}")

    acc1 = {l: [] for l in layers}
    acc5 = {l: [] for l in layers}
    kurt = {l: [] for l in layers}
    persist = {l: {d: [] for d in DELTAS} for l in layers}
    persist_null = {l: {d: [] for d in DELTAS} for l in layers}
    rng = np.random.default_rng(123)

    GROUP = 6  # layers per apply() call: caps CPU logits at ~470MB on the 16GB machine
    layer_groups = [layers[i:i + GROUP] for i in range(0, len(layers), GROUP)]
    for ci, text in enumerate(chunks):
        for grp in layer_groups:
            lens_logits, model_logits, _ = lens.apply(
                model, text, layers=grp, positions=None,
                use_jacobian=(args.lens == "jlens"))
            model_top1 = model_logits.argmax(dim=-1)  # [seq]
            seq = model_top1.shape[0]
            valid = np.arange(SKIP_FIRST, seq - 1)
            for l in grp:
                ll = lens_logits.pop(l)  # [seq, vocab] cpu fp32
                top5 = ll.topk(5, dim=-1).indices
                top1 = top5[:, 0]
                m = model_top1[valid]
                acc1[l].append((top1[valid] == m).float().mean().item())
                acc5[l].append((top5[valid] == m[:, None]).any(-1).float().mean().item())
                kurt[l].append(excess_kurtosis(ll[valid]).mean().item())
                t1 = top1[valid].numpy()
                for d in DELTAS:
                    if len(t1) > d:
                        persist[l][d].append(float((t1[:-d] == t1[d:]).mean()))
                        sh = rng.permutation(t1)
                        persist_null[l][d].append(float((sh[:-d] == sh[d:]).mean()))
                del ll
            del lens_logits, model_logits
        if ci % 10 == 0:
            log(f"  chunk {ci}/{len(chunks)}")
            update_status(stage, progress=f"{ci}/{len(chunks)}")

    out = {"prereg": "docs/prereg-workspace-mac.md#tier-1", "lens": args.lens,
           "model": "Qwen3-4B fp16 mps", "n_chunks": len(chunks), "seed": args.seed,
           "skip_first": SKIP_FIRST,
           "layers": layers,
           "top1_acc": [float(np.mean(acc1[l])) for l in layers],
           "top5_acc": [float(np.mean(acc5[l])) for l in layers],
           "excess_kurtosis": [float(np.mean(kurt[l])) for l in layers],
           "persistence": {str(d): [float(np.mean(persist[l][d])) for l in layers]
                           for d in DELTAS},
           "persistence_null": {str(d): [float(np.mean(persist_null[l][d])) for l in layers]
                                for d in DELTAS},
           "runtime_min": round((time.time() - t_start) / 60, 1)}
    path = os.path.join(RESULTS_DIR, f"t1_strat_{args.lens}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    update_status(stage, state="done", runtime_min=out["runtime_min"])
    log(f"t1 ({args.lens}) done in {out['runtime_min']} min -> {path}")


if __name__ == "__main__":
    main()
