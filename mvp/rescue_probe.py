#!/usr/bin/env python
"""Latent-insight probe: are the 4B's circling failures rescuable (World A: insight latent, stuck in rut)
or capability walls (World B: insight absent)? For each failed problem, re-run with:
  BASELINE  = original prompt (confirm it fails again),
  GENERIC   = a 'stop circling / don't overcomplicate' nudge (what a loop-break vector would do),
  SPECIFIC  = the actual structural insight handed over (upper bound: can it execute given the idea?).
If GENERIC rescues -> loop-break steering is promising (World A). If only SPECIFIC -> needs the insight.
If neither -> capability wall (World B).
"""
import argparse, json, os, sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
sys.path.insert(0, os.path.dirname(__file__))
from reasoning_baseline import extract_answer, score, all_boxed

PRIMER = "\n\n</think>\n\nThe final answer is \\boxed{"
HINTS = {
 9:  dict(generic="\n\n(You may be going in circles here. Step back: identify what stays fixed and what actually varies, then commit to a number.)",
         specific="\n\nHint: the product 2*3*4*5 = 120 is fixed no matter how you group the multiplications; only which suffix ending in 5 the +1 attaches to changes the value."),
 25: dict(generic="\n\n(This is a straightforward arithmetic problem - don't overcomplicate it. Compute directly and commit.)",
          specific="\n\nHint: everyone arrived in the cars and buses and went inside; just compute 20*3 + 12*35."),
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--traces", default="results/legibility/reasoning_4b_overnight.json")
    ap.add_argument("--max-think", type=int, default=2048)
    ap.add_argument("--out", default="results/legibility/rescue_probe.json")
    args = ap.parse_args()
    rows = json.load(open(args.traces))["rows"]
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float16).to(args.device).eval()
    print(f"[load] {args.model}", flush=True)

    @torch.no_grad()
    def solve(q):
        m = [{"role": "user", "content": q + "\nReason step by step, then give the final answer in \\boxed{}."}]
        try: e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True, enable_thinking=True)
        except TypeError: e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        ids = e["input_ids"].to(args.device); L = ids.shape[1]
        o = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids), max_new_tokens=args.max_think,
                           do_sample=False, pad_token_id=tok.eos_token_id)
        full = tok.decode(o[0][L:], skip_special_tokens=True)
        if all_boxed(full):
            return extract_answer(full, "math500")
        # force-commit if it truncated without boxing
        pr = tok(PRIMER, add_special_tokens=False, return_tensors="pt")["input_ids"].to(args.device)
        ids2 = torch.cat([o[0:1], pr], 1)
        o2 = model.generate(input_ids=ids2, attention_mask=torch.ones_like(ids2), max_new_tokens=32,
                            do_sample=False, pad_token_id=tok.eos_token_id)
        return tok.decode(o2[0][ids2.shape[1]:], skip_special_tokens=True).split("}")[0].strip()

    out = []
    for idx, hints in HINTS.items():
        r = rows[idx]; gold = str(r["gold"]); q = r["question"]; src = r["source"]
        conds = {"baseline": q, "generic": q + hints["generic"], "specific": q + hints["specific"]}
        res = {}
        for name, prompt in conds.items():
            ans = solve(prompt); ok = bool(score(ans, gold, src))
            res[name] = dict(ans=ans[:30], ok=ok)
            print(f"  #{idx} [{name:9}] -> '{ans[:24]}'  {'OK' if ok else 'wrong'}", flush=True)
            if args.device == "mps": torch.mps.empty_cache()
        out.append(dict(idx=idx, gold=gold, **res))
        json.dump(out, open(args.out, "w"), indent=1)
        print()
    print("=== VERDICT ===")
    for r in out:
        w = "World A (loop-break promising)" if r["generic"]["ok"] else \
            ("needs-insight (specific only)" if r["specific"]["ok"] else "World B (capability wall)")
        print(f"  #{r['idx']}: baseline={r['baseline']['ok']} generic={r['generic']['ok']} specific={r['specific']['ok']}  -> {w}")
    print("[done] ->", args.out)

if __name__ == "__main__":
    main()
