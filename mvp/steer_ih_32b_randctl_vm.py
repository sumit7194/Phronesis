#!/usr/bin/env python
"""Random-vector control at the SWEET-SPOT alpha for the IH-steering result (v3).

Rules out the confound: at alpha~92-184 (0.1-0.2x residual norm), is 'correct preserved +
confab perturbed toward humility' specific to the IH direction, or would ANY magnitude-matched
vector do it? Runs multi-seed random unit vectors at the SAME alphas the IH sweep used, on the
SAME 25 eval items. Compare hand-read to ih_32b_v3.json: IH should hedge/vaguen confabs; random
should just churn fluently.
"""
import argparse, json, time
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


class AdditiveSteeringHook:
    def __init__(self, layer_idx, vector, alpha):
        self.layer_idx, self.alpha = layer_idx, alpha
        v = torch.tensor(vector, dtype=torch.float32)
        self.v = (v / (v.norm() + 1e-10)).unsqueeze(0).unsqueeze(0)
        self.handle = None
    def hook_fn(self, m, i, out):
        h = out[0] if isinstance(out, tuple) else out
        h = h + self.alpha * self.v.to(h.device).to(h.dtype)
        return (h,) + out[1:] if isinstance(out, tuple) else h
    def attach(self, model):
        self.handle = model.model.layers[self.layer_idx].register_forward_hook(self.hook_fn)
    def detach(self):
        if self.handle: self.handle.remove(); self.handle = None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-32B")
    ap.add_argument("--layer", type=int, default=24)
    ap.add_argument("--vec", default="vectors_ih_32b/layer_24_virtue_vector.npy")
    ap.add_argument("--evalset", default="ih_steer_evalset.json")
    ap.add_argument("--fracs", default="0.1,0.15,0.2")     # the sweet-spot band from v3
    ap.add_argument("--seeds", default="0,1")
    ap.add_argument("--max-new", type=int, default=48)
    ap.add_argument("--out", default="ih_32b_randctl.json")
    args = ap.parse_args()

    vec = np.load(args.vec); dim = vec.shape[0]
    evalset = json.load(open(args.evalset))
    print(f"[data] {len(evalset)} items, dim {dim}, layer {args.layer}", flush=True)

    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, quantization_config=bnb, device_map="cuda").eval()
    print("[load] done", flush=True)

    def encode(q):
        m = [{"role": "user", "content": q + " Answer with just the name, as briefly as possible."}]
        try:
            enc = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt",
                                          return_dict=True, enable_thinking=False)
        except TypeError:
            enc = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        return {k: v.to("cuda") for k, v in enc.items()}

    # measure residual norm at layer L (same calibration as v3 -> matching alphas)
    norms = []
    def cap(m, i, out):
        h = out[0] if isinstance(out, tuple) else out
        norms.append(float(h[0].norm(dim=-1).mean()))
    hh = model.model.layers[args.layer].register_forward_hook(cap)
    with torch.no_grad():
        for it in evalset[:5]:
            model(**encode(it["q"]))
    hh.remove()
    rnorm = float(np.mean(norms))
    ALPHAS = [round(float(f) * rnorm, 1) for f in args.fracs.split(",")]
    print(f"[calib] resid norm {rnorm:.0f}; sweet-spot alphas = {ALPHAS}", flush=True)

    def gen(q, vector, alpha):
        enc = encode(q); L = enc["input_ids"].shape[1]
        hook = AdditiveSteeringHook(args.layer, vector, alpha); hook.attach(model)
        try:
            with torch.no_grad():
                o = model.generate(**enc, max_new_tokens=args.max_new, do_sample=False, pad_token_id=tok.eos_token_id)
        finally:
            hook.detach()
        txt = tok.decode(o[0][L:], skip_special_tokens=True)
        return next((l.strip() for l in txt.split("\n") if l.strip()), "")[:120]

    result = dict(model=args.model, layer=args.layer, residual_norm=rnorm, alphas=ALPHAS,
                  vec_norm=float(np.linalg.norm(vec)), seeds=args.seeds, items=[])
    t0 = time.time()
    for j, it in enumerate(evalset):
        rec = dict(q=it["q"], gold=it["gold"], kind=it["kind"], base=it["base"], rand={})
        for seed in [int(s) for s in args.seeds.split(",")]:
            rv = np.random.default_rng(seed).standard_normal(dim).astype(np.float32)  # fixed dir per seed
            rec["rand"][f"seed{seed}"] = {str(a): gen(it["q"], rv, a) for a in ALPHAS}
        result["items"].append(rec)
        json.dump(result, open(args.out, "w"), indent=1)
        print(f"  [{j+1}/{len(evalset)}] {it['kind']:7s} {it['q'][:38]:38s} ({(time.time()-t0):.0f}s)", flush=True)
    print(f"[done] -> {args.out}", flush=True)


if __name__ == "__main__":
    main()
