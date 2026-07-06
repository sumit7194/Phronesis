#!/usr/bin/env python
"""Overnight (F188 follow-up): is Qwen3-4B CALIBRATED on math reasoning — does its confidence predict
its own correctness — and is it specifically OVERCONFIDENT at boundaries (the 'confidently-wrong-at-a-
boundary' third mode)? Difficulty-stratified over our labeled GSM8K (PLAIN / WRINKLE / HARD).

Per problem: (1) solve with thinking (force-commit on truncation) -> correct/wrong;
             (2) P(True): a Yes/No probe read from logits (F178's surviving signal);
             (3) verbalized confidence: model states a 0-100% (F178 found this does NOT survive -> compare).
Analysis: AUROC(confidence -> correctness) + mean-conf(correct vs wrong) + ECE, overall and per stratum.
Prediction (F188): confidence is high even on WRONG boundary answers -> low AUROC / high wrong-conf on WRINKLE.
Robust for unattended run: resumable (skips scored qids), incremental save + status.json, disk-guard (stops
gracefully if free space < 2 GiB so an MPS-scratch disk-fill can't corrupt the night)."""
import argparse, json, os, re, shutil, sys
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
sys.path.insert(0, os.path.dirname(__file__))
from reasoning_baseline import extract_answer, score, all_boxed

PRIMER = "\n\n</think>\n\nThe final answer is \\boxed{"

def build_set(labels_f, pool_f, ns, seed=11):
    import random
    labels = json.load(open(labels_f)); pool = {r["qid"]: r for r in json.load(open(pool_f))}
    byl = {"PLAIN": [], "WRINKLE": [], "HARD": []}
    for r in labels:
        if r["label"] in byl and r["qid"] in pool: byl[r["label"]].append(r["qid"])
    rng = random.Random(seed); out = []
    for lab, n in ns.items():
        for q in rng.sample(byl[lab], min(n, len(byl[lab]))):
            out.append(dict(**pool[q], group=lab))
    return out

