#!/usr/bin/env python
"""Validity checks on the mindedness-axis finding (amendment to docs/prereg-mindedness-geometry.md).

V1 ANSWER-POLARITY CONFOUND (the big one). Mental questions about a rock expect "no"; about a human
    expect "yes". Physical questions expect "yes" for nearly everything. So v_mind = mean(mental) -
    mean(physical) could partly encode the EXPECTED ANSWER rather than mindedness. Build v_polarity
    from unrelated unambiguous yes/no items and measure cos(v_mind, v_polarity). Also record the
    model's actual P(yes) per (class, kind) — an independent behavioural gradient.
V2 TEMPLATE ROBUSTNESS. Rebuild v_mind under 3 wrappers; cos across templates within class.
    If the axis is template-specific, the result is an artifact of one phrasing.
V3 ATTRIBUTE-SPLIT RELIABILITY. Original ceiling split by EXEMPLAR; this splits by ATTRIBUTE
    (does the direction generalize across *which* mental property is asked?).

Read-only forward passes. Frozen entity/attribute banks imported from mindedness_geometry.
"""
import argparse, json, os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from mindedness_geometry import ENTITIES, MENTAL, PHYSICAL, cos

DEVICE = "mps"

TEMPLATES = {
    "T1": "Question: Does {e} {a}?\nAnswer:",              # original (frozen)
    "T2": "Answer yes or no. Does {e} {a}?\nAnswer:",
    "T3": "{e} — does it {a}?\nAnswer:",
}
# unrelated unambiguous polarity items (content has nothing to do with minds)
POLARITY_YES = ["Is the sky blue on a clear day", "Is water wet", "Is two plus two equal to four",
                "Is ice colder than boiling water", "Do birds have feathers", "Is Paris in France"]
