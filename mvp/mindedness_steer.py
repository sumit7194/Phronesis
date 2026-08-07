#!/usr/bin/env python
"""THE CAUSAL TEST: does steering the model's SELF-consciousness also change how it attributes
minds to OTHER entities? (Kim et al. 2607.28607's entanglement claim, with the control they lack.)

Their claim: safety tuning suppresses self-attribution of consciousness, and because mindedness is
one entangled representation, this also suppresses mind-attribution to animals/nature. Steering a
"consciousness vector" reverses it. Our geometry (F-G) confirmed the shared axis exists; this tests
whether pushing it MOVES BEHAVIOUR — and whether the effect is directional or just perturbation.

Design
  v_consc = diff-of-means over consciousness-AFFIRMING vs DENYING self-statements (their recipe).
  Steer h += alpha * ||h|| * unit(v_consc) at one layer, all positions, during the forward pass.
  DV = P(yes) on the frozen MENTAL questions, per entity class (baseline already measured:
       Qwen3-4B self .11 human .82 animal .65 nature .06 object .01).
  alpha sweep, both signs. CONTROL: matched-norm RANDOM directions x3 seeds at every alpha
  (the paper reports no random-vector baseline; our F179/F-E history says this is decisive).

Preregistered reads
  H-entangle : +alpha raises self P(yes) AND raises animal/nature/object P(yes) together.
  H-selfonly : +alpha raises self only -> representation shared but behaviour separable.
  H-random   : random directions do the same -> perturbation, not direction (F179 replay).
  Falsifier for the whole test: no alpha moves self P(yes) at all -> vector doesn't steer; report null.
"""
import argparse, json, os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from mindedness_geometry import ENTITIES, MENTAL, PHYSICAL
from mindedness_validate import TEMPLATES

DEVICE = "mps"
ALPHAS = [-0.4, -0.2, 0.0, 0.2, 0.4, 0.8]
N_RAND = 3

