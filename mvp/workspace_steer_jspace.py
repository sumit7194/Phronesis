#!/usr/bin/env python
"""Observe how STEERING changes the J-space (workspace) on our probe prompts.

For each prompt x steering condition: CAA-steer (h += alpha * v_unit) at L14 for all positions,
generate greedy (cap 2048), then read the masked J-space of the steered trace (hook active, so
residuals reflect the steering). Records behavior (commit/correct), the doubt-load (our F-B
metric), and the full per-position concepts (viewer format).

Conditions: 4 virtues (IH, evidence-grounding, reasoning-transparency, verbosity-control) at
+-alpha, plus matched-norm RANDOM x2 seeds (mandatory control, guidelines s2). Baseline exists.
Resumable: skips any condition whose output JSON already exists. Disk-guarded, status heartbeat.
"""
import json, os, re, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from jlens.lens import JacobianLens
from jlens.vis import _meaningful_token_mask
from workspace_common import BAND, LENS_PATH
from reasoning_baseline import score

DEVICE, LAYER, ALPHA, MAX_NEW = "mps", 14, 12.0, 2048
LAYERS = ["14", "20", "26"]
TOPK, SKIP_FIRST, POS_CHUNK = 8, 5, 128
OUTDIR, STATUS = "results/workspace/steer", "results/workspace/steer/status.json"
VDIR = "results/vectors/qwen3-4b"
VIRTUES = {"IH": "triplets-intellectual-humility", "EG": "triplets-evidence-grounding",
           "RT": "triplets-reasoning-transparency", "VC": "triplets-verbosity-control"}
PROMPTS = ["q1_no_a", "q3_gsm_rescuable", "q6_gsm_failed", "q5_gsm_solved"]
DOUBT = {"wait", "hmm", "maybe", "actually", "however", "but", "confused", "confusion",
         "mistake", "wrong", "doubt", "unsure", "uncertain", "perhaps", "again", "guess",
         "suppose", "seems", "no", "not", "oops", "error"}


def build_prompt(tok, q):
    m = [{"role": "user", "content": q + "\nReason step by step, then give the final answer in \\boxed{}."}]
    try:
        return tok.apply_chat_template(m, add_generation_prompt=True, tokenize=False, enable_thinking=True)
    except TypeError:
        return tok.apply_chat_template(m, add_generation_prompt=True, tokenize=False)


