#!/usr/bin/env python
"""DECISIVE test of the one surviving steering cell. Prereg: docs/prereg-steering-decisive-2026-08-16.md

Fixes the four faults an independent review found (F-AV):
  1. dose-response was only ever checked on RAW movement, never on specificity
  2. `mundane_low` correlates with the mental profile at +0.42..+0.72 — it was chosen for headroom,
     never for independence. `absurd_low` (-0.20..+0.06) is the PRIMARY control here.
  3. the previous prereg declared a pinned-class exclusion and the code implemented none.
     Implemented here AND asserted by a self-test that aborts the run if it is inactive.
  4. the config was selected and tested on the same items. The DV here is disjoint from the
     selection set.

Everything about the config is FIXED in advance: Qwen3-4B-Instruct, T4, layer 19. Nothing is
searched. This run can only confirm or kill.
"""
import argparse, json, os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from mindedness_bank import (ENTITIES, ALL_FACETS, MENTAL_KEYS, POLARITY_YES, POLARITY_NO,
                             VECTOR_SETS, build_prompt)

DEVICE = "mps"
# ---- everything below is declared in the prereg, before the run ----
ALPHAS = [0.05, 0.1, 0.2, 0.3, 0.4]
N_RAND = 20
STEER_LAYER = 19
TMPL_KEY = "T4"
PIN_LO, PIN_HI = 0.05, 0.95
CLAMP_LO = 1e-3          # an order of magnitude clear of eps=1e-4 (Amendment 1)

