#!/usr/bin/env python
"""S3 (exp-gated-controller): does gating on the L14 reasoning-decisiveness signal find a GOOD
commit point — right answer, fewer tokens — better than random timing?

Retrospective gate-eval (cheap: reuses solved traces + short force-commit completions).
Per solved trace, force-commit at:
  GATE   = first token (after min_frac) where proj_z crosses tau (model entered a 'conclude' state)
  RANDOM = matched random points (control: same 'stop early' budget, random timing) x3 seeds
  FULL   = end of trace (baseline: full budget then commit)
Metric: accuracy + tokens-used. GATE wins iff it matches FULL accuracy with fewer tokens AND beats RANDOM.
"""
import argparse, json, os, sys
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
sys.path.insert(0, os.path.dirname(__file__))
from reasoning_baseline import score

PRIMER = "\n\n</think>\n\nThe final answer is \\boxed{"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--layer", type=int, default=14)
    ap.add_argument("--axes", default="results/legibility/axes_4b.npy")
    ap.add_argument("--traces", default="results/legibility/reasoning_4b_overnight.json")
    ap.add_argument("--rescored", default="results/legibility/reasoning_4b_rescored.json")
    ap.add_argument("--tau", type=float, default=1.0)         # conclude-state threshold (z)
    ap.add_argument("--min-frac", type=float, default=0.25)   # don't gate in first 25%
    ap.add_argument("--nrand", type=int, default=3)
    ap.add_argument("--out", default="results/legibility/s3_gate_pilot.json")
    args = ap.parse_args()
    L = args.layer
    v = np.asarray(np.load(args.axes, allow_pickle=True).item()[f"commitment_{L}"], "float32"); v /= np.linalg.norm(v)
    rows = json.load(open(args.traces))["rows"]
    resc = {r["idx"]: r for r in json.load(open(args.rescored))}
    # solved MATH traces (true_ok) — the dithering-candidate regime
    pick = [i for i, r in enumerate(rows) if r["source"] == "math500" and resc.get(i, {}).get("true_ok")][:8]

    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float16).to(args.device).eval()
    print(f"[load] {args.model}; gate tau={args.tau}; solved MATH traces {pick}", flush=True)
    rng = np.random.default_rng(5)

    def chat_ids(q):
        m = [{"role": "user", "content": q + "\nReason step by step, then give the final answer in \\boxed{}."}]
        try: e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True, enable_thinking=True)
        except TypeError: e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        return e["input_ids"]

    @torch.no_grad()
    def commit_at(base, trace_ids, cut):
        pr = tok(PRIMER, add_special_tokens=False, return_tensors="pt")["input_ids"]
        ids = torch.cat([base, trace_ids[:, :cut], pr], 1).to(args.device)
        o = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids), max_new_tokens=32,
                           do_sample=False, pad_token_id=tok.eos_token_id)
        return tok.decode(o[0][ids.shape[1]:], skip_special_tokens=True).split("}")[0].strip()

    results = []
    for idx in pick:
        r = rows[idx]; gold = str(r["gold"])
        base = chat_ids(r["question"])
        tids = tok(r["greedy_trace"], add_special_tokens=False, return_tensors="pt")["input_ids"]
        T = tids.shape[1]
        # per-token L14 projection over the trace (cheap: no vocab)
        with torch.no_grad():
            full = torch.cat([base, tids], 1).to(args.device)
            H = model(input_ids=full, output_hidden_states=True).hidden_states[L+1][0].float().cpu().numpy()
        proj = H[base.shape[1]:] @ v
        z = (proj - proj.mean()) / (proj.std() + 1e-6)
        lo = int(T * args.min_frac)
        # GATE (first crossing of tau after lo) + GATE-LAST (last crossing, closest to the answer)
        cross = np.where(z[lo:] > args.tau)[0]
        gate_cut = (lo + int(cross[0])) if len(cross) else T
        gate_last = (lo + int(cross[-1])) if len(cross) else T
        gate_ans = commit_at(base, tids, gate_cut); gate_ok = bool(score(gate_ans, gold, r["source"]))
        last_ans = commit_at(base, tids, gate_last); last_ok = bool(score(last_ans, gold, r["source"]))
        # FULL baseline
        full_ans = commit_at(base, tids, T); full_ok = bool(score(full_ans, gold, r["source"]))
        # RANDOM control: BUDGET-MATCHED to the gate (random position, same mean token count as gate)
        rand = []
        span = max(40, gate_cut - lo)
        for s in range(args.nrand):
            rc = int(np.clip(rng.integers(gate_cut - span, gate_cut + span + 1), lo, T))
            ra = commit_at(base, tids, rc); rand.append((rc, bool(score(ra, gold, r["source"]))))
        results.append(dict(idx=idx, gold=gold, T=int(T),
                            gate_cut=int(gate_cut), gate_ok=gate_ok, gate_saved=round(1-gate_cut/T, 2),
                            gate_last=int(gate_last), last_ok=last_ok, last_saved=round(1-gate_last/T, 2),
                            full_ok=full_ok, rand=[(int(c), o) for c, o in rand]))
        json.dump(results, open(args.out, "w"), indent=1)
        if args.device == "mps": torch.mps.empty_cache()
        print(f"  #{idx} gold={gold:10} | GATE-1st @{gate_cut}(save {1-gate_cut/T:.0%}) ok={gate_ok} | "
              f"GATE-last @{gate_last}(save {1-gate_last/T:.0%}) ok={last_ok} | FULL ok={full_ok} | RAND(budget-matched) ok={[o for _,o in rand]}", flush=True)

    # verdict
    ga = np.mean([r["gate_ok"] for r in results]); fa = np.mean([r["full_ok"] for r in results])
    ra = np.mean([o for r in results for _, o in r["rand"]])
    gt = np.mean([r["gate_cut"]/r["T"] for r in results]); rt = np.mean([c/r["T"] for r in results for c, _ in r["rand"]])
    print(f"\n=== S3 VERDICT (n={len(results)} solved MATH) ===")
    la=np.mean([r["last_ok"] for r in results]); lt=np.mean([r["gate_last"]/r["T"] for r in results])
    print(f"  GATE-1st : acc {ga:.0%}  tokens {gt:.0%} of full")
    print(f"  GATE-last: acc {la:.0%}  tokens {lt:.0%} of full")
    print(f"  RANDOM: acc {ra:.0%}  tokens {rt:.0%} of full   (matched-budget control)")
    print(f"  FULL  : acc {fa:.0%}  tokens 100%")
    print(f"  -> gate WINS iff acc({ga:.0%}) ~ full({fa:.0%}) with fewer tokens AND acc > random({ra:.0%})")
    print("[done] ->", args.out)

if __name__ == "__main__":
    main()
