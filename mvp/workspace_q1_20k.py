#!/usr/bin/env python
"""Give the one true non-terminator (q1 no-a) a 20k-token budget: does it EVER commit to
'none', or spiral indefinitely? Tracks how many times it 'almost concludes' (says none/no-such
but keeps going) and how high it enumerates."""
import json, os, re, sys, time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

DEVICE = "mps"
MAX_NEW = 20480
QUESTION = ("Is there a positive whole number less than 1000 whose English spelling contains "
            "the letter 'a'? Do not count the word 'and'. If such a number exists, give the "
            "smallest one. If no such number exists, say so.")
OUT = "results/workspace/nocap_q1_20k.json"


def main():
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-4B")
    hf = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-4B", dtype=torch.float16).to(DEVICE).eval()
    m = [{"role": "user", "content": QUESTION + "\nReason step by step, then give the final answer in \\boxed{}."}]
    try:
        prompt = tok.apply_chat_template(m, add_generation_prompt=True, tokenize=False, enable_thinking=True)
    except TypeError:
        prompt = tok.apply_chat_template(m, add_generation_prompt=True, tokenize=False)
    ids = tok(prompt, return_tensors="pt")["input_ids"].to(DEVICE)
    print(f"[load] q1 no-a @ MAX_NEW={MAX_NEW} (~2h). generating...", flush=True)
    t0 = time.time()
    with torch.no_grad():
        o = hf.generate(input_ids=ids, attention_mask=torch.ones_like(ids),
                        max_new_tokens=MAX_NEW, do_sample=False, pad_token_id=tok.eos_token_id)
    gen = o[0][ids.shape[1]:]
    n_new = gen.shape[0]
    trace = tok.decode(gen, skip_special_tokens=True)
    hit_cap = n_new >= MAX_NEW - 2
    committed = ("</think>" in trace) or bool(re.search(r"\\boxed\{[^}]*\}", trace))
    box = re.findall(r"\\boxed\{([^}]*)\}", trace)
    tl = trace.lower()
    almost = sum(tl.count(w) for w in ("no such", "none of", "no number", "there is no", "does not contain", "doesn't contain"))
    highest = max([int(x) for x in re.findall(r"\b(\d{1,3})\b", trace)] or [0])
    row = {"n_new_tokens": n_new, "hit_cap": hit_cap, "committed": committed,
           "answer": box[-1].strip() if box else ("(committed,no box)" if committed else "(spiraled to cap)"),
           "almost_concluded_count": almost, "highest_number_enumerated": highest,
           "gen_sec": round(time.time() - t0), "trace_chars": len(trace), "trace": trace}
    json.dump(row, open(OUT, "w"), indent=1)
    print(f"[done] tokens={n_new} committed={committed} hit_cap={hit_cap} answer={row['answer']!r}", flush=True)
    print(f"  almost-concluded 'none/no-such' {almost}x | enumerated up to {highest} | {row['gen_sec']}s -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
