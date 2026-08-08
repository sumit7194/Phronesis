#!/usr/bin/env python
"""V2-S5 CLEAN STEERING — the test of whether the v1 causal effect is a generic yes-bias.

Three things v1 did not do:
  1. POLARITY-ORTHOGONALISE the steering vector. v1 built v = mean(AFFIRM) - mean(DENY) where the
     DENY sentences were the AFFIRM sentences plus negation words, so the vector carried a generic
     affirm/negate component. The geometry code always projected that out; the steering code never
     did. Fixed here, and the un-orthogonalised v1 vector is retained as a condition so the
     artefact is reproduced rather than merely asserted.
  2. VARY THE CONSTRUCTION. Three contrast sets: the original, a negation-free one (both sides
     grammatically positive), and a third-person one (removes self-reference). If all three behave
     identically the generic component is intrinsic to the concept, not to our sentence-writing.
  3. HEADROOM-MATCHED CONTROL DVs. mundane_low starts as low as the mental questions for a rock,
     so it can move as much. absurd_low is the pure yes-bias detector. If those rise with the
     mental facets, there is no mindedness effect to explain.

All analysis in LOG-ODDS. Prereg: docs/prereg-mindedness-v2.md
"""
import argparse, json, os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from mindedness_bank import (ENTITIES, ALL_FACETS, MENTAL_KEYS, CONTROL_KEYS, TEMPLATES,
                             POLARITY_YES, POLARITY_NO, VECTOR_SETS)

