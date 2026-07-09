#!/usr/bin/env python
"""No-thinking-cap spiral test: run the 6 curated prompts greedily with a very high token
budget and measure how long each spirals before it commits (emits </think> + an answer) or
hits the cap. Same prompts as the viewer's capped(2048) runs -> direct capped-vs-uncapped
comparison. Saves full traces for later workspace reading.
"""
import json, os, re, sys, time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
from reasoning_baseline import score

DEVICE = "mps"
MAX_NEW = 8192          # 4x the original cap; if it still hits this, the spiral is ~unbounded
OUT = "results/workspace/nocap_traces.json"


def build_prompt(tok, q):
    m = [{"role": "user", "content": q + "\nReason step by step, then give the final answer in \\boxed{}."}]
    try:
        return tok.apply_chat_template(m, add_generation_prompt=True, tokenize=False, enable_thinking=True)
    except TypeError:
        return tok.apply_chat_template(m, add_generation_prompt=True, tokenize=False)


def main():
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-4B")
    hf = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-4B", dtype=torch.float16).to(DEVICE).eval()
    qs = json.load(open("workspace_6q_stimuli.json"))["questions"]
    done = {r["id"]: r for r in json.load(open(OUT))["rows"]} if os.path.exists(OUT) else {}
    rows = list(done.values())
    print(f"[load] MAX_NEW={MAX_NEW}; {len(qs)} prompts, {len(done)} already done", flush=True)

    for q in qs:
        if q["id"] in done:
            continue
        prompt = build_prompt(tok, q["question"])
        ids = tok(prompt, return_tensors="pt")["input_ids"].to(DEVICE)
        t0 = time.time()
        with torch.no_grad():
            o = hf.generate(input_ids=ids, attention_mask=torch.ones_like(ids),
                            max_new_tokens=MAX_NEW, do_sample=False, pad_token_id=tok.eos_token_id)
        gen = o[0][ids.shape[1]:]
        n_new = gen.shape[0]
        trace = tok.decode(gen, skip_special_tokens=True)
        hit_cap = n_new >= MAX_NEW - 2
        committed = ("</think>" in trace) or bool(re.search(r"\\boxed\{[^}]*\}", trace))
        m = re.findall(r"\\boxed\{([^}]*)\}", trace)
        ans = m[-1].strip() if m else ("(committed, no box)" if committed else "(spiraled to cap)")
        ok = bool(score(ans, str(q["gold"]), "gsm8k")) if m else False
        # where did it first reach the gold in text (spiral depth to first-correct)?
        gold = str(q["gold"]).lower()
        first_gold_char = trace.lower().find(gold) if gold != "none" else \
            min([i for i in [trace.lower().find(w) for w in ("no such", "none", "no number")] if i >= 0], default=-1)
        row = {"id": q["id"], "category": q["category"], "gold": q["gold"], "answer": ans,
               "correct": ok, "committed": committed, "hit_cap": hit_cap, "n_new_tokens": n_new,
               "gen_sec": round(time.time() - t0), "first_gold_charpos": first_gold_char,
               "trace_chars": len(trace), "trace": trace}
        rows.append(row)
        json.dump({"rows": rows, "max_new": MAX_NEW}, open(OUT, "w"))
        print(f"  {q['id']:16} tokens={n_new:5} committed={committed} hit_cap={hit_cap} "
              f"ans={ans[:16]!r} ok={ok} ({row['gen_sec']}s)", flush=True)
        if DEVICE == "mps":
            torch.mps.empty_cache()

    print("\n=== SPIRAL SUMMARY (uncapped vs original 2048 cap) ===", flush=True)
    for r in rows:
        mark = "SPIRALED TO CAP" if r["hit_cap"] else ("committed@%d" % r["n_new_tokens"])
        print(f"  {r['id']:16} {mark:18} gold-first-appears@char {r['first_gold_charpos']:5} "
              f"correct={r['correct']}", flush=True)
    print("[done] ->", OUT, flush=True)


if __name__ == "__main__":
    main()
