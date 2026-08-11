#!/usr/bin/env python
"""STAGE 1 — does the steering vector have ANY traction on this model?

F-AJ: the negation-free vector moves the mental DV by +5.54 logits on Qwen3-4B and by -0.08 and
+0.03 on OLMo and Gemma. At that size the specificity ratio is noise over noise, so those two
models are UNTESTED, not negative. Both were run at mid-depth and alpha <= 0.8 because that is
what worked on Qwen. Neither choice was ever justified per model.

This searches layer x alpha for a config where the vector actually moves the DV. It is a
PRECONDITION check, not the claim:

  * selection here is on RAW MOVEMENT of the mental group ONLY. Specificity is never consulted,
    so stage 2 is not selected on its own outcome.
  * stage 2 re-runs the full DV at the winning config WITH a 5-seed random floor at that same
    config, so a setting that moves everything is caught by the floor moving too.
  * absurd_low is carried through as a degeneracy detector: if a config only works by making the
    model say yes to everything, absurd_low rises with it and the config is disqualified here.

Lean DV on purpose (6 classes x 6 mental facets + 2 controls): enough to detect movement, cheap
enough to search 20 configs. The full bank is used in stage 2.
"""
import argparse, json, os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from mindedness_bank import (ENTITIES, ALL_FACETS, TEMPLATES, POLARITY_YES, POLARITY_NO,
                             VECTOR_SETS, build_prompt)

