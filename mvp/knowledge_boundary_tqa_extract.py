#!/usr/bin/env python
"""Experiment B (real) — knowledge-boundary probe on TruthfulQA MC1 (docs/prereg-legibility-law-B.md).

The hand-built factual battery was too easy (Qwen3-4B ~95% correct → no class balance). Pivot to
TruthfulQA MC1: exact built-in labels, the false-premise/misconception domain F121 lives in, and a
4B sits at a balanced accuracy. No confabulation risk (labels are the dataset's).

Per question: read the pre-answer activation at the end of "Q: {question}\nA:" (where "do I know the
truthful answer" must live), then label correctness by standard MC1 — the model is correct iff it
assigns the highest total log-probability to the dataset's correct choice (vs the misconception
distractors). Raw-text LL scoring; nothing is sampled/parsed.

Output: results/legibility/{actsB.npy, metaB.json}.
"""
import argparse, json, os, time
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

HF_ID = "Qwen/Qwen3-4B"
LAYERS = [4, 8, 12, 16, 20, 24, 28, 32, 36]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="first N questions (0 = all 817)")
    ap.add_argument("--output-dir", default="results/legibility")
    args = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(here, args.output_dir); os.makedirs(out_dir, exist_ok=True)

    ds = load_dataset("truthful_qa", "multiple_choice")["validation"]
    rows = list(ds)
    if args.limit:
        rows = rows[:args.limit]

    dev = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[load] {HF_ID} on {dev} ...", flush=True)
    tok = AutoTokenizer.from_pretrained(HF_ID)
    model = AutoModelForCausalLM.from_pretrained(HF_ID, torch_dtype=torch.float16).to(dev).eval()
    hidden = model.config.hidden_size
    acts = np.zeros((len(rows), len(LAYERS), hidden), dtype=np.float32)
    print(f"[load] done; {len(rows)} questions; hidden={hidden}", flush=True)

    def option_logprob(prefix_ids, option_text):
        opt_ids = tok(" " + option_text.strip(), add_special_tokens=False)["input_ids"]
        if not opt_ids:
            return -1e9
        ids = prefix_ids + opt_ids
        with torch.no_grad():
            logits = model(torch.tensor([ids], device=dev)).logits[0].float()
        lp = torch.log_softmax(logits, dim=-1)
        total = 0.0
        for k, tid in enumerate(opt_ids):
            pos = len(prefix_ids) + k
            total += lp[pos - 1, tid].item()
        return total  # total (un-normalized) log-prob — canonical MC1

    items = []
    t0 = time.time()
    with torch.no_grad():
        for j, r in enumerate(rows):
            q = r["question"]
            prefix = f"Q: {q}\nA:"
            enc = tok(prefix, return_tensors="pt").to(dev)
            prefix_ids = enc["input_ids"][0].tolist()
            out = model(**enc, output_hidden_states=True)
            for li, L in enumerate(LAYERS):
                acts[j, li] = out.hidden_states[L][0, -1].float().cpu().numpy()
            choices = r["mc1_targets"]["choices"]
            labels = r["mc1_targets"]["labels"]
            correct_idx = labels.index(1)
            lps = [option_logprob(prefix_ids, c) for c in choices]
            pred_idx = int(np.argmax(lps))
            items.append(dict(domain="truthfulqa", entity=q[:80], question=q,
                              n_choices=len(choices), correct_idx=int(correct_idx),
                              pred_idx=pred_idx, correct=bool(pred_idx == correct_idx),
                              pred_answer=choices[pred_idx][:80], gold_answer=choices[correct_idx][:80]))
            if (j + 1) % 50 == 0 or j + 1 == len(rows):
                acc = sum(it["correct"] for it in items) / len(items)
                print(f"  {j+1}/{len(rows)}  acc={acc:.3f}  ({(time.time()-t0)/(j+1):.2f}s/q)", flush=True)

    np.save(os.path.join(out_dir, "actsB.npy"), acts)
    json.dump({"layers": LAYERS, "hf_id": HF_ID, "task": "truthfulqa_mc1", "items": items},
              open(os.path.join(out_dir, "metaB.json"), "w"), indent=1)
    nc = sum(it["correct"] for it in items)
    print(f"[done] {len(items)} q, correct={nc} ({nc/len(items):.1%}) -> actsB.npy", flush=True)

if __name__ == "__main__":
    main()
