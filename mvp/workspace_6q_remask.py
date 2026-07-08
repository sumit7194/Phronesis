#!/usr/bin/env python
"""Re-extract workspace concepts for the 6 questions using the REPO's masked readout.

No regeneration — reads the saved full traces from results/workspace/6q/<id>.json and redoes
only the readout, now applying jlens.vis._meaningful_token_mask (keep word-like tokens, drop
punctuation/special tokens) before top-25. This is the repo's own fix for punctuation-dominated
readouts. Fast: one forward pass per question.

  --only q2_math_solved   test on a single question first
"""
import argparse, json, os, sys, time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from jlens.lens import JacobianLens
from jlens.vis import _meaningful_token_mask
from workspace_common import LENS_PATH

DEVICE = "mps"
OUTDIR = "results/workspace/6q"
LAYERS = [14, 20, 26]
PRIMARY = 20
TOPK = 25
SKIP_FIRST = 16
POS_CHUNK = 128


def build_prompt(tok, q):
    m = [{"role": "user", "content": q + "\nReason step by step, then give the final answer in \\boxed{}."}]
    try:
        return tok.apply_chat_template(m, add_generation_prompt=True, tokenize=False, enable_thinking=True)
    except TypeError:
        return tok.apply_chat_template(m, add_generation_prompt=True, tokenize=False)


@torch.no_grad()
def masked_readout(model, hf, tok, lens, band, full_text, start_pos, mask):
    ids = tok(full_text, return_tensors="pt")["input_ids"][:, :2048].to(DEVICE)
    n = ids.shape[1]
    with ActivationRecorder(model.layers, at=band) as rec:
        hf.model(input_ids=ids, use_cache=False)
        acts = {l: rec.activations[l][0].detach() for l in band}
    toks = [tok.decode([t]) for t in ids[0].tolist()]
    # include the PROMPT span too (from the attention-sink cutoff), not just reasoning —
    # so we can read the workspace while the model READS the question. start_pos (prompt_len)
    # is still recorded separately so the viewer can mark the prompt|thinking boundary.
    span = list(range(SKIP_FIRST, n))
    per_layer = {l: {} for l in band}
    neg_inf = torch.finfo(torch.float32).min
    for l in band:
        Jl = lens.jacobians[l].to(DEVICE)
        for s in range(0, len(span), POS_CHUNK):
            pos = span[s:s + POS_CHUNK]
            h = acts[l][pos].float()
            logits = model.unembed(h @ Jl.T).float()
            logits = logits.masked_fill(~mask, neg_inf)          # <-- repo's fix
            probs = torch.softmax(logits, dim=-1)
            tp = probs.topk(TOPK, dim=-1)
            for i, p in enumerate(pos):
                per_layer[l][p] = [(tok.decode([int(t)]).strip(), round(float(w), 4))
                                   for t, w in zip(tp.indices[i], tp.values[i])]
            del logits, probs
        torch.mps.empty_cache()
    return toks, span, per_layer, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    args = ap.parse_args()
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-4B")
    hf = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-4B", dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    lens = JacobianLens.load(LENS_PATH)
    band = [l for l in LAYERS if l in lens.source_layers]
    mask = _meaningful_token_mask(tok, model._lm_head.weight.shape[0], DEVICE)
    print(f"[load] lens n={lens.n_prompts}, band={band}, wordlike tokens={int(mask.sum())}", flush=True)

    stim = {q["id"]: q for q in json.load(open("workspace_6q_stimuli.json"))["questions"]}
    ids = [args.only] if args.only else list(stim)
    for qid in ids:
        rec0 = json.load(open(f"{OUTDIR}/{qid}.json"))
        q = stim[qid]
        prompt = build_prompt(tok, q["question"])
        full = prompt + rec0["trace"]
        prompt_len = rec0["prompt_len"]
        print(f"[{qid}] masked readout...", flush=True)
        toks, span, per_layer, n = masked_readout(model, hf, tok, lens, band, full, prompt_len, mask)
        out = {"id": qid, "category": q["category"], "gold": q["gold"], "answer": rec0["answer"],
               "correct": rec0["correct"], "masked": True, "n_tokens": n, "prompt_len": prompt_len,
               "tokens": toks, "trace": rec0["trace"], "positions": {}}
        for p in span:
            out["positions"][p] = {"token": toks[p], "by_layer": {l: per_layer[l].get(p, []) for l in band}}
        json.dump(out, open(f"{OUTDIR}/{qid}_masked.json", "w"), indent=1)
        with open(f"{OUTDIR}/{qid}_masked.txt", "w") as f:
            f.write(f"{qid} | {q['category']} | gold={q['gold']} answer={out['answer']} correct={out['correct']}\n")
            f.write(f"MASKED (word-like only) top-{TOPK} normalized readout, primary L{PRIMARY}, lens n={lens.n_prompts}\n")
            f.write("=" * 100 + "\n")
            for p in span:
                top = ", ".join(f"{c}({w})" for c, w in per_layer[PRIMARY].get(p, [])[:15])
                f.write(f"[{p:4}] {toks[p]!r:14} | {top}\n")
        # quick console sample around content tokens
        sample = [p for p in span if any(w in toks[p].lower() for w in ("prime", "factor", "196", "13", "tree", "none"))][:3]
        for p in sample:
            print(f"    [{p}] tok={toks[p]!r} -> " + ", ".join(c for c, _ in per_layer[PRIMARY].get(p, [])[:8]), flush=True)
        print(f"    saved {qid}_masked ({len(span)} pos)", flush=True)
    print(f"[done] {round((time.time()-t0)/60,1)} min", flush=True)


if __name__ == "__main__":
    main()
