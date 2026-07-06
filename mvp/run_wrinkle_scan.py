#!/usr/bin/env python
"""Option A (prereg docs/prereg-wrinkle-scan-2026-07.md): does the 'wrinkle' property enrich World-A
(rumination) failures vs a PLAIN control? Consumes a blind-labeled test set (wrinkle_labels.json +
wrinkle_pool.json), runs identical baseline+generic-nudge pipeline as scan_worldA.py, and compares
World-A rate between WRINKLE and PLAIN. Resumable; status.json for progress.
"""
import argparse, json, os, sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
sys.path.insert(0, os.path.dirname(__file__))
from reasoning_baseline import extract_answer, score, all_boxed

PRIMER  = "\n\n</think>\n\nThe final answer is \\boxed{"
GENERIC = "\n\n(Reminder: don't go in circles or keep second-guessing yourself. Make steady progress toward a concrete answer and commit to it.)"

def build_set(adjudicated_f, labels_f, pool_f, n_wrinkle, n_plain, seed=7):
    import random
    adj = {r["qid"]: r for r in json.load(open(adjudicated_f))}
    labels = {r["qid"]: r for r in json.load(open(labels_f))}
    pool = {r["qid"]: r for r in json.load(open(pool_f))}
    wr = [q for q, r in adj.items() if r["verdict"] == "STRONG"][:n_wrinkle]  # adjudicated STRONG only
    pl_all = [q for q, r in labels.items() if r["label"] == "PLAIN"]
    rng = random.Random(seed)
    pl = rng.sample(pl_all, min(n_plain, len(pl_all)))
    out = []
    for q in wr: out.append(dict(**pool[q], group="WRINKLE", type=adj[q].get("type")))
    for q in pl: out.append(dict(**pool[q], group="PLAIN", type=None))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--adjudicated", default="results/legibility/wrinkle_adjudicated.json")
    ap.add_argument("--labels", default="results/legibility/wrinkle_labels_full.json")
    ap.add_argument("--pool", default="results/legibility/wrinkle_pool_full.json")
    ap.add_argument("--n-wrinkle", type=int, default=30)
    ap.add_argument("--n-plain", type=int, default=25)
    ap.add_argument("--max-think", type=int, default=2048)
    ap.add_argument("--out", default="results/legibility/wrinkle_scan.json")
    ap.add_argument("--status", default="results/legibility/status_wrinkle.json")
    args = ap.parse_args()
    for p in (args.out, args.status):
        os.makedirs(os.path.dirname(p) or ".", exist_ok=True)

    testset = build_set(args.adjudicated, args.labels, args.pool, args.n_wrinkle, args.n_plain)
    out, tally = [], {g: dict(n=0, solved=0, A=0, B=0) for g in ("WRINKLE", "PLAIN")}
    if os.path.exists(args.out):
        prev = json.load(open(args.out)); out = prev["rows"]; tally = prev["tally"]
        done = {r["qid"] for r in out}
        testset = [it for it in testset if it["qid"] not in done]
        print(f"[resume] {len(out)} done; {len(testset)} remaining", flush=True)

    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float16).to(args.device).eval()
    print(f"[load] {args.model}; remaining={len(testset)}", flush=True)

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
        pr = tok(PRIMER, add_special_tokens=False, return_tensors="pt")["input_ids"].to(args.device)
        ids2 = torch.cat([o[0:1], pr], 1)
        o2 = model.generate(input_ids=ids2, attention_mask=torch.ones_like(ids2), max_new_tokens=32,
                            do_sample=False, pad_token_id=tok.eos_token_id)
        return tok.decode(o2[0][ids2.shape[1]:], skip_special_tokens=True).split("}")[0].strip()

    base_n = len(out); tot = base_n + len(testset)
    for i, it in enumerate(testset):
        g = it["group"]
        b_ans = solve(it["question"]); b_ok = bool(score(b_ans, it["gold"], "gsm8k"))
        rec = dict(qid=it["qid"], group=g, type=it.get("type"), gold=it["gold"], base_ans=b_ans[:24], base_ok=b_ok)
        tally[g]["n"] += 1
        if b_ok:
            rec["world"] = "solved"; tally[g]["solved"] += 1
        else:
            n_ans = solve(it["question"] + GENERIC); n_ok = bool(score(n_ans, it["gold"], "gsm8k"))
            rec.update(nudge_ans=n_ans[:24], nudge_ok=n_ok)
            rec["world"] = "A" if n_ok else "B"; tally[g][rec["world"]] += 1
        out.append(rec)
        json.dump(dict(tally=tally, rows=out), open(args.out, "w"), indent=1)
        json.dump(dict(done=base_n+i+1, total=tot, current=g, tally=tally), open(args.status, "w"), indent=1)
        mark = {"solved": "ok", "A": "A*", "B": "B "}[rec["world"]]
        print(f"  [{base_n+i+1:2}/{tot}] {g:7} gold={it['gold'][:8]:8} base={'OK' if b_ok else 'x'}"
              f"{'' if b_ok else ' nudge='+('OK' if rec.get('nudge_ok') else 'x')} -> {mark}", flush=True)
        if args.device == "mps": torch.mps.empty_cache()

    print(f"\n=== WRINKLE-SCAN VERDICT ===")
    for g in ("WRINKLE", "PLAIN"):
        t = tally[g]; fails = t["A"] + t["B"]
        rate = t["A"] / t["n"] if t["n"] else 0
        arate = t["A"] / fails if fails else 0
        print(f"  {g:7}: n={t['n']:2}  solved={t['solved']:2}  World-A={t['A']}  World-B={t['B']}  "
              f"| World-A rate={rate:.0%} of all, {arate:.0%} of failures")
    wa = tally["WRINKLE"]["A"] / max(1, tally["WRINKLE"]["n"])
    pa = tally["PLAIN"]["A"] / max(1, tally["PLAIN"]["n"])
    print(f"  -> WRINKLE World-A {wa:.0%} vs PLAIN {pa:.0%} vs ~3% background")
    print(f"  -> {'ENRICHED (signature holds, pending hand-read)' if wa > pa and tally['WRINKLE']['A']>=2 else 'NOT enriched / underpowered (see prereg falsification)'}")
    print("  World-A items:", [r["qid"] for r in out if r["world"]=="A"])
    print("[done] ->", args.out)

if __name__ == "__main__":
    main()
