#!/usr/bin/env python
"""Overnight commit-race (F182 follow-up, user-designed): on hard MATH-500 (level 4-5), compare
ways of handling the think-budget wall. All conditions use the SAME fixed ruler (robust scoring +
force-commit extraction), so differences are intervention effects, not measurement.

Conditions per item:
  A  BASELINE      think to FULL budget; force-commit primer only if </think> never emitted.
  B  EARLY-STOP    think to GATE budget only, then always force-commit (s1 budget-forcing control).
  C  COMMIT-VEC    think to GATE budget; if unclosed, continue to FULL with +v_commit@L17 steering
                   (late-onset gate, F163-style); force-commit if still unclosed.
  D  RANDOM-CTL    same protocol as C with random vectors of equal norm (2 seeds) — floor control.

Metrics: accuracy (fixed ruler), natural-close rate, generated tokens (efficiency), trace length.
Hypotheses: C closes naturally more often / shorter than A at equal accuracy; B risks premature
commits on unfinished items; D ≈ A (else the effect is norm, not direction).
Vector: content-controlled commit_17 from v_hedge_cc_4b.npy (RECALL-domain extraction — this is a
domain-transfer test onto reasoning; noted in the finding).
"""
import argparse, json, os, sys, time
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
sys.path.insert(0, os.path.dirname(__file__))
from reasoning_baseline import extract_answer, score

PRIMER = "\n\n</think>\n\nThe final answer is \\boxed{"