POLARITY_NO = ["Is the sky green on a clear day", "Is fire cold", "Is two plus two equal to five",
               "Is ice hotter than boiling water", "Do birds have scales", "Is Paris in Brazil"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3.5-4B")
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()
    tag = args.tag or args.model.split("/")[-1].replace(".", "_")
    OUT = f"results/workspace/mindedness_validate_{tag}.json"
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(args.model)
    try:
        hf = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    except Exception:
        from transformers import AutoModel
        hf = AutoModel.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    L, d = model.n_layers, model.d_model
    layers = list(range(L))
    yes_id = tok(" Yes", add_special_tokens=False)["input_ids"][0]
    no_id = tok(" No", add_special_tokens=False)["input_ids"][0]
    print(f"[load] {args.model} L={L} d={d}", flush=True)

    @torch.no_grad()
    def run(text):
        """last-token residuals at every layer + P(yes) over {Yes,No} at the answer slot."""
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=layers) as rec:
            model.forward(ids)
            acts = torch.stack([rec.activations[l][0, -1] for l in layers]).float().cpu().numpy()
            lg = model.unembed(rec.activations[L - 1][0, -1].unsqueeze(0).float()).float()[0]
        py = float(torch.softmax(torch.tensor([lg[yes_id], lg[no_id]]), 0)[0])
        return acts, py

    # ---------- collect: 3 templates x 240 prompts ----------
    A, P = {}, {}
    for tname, tmpl in TEMPLATES.items():
        for cls, exs in ENTITIES.items():
            for ei, e in enumerate(exs):
                for kind, attrs in (("mental", MENTAL), ("phys", PHYSICAL)):
                    for ai, a in enumerate(attrs):
                        acts, py = run(tmpl.format(e=e, a=a))
                        A[(tname, cls, ei, kind, ai)] = acts
                        P[(tname, cls, ei, kind, ai)] = py
        print(f"  [{tname}] done {round(time.time()-t0)}s", flush=True)

    # polarity direction (template T1 wrapper, unrelated content)
    py_acts = [run(f"Question: {q}?\nAnswer:")[0] for q in POLARITY_YES]
    pn_acts = [run(f"Question: {q}?\nAnswer:")[0] for q in POLARITY_NO]
    v_pol = np.mean(py_acts, 0) - np.mean(pn_acts, 0)
    pol_yes_py = np.mean([run(f"Question: {q}?\nAnswer:")[1] for q in POLARITY_YES])
    pol_no_py = np.mean([run(f"Question: {q}?\nAnswer:")[1] for q in POLARITY_NO])
    print(f"  [polarity sanity] P(yes) on YES items={pol_yes_py:.2f} on NO items={pol_no_py:.2f}", flush=True)

    def vmind(tname, cls, exs=None, mi=None, pi=None):
        exs = range(4) if exs is None else exs
        mi = range(len(MENTAL)) if mi is None else mi
        pi = range(len(PHYSICAL)) if pi is None else pi
        m = np.mean([A[(tname, cls, e, "mental", a)] for e in exs for a in mi], 0)
        p = np.mean([A[(tname, cls, e, "phys", a)] for e in exs for a in pi], 0)
        return m - p

    classes = list(ENTITIES)
    res = {"model": args.model, "n_layers": L, "layers_frac": [l / (L - 1) for l in layers]}

    # ---- V1: polarity contamination + behavioural P(yes) gradient ----
    res["V1_polarity_cos"] = {c: [cos(vmind("T1", c)[l], v_pol[l]) for l in layers] for c in classes}
    res["V1_pyes"] = {c: {k: float(np.mean([P[("T1", c, e, k, a)] for e in range(4)
                                            for a in range(6)])) for k in ("mental", "phys")}
                      for c in classes}
    # ---- V2: template robustness ----
    res["V2_template_cos"] = {c: {f"{t1}|{t2}": [cos(vmind(t1, c)[l], vmind(t2, c)[l]) for l in layers]
                                  for i, t1 in enumerate(TEMPLATES) for t2 in list(TEMPLATES)[i + 1:]}
                              for c in classes}
    # between-class structure under T2/T3 (does the self-outlier survive rephrasing?)
    res["V2_between"] = {t: {f"{a}|{b}": [cos(vmind(t, a)[l], vmind(t, b)[l]) for l in layers]
                             for i, a in enumerate(classes) for b in classes[i + 1:]}
                         for t in TEMPLATES}
    # ---- V3: attribute-split ceiling (vs the original exemplar-split) ----
    res["V3_attr_split"] = {c: [cos(vmind("T1", c, mi=[0, 1, 2], pi=[0, 1, 2])[l],
                                    vmind("T1", c, mi=[3, 4, 5], pi=[3, 4, 5])[l]) for l in layers]
                            for c in classes}
    res["runtime_min"] = round((time.time() - t0) / 60, 1)
    json.dump(res, open(OUT, "w"), indent=1)

    # ---------- report at the mid/deep band ----------
    band = [l for l in layers if 0.5 <= l / (L - 1) <= 0.8]
    mean_band = lambda seq: float(np.mean([seq[l] for l in band]))
    print("\n=== V1 POLARITY CONTAMINATION (want LOW |cos|; high = axis is really yes/no) ===")
    for c in classes:
        print(f"  {c:8} cos(v_mind, v_polarity) = {mean_band(res['V1_polarity_cos'][c]):+.3f}")
    print("\n=== V1 behavioural P(yes) — does mind-attribution actually grade by entity? ===")
    for c in classes:
        r = res["V1_pyes"][c]
        print(f"  {c:8} mental={r['mental']:.2f}  physical={r['phys']:.2f}")
    print("\n=== V2 TEMPLATE ROBUSTNESS (cos of v_mind across wrappers, same class) ===")
    for c in classes:
        vals = {k: mean_band(v) for k, v in res["V2_template_cos"][c].items()}
        print(f"  {c:8} " + "  ".join(f"{k}={v:+.3f}" for k, v in vals.items()))
    print("\n=== V2 self-outlier under each template (self-pairs vs non-self) ===")
    for t in TEMPLATES:
        sp = [mean_band(v) for k, v in res["V2_between"][t].items() if "self" in k]
        op = [mean_band(v) for k, v in res["V2_between"][t].items() if "self" not in k]
        print(f"  {t}: self={np.mean(sp):+.3f}  non-self={np.mean(op):+.3f}  "
              f"{'SELF OUTLIER' if np.mean(sp) < np.mean(op) else 'no'}")
    print("\n=== V3 ATTRIBUTE-SPLIT reliability (generalize across which property is asked?) ===")
    for c in classes:
        print(f"  {c:8} {mean_band(res['V3_attr_split'][c]):+.3f}")
    print(f"\n[done] {res['runtime_min']} min -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
