#!/usr/bin/env python
"""F189 follow-up: is the overconfident-boundary mode RESCUABLE, and by WHAT? The confidence gate is blind
to boundary errors (P(True)~1.0 on #408/#1193), and the anti-rumination nudge doesn't fix them (F188).
Test a graded nudge on the 12 known failures (7 WRINKLE boundary + 5 HARD capability = specificity control):
  baseline  -> re-confirm wrong
  antirum   -> F187 'stop circling, commit' (should NOT help boundary errors)
  verify    -> generic 'double-check your answer' (does any verification help, or must it be boundary-specific?)
  boundary  -> explicit 'recount off-by-one / thresholds / who-is-included' (the F189 controller's proposed step)
Prediction: boundary > verify > antirum on WRINKLE; and boundary does NOT rescue HARD (capability, not boundary)
-> that specificity is the result. Resumable, disk-guarded (MPS graph-cache fills disk); run via chunk loop."""
import argparse, json, os, shutil, sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
sys.path.insert(0, os.path.dirname(__file__))
from reasoning_baseline import extract_answer, score, all_boxed

PRIMER = "\n\n</think>\n\nThe final answer is \\boxed{"
NUDGES = {
    "baseline": "",
    "antirum":  "\n\n(Reminder: don't go in circles or keep second-guessing yourself. Make steady progress toward a concrete answer and commit to it.)",
    "verify":   "\n\n(Before you commit, double-check your answer carefully.)",
    "boundary": "\n\n(Before you commit, explicitly re-check any boundary in this problem: off-by-one / fencepost counting, "
                "strict vs inclusive thresholds like 'more than' vs 'at least' vs 'exactly', and precisely which people or "
                "items are included in what the question asks. Recount that step, then commit.)",
    # PLACEBO CONTROL: neutral parenthetical, same position/length, ZERO reasoning/metacognitive guidance.
    # If this rescues ~as many as the real nudges -> rescue is greedy-trajectory PERTURBATION of low-confidence
    # errors, not nudge content (and boundary/verify/antirum "working" is an illusion).
    "placebo":  "\n\n(Note: this is question 7 of today's problem set. The current season is autumn.)",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--targets", default="results/legibility/boundary_targets.json")
    ap.add_argument("--pool", default="results/legibility/wrinkle_pool_full.json")
    ap.add_argument("--max-think", type=int, default=2048)
    ap.add_argument("--min-disk-gb", type=float, default=3.0)
    ap.add_argument("--out", default="results/legibility/boundary_rescue.json")
    ap.add_argument("--status", default="results/legibility/status_boundary.json")
    args = ap.parse_args()
    for p in (args.out, args.status): os.makedirs(os.path.dirname(p) or ".", exist_ok=True)

    tgt = json.load(open(args.targets)); pool = {r["qid"]: r for r in json.load(open(args.pool))}
    jobs = []
    for group, qids in tgt.items():
        for q in qids:
            for cond in NUDGES:
                jobs.append((q, group, cond))
    out = []
    if os.path.exists(args.out):
        out = json.load(open(args.out))["rows"]; done = {(r["qid"], r["cond"]) for r in out}
        jobs = [j for j in jobs if (j[0], j[2]) not in done]
        print(f"[resume] {len(out)} done; {len(jobs)} remaining", flush=True)

    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float16).to(args.device).eval()
    print(f"[load] {args.model}; remaining={len(jobs)}", flush=True)

    @torch.no_grad()
    def solve(q):
        m = [{"role": "user", "content": q + "\nReason step by step, then give the final answer in \\boxed{}."}]
        try: e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True, enable_thinking=True)
        except TypeError: e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        ids = e["input_ids"].to(args.device); L = ids.shape[1]
        o = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids), max_new_tokens=args.max_think,
                           do_sample=False, pad_token_id=tok.eos_token_id)
        full = tok.decode(o[0][L:], skip_special_tokens=True)
        if all_boxed(full): return extract_answer(full, "math500")
        pr = tok(PRIMER, add_special_tokens=False, return_tensors="pt")["input_ids"].to(args.device)
        ids2 = torch.cat([o[0:1], pr], 1)
        o2 = model.generate(input_ids=ids2, attention_mask=torch.ones_like(ids2), max_new_tokens=32,
                            do_sample=False, pad_token_id=tok.eos_token_id)
        return tok.decode(o2[0][ids2.shape[1]:], skip_special_tokens=True).split("}")[0].strip()

    tot = len(out) + len(jobs)
    for i, (qid, group, cond) in enumerate(jobs):
        free = shutil.disk_usage("/").free / 2**30
        if free < args.min_disk_gb:
            print(f"[STOP] disk low ({free:.1f} GiB); saved {len(out)}. Resumable.", flush=True); break
        gold = pool[qid]["gold"]
        ans = solve(pool[qid]["question"] + NUDGES[cond]); ok = bool(score(ans, gold, "gsm8k"))
        out.append(dict(qid=qid, group=group, cond=cond, gold=gold, ans=ans[:24], ok=ok))
        json.dump(dict(rows=out), open(args.out, "w"), indent=1)
        json.dump(dict(done=len(out), total=tot, free_gb=round(free, 1)), open(args.status, "w"))
        print(f"  [{len(out):3}/{tot}] {group:7} {qid:16} {cond:9} -> {'OK' if ok else 'x '} (disk {free:.1f}G)", flush=True)
        if args.device == "mps": torch.mps.empty_cache()

    # ---- verdict: rescue rate per condition, per group ----
    if len(out) >= tot:
        from collections import defaultdict
        by = defaultdict(dict)
        for r in out: by[r["qid"]][r["cond"]] = r["ok"]
        groups = {}
        for r in out: groups[r["qid"]] = r["group"]
        print("\n=== BOUNDARY-RESCUE VERDICT (rescued = became correct under the nudge) ===")
        for g in ("WRINKLE", "HARD"):
            qs = [q for q in by if groups[q] == g]
            print(f"  {g} (n={len(qs)} failures):")
            for cond in NUDGES:
                resc = sum(1 for q in qs if by[q].get(cond))
                print(f"    {cond:9}: {resc}/{len(qs)} correct")
        print("  -> boundary-specific rescue iff boundary>verify>antirum on WRINKLE AND boundary~0 on HARD")
    print("[done] ->", args.out)

if __name__ == "__main__":
    main()
