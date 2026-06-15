#!/usr/bin/env python
"""Experiment A extraction — Legibility Law on Qwen3-4B (see docs/prereg-legibility-law-A.md).

For each target (atomic_number, birth_year, population) x arm (parametric, in-context) x entity
x 3 templates: build a raw-text completion prompt that ends just before the scalar would be
emitted, run a forward pass, and store the last-token residual at a set of layers.

Parametric arm uses the real entity (value recalled from weights). In-context arm uses a nonce
entity bound to the SAME value (value supplied in the prompt) — identical value distribution,
only the route differs. Reads representations on a forced sequence; nothing is sampled.

Output: results/legibility/actsA.npy  [n_rows, n_layers, hidden]  +  metaA.json (row metadata).
Resumable: re-run is cheap (~minutes); checkpoints every 100 rows.
"""
import argparse, json, os, sys, time
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

HF_ID = "Qwen/Qwen3-4B"
LAYERS = [4, 8, 12, 16, 20, 24, 28, 32, 36]

# deterministic nonce names per target (no real-entity collisions); index-stable
_SYL_A = ["flor", "zel", "quan", "brae", "thon", "vix", "morp", "glen", "drav", "skor",
          "pell", "wun", "yarl", "creb", "nost", "jib", "harn", "lutz", "ozai", "venn"]
_SYL_B = ["ium", "ite", "on", "ax", "ene", "yl", "ade", " os", "ix", "um"]
_PERSON_A = ["Zarnak", "Velm", "Quorin", "Brael", "Thessa", "Vondar", "Mirek", "Galwin",
             "Drevia", "Skorin", "Pellan", "Wunmi", "Yarlo", "Cresca", "Nostra", "Jibal",
             "Harnek", "Lutzia", "Ozain", "Vennor"]
_PERSON_B = ["Voss", "Karr", "Quen", "Brel", "Thann", "Vix", "Moric", "Glenn", "Drav",
             "Skell", "Pell", "Wund", "Yarl", "Creb", "Nost", "Jib", "Harn", "Lutz", "Ozai", "Venn"]
_COUNTRY = ["Qwistan", "Bravania", "Thelmora", "Vondoria", "Skorland", "Pellovia", "Wunmaria",
            "Yarlund", "Crescia", "Nostavia", "Jibalia", "Harnesia", "Lutzania", "Ozaimar",
            "Vennoria", "Florinia", "Zelmark", "Quandar", "Braelund", "Thonia", "Vixenia",
            "Morpovia", "Glenmark", "Dravania", "Skellos", "Pellund", "Wundar", "Yarlovia",
            "Crebland", "Nostmar", "Jibovia", "Harnland", "Lutzia", "Ozavia", "Vennmark",
            "Florund", "Zeltavia", "Quanmark", "Braevia", "Thelund"]

def nonce(target, i):
    if target == "atomic_number":
        return (_SYL_A[i % len(_SYL_A)] + _SYL_B[(i // len(_SYL_A)) % len(_SYL_B)]).capitalize()
    if target == "birth_year":
        return f"{_PERSON_A[i % len(_PERSON_A)]} {_PERSON_B[(i // len(_PERSON_A)) % len(_PERSON_B)]}"
    return _COUNTRY[i % len(_COUNTRY)]

def fmt_val(target, v):
    # how the value appears literally in the in-context prompt
    if target == "population":
        return f"{v:g}"
    return str(int(v))

def build_rows(targets):
    rows = []
    for tname, tcfg in targets.items():
        if tname.startswith("_"):
            continue
        ents = list(tcfg["entities"].items())  # [(entity, value)]
        for arm in ("parametric", "incontext"):
            tpls = tcfg["templates_parametric"] if arm == "parametric" else tcfg["templates_incontext"]
            for i, (ent, val) in enumerate(ents):
                name = ent if arm == "parametric" else nonce(tname, i)
                for ti, tpl in enumerate(tpls):
                    if arm == "parametric":
                        text = tpl.replace("{E}", ent)
                    else:
                        text = tpl.replace("{N}", name).replace("{V}", fmt_val(tname, val))
                    rows.append(dict(uid=f"{tname}|{arm}|{i}|{ti}", target=tname, arm=arm,
                                     entity=ent, value=float(val), tpl=ti, text=text))
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", default="../corpus/legibility/targets.json")
    ap.add_argument("--output-dir", default="results/legibility")
    ap.add_argument("--limit", type=int, default=0, help="smoke test: only first N rows")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    targets = json.load(open(os.path.join(here, args.targets)))
    rows = build_rows(targets)
    if args.limit:
        rows = rows[:args.limit]
    out_dir = os.path.join(here, args.output_dir)
    os.makedirs(out_dir, exist_ok=True)
    acts_path = os.path.join(out_dir, "actsA.npy")
    meta_path = os.path.join(out_dir, "metaA.json")

    # resume: skip rows already extracted (matched by uid order)
    done = 0
    acts = np.zeros((len(rows), len(LAYERS), 0), dtype=np.float32)  # hidden dim filled on first pass
    if os.path.exists(meta_path) and os.path.exists(acts_path):
        try:
            prev = json.load(open(meta_path))
            prev_acts = np.load(acts_path)
            if [r["uid"] for r in prev["rows"]] == [r["uid"] for r in rows][:len(prev["rows"])] \
               and prev["layers"] == LAYERS:
                done = len(prev["rows"])
                acts = np.zeros((len(rows), len(LAYERS), prev_acts.shape[2]), dtype=np.float32)
                acts[:done] = prev_acts
                print(f"[resume] {done}/{len(rows)} rows present", flush=True)
        except Exception:
            done = 0

    dev = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[load] {HF_ID} on {dev} ...", flush=True)
    tok = AutoTokenizer.from_pretrained(HF_ID)
    model = AutoModelForCausalLM.from_pretrained(HF_ID, torch_dtype=torch.float16).to(dev)
    model.eval()
    hidden = model.config.hidden_size
    if acts.shape[2] == 0:
        acts = np.zeros((len(rows), len(LAYERS), hidden), dtype=np.float32)
    print(f"[load] done; hidden={hidden}; rows={len(rows)} (done={done})", flush=True)

    def save():
        np.save(acts_path, acts)
        json.dump({"layers": LAYERS, "hf_id": HF_ID,
                   "rows": [{k: r[k] for k in ("uid","target","arm","entity","value","tpl","text")} for r in rows[:done]]},
                  open(meta_path, "w"), indent=1)

    t0 = time.time()
    with torch.no_grad():
        for j in range(done, len(rows)):
            enc = tok(rows[j]["text"], return_tensors="pt").to(dev)
            out = model(**enc, output_hidden_states=True)
            for li, L in enumerate(LAYERS):
                acts[j, li] = out.hidden_states[L][0, -1].float().cpu().numpy()
            done = j + 1
            if done % 100 == 0 or done == len(rows):
                save()
                print(f"  {done}/{len(rows)}  ({(time.time()-t0)/done:.2f}s/row)", flush=True)
    save()
    print(f"[done] {done} rows -> {acts_path}", flush=True)

if __name__ == "__main__":
    main()
