#!/usr/bin/env python
"""Incubation experiment — Stage 0 screening (docs/idea-workspace-incubation.md v2).

Find edge-of-ability candidates on the 4B: greedy FAILS but pass@k SUCCEEDS (reachable
solution, stuck trajectory — the F187 rumination family). Unlike reasoning_baseline.py this
saves FULL trace text for greedy AND every sample (§6: raw first, parse later), because the
solving-vs-failing trace diff is how we identify the missing MOVE per candidate.

Run (repo root):  mvp/.venv/bin/python mvp/incubation_screen.py
Resumable per item; disk-guarded; status heartbeat.
"""
import argparse, json, os, shutil, sys, time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
from reasoning_baseline import CLOSE, extract_answer, score

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--corpus", default=os.path.join(ROOT, "corpus", "reasoning"))
    ap.add_argument("--sets", default="math500,gsm8k_probe")
    ap.add_argument("--n", type=int, default=40)      # per set
    ap.add_argument("--k", type=int, default=8)       # samples (+1 greedy)
    ap.add_argument("--temp", type=float, default=0.7)
    ap.add_argument("--max-think", type=int, default=2048)
    ap.add_argument("--min-disk-gb", type=float, default=3.0)
    ap.add_argument("--seed", type=int, default=17)
    ap.add_argument("--out", default="results/workspace/incubation_screen.json")
    ap.add_argument("--status", default="results/workspace/status_incubation.json")
    args = ap.parse_args()
    for p in (args.out, args.status):
        os.makedirs(os.path.dirname(p) or ".", exist_ok=True)

    items = []
    for s in args.sets.split(","):
        rows = [json.loads(l) for l in open(os.path.join(args.corpus, f"{s}.jsonl"))]
        for r in rows[:args.n or len(rows)]:
            r["source"] = r.get("source", s.split("_")[0])
            items.append(r)
    print(f"[data] {len(items)} items from {args.sets}", flush=True)

    done_rows = []
    if os.path.exists(args.out):
        done_rows = json.load(open(args.out))["rows"]
    done_ids = {r["qid"] for r in done_rows}

    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=torch.float16).to(args.device).eval()
    torch.manual_seed(args.seed)
    print(f"[load] {args.model} on {args.device}; resume: {len(done_rows)} done", flush=True)

    def gen(q, greedy):
        m = [{"role": "user", "content":
              q + "\nReason step by step, then give the final answer in \\boxed{}."}]
        try:
            e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt",
                                        return_dict=True, enable_thinking=True)
        except TypeError:
            e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt",
                                        return_dict=True)
        enc = e["input_ids"].to(args.device)
        kw = dict(max_new_tokens=args.max_think, pad_token_id=tok.eos_token_id)
        if greedy:
            kw["do_sample"] = False
        else:
            kw.update(do_sample=True, temperature=args.temp, top_p=0.95)
        o = model.generate(input_ids=enc, attention_mask=torch.ones_like(enc), **kw)
        return tok.decode(o[0].tolist()[enc.shape[1]:], skip_special_tokens=True)

    t0 = time.time()
    for i, it in enumerate(items):
        qid = it.get("qid") or it.get("id") or f"{it['source']}-{i}"
        if qid in done_ids:
            continue
        free = shutil.disk_usage("/").free / 2 ** 30
        if free < args.min_disk_gb:
            print(f"[STOP] disk low ({free:.1f} GiB). Resumable.", flush=True)
            break
        q, gold, src = it["question"], str(it.get("gold", it.get("answer"))), it["source"]
        full = gen(q, greedy=True)
        g_ans = extract_answer(full, src)
        row = {"qid": qid, "source": src, "question": q, "gold": gold,
               "greedy_trace": full, "greedy_answer": g_ans,
               "greedy_ok": bool(score(g_ans, gold, src)), "samples": []}
        # Only pay the k-sample cost where it matters: greedy failures are the
        # candidate pool; a few greedy-successes keep a comparison shelf.
        n_samples = args.k if not row["greedy_ok"] else 2
        for s_i in range(n_samples):
            full_s = gen(q, greedy=False)
            a = extract_answer(full_s, src)
            row["samples"].append({"trace": full_s, "answer": a,
                                   "ok": bool(score(a, gold, src))})
        row["passk"] = row["greedy_ok"] or any(s["ok"] for s in row["samples"])
        row["candidate"] = (not row["greedy_ok"]) and any(s["ok"] for s in row["samples"])
        done_rows.append(row)
        json.dump({"rows": done_rows}, open(args.out, "w"))
        n_cand = sum(r.get("candidate") for r in done_rows)
        json.dump({"done": len(done_rows), "total": len(items), "candidates": n_cand,
                   "elapsed_min": round((time.time() - t0) / 60, 1), "free_gb": round(free, 1)},
                  open(args.status, "w"))
        print(f"  [{len(done_rows)}/{len(items)}] {qid:22} greedy={'OK' if row['greedy_ok'] else 'x'} "
              f"passk={'OK' if row['passk'] else 'x'} candidate={row['candidate']} "
              f"(cands so far: {n_cand}, disk {free:.0f}G)", flush=True)
        if args.device == "mps":
            torch.mps.empty_cache()

    n_cand = sum(r.get("candidate") for r in done_rows)
    print(f"[done] {len(done_rows)} screened, {n_cand} candidates -> {args.out}", flush=True)


if __name__ == "__main__":
    main()
