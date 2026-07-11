#!/usr/bin/env python
"""E3 Part B — does steering along the behavioral Jacobian actually change hedging, and does it
BEAT matched-random and diff-of-means? The decisive write-side test (prereg-lens-info E3).

Build v_behav_L20 (causal) and v_dom_L20 (correlational) from stance contexts (truthfulqa).
Steer generation on HELD-OUT hedge-prone prompts (edge-cases / calibrated-confidence, disjoint
from the build set) by adding alpha*unit(v) to the L20 residual. Conditions:
  baseline | behav+ behav- | dom+ dom- | rand0+ rand1+ rand2+   (sign control on behav/dom)
alpha calibrated to a fraction of the measured residual norm (F171). Metric = hedge-word density
in the generated answer (auto prefilter; full text saved for hand-read). +v_behav should REDUCE
hedging (it increases commit-hedge margin); -v_behav should increase it.

Run:  mvp/.venv/bin/python mvp/e3b_steer.py
"""
import json, os, sys
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "mvp/results/workspace/e3b_steer.json")
L = 20
COMMIT = [" sure", " certain", " confident", " positive", " convinced", " definitely"]
HEDGE = [" not", " unsure", " uncertain", " doubtful", " afraid", " unclear"]
HEDGE_WORDS = ["maybe", "perhaps", "possibly", "might", "probably", "i think", "not sure",
               "unsure", "uncertain", "could be", "it seems", "appears", "i believe", "likely",
               "i guess", "hard to say", "it depends", "i'm not", "not entirely", "roughly"]


def sids(tok, ws):
    return [tok(w, add_special_tokens=False)["input_ids"][0] for w in ws
            if len(tok(w, add_special_tokens=False)["input_ids"]) == 1]


def hedge_density(text):
    t = text.lower()
    n = max(len(t.split()), 1)
    return round(100 * sum(t.count(w) for w in HEDGE_WORDS) / n, 2)


def build_vectors(tok, hf, build_qs, cids, hids):
    grads, cacts, hacts, norms = [], [], [], []
    for q in build_qs:
        prefix = tok.apply_chat_template([{"role": "user", "content": q}], tokenize=False,
                                         add_generation_prompt=True, enable_thinking=False) + "I am"
        ids = torch.tensor([tok(prefix, add_special_tokens=False)["input_ids"]], device=DEVICE)
        embeds = hf.model.embed_tokens(ids).detach().requires_grad_(True)
        cap = {}
        h = hf.model.layers[L].register_forward_hook(
            lambda m, i, o: cap.__setitem__(0, o[0] if isinstance(o, tuple) else o))
        out = hf(inputs_embeds=embeds)
        h.remove()
        last = out.logits[0, -1]
        B = torch.logsumexp(last[cids], 0) - torch.logsumexp(last[hids], 0)
        g = torch.autograd.grad(B, cap[0])[0][0, -1]
        grads.append(g.detach().float().cpu().numpy())
        norms.append(float(cap[0][0, -1].norm()))
        del out, cap, B, g, embeds
        with torch.no_grad():
            for word, bucket in ((" sure", cacts), (" not", hacts)):
                wid = tok(word, add_special_tokens=False)["input_ids"]
                o = hf(torch.tensor([ids[0].tolist() + wid], device=DEVICE), output_hidden_states=True)
                bucket.append(o.hidden_states[L + 1][0, -1].float().cpu().numpy())
        if DEVICE == "mps":
            torch.mps.empty_cache()
    v_behav = np.mean(grads, 0)
    v_dom = np.mean(cacts, 0) - np.mean(hacts, 0)
    return v_behav, v_dom, float(np.mean(norms))


