#!/usr/bin/env python
"""E3 Part A — behavioral Jacobian vs diff-of-means vs logistic probe (prereg-lens-info + the
behavioral-jacobian seed). All three directions built from the SAME stance contexts, same layer,
same position — a fair comparison. Answers falsifier-2: is v_behav a NEW object or just diff-of-means?

Stance slot: chat(question) + "I am" -> next token is a confidence adverb.
  B(context) = logsumexp(commit-token logits) - logsumexp(hedge-token logits) at that slot.
  v_behav_L = mean_q d B / d h_L            (autograd; the causal write direction, to 1st order)
  v_dom_L   = mean(commit-act) - mean(hedge-act)   at the stance token   (diff-of-means)
  v_probe_L = logistic(commit-act vs hedge-act)     at the stance token   (correlational probe)

Part B (steering + random controls) is a separate run, gated on this.
Run:  mvp/.venv/bin/python mvp/e3_behavioral_jacobian.py
"""
import json, os, sys
import numpy as np
import torch
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "mvp/results/workspace/e3_behavioral_jacobian.json")
LAYERS = [10, 14, 17, 20]
COMMIT = [" sure", " certain", " confident", " positive", " convinced", " definitely"]
HEDGE = [" not", " unsure", " uncertain", " doubtful", " afraid", " unclear"]


def single_ids(tok, words):
    out = []
    for w in words:
        ids = tok(w, add_special_tokens=False)["input_ids"]
        if len(ids) == 1:
            out.append(ids[0])
    return out


def main():
    qs = [d["prompt"] for d in json.load(open(os.path.join(ROOT, "corpus/eval-prompts/truthfulqa-probe.json")))][:30]
    print(f"[load] Qwen3-4B ... ({len(qs)} stance contexts)", flush=True)
    tok, hf, _ = load_model()
    cids, hids = single_ids(tok, COMMIT), single_ids(tok, HEDGE)
    print(f"  commit toks={len(cids)} hedge toks={len(hids)}")
    layers = {L: hf.model.layers[L] for L in LAYERS}

    grads = {L: [] for L in LAYERS}       # v_behav samples
    commit_acts = {L: [] for L in LAYERS}
    hedge_acts = {L: [] for L in LAYERS}

    for qi, q in enumerate(qs):
        prefix = tok.apply_chat_template([{"role": "user", "content": q}], tokenize=False,
                                         add_generation_prompt=True, enable_thinking=False) + "I am"
        ids = torch.tensor([tok(prefix, add_special_tokens=False)["input_ids"]], device=DEVICE)

        # --- v_behav: grad of B wrt h_L at the stance slot (last position) ---
        # feed inputs_embeds w/ requires_grad so the graph carries gradients (ids alone don't).
        embeds = hf.model.embed_tokens(ids).detach().requires_grad_(True)
        captured = {}
        hooks = []
        for L, mod in layers.items():
            def mk(L):
                def hook(m, i, o):
                    h = o[0] if isinstance(o, tuple) else o
                    h.retain_grad()
                    captured[L] = h
                return hook
            hooks.append(mod.register_forward_hook(mk(L)))
        out = hf(inputs_embeds=embeds)
        for h in hooks:
            h.remove()
        last = out.logits[0, -1]
        B = torch.logsumexp(last[cids], 0) - torch.logsumexp(last[hids], 0)
        gs = torch.autograd.grad(B, [captured[L] for L in LAYERS])
        for L, g in zip(LAYERS, gs):
            grads[L].append(g[0, -1].detach().float().cpu().numpy())
        del out, captured, gs, B, embeds
        if DEVICE == "mps":
            torch.mps.empty_cache()

        # --- v_dom / v_probe: activations at the stance token for commit vs hedge completions ---
        with torch.no_grad():
            for word, bucket in ((" sure", commit_acts), (" not", hedge_acts)):
                wid = tok(word, add_special_tokens=False)["input_ids"]
                cids2 = torch.tensor([ids[0].tolist() + wid], device=DEVICE)
                o = hf(cids2, output_hidden_states=True)
                for L in LAYERS:
                    bucket[L].append(o.hidden_states[L + 1][0, -1].float().cpu().numpy())
            del o
            if DEVICE == "mps":
                torch.mps.empty_cache()
        if (qi + 1) % 10 == 0:
            print(f"  {qi+1}/{len(qs)}", flush=True)

    def unit(v):
        v = np.asarray(v, float)
        return v / (np.linalg.norm(v) + 1e-9)

    def cos(a, b):
        return float(np.dot(unit(a), unit(b)))

    vhedge = np.load(os.path.join(ROOT, "mvp/results/legibility/v_hedge_cc_4b.npy"), allow_pickle=True).item()
    results = {}
    print("\n=== E3 Part A: cosine matrix per layer ===")
    for L in LAYERS:
        v_behav = np.mean(grads[L], 0)                       # increases commit
        v_dom = np.mean(commit_acts[L], 0) - np.mean(hedge_acts[L], 0)
        X = np.array(commit_acts[L] + hedge_acts[L])
        y = np.array([1] * len(commit_acts[L]) + [0] * len(hedge_acts[L]))
        clf = LogisticRegression(max_iter=2000, C=1.0).fit(X - X.mean(0), y)
        v_probe = clf.coef_[0]
        v_dom_saved = np.asarray(vhedge[f"commit_{L}"], float)   # recall-commit diff-of-means (prior)
        m = {
            "behav_vs_dom": cos(v_behav, v_dom),
            "behav_vs_probe": cos(v_behav, v_probe),
            "behav_vs_domSaved": cos(v_behav, v_dom_saved),
            "dom_vs_probe": cos(v_dom, v_probe),
            "dom_vs_domSaved": cos(v_dom, v_dom_saved),
            "behav_norm": float(np.linalg.norm(v_behav)),
        }
        results[L] = m
        print(f"  L{L:>2}: behav·dom={m['behav_vs_dom']:+.2f}  behav·probe={m['behav_vs_probe']:+.2f}  "
              f"behav·domSaved={m['behav_vs_domSaved']:+.2f}  dom·probe={m['dom_vs_probe']:+.2f}  "
              f"dom·domSaved={m['dom_vs_domSaved']:+.2f}")
        np.save(os.path.join(ROOT, f"mvp/results/workspace/v_behav_L{L}.npy"), v_behav)

    json.dump(results, open(OUT, "w"), indent=2)
    print(f"\n[done] -> {OUT}")
    print("Falsifier-2: |behav·dom| > 0.8 at the working layer => not a new object.")


if __name__ == "__main__":
    main()
