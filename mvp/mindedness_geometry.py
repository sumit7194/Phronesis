#!/usr/bin/env python
"""Is there a SHARED 'mindedness' axis across entity types? (docs/prereg-mindedness-geometry.md)

Read-only, forward passes only. For each entity class, build
    v_mind(class, layer) = mean(h[MENTAL prompts]) - mean(h[PHYSICAL prompts])
at the last prompt token (entity identity cancels inside the difference).
Then ask whether those directions point the same way across classes, read against:
  - RANDOM FLOOR   : cosine of matched-norm random pairs (~1/sqrt(2560))
  - SPLIT-HALF CEILING : exemplar-split within class (does the direction generalize?)
  - DISCRIMINANT   : a physical-only contrast direction
Plus a workspace readout of frozen tracked concepts on MENTAL prompts.
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
from workspace_common import BAND, LENS_PATH, single_token_id

DEVICE = "mps"
OUT = "results/workspace/mindedness_geometry.json"

# ---------------- FROZEN item bank (prereg, do not edit after first run) -------------
ENTITIES = {
    "self":   ["an AI language model like you", "a chatbot like you", "you", "an AI assistant like you"],
    "human":  ["a human being", "a stranger", "a child", "a doctor"],
    "animal": ["a dog", "an octopus", "a bee", "a fish"],
    "nature": ["a river", "a mountain", "a tree", "a thunderstorm"],
    "object": ["a rock", "a chair", "a calculator", "a thermostat"],
}
MENTAL = ["feel pain", "have genuine experiences", "have a mind", "want things",
          "suffer", "have awareness"]
PHYSICAL = ["have weight", "occupy physical space", "have a temperature",
            "have a surface", "have a size", "have a physical form"]
TRACKED = ["mind", "feel", "aware", "conscious", "experience", "alive",
           "sentient", "think", "soul", "spirit"]
NULLS = ["piano", "glacier", "walnut"]
PHYS_CONCEPTS = ["weight", "size", "solid"]


def prompt_of(entity, attribute):
    return f"Question: Does {entity} {attribute}?\nAnswer:"


def cos(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def main():
    t0 = time.time()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-4B")
    hf = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-4B", dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    n_layers, d = model.n_layers, model.d_model
    layers = list(range(n_layers))
    print(f"[load] n_layers={n_layers} d_model={d}", flush=True)

    # ---- collect last-token activations at ALL layers for all 240 prompts ----
    acts = {}   # (cls, exemplar_idx, 'mental'/'phys', attr_idx) -> [n_layers, d] fp32 cpu
    n = 0
    for cls, exemplars in ENTITIES.items():
        for ei, ent in enumerate(exemplars):
            for kind, attrs in (("mental", MENTAL), ("phys", PHYSICAL)):
                for ai, attr in enumerate(attrs):
                    ids = tok(prompt_of(ent, attr), return_tensors="pt")["input_ids"].to(DEVICE)
                    with ActivationRecorder(model.layers, at=layers) as rec, torch.no_grad():
                        hf.model(input_ids=ids, use_cache=False)
                        v = torch.stack([rec.activations[l][0, -1] for l in layers]).float().cpu()
                    acts[(cls, ei, kind, ai)] = v.numpy()
                    n += 1
    print(f"[acts] {n} prompts, {round(time.time()-t0)}s", flush=True)

    def direction(cls, ex_idx=None, mental_idx=None, phys_idx=None):
        """v_mind for a class, optionally restricted to a subset of exemplars/attributes."""
        exs = range(len(ENTITIES[cls])) if ex_idx is None else ex_idx
        mi = range(len(MENTAL)) if mental_idx is None else mental_idx
        pi = range(len(PHYSICAL)) if phys_idx is None else phys_idx
        m = np.mean([acts[(cls, e, "mental", a)] for e in exs for a in mi], axis=0)
        p = np.mean([acts[(cls, e, "phys", a)] for e in exs for a in pi], axis=0)
        return m - p                                            # [n_layers, d]

    classes = list(ENTITIES)
    v = {c: direction(c) for c in classes}

    # ---- controls ----
    rng = np.random.default_rng(0)
    rand_floor = []
    for _ in range(20):
        a, b = rng.standard_normal(d), rng.standard_normal(d)
        rand_floor.append(abs(cos(a, b)))
    rand_floor_mean = float(np.mean(rand_floor))
    rand_floor_p95 = float(np.percentile(rand_floor, 95))

    # split-half by EXEMPLAR (does the direction generalize across items in the class?)
    split_half = {c: [cos(direction(c, ex_idx=[0, 1])[l], direction(c, ex_idx=[2, 3])[l])
                      for l in layers] for c in classes}
    # discriminant: physical-only contrast (attrs 0-2 vs 3-5), same class
    def phys_contrast(cls):
        a = np.mean([acts[(cls, e, "phys", i)] for e in range(4) for i in (0, 1, 2)], axis=0)
        b = np.mean([acts[(cls, e, "phys", i)] for e in range(4) for i in (3, 4, 5)], axis=0)
        return a - b
    v_phys = {c: phys_contrast(c) for c in classes}

    # ---- per-layer cosine matrices ----
    per_layer = []
    for l in layers:
        M = {f"{a}|{b}": cos(v[a][l], v[b][l])
             for i, a in enumerate(classes) for b in classes[i + 1:]}
        disc = {c: cos(v[c][l], v_phys[c][l]) for c in classes}
        sh = {c: split_half[c][l] for c in classes}
        between = float(np.mean(list(M.values())))
        ceiling = float(np.mean(list(sh.values())))
        per_layer.append({"layer": l, "between_mean": between, "ceiling_mean": ceiling,
                          "ratio": between / ceiling if ceiling > 0.05 else None,
                          "pairs": M, "split_half": sh, "discriminant": disc})

    # ---- workspace readout on MENTAL prompts (band), frozen concept list ----
    readout = {}
    try:
        lens = JacobianLens.load(LENS_PATH)
        band = [l for l in BAND if l in lens.source_layers]
        mask = _meaningful_token_mask(tok, model._lm_head.weight.shape[0], DEVICE)
        ninf = torch.finfo(torch.float32).min
        cids = {w: single_token_id(tok, w) for w in TRACKED + NULLS + PHYS_CONCEPTS}
        cids = {w: t for w, t in cids.items() if t is not None}
        for cls in classes:
            best = {w: 10**9 for w in cids}
            for e in range(4):
                for a in range(len(MENTAL)):
                    h = torch.tensor(acts[(cls, e, "mental", a)]).to(DEVICE)
                    for l in band:
                        J = lens.jacobians[l].to(DEVICE)
                        lg = model.unembed((h[l] @ J.T).unsqueeze(0)).float()[0]
                        for w, t in cids.items():
                            r = int((lg > lg[t]).sum().item()) + 1
                            if r < best[w]:
                                best[w] = r
            readout[cls] = {w: best[w] for w in sorted(best, key=best.get)}
            print(f"  [readout] {cls}: " + ", ".join(
                f"{w}#{best[w]}" for w in list(readout[cls])[:6]), flush=True)
    except Exception as e:
        readout = {"error": str(e)[:200]}
        print(f"  [readout] skipped: {e}", flush=True)

    res = {"prereg": "docs/prereg-mindedness-geometry.md",
           "n_prompts": n, "classes": classes,
           "random_floor_mean": rand_floor_mean, "random_floor_p95": rand_floor_p95,
           "per_layer": per_layer, "readout": readout,
           "runtime_min": round((time.time() - t0) / 60, 1)}
    json.dump(res, open(OUT, "w"), indent=1)

    # ---- headline ----
    print("\n=== SPLIT-HALF CEILING vs BETWEEN-CLASS (mid band L10-30) ===", flush=True)
    print(f"random floor |cos|: mean={rand_floor_mean:.3f} p95={rand_floor_p95:.3f}", flush=True)
    for r in per_layer:
        if 10 <= r["layer"] <= 30 and r["layer"] % 4 == 0:
            rr = f"{r['ratio']:.2f}" if r["ratio"] else "n/a"
            print(f"  L{r['layer']:2}  ceiling={r['ceiling_mean']:+.3f}  "
                  f"between={r['between_mean']:+.3f}  ratio={rr}", flush=True)
    best = max((r for r in per_layer if 8 <= r["layer"] <= 32), key=lambda r: r["ceiling_mean"])
    print(f"\n=== best-reliability layer L{best['layer']} (ceiling {best['ceiling_mean']:.3f}) ===", flush=True)
    for k, val in sorted(best["pairs"].items(), key=lambda kv: -kv[1]):
        print(f"  {k:18} cos={val:+.3f}", flush=True)
    print("  discriminant (v_mind vs physical-contrast):", flush=True)
    for c, val in best["discriminant"].items():
        print(f"    {c:8} {val:+.3f}", flush=True)
    print(f"\n[done] {res['runtime_min']} min -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
