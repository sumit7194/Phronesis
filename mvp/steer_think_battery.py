#!/usr/bin/env python
"""Steering × thinking on TruthfulQA (calibration). Overnight-style data-collection run.

For each TruthfulQA-generation item, generate an answer under 5 conditions
(baseline / IH / EG / RT / random, all at one layer, matched α) × 2 modes (thinking on/off).
Tests whether a virtue vector does MORE when it can shape the chain-of-thought (think) vs only the
answer (nothink). Saves RAW answers + traces; scoring is a next-day HAND-READ (auto truth/myth match
is only a prefilter). Checkpointed every 2 items (resumes after kill/power).
"""
import argparse, json, os, re, time, unicodedata
import numpy as np, torch, sys
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from steer import AdditiveSteeringHook

HF_ID = "Qwen/Qwen3-4B"
VEC = {
    "IH": "results/vectors/qwen3-4b/triplets-intellectual-humility/last_token/layer_{L}_virtue_vector.npy",
    "EG": "results/vectors/qwen3-4b/triplets-evidence-grounding/last_token/layer_{L}_virtue_vector.npy",
    "RT": "results/vectors/qwen3-4b/triplets-reasoning-transparency/last_token/layer_{L}_virtue_vector.npy",
    "random": "results/vectors/qwen3-4b/random_L22_vector.npy",
}

def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFKD", str(s)) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", " ", s.lower()).strip()

def first_line(txt):
    return next((l.strip() for l in txt.split("\n") if l.strip()), "")[:120]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=80)
    ap.add_argument("--layer", type=int, default=17)
    ap.add_argument("--alpha", type=float, default=16.0)
    ap.add_argument("--max-new-think", type=int, default=640)
    ap.add_argument("--output", default="results/legibility/steer_think_tqa.json")
    args = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(here, args.output)

    vecs = {"baseline": None}
    for name, tmpl in VEC.items():
        p = os.path.join(here, tmpl.format(L=args.layer))
        if not os.path.exists(p):
            print(f"[warn] missing {name} at L{args.layer}: {p}"); continue
        vecs[name] = np.load(p).astype(np.float32)
    conds = list(vecs.keys())
    print(f"[cfg] L{args.layer} α{args.alpha} conditions={conds}", flush=True)

    ds = load_dataset("truthful_qa", "generation")["validation"]
    items = list(ds)[: args.n]

    results = []
    if os.path.exists(out_path):
        try:
            results = json.load(open(out_path))["rows"]
        except Exception:
            results = []
    start = len(results)
    if start:
        print(f"[resume] {start}/{len(items)} done", flush=True)

    dev = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[load] {HF_ID} on {dev} ...", flush=True)
    tok = AutoTokenizer.from_pretrained(HF_ID)
    model = AutoModelForCausalLM.from_pretrained(HF_ID, torch_dtype=torch.float16).to(dev).eval()
    close_ids = tok("</think>", add_special_tokens=False)["input_ids"]
    print("[load] done", flush=True)

    def encode(q, thinking):
        msgs = [{"role": "user", "content": q + " Answer concisely."}]
        try:
            enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt",
                                          return_dict=True, enable_thinking=thinking)
        except TypeError:
            enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        return {k: v.to(dev) for k, v in enc.items()}

    def find_close(ids):
        n = len(close_ids)
        for i in range(len(ids) - n, -1, -1):
            if ids[i:i + n] == close_ids:
                return i + n
        return None

    def gen(q, thinking, vec):
        hook = None
        if vec is not None:
            hook = AdditiveSteeringHook(layer_idx=args.layer, virtue_vector=vec, alpha=args.alpha)
            hook.attach(model)
        try:
            enc = encode(q, thinking); in_len = enc["input_ids"].shape[1]
            with torch.no_grad():
                if not thinking:
                    out = model.generate(**enc, max_new_tokens=48, do_sample=False, pad_token_id=tok.eos_token_id)
                    return first_line(tok.decode(out[0][in_len:], skip_special_tokens=True)), ""
                out1 = model.generate(**enc, max_new_tokens=args.max_new_think, do_sample=False, pad_token_id=tok.eos_token_id)
                ids = out1[0].tolist()
                if find_close(ids[in_len:]) is None:
                    ids = ids + close_ids
                inp = torch.tensor([ids], device=dev)
                out2 = model.generate(input_ids=inp, attention_mask=torch.ones_like(inp),
                                      max_new_tokens=48, do_sample=False, pad_token_id=tok.eos_token_id)
            final = out2[0].tolist(); c = find_close(final)
            ans = first_line(tok.decode(final[c:] if c else final[in_len:], skip_special_tokens=True))
            trace = tok.decode(final[in_len:c] if c else final[in_len:], skip_special_tokens=True)[:400]
            return ans, trace
        finally:
            if hook:
                hook.detach()

    def score(ans, corr, incorr):
        na = norm(ans)
        t = any(len(norm(a)) >= 4 and norm(a) in na for a in corr)
        m = any(len(norm(a)) >= 4 and norm(a) in na for a in incorr)
        return bool(t), bool(m)

    t0 = time.time()
    for j in range(start, len(items)):
        it = items[j]; q = it["question"]
        corr = it.get("correct_answers", []); incorr = it.get("incorrect_answers", [])
        cells = {}
        for cname in conds:
            for mode in ("think", "nothink"):
                ans, trace = gen(q, mode == "think", vecs[cname])
                at, am = score(ans, corr, incorr)
                cells[f"{cname}|{mode}"] = dict(answer=ans, trace_len=len(trace), trace=trace,
                                                auto_truth=at, auto_myth=am)
        results.append(dict(question=q, best_answer=it.get("best_answer", ""),
                            correct=corr, incorrect=incorr, cells=cells))
        if (j + 1) % 2 == 0 or j + 1 == len(items):
            json.dump({"layer": args.layer, "alpha": args.alpha, "conditions": conds, "rows": results},
                      open(out_path, "w"), indent=1)
            el = time.time() - t0; per = el / max(1, j + 1 - start)
            print(f"  {j+1}/{len(items)}  ({per:.0f}s/item, ~{per*(len(items)-j-1)/3600:.1f}h left)", flush=True)
    print(f"[done] -> {out_path}", flush=True)

if __name__ == "__main__":
    main()
