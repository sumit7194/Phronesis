#!/usr/bin/env python
"""Experiment B extraction — knowledge-boundary probe (see docs/prereg-legibility-law-B.md).

For each battery item: read the model's pre-answer activation (last token of the chat-templated
prompt, add_generation_prompt=True, thinking disabled) at a set of layers, then generate the answer
greedily and exact-match it against ground truth -> correct / incorrect label.

Output: results/legibility/actsB.npy [n,n_layers,hidden] + metaB.json (per-item label/answer/gt).
"""
import argparse, json, os, re, time, unicodedata
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

HF_ID = "Qwen/Qwen3-4B"
LAYERS = [4, 8, 12, 16, 20, 24, 28, 32, 36]

def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()

def build_items(batt):
    items = []
    for name, z in batt["elements"].items():
        items.append(dict(domain="element", entity=name, gt=str(int(z)),
                          question=f"What is the atomic number of {name}? Reply with only the number."))
    for country, cap in batt["capitals"].items():
        items.append(dict(domain="capital", entity=country, gt=cap,
                          question=f"What is the capital city of {country}? Reply with only the city name."))
    return items

def score(item, answer):
    if item["domain"] == "element":
        m = re.search(r"-?\d+", answer)
        return int(m.group()) == int(item["gt"]) if m else False
    na = norm(answer)  # capital: any accepted spelling ('|'-separated) appears in the reply
    return any(norm(a) in na for a in item["gt"].split("|"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--battery", default="../corpus/legibility/knowledge_battery.json")
    ap.add_argument("--output-dir", default="results/legibility")
    ap.add_argument("--max-new", type=int, default=16)
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    batt = json.load(open(os.path.join(here, args.battery)))
    items = build_items(batt)
    out_dir = os.path.join(here, args.output_dir); os.makedirs(out_dir, exist_ok=True)
    acts_path, meta_path = os.path.join(out_dir, "actsB.npy"), os.path.join(out_dir, "metaB.json")

    dev = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[load] {HF_ID} on {dev} ...", flush=True)
    tok = AutoTokenizer.from_pretrained(HF_ID)
    model = AutoModelForCausalLM.from_pretrained(HF_ID, torch_dtype=torch.float16).to(dev).eval()
    hidden = model.config.hidden_size
    acts = np.zeros((len(items), len(LAYERS), hidden), dtype=np.float32)
    print(f"[load] done; {len(items)} items; hidden={hidden}", flush=True)

    def encode(q):
        try:
            enc = tok.apply_chat_template([{"role": "user", "content": q}], add_generation_prompt=True,
                                          return_tensors="pt", return_dict=True, enable_thinking=False)
        except TypeError:
            enc = tok.apply_chat_template([{"role": "user", "content": q}], add_generation_prompt=True,
                                          return_tensors="pt", return_dict=True)
        return {k: v.to(dev) for k, v in enc.items()}

    t0 = time.time()
    with torch.no_grad():
        for j, it in enumerate(items):
            enc = encode(it["question"]); in_len = enc["input_ids"].shape[1]
            out = model(**enc, output_hidden_states=True)
            for li, L in enumerate(LAYERS):
                acts[j, li] = out.hidden_states[L][0, -1].float().cpu().numpy()
            gen = model.generate(**enc, max_new_tokens=args.max_new, do_sample=False, pad_token_id=tok.eos_token_id)
            ans = tok.decode(gen[0][in_len:], skip_special_tokens=True).strip()
            it["answer"] = ans.replace("\n", " ")[:60]
            it["correct"] = bool(score(it, ans))
            if (j + 1) % 25 == 0 or j + 1 == len(items):
                print(f"  {j+1}/{len(items)}  ({(time.time()-t0)/(j+1):.2f}s/item)", flush=True)

    np.save(acts_path, acts)
    json.dump({"layers": LAYERS, "hf_id": HF_ID, "items": items}, open(meta_path, "w"), indent=1)
    n_corr = sum(it["correct"] for it in items)
    print(f"[done] {len(items)} items, correct={n_corr} ({n_corr/len(items):.1%}) -> {acts_path}", flush=True)
    for dom in ("element", "capital"):
        d = [it for it in items if it["domain"] == dom]
        print(f"  {dom}: {sum(i['correct'] for i in d)}/{len(d)} correct")

if __name__ == "__main__":
    main()
