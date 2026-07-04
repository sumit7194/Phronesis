#!/usr/bin/env python
"""Gate->commit pilot (Phase 2, user-designed). Tests whether forcing the model to COMMIT at
budget-truncation rescues the "reached-the-answer-but-dithered-until-cut-off" failures (F181 confound).

Conditions per prompt:
  A. BASELINE      — the original truncated generation (already have it; scored wrong).
  B. FORCE-STOP    — s1-style control: splice '</think> ... final answer is \boxed{' onto the truncated
                     trace and let it fill the box. Reuses the existing trace (cheap: ~30-token completion).
  C. COMMIT-VECTOR — [added after 4B commit vector extracted] steer residual toward assert/commit.

Small curated set (commit_pilot_prompts.json): truncated (commit-candidate) + genuinely-wrong (control).
Model: Qwen3-4B fp16/mps. Reads baseline traces from reasoning_4b_overnight.json.
"""
import argparse, json, os, re, sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
sys.path.insert(0, os.path.dirname(__file__))
from reasoning_baseline import extract_boxed, score, all_boxed

CLOSE = "</think>"
PRIMER = "\n\n</think>\n\nThe final answer is \\boxed{"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--prompts", default="results/legibility/commit_pilot_prompts.json")
    ap.add_argument("--baseline", default="results/legibility/reasoning_4b_overnight.json")
    ap.add_argument("--out", default="results/legibility/commit_pilot_results.json")
    args = ap.parse_args()

    prompts = json.load(open(args.prompts))
    base_rows = json.load(open(args.baseline))["rows"]
    by_q = {r["question"]: r for r in base_rows}

    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float16).to(args.device).eval()
    print(f"[load] {args.model} on {args.device}", flush=True)

    def chat_ids(q):
        m = [{"role": "user", "content": q + "\nReason step by step, then give the final answer in \\boxed{}."}]
        try: e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True, enable_thinking=True)
        except TypeError: e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        return e["input_ids"]

    @torch.no_grad()
    def force_stop(q, trace):
        # reconstruct: chat(q) + model's own (truncated) reasoning + commit primer -> fill the box
        base = chat_ids(q)
        cont = tok(trace + PRIMER, add_special_tokens=False, return_tensors="pt")["input_ids"]
        ids = torch.cat([base, cont], 1).to(args.device)
        o = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids),
                           max_new_tokens=32, do_sample=False, pad_token_id=tok.eos_token_id)
        gen = tok.decode(o[0][ids.shape[1]:], skip_special_tokens=True)
        # answer is what fills the box: everything up to the first '}'
        ans = gen.split("}")[0].strip()
        return ans

    results = []
    print(f"\n{'#':>3} {'type':16} {'gold':16} {'BASE':>5} {'FORCE-STOP':>26} {'ok':>3}")
    for p in prompts:
        r = by_q.get(p["question"], {})
        trace = r.get("greedy_trace", "")
        base_ok = bool(r.get("pass1"))
        fs_ans = force_stop(p["question"], trace)
        fs_ok = score(fs_ans, p["gold"], p["source"])
        results.append(dict(idx=p["idx"], type=p["type"], gold=p["gold"], source=p["source"],
                            base_ok=base_ok, base_ans=r.get("greedy_answer","")[:30],
                            forcestop_ans=fs_ans, forcestop_ok=bool(fs_ok)))
        json.dump(results, open(args.out, "w"), indent=1)
        if args.device == "mps": torch.mps.empty_cache()
        print(f"{p['idx']:>3} {p['type']:16} {str(p['gold'])[:16]:16} {str(base_ok):>5} {fs_ans[:24]:>26} {'✓' if fs_ok else '✗':>3}", flush=True)

    # summary
    trunc = [r for r in results if r["type"] == "truncated"]
    gw = [r for r in results if r["type"] == "genuinely_wrong"]
    print(f"\n=== FORCE-STOP rescue rate ===")
    print(f"  truncated (should rescue dithering): {sum(r['forcestop_ok'] for r in trunc)}/{len(trunc)} now correct")
    print(f"  genuinely-wrong (control, should NOT help): {sum(r['forcestop_ok'] for r in gw)}/{len(gw)} now correct")
    print("[done] ->", args.out)

if __name__ == "__main__":
    main()
