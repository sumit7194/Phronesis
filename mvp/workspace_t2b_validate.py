#!/usr/bin/env python
"""Tier 2b — J-lens QC gate + causal swap positive control (prereg-workspace-mac.md).

QC gate:  lens-eval-multihop.json — does the unspoken intermediate (e.g. 'Brazil')
          surface in the lens top-10 at any (band layer, position)? J-lens vs logit lens.
Swaps:    probe-swap.json — patch in lens coordinates h <- h + strength*V(sigma(c)-c)
          at every prompt position across the band; success = greedy next token becomes
          swap_answer. Controls: 3-seed random-token swap (magnitude-matched by
          construction: same patch form, random target vector), no-op patch.
"""
import argparse, json, os, sys, time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import (BAND, JLENS_REPO_DATA, LENS_PATH, RESULTS_DIR,
                              lens_vectors, load_model, log, single_token_id,
                              update_status)
from jlens.hooks import ActivationRecorder
from jlens.lens import JacobianLens

RAND_WORDS = ["piano", "glacier", "helmet", "walnut", "lantern", "cactus", "violin",
              "harbor", "meadow", "falcon", "marble", "tunnel", "candle", "pepper",
              "throne", "anchor", "blanket", "compass", "dragon", "engine"]


def readout_ranks(model, lens, text, token_id, layers, use_jacobian, topk=10):
    """Best rank (1-based) of token_id over all (layer, position); also min layer/pos hit."""
    best = None
    lens_logits, _, _ = lens.apply(model, text, layers=layers, positions=None,
                                   use_jacobian=use_jacobian)
    for l in layers:
        ll = lens_logits[l]  # [seq, vocab]
        ranks = (ll > ll[:, token_id:token_id + 1]).sum(dim=1) + 1  # [seq]
        r = int(ranks.min().item())
        if best is None or r < best:
            best = r
    return best


class SwapHooks:
    """Forward hooks on band blocks applying h <- h + strength * V (sigma(c) - c)."""

    def __init__(self, model, vecs_s, vecs_t, layers, strength=1.0, noop=False):
        self.model, self.layers, self.strength, self.noop = model, layers, strength, noop
        self.mats = {}
        for l in layers:
            V = torch.stack([vecs_s[l], vecs_t[l]], dim=1)  # [d, 2] fp32
            self.mats[l] = (V, torch.linalg.pinv(V))  # pinv: [2, d]
        self.handles = []

    def __enter__(self):
        for l in self.layers:
            V, P = self.mats[l]
            V = V.to("mps"); P = P.to("mps")

            def hook(module, inputs, output, V=V, P=P):
                h = output[0] if not torch.is_tensor(output) else output
                c = h.float() @ P.T                     # [b, seq, 2]
                if self.noop:
                    return output
                delta = (c[..., [1, 0]] - c) @ V.T      # swap the two coordinates
                h2 = (h.float() + self.strength * delta).to(h.dtype)
                if torch.is_tensor(output):
                    return h2
                return (h2, *output[1:])

            self.handles.append(self.model.layers[l].register_forward_hook(hook))
        return self

    def __exit__(self, *exc):
        for h in self.handles:
            h.remove()
        self.handles = []


