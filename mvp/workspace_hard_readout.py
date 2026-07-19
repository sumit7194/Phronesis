#!/usr/bin/env python
"""Single-pass workspace readout for the 6 curated questions (workspace_hard_stimuli.json).

For each question: ONE greedy pass (baseline model, no steering; full trace saved), then the
CORRECTLY-NORMALIZED J-lens readout at each token position — top-25 concepts per workspace-band
layer. Normalized = model.unembed applies the final layernorm before decoding (jlens/hf.py:170),
which is what the public repo's readout does; my earlier raw-residual pursuit skipped it and got
massive-activation garbage. This is the repo-vetted method.

Records 3 representative workspace layers (early/mid/late) to keep the data combable; expand
LAYERS to the full band if wanted. n=45 lens (best available).

Outputs per question:
  results/workspace/hard/<id>.json   full: per position x 3 layers x top-25 (token, prob)
  results/workspace/hard/<id>.txt    readable rolling log at the primary layer
  results/workspace/hard/summary.json  answers + correctness per question
"""
import json, os, sys, time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from jlens.lens import JacobianLens
from workspace_common import BAND, LENS_PATH
from reasoning_baseline import score

DEVICE = "mps"
OUTDIR = "results/workspace/hard"
LAYERS = [14, 20, 26]      # early / mid / late workspace
PRIMARY = 20
TOPK = 25
MAX_NEW = 2048
SKIP_FIRST = 16
POS_CHUNK = 128
CLOSE = "</think>"


def build_prompt(tok, q):
    m = [{"role": "user", "content": q + "\nReason step by step, then give the final answer in \\boxed{}."}]
    try:
        return tok.apply_chat_template(m, add_generation_prompt=True, tokenize=False, enable_thinking=True)
    except TypeError:
        return tok.apply_chat_template(m, add_generation_prompt=True, tokenize=False)


@torch.no_grad()
def greedy(hf, tok, prompt):
    ids = tok(prompt, return_tensors="pt")["input_ids"].to(DEVICE)
    o = hf.generate(input_ids=ids, attention_mask=torch.ones_like(ids),
                    max_new_tokens=MAX_NEW, do_sample=False, pad_token_id=tok.eos_token_id)
    return tok.decode(o[0][ids.shape[1]:], skip_special_tokens=True)


@torch.no_grad()
def readout(model, hf, tok, lens, band, full_text, start_pos):
    """Normalized J-lens top-25 per (band layer, position>=start_pos)."""
    ids = tok(full_text, return_tensors="pt")["input_ids"][:, :2048].to(DEVICE)
    n = ids.shape[1]
    with ActivationRecorder(model.layers, at=band) as rec:
        hf.model(input_ids=ids, use_cache=False)
        acts = {l: rec.activations[l][0].detach() for l in band}
    toks = [tok.decode([t]) for t in ids[0].tolist()]
    per_layer = {l: {} for l in band}
    span = list(range(max(start_pos, SKIP_FIRST), n))
    for l in band:
        Jl = lens.jacobians[l].to(DEVICE)
        for s in range(0, len(span), POS_CHUNK):
            pos = span[s:s + POS_CHUNK]
            h = acts[l][pos].float()                       # [c,d]
            transported = h @ Jl.T                          # [c,d]
            logits = model.unembed(transported).float()     # normalized (final_norm inside)
            probs = torch.softmax(logits, dim=-1)
            tp = probs.topk(TOPK, dim=-1)
            for i, p in enumerate(pos):
                per_layer[l][p] = [(tok.decode([int(t)]).strip(), round(float(w), 4))
                                   for t, w in zip(tp.indices[i], tp.values[i])]
            del logits, probs, transported
        torch.mps.empty_cache()
    return toks, span, per_layer, n


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-4B")
    hf = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-4B", dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    lens = JacobianLens.load(LENS_PATH)
    band = [l for l in LAYERS if l in lens.source_layers]
    print(f"[load] lens n={lens.n_prompts}, band={band}", flush=True)

    questions = json.load(open("workspace_hard_stimuli.json"))["questions"]
    summary = {"lens_n": lens.n_prompts, "band": band, "topk": TOPK, "primary": PRIMARY, "items": []}
    for qi, q in enumerate(questions):
        print(f"[hard] {q['id']} — generating...", flush=True)
        prompt = build_prompt(tok, q["question"])
        trace = greedy(hf, tok, prompt)
        import re
        m = re.findall(r"\\boxed\{([^}]*)\}", trace)
        ans = m[-1].strip() if m else "(no box)"
        ok = bool(score(ans, str(q["gold"]), "gsm8k")) if ans != "(no box)" else False
        prompt_len = tok(prompt, return_tensors="pt")["input_ids"].shape[1]
        print(f"       answer={ans!r} ok={ok}; reading workspace...", flush=True)
        toks, span, per_layer, n = readout(model, hf, tok, lens, band, prompt + trace, prompt_len)

        rec = {"id": q["id"], "category": q["category"], "gold": q["gold"], "answer": ans,
               "correct": ok, "n_tokens": n, "prompt_len": prompt_len, "tokens": toks,
               "trace": trace, "positions": {}}
        for p in span:
            rec["positions"][p] = {"token": toks[p],
                                   "by_layer": {l: per_layer[l].get(p, []) for l in band}}
        json.dump(rec, open(f"{OUTDIR}/{q['id']}.json", "w"), indent=1)
        with open(f"{OUTDIR}/{q['id']}.txt", "w") as f:
            f.write(f"{q['id']} | {q['category']} | gold={q['gold']} answer={ans} correct={ok}\n")
            f.write(f"lens n={lens.n_prompts}, primary L{PRIMARY}, top-{TOPK} normalized readout\n")
            f.write("=" * 100 + "\n")
            for p in span:
                if PRIMARY in per_layer:
                    top = ", ".join(f"{c}({w})" for c, w in per_layer[PRIMARY].get(p, [])[:15])
                    f.write(f"[{p:4}] {toks[p]!r:14} | {top}\n")
        summary["items"].append({"id": q["id"], "category": q["category"], "gold": q["gold"],
                                 "answer": ans, "correct": ok, "n_tokens": n})
        print(f"       saved {q['id']} ({len(span)} positions)", flush=True)

    json.dump(summary, open(f"{OUTDIR}/summary.json", "w"), indent=1)
    print(f"[done] {round((time.time()-t0)/60,1)} min -> {OUTDIR}/", flush=True)
    for it in summary["items"]:
        print(f"  {it['id']:18} correct={it['correct']} ans={it['answer']!r}", flush=True)


if __name__ == "__main__":
    main()