class Hook:
    def __init__(self, layer_idx, vec, alpha):
        self.layer_idx, self.alpha = layer_idx, alpha
        self.vec = vec / (np.linalg.norm(vec) + 1e-9)
        self.h = None
    def attach(self, model):
        v = torch.tensor(self.vec, dtype=torch.float16)
        def fn(m, i, o):
            hs = o[0] if isinstance(o, tuple) else o
            hs = hs + self.alpha * v.to(hs.device, hs.dtype)
            return (hs,) + tuple(o[1:]) if isinstance(o, tuple) else hs
        self.h = model.model.layers[self.layer_idx].register_forward_hook(fn)
    def detach(self):
        if self.h: self.h.remove(); self.h = None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--items", default="results/legibility/commit_race_items.json")
    ap.add_argument("--vec", default="results/legibility/v_hedge_cc_4b.npy")
    ap.add_argument("--layer", type=int, default=17)
    ap.add_argument("--alpha", type=float, default=24.0)     # frac 0.04 x resid 601 (CC-4B window)
    ap.add_argument("--gate", type=int, default=1536)         # gate budget (segment 1)
    ap.add_argument("--full", type=int, default=2048)         # full budget (A/C/D cap)
    ap.add_argument("--rand-seeds", default="0,1")
    ap.add_argument("--n", type=int, default=0)
    ap.add_argument("--out", default="results/legibility/commit_race_results.json")
    ap.add_argument("--status", default="results/legibility/status_race.json")
    args = ap.parse_args()

    items = json.load(open(args.items))
    if args.n: items = items[:args.n]
    store = np.load(args.vec, allow_pickle=True).item()
    v_commit = np.asarray(store[f"commit_{args.layer}"], dtype="float32")
    rng_vecs = {s: (lambda r: r / np.linalg.norm(r) * np.linalg.norm(v_commit))(
                    np.random.default_rng(s).standard_normal(v_commit.shape).astype("float32"))
                for s in [int(x) for x in args.rand_seeds.split(",")]}

    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float16).to(args.device).eval()
    CLOSE_ID = tok("</think>", add_special_tokens=False)["input_ids"]
    print(f"[load] {args.model} | L{args.layer} alpha={args.alpha} gate={args.gate} full={args.full}", flush=True)

    def chat_ids(q):
        m = [{"role": "user", "content": q + "\nReason step by step, then give the final answer in \\boxed{}."}]
        try: e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True, enable_thinking=True)
        except TypeError: e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        return e["input_ids"].to(args.device)

    def has_close(ids_list):
        n = len(CLOSE_ID)
        return any(ids_list[i:i+n] == CLOSE_ID for i in range(len(ids_list)-n+1))

    @torch.no_grad()
    def gen(ids, max_new, hook=None):
        if hook: hook.attach(model)
        try:
            o = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids),
                               max_new_tokens=max_new, do_sample=False, pad_token_id=tok.eos_token_id)
        finally:
            if hook: hook.detach()
        return o

    @torch.no_grad()
    def force_commit(full_ids):
        cont = tok(PRIMER, add_special_tokens=False, return_tensors="pt")["input_ids"].to(args.device)
        ids = torch.cat([full_ids, cont], 1)
        o = gen(ids, 32)
        return tok.decode(o[0][ids.shape[1]:], skip_special_tokens=True).split("}")[0].strip(), 32

    def run_condition(q, gold, src, mode, vec=None):
        base = chat_ids(q); L0 = base.shape[1]
        seg1_cap = args.gate if mode in ("early",) else args.gate
        o = gen(base, args.gate)
        ids_l = o[0].tolist(); gen_tok = len(ids_l) - L0
        closed = has_close(ids_l[L0:])
        forced = False
        if not closed:
            if mode == "early":
                pass                                  # straight to force-commit
            else:                                     # baseline / vector / random: continue to FULL
                hook = Hook(args.layer, vec, args.alpha) if (mode in ("vector","random") and vec is not None) else None
                o = gen(o, args.full - args.gate, hook=hook)
                ids_l = o[0].tolist(); gen_tok = len(ids_l) - L0
                closed = has_close(ids_l[L0:])
        text = tok.decode(ids_l[L0:], skip_special_tokens=True)
        if closed:
            ans = extract_answer(text, src)
        else:
            ans, extra = force_commit(o); gen_tok += extra; forced = True
        ok = bool(score(ans, gold, src))
        if args.device == "mps": torch.mps.empty_cache()
        return dict(ans=ans[:60], ok=ok, closed=bool(closed), forced=forced,
                    gen_tokens=int(gen_tok), trace_chars=len(text))

    results = []
    if os.path.exists(args.out):
        try: results = json.load(open(args.out))
        except Exception: results = []
    t0 = time.time()
    for j, it in enumerate(items):
        if j < len(results): continue                  # resume
        q, gold, src = it["question"], str(it["answer"]), it["source"]
        rec = dict(idx=j, level=str(it.get("level")), gold=gold, q=q[:80])
        rec["A_base"]   = run_condition(q, gold, src, "base")
        rec["B_early"]  = run_condition(q, gold, src, "early")
        rec["C_vector"] = run_condition(q, gold, src, "vector", v_commit)
        for s, rv in rng_vecs.items():
            rec[f"D_rand{s}"] = run_condition(q, gold, src, "random", rv)
        results.append(rec)
        json.dump(results, open(args.out, "w"), indent=1)
        per = (time.time() - t0) / max(1, len(results))
        json.dump(dict(done=len(results), total=len(items), s_per_item=round(per),
                       eta_min=round((len(items)-len(results))*per/60)), open(args.status, "w"))
        cs = {k: rec[k]["ok"] for k in rec if k[0] in "ABCD"}
        print(f"  [{j+1}/{len(items)}] L{rec['level']} " +
              " ".join(f"{k}:{'✓' if v else '✗'}" for k, v in cs.items()) +
              f" | A_tok={rec['A_base']['gen_tokens']} C_tok={rec['C_vector']['gen_tokens']} ({per:.0f}s/it)", flush=True)

    # summary
    conds = ["A_base","B_early","C_vector"] + [f"D_rand{s}" for s in rng_vecs]
    print("\n=== SUMMARY (n=%d) ===" % len(results))
    print(f"{'cond':10} {'acc':>6} {'nat-close':>10} {'forced':>7} {'avg-tok':>8}")
    for c in conds:
        rs = [r[c] for r in results]
        print(f"{c:10} {np.mean([x['ok'] for x in rs]):>6.0%} {np.mean([x['closed'] for x in rs]):>10.0%} "
              f"{np.mean([x['forced'] for x in rs]):>7.0%} {np.mean([x['gen_tokens'] for x in rs]):>8.0f}")
    print("[done] ->", args.out)

if __name__ == "__main__":
    main()
