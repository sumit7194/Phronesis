#!/usr/bin/env python
"""Ask the no-a question PLAIN — no 'reason step by step / box it' scaffold — and read the
workspace. Tests whether the leading instruction is what pushes the model into enumeration.
Saves results/workspace/6q/q1_plain_masked.json in the viewer format (skip_first=5 so the
full question shows in the stream)."""
import json, os, re, sys, time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from jlens.lens import JacobianLens
from jlens.vis import _meaningful_token_mask
from workspace_common import BAND, LENS_PATH

DEVICE = "mps"
LAYERS = ["14", "20", "26"]
TOPK, SKIP_FIRST, POS_CHUNK, MAX_NEW = 8, 5, 128, 2048
QUESTION = ("Is there a positive whole number less than 1000 whose English spelling contains "
            "the letter 'a'? Do not count the word 'and'. If such a number exists, give the "
            "smallest one. If no such number exists, say so.")


def main():
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-4B")
    hf = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-4B", dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    lens = JacobianLens.load(LENS_PATH)
    band = [l for l in BAND if l in lens.source_layers]
    mask = _meaningful_token_mask(tok, model._lm_head.weight.shape[0], DEVICE)

    # PLAIN prompt: bare question, no reasoning/box instruction. Thinking left on (Qwen3 default).
    msg = [{"role": "user", "content": QUESTION}]
    try:
        prompt = tok.apply_chat_template(msg, add_generation_prompt=True, tokenize=False, enable_thinking=True)
    except TypeError:
        prompt = tok.apply_chat_template(msg, add_generation_prompt=True, tokenize=False)
    print(f"[load] lens n={lens.n_prompts}. PLAIN prompt (no scaffold):\n---\n{prompt}\n---", flush=True)

    ids = tok(prompt, return_tensors="pt")["input_ids"].to(DEVICE)
    prompt_len = ids.shape[1]
    with torch.no_grad():
        o = hf.generate(input_ids=ids, attention_mask=torch.ones_like(ids),
                        max_new_tokens=MAX_NEW, do_sample=False, pad_token_id=tok.eos_token_id)
    trace = tok.decode(o[0][prompt_len:], skip_special_tokens=True)
    m = re.findall(r"\\boxed\{([^}]*)\}", trace)
    tail = trace[-160:].lower()
    if m:
        ans = m[-1].strip()
    elif any(w in tail for w in ("none", "no such", "no number", "does not exist", "doesn't exist")):
        ans = "none (stated)"
    elif "</think>" in trace and trace.split("</think>")[-1].strip():
        ans = trace.split("</think>")[-1].strip()[:60]
    else:
        ans = "(no clear answer / truncated)"
    hit_cap = (o.shape[1] - prompt_len) >= MAX_NEW - 2
    print(f"[gen] answer={ans!r}  hit_cap={hit_cap}  trace_chars={len(trace)}", flush=True)

    # masked, prompt-inclusive readout
    full_ids = tok(prompt + trace, return_tensors="pt")["input_ids"][:, :2048].to(DEVICE)
    n = full_ids.shape[1]
    toks = [tok.decode([t]) for t in full_ids[0].tolist()]
    with ActivationRecorder(model.layers, at=[int(l) for l in LAYERS]) as rec, torch.no_grad():
        hf.model(input_ids=full_ids, use_cache=False)
        acts = {int(l): rec.activations[int(l)][0].detach() for l in LAYERS}
    span = list(range(SKIP_FIRST, n))
    per_layer = {l: {} for l in LAYERS}
    neg_inf = torch.finfo(torch.float32).min
    for l in LAYERS:
        Jl = lens.jacobians[int(l)].to(DEVICE)
        for s in range(0, len(span), POS_CHUNK):
            pos = span[s:s + POS_CHUNK]
            h = acts[int(l)][pos].float()
            logits = model.unembed(h @ Jl.T).float().masked_fill(~mask, neg_inf)
            tp = torch.softmax(logits, -1).topk(TOPK, dim=-1)
            for i, p in enumerate(pos):
                per_layer[l][p] = [[tok.decode([int(t)]).strip(), round(float(w), 3)]
                                   for t, w in zip(tp.indices[i], tp.values[i])]
        torch.mps.empty_cache()

    out = {"id": "q1_plain", "category": "no-a asked PLAIN (no reason/box scaffold)",
           "gold": "none", "answer": str(ans), "correct": "none" in str(ans).lower(),
           "question": QUESTION, "lens_n": lens.n_prompts, "prompt_len": prompt_len,
           "n_tokens": n, "trace": trace, "tokens": toks, "positions": {}}
    for p in span:
        out["positions"][p] = {"token": toks[p], "by_layer": {l: per_layer[l].get(p, []) for l in LAYERS}}
    json.dump(out, open("results/workspace/6q/q1_plain_masked.json", "w"), indent=1)
    print(f"[done] {round((time.time()-t0)/60,1)} min -> q1_plain_masked.json", flush=True)


if __name__ == "__main__":
    main()