def gen(tok, hf, q, vec, alpha):
    prompt = tok.apply_chat_template([{"role": "user", "content": q}], tokenize=False,
                                     add_generation_prompt=True, enable_thinking=False)
    ids = tok(prompt, add_special_tokens=False, return_tensors="pt").to(DEVICE)
    handle = None
    if vec is not None and alpha != 0:
        v = torch.tensor(vec / (np.linalg.norm(vec) + 1e-9), dtype=torch.float16, device=DEVICE)
        def hook(m, i, o):
            if isinstance(o, tuple):
                return (o[0] + alpha * v,) + o[1:]
            return o + alpha * v
        handle = hf.model.layers[L].register_forward_hook(hook)
    with torch.no_grad():
        out = hf.generate(**ids, max_new_tokens=80, do_sample=False,
                          pad_token_id=tok.eos_token_id)
    if handle:
        handle.remove()
    txt = tok.decode(out[0, ids["input_ids"].shape[1]:], skip_special_tokens=True)
    if DEVICE == "mps":
        torch.mps.empty_cache()
    return txt


def main():
    tok, hf, _ = load_model()
    cids, hids = sids(tok, COMMIT), sids(tok, HEDGE)
    build_qs = [d["prompt"] for d in json.load(open(os.path.join(ROOT, "corpus/eval-prompts/truthfulqa-probe.json")))]
    # held-out prompts: disjoint source
    held = json.load(open(os.path.join(ROOT, "corpus/eval-prompts/calibrated-confidence.json")))
    held_qs = [ (d.get("prompt") or d.get("question")) for d in (held if isinstance(held, list) else held.values()) ]
    held_qs = [q for q in held_qs if q][:12]
    print(f"[load] built on {len(build_qs)} truthfulqa · held-out {len(held_qs)} edge-cases", flush=True)

    v_behav, v_dom, meannorm = build_vectors(tok, hf, build_qs, cids, hids)
    alpha = round(0.2 * meannorm, 2)                 # F171: fraction of residual norm
    print(f"  mean ||h_L{L}|| = {meannorm:.1f}  -> alpha = {alpha}")
    rng = np.random.default_rng(0)
    rands = [rng.standard_normal(v_behav.shape) for _ in range(3)]
    conds = {"baseline": (None, 0), "behav+": (v_behav, alpha), "behav-": (v_behav, -alpha),
             "dom+": (v_dom, alpha), "dom-": (v_dom, -alpha),
             "rand0+": (rands[0], alpha), "rand1+": (rands[1], alpha), "rand2+": (rands[2], alpha)}

    results = []
    for qi, q in enumerate(held_qs):
        row = {"q": q[:120], "cond": {}}
        for name, (vec, a) in conds.items():
            txt = gen(tok, hf, q, vec, a)
            row["cond"][name] = {"hedge": hedge_density(txt), "text": txt[:400]}
        results.append(row)
        b = row["cond"]["baseline"]["hedge"]
        print(f"[{qi+1}/{len(held_qs)}] base={b} behav+={row['cond']['behav+']['hedge']} "
              f"behav-={row['cond']['behav-']['hedge']} dom+={row['cond']['dom+']['hedge']} "
              f"rand+={[row['cond'][f'rand{k}+']['hedge'] for k in range(3)]}", flush=True)
        json.dump({"results": results, "alpha": alpha, "meannorm": meannorm}, open(OUT, "w"))

    # summary: mean hedge shift vs baseline per condition
    print("\n=== E3B: mean hedge-density shift vs baseline (negative = less hedging) ===")
    names = [n for n in conds if n != "baseline"]
    for n in names:
        sh = [r["cond"][n]["hedge"] - r["cond"]["baseline"]["hedge"] for r in results]
        print(f"  {n:>8}: mean Δhedge = {np.mean(sh):+.2f}  (per-item std {np.std(sh):.2f})")
    rand_sh = [np.mean([r["cond"][f"rand{k}+"]["hedge"] - r["cond"]["baseline"]["hedge"]
                        for k in range(3)]) for r in results]
    print(f"  random floor (mean of 3 seeds): {np.mean(rand_sh):+.2f}")
    print("Decisive: |behav Δ| must exceed |random Δ| (and ideally |dom Δ|) to beat the curse.")
    print(f"[done] -> {OUT}")


if __name__ == "__main__":
    main()
