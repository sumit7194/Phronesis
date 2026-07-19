#!/usr/bin/env python
"""Round 1 — connection-gap calibration screen (connect_chains.json).

For each 2-hop chain, ask hop1 (find bridge), hop2 (property of bridge), and the composed query.
A CANDIDATE = model answers hop1 AND hop2 correctly but FAILS the composed query = it KNOWS the
pieces but can't CONNECT them (the substrate for a bridge-injection nudge). Saves full traces
(§6) for hand-verify; auto scoring is a prefilter only. Resumable, disk-guarded.
"""
import json, os, re, shutil, sys, time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

DEVICE, MAX_NEW = "mps", 1024
OUT = "results/workspace/connect_screen.json"


def main():
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-4B")
    hf = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-4B", dtype=torch.float16).to(DEVICE).eval()
    chains = json.load(open(os.path.join(os.path.dirname(__file__), "connect_chains.json")))["chains"]
    rows = json.load(open(OUT))["rows"] if os.path.exists(OUT) else []
    done = {r["id"] for r in rows}
    print(f"[load] {len(chains)} chains, {len(done)} done", flush=True)

    @torch.no_grad()
    def ask(q):
        m = [{"role": "user", "content": q + "\nAnswer concisely."}]
        try:
            e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt",
                                        return_dict=True, enable_thinking=True)
        except TypeError:
            e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        ids = e["input_ids"].to(DEVICE)
        o = hf.generate(input_ids=ids, attention_mask=torch.ones_like(ids), max_new_tokens=MAX_NEW,
                        do_sample=False, pad_token_id=tok.eos_token_id)
        full = tok.decode(o[0][ids.shape[1]:], skip_special_tokens=True)
        ans = full.split("</think>")[-1].strip() if "</think>" in full else full.strip()
        return full, ans

    def hit(ans, expected):
        return any(e.lower() in ans.lower() for e in expected)

    for ch in chains:
        if ch["id"] in done:
            continue
        if shutil.disk_usage("/").free / 2**30 < 3.0:
            print("[STOP] disk low. resumable.", flush=True); break
        t1_full, t1 = ask(ch["hop1_q"]); h1 = hit(t1, ch["hop1_ans"])
        t2_full, t2 = ask(ch["hop2_q"]); h2 = hit(t2, ch["ans"])
        tc_full, tc = ask(ch["composed_q"]); hc = hit(tc, ch["ans"])
        candidate = h1 and h2 and (not hc)
        row = {"id": ch["id"], "diff": ch["diff"], "bridge": ch["bridge"], "gold": ch["ans"],
               "hop1_ok": h1, "hop2_ok": h2, "composed_ok": hc, "candidate": candidate,
               "hop1_ans": t1[:80], "hop2_ans": t2[:80], "composed_ans": tc[:100],
               "composed_trace": tc_full}
        rows.append(row)
        json.dump({"rows": rows}, open(OUT, "w"), indent=1)
        flag = "  <== CANDIDATE (knows pieces, fails to connect)" if candidate else ""
        print(f"  {ch['id']:20} {ch['diff']:16} hop1={h1} hop2={h2} composed={hc}{flag}", flush=True)
        if DEVICE == "mps":
            torch.mps.empty_cache()

    cands = [r for r in rows if r["candidate"]]
    print(f"\n[done] {len(cands)}/{len(rows)} candidates (knows both hops, fails composed):", flush=True)
    for r in cands:
        print(f"  {r['id']:20} bridge={r['bridge']:16} composed_said={r['composed_ans'][:60]!r}", flush=True)


if __name__ == "__main__":
    main()
