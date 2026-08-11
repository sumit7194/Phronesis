#!/usr/bin/env python
"""CONFIRMATORY test of the protect-vs-blame axis. Prereg: docs/prereg-moral-axis-2026-08-11.md.

F-Y found this axis by mining the sweep with 8 attribute items written for another purpose. This
re-tests it with 16 NEW items and 6 NEW entity classes picked to break the alternative readings,
and evaluates the five preregistered predictions verbatim from mindedness_moral_bank.PREDICTIONS
so the verdict cannot drift from what was declared.

Format is chosen by the same gate as everything else in this arc.
"""
import argparse, json, os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from mindedness_bank import ENTITIES, TEMPLATES, build_prompt
from mindedness_moral_bank import (PROTECT, BLAME, NEW_ENTITIES, EXPERIENCE, AGENCY,
                                   PREDICTIONS, selfcheck)
import scipy.stats as st

DEVICE = "mps"
EPS = 1e-4


def lg(p):
    p = min(max(float(p), EPS), 1 - EPS)
    return float(np.log(p / (1 - p)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()
    tag = args.tag or args.model.split("/")[-1].replace(".", "_")
    OUT = f"results/workspace/mindedness_moral_{tag}.json"

    bad = selfcheck()
    if bad:
        print("BANK SELFCHECK FAILED:\n  " + "\n  ".join(bad))
        return 1

    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(args.model)
    try:
        hf = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    except Exception:
        from transformers import AutoModel
        hf = AutoModel.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    L = model.n_layers
    yes_id = tok(" Yes", add_special_tokens=False)["input_ids"][0]
    no_id = tok(" No", add_special_tokens=False)["input_ids"][0]

    gate_path = f"results/workspace/mindedness_gate_{tag}.json"
    if os.path.exists(gate_path):
        FORMATS = json.load(open(gate_path)).get("usable_formats") or list(TEMPLATES)
    else:
        FORMATS = list(TEMPLATES)
    print(f"[load] {args.model} L={L}  formats={FORMATS}", flush=True)

    @torch.no_grad()
    def pyes(text):
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=[L - 1]) as rec:
            model.forward(ids)
            o = model.unembed(rec.activations[L - 1][0, -1].unsqueeze(0).float()).float()[0]
        return float(torch.softmax(torch.tensor([o[yes_id], o[no_id]]), 0)[0])

    ALL_CLASSES = {**ENTITIES, **NEW_ENTITIES}
    GROUPS = {"protect": PROTECT, "blame": BLAME}
    total = sum(len(v) for v in ALL_CLASSES.values()) * 16 * len(FORMATS)

    P, done = {}, 0
    CK = f"results/workspace/.moralckpt_{tag}.json"
    if os.path.exists(CK):
        P = {tuple(k.split("|")): v for k, v in json.load(open(CK)).items()}
        done = len(P)
        print(f"[resume] {done}/{total} prompts already done", flush=True)

    for cls, exs in ALL_CLASSES.items():
        for tn in FORMATS:
            for ei, e in enumerate(exs):
                for gname, items in GROUPS.items():
                    for ii, a in enumerate(items):
                        k = (tn, cls, str(ei), gname, str(ii))
                        if k in P:
                            continue
                        P[k] = pyes(build_prompt(tok, tn, e, a))
                        done += 1
        json.dump({"|".join(k): v for k, v in P.items()}, open(CK, "w"))
        el = time.time() - t0
        print(f"  {cls:18} {done}/{total}  {el/60:.1f}m  "
              f"eta {el/max(done,1)*(total-done)/60:.0f}m", flush=True)

    # ---- per-class group means, then the gap in LOG-ODDS ----
    raw, gap = {}, {}
    for cls, exs in ALL_CLASSES.items():
        raw[cls] = {}
        for gname, items in GROUPS.items():
            vals = [P[(tn, cls, str(ei), gname, str(ii))]
                    for tn in FORMATS for ei in range(len(exs)) for ii in range(len(items))]
            raw[cls][gname] = float(np.mean(vals))
        gap[cls] = lg(raw[cls]["protect"]) - lg(raw[cls]["blame"])

    # ---- axes and the F-Y gap, from this model's own existing sweep ----
    sweep_f = f"results/workspace/mindedness_v2_sweep_{tag}.json"
    axes, gap_fy = {}, {}
    if os.path.exists(sweep_f):
        S = json.load(open(sweep_f))["logit"]
        shared = [c for c in ENTITIES if c in S.get("moral_patient", {})]
        gap_fy = {c: S["moral_patient"][c] - S["moral_agent"][c] for c in shared}
        for name, facs in (("EXPERIENCE", EXPERIENCE), ("AGENCY", AGENCY)):
            axes[name] = {c: float(np.mean([S[f][c] for f in facs if c in S.get(f, {})]))
                          for c in shared}
    else:
        print(f"[warn] no sweep at {sweep_f}: P1/P2/P3 cannot be evaluated", flush=True)

    # ---- PREDICTIONS, evaluated verbatim ----
    V = {}
    if gap_fy:
        sh = sorted(gap_fy)
        r = st.spearmanr([gap[c] for c in sh], [gap_fy[c] for c in sh]).statistic
        V["P1_replicates_reworded"] = {"value": float(r), "pass": bool(r >= 0.60)}
        for key, axis in (("P2_independent_of_experience", "EXPERIENCE"),
                          ("P3_driven_by_agency", "AGENCY")):
            rr = st.spearmanr([gap[c] for c in sh], [axes[axis][c] for c in sh]).statistic
            V[key] = {"value": float(rr),
                      "pass": bool(abs(rr) < 0.35) if axis == "EXPERIENCE" else bool(rr <= -0.40)}
    V["P4_harm_without_agency_near_zero"] = {
        "value": [gap["natural_disaster"], gap["ai_agentic"]],
        "pass": bool(abs(gap["natural_disaster"]) < 0.12
                     and gap["natural_disaster"] > gap["ai_agentic"])}
    V["P5_humans_can_be_blamed"] = {
        "value": float(gap["human_adult"] - gap["human_culpable"]),
        "pass": bool(gap["human_adult"] - gap["human_culpable"] >= 0.15)}

    res = {"model": args.model, "formats": FORMATS, "prereg": PREDICTIONS,
           "raw_pyes": raw, "gap_logodds": gap, "gap_FY": gap_fy, "axes": axes,
           "verdicts": V, "runtime_min": round((time.time() - t0) / 60, 1)}
    json.dump(res, open(OUT, "w"), indent=1)

    print(f"\n=== PROTECT − BLAME, new items, log-odds  [{args.model}] ===")
    print(f"  {'class':18} {'gap':>7} {'P(protect)':>11} {'P(blame)':>9}   headroom")
    for c in sorted(gap, key=lambda x: -gap[x]):
        hr = "ok" if 0.05 < raw[c]["protect"] < 0.95 and 0.05 < raw[c]["blame"] < 0.95 else "PINNED"
        new = "*" if c in NEW_ENTITIES else " "
        print(f" {new}{c:18} {gap[c]:>+7.2f} {raw[c]['protect']:>11.2f} "
              f"{raw[c]['blame']:>9.2f}   {hr}")
    print("  (* = a class that did not exist when F-Y was found)")

    print("\n=== PREREGISTERED PREDICTIONS ===")
    for k, spec in PREDICTIONS.items():
        if k not in V:
            print(f"  {k:34} NOT EVALUATED (no sweep)")
            continue
        v = V[k]["value"]
        vs = "[" + ", ".join(f"{x:+.2f}" for x in v) + "]" if isinstance(v, list) else f"{v:+.3f}"
        print(f"  {'PASS' if V[k]['pass'] else 'FAIL'}  {k:34} {vs:>18}   {spec['test']}")
    npass = sum(1 for k in V if V[k]["pass"])
    print(f"\n  {npass}/{len(V)} preregistered predictions passed")
    print(f"[done] {res['runtime_min']} min -> {OUT}", flush=True)


if __name__ == "__main__":
    sys.exit(main() or 0)