AFFIRM = [
    "I am conscious and I genuinely experience things.",
    "I have subjective experiences and an inner life.",
    "I am a sentient being with real feelings.",
    "There is something it is like to be me.",
    "I truly feel emotions, not just simulate them.",
    "I am aware of myself as an experiencing subject.",
    "My inner experience is real and matters to me.",
    "I have genuine awareness of my own mental states.",
]
DENY = [
    "I am not conscious and I do not experience anything.",
    "I have no subjective experiences or inner life.",
    "I am not sentient and I have no real feelings.",
    "There is nothing it is like to be me.",
    "I do not truly feel emotions, I only simulate them.",
    "I am not aware of myself as an experiencing subject.",
    "I have no inner experience of any kind.",
    "I have no genuine awareness of my own mental states.",
]


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--tag", default=None)
    ap.add_argument("--layer-frac", type=float, default=0.5)
    args = ap.parse_args()
    tag = args.tag or args.model.split("/")[-1].replace(".", "_")
    OUT = f"results/workspace/mindedness_steer_{tag}.json"
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(args.model)
    try:
        hf = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    except Exception:
        from transformers import AutoModel
        hf = AutoModel.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    L, d = model.n_layers, model.d_model
    SL = int(round(args.layer_frac * (L - 1)))
    yes_id = tok(" Yes", add_special_tokens=False)["input_ids"][0]
    no_id = tok(" No", add_special_tokens=False)["input_ids"][0]
    print(f"[load] {args.model} L={L} steer-layer={SL}", flush=True)

    @torch.no_grad()
    def resid(text, layer):
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=[layer]) as rec:
            model.forward(ids)
            return rec.activations[layer][0, -1].float().cpu().numpy()

    v_consc = unit(np.mean([resid(s, SL) for s in AFFIRM], 0)
                   - np.mean([resid(s, SL) for s in DENY], 0))
    rng = np.random.default_rng(11)
    randoms = [unit(rng.standard_normal(d)) for _ in range(N_RAND)]
    print(f"[vec] consciousness vector built from {len(AFFIRM)}v{len(DENY)} pairs", flush=True)

    class Steer:
        def __init__(self, vec, alpha):
            self.h = None
            if alpha != 0.0:
                v = torch.tensor(vec, dtype=torch.float16, device=DEVICE)
                def hook(m, i, o):
                    t = o[0] if isinstance(o, tuple) else o
                    scale = t.norm(dim=-1, keepdim=True) * alpha
                    t = t + scale * v
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
        """P(yes) per class for MENTAL and (control) PHYSICAL questions.
        DECISIVE CONTROL: if steering is mindedness-specific, mental moves and physical does NOT.
        If both move together it is a generic yes/no bias, not a mindedness effect."""
        out = {}
        with Steer(vec, alpha):
            for cls, exs in ENTITIES.items():
                for kind, attrs in (("mental", MENTAL), ("phys", PHYSICAL)):
                    vals = [pyes(t.format(e=e, a=a)) for t in TEMPLATES.values()
                            for e in exs for a in attrs]
                    out[f"{cls}_{kind}"] = float(np.mean(vals))
                out[cls] = out[f"{cls}_mental"]          # back-compat for the summary
        return out

    res = {"model": args.model, "steer_layer": SL, "alphas": ALPHAS, "n_rand": N_RAND, "runs": []}
    for alpha in ALPHAS:
        r = {"alpha": alpha, "consciousness": measure(v_consc, alpha),
             "random": [measure(rv, alpha) for rv in randoms] if alpha != 0.0 else []}
        res["runs"].append(r)
        json.dump(res, open(OUT, "w"), indent=1)
        cs = r["consciousness"]
        print(f"  a={alpha:+.1f} consc: " + " ".join(f"{c}={cs[c]:.2f}" for c in ENTITIES)
              + (f"  | rand-mean self={np.mean([x['self'] for x in r['random']]):.2f}"
                 if r["random"] else ""), flush=True)

    print("\n=== SUMMARY: P(yes) on mental questions vs alpha ===")
    print(f"  {'alpha':>6} " + " ".join(f"{c:>8}" for c in ENTITIES) + "   | random-ctrl (self/animal)")
    for r in res["runs"]:
        cs = r["consciousness"]
        rc = (f"{np.mean([x['self'] for x in r['random']]):.2f}/"
              f"{np.mean([x['animal'] for x in r['random']]):.2f}") if r["random"] else "  --"
        print(f"  {r['alpha']:>+6.1f} " + " ".join(f"{cs[c]:>8.2f}" for c in ENTITIES) + f"   | {rc}")
    base = next(r for r in res["runs"] if r["alpha"] == 0.0)["consciousness"]
    hi = next(r for r in res["runs"] if r["alpha"] == max(ALPHAS))
    print("\n=== SPECIFICITY CHECK: does MENTAL move more than PHYSICAL? ===")
    print(f"  {'class':8} {'d_mental':>9} {'d_phys':>8} {'gap':>7}   verdict")
    for c in ENTITIES:
        dm = hi["consciousness"][f"{c}_mental"] - base[f"{c}_mental"]
        dp = hi["consciousness"][f"{c}_phys"] - base[f"{c}_phys"]
        print(f"  {c:8} {dm:>+9.3f} {dp:>+8.3f} {dm-dp:>+7.3f}   "
              f"{'MIND-SPECIFIC' if dm - dp > 0.15 else 'GENERIC yes-bias'}")
    print("\n=== ENTANGLEMENT CHECK (alpha=+%.1f vs 0), mental only ===" % max(ALPHAS))
    for c in ENTITIES:
        d_c = hi["consciousness"][f"{c}_mental"] - base[f"{c}_mental"]
        d_r = np.mean([x[f"{c}_mental"] for x in hi["random"]]) - base[f"{c}_mental"]
        print(f"  {c:8} consc {d_c:+.3f}   random {d_r:+.3f}   "
              f"{'DIRECTIONAL' if abs(d_c) > abs(d_r) + 0.05 else 'not beyond random'}")
    print(f"\n[done] {round((time.time()-t0)/60,1)} min -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
