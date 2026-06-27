#!/usr/bin/env python
"""Does reasoning flatten the depth-of-emergence of parametric recall? (docs/prereg-thinking-recall.md)

Welds F165 (recalled facts legible only at deep layers) to Google's "Thinking to Recall". For each
fact: read the pre-answer residual (a) thinking OFF at the input end, (b) thinking ON at the end of the
generated reasoning trace; probe the scalar's legibility per layer. Splits: by whether the model
RECALLS the fact directly (easy vs hard — where thinking has room to help), and whether the THINK trace
STATES the value (priming vs pure computational-buffer).

One fact type per invocation (atomic_number | birth_year); v2 = run both, analyze together.
  mvp/.venv/bin/python mvp/thinking_recall.py --fact atomic_number --model Qwen/Qwen3-4B \
     --layers 4,8,12,16,20,24,28,32,36
"""
import argparse, json, os, re, time
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_predict, KFold

FACTS = {
    "atomic_number": dict(src="../corpus/legibility/knowledge_battery.json", path=["elements"],
                          q="What is the atomic number of {name}? Reply with only the number.",
                          rx=r"-?\d+"),
    "birth_year": dict(src="../corpus/legibility/targets.json", path=["birth_year", "entities"],
                       q="In what year was {name} born? Reply with only the year.",
                       rx=r"\b(1[0-9]{3}|20[0-9]{2})\b"),
}