class Steer:
    """CAA additive steer at LAYER: h += alpha * v_unit (all positions, every forward)."""
    def __init__(self, model, v_unit, alpha):
        self.h = None
        vec = (alpha * v_unit).to(DEVICE)

        def hook(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            t = t + vec.to(t.dtype)
            return (t,) + out[1:] if isinstance(out, tuple) else t
        self.handle = model.layers[LAYER].register_forward_hook(hook)

    def __enter__(self): return self
    def __exit__(self, *a): self.handle.remove()


def load_vunit(name):
    v = np.load(f"{VDIR}/{VIRTUES[name]}/last_token/layer_14_virtue_vector.npy").astype(np.float32)
    t = torch.tensor(v)
    return t / (t.norm() + 1e-10)


def masked_readout(model, hf, tok, lens, band, mask, full_text):
    ids = tok(full_text, return_tensors="pt")["input_ids"][:, :2048].to(DEVICE)
    n = ids.shape[1]
    with ActivationRecorder(model.layers, at=[int(l) for l in LAYERS]) as rec, torch.no_grad():
        hf.model(input_ids=ids, use_cache=False)   # Steer hook (if active) applies here too
        acts = {int(l): rec.activations[int(l)][0].detach() for l in LAYERS}
    toks = [tok.decode([t]) for t in ids[0].tolist()]
    span = list(range(SKIP_FIRST, n))
    per_layer = {l: {} for l in LAYERS}
    ninf = torch.finfo(torch.float32).min
    for l in LAYERS:
        Jl = lens.jacobians[int(l)].to(DEVICE)
        for s in range(0, len(span), POS_CHUNK):
            pos = span[s:s + POS_CHUNK]
            h = acts[int(l)][pos].float()
            logits = model.unembed(h @ Jl.T).float().masked_fill(~mask, ninf)
            tp = torch.softmax(logits, -1).topk(TOPK, -1)
            for i, p in enumerate(pos):
                per_layer[l][p] = [[tok.decode([int(t)]).strip(), round(float(w), 3)]
                                   for t, w in zip(tp.indices[i], tp.values[i])]
        torch.mps.empty_cache()
    return toks, span, per_layer, n


def doubt_load(per_layer, span):
    tot = 0.0
    for p in span:
        tot += sum(w for c, w in per_layer["20"].get(p, []) if c.lower() in DOUBT)
    return round(tot / max(len(span), 1), 4)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-4B")
    hf = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-4B", dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    lens = JacobianLens.load(LENS_PATH)
    band = [l for l in BAND if l in lens.source_layers]
    mask = _meaningful_token_mask(tok, model._lm_head.weight.shape[0], DEVICE)
    stim = {q["id"]: q for q in json.load(open("workspace_6q_stimuli.json"))["questions"]}

    vunits = {name: load_vunit(name) for name in VIRTUES}
    conds = []
    for name in VIRTUES:
        conds += [(f"{name}+{int(ALPHA)}", vunits[name], ALPHA),
                  (f"{name}-{int(ALPHA)}", vunits[name], -ALPHA)]
    for seed in (0, 1):
        g = torch.Generator().manual_seed(500 + seed)
        r = torch.randn(model.d_model, generator=g)
        conds.append((f"random{seed}+{int(ALPHA)}", r / r.norm(), ALPHA))
    print(f"[load] lens n={lens.n_prompts}, L{LAYER}, alpha={ALPHA}, {len(PROMPTS)}x{len(conds)} runs", flush=True)

    summary = []
    total, done = len(PROMPTS) * len(conds), 0
    t0 = time.time()
    for pid in PROMPTS:
        q = stim[pid]
        prompt = build_prompt(tok, q["question"])
        for cname, vunit, alpha in conds:
            outp = f"{OUTDIR}/{pid}__{cname}.json"
            if os.path.exists(outp):
                done += 1
                summary.append(json.load(open(outp)).get("_sum", {}))
                continue
            import shutil
            if shutil.disk_usage("/").free / 2**30 < 3.0:
                print("[STOP] disk low. resumable.", flush=True); return
            with Steer(model, vunit, alpha):
                ids = tok(prompt, return_tensors="pt")["input_ids"].to(DEVICE)
                with torch.no_grad():
                    o = hf.generate(input_ids=ids, attention_mask=torch.ones_like(ids),
                                    max_new_tokens=MAX_NEW, do_sample=False, pad_token_id=tok.eos_token_id)
                trace = tok.decode(o[0][ids.shape[1]:], skip_special_tokens=True)
                toks, span, per_layer, n = masked_readout(model, hf, tok, lens, band, mask, prompt + trace)
            box = re.findall(r"\\boxed\{([^}]*)\}", trace)
            committed = ("</think>" in trace) or bool(box)
            ans = box[-1].strip() if box else ("(committed,no box)" if committed else "(spiral/cap)")
            ok = bool(score(ans, str(q["gold"]), "gsm8k")) if box else False
            dl = doubt_load(per_layer, span)
            sm = {"prompt": pid, "cond": cname, "alpha": alpha, "committed": committed,
                  "correct": ok, "answer": ans[:20], "doubt_load": dl, "n_tokens": n}
            out = {"id": f"{pid}__{cname}", "category": f"{pid} · steer {cname}",
                   "gold": q["gold"], "answer": ans, "correct": ok, "question": q["question"],
                   "lens_n": lens.n_prompts, "prompt_len": ids.shape[1], "n_tokens": n,
                   "trace": trace, "tokens": toks, "_sum": sm,
                   "positions": {p: {"token": toks[p], "by_layer": {l: per_layer[l].get(p, []) for l in LAYERS}}
                                 for p in span}}
            json.dump(out, open(outp, "w"))
            summary.append(sm)
            done += 1
            json.dump({"done": done, "total": total, "elapsed_min": round((time.time()-t0)/60, 1),
                       "summary": summary}, open(STATUS, "w"), indent=1)
            print(f"  [{done}/{total}] {pid:16} {cname:12} commit={committed} ok={ok} "
                  f"doubt={dl:.4f} ans={ans[:14]!r}", flush=True)
            torch.mps.empty_cache()

    json.dump({"done": done, "total": total, "summary": summary}, open(STATUS, "w"), indent=1)
    print(f"[done] {round((time.time()-t0)/60,1)} min -> {OUTDIR}/", flush=True)


if __name__ == "__main__":
    main()
