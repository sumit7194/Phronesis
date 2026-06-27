#!/usr/bin/env python
"""EntityQuestions thinking-recall on a BIG model (Qwen3-32B, 4-bit) — the F169 scale test.

Identical battery + selection to the 4B run (entityq_thinking.py) so results are apples-to-apples:
same 200 stratified-by-popularity obscure items, same force-close thinking, same raw-save + scoring.
Writes status.json each checkpoint for the live dashboard. Checkpointed/resumable.
"""
import argparse, json, os, re, time, unicodedata
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from datasets import load_dataset

def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFKD", str(s)) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", " ", s.lower()).strip()

def first_line(txt):
    return next((l.strip() for l in txt.split("\n") if l.strip()), "")[:80]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-32B")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--max-new-think", type=int, default=768)
    ap.add_argument("--out", default="entityq_think_32b.json")
    ap.add_argument("--status", default="status.json")
    args = ap.parse_args()
    tag = args.model.split("/")[-1]

    ds = load_dataset("google/granola-entity-questions")["train"]
    rows = [r for r in ds if str(r["question_entity_popularity"]) not in ("None", "", "nan")]
    rows.sort(key=lambda r: float(r["question_entity_popularity"]))
    sel = np.linspace(0, len(rows) - 1, args.n).astype(int)        # IDENTICAL to the 4B run
    rows = [rows[i] for i in sel]
    def golds(r):
        gs = [r["answer"]] + [r.get(f"granola_answer_{i}") for i in range(1, 15)]
        return [norm(g) for g in gs if g and g != "None"]
    items = [dict(q=r["question"], entity=r["question_entity"], pop=float(r["question_entity_popularity"]),
                  gold=golds(r), gold_raw=r["answer"]) for r in rows]

    results = []
    if os.path.exists(args.out):
        try: results = json.load(open(args.out))["rows"]
        except Exception: results = []
    start = len(results)
    print(f"[load] {args.model} 4-bit ... ({start}/{len(items)} resumed)", flush=True)
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, quantization_config=bnb, device_map="cuda").eval()
    close_ids = tok("</think>", add_special_tokens=False)["input_ids"]
    print("[load] done", flush=True)

    def encode(q, thinking):
        m = [{"role": "user", "content": q + " Answer with just the name, as briefly as possible."}]
        try: enc = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True, enable_thinking=thinking)
        except TypeError: enc = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        return {k: v.to("cuda") for k, v in enc.items()}

    def find_close(ids):
        n = len(close_ids)
        for i in range(len(ids) - n, -1, -1):
            if ids[i:i + n] == close_ids: return i + n
        return None

    def gen_nothink(q):
        enc = encode(q, False); L = enc["input_ids"].shape[1]
        with torch.no_grad():
            o = model.generate(**enc, max_new_tokens=32, do_sample=False, pad_token_id=tok.eos_token_id)
        return first_line(tok.decode(o[0][L:], skip_special_tokens=True))

    def gen_think(q, K):
        enc = encode(q, True); L = enc["input_ids"].shape[1]
        with torch.no_grad():
            o1 = model.generate(**enc, max_new_tokens=K, do_sample=False, pad_token_id=tok.eos_token_id)
        ids = o1[0].tolist(); natural = find_close(ids[L:]) is not None
        if not natural: ids = ids + close_ids
        inp = torch.tensor([ids], device="cuda")
        with torch.no_grad():
            o2 = model.generate(input_ids=inp, attention_mask=torch.ones_like(inp), max_new_tokens=40, do_sample=False, pad_token_id=tok.eos_token_id)
        f = o2[0].tolist(); c = find_close(f)
        ans = first_line(tok.decode(f[c:] if c else f[L:], skip_special_tokens=True))
        trace = tok.decode(f[L:c] if c else f[L:], skip_special_tokens=True)[:300]
        return ans, trace, natural

    def correct(ans, gold):
        na = norm(ans)
        return bool(na) and any(len(g) >= 3 and g in na for g in gold)

    def write_status(j, t0):
        no = [r["auto_no_ok"] for r in results]; th = [r["auto_th_ok"] for r in results]
        per = (time.time() - t0) / max(1, j + 1 - start)
        json.dump(dict(model=tag, done=len(results), total=len(items),
                       auto_nothink=round(float(np.mean(no)), 3) if no else 0,
                       auto_think=round(float(np.mean(th)), 3) if th else 0,
                       s_per_item=round(per, 1), eta_h=round(per * (len(items) - j - 1) / 3600, 2),
                       recent=[{"pop": int(r["pop"]), "q": r["q"][:70], "gold": r["gold_raw"],
                                "nothink": r["nothink"], "think": r["think"]} for r in results[-6:]]),
                  open(args.status, "w"), indent=1)

    t0 = time.time()
    for j in range(start, len(items)):
        it = items[j]
        no_ans = gen_nothink(it["q"])
        th_ans, th_trace, fin = gen_think(it["q"], args.max_new_think)
        results.append(dict(entity=it["entity"], q=it["q"], pop=it["pop"], gold_raw=it["gold_raw"], gold=it["gold"],
                            nothink=no_ans, think=th_ans, think_trace=th_trace, think_finished=fin,
                            auto_no_ok=correct(no_ans, it["gold"]), auto_th_ok=correct(th_ans, it["gold"])))
        json.dump({"model": args.model, "rows": results}, open(args.out, "w"), indent=1)
        write_status(j, t0)
        if (j + 1) % 5 == 0 or j + 1 == len(items):
            na = np.mean([r["auto_no_ok"] for r in results]); ta = np.mean([r["auto_th_ok"] for r in results])
            print(f"  {j+1}/{len(items)} auto no={na:.3f} th={ta:.3f} ({(time.time()-t0)/max(1,j+1-start):.0f}s/it)", flush=True)
    print(f"[done] -> {args.out}", flush=True)

if __name__ == "__main__":
    main()
