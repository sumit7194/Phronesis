#!/usr/bin/env python
"""Phase-1 reasoning baseline harness (roadmap-2026-07 §3). Thinking-mode generation on the
frozen benchmark sets, robust math scoring, FULL trace saving (F177 lesson), difficulty map +
overthinking measurement. Reusable Mac (4B fp16/mps) or VM (7B/8B fp16/cuda, or --quant 1).

Per item saves: greedy + k samples, each with FULL thinking trace and extracted answer, scored.
Computes pass@1 (greedy), pass@k, trace length, overthinking-marker counts, and the
"right-answer-in-trace-but-not-emitted" flag (Lotfi 2606.00206 signature, our recall/reasoning setup).
"""
import argparse, json, os, re, time
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

OVERTHINK = ["wait", "but ", "alternatively", "hmm", "perhaps", "maybe", "let me reconsider",
             "on second thought", "actually", "hold on", "let me re-"]
CLOSE = "</think>"

def extract_boxed(t):
    i = t.rfind(r"\boxed")
    if i < 0: return None
    j = t.find("{", i)
    if j < 0: return None
    depth, k = 0, j
    while k < len(t):
        if t[k] == "{": depth += 1
        elif t[k] == "}":
            depth -= 1
            if depth == 0: return t[j+1:k]
        k += 1
    return None

def all_boxed(t):
    out, i = [], 0
    while True:
        i = t.find(r"\boxed", i)
        if i < 0: break
        j = t.find("{", i)
        if j < 0: break
        depth, k = 0, j
        while k < len(t):
            if t[k] == "{": depth += 1
            elif t[k] == "}":
                depth -= 1
                if depth == 0:
                    out.append(t[j+1:k]); break
            k += 1
        i = k + 1
    return out

def extract_answer(text, source):
    """Pull the final answer from the post-think output."""
    b = extract_boxed(text)
    if b is not None: return b.strip()
    if source == "gpqa_diamond":
        m = re.findall(r"\b([A-D])\b", text)
        return m[-1] if m else text.strip()[:40]
    if source in ("gsm8k", "aime"):
        nums = re.findall(r"-?\d[\d,]*\.?\d*", text.replace(",", ""))
        return nums[-1] if nums else text.strip()[:40]
    # math500: last non-empty line
    return next((l.strip() for l in reversed(text.split("\n")) if l.strip()), text.strip())[:120]

