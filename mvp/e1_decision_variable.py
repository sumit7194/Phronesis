#!/usr/bin/env python
"""E1 (decision-variable trajectory) + E2 (self-surprise) — prereg-lens-info-2026-07.md.

Retrospective, no generation. Teacher-force each saved candidate trace (the failing greedy
trace AND its samples) through Qwen3-4B; from ONE forward pass per trace read:
  E1: margin(t) = lens_logit(gold_first_tok) - lens_logit(wrong_first_tok) across the trace
      -> #lead-changes, longest run, frac gold leads, peak/final. Output-layer AND L20.
  E2: surprise(t) = -log P(actual_next | ctx) and rank of the actual next token.
Text baselines (F-A / F-B) computed on the same trace text: repeated-candidate count, doubt-load.

Run (repo root):  mvp/.venv/bin/python mvp/e1_decision_variable.py --limit 3   # smoke
                  mvp/.venv/bin/python mvp/e1_decision_variable.py             # full 19
"""
import argparse, json, math, os, re, sys
import torch

sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCREEN = os.path.join(ROOT, "mvp/results/workspace/incubation_screen.json")
OUT = os.path.join(ROOT, "mvp/results/workspace/e1_decision_variable.json")
L_WS = 20
DOUBT = [" maybe", " but", " actually", " wait", " hmm", " alternatively", " again",
         " perhaps", " however", " though"]


def first_tok_id(tok, s):
    """First CONTENT token of the number (digits tokenize as [space, d, d]; skip the space)."""
    s = s.strip().rstrip(".").strip()
    ids = tok(s, add_special_tokens=False)["input_ids"]      # no leading space
    return ids[0] if ids else None


def runs_and_flips(sign_series):
    """#sign-changes and longest same-sign run over a +-1 series (0 ignored)."""
    s = [x for x in sign_series if x != 0]
    if not s:
        return 0, 0
    flips = sum(1 for a, b in zip(s, s[1:]) if a != b)
    longest = cur = 1
    for a, b in zip(s, s[1:]):
        cur = cur + 1 if a == b else 1
        longest = max(longest, cur)
    return flips, longest


def analyze_trace(tok, hf, lens, question, trace, gold, wrong, max_len=3200):
    msgs = [{"role": "user", "content": question}]
    prefix = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                     enable_thinking=True)
    pre_ids = tok(prefix, add_special_tokens=False)["input_ids"]
    tr_ids = tok(trace, add_special_tokens=False)["input_ids"]
    ids = (pre_ids + tr_ids)[:max_len]
    t0 = min(len(pre_ids), len(ids) - 1)           # first trace position
    inp = torch.tensor([ids], device=DEVICE)
    with torch.no_grad():
        out = hf(inp, output_hidden_states=True)
    logits = out.logits[0].float()                 # [T, V] output-layer next-token
    h20 = out.hidden_states[L_WS][0]               # [T, d]
    ws_logits = lens.unembed(h20).float()          # [T, V] L20 logit-lens

    gtok, wtok = first_tok_id(tok, gold), first_tok_id(tok, wrong)
    series = {"out": [], "ws": []}
    surprise, ranks = [], []
    for t in range(t0, len(ids) - 1):
        nxt = ids[t + 1]
        lp = torch.log_softmax(logits[t], -1)
        surprise.append(round(-lp[nxt].item(), 3))
        ranks.append(int((logits[t] > logits[t][nxt]).sum().item()))
        if gtok is not None and wtok is not None:
            series["out"].append(round((logits[t][gtok] - logits[t][wtok]).item(), 3))
            series["ws"].append(round((ws_logits[t][gtok] - ws_logits[t][wtok]).item(), 3))
    del out, logits, h20, ws_logits
    if DEVICE == "mps":
        torch.mps.empty_cache()

    res = {"n_pos": len(surprise), "gtok": gtok, "wtok": wtok,
           "surprise_med": round(sorted(surprise)[len(surprise) // 2], 3) if surprise else None,
           "surprise_max": max(surprise) if surprise else None,
           "self_correct_rate": round(sum(r > 0 for r in ranks) / len(ranks), 3) if ranks else None,
           "surprise_series": surprise, "rank_series": ranks}
    for k, m in series.items():
        if m:
            flips, longest = runs_and_flips([1 if x > 0 else -1 if x < 0 else 0 for x in m])
            res[f"{k}_flips"] = flips
            res[f"{k}_longest_run"] = longest
            res[f"{k}_frac_gold_leads"] = round(sum(x > 0 for x in m) / len(m), 3)
            res[f"{k}_peak"] = round(max(m), 3)
            res[f"{k}_final"] = round(m[-1], 3)
            res[f"{k}_series"] = m
    return res


def text_baselines(trace, gold, wrong):
    def count(s):
        return len(re.findall(r"(?<!\d)" + re.escape(s.strip().rstrip(".")) + r"(?!\d)", trace))
    return {"txt_gold_count": count(gold), "txt_wrong_count": count(wrong),
            "txt_doubt": sum(trace.lower().count(d.strip()) for d in DOUBT)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    rows = [r for r in json.load(open(SCREEN))["rows"] if r.get("candidate")]
    if args.limit:
        rows = rows[:args.limit]
    print(f"[load] Qwen3-4B ... ({len(rows)} candidates)", flush=True)
    tok, hf, lens = load_model()
    results = []
    for i, r in enumerate(rows):
        gold, wrong = str(r["gold"]), str(r["greedy_answer"])
        entry = {"qid": r["qid"], "gold": gold, "greedy_answer": wrong,
                 "question": r["question"][:200], "arms": []}
        arms = [("greedy_fail", r["greedy_trace"], False)]
        for j, s in enumerate(r.get("samples", [])):
            arms.append((f"sample{j}_{'ok' if s['ok'] else 'fail'}", s["trace"], s["ok"]))
        for name, trace, ok in arms:
            a = analyze_trace(tok, hf, lens, r["question"], trace, gold, wrong)
            a.update(text_baselines(trace, gold, wrong))
            a["arm"], a["ok"] = name, ok
            entry["arms"].append(a)
        results.append(entry)
        g = next(a for a in entry["arms"] if a["arm"] == "greedy_fail")
        print(f"[{i+1}/{len(rows)}] {r['qid']:>18} gold={gold:>5} wrong={wrong:>5} "
              f"| FAIL out_flips={g.get('out_flips','?')} gold_leads={g.get('out_frac_gold_leads','?')} "
              f"txt_gold×{g['txt_gold_count']} txt_wrong×{g['txt_wrong_count']}", flush=True)
        json.dump({"results": results}, open(OUT, "w"))
    print(f"[done] -> {OUT}")


if __name__ == "__main__":
    main()
