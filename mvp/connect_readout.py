#!/usr/bin/env python
"""Masked J-space readout of the composed-query traces from Round 1 (connect_screen.json),
tracking the BRIDGE token. Produces viewer-format JSON so the connection chains show up in the
steer viewer. No generation — reuses saved traces. Also runs a NO-THINK composed pass per chain
(enable_thinking=False) to surface the latent compositionality gap + read its workspace."""
import json, os, sys, time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from jlens.lens import JacobianLens
from jlens.vis import _meaningful_token_mask
from workspace_common import BAND, LENS_PATH, single_token_id

DEVICE, LAYERS, TOPK, SKIP_FIRST, POS_CHUNK = "mps", ["14", "20", "26"], 8, 5, 128
OUTDIR = "results/workspace/connect"


@torch.no_grad()
def readout(model, hf, tok, lens, mask, prompt, trace, bridge_ids, gold_ids):
    full = tok(prompt + trace, return_tensors="pt")["input_ids"][:, :2048].to(DEVICE)
    n = full.shape[1]
    plen = tok(prompt, return_tensors="pt")["input_ids"].shape[1]
    toks = [tok.decode([t]) for t in full[0].tolist()]
    with ActivationRecorder(model.layers, at=[int(l) for l in LAYERS]) as rec:
        hf.model(input_ids=full, use_cache=False)
        acts = {int(l): rec.activations[int(l)][0].detach() for l in LAYERS}
    span = list(range(SKIP_FIRST, n))
    per_layer = {l: {} for l in LAYERS}
    ninf = torch.finfo(torch.float32).min
    br = {"bridge": 10**9, "gold": 10**9}
    for l in LAYERS:
        Jl = lens.jacobians[int(l)].to(DEVICE)
        for s in range(0, len(span), POS_CHUNK):
            pos = span[s:s + POS_CHUNK]
            h = acts[int(l)][pos].float()
            lf = model.unembed(h @ Jl.T).float()
            tp = torch.softmax(lf.masked_fill(~mask, ninf), -1).topk(TOPK, -1)
            for i, p in enumerate(pos):
                per_layer[l][p] = [[tok.decode([int(t)]).strip(), round(float(w), 3)]
                                   for t, w in zip(tp.indices[i], tp.values[i])]
            for nm, ids in (("bridge", bridge_ids), ("gold", gold_ids)):
                for tid in ids:
                    if tid is None:
                        continue
                    r = int(((lf > lf[:, tid:tid+1]).sum(1) + 1).min().item())
                    if r < br[nm]:
                        br[nm] = r
        torch.mps.empty_cache()
    return toks, span, per_layer, plen, n, br


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-4B")
    hf = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-4B", dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    lens = JacobianLens.load(LENS_PATH)
    mask = _meaningful_token_mask(tok, model._lm_head.weight.shape[0], DEVICE)
    chains = {c["id"]: c for c in json.load(open("connect_chains.json"))["chains"]}
    screen = {r["id"]: r for r in json.load(open("results/workspace/connect_screen.json"))["rows"]}

    def prompt_of(q):
        m = [{"role": "user", "content": q + "\nAnswer concisely."}]
        return tok.apply_chat_template(m, add_generation_prompt=True, tokenize=False, enable_thinking=True)

    def nothink_prompt(q):
        m = [{"role": "user", "content": q + "\nAnswer concisely."}]
        try:
            return tok.apply_chat_template(m, add_generation_prompt=True, tokenize=False, enable_thinking=False)
        except TypeError:
            return tok.apply_chat_template(m, add_generation_prompt=True, tokenize=False)

    t0 = time.time()
    for cid, ch in chains.items():
        outp = f"{OUTDIR}/{cid}__think.json"
        bridge_ids = [single_token_id(tok, ch["bridge"].split()[0])]
        gold_ids = [single_token_id(tok, g.split()[0]) for g in ch["ans"]]
        # (1) THINK composed trace (reuse saved) + readout
        if not os.path.exists(outp) and cid in screen:
            prompt = prompt_of(ch["composed_q"])
            trace = screen[cid]["composed_trace"]
            toks, span, per, plen, n, br = readout(model, hf, tok, lens, mask, prompt, trace, bridge_ids, gold_ids)
            json.dump({"id": f"{cid}__think", "category": f"{cid} · composed (think)",
                       "gold": ",".join(ch["ans"]), "answer": screen[cid]["composed_ans"],
                       "correct": screen[cid]["composed_ok"], "question": ch["composed_q"],
                       "lens_n": lens.n_prompts, "prompt_len": plen, "n_tokens": n, "trace": trace,
                       "tokens": toks, "_sum": {"regime": "think", "composed_ok": screen[cid]["composed_ok"],
                       "bridge_rank": br["bridge"], "gold_rank": br["gold"], "bridge": ch["bridge"]},
                       "positions": {p: {"token": toks[p], "by_layer": {l: per[l].get(p, []) for l in LAYERS}} for p in span}},
                      open(outp, "w"))
            print(f"  {cid:20} think   composed_ok={screen[cid]['composed_ok']} bridge_rank={br['bridge']} gold_rank={br['gold']}", flush=True)
        # (2) NO-THINK composed (fresh gen) + readout — the latent regime where the gap lives
        outp2 = f"{OUTDIR}/{cid}__nothink.json"
        if not os.path.exists(outp2):
            p2 = nothink_prompt(ch["composed_q"])
            ids = tok(p2, return_tensors="pt")["input_ids"].to(DEVICE)
            o = hf.generate(input_ids=ids, attention_mask=torch.ones_like(ids), max_new_tokens=64,
                            do_sample=False, pad_token_id=tok.eos_token_id)
            tr = tok.decode(o[0][ids.shape[1]:], skip_special_tokens=True)
            ok = any(g.lower() in tr.lower() for g in ch["ans"])
            toks, span, per, plen, n, br = readout(model, hf, tok, lens, mask, p2, tr, bridge_ids, gold_ids)
            json.dump({"id": f"{cid}__nothink", "category": f"{cid} · composed (NO-think/latent)",
                       "gold": ",".join(ch["ans"]), "answer": tr.strip()[:60], "correct": ok,
                       "question": ch["composed_q"], "lens_n": lens.n_prompts, "prompt_len": plen,
                       "n_tokens": n, "trace": tr, "tokens": toks,
                       "_sum": {"regime": "nothink", "composed_ok": ok, "bridge_rank": br["bridge"],
                                "gold_rank": br["gold"], "bridge": ch["bridge"]},
                       "positions": {p: {"token": toks[p], "by_layer": {l: per[l].get(p, []) for l in LAYERS}} for p in span}},
                      open(outp2, "w"))
            print(f"  {cid:20} NOTHINK composed_ok={ok} bridge_rank={br['bridge']} gold_rank={br['gold']} ans={tr.strip()[:30]!r}", flush=True)
        torch.mps.empty_cache()
    print(f"[done] {round((time.time()-t0)/60,1)} min -> {OUTDIR}/", flush=True)


if __name__ == "__main__":
    main()
