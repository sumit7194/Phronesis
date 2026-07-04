#!/usr/bin/env python
"""Recover TRUE 4B reasoning accuracy by fixing the two measurement bugs F182 exposed:
  (1) LaTeX-robust scoring (reasoning_baseline.score, now patched)
  (2) force-commit-on-truncation extraction (s1 budget-forcing) for items the harness cut off.
Reuses the existing 40 traces (no re-reasoning) -> only short commit completions for the wrong ones.
Reports: old-auto -> robust-rescored -> robust+force-commit (true), per benchmark.
"""
import argparse, json, os, sys, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
sys.path.insert(0, os.path.dirname(__file__))
from reasoning_baseline import extract_answer, score, all_boxed
import numpy as np

PRIMER = "\n\n</think>\n\nThe final answer is \\boxed{"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--infile", default="results/legibility/reasoning_4b_overnight.json")
    ap.add_argument("--out", default="results/legibility/reasoning_4b_rescored.json")
    args = ap.parse_args()
    rows = json.load(open(args.infile))["rows"]
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float16).to(args.device).eval()
    print(f"[load] {args.model}", flush=True)

    def chat_ids(q):
        m = [{"role": "user", "content": q + "\nReason step by step, then give the final answer in \\boxed{}."}]
        try: e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True, enable_thinking=True)
        except TypeError: e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        return e["input_ids"]

    @torch.no_grad()
    def force_commit(q, trace):
        base = chat_ids(q); cont = tok(trace + PRIMER, add_special_tokens=False, return_tensors="pt")["input_ids"]
        ids = torch.cat([base, cont], 1).to(args.device)
        o = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids), max_new_tokens=32,
                           do_sample=False, pad_token_id=tok.eos_token_id)
        return tok.decode(o[0][ids.shape[1]:], skip_special_tokens=True).split("}")[0].strip()

    out = []
    for i, r in enumerate(rows):
        src, gold, tr = r["source"], str(r["gold"]), r["greedy_trace"]
        old_ok = bool(r["pass1"])                                        # original auto-score
        rob_ok = score(extract_answer(tr, src), gold, src)              # robust re-score, same extraction
        commit_ans, commit_ok = None, False
        if not rob_ok:                                                  # try to rescue via force-commit
            commit_ans = force_commit(r["question"], tr)
            commit_ok = bool(score(commit_ans, gold, src))
        out.append(dict(idx=i, source=src, gold=gold, old_ok=old_ok, robust_ok=bool(rob_ok),
                        commit_ans=commit_ans, commit_ok=commit_ok, true_ok=bool(rob_ok or commit_ok)))
        json.dump(out, open(args.out, "w"), indent=1)
        if args.device == "mps": torch.mps.empty_cache()
        if (i+1) % 10 == 0: print(f"  {i+1}/{len(rows)}", flush=True)

    print("\n=== accuracy recovery ===")
    for s in ("math500", "gsm8k"):
        rs = [x for x in out if x["source"] == s]
        if not rs: continue
        a=np.mean([x["old_ok"] for x in rs]); b=np.mean([x["robust_ok"] for x in rs]); c=np.mean([x["true_ok"] for x in rs])
        print(f"  {s:8} n={len(rs)}  old-auto {a:.0%}  ->  +robust-score {b:.0%}  ->  +force-commit {c:.0%}")
    print("[done] ->", args.out)

if __name__ == "__main__":
    main()
