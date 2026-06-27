#!/usr/bin/env python
"""Behavioral replication of Google's "Thinking to Recall" (docs/prereg-thinking-recall.md, pivot).

Positive control for our methodology: on genuinely OBSCURE single-hop facts (granola-entity-questions,
lowest-popularity entities), does thinking-ON beat thinking-OFF on recall accuracy? If we reproduce
Google's effect, our generation+scoring harness is validated. Gold = answer + all granola granularities
(any correct granularity counts). Checkpointed (resumes after kill/outage).
"""
import argparse, json, os, re, time, unicodedata
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFKD", str(s)) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", " ", s.lower()).strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--n", type=int, default=200, help="N most-obscure items")
    ap.add_argument("--max-new-think", type=int, default=768)
    ap.add_argument("--output-dir", default="results/legibility")
    args = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(here, args.output_dir); os.makedirs(out_dir, exist_ok=True)
    tag = args.model.split("/")[-1]
    json_path = os.path.join(out_dir, f"entityq_think_{tag}.json")

    ds = load_dataset("google/granola-entity-questions")["train"]
    rows = [r for r in ds if str(r["question_entity_popularity"]) not in ("None", "", "nan")]
    rows.sort(key=lambda r: float(r["question_entity_popularity"]))
    sel = np.linspace(0, len(rows) - 1, args.n).astype(int)   # stratified across the popularity range
    rows = [rows[i] for i in sel]
    def golds(r):
        gs = [r["answer"]] + [r.get(f"granola_answer_{i}") for i in range(1, 15)]
        return [norm(g) for g in gs if g and g != "None"]
    items = [dict(q=r["question"], entity=r["question_entity"], pop=float(r["question_entity_popularity"]),
                  rel=r["relation"], gold=golds(r), gold_raw=r["answer"]) for r in rows]

    results = []
    if os.path.exists(json_path):
        try:
            results = json.load(open(json_path))["rows"]
        except Exception:
            results = []
    start = len(results)
    if start:
        print(f"[resume] {start}/{len(items)} done", flush=True)

    dev = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[load] {args.model} on {dev}; {len(items)} obscure items (pop {items[0]['pop']:.0f}–{items[-1]['pop']:.0f}) ...", flush=True)
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float16).to(dev).eval()
    close_ids = tok("</think>", add_special_tokens=False)["input_ids"]

    def find_close(ids):
        n = len(close_ids)
        for i in range(len(ids) - n, -1, -1):
            if ids[i:i + n] == close_ids:
                return i + n
        return None

    def encode(q, thinking):
        msgs = [{"role": "user", "content": q + " Answer with just the name, as briefly as possible."}]
        try:
            enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt",
                                          return_dict=True, enable_thinking=thinking)
        except TypeError:
            enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        return {k: v.to(dev) for k, v in enc.items()}

    def gen_nothink(q):
        enc = encode(q, False); in_len = enc["input_ids"].shape[1]
        with torch.no_grad():
            out = model.generate(**enc, max_new_tokens=32, do_sample=False, pad_token_id=tok.eos_token_id)
        txt = tok.decode(out[0][in_len:], skip_special_tokens=True)
        ans = next((l.strip() for l in txt.split("\n") if l.strip()), "")[:80]
        return ans, txt.strip()[:200]   # (extracted answer, raw text) — raw saved so a parse bug is re-parsable

    def gen_think(q, K):
        # reason up to K tokens; if </think> didn't close, FORCE-close it; then generate the answer
        enc = encode(q, True); in_len = enc["input_ids"].shape[1]
        with torch.no_grad():
            out1 = model.generate(**enc, max_new_tokens=K, do_sample=False, pad_token_id=tok.eos_token_id)
        ids = out1[0].tolist()
        natural = find_close(ids[in_len:]) is not None
        if not natural:
            ids = ids + close_ids                       # force-close the reasoning so an answer must follow
        inp = torch.tensor([ids], device=dev)
        with torch.no_grad():
            out2 = model.generate(input_ids=inp, attention_mask=torch.ones_like(inp),
                                   max_new_tokens=40, do_sample=False, pad_token_id=tok.eos_token_id)
        final = out2[0].tolist(); c = find_close(final)
        ansraw = tok.decode(final[c:] if c else final[in_len:], skip_special_tokens=True)
        trace = tok.decode(final[in_len:c] if c else final[in_len:], skip_special_tokens=True)
        ans = next((l.strip() for l in ansraw.split("\n") if l.strip()), "")[:80]
        return ans, ansraw.strip()[:200], trace.strip(), natural   # answer, raw answer, full reasoning trace

    def correct(ans, gold):
        na = norm(ans)
        return bool(na) and any(len(g) >= 3 and g in na for g in gold)  # answer must contain a gold string

    t0 = time.time()
    for j in range(start, len(items)):
        it = items[j]
        no_ans, no_full = gen_nothink(it["q"])                            # thinking OFF
        th_ans, th_full, th_trace, finished = gen_think(it["q"], args.max_new_think)  # thinking ON (force-closed)
        results.append(dict(entity=it["entity"], q=it["q"], pop=it["pop"], gold_raw=it["gold_raw"], gold=it["gold"],
                            nothink=no_ans, nothink_full=no_full, think=th_ans, think_full=th_full,
                            think_trace=th_trace, think_finished=finished,
                            auto_no_ok=correct(no_ans, it["gold"]), auto_th_ok=correct(th_ans, it["gold"])))  # auto = PREFILTER, not truth
        if (j + 1) % 10 == 0 or j + 1 == len(items):
            json.dump({"model": args.model, "rows": results}, open(json_path, "w"), indent=1)
            na = np.mean([r["auto_no_ok"] for r in results]); ta = np.mean([r["auto_th_ok"] for r in results])
            print(f"  {j+1}/{len(items)}  nothink_acc={na:.3f} think_acc={ta:.3f}  ({(time.time()-t0)/max(1,j+1-start):.1f}s/it)", flush=True)

    no_ok = np.array([r["auto_no_ok"] for r in results]); th_ok = np.array([r["auto_th_ok"] for r in results])
    fin = np.array([r["think_finished"] for r in results])
    print(f"\n=== {tag}: {len(results)} items — AUTO PREFILTER ONLY (hand-read is the real label) ===")
    print(f"  [auto] nothink≈{no_ok.mean():.3f}  think≈{th_ok.mean():.3f}  (Δ≈{th_ok.mean()-no_ok.mean():+.3f})  think_finished={fin.sum()}/{len(fin)}")
    print(f"  raw answers + traces saved -> hand-read scoring pass next. {json_path}")

if __name__ == "__main__":
    main()