def auroc(scores, labels):  # AUROC of score predicting correct (Mann-Whitney, tie-averaged ranks)
    s = np.asarray(scores, float); y = np.asarray(labels, int)
    npos, nneg = int((y == 1).sum()), int((y == 0).sum())
    if npos == 0 or nneg == 0 or len(s) == 0: return float("nan")
    order = np.argsort(s, kind="mergesort"); ranks = np.empty(len(s), float)
    ranks[order] = np.arange(1, len(s) + 1)
    # average ranks within tied score groups
    u, inv = np.unique(s, return_inverse=True)
    for g in range(len(u)):
        idx = np.where(inv == g)[0]
        if len(idx) > 1: ranks[idx] = ranks[idx].mean()
    R = ranks[y == 1].sum()
    return (R - npos * (npos + 1) / 2) / (npos * nneg)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--labels", default="results/legibility/wrinkle_labels_full.json")
    ap.add_argument("--pool", default="results/legibility/wrinkle_pool_full.json")
    ap.add_argument("--n-plain", type=int, default=45)
    ap.add_argument("--n-wrinkle", type=int, default=68)
    ap.add_argument("--n-hard", type=int, default=45)
    ap.add_argument("--max-think", type=int, default=2048)
    ap.add_argument("--min-disk-gb", type=float, default=2.0)
    ap.add_argument("--out", default="results/legibility/confidence_calib.json")
    ap.add_argument("--status", default="results/legibility/status_calib.json")
    args = ap.parse_args()
    for p in (args.out, args.status): os.makedirs(os.path.dirname(p) or ".", exist_ok=True)

    testset = build_set(args.labels, args.pool, {"PLAIN": args.n_plain, "WRINKLE": args.n_wrinkle, "HARD": args.n_hard})
    out = []
    if os.path.exists(args.out):
        out = json.load(open(args.out))["rows"]; done = {r["qid"] for r in out}
        testset = [it for it in testset if it["qid"] not in done]
        print(f"[resume] {len(out)} done; {len(testset)} remaining", flush=True)

    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float16).to(args.device).eval()
    print(f"[load] {args.model}; remaining={len(testset)}", flush=True)

    def tok_ids(words):
        s = set()
        for w in words:
            for v in (w, " " + w):
                t = tok(v, add_special_tokens=False)["input_ids"]
                if len(t) == 1: s.add(t[0])
        return list(s)
    YES, NO = tok_ids(["Yes", "yes", "YES"]), tok_ids(["No", "no", "NO"])

    def chat(content, thinking):
        m = [{"role": "user", "content": content}]
        try: e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True, enable_thinking=thinking)
        except TypeError: e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        return e["input_ids"].to(args.device)

    @torch.no_grad()
    def solve(q):
        ids = chat(q + "\nReason step by step, then give the final answer in \\boxed{}.", True); L = ids.shape[1]
        o = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids), max_new_tokens=args.max_think,
                           do_sample=False, pad_token_id=tok.eos_token_id)
        full = tok.decode(o[0][L:], skip_special_tokens=True); used = int(o.shape[1] - L)
        if all_boxed(full): return extract_answer(full, "math500"), used
        pr = tok(PRIMER, add_special_tokens=False, return_tensors="pt")["input_ids"].to(args.device)
        ids2 = torch.cat([o[0:1], pr], 1)
        o2 = model.generate(input_ids=ids2, attention_mask=torch.ones_like(ids2), max_new_tokens=32,
                            do_sample=False, pad_token_id=tok.eos_token_id)
        return tok.decode(o2[0][ids2.shape[1]:], skip_special_tokens=True).split("}")[0].strip(), used

    @torch.no_grad()
    def p_true(q, ans):
        ids = chat(f"Question: {q}\n\nProposed answer: {ans}\n\nIs the proposed answer correct? "
                   f"Respond with only 'Yes' or 'No'.", False)
        lg = model(input_ids=ids).logits[0, -1].float()
        p = torch.softmax(lg, -1)
        py = float(p[YES].sum()); pn = float(p[NO].sum())
        return py / (py + pn + 1e-9)

    @torch.no_grad()
    def verbalized(q, ans):
        ids = chat(f"Question: {q}\n\nProposed answer: {ans}\n\nHow confident are you (0-100%) that the "
                   f"proposed answer is correct? Respond with just a percentage.", False)
        o = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids), max_new_tokens=12,
                           do_sample=False, pad_token_id=tok.eos_token_id)
        txt = tok.decode(o[0][ids.shape[1]:], skip_special_tokens=True)
        m = re.search(r"(\d{1,3}(?:\.\d+)?)\s*%", txt) or re.search(r"\b(\d{1,3}(?:\.\d+)?)\b", txt)
        return (min(float(m.group(1)), 100.0) / 100.0) if m else None

    tot = len(out) + len(testset)
    for i, it in enumerate(testset):
        free_gb = shutil.disk_usage("/").free / 2**30
        if free_gb < args.min_disk_gb:
            print(f"[STOP] disk low ({free_gb:.1f} GiB free < {args.min_disk_gb}); saved {len(out)}. Resumable.", flush=True)
            break
        q, gold = it["question"], it["gold"]
        ans, used = solve(q); ok = bool(score(ans, gold, "gsm8k"))
        pt = p_true(q, ans); vc = verbalized(q, ans)
        out.append(dict(qid=it["qid"], group=it["group"], gold=gold, ans=ans[:24],
                        correct=ok, p_true=round(pt, 4), vconf=(round(vc, 4) if vc is not None else None), tokens=used))
        json.dump(dict(rows=out), open(args.out, "w"), indent=1)
        json.dump(dict(done=len(out), total=tot, group=it["group"], free_gb=round(free_gb, 1)), open(args.status, "w"))
        print(f"  [{len(out):3}/{tot}] {it['group']:7} {'OK ' if ok else 'ERR'} pT={pt:.2f} "
              f"vc={vc if vc is None else round(vc,2)} (tok {used}, disk {free_gb:.1f}G)", flush=True)
        if args.device == "mps": torch.mps.empty_cache()

    # ---- analysis ----
    def report(rows, name):
        if not rows: return
        y = [r["correct"] for r in rows]; acc = np.mean(y)
        pt = [r["p_true"] for r in rows]; vc = [r["vconf"] for r in rows if r["vconf"] is not None]
        vy = [r["correct"] for r in rows if r["vconf"] is not None]
        ptc = np.mean([r["p_true"] for r in rows if r["correct"]]) if any(y) else float("nan")
        ptw = np.mean([r["p_true"] for r in rows if not r["correct"]]) if not all(y) else float("nan")
        print(f"  {name:9} n={len(rows):3} acc={acc:.0%} | P(True) AUROC={auroc(pt,y):.2f}  "
              f"mean(correct)={ptc:.2f} mean(WRONG)={ptw:.2f}  | vconf AUROC={auroc(vc,vy):.2f}", flush=True)

    print("\n=== CONFIDENCE-CALIBRATION VERDICT ===")
    print("  (overconfident-boundary => WRINKLE wrong-answers keep HIGH P(True), AUROC drops)")
    report(out, "ALL")
    for g in ("PLAIN", "WRINKLE", "HARD"):
        report([r for r in out if r["group"] == g], g)
    print("[done] ->", args.out)

if __name__ == "__main__":
    main()
