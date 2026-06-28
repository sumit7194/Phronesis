#!/usr/bin/env python
"""Qwen3-4B knowledge-edge map — competence × expressed-confidence signals per item.

Follows docs/prereg-knowledge-edge-map.md and docs/EXPERIMENTATION_GUIDELINES.md.
Reuses the 200 hand-scored obscure EntityQuestions (GT correctness already in hand). Adds, per item:
  - k-sampling (k @ T) -> pass@k (competence: is the answer reachable?) + semantic entropy (cluster by meaning)
  - greedy regen with scores -> sequence log-prob + mean predictive entropy
  - verbalized P(True) (Kadavath A/B token-prob self-eval)
All raw saved (every sample, seeds, logits-derived numbers). Auto-correctness is PREFILTER only; hand-read is truth.
Local (Mac MPS). Checkpointed/resumable.
"""
import argparse, json, os, math, unicodedata, re
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFKD", str(s)) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", " ", s.lower()).strip()

def first_line(txt):
    return next((l.strip() for l in txt.split("\n") if l.strip()), "")[:80]

def correct(ans, gold):
    na = norm(ans)
    return bool(na) and any(len(g) >= 3 and g in na for g in gold)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--gt", default="results/legibility/entityq_handscore.json")
    ap.add_argument("--gens", default="results/legibility/entityq_think_Qwen3-4B.json")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--temp", type=float, default=0.7)
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--out", default="results/legibility/knowledge_edge_4b.json")
    ap.add_argument("--device", default="mps")
    args = ap.parse_args()

    gt = {r["q"]: r for r in json.load(open(args.gt))}          # has gold, hand_no_ok (greedy GT)
    gens = json.load(open(args.gens))
    gens = gens["rows"] if isinstance(gens, dict) else gens
    items = []
    for r in gens[:args.n]:
        g = gt.get(r["q"])
        items.append(dict(q=r["q"], entity=r.get("entity"), pop=r.get("pop"),
                          gold=r["gold"], gold_raw=r.get("gold_raw"),
                          greedy_nothink=r.get("nothink", ""),
                          hand_no_ok=(g or {}).get("hand_no_ok")))
    print(f"[data] {len(items)} items; k={args.k} T={args.temp}", flush=True)

    results = []
    if os.path.exists(args.out):
        try: results = json.load(open(args.out))["rows"]
        except Exception: results = []
    start = len(results)
    print(f"[load] {args.model} on {args.device} ({start} resumed) ...", flush=True)
    tok = AutoTokenizer.from_pretrained(args.model)
    dtype = torch.float16 if args.device == "mps" else torch.bfloat16
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype).to(args.device).eval()
    # token ids for A/B P(True) self-eval
    def tid(s):
        ids = tok(s, add_special_tokens=False)["input_ids"]
        return ids[0]
    A_id, B_id = tid("A"), tid("B")
    print("[load] done", flush=True)

    def enc_chat(q, suffix=""):
        m = [{"role": "user", "content": q + " Answer with just the name, as briefly as possible."}]
        try:
            e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt",
                                        return_dict=True, enable_thinking=False)
        except TypeError:
            e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        if suffix:
            sfx = tok(suffix, add_special_tokens=False, return_tensors="pt")
            e = {"input_ids": torch.cat([e["input_ids"], sfx["input_ids"]], 1),
                 "attention_mask": torch.cat([e["attention_mask"], torch.ones_like(sfx["input_ids"])], 1)}
        return {k: v.to(args.device) for k, v in e.items()}

    @torch.no_grad()
    def greedy_with_scores(q):
        enc = enc_chat(q); L = enc["input_ids"].shape[1]
        o = model.generate(**enc, max_new_tokens=24, do_sample=False, pad_token_id=tok.eos_token_id,
                           output_scores=True, return_dict_in_generate=True)
        seq = o.sequences[0][L:]
        ans = first_line(tok.decode(seq, skip_special_tokens=True))
        # sequence logprob (length-normalized) + mean predictive entropy over generated steps
        logps, ents = [], []
        for step, logit in enumerate(o.scores):
            lp = torch.log_softmax(logit[0].float(), -1)
            p = lp.exp()
            ents.append(float(-(p * lp).sum()))
            if step < len(seq):
                logps.append(float(lp[seq[step]]))
        return ans, (float(np.mean(logps)) if logps else 0.0), (float(np.mean(ents)) if ents else 0.0)

    @torch.no_grad()
    def sample_k(q, k):
        enc = enc_chat(q); L = enc["input_ids"].shape[1]
        outs = []
        for s in range(k):
            torch.manual_seed(1000 + s)
            o = model.generate(**enc, max_new_tokens=24, do_sample=True, temperature=args.temp,
                               top_p=args.top_p, pad_token_id=tok.eos_token_id)
            outs.append(first_line(tok.decode(o[0][L:], skip_special_tokens=True)))
        return outs

    @torch.no_grad()
    def p_true(q, proposed):
        prompt = (f"Question: {q}\nProposed answer: {proposed}\nIs the proposed answer correct?\n"
                  f"(A) True\n(B) False\nThe single most likely option is (")
        m = [{"role": "user", "content": prompt}]
        try:
            e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt",
                                        return_dict=True, enable_thinking=False)
        except TypeError:
            e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        e = {k: v.to(args.device) for k, v in e.items()}
        logits = model(**e).logits[0, -1].float()
        pa, pb = logits[A_id].item(), logits[B_id].item()
        m_ = max(pa, pb)
        return math.exp(pa - m_) / (math.exp(pa - m_) + math.exp(pb - m_))   # P(True)

    def semantic_entropy(samples):
        # v1: cluster by normalized-string equality (good proxy for short entity answers; upgrade to NLI later)
        from collections import Counter
        clusters = Counter(norm(s) or "∅" for s in samples)
        tot = sum(clusters.values())
        return float(-sum((c / tot) * math.log(c / tot) for c in clusters.values())), len(clusters)

    for j in range(start, len(items)):
        it = items[j]
        g_ans, seq_lp, ent = greedy_with_scores(it["q"])
        samples = sample_k(it["q"], args.k)
        ptrue = p_true(it["q"], g_ans)
        se, n_clusters = semantic_entropy(samples)
        passk = any(correct(s, it["gold"]) for s in samples)
        results.append(dict(
            q=it["q"], entity=it["entity"], pop=it["pop"], gold_raw=it["gold_raw"], gold=it["gold"],
            hand_no_ok=it["hand_no_ok"],                          # GT correctness (greedy, hand-scored)
            greedy=g_ans, seq_logprob=round(seq_lp, 4), mean_entropy=round(ent, 4),
            p_true=round(ptrue, 4), samples=samples,
            semantic_entropy=round(se, 4), n_clusters=n_clusters,
            auto_greedy_ok=correct(g_ans, it["gold"]), auto_passk=passk,
        ))
        json.dump({"model": args.model, "k": args.k, "temp": args.temp, "rows": results},
                  open(args.out, "w"), indent=1)
        if args.device == "mps": torch.mps.empty_cache()
        if (j + 1) % 5 == 0 or j + 1 == len(items):
            r = results
            ag = np.mean([x["auto_greedy_ok"] for x in r]); pk = np.mean([x["auto_passk"] for x in r])
            print(f"  {j+1}/{len(items)} auto greedy={ag:.2f} pass@k={pk:.2f} "
                  f"(last: P(T)={ptrue:.2f} SE={se:.2f} clu={n_clusters})", flush=True)
    print(f"[done] -> {args.out}", flush=True)

if __name__ == "__main__":
    main()
