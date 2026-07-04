#!/usr/bin/env python
"""World-A scan: sort the 4B's failures into rumination-rescuable (World A) vs capability-wall (World B).
For a fresh, UNSEEN batch (easy GSM8K where World A lives + hard MATH level-5 where World B lives):
  1. run BASELINE (its normal reasoning).            baseline OK -> 'solved', skip.
  2. if baseline WRONG, run a GENERIC anti-rumination nudge (no knowledge, no 'it's easy' claim):
       nudge OK  -> World A  (rumination; a loop-break vector has a target here)  <-- test set
       nudge WRONG-> World B  (capability wall; no steering rescues it)
The generic nudge is the prompt-space analog of the anti-rumination vector, so 'World A rate' =
upper bound on what the vector could rescue. Mac/4B. Saves incrementally + status.json for progress.
"""
import argparse, json, os, sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
sys.path.insert(0, os.path.dirname(__file__))
from reasoning_baseline import extract_answer, score, all_boxed

PRIMER  = "\n\n</think>\n\nThe final answer is \\boxed{"
# honest anti-rumination nudge: no injected knowledge, no false 'this is easy' claim
GENERIC = "\n\n(Reminder: don't go in circles or keep second-guessing yourself. Make steady progress toward a concrete answer and commit to it.)"

def build_batch(corpus, n_gsm, n_math):
    gsm = [json.loads(l) for l in open(f"{corpus}/gsm8k_probe.jsonl")]
    math = [json.loads(l) for l in open(f"{corpus}/math500.jsonl")]
    batch = []
    for r in gsm[20:20+n_gsm]:                      # unseen (first 20 were in overnight run)
        batch.append(dict(qid=r["id"], source="gsm8k", question=r["question"], gold=str(r["answer"]), tag="gsm8k"))
    hard = [r for r in math[20:] if r.get("level") == "5"][:n_math]   # unseen, hardest
    for r in hard:
        batch.append(dict(qid=r["id"], source="math500", question=r["question"], gold=str(r["answer"]), tag="math-L5"))
    return batch

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--corpus", default="corpus/reasoning")
    ap.add_argument("--n-gsm", type=int, default=20)
    ap.add_argument("--n-math", type=int, default=12)
    ap.add_argument("--max-think", type=int, default=2048)
    ap.add_argument("--out", default="results/legibility/worldA_scan.json")
    ap.add_argument("--status", default="results/legibility/status_worldA.json")
    args = ap.parse_args()
    for p in (args.out, args.status):
        os.makedirs(os.path.dirname(p) or ".", exist_ok=True)

    batch = build_batch(args.corpus, args.n_gsm, args.n_math)
    # resume: skip qids already scored, restore tally
    out, tally = [], dict(solved=0, worldA=0, worldB=0)
    if os.path.exists(args.out):
        prev = json.load(open(args.out))
        out = prev["rows"]; tally = prev["tally"]
        done_qids = {r["qid"] for r in out}
        batch = [it for it in batch if it["qid"] not in done_qids]
        print(f"[resume] {len(out)} done ({tally}); {len(batch)} remaining", flush=True)
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float16).to(args.device).eval()
    print(f"[load] {args.model}; remaining={len(batch)}", flush=True)

    @torch.no_grad()
    def solve(q):
        m = [{"role": "user", "content": q + "\nReason step by step, then give the final answer in \\boxed{}."}]
        try: e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True, enable_thinking=True)
        except TypeError: e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        ids = e["input_ids"].to(args.device); L = ids.shape[1]
        o = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids), max_new_tokens=args.max_think,
                           do_sample=False, pad_token_id=tok.eos_token_id)
        full = tok.decode(o[0][L:], skip_special_tokens=True)
        used = int(o.shape[1] - L)
        if all_boxed(full):
            return extract_answer(full, "math500"), used
        pr = tok(PRIMER, add_special_tokens=False, return_tensors="pt")["input_ids"].to(args.device)
        ids2 = torch.cat([o[0:1], pr], 1)
        o2 = model.generate(input_ids=ids2, attention_mask=torch.ones_like(ids2), max_new_tokens=32,
                            do_sample=False, pad_token_id=tok.eos_token_id)
        return tok.decode(o2[0][ids2.shape[1]:], skip_special_tokens=True).split("}")[0].strip(), used

    base_n = len(out)
    for i, it in enumerate(batch):
        b_ans, b_used = solve(it["question"]); b_ok = bool(score(b_ans, it["gold"], it["source"]))
        rec = dict(**{k: it[k] for k in ("qid", "source", "tag", "gold")},
                   base_ans=b_ans[:24], base_ok=b_ok, base_tokens=b_used)
        if b_ok:
            rec["world"] = "solved"; tally["solved"] += 1
        else:
            n_ans, _ = solve(it["question"] + GENERIC); n_ok = bool(score(n_ans, it["gold"], it["source"]))
            rec.update(nudge_ans=n_ans[:24], nudge_ok=n_ok)
            rec["world"] = "A" if n_ok else "B"; tally["world" + rec["world"]] += 1
        out.append(rec)
        json.dump(dict(tally=tally, rows=out), open(args.out, "w"), indent=1)
        tot = base_n + len(batch); dn = base_n + i + 1
        json.dump(dict(done=dn, total=tot, current=it["tag"], **tally), open(args.status, "w"), indent=1)
        mark = {"solved": "ok ", "A": "A* ", "B": "B  "}[rec["world"]]
        print(f"  [{dn:2}/{tot}] {it['tag']:8} gold={it['gold'][:10]:10} base={'OK' if b_ok else 'x'}"
              f"{'' if b_ok else ' nudge='+('OK' if rec.get('nudge_ok') else 'x')}  -> {mark}  (tok {b_used})", flush=True)
        if args.device == "mps": torch.mps.empty_cache()

    A = [r for r in out if r["world"] == "A"]
    print(f"\n=== WORLD-A SCAN (n={len(out)}) ===")
    print(f"  solved (baseline OK)      : {tally['solved']}")
    print(f"  World A (nudge RESCUED)    : {tally['worldA']}   <- rumination, vector test set")
    print(f"  World B (capability wall)  : {tally['worldB']}")
    fails = tally['worldA'] + tally['worldB']
    if fails: print(f"  -> of {fails} failures, {tally['worldA']/fails:.0%} are rumination (rescuable by a behavioral nudge)")
    print("  World-A items:", [r["qid"] for r in A])
    print("[done] ->", args.out)

if __name__ == "__main__":
    main()