def score(pred, gold, source):
    if source == "gpqa_diamond":
        return pred.strip().upper()[:1] == gold.strip().upper()[:1]
    if source in ("gsm8k", "aime"):
        def _num(s):
            s = str(s).strip()
            m = re.fullmatch(r"(\d{1,2}):(\d{2})\s*([ap]\.?m\.?)?", s, re.I)  # time-of-day "2:00" -> 2.0 hours
            if m: return int(m.group(1)) + int(m.group(2)) / 60.0
            return float(re.sub(r"[^\d.\-]", "", s))
        try: return abs(_num(pred) - _num(gold)) < 1e-4
        except Exception: return pred.strip() == gold.strip()
    # math500 / competition: math_verify, then a whitespace/delimiter-normalized string fallback
    # (math_verify is reliable on scalars/fractions but breaks on tuples/intervals/sets — validated 2026-07-02)
    try:
        from math_verify import parse, verify
        if verify(parse(gold), parse(pred)): return True
    except Exception:
        pass
    def sn(s):
        s = str(s)
        s = re.sub(r"\\text\s*\{([^{}]*)\}", r"\1", s)          # \text{Evelyn} -> Evelyn
        s = re.sub(r"\\mathrm\s*\{([^{}]*)\}", r"\1", s)
        s = s.replace(r"\pi", "π").replace(r"\Pi", "π")           # \pi <-> π
        s = re.sub(r"\^?\s*\\?circ", "", s).replace("°", "")     # ^\circ / degree
        s = re.sub(r"\\(left|right|!|,|;|quad|qquad|\$)", "", s)
        s = re.sub(r"\s+", "", s).replace(r"\dfrac", r"\frac")
        return s.strip().rstrip(".").strip("$").lower()
    return bool(sn(gold)) and sn(gold) == sn(pred)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--quant", type=int, default=0)
    ap.add_argument("--sets", default="gsm8k_probe,math500,aime_2021_2024")
    ap.add_argument("--n", type=int, default=10)          # per set (0=all)
    ap.add_argument("--k", type=int, default=3)           # samples (+1 greedy)
    ap.add_argument("--max-think", type=int, default=2048)
    ap.add_argument("--max-answer", type=int, default=120)
    ap.add_argument("--temp", type=float, default=0.7)
    ap.add_argument("--corpus", default="corpus/reasoning")
    ap.add_argument("--out", default="results/legibility/reasoning_baseline_4b.json")
    ap.add_argument("--status", default="results/legibility/status_reasoning.json")
    args = ap.parse_args()

    for p in (args.out, args.status):
        os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    items = []
    for s in args.sets.split(","):
        rows = [json.loads(l) for l in open(f"{args.corpus}/{s}.jsonl")]
        items += (rows if args.n == 0 else rows[:args.n])
    print(f"[data] {len(items)} items from {args.sets}", flush=True)

    tok = AutoTokenizer.from_pretrained(args.model)
    if args.quant:
        from transformers import BitsAndBytesConfig
        bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                 bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
        model = AutoModelForCausalLM.from_pretrained(args.model, quantization_config=bnb, device_map="cuda").eval()
        args.device = "cuda"
    else:
        model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float16).to(args.device).eval()
    close_ids = tok(CLOSE, add_special_tokens=False)["input_ids"]
    print(f"[load] {args.model} on {args.device}", flush=True)

    def gen_think(q, greedy):
        m = [{"role": "user", "content": q + "\nReason step by step, then give the final answer in \\boxed{}."}]
        try: e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True, enable_thinking=True)
        except TypeError: e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        enc = e["input_ids"].to(args.device); L = enc.shape[1]
        kw = dict(max_new_tokens=args.max_think, pad_token_id=tok.eos_token_id)
        if greedy: kw["do_sample"] = False
        else: kw.update(do_sample=True, temperature=args.temp, top_p=0.95)
        o = model.generate(input_ids=enc, attention_mask=torch.ones_like(enc), **kw)
        ids = o[0].tolist()[L:]
        full = tok.decode(ids, skip_special_tokens=True)
        trace = full.partition(CLOSE)[0] if CLOSE in full else full
        # Reasoning models (Qwen3) box the answer INSIDE the think block; the answer is the last
        # \boxed{} anywhere. Only force-generate more if no boxed AND </think> never closed (truncated).
        if extract_boxed(full) is None and CLOSE not in full:
            full = full + CLOSE + _finish(enc, o[0].tolist() + close_ids)
        return trace, full

    def _finish(enc, id_seq):
        inp = torch.tensor([id_seq], device=args.device)
        o2 = model.generate(input_ids=inp, attention_mask=torch.ones_like(inp),
                            max_new_tokens=args.max_answer, do_sample=False, pad_token_id=tok.eos_token_id)
        return tok.decode(o2[0].tolist()[len(id_seq):], skip_special_tokens=True).strip()

    def overthink_count(trace):
        low = trace.lower()
        return {w.strip(): low.count(w) for w in OVERTHINK if low.count(w)}

    results = []
    if os.path.exists(args.out):
        try: results = json.load(open(args.out))["rows"]
        except Exception: results = []
    start = len(results); t0 = time.time()
    for j in range(start, len(items)):
        it = items[j]; src = it["source"]; gold = str(it["answer"])
        gt, ga = gen_think(it["question"], greedy=True)
        g_ok = score(extract_answer(ga, src), gold, src)
        # Lotfi signature: a correct answer appears somewhere, but the final committed answer is wrong.
        trace_had = (not g_ok) and any(score(b.strip(), gold, src) for b in all_boxed(ga))
        samples = []
        for s in range(args.k):
            torch.manual_seed(4000 + s)
            st, sa = gen_think(it["question"], greedy=False)
            samples.append(dict(trace_len=len(st), answer=extract_answer(sa, src),
                                ok=score(extract_answer(sa, src), gold, src), overthink=overthink_count(st)))
        passk = g_ok or any(s["ok"] for s in samples)
        results.append(dict(id=it["id"], source=src, question=it["question"], gold=gold,
                            greedy_answer=extract_answer(ga, src), greedy_ok=g_ok, greedy_trace=gt,
                            greedy_trace_len=len(gt), greedy_overthink=overthink_count(gt),
                            trace_had_answer_not_emitted=trace_had,
                            samples=samples, pass1=g_ok, passk=passk,
                            difficulty=np.mean([g_ok] + [s["ok"] for s in samples])))
        json.dump(dict(model=args.model, rows=results), open(args.out, "w"), indent=1)
        per = (time.time() - t0) / max(1, j + 1 - start)
        by_src = {}
        for r in results: by_src.setdefault(r["source"], []).append(r["pass1"])
        json.dump(dict(done=len(results), total=len(items), s_per_item=round(per, 1),
                       pass1={k: round(float(np.mean(v)), 2) for k, v in by_src.items()},
                       eta_min=round((len(items) - len(results)) * per / 60)),
                  open(args.status, "w"), indent=1)
        if args.device == "mps": torch.mps.empty_cache()
        print(f"  [{j+1}/{len(items)}] {src:14} p1={g_ok} passk={passk} tlen={len(gt):5} "
              f"not_emitted={trace_had} ({per:.0f}s/it)", flush=True)
    # summary
    print("\n=== baseline summary (pass@1 / pass@k / avg trace len / not-emitted rate) ===", flush=True)
    for s in set(r["source"] for r in results):
        rs = [r for r in results if r["source"] == s]
        print(f"  {s:16} p1={np.mean([r['pass1'] for r in rs]):.2f} passk={np.mean([r['passk'] for r in rs]):.2f} "
              f"tlen={np.mean([r['greedy_trace_len'] for r in rs]):.0f} "
              f"not_emitted={np.mean([r['trace_had_answer_not_emitted'] for r in rs]):.2f} (n={len(rs)})", flush=True)
    print("[done] ->", args.out, flush=True)

if __name__ == "__main__":
    main()