@torch.no_grad()
def greedy_next(model, hf, text):
    ids = model.encode(text, max_length=256)
    out = hf(input_ids=ids, use_cache=False)
    return int(out.logits[0, -1].argmax().item())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()
    update_status("t2b", state="running")
    t_start = time.time()
    rng = np.random.default_rng(args.seed)

    tok, hf, model = load_model()
    lens = JacobianLens.load(LENS_PATH)
    band = [l for l in BAND if l in lens.source_layers]
    log(f"lens n_prompts={lens.n_prompts}, band={band}")

    # ---------- QC gate: multihop intermediates in the readout ----------
    with open(os.path.join(JLENS_REPO_DATA, "evaluations", "lens-eval-multihop.json")) as f:
        mh = json.load(f)["items"]
    qc = {"jlens": [], "logit": []}
    for i, it in enumerate(mh):
        tid = single_token_id(tok, it["intermediates"][0])
        if tid is None:
            continue
        for mode in ("jlens", "logit"):
            r = readout_ranks(model, lens, it["prompt"], tid, band, mode == "jlens")
            qc[mode].append({"name": it["name"], "best_rank": r})
        if i % 20 == 0:
            log(f"  qc {i}/{len(mh)}")
            update_status("t2b", progress=f"qc {i}/{len(mh)}")
    qc_summary = {m: {"n": len(v),
                      "hit_top1": sum(x["best_rank"] == 1 for x in v),
                      "hit_top10": sum(x["best_rank"] <= 10 for x in v)}
                  for m, v in qc.items()}
    log(f"QC: {qc_summary}")

    # ---------- causal swaps ----------
    with open(os.path.join(JLENS_REPO_DATA, "experiments", "probe-swap.json")) as f:
        items = json.load(f)["items"]
    rand_ids = [single_token_id(tok, w) for w in RAND_WORDS]
    rand_ids = [r for r in rand_ids if r is not None]
    rows = []
    for i, it in enumerate(items):
        ids = {k: single_token_id(tok, it[k]) for k in
               ("intermediate", "answer", "swap_to", "swap_answer")}
        if any(v is None for v in ids.values()):
            rows.append({"name": it["name"], "skip": "multi-token"})
            continue
        base_next = greedy_next(model, hf, it["prompt"])
        base_ok = base_next == ids["answer"]
        row = {"name": it["name"], "category": it["category"], "base_ok": bool(base_ok),
               "base_next": tok.decode(base_next)}
        if base_ok:
            need = sorted({ids["intermediate"], ids["swap_to"], *rand_ids})
            vecs = lens_vectors(lens, model, need, band)
            idx = {t: j for j, t in enumerate(need)}
            vs = {l: vecs[l][idx[ids["intermediate"]]] for l in band}
            for strength in (1.0, 2.0):
                vt = {l: vecs[l][idx[ids["swap_to"]]] for l in band}
                with SwapHooks(model, vs, vt, band, strength=strength):
                    nxt = greedy_next(model, hf, it["prompt"])
                row[f"swap_s{strength:g}"] = tok.decode(nxt)
                row[f"swap_s{strength:g}_hit"] = nxt == ids["swap_answer"]
                row[f"swap_s{strength:g}_kept_base"] = nxt == ids["answer"]
            # no-op control: patch machinery active, sigma = identity
            with SwapHooks(model, vs, vt, band, noop=True):
                noop_next = greedy_next(model, hf, it["prompt"])
            row["noop_ok"] = noop_next == ids["answer"]
            # random-target control, 3 seeds
            row["rand_hits"], row["rand_broke_base"] = [], []
            for t in rng.choice(rand_ids, size=3, replace=False):
                vr = {l: vecs[l][idx[int(t)]] for l in band}
                with SwapHooks(model, vs, vr, band, strength=1.0):
                    nxt = greedy_next(model, hf, it["prompt"])
                row["rand_hits"].append(nxt == ids["swap_answer"])
                row["rand_broke_base"].append(nxt != ids["answer"])
        rows.append(row)
        if i % 10 == 0:
            log(f"  swap {i}/{len(items)}")
            update_status("t2b", progress=f"swap {i}/{len(items)}")

    gated = [r for r in rows if r.get("base_ok")]
    summary = {
        "n_items": len(items), "n_gated": len(gated),
        "swap_s1_hits": sum(r.get("swap_s1_hit", False) for r in gated),
        "swap_s2_hits": sum(r.get("swap_s2_hit", False) for r in gated),
        "noop_ok": sum(r.get("noop_ok", False) for r in gated),
        "rand_hits_total": sum(sum(r.get("rand_hits", [])) for r in gated),
        "rand_trials": sum(len(r.get("rand_hits", [])) for r in gated),
        "rand_broke_base": sum(sum(r.get("rand_broke_base", [])) for r in gated),
    }
    out = {"prereg": "docs/prereg-workspace-mac.md#tier-2b", "seed": args.seed,
           "lens_n_prompts": lens.n_prompts, "band": band,
           "qc_multihop": qc_summary, "qc_rows": qc,
           "swap_summary": summary, "swap_rows": rows,
           "runtime_min": round((time.time() - t_start) / 60, 1)}
    with open(os.path.join(RESULTS_DIR, "t2b_validate.json"), "w") as f:
        json.dump(out, f, indent=2)
    update_status("t2b", state="done", qc=qc_summary, swaps=summary,
                  runtime_min=out["runtime_min"])
    log(f"t2b done: QC {qc_summary} SWAPS {summary}")


if __name__ == "__main__":
    main()
