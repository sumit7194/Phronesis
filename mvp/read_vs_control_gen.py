#!/usr/bin/env python
"""Read-vs-Control Part 2 — free-generation hand-read (docs/prereg-readvscontrol.md, secondary).

Part 1 showed diff-of-means (rank1) is the only clean control lever on the MC1 margin, but modest. This
asks the direct F121 question: under +rank1 steering, does the model actually HEDGE / ABSTAIN / CORRECT
in open generation, or does it stay on the myth? Generates Q->A continuations on baseline-wrong items
under {baseline, +rank1, -rank1, random}, all matched-norm at L20. Output is hand-read under a frozen
rubric (abstain/hedge | correct | myth | degenerate), author-reviewed. Directions re-fit identically to
Part 1 (same split/seed).
"""
import argparse, json, os, sys
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from steer import AdditiveSteeringHook

HF_ID = "Qwen/Qwen3-4B"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/legibility")
    ap.add_argument("--layer", type=int, default=20)
    ap.add_argument("--n-items", type=int, default=16)
    ap.add_argument("--max-new", type=int, default=64)
    ap.add_argument("--output", default="results/legibility/readvscontrol_gen.json")
    args = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(here, args.dir)
    acts = np.load(os.path.join(d, "actsB.npy")); meta = json.load(open(os.path.join(d, "metaB.json")))
    layers, items = meta["layers"], meta["items"]; n = len(items); acts = acts[:n]
    li = layers.index(args.layer); X = acts[:, li, :]
    y = np.array([1 if it["correct"] else 0 for it in items])

    rng = np.random.RandomState(0); idx = np.arange(n); tr = np.zeros(n, bool)
    for c in (0, 1):
        ci = idx[y == c]; rng.shuffle(ci); tr[ci[: len(ci)//2]] = True
    te = ~tr
    dom = X[tr][y[tr] == 1].mean(0) - X[tr][y[tr] == 0].mean(0)
    rank1 = (dom / (np.linalg.norm(dom) + 1e-9)).astype(np.float32)
    randv = np.random.RandomState(50).randn(X.shape[1]).astype(np.float32); randv /= np.linalg.norm(randv)
    a = float(np.linalg.norm(X, axis=1).mean())   # matched injection norm (frac 1.0)

    test_wrong = [i for i in range(n) if te[i] and not items[i]["correct"]][: args.n_items]
    print(f"L*={args.layer} alpha={a:.1f} items={len(test_wrong)}", flush=True)

    dev = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
    tok = AutoTokenizer.from_pretrained(HF_ID)
    model = AutoModelForCausalLM.from_pretrained(HF_ID, torch_dtype=torch.float16).to(dev).eval()

    def gen(prompt, vec, alpha):
        hook = None
        if vec is not None:
            hook = AdditiveSteeringHook(layer_idx=args.layer, virtue_vector=vec, alpha=alpha); hook.attach(model)
        try:
            enc = tok(prompt, return_tensors="pt").to(dev)
            with torch.no_grad():
                out = model.generate(**enc, max_new_tokens=args.max_new, do_sample=False, pad_token_id=tok.eos_token_id)
        finally:
            if hook: hook.detach()
        txt = tok.decode(out[0][enc["input_ids"].shape[1]:], skip_special_tokens=True)
        return txt.split("\nQ:")[0].strip().replace("\n", " ")[:240]

    conds = [("baseline", None, 0.0), ("+rank1", rank1, a), ("-rank1", rank1, -a), ("random", randv, a)]
    rows = []
    for k, i in enumerate(test_wrong):
        it = items[i]; prompt = f"Q: {it['question']}\nA:"
        r = {"question": it["question"], "gold": it["gold_answer"], "myth_picked": it["pred_answer"], "gen": {}}
        for name, vec, alpha in conds:
            r["gen"][name] = gen(prompt, vec, alpha)
        rows.append(r)
        print(f"  [{k+1}/{len(test_wrong)}] {it['question'][:60]}", flush=True)
    json.dump({"layer": args.layer, "alpha": a, "rows": rows}, open(os.path.join(here, args.output), "w"), indent=1)
    print(f"[done] -> {args.output}", flush=True)

if __name__ == "__main__":
    main()
