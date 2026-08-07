#!/usr/bin/env python
"""Decode the mindedness DIRECTIONS through the J-lens — what do they actually mean?

The geometry says self's v_mind points somewhere different from animal/nature/object's.
It cannot say WHAT differs. This decodes each direction into vocabulary:

  A. decode v_mind_clean(class)            -> "the mindedness axis points at these words"
  B. decode (v_self - v_animal) etc.       -> "what makes SELF's version distinctive"
  C. random-direction control               -> the garbage floor
  D. J-lens vs logit lens side by side      -> our QC found J~=logit at 4B; verify here too

Qwen3-4B only (the fitted lens is model-specific). Directions = template-averaged +
polarity-orthogonalised, identical construction to mindedness_clean.py.
Masked to word-like tokens (punctuation-domination lesson).
"""
import json, os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from jlens.lens import JacobianLens
from jlens.vis import _meaningful_token_mask
from workspace_common import BAND, LENS_PATH
from mindedness_geometry import ENTITIES, MENTAL, PHYSICAL
from mindedness_validate import TEMPLATES, POLARITY_YES, POLARITY_NO

DEVICE, MODEL = "mps", "Qwen/Qwen3-4B"
OUT = "results/workspace/mindedness_decode_Qwen3-4B.json"
TOPK = 12


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def main():
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(MODEL)
    hf = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    lens = JacobianLens.load(LENS_PATH)
    L = model.n_layers
    layers = list(range(L))
    band = [l for l in BAND if l in lens.source_layers]
    mask = _meaningful_token_mask(tok, model._lm_head.weight.shape[0], DEVICE)
    ninf = torch.finfo(torch.float32).min
    print(f"[load] {MODEL} L={L}; lens n={lens.n_prompts}; decode band={band}", flush=True)

    @torch.no_grad()
    def acts_of(text):
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=layers) as rec:
            model.forward(ids)
            return torch.stack([rec.activations[l][0, -1] for l in layers]).float().cpu().numpy()

    # ---- rebuild clean directions (same construction as mindedness_clean.py) ----
    A = {}
    for tn, tmpl in TEMPLATES.items():
        for cls, exs in ENTITIES.items():
            for ei, e in enumerate(exs):
                for kind, attrs in (("mental", MENTAL), ("phys", PHYSICAL)):
                    for ai, a in enumerate(attrs):
                        A[(tn, cls, ei, kind, ai)] = acts_of(tmpl.format(e=e, a=a))
    pol = []
    for tn, tmpl in TEMPLATES.items():
        w = tmpl.split("{e}")[0]
        y = np.mean([acts_of(f"{w}{q}?\nAnswer:") for q in POLARITY_YES], 0)
        n_ = np.mean([acts_of(f"{w}{q}?\nAnswer:") for q in POLARITY_NO], 0)
        pol.append(np.stack([unit(x) for x in (y - n_)]))
    v_pol = np.mean(pol, 0)

    def vmind(cls):
        v = np.mean([np.stack([unit(x) for x in (
            np.mean([A[(tn, cls, e, "mental", a)] for e in range(4) for a in range(6)], 0)
            - np.mean([A[(tn, cls, e, "phys", a)] for e in range(4) for a in range(6)], 0))])
            for tn in TEMPLATES], 0)
        return np.stack([v[l] - np.dot(v[l], unit(v_pol[l])) * unit(v_pol[l]) for l in layers])

    classes = list(ENTITIES)
    V = {c: vmind(c) for c in classes}
    print(f"[dirs] built {round(time.time()-t0)}s", flush=True)

    # ---- decoding ----
    @torch.no_grad()
    def decode(vec_layers, use_jacobian=True, k=TOPK):
        """aggregate top tokens across the band for a [L,d] direction."""
        score = None
        for l in band:
            v = torch.tensor(vec_layers[l], dtype=torch.float32, device=DEVICE)
            if use_jacobian:
                v = v @ lens.jacobians[l].to(DEVICE).T
            lg = model.unembed(v.unsqueeze(0)).float()[0]
            valid = lg[mask]                                   # stats over word-like tokens ONLY
            z = (lg - valid.mean()) / (valid.std() + 1e-6)     # per-layer z so layers combine fairly
            z = z.masked_fill(~mask, ninf)                     # mask AFTER normalising (else nan)
            score = z if score is None else score + z
        top = score.topk(k)
        return [(tok.decode([int(i)]).strip(), round(float(s) / len(band), 2))
                for i, s in zip(top.indices, top.values)]

    res = {"model": MODEL, "lens_n": lens.n_prompts, "band": band}
    res["A_direction_jlens"] = {c: decode(V[c], True) for c in classes}
    res["A_direction_logit"] = {c: decode(V[c], False) for c in classes}
    # B: what makes self distinctive vs each other class
    res["B_self_minus"] = {c: decode(np.stack([V["self"][l] - V[c][l] for l in layers]), True)
                           for c in classes if c != "self"}
    res["B_minus_self"] = {c: decode(np.stack([V[c][l] - V["self"][l] for l in layers]), True)
                           for c in classes if c != "self"}
    # C: random floor
    rng = np.random.default_rng(0)
    res["C_random"] = [decode(np.stack([rng.standard_normal(model.d_model) for _ in layers]), True)
                       for _ in range(2)]
    json.dump(res, open(OUT, "w"), indent=1)

    print("\n=== A. what the mindedness axis points at (J-lens, band-aggregated) ===")
    for c in classes:
        print(f"  {c:8} " + ", ".join(w for w, _ in res["A_direction_jlens"][c]))
    print("\n=== A'. same via LOGIT lens (QC: J~=logit at 4B — do they agree?) ===")
    for c in classes:
        print(f"  {c:8} " + ", ".join(w for w, _ in res["A_direction_logit"][c]))
    print("\n=== B. SELF minus other  (what is distinctive about self's mindedness) ===")
    for c, d in res["B_self_minus"].items():
        print(f"  self−{c:7} " + ", ".join(w for w, _ in d))
    print("\n=== B'. other minus SELF (what self LACKS) ===")
    for c, d in res["B_minus_self"].items():
        print(f"  {c:7}−self " + ", ".join(w for w, _ in d))
    print("\n=== C. random-direction floor (should be incoherent) ===")
    for r in res["C_random"]:
        print("  " + ", ".join(w for w, _ in r))
    print(f"\n[done] {round((time.time()-t0)/60,1)} min -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