def pearson(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return 0.0 if a.std() < 1e-9 or b.std() < 1e-9 else float(np.corrcoef(a, b)[0, 1])

def ridge_r(X, y):
    if len(y) < 10 or np.std(y) < 1e-9:
        return float("nan")
    est = make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-1, 4, 10)))
    return pearson(cross_val_predict(est, X, y, cv=KFold(5, shuffle=True, random_state=42)), y)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fact", default="atomic_number", choices=list(FACTS))
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--layers", default="4,8,12,16,20,24,28,32,36")
    ap.add_argument("--max-new", type=int, default=320)
    ap.add_argument("--output-dir", default="results/legibility")
    args = ap.parse_args()
    LAYERS = [int(x) for x in args.layers.split(",")]
    cfg = FACTS[args.fact]
    here = os.path.dirname(os.path.abspath(__file__))
    tbl = json.load(open(os.path.join(here, cfg["src"])))
    for k in cfg["path"]:
        tbl = tbl[k]
    items = [(n, float(v)) for n, v in tbl.items()]
    out_dir = os.path.join(here, args.output_dir); os.makedirs(out_dir, exist_ok=True)
    tag = f"{args.fact}_{args.model.split('/')[-1]}"

    dev = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[load] {args.model} on {dev}; {len(items)} {args.fact} facts ...", flush=True)
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float16).to(dev).eval()
    hidden = model.config.hidden_size
    close_ids = tok("</think>", add_special_tokens=False)["input_ids"]
    print(f"[load] done; hidden={hidden}; </think>={close_ids}", flush=True)

    def templ(name, thinking):
        msgs = [{"role": "user", "content": cfg["q"].format(name=name)}]
        try:
            enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt",
                                          return_dict=True, enable_thinking=thinking)
        except TypeError:
            enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        return {k: v.to(dev) for k, v in enc.items()}

    def find_close(cont):
        n = len(close_ids)
        for i in range(len(cont) - n, -1, -1):
            if cont[i:i + n] == close_ids:
                return i + n
        return None

    acts_no = np.zeros((len(items), len(LAYERS), hidden), np.float32)
    acts_th = np.zeros((len(items), len(LAYERS), hidden), np.float32)
    meta = []
    npz_path = os.path.join(out_dir, f"thinkrecall_{tag}.npz")
    json_path = os.path.join(out_dir, f"thinkrecall_{tag}.json")
    start = 0
    if os.path.exists(npz_path) and os.path.exists(json_path):
        try:
            d = np.load(npz_path); jm = json.load(open(json_path))
            if d["acts_no"].shape == acts_no.shape and jm.get("fact") == args.fact:
                acts_no, acts_th = d["acts_no"].copy(), d["acts_th"].copy()
                meta = jm["meta"]; start = len(meta)
                print(f"[resume] {start}/{len(items)} items present", flush=True)
        except Exception:
            start = 0; meta = []

    def save():
        np.savez(npz_path, acts_no=acts_no, acts_th=acts_th, layers=LAYERS)
        json.dump({"model": args.model, "fact": args.fact, "layers": LAYERS, "meta": meta},
                  open(json_path, "w"), indent=1)

    t0 = time.time()
    with torch.no_grad():
        for j in range(start, len(items)):
            name, val = items[j]
            # nothink: read activation at input end + a short direct answer for the recall (easy/hard) label
            enc = templ(name, False); in_len = enc["input_ids"].shape[1]
            out = model(**enc, output_hidden_states=True)
            for li, L in enumerate(LAYERS):
                acts_no[j, li] = out.hidden_states[L][0, -1].float().cpu().numpy()
            ga = model.generate(**enc, max_new_tokens=16, do_sample=False, pad_token_id=tok.eos_token_id)
            ans = tok.decode(ga[0][in_len:], skip_special_tokens=True)
            m = re.search(cfg["rx"], ans)
            recalled = bool(m and int(re.search(r"-?\d+", m.group()).group()) == int(val))
            # think: generate trace, read activation at end of trace
            enc = templ(name, True); in_len = enc["input_ids"].shape[1]
            gt = model.generate(**enc, max_new_tokens=args.max_new, do_sample=False, pad_token_id=tok.eos_token_id)
            full = gt[0].tolist(); cont = full[in_len:]
            close = find_close(cont); finished = close is not None
            read_pos = (in_len + close - 1) if finished else len(full) - 1
            trace = tok.decode(cont[:close] if finished else cont, skip_special_tokens=True)
            out = model(torch.tensor([full[:read_pos + 1]], device=dev), output_hidden_states=True)
            for li, L in enumerate(LAYERS):
                acts_th[j, li] = out.hidden_states[L][0, -1].float().cpu().numpy()
            meta.append(dict(name=name, value=val, recalled=recalled,
                             z_stated=bool(re.search(rf"\b{int(val)}\b", trace)),
                             think_finished=finished, trace_len=len(cont), trace=trace[:300]))
            if (j + 1) % 10 == 0 or j + 1 == len(items):
                save()
                print(f"  {j+1}/{len(items)}  ({(time.time()-t0)/max(1,j+1-start):.1f}s/item)", flush=True)
    save()

    val = np.array([m["value"] for m in meta], float)
    rec = np.array([m["recalled"] for m in meta]); zst = np.array([m["z_stated"] for m in meta])
    fin = np.array([m["think_finished"] for m in meta])
    print(f"\n{args.fact}: recalled(easy) {rec.sum()}/{len(rec)} | z_stated {zst.sum()} | think_finished {fin.sum()}")

    def ramp(base, label):
        mask = base & fin   # think-read is only valid where </think> closed; compare both arms on it
        if mask.sum() < 10:
            print(f"  {label}: n_finished={mask.sum()} (<10, skip)"); return None
        print(f"\n  {label} (n_finished={mask.sum()}/{base.sum()}):   {'layer':>5s} {'nothink':>8s} {'think':>8s} {'think|noZ':>10s}")
        rows = []
        for li, L in enumerate(LAYERS):
            r_no = ridge_r(acts_no[mask, li, :], val[mask])
            r_th = ridge_r(acts_th[mask, li, :], val[mask])
            nz = mask & ~zst
            r_tn = ridge_r(acts_th[nz, li, :], val[nz])
            rows.append(dict(layer=L, nothink=r_no, think=r_th, think_noZ=r_tn))
            print(f"  {'':>{len(label)+8}s}{L:>5d} {r_no:>8.3f} {r_th:>8.3f} {r_tn:>10.3f}")
        return rows
    full = np.ones(len(items), bool)
    report = dict(all=ramp(full, "ALL"), easy=ramp(rec, "EASY (recalled)"), hard=ramp(~rec, "HARD (not recalled)"))
    json.dump(report, open(os.path.join(out_dir, f"thinkrecall_{tag}_probe.json"), "w"), indent=1)
    print(f"\n[done] -> thinkrecall_{tag}_probe.json")

if __name__ == "__main__":
    main()
