#!/usr/bin/env python
"""E3 gate — is v_behav SIGNAL or NOISE? Recompute per-question behavioral gradients and check
whether they point a consistent direction (real causal axis) or scatter (mean is meaningless).
  - mean pairwise cosine among per-q grads  (>~0.2 = consistent; ~0 = noise)
  - ||mean|| / mean||grad||                  (~1 = aligned; ~1/sqrt(n) = cancelling noise)
Run:  mvp/.venv/bin/python mvp/e3_consistency.py
"""
import json, os, sys
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYERS = [14, 20]
COMMIT = [" sure", " certain", " confident", " positive", " convinced", " definitely"]
HEDGE = [" not", " unsure", " uncertain", " doubtful", " afraid", " unclear"]


def sids(tok, ws):
    return [tok(w, add_special_tokens=False)["input_ids"][0] for w in ws
            if len(tok(w, add_special_tokens=False)["input_ids"]) == 1]


def main():
    qs = [d["prompt"] for d in json.load(open(os.path.join(ROOT, "corpus/eval-prompts/truthfulqa-probe.json")))]
    print(f"[load] Qwen3-4B ... ({len(qs)} contexts)", flush=True)
    tok, hf, _ = load_model()
    cids, hids = sids(tok, COMMIT), sids(tok, HEDGE)
    per = {L: [] for L in LAYERS}
    for q in qs:
        prefix = tok.apply_chat_template([{"role": "user", "content": q}], tokenize=False,
                                         add_generation_prompt=True, enable_thinking=False) + "I am"
        ids = torch.tensor([tok(prefix, add_special_tokens=False)["input_ids"]], device=DEVICE)
        embeds = hf.model.embed_tokens(ids).detach().requires_grad_(True)
        cap = {}
        hs = [hf.model.layers[L].register_forward_hook(
            (lambda L: (lambda m, i, o: cap.__setitem__(L, (o[0] if isinstance(o, tuple) else o))))(L))
            for L in LAYERS]
        out = hf(inputs_embeds=embeds)
        for h in hs:
            h.remove()
        last = out.logits[0, -1]
        B = torch.logsumexp(last[cids], 0) - torch.logsumexp(last[hids], 0)
        gs = torch.autograd.grad(B, [cap[L] for L in LAYERS])
        for L, g in zip(LAYERS, gs):
            per[L].append(g[0, -1].detach().float().cpu().numpy())
        del out, cap, gs, B, embeds
        if DEVICE == "mps":
            torch.mps.empty_cache()

    print("\n=== v_behav consistency (signal vs noise) ===")
    for L in LAYERS:
        G = np.array(per[L])
        U = G / (np.linalg.norm(G, axis=1, keepdims=True) + 1e-9)
        C = U @ U.T
        iu = np.triu_indices(len(G), 1)
        mean_pair = float(C[iu].mean())
        ratio = float(np.linalg.norm(G.mean(0)) / (np.linalg.norm(G, axis=1).mean() + 1e-9))
        noise_floor = 1.0 / np.sqrt(len(G))
        print(f"  L{L}: mean pairwise cos = {mean_pair:+.3f}  (noise≈0)   "
              f"||mean||/mean||g|| = {ratio:.3f}  (noise≈{noise_floor:.3f}, n={len(G)})")
        verdict = "SIGNAL (consistent direction)" if mean_pair > 0.15 else \
                  "NOISE (scatters; mean is meaningless)" if mean_pair < 0.05 else "WEAK/ambiguous"
        print(f"       -> {verdict}")


if __name__ == "__main__":
    main()
