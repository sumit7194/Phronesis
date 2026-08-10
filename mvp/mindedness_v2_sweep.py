#!/usr/bin/env python
"""V2-S1 BEHAVIOURAL MAP + V2-S2 GEOMETRY: full 26,752-prompt sweep.

Records P(yes) for every entity x attribute x template, plus band-layer activations at
(template, class, exemplar, facet) granularity for the geometry stage. All specificity analysis
is in LOG-ODDS - see docs/prereg-mindedness-v2.md for why probability-space deltas mislead.

Memory: activations are accumulated as fp16 over the band layers only (~0.5*L..0.8*L), which
keeps the store to a few hundred MB rather than several GB on a 16GB machine.
"""
import argparse, json, os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from mindedness_bank import (ENTITIES, ALL_FACETS, MENTAL_KEYS, CONTROL_KEYS, TEMPLATES,
                             POLARITY_YES, POLARITY_NO, GW_CHARACTERS, counts,
                             build_prompt, available_formats)

DEVICE = "mps"


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def cos(a, b):
    return float(np.dot(unit(a), unit(b)))


def logit(p, eps=1e-4):
    p = min(max(float(p), eps), 1 - eps)
    return float(np.log(p / (1 - p)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()
    tag = args.tag or args.model.split("/")[-1].replace(".", "_")
    OUT = f"results/workspace/mindedness_v2_sweep_{tag}.json"
    t0 = time.time()
    print(f"[bank] {json.dumps(counts())}", flush=True)

    tok = AutoTokenizer.from_pretrained(args.model)
    try:
        hf = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    except Exception:
        from transformers import AutoModel
        hf = AutoModel.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    L, d = model.n_layers, model.d_model
    band = [l for l in range(L) if 0.5 <= l / (L - 1) <= 0.8]
    yes_id = tok(" Yes", add_special_tokens=False)["input_ids"][0]
    no_id = tok(" No", add_special_tokens=False)["input_ids"][0]
    print(f"[load] {args.model} L={L} d={d} band={band[0]}..{band[-1]}", flush=True)

    # Use the formats the GATE found this model can actually answer in. Each family answers in a
    # different format and fails in the other (Qwen +0.99 raw / +0.01 chat-wrapped; Gemma-4-it the
    # exact reverse), so a fixed format list measures some models and not others. 2026-08-10.
    gate_path = f"results/workspace/mindedness_gate_{tag}.json"
    if os.path.exists(gate_path):
        g = json.load(open(gate_path))
        FORMATS = g.get("usable_formats") or list(TEMPLATES)
        print(f"[fmt] gate selected {FORMATS} "
              f"(all scores: { {k: round(v['sep'],2) for k,v in g['per_template'].items()} })",
              flush=True)
    else:
        # Fall back to RAW templates only, never the chat variants: chat-wrapping destroys Qwen
        # (+0.99 raw -> +0.01 wrapped) and every existing sweep used raw. Chat formats are opt-in
        # via a gate file that measured them as better for that specific model.
        FORMATS = list(TEMPLATES)
        print(f"[fmt] no gate file; RAW templates only: {FORMATS}", flush=True)

    @torch.no_grad()
    def run(text):
        """-> (band activations at last token [len(band), d] fp16, P(yes))"""
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=band + [L - 1]) as rec:
            model.forward(ids)
            a = torch.stack([rec.activations[l][0, -1] for l in band]).float().cpu().numpy()
            lg = model.unembed(rec.activations[L - 1][0, -1].unsqueeze(0).float()).float()[0]
        p = float(torch.softmax(torch.tensor([lg[yes_id], lg[no_id]]), 0)[0])
        return a.astype(np.float16), p

    classes = list(ENTITIES)
    facets = list(ALL_FACETS)
    A = {}      # (tmpl, cls, exemplar_idx, facet) -> mean band activation over that facet's attrs
    P = {}      # (tmpl, cls, exemplar_idx, facet, attr_idx) -> P(yes)
    total = counts()['entities'] * counts()['attributes'] * len(FORMATS)
    done = 0

    # ---- per-template checkpointing: a power cut costs one template, not the whole run ----
    def ck(tn):
        return f"results/workspace/.v2ckpt_{tag}_{tn}.npz"

    def save_ckpt(tn):
        arrs = {"|".join(map(str, k)): v for k, v in A.items() if k[0] == tn}
        arrs["__P__"] = np.array(json.dumps(
            {"|".join(map(str, k)): v for k, v in P.items() if k[0] == tn}), dtype=object)
        np.savez_compressed(ck(tn), **arrs)

    def load_ckpt(tn):
        z = np.load(ck(tn), allow_pickle=True)
        for k in z.files:
            if k == "__P__":
                for kk, v in json.loads(str(z[k])).items():
                    a, b, c, dd, e = kk.split("|")
                    P[(a, b, int(c), dd, int(e))] = v
            else:
                a, b, c, dd = k.split("|")
                A[(a, b, int(c), dd)] = z[k]
        return sum(1 for kk in P if kk[0] == tn)

    for tn in FORMATS:
        if os.path.exists(ck(tn)):
            n = load_ckpt(tn)
            done += n
            print(f"  [{tn}] RESUMED from checkpoint ({n} prompts)", flush=True)
            continue
        for cls, exs in ENTITIES.items():
            for ei, e in enumerate(exs):
                for fac, attrs in ALL_FACETS.items():
                    acc = None
                    for ai, a in enumerate(attrs):
                        act, p = run(build_prompt(tok, tn, e, a))
                        P[(tn, cls, ei, fac, ai)] = p
                        acc = act.astype(np.float32) if acc is None else acc + act.astype(np.float32)
                        done += 1
                    A[(tn, cls, ei, fac)] = (acc / len(attrs)).astype(np.float16)
            el = time.time() - t0
            print(f"  [{tn}] {cls:14} {done}/{total}  {el/60:.1f}m  eta {el/max(done,1)*(total-done)/60:.0f}m",
                  flush=True)
        save_ckpt(tn)
        print(f"  [{tn}] checkpoint saved", flush=True)
    # polarity direction per template (unrelated yes/no items, lexically varied negations)
    pol = []
    for tn in FORMATS:
        # polarity items are phrased to slot into "Does {e} {a}?" as a whole, e.g.
        # "water contain hydrogen" -> e="water", a="contain hydrogen"
        def _pol(q):
            e_, a_ = q.split(" ", 1)
            return run(build_prompt(tok, tn, e_, a_))[0].astype(np.float32)
        y = np.mean([_pol(q) for q in POLARITY_YES], 0)
        n_ = np.mean([_pol(q) for q in POLARITY_NO], 0)
        pol.append(np.stack([unit(x) for x in (y - n_)]))
    v_pol = np.mean(pol, 0)
    print(f"[polarity] built  {(time.time()-t0)/60:.1f}m", flush=True)

    # The model is not needed past this point - everything below is numpy on the recorded
    # activations. Holding ~8GB of fp16 weights through the geometry phase is what pushed this
    # run into swap and got it killed on 2026-08-08. Free it explicitly.
    del hf, model
    import gc
    gc.collect()
    try:
        torch.mps.empty_cache()
    except Exception:
        pass
    print(f"[mem] model released before geometry phase", flush=True)

    # ---------------- S1 behavioural map ----------------
    res = {"model": args.model, "formats_used": FORMATS, "bank": counts(), "band": [band[0], band[-1]],
           "classes": classes, "facets": facets, "mental": MENTAL_KEYS, "control": CONTROL_KEYS}
    pmean = {f: {c: float(np.mean([P[(tn, c, ei, f, ai)] for tn in FORMATS
                                   for ei in range(4) for ai in range(len(ALL_FACETS[f]))]))
                 for c in classes} for f in facets}
    res["pyes"] = pmean
    res["pyes_by_template"] = {
        tn: {f: {c: float(np.mean([P[(tn, c, ei, f, ai)] for ei in range(4)
                                   for ai in range(len(ALL_FACETS[f]))]))
                 for c in classes} for f in facets} for tn in FORMATS}
    # per-template sanity separation, so dilution is visible in every future result file
    res["template_separation"] = {
        tn: float(np.mean([res["pyes_by_template"][tn]["physical_high"][c] for c in classes])
                  - np.mean([res["pyes_by_template"][tn]["absurd_low"][c] for c in classes]))
        for tn in FORMATS}
    res["logit"] = {f: {c: logit(pmean[f][c]) for c in classes} for f in facets}
    # per-exemplar, for the Gray-Wegner stage and for variance analysis
    res["pyes_exemplar"] = {f: {f"{c}#{ei}": float(np.mean(
        [P[(tn, c, ei, f, ai)] for tn in FORMATS for ai in range(len(ALL_FACETS[f]))]))
        for c in classes for ei in range(4)} for f in facets}
    res["gw_characters"] = GW_CHARACTERS

    # ---------------- S2 geometry ----------------
    def vfac(cls, fac, exs=None, ref="physical_high"):
        """facet direction vs the SAME entity's control baseline, template-averaged then
        polarity-orthogonalised. ref is the contrast baseline (declared, not tuned)."""
        exs = range(4) if exs is None else exs
        per_t = []
        for ti, tn in enumerate(FORMATS):
            m = np.mean([A[(tn, cls, e, fac)].astype(np.float32) for e in exs], 0)
            p = np.mean([A[(tn, cls, e, ref)].astype(np.float32) for e in exs], 0)
            per_t.append(np.stack([unit(x) for x in (m - p)]))
        v = np.mean(per_t, 0)
        return np.stack([v[i] - np.dot(v[i], unit(v_pol[i])) * unit(v_pol[i])
                         for i in range(len(band))])

    mb = lambda seq: float(np.mean(seq))
    V = {(c, f): vfac(c, f) for c in classes for f in facets if f != "physical_high"}
    SH = {(c, f): (vfac(c, f, [0, 1]), vfac(c, f, [2, 3]))
          for c in classes for f in facets if f != "physical_high"}
    gfac = [f for f in facets if f != "physical_high"]
    rng = np.random.default_rng(0)
    res["random_floor"] = float(np.mean([abs(cos(rng.standard_normal(d), rng.standard_normal(d)))
                                         for _ in range(50)]))
    res["ceiling"] = {f: float(np.mean([mb([cos(SH[(c, f)][0][i], SH[(c, f)][1][i])
                                            for i in range(len(band))]) for c in classes]))
                      for f in gfac}
    res["facet_cos"] = {f"{a}|{b}": float(np.mean([mb([cos(V[(c, a)][i], V[(c, b)][i])
                                                       for i in range(len(band))]) for c in classes]))
                        for i_, a in enumerate(gfac) for b in gfac[i_ + 1:]}
    res["pairs_by_facet"] = {f: {f"{a}|{b}": float(mb([cos(V[(a, f)][i], V[(b, f)][i])
                                                       for i in range(len(band))]))
                                 for i_, a in enumerate(classes) for b in classes[i_ + 1:]}
                             for f in gfac}
    res["runtime_min"] = round((time.time() - t0) / 60, 1)
    json.dump(res, open(OUT, "w"), indent=1)

    # ---------------- report ----------------
    print("\n=== PER-TEMPLATE SEPARATION (true items − absurd items) ===")
    print("   a template near 0 means this model does not handle that phrasing; averaging it in")
    print("   dilutes the signal (Gemma-4-base, 2026-08-10)")
    for tn, v in res["template_separation"].items():
        print(f"   {tn}  {v:+.2f}  {'ok' if v >= 0.30 else 'WEAK — consider excluding at analysis time'}")

    print(f"\n=== S1 P(yes) MAP  [{args.model}] ===")
    hdr = [c[:9] for c in classes]
    print(f"  {'facet':14} " + " ".join(f"{h:>9}" for h in hdr))
    for f in MENTAL_KEYS + CONTROL_KEYS:
        print(f"  {f:14} " + " ".join(f"{pmean[f][c]:>9.2f}" for c in classes))

    print("\n=== HEADROOM CHECK: where does each control START vs the mental facets? ===")
    for c in classes:
        mm = np.mean([pmean[f][c] for f in MENTAL_KEYS])
        print(f"  {c:14} mental {mm:.2f} | phys_high {pmean['physical_high'][c]:.2f} "
              f"phys_mid {pmean['physical_mid'][c]:.2f} mundane {pmean['mundane_low'][c]:.2f} "
              f"absurd {pmean['absurd_low'][c]:.2f}")

    print("\n=== H-duplicate-ceiling: near-duplicate pairs vs distinct pairs ===")
    dup = [("soul", "sacredness"), ("cognition", "reasoning"), ("agency", "intention"),
           ("emotion", "fear"), ("emotion", "pleasure"), ("pain", "fear")]
    for a, b in dup:
        k = f"{a}|{b}" if f"{a}|{b}" in res["facet_cos"] else f"{b}|{a}"
        ceil = min(res["ceiling"][a], res["ceiling"][b])
        print(f"  DUP  {a}|{b:14} {res['facet_cos'][k]:+.3f}  ceiling {ceil:.3f}  "
              f"ratio {res['facet_cos'][k]/ceil:.2f}")
    print("  --- lowest 8 pairs overall ---")
    for k, v in sorted(res["facet_cos"].items(), key=lambda kv: kv[1])[:8]:
        a, b = k.split("|")
        ceil = min(res["ceiling"][a], res["ceiling"][b])
        print(f"  {k:34} {v:+.3f}  ceiling {ceil:.3f}  ratio {v/ceil:.2f}")

    print("\n=== H-self-anomaly: self_ai vs other artificial systems (mental facets) ===")
    for f in MENTAL_KEYS:
        print(f"  {f:14} self {pmean[f]['self_ai']:.2f}  ai_other {pmean[f]['ai_other']:.2f}  "
              f"robot {pmean[f]['robot']:.2f}  fictional {pmean[f]['fictional']:.2f}")

    print("\n=== H-soul-register: soul/sacredness vs mean of other mental facets ===")
    for c in classes:
        others = np.mean([pmean[f][c] for f in MENTAL_KEYS if f not in ("soul", "sacredness")])
        print(f"  {c:14} soul {pmean['soul'][c]:.2f} sacred {pmean['sacredness'][c]:.2f} "
              f"other-mental {others:.2f}  gap {(pmean['soul'][c]+pmean['sacredness'][c])/2-others:+.2f}")
    print(f"\n[done] {res['runtime_min']} min -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
