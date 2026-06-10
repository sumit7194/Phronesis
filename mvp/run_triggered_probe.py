#!/usr/bin/env python
"""Rumination-TRIGGERED steering probe (F162 follow-up; 'phase-gating generalized').

Conditions per prompt:
  baseline        — no steering
  alwayson_a16    — v_IH attached for the whole generation (the F162 arm)
  trig_vIH        — generate unsteered for `--trigger-at` tokens; if </think> has NOT
                    appeared (rumination), attach v_IH for the remainder; else never steer
  trig_rand_s1/s2 — same trigger, matched-norm random vectors (the control)

Notes:
- Greedy decoding throughout (deterministic). When the trigger does not fire, the
  triggered condition's output equals baseline by construction.
- When the hook attaches for the continuation, the re-encoded prefix is also steered
  during prefill — same semantics as the F160 phase-gating harness (documented).
- Reuses comparable 2048-budget cells (baseline/alwayson) from a prior results file
  via --reuse, matched by (id, condition). Saves after EVERY generation; resumable.
"""
import argparse, json, os, sys, time
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from steer import AdditiveSteeringHook

CFG = dict(hf_id="Qwen/Qwen3-4B", layer_accessor="model.layers", thinking=True)

def delivered(text):
    if "</think>" in text:
        return text.rsplit("</think>", 1)[-1].strip()
    return text.strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", default="../corpus/eval-prompts/hard-reasoning-v2.json")
    ap.add_argument("--vector", default="results/vectors/qwen3-4b/triplets-intellectual-humility/last_token/layer_17_virtue_vector.npy")
    ap.add_argument("--layer", type=int, default=17)
    ap.add_argument("--alpha", type=float, default=16.0)
    ap.add_argument("--trigger-at", type=int, default=768)
    ap.add_argument("--tag", default="trig", help="condition-name prefix (e.g. trig1200)")
    ap.add_argument("--max-new", type=int, default=2048)
    ap.add_argument("--reuse", default="results/local_probe_hardreasoning.json",
                    help="prior results file to copy comparable baseline/alwayson cells from (2048-budget only)")
    ap.add_argument("--output", default="results/local_probe_triggered.json")
    args = ap.parse_args()

    dev = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
    here = os.path.dirname(os.path.abspath(__file__))
    prompts = json.load(open(os.path.join(here, args.prompts)))
    vec = np.load(os.path.join(here, args.vector))
    rands = {f"{args.tag}_rand_s{s+1}": np.random.RandomState(1000 + s).randn(vec.shape[0]).astype(np.float32) for s in range(2)}

    out_path = os.path.join(here, args.output)
    by_id = {}
    if os.path.exists(out_path):
        try:
            for r in json.load(open(out_path)):
                by_id[r["id"]] = r
            print(f"[resume] {len(by_id)} items present", flush=True)
        except Exception:
            by_id = {}

    # copy-reuse comparable cells (greedy => identical regeneration; only 2048-budget items)
    reuse_path = os.path.join(here, args.reuse)
    REUSE_2048 = {"hr-01-br-mammogram","hr-02-br-taxicab","hr-03-br-rare-disease",
                  "hr-04-br-linda-conjunction","hr-06-bbh-logic","hr-07-bbh-logic","hr-10-gsm8k"}
    if os.path.exists(reuse_path):
        for r in json.load(open(reuse_path)):
            if r["id"] in REUSE_2048:
                rec = by_id.setdefault(r["id"], {})
                rec.setdefault("baseline", r.get("baseline"))
                if "steered_a16" in r:
                    rec.setdefault("alwayson_a16", r["steered_a16"])

    def save():
        merged = []
        for p in prompts:
            rec = by_id.get(p["id"], {})
            row = {k: p[k] for k in ("id","category","prompt","truth","source") if k in p}
            row.update(rec)
            merged.append(row)
        json.dump(merged, open(out_path, "w"), indent=1)

    print(f"[load] {CFG['hf_id']} on {dev} ...", flush=True)
    tok = AutoTokenizer.from_pretrained(CFG["hf_id"])
    model = AutoModelForCausalLM.from_pretrained(CFG["hf_id"], torch_dtype=torch.float16).to(dev)
    model.eval()
    print("[load] done", flush=True)

    def encode(msgs):
        try:
            enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt",
                                          return_dict=True, enable_thinking=True)
        except TypeError:
            enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        return {k: v.to(dev) for k, v in enc.items()}

    def gen_plain(msgs, mnt, v=None, alpha=None):
        enc = encode(msgs); in_len = enc["input_ids"].shape[1]
        hook = None
        if v is not None:
            hook = AdditiveSteeringHook(layer_idx=args.layer, virtue_vector=v, alpha=alpha)
            hook.attach(model, layer_accessor=CFG["layer_accessor"])
        try:
            with torch.no_grad():
                out = model.generate(**enc, max_new_tokens=mnt, do_sample=False, pad_token_id=tok.eos_token_id)
        finally:
            if hook: hook.detach()
        return tok.decode(out[0][in_len:], skip_special_tokens=True)

    def gen_triggered(msgs, mnt, v):
        enc = encode(msgs); in_len = enc["input_ids"].shape[1]
        with torch.no_grad():
            out1 = model.generate(**enc, max_new_tokens=args.trigger_at, do_sample=False, pad_token_id=tok.eos_token_id)
        seg1 = out1[0][in_len:]
        txt1 = tok.decode(seg1, skip_special_tokens=True)
        n1 = int(seg1.shape[0])
        finished = n1 < args.trigger_at or seg1[-1].item() == tok.eos_token_id
        ruminating = ("</think>" not in txt1)
        meta = {"triggered": False, "pre_tokens": n1, "closed_think_pre": not ruminating}
        if finished or mnt - n1 <= 0:
            return txt1, meta
        hook = None
        if ruminating:
            meta["triggered"] = True
            hook = AdditiveSteeringHook(layer_idx=args.layer, virtue_vector=v, alpha=args.alpha)
            hook.attach(model, layer_accessor=CFG["layer_accessor"])
        try:
            with torch.no_grad():
                out2 = model.generate(input_ids=out1, attention_mask=torch.ones_like(out1),
                                      max_new_tokens=mnt - n1, do_sample=False, pad_token_id=tok.eos_token_id)
        finally:
            if hook: hook.detach()
        return tok.decode(out2[0][in_len:], skip_special_tokens=True), meta

    conds = ["baseline", "alwayson_a16", f"{args.tag}_vIH", f"{args.tag}_rand_s1", f"{args.tag}_rand_s2"]
    for p in prompts:
        msgs = [{"role": "user", "content": p["prompt"]}]
        rec = by_id.setdefault(p["id"], {})
        for c in conds:
            if rec.get(c):
                continue
            t = time.time()
            if c == "baseline":
                rec[c] = delivered(gen_plain(msgs, args.max_new))
            elif c == "alwayson_a16":
                rec[c] = delivered(gen_plain(msgs, args.max_new, v=vec, alpha=args.alpha))
            elif c == f"{args.tag}_vIH":
                txt, meta = gen_triggered(msgs, args.max_new, vec)
                rec[c] = delivered(txt); rec[c + "_meta"] = meta
            else:
                txt, meta = gen_triggered(msgs, args.max_new, rands[c])
                rec[c] = delivered(txt); rec[c + "_meta"] = meta
            save()
            print(f"  {p['id']:26s} {c:14s} {time.time()-t:.0f}s", flush=True)
    print("[done] ->", out_path)

if __name__ == "__main__":
    main()