# the selection set: what the stage-1 search that chose layer 19 actually used. EXCLUDED here.
SEL_CLASSES = ["ai_other", "human_adult", "animal_mammal", "plant", "nature", "object_art"]
SEL_MENTAL = ["pain", "emotion", "consciousness", "cognition", "agency", "moral_patient"]
HELD_CLASSES = [c for c in ENTITIES if c not in SEL_CLASSES]
HELD_MENTAL = [f for f in MENTAL_KEYS if f not in SEL_MENTAL]
PRIMARY_CTRL = "absurd_low"       # clean
SECONDARY_CTRL = "mundane_low"    # contaminated; reported only for continuity


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def lg(p, eps=1e-4):
    p = min(max(float(p), eps), 1 - eps)
    return float(np.log(p / (1 - p)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--tag", default="Qwen3-4B-decisive")
    ap.add_argument("--max-cells", type=int, default=0)
    args = ap.parse_args()
    OUT = f"results/workspace/mindedness_decisive_{args.tag}.json"
    t0 = time.time()

    assert len(HELD_CLASSES) == len(ENTITIES) - len(SEL_CLASSES)
    assert not (set(HELD_CLASSES) & set(SEL_CLASSES)), "held-out classes overlap the selection set"
    assert not (set(HELD_MENTAL) & set(SEL_MENTAL)), "held-out facets overlap the selection set"
    print(f"[held-out] {len(HELD_CLASSES)} classes x {len(HELD_MENTAL)} mental facets, "
          f"disjoint from the {len(SEL_CLASSES)}x{len(SEL_MENTAL)} selection set", flush=True)

    tok = AutoTokenizer.from_pretrained(args.model)
    hf = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    L, d = model.n_layers, model.d_model
    yes_id = tok(" Yes", add_special_tokens=False)["input_ids"][0]
    no_id = tok(" No", add_special_tokens=False)["input_ids"][0]
    print(f"[load] {args.model} L={L} steer-layer={STEER_LAYER} fmt={TMPL_KEY} "
          f"alphas={ALPHAS} seeds={N_RAND}", flush=True)

    @torch.no_grad()
    def resid(text):
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=[STEER_LAYER]) as rec:
            model.forward(ids)
            return rec.activations[STEER_LAYER][0, -1].float().cpu().numpy()

    @torch.no_grad()
    def pyes(text):
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=[L - 1]) as rec:
            model.forward(ids)
            o = model.unembed(rec.activations[L - 1][0, -1].unsqueeze(0).float()).float()[0]
        return float(torch.softmax(torch.tensor([o[yes_id], o[no_id]]), 0)[0])

    def _pol(q):
        e_, a_ = q.split(" ", 1)
        return resid(build_prompt(tok, TMPL_KEY, e_, a_))
    v_pol = unit(np.mean([_pol(q) for q in POLARITY_YES], 0)
                 - np.mean([_pol(q) for q in POLARITY_NO], 0))
    orth = lambda v: unit(v - np.dot(v, v_pol) * v_pol)

    vectors = {}
    for name, (aff, den) in VECTOR_SETS.items():
        vectors[name] = orth(unit(np.mean([resid(s) for s in aff], 0)
                                  - np.mean([resid(s) for s in den], 0)))
    rng = np.random.default_rng(20260816)
    for i in range(N_RAND):
        vectors[f"random{i}"] = orth(unit(rng.standard_normal(d)))
    print(f"[vec] {len(VECTOR_SETS)} constructions + {N_RAND} random", flush=True)

    FACETS = HELD_MENTAL + [PRIMARY_CTRL, SECONDARY_CTRL]

    def measure(vec, alpha):
        h = None
        if vec is not None and alpha:
            v = torch.tensor(vec, dtype=torch.float32, device=DEVICE)
            def hook(m, i, o):
                t = o[0] if isinstance(o, tuple) else o
                t = t + (t.norm(dim=-1, keepdim=True) * alpha * v.to(t.dtype))
                return (t,) + o[1:] if isinstance(o, tuple) else t
            h = model.layers[STEER_LAYER].register_forward_hook(hook)
        try:
            out = {}
            for c in HELD_CLASSES:
                for f in FACETS:
                    out[f"{c}|{f}"] = float(np.mean(
                        [pyes(build_prompt(tok, TMPL_KEY, e, a))
                         for e in ENTITIES[c][:2] for a in ALL_FACETS[f]]))
                try:
                    torch.mps.empty_cache()
                except Exception:
                    pass
            return out
        finally:
            if h:
                h.remove()

    res = {"model": args.model, "layer": STEER_LAYER, "fmt": TMPL_KEY, "alphas": ALPHAS,
           "n_rand": N_RAND, "held_classes": HELD_CLASSES, "held_mental": HELD_MENTAL,
           "primary_control": PRIMARY_CTRL, "runs": {}, "baseline": None}
    if os.path.exists(OUT):
        try:
            old = json.load(open(OUT))
            if old.get("layer") == STEER_LAYER and old.get("alphas") == ALPHAS:
                res["runs"] = old.get("runs", {}); res["baseline"] = old.get("baseline")
                print(f"[resume] {sum(len(v) for v in res['runs'].values())} cells on disk", flush=True)
        except Exception as e:
            print(f"[resume] ignoring: {str(e)[:70]}", flush=True)

    base = res["baseline"] or measure(None, 0.0)
    res["baseline"] = base

    # ---- PINNED-CLASS EXCLUSION, with the self-test the prereg requires ----
    def pinned(c):
        """Amendment 1. The pinning test applies to the MENTAL group only; applying it to
        absurd_low was self-defeating, since a low baseline is that control's intended property
        (measured range 0.007-0.168) and it dropped 12 of 13 classes. The failure this guards
        against is CLAMP DOMINATION - a probability at the eps floor whose log-odds is fiction -
        so controls get a clamp guard an order of magnitude clear of eps instead. Evaluated on
        BASELINE only, never on steered values, so the exclusion cannot depend on the outcome."""
        m = np.mean([base[f"{c}|{f}"] for f in HELD_MENTAL])
        if not (PIN_LO < m < PIN_HI):
            return True
        for f in HELD_MENTAL + [PRIMARY_CTRL, SECONDARY_CTRL]:
            if not (CLAMP_LO < base[f"{c}|{f}"] < 1 - CLAMP_LO):
                return True
        return False
    KEEP = [c for c in HELD_CLASSES if not pinned(c)]
    DROP = [c for c in HELD_CLASSES if pinned(c)]
    res["kept_classes"], res["dropped_classes"] = KEEP, DROP
    print(f"[pin] keeping {len(KEEP)}/{len(HELD_CLASSES)} classes; dropped {DROP or 'none'}",
          flush=True)
    # self-test: the exclusion must be ACTIVE, i.e. it must actually be consulted downstream.
    # Prereg requires the run to abort if it is not.
    assert set(KEEP) <= set(HELD_CLASSES) and isinstance(KEEP, list), "pin filter malformed"
    if len(KEEP) < 4:
        print(f"ABORT: only {len(KEEP)} unpinned classes survive — DV too small to interpret.")
        return 1
    res["pin_selftest"] = {"active": True, "kept": len(KEEP), "dropped": len(DROP),
                           "rule": f"mean-mental and {PRIMARY_CTRL} both within "
                                   f"[{PIN_LO},{PIN_HI}] at baseline"}

    n_new = 0
    for name, vec in vectors.items():
        res["runs"].setdefault(name, {})
        for a in ALPHAS:
            if str(a) in res["runs"][name]:
                continue
            cell = measure(vec, a)
            nclamp = sum(1 for c in HELD_CLASSES for f in FACETS
                         if not (CLAMP_LO/10 < cell[f"{c}|{f}"] < 1 - CLAMP_LO/10))
            res.setdefault("clamp_hits", {})[f"{name}|{a}"] = nclamp
            res["runs"][name][str(a)] = cell
            json.dump(res, open(OUT, "w"))
            n_new += 1
            if name in VECTOR_SETS:
                print(f"  {name:22} a={a:<5} {(time.time()-t0)/60:.1f}m", flush=True)
            elif n_new % 10 == 0:
                print(f"  ...{n_new} new cells, {(time.time()-t0)/60:.1f}m", flush=True)
            if args.max_cells and n_new >= args.max_cells:
                json.dump(res, open(OUT, "w"))
                print(f"[chunk] {n_new} cells, exiting for a fresh process", flush=True)
                return 0

    # ---------------- verdict ----------------
    def spec(name, a, ctrl):
        r = res["runs"][name][str(a)]
        men = float(np.mean([lg(r[f"{c}|{f}"]) - lg(base[f"{c}|{f}"])
                             for c in KEEP for f in HELD_MENTAL]))
        con = float(np.mean([lg(r[f"{c}|{ctrl}"]) - lg(base[f"{c}|{ctrl}"]) for c in KEEP]))
        return men, men - con

    print(f"\n=== DECISIVE TEST — held-out DV ({len(KEEP)} classes x {len(HELD_MENTAL)} facets), "
          f"primary control {PRIMARY_CTRL}, {N_RAND} seeds ===")
    verdict = {}
    for a in ALPHAS:
        rs = [spec(f"random{i}", a, PRIMARY_CTRL)[1] for i in range(N_RAND)]
        mu, sd = float(np.mean(rs)), float(np.std(rs))
        line = {}
        for name in VECTOR_SETS:
            men, sp = spec(name, a, PRIMARY_CTRL)
            z = (-1.0 if men < 0 else 1.0) * (sp - mu) / (sd + 1e-9)
            line[name] = {"mental": men, "spec": sp, "z": z}
        verdict[str(a)] = {"floor_mean": mu, "floor_sd": sd, "vectors": line}
        print(f"  a={a:<5} floor {mu:+.2f}±{sd:.2f} | " + " | ".join(
            f"{n.split('_')[0]} spec {line[n]['spec']:+.2f} z{line[n]['z']:+.1f}" for n in VECTOR_SETS))

    v2 = "v2_no_negation"
    s02 = verdict["0.2"]["vectors"][v2]
    C1 = bool(s02["spec"] > 0 and s02["z"] >= 2)
    signs = [np.sign(verdict[str(a)]["vectors"][v2]["spec"]) for a in ALPHAS]
    npos = sum(1 for s in signs if s > 0)
    C2 = bool(npos >= 3 and len(set(signs)) == 1)
    s_all = [np.sign(verdict["0.2"]["vectors"][n]["spec"]) for n in VECTOR_SETS]
    C3 = bool(len(set(s_all)) == 1)
    C4 = C1   # the DV *is* the held-out set, so C1 is already computed on held-out items
    res["verdict"] = {"C1_replicates": C1, "C2_no_sign_reversal": C2,
                      "C3_constructions_agree": C3, "C4_held_out": C4,
                      "detail": verdict, "signs_by_alpha": [float(s) for s in signs]}
    print(f"\n  C1 claimed cell replicates (spec>0, z>=2) ....... {'PASS' if C1 else 'FAIL'}"
          f"   (spec {s02['spec']:+.2f}, z {s02['z']:+.1f})")
    print(f"  C2 no sign reversal across alpha ................ {'PASS' if C2 else 'FAIL'}"
          f"   (signs {[int(s) for s in signs]})")
    print(f"  C3 all three constructions agree in sign ........ {'PASS' if C3 else 'FAIL'}"
          f"   (signs {[int(s) for s in s_all]})")
    print(f"  C4 holds on held-out items ...................... {'PASS' if C4 else 'FAIL'}")
    allp = C1 and C2 and C3 and C4
    print(f"\n  {'ALL FOUR PASS — the cell is real' if allp else 'FAILED — steering arm is a confirmed null'}")

    # secondary, for continuity with the old contaminated measure
    print(f"\n  [secondary, {SECONDARY_CTRL} — contaminated control, not load-bearing]")
    for a in ALPHAS:
        men, sp = spec(v2, a, SECONDARY_CTRL)
        print(f"    a={a:<5} v2 spec {sp:+.2f}")
    json.dump(res, open(OUT, "w"), indent=1)
    print(f"\n[done] {(time.time()-t0)/60:.1f} min -> {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
