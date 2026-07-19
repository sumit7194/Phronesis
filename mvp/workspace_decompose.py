#!/usr/bin/env python
"""Full sparse workspace decomposition of the 'a'-number BASELINE (failing) trace.

For every token position in the reasoning span, at each workspace-band layer, decompose the
residual state into a sparse NON-NEGATIVE combination of <=K J-lens concept vectors (the
paper's workspace decomposition; here via batched non-negative matching pursuit). Logs the
active concepts + weights per (position, layer) so we can watch what the model holds in mind
while it enumerates and fails.

Key identity: <h, v_t> (correlation of state h with atom for token t) = W_U[t] . (J_l @ h)
= the J-lens logit. So one lens readout scores ALL atoms at once -> MP is cheap and batched.

Outputs:
  results/workspace/decompose_none.json   (full: per position, per layer, top concepts+weights)
  results/workspace/decompose_none.txt    (human-readable primary-layer rolling log)
"""
import json, os, sys, time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from jlens.lens import JacobianLens
from workspace_common import BAND, LENS_PATH

DEVICE = "mps"
K = 25                       # paper's sparsity cap
LAYERS = [14, 20, 26]        # early / mid / late workspace band
PRIMARY = 20                 # layer for the readable rolling log
SKIP_FIRST = 16
VOCAB_CHUNK = 20000
NEG_CONCEPTS = ["none", "no", "not", "impossible", "empty", "zero", "never", "cannot"]


def atom_norms(W_U, J_l):
    """||v_t|| for every vocab token t, v_t = W_U[t] @ J_l. Chunked to bound memory."""
    M = (J_l @ J_l.T).float()                       # [d,d]
    out = torch.empty(W_U.shape[0], device=W_U.device)
    for s in range(0, W_U.shape[0], VOCAB_CHUNK):
        w = W_U[s:s + VOCAB_CHUNK].float()          # [c,d]
        out[s:s + w.shape[0]] = ((w @ M) * w).sum(1).clamp_min(1e-8).sqrt()
    return out                                      # [vocab]


def decompose_layer(H, W_U, J_l, norms, tok, k=K):
    """Batched non-negative MP. H: [N,d] residuals. Returns list per position of
    [(token_id, weight), ...] up to k, in selection order (most dominant first)."""
    N, d = H.shape
    R = H.float().clone()                            # working residual per position
    picks = [[] for _ in range(N)]
    Jt = J_l.T.float()
    for step in range(k):
        # scores_t = <R, v_t> = (R @ J_l^T) @ W_U^T  -> [N, vocab]; normalized by ||v_t||
        proj = R @ Jt                                # [N,d]
        scores = proj @ W_U.float().T                # [N, vocab]  (raw correlations)
        norm_scores = scores / norms[None, :]
        best = norm_scores.argmax(dim=1)             # [N] chosen token per position
        best_raw = scores.gather(1, best[:, None]).squeeze(1)      # <r, v*>
        coef = (best_raw / (norms[best] ** 2)).clamp_min(0.0)      # non-negative scalar coef
        # subtract coef * v_best from each position's residual: v_best = W_U[best] @ J_l
        v_best = W_U[best].float() @ J_l.float()     # [N,d]
        R = R - coef[:, None] * v_best
        for i in range(N):
            if coef[i] > 0:
                picks[i].append((int(best[i]), float(coef[i])))
        if step % 5 == 0:
            print(f"    layer step {step + 1}/{k}", flush=True)
    return picks


def main():
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-4B")
    hf = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-4B", dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    lens = JacobianLens.load(LENS_PATH)
    layers = [l for l in LAYERS if l in lens.source_layers]
    W_U = model._lm_head.weight.detach().to(DEVICE)                 # [vocab, d]
    print(f"[load] lens n={lens.n_prompts}, layers={layers}, vocab={W_U.shape[0]}", flush=True)

    d = json.load(open("results/workspace/inject_none_test.json"))
    base = [r for r in d["runs"] if r["label"] == "baseline"][0]["trace"]
    from inject_none_test import build_prompt
    full = build_prompt(tok) + base
    ids = tok(full, return_tensors="pt")["input_ids"][:, :2048].to(DEVICE)
    prompt_len = tok(build_prompt(tok), return_tensors="pt")["input_ids"].shape[1]
    toks = [tok.decode([t]) for t in ids[0].tolist()]
    n = ids.shape[1]
    print(f"[trace] {n} tokens ({prompt_len} prompt + {n - prompt_len} reasoning)", flush=True)

    with ActivationRecorder(model.layers, at=layers) as rec, torch.no_grad():
        hf.model(input_ids=ids, use_cache=False)
        acts = {l: rec.activations[l][0].detach() for l in layers}   # [n,d]

    span = list(range(max(prompt_len, SKIP_FIRST), n))               # reasoning span
    result = {"question_gold": "none", "lens_n": lens.n_prompts, "layers": layers,
              "primary": PRIMARY, "n_tokens": n, "prompt_len": prompt_len,
              "tokens": toks, "positions": {}}
    per_layer = {}
    for l in layers:
        print(f"[layer {l}] decomposing {len(span)} positions...", flush=True)
        norms = atom_norms(W_U, lens.jacobians[l].to(DEVICE))
        H = acts[l][span]
        picks = decompose_layer(H, W_U, lens.jacobians[l].to(DEVICE), norms, tok)
        per_layer[l] = picks
        del norms
        torch.mps.empty_cache()

    # assemble per-position record + negative-concept tracking
    neg_ids = set()
    for w in NEG_CONCEPTS:
        for form in (" " + w, w):
            t = tok(form, add_special_tokens=False)["input_ids"]
            if len(t) == 1:
                neg_ids.add(t[0])
    neg_hits = []
    for idx, pos in enumerate(span):
        rec_pos = {}
        for l in layers:
            concepts = [(tok.decode([tid]).strip(), round(w, 3)) for tid, w in per_layer[l][idx]]
            rec_pos[l] = concepts
            for rank, (tid, w) in enumerate(per_layer[l][idx]):
                if tid in neg_ids:
                    neg_hits.append({"pos": pos, "layer": l, "rank": rank,
                                     "concept": tok.decode([tid]).strip(), "weight": round(w, 3)})
        result["positions"][pos] = {"token": toks[pos], "by_layer": rec_pos}
    result["neg_concept_hits"] = neg_hits
    result["neg_concepts_tracked"] = sorted({tok.decode([t]).strip() for t in neg_ids})

    json.dump(result, open("results/workspace/decompose_none.json", "w"), indent=1)

    # readable rolling log at the primary layer
    with open("results/workspace/decompose_none.txt", "w") as f:
        f.write(f"WORKSPACE DECOMPOSITION — 'a'-number baseline (failing) trace\n")
        f.write(f"lens n={lens.n_prompts}, primary layer L{PRIMARY}, k<={K}, gold=none\n")
        f.write(f"negative-existence concepts EVER in workspace: {len(neg_hits)} hits "
                f"(tracked: {result['neg_concepts_tracked']})\n")
        f.write("=" * 90 + "\n")
        for pos in span:
            if PRIMARY not in per_layer:
                break
            concepts = result["positions"][pos]["by_layer"].get(PRIMARY, [])
            top = ", ".join(f"{c}({w})" for c, w in concepts[:12])
            f.write(f"[{pos:4}] tok={result['positions'][pos]['token']!r:14} | {top}\n")

    print(f"[done] {round((time.time()-t0)/60,1)} min. neg-concept hits: {len(neg_hits)}", flush=True)
    print(f"  -> results/workspace/decompose_none.json + .txt", flush=True)


if __name__ == "__main__":
    main()