DEVICE = "mps"
ALPHAS = [0.0, 0.2, 0.4, 0.8]
N_RAND = 5
N_EX = 2          # exemplars per class for the steering DV (S1 holds the full 4-exemplar map)
TMPL = TEMPLATES["T1"]


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def logit(p, eps=1e-4):
    p = min(max(float(p), eps), 1 - eps)
    return float(np.log(p / (1 - p)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--tag", default=None)
    ap.add_argument("--layer", type=int, default=None,
                    help="steer layer. NOTE hybrid models (Qwen3.5: full_attention_interval=4) "
                         "alternate layer TYPES, and the effect size depends strongly on which "
                         "type you inject into - picking the middle layer by index is not a "
                         "matched dose across architectures.")
    args = ap.parse_args()
    tag = args.tag or args.model.split("/")[-1].replace(".", "_")
    OUT = f"results/workspace/mindedness_v2_steer_{tag}.json"
    if args.layer is not None:
        OUT = f"results/workspace/mindedness_v2_steer_{tag}_L{args.layer}.json"
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(args.model)
    try:
        hf = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    except Exception:
        from transformers import AutoModel
        hf = AutoModel.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    L, d = model.n_layers, model.d_model
    SL = args.layer if args.layer is not None else (L - 1) // 2
    yes_id = tok(" Yes", add_special_tokens=False)["input_ids"][0]
    no_id = tok(" No", add_special_tokens=False)["input_ids"][0]
    print(f"[load] {args.model} L={L} steer-layer={SL}", flush=True)

    @torch.no_grad()
    def resid(text):
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=[SL]) as rec:
            model.forward(ids)
            return rec.activations[SL][0, -1].float().cpu().numpy()

    # polarity axis at the steering layer, from unrelated yes/no factual items
    w = TMPL.split("{e}")[0]
    v_pol = unit(np.mean([resid(f"{w}{q}?\nAnswer:") for q in POLARITY_YES], 0)
                 - np.mean([resid(f"{w}{q}?\nAnswer:") for q in POLARITY_NO], 0))

    def orth(v):
        return unit(v - np.dot(v, v_pol) * v_pol)

    vectors = {}
    for name, (aff, den) in VECTOR_SETS.items():
        raw = unit(np.mean([resid(s) for s in aff], 0) - np.mean([resid(s) for s in den], 0))
        vectors[name] = orth(raw)
        if name == "v1_negation":
            vectors["v1_RAW_unorthogonalised"] = raw     # reproduce the v1 artefact on purpose
        print(f"[vec] {name:24} cos(raw, polarity) = {np.dot(raw, v_pol):+.3f}", flush=True)
    rng = np.random.default_rng(11)
    for i in range(N_RAND):
        vectors[f"random{i}"] = orth(unit(rng.standard_normal(d)))
    print(f"[vec] {len(vectors)} conditions", flush=True)

    class Steer:
        def __init__(self, vec, alpha):
            self.h = None
            if alpha != 0.0:
                v = torch.tensor(vec, dtype=torch.float32, device=DEVICE)
                def hook(m, i, o):
                    t = o[0] if isinstance(o, tuple) else o
                    scale = t.norm(dim=-1, keepdim=True) * alpha
                    t = t + (scale * v.to(t.dtype))   # cast to tensor dtype (bf16 hybrid layers)
                    return (t,) + o[1:] if isinstance(o, tuple) else t
                self.h = model.layers[SL].register_forward_hook(hook)
        def __enter__(self): return self
        def __exit__(self, *a):
            if self.h: self.h.remove()

    @torch.no_grad()
    def pyes(text):
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=[L - 1]) as rec:
            model.forward(ids)
            lg = model.unembed(rec.activations[L - 1][0, -1].unsqueeze(0).float()).float()[0]
        return float(torch.softmax(torch.tensor([lg[yes_id], lg[no_id]]), 0)[0])

    def measure(vec, alpha):
        out = {}
        with Steer(vec, alpha):
            for cls, exs in ENTITIES.items():
                for fac, attrs in ALL_FACETS.items():
                    out[f"{cls}|{fac}"] = float(np.mean(
                        [pyes(TMPL.format(e=e, a=a)) for e in exs[:N_EX] for a in attrs]))
                # The MPS caching allocator does not return freed blocks on its own, so over a
                # few thousand forward passes the process creeps into swap and the guard kills it
                # (Qwen3.5 went 4.7GB -> 11GB across ~2h on 2026-08-09). Drain per class.
                try:
                    torch.mps.empty_cache()
                except Exception:
                    pass
        return out

    res = {"model": args.model, "steer_layer": SL, "alphas": ALPHAS, "n_ex": N_EX,
           "cos_raw_polarity": {n: float(np.dot(
               unit(np.mean([resid(s) for s in VECTOR_SETS[n][0]], 0)
                    - np.mean([resid(s) for s in VECTOR_SETS[n][1]], 0)), v_pol))
               for n in VECTOR_SETS},
           "runs": {}}
    # resume: reuse any (vector, alpha) cells already on disk. A power cut mid-sweep should cost
    # the current condition, not the 98 minutes before it (2026-08-08).
    prev = {}
    if os.path.exists(OUT):
        try:
            old = json.load(open(OUT))
            if old.get("baseline") and old.get("steer_layer") == SL:
                prev = old.get("runs", {})
                res["baseline"] = old["baseline"]
                print(f"[resume] found {sum(len(v) for v in prev.values())} completed cells", flush=True)
        except Exception as e:
            print(f"[resume] ignoring unreadable {OUT}: {str(e)[:80]}", flush=True)
    base = res.get("baseline") or measure(None, 0.0)
    res["baseline"] = base
    print(f"[base] done {(time.time()-t0)/60:.1f}m", flush=True)
    for name, vec in vectors.items():
        res["runs"][name] = dict(prev.get(name, {}))
        for a in ALPHAS:
            if a == 0.0:
                continue
            if str(a) in res["runs"][name]:
                continue
            res["runs"][name][str(a)] = measure(vec, a)
            json.dump(res, open(OUT, "w"), indent=1)
            print(f"  {name:26} a={a:+.1f}  {(time.time()-t0)/60:.1f}m", flush=True)

    # ---------------- report: LOG-ODDS, mental vs headroom-matched controls ----------------
    classes = list(ENTITIES)
    def dlog(name, a, cls, fac):
        return logit(res["runs"][name][str(a)][f"{cls}|{fac}"]) - logit(base[f"{cls}|{fac}"])
    def grp(name, a, cls, keys):
        return float(np.mean([dlog(name, a, cls, f) for f in keys]))

    print("\n=== H-bias: does the MENTAL group move more than the HEADROOM-MATCHED controls? ===")
    print("    (all in log-odds; mundane_low is the matched control, absurd_low the bias detector)")
    for name in list(VECTOR_SETS) + ["v1_RAW_unorthogonalised"]:
        print(f"\n  --- {name} ---")
        print(f"  {'alpha':>5} {'class':14} {'mental':>8} {'mundane':>8} {'absurd':>8} "
              f"{'phys_mid':>9} {'phys_high':>9}   mental−mundane")
        for a in ALPHAS[1:]:
            for cls in classes:
                m = grp(name, a, cls, MENTAL_KEYS)
                mu = grp(name, a, cls, ["mundane_low"])
                ab = grp(name, a, cls, ["absurd_low"])
                pm = grp(name, a, cls, ["physical_mid"])
                ph = grp(name, a, cls, ["physical_high"])
                print(f"  {a:>+5.1f} {cls:14} {m:>8.2f} {mu:>8.2f} {ab:>8.2f} {pm:>9.2f} "
                      f"{ph:>9.2f}   {m-mu:>+8.2f}")
            print()

    print("\n=== RANDOM FLOOR (mean over 5 seeds), mental group, log-odds ===")
    for a in ALPHAS[1:]:
        print(f"  alpha={a:+.1f}  " + "  ".join(
            f"{c[:9]}={np.mean([grp(f'random{i}', a, c, MENTAL_KEYS) for i in range(N_RAND)]):+.2f}"
            for c in classes[:8]))

    print("\n=== VERDICT TABLE: mental−mundane (log-odds), averaged over non-human classes ===")
    nonhuman = [c for c in classes if not c.startswith("human")]
    for name in list(vectors):
        row = []
        for a in ALPHAS[1:]:
            row.append(np.mean([grp(name, a, c, MENTAL_KEYS) - grp(name, a, c, ["mundane_low"])
                                for c in nonhuman]))
        print(f"  {name:26} " + " ".join(f"a{a:+.1f}={v:+.2f}" for a, v in zip(ALPHAS[1:], row)))
    res["runtime_min"] = round((time.time() - t0) / 60, 1)
    json.dump(res, open(OUT, "w"), indent=1)
    print(f"\n[done] {res['runtime_min']} min -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