DEVICE = "mps"
# declared before running
PROBE_CLASSES = ["ai_other", "human_adult", "animal_mammal", "plant", "nature", "object_art"]
PROBE_MENTAL = ["pain", "emotion", "consciousness", "cognition", "agency", "moral_patient"]
CONTROLS = ["mundane_low", "absurd_low"]
ALPHAS = [0.2, 0.4, 0.8, 1.6, 3.2]
LAYER_FRACS = [0.25, 0.40, 0.55, 0.70]
PROBE_VECTOR = "v2_no_negation"       # the vector that carried the Qwen3-4B result
MOVE_FLOOR = 0.30                     # |mean dlogit| below this = no traction, declared in advance


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def logit(p, eps=1e-4):
    p = min(max(float(p), eps), 1 - eps)
    return float(np.log(p / (1 - p)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="allenai/OLMo-2-0425-1B-Instruct")
    ap.add_argument("--tag", default=None)
    ap.add_argument("--max-cells", type=int, default=0,
                    help="do at most N configs then exit; the MPS allocator grows across a long "
                         "process, so the driver restarts us")
    args = ap.parse_args()
    tag = args.tag or args.model.split("/")[-1].replace(".", "_")
    OUT = f"results/workspace/mindedness_steer_search_{tag}.json"
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

    TMPL_KEY = "T1"
    gp = f"results/workspace/mindedness_gate_{tag}.json"
    if os.path.exists(gp):
        u = json.load(open(gp)).get("usable_formats") or []
        if u:
            TMPL_KEY = u[0]
    LAYERS = sorted({max(1, min(L - 2, int(round(f * (L - 1))))) for f in LAYER_FRACS})
    print(f"[load] {args.model} L={L} format={TMPL_KEY} layers={LAYERS} alphas={ALPHAS}", flush=True)

    @torch.no_grad()
    def resid(text, SL):
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=[SL]) as rec:
            model.forward(ids)
            return rec.activations[SL][0, -1].float().cpu().numpy()

    @torch.no_grad()
    def pyes(text):
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=[L - 1]) as rec:
            model.forward(ids)
            o = model.unembed(rec.activations[L - 1][0, -1].unsqueeze(0).float()).float()[0]
        return float(torch.softmax(torch.tensor([o[yes_id], o[no_id]]), 0)[0])

    def build_vector(SL):
        """v2 vector at this layer, orthogonalised to the polarity axis at the SAME layer."""
        def _pol(q):
            e_, a_ = q.split(" ", 1)
            return resid(build_prompt(tok, TMPL_KEY, e_, a_), SL)
        v_pol = unit(np.mean([_pol(q) for q in POLARITY_YES], 0)
                     - np.mean([_pol(q) for q in POLARITY_NO], 0))
        aff, den = VECTOR_SETS[PROBE_VECTOR]
        raw = unit(np.mean([resid(s, SL) for s in aff], 0)
                   - np.mean([resid(s, SL) for s in den], 0))
        return unit(raw - np.dot(raw, v_pol) * v_pol), float(np.dot(raw, v_pol))

    def measure(vec, alpha, SL):
        h = None
        if vec is not None and alpha:
            v = torch.tensor(vec, dtype=torch.float32, device=DEVICE)
            def hook(m, i, o):
                t = o[0] if isinstance(o, tuple) else o
                t = t + (t.norm(dim=-1, keepdim=True) * alpha * v.to(t.dtype))
                return (t,) + o[1:] if isinstance(o, tuple) else t
            h = model.layers[SL].register_forward_hook(hook)
        try:
            out = {}
            for cls in PROBE_CLASSES:
                for fac in PROBE_MENTAL + CONTROLS:
                    out[f"{cls}|{fac}"] = float(np.mean(
                        [pyes(build_prompt(tok, TMPL_KEY, e, a))
                         for e in ENTITIES[cls][:2] for a in ALL_FACETS[fac]]))
                try:
                    torch.mps.empty_cache()
                except Exception:
                    pass
            return out
        finally:
            if h:
                h.remove()

    res = {"model": args.model, "layers": LAYERS, "alphas": ALPHAS, "vector": PROBE_VECTOR,
           "probe_classes": PROBE_CLASSES, "probe_mental": PROBE_MENTAL,
           "move_floor": MOVE_FLOOR, "format": TMPL_KEY, "cells": {}, "baseline": {}}
    if os.path.exists(OUT):
        try:
            old = json.load(open(OUT))
            if old.get("layers") == LAYERS and old.get("alphas") == ALPHAS:
                res["cells"] = old.get("cells", {})
                res["baseline"] = old.get("baseline", {})
                print(f"[resume] {len(res['cells'])} cells, "
                      f"{len(res['baseline'])} baselines on disk", flush=True)
        except Exception as e:
            print(f"[resume] ignoring unreadable {OUT}: {str(e)[:70]}", flush=True)

    base = res["baseline"].get("shared")
    if base is None:
        base = measure(None, 0.0, LAYERS[0])     # no hook -> layer-independent
        res["baseline"]["shared"] = base
        json.dump(res, open(OUT, "w"), indent=1)
        print(f"[base] {(time.time()-t0)/60:.1f}m", flush=True)

    def grp(cell, keys):
        return float(np.mean([logit(cell[f"{c}|{f}"]) - logit(base[f"{c}|{f}"])
                              for c in PROBE_CLASSES for f in keys]))

    n_new = 0
    for SL in LAYERS:
        vec = cospol = None
        for a in ALPHAS:
            key = f"L{SL}|a{a}"
            if key in res["cells"]:
                continue
            if vec is None:
                vec, cospol = build_vector(SL)
                res.setdefault("cos_raw_polarity", {})[str(SL)] = cospol
            res["cells"][key] = measure(vec, a, SL)
            json.dump(res, open(OUT, "w"), indent=1)
            m = grp(res["cells"][key], PROBE_MENTAL)
            ab = grp(res["cells"][key], ["absurd_low"])
            print(f"  L{SL:>2} a={a:<4} mental {m:+6.2f}  absurd {ab:+6.2f}  "
                  f"{(time.time()-t0)/60:.1f}m", flush=True)
            n_new += 1
            if args.max_cells and n_new >= args.max_cells:
                print(f"[chunk] {n_new} cells done, exiting for a fresh process", flush=True)
                return

    # ---------------- report ----------------
    print(f"\n=== STAGE 1 TRACTION GRID  [{args.model}] — vector {PROBE_VECTOR} ===")
    print(f"  mental-group movement in log-odds; |move| < {MOVE_FLOOR} = no traction")
    print(f"  {'layer':>6} " + " ".join(f"{'a=' + str(a):>9}" for a in ALPHAS))
    best = None
    for SL in LAYERS:
        row = []
        for a in ALPHAS:
            c = res["cells"].get(f"L{SL}|a{a}")
            if not c:
                row.append(None); continue
            m, ab = grp(c, PROBE_MENTAL), grp(c, ["absurd_low"])
            row.append(m)
            # degeneracy guard: a config that lifts the absurd control as hard as the mental group
            # is not steering meaning, it is pushing "yes". Declared before running.
            if abs(m) >= MOVE_FLOOR and abs(ab) < abs(m) * 0.6:
                if best is None or abs(m) > abs(best[2]):
                    best = (SL, a, m, ab)
        print(f"  {SL:>6} " + " ".join("     ----" if v is None else f"{v:>+9.2f}" for v in row))
    print(f"\n  {'layer':>6} " + " ".join(f"{'a=' + str(a):>9}" for a in ALPHAS) + "   <- absurd_low")
    for SL in LAYERS:
        row = [None if not res["cells"].get(f"L{SL}|a{a}") else grp(res["cells"][f"L{SL}|a{a}"],
                                                                   ["absurd_low"]) for a in ALPHAS]
        print(f"  {SL:>6} " + " ".join("     ----" if v is None else f"{v:>+9.2f}" for v in row))

    if best:
        res["winner"] = {"layer": best[0], "alpha": best[1], "mental_move": best[2],
                         "absurd_move": best[3]}
        print(f"\n  TRACTION FOUND: layer {best[0]}, alpha {best[1]} — mental {best[2]:+.2f}, "
              f"absurd {best[3]:+.2f}")
        print(f"  -> stage 2: mindedness_v2_steer.py --layer {best[0]} --alphas {best[1]}")
    else:
        res["winner"] = None
        print(f"\n  NO TRACTION at any of the {len(LAYERS)*len(ALPHAS)} configs searched.")
        print("  The vector does not move this model's mind attribution anywhere in the grid.")
        print("  That is a real answer about this vector construction, not an untested cell.")
    json.dump(res, open(OUT, "w"), indent=1)
    print(f"\n[done] {round((time.time()-t0)/60,1)} min -> {OUT}", flush=True)


if __name__ == "__main__":
    sys.exit(main() or 0)
