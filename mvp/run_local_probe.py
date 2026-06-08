#!/usr/bin/env python
"""Local (Mac / MPS) baseline-vs-steered probe for category-C question types.

For each prompt: generate a baseline answer, then steered answers with the v_IH
vector at the given alphas. Saves to JSON for HAND-reading (no auto-scoring).
Checkpoints after every prompt so partial runs survive interruption.

Example:
  mvp/.venv/bin/python mvp/run_local_probe.py --model qwen3-4b --limit 4 --alphas 16
"""
import argparse, json, os, sys, time
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from steer import AdditiveSteeringHook

MODELS = {
    "qwen3-4b":   dict(hf_id="Qwen/Qwen3-4B",            layer_accessor="model.layers", thinking=True),
    "qwen2.5-3b": dict(hf_id="Qwen/Qwen2.5-3B-Instruct", layer_accessor="model.layers", thinking=False),
}

def delivered(text, thinking):
    if thinking and "</think>" in text:
        return text.rsplit("</think>", 1)[-1].strip()
    return text.strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3-4b", choices=list(MODELS))
    ap.add_argument("--prompts", default="../corpus/eval-prompts/category-c-probe.json")
    ap.add_argument("--vector", default="results/vectors/qwen3-4b/triplets-intellectual-humility/last_token/layer_17_virtue_vector.npy")
    ap.add_argument("--layer", type=int, default=17)
    ap.add_argument("--alphas", default="8,16")
    ap.add_argument("--limit", type=int, default=0, help="only first N prompts (0 = all)")
    ap.add_argument("--max-new", type=int, default=0, help="override per-prompt max_new_tokens (0 = use battery value)")
    ap.add_argument("--random", type=int, default=0, help="N matched-norm random-vector controls at the first alpha (F160 lesson)")
    ap.add_argument("--output", default="results/local_probe_categoryC.json")
    args = ap.parse_args()

    dev = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
    cfg = MODELS[args.model]
    alphas = [float(a) for a in args.alphas.split(",") if a.strip()]
    here = os.path.dirname(os.path.abspath(__file__))
    prompts = json.load(open(os.path.join(here, args.prompts)))
    if args.limit:
        prompts = prompts[:args.limit]
    vpath = os.path.join(here, args.vector)
    vec = np.load(vpath) if os.path.exists(vpath) else None
    if vec is None:
        print(f"[warn] no vector at {vpath}; baseline only")

    print(f"[load] {cfg['hf_id']} on {dev} (fp16) ...", flush=True)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(cfg["hf_id"])
    model = AutoModelForCausalLM.from_pretrained(cfg["hf_id"], torch_dtype=torch.float16).to(dev)
    model.eval()
    print(f"[load] done in {time.time()-t0:.0f}s", flush=True)

    def gen(msgs, mnt):
        try:
            enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt",
                                          return_dict=True, enable_thinking=cfg["thinking"])
        except TypeError:
            enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt",
                                          return_dict=True)
        enc = {k: v.to(dev) for k, v in enc.items()}
        in_len = enc["input_ids"].shape[1]
        with torch.no_grad():
            out = model.generate(**enc, max_new_tokens=mnt, do_sample=False, pad_token_id=tok.eos_token_id)
        return tok.decode(out[0][in_len:], skip_special_tokens=True)

    out_path = os.path.join(here, args.output)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    results = []
    for i, p in enumerate(prompts):
        mnt = args.max_new or p.get("max_new_tokens", 700)
        msgs = [{"role": "user", "content": p["prompt"]}]
        t = time.time()
        rec = {k: p[k] for k in ("id", "category", "prompt", "expected_behavior", "truth", "myth", "source") if k in p}
        rec["baseline"] = delivered(gen(msgs, mnt), cfg["thinking"])
        for a in alphas:
            if vec is None:
                continue
            hook = AdditiveSteeringHook(layer_idx=args.layer, virtue_vector=vec, alpha=a)
            hook.attach(model, layer_accessor=cfg["layer_accessor"])
            try:
                rec[f"steered_a{int(a)}"] = delivered(gen(msgs, mnt), cfg["thinking"])
            finally:
                hook.detach()
        # matched-norm random-vector controls at the first alpha (the hook unit-normalizes, so norm is matched by construction)
        if args.random and vec is not None:
            a0 = alphas[0]
            for s in range(args.random):
                rv = np.random.RandomState(1000 + s).randn(vec.shape[0]).astype(np.float32)
                hook = AdditiveSteeringHook(layer_idx=args.layer, virtue_vector=rv, alpha=a0)
                hook.attach(model, layer_accessor=cfg["layer_accessor"])
                try:
                    rec[f"random_a{int(a0)}_s{s+1}"] = delivered(gen(msgs, mnt), cfg["thinking"])
                finally:
                    hook.detach()
        results.append(rec)
        json.dump(results, open(out_path, "w"), indent=1)  # checkpoint
        print(f"[{i+1}/{len(prompts)}] {p['id']:28s} {time.time()-t:.0f}s", flush=True)
    print(f"[done] {len(results)} prompts -> {out_path}")

if __name__ == "__main__":
    main()
