#!/usr/bin/env python
"""E1 fix #1 — full-number-sequence decision variable (de-confounds the leading-digit proxy).

At a uniform sample of positions in each saved trace, score the FULL token sequence of the gold
number vs the wrong number as a continuation (sum of teacher-forced log-probs over the candidate's
tokens, given the local context). margin(p) = logP(" gold") - logP(" wrong"). No single-digit
confound. Within-problem fail-vs-solved delta is the test (cancels any residual per-number bias).

Run:  mvp/.venv/bin/python mvp/e1b_fullnum.py
"""
import argparse, json, os, sys
import torch

sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCREEN = os.path.join(ROOT, "mvp/results/workspace/incubation_screen.json")
OUT = os.path.join(ROOT, "mvp/results/workspace/e1b_fullnum.json")
NPOS, CTX = 40, 256


def seq_logprob_batch(hf, ctxs, cand_ids, chunk=8):
    """For each context, sum logP of cand_ids as continuation. Left-pad; chunked to bound the
    logits tensor (full-vocab logits for 40 long seqs at once = ~7GB → swap; chunk keeps it ~1GB)."""
    out = []
    k = len(cand_ids)
    for c0 in range(0, len(ctxs), chunk):
        seqs = [c + cand_ids for c in ctxs[c0:c0 + chunk]]
        L = max(len(s) for s in seqs)
        inp = torch.zeros((len(seqs), L), dtype=torch.long)
        mask = torch.zeros((len(seqs), L), dtype=torch.long)
        for i, s in enumerate(seqs):
            inp[i, L - len(s):] = torch.tensor(s)
            mask[i, L - len(s):] = 1
        inp, mask = inp.to(DEVICE), mask.to(DEVICE)
        with torch.no_grad():
            logits = hf(inp, attention_mask=mask).logits.float()
        for i in range(len(seqs)):
            start = L - k
            tot = 0.0
            for j in range(k):
                tot += torch.log_softmax(logits[i, start + j - 1], -1)[cand_ids[j]].item()
            out.append(tot)
        del logits
        if DEVICE == "mps":
            torch.mps.empty_cache()
    return out


def analyze(tok, hf, question, trace, gold, wrong):
    msgs = [{"role": "user", "content": question}]
    prefix = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                     enable_thinking=True)
    ids = tok(prefix, add_special_tokens=False)["input_ids"] + \
        tok(trace, add_special_tokens=False)["input_ids"]
    ids = ids[:3200]
    g_ids = tok(" " + str(gold).strip().rstrip("."), add_special_tokens=False)["input_ids"]
    w_ids = tok(" " + str(wrong).strip().rstrip("."), add_special_tokens=False)["input_ids"]
    lo, hi = len(tok(prefix, add_special_tokens=False)["input_ids"]), len(ids)
    if hi - lo < 5:
        return None
    pos = [lo + int((hi - lo - 1) * i / (NPOS - 1)) for i in range(NPOS)]
    ctxs = [ids[max(0, p - CTX):p + 1] for p in pos]
    gs = seq_logprob_batch(hf, ctxs, g_ids)
    ws = seq_logprob_batch(hf, ctxs, w_ids)
    margin = [round(a - b, 3) for a, b in zip(gs, ws)]
    if DEVICE == "mps":
        torch.mps.empty_cache()
    return {"frac_gold_leads": round(sum(m > 0 for m in margin) / len(margin), 3),
            "peak": round(max(margin), 3), "final": round(margin[-1], 3),
            "median": round(sorted(margin)[len(margin) // 2], 3), "margin": margin}


def main():
    rows = [r for r in json.load(open(SCREEN))["rows"]
            if r.get("candidate") and r["qid"].startswith("gsm8k")
            and str(r["greedy_answer"]).strip().rstrip(".").replace(",", "").isdigit()]
    print(f"[load] Qwen3-4B ... ({len(rows)} clean gsm8k candidates)", flush=True)
    tok, hf, _ = load_model()
    results = []
    for i, r in enumerate(rows):
        gold, wrong = str(r["gold"]), str(r["greedy_answer"])
        e = {"qid": r["qid"], "gold": gold, "wrong": wrong, "arms": []}
        arms = [("greedy_fail", r["greedy_trace"], False)]
        arms += [(f"sample{j}_{'ok' if s['ok'] else 'fail'}", s["trace"], s["ok"])
                 for j, s in enumerate(r.get("samples", []))]
        for name, trace, ok in arms:
            a = analyze(tok, hf, r["question"], trace, gold, wrong)
            if a:
                a.update(arm=name, ok=ok)
                e["arms"].append(a)
        results.append(e)
        fg = next(a for a in e["arms"] if a["arm"] == "greedy_fail")
        print(f"[{i+1}/{len(rows)}] {r['qid']:>18} gold={gold:>5} wrong={wrong:>5} | "
              f"FAIL gold_leads={fg['frac_gold_leads']} peak={fg['peak']} final={fg['final']}", flush=True)
        json.dump({"results": results, "npos": NPOS, "ctx": CTX}, open(OUT, "w"))
    print(f"[done] -> {OUT}")


if __name__ == "__main__":
    main()
