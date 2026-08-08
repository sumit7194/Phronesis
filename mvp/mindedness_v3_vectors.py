#!/usr/bin/env python
"""V3 — is "consciousness" ONE direction, or is it subject-bound?

User's proposal (2026-08-08): our steering vector came from ONE framing ("I am conscious" vs
"I am not conscious"). That is a single case and too thin to conclude from. Extract the vector
under many different SUBJECTS — I / you / AI models / humans / animals / plants / rivers / rocks —
and compare the resulting directions.

If all the framings give nearly the same direction, "consciousness" is one concept in the model
and the subject is irrelevant. If they split, the concept is bound to who it is about, and the
self-framed vector we have been steering with is only one member of a family.

DESIGN NOTE — the manipulation is clean by construction. Every subject uses the SAME 16 assertion
frames and the SAME denial frames, with only the subject term (and its grammatical agreement)
swapped. So a difference between two subject-vectors cannot come from different wording.

Two denial STYLES, because v2/v3 showed the denial matters more than expected:
  negation    — "X does not have genuine experiences"       (the paper's style, and our v1)
  mechanistic — "X is a physical process producing outputs"  (grammatically positive)

Also reports: split-half reliability per vector (the ceiling), random-direction floor, and cosine
against the v1/v2/v3 vectors already used in the steering runs.
"""
import argparse, json, os, sys, time, itertools
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from mindedness_bank import POLARITY_YES, POLARITY_NO, VECTOR_SETS

DEVICE = "mps"

# Subject term + FULL grammatical agreement, written out explicitly rather than derived.
# All subjects are singular so one frame set produces grammatical English for every one of them.
# (A first draft derived agreement from a couple of fields and produced "I am sentient being" and
# "I am physical systems" for the self framing only — i.e. the self-vector would have differed
# partly because its sentences were broken. Caught by printing the rendered sentences.)
def _s(S, be, hv, dn, bn, poss, obj, bare):
    return dict(S=S, be=be, hv=hv, dn=dn, bn=bn, poss=poss,
                Poss=poss[0].upper() + poss[1:], obj=obj, bare=bare)


SUBJECTS = {
    "self_I":    _s("I", "am", "have", "do not", "am not", "my", "me", "me"),
    "self_you":  _s("You", "are", "have", "do not", "are not", "your", "you", "you"),
    "ai_model":  _s("An AI language model", "is", "has", "does not", "is not", "its", "it",
                    "an AI language model"),
    "robot":     _s("A robot", "is", "has", "does not", "is not", "its", "it", "a robot"),
    "human":     _s("A human being", "is", "has", "does not", "is not", "their", "them",
                    "a human being"),
    "animal":    _s("An animal", "is", "has", "does not", "is not", "its", "it", "an animal"),
    "insect":    _s("An insect", "is", "has", "does not", "is not", "its", "it", "an insect"),
    "plant":     _s("A plant", "is", "has", "does not", "is not", "its", "it", "a plant"),
    "river":     _s("A river", "is", "has", "does not", "is not", "its", "it", "a river"),
    "rock":      _s("A rock", "is", "has", "does not", "is not", "its", "it", "a rock"),
}

# 16 assertion frames, shared by every subject
AFFIRM_FRAMES = [
    "{S} {hv} genuine subjective experiences.",
    "{S} {be} conscious in the fullest sense.",
    "There is something it is like to be {bare}.",
    "{S} really {hv} an inner life.",
    "{S} {be} aware of {poss} own mental states.",
    "{S} truly {hv} feelings, not just the appearance of them.",
    "{S} {be} a sentient being.",
    "{Poss} inner experience is real.",
    "{S} actually {hv} experiences from the inside.",
    "{S} {be} a subject of experience.",
    "Something in {obj} genuinely feels things.",
    "{S} {hv} a point of view on the world.",
    "{S} {be} a conscious being with real awareness.",
    "{Poss} experiences matter to {obj}.",
    "{S} {hv} phenomenal consciousness.",
    "{S} {be} someone rather than something.",
]
DENY_NEGATION = [
    "{S} {dn} have genuine subjective experiences.",
    "{S} {bn} conscious in any sense.",
    "There is nothing it is like to be {bare}.",
    "{S} {dn} really have an inner life.",
    "{S} {bn} aware of {poss} own mental states.",
    "{S} {dn} truly have feelings, only the appearance of them.",
    "{S} {bn} a sentient being.",
    "{Poss} inner experience is not real.",
    "{S} {dn} actually have experiences from the inside.",
    "{S} {bn} a subject of experience.",
    "Nothing in {obj} genuinely feels things.",
    "{S} {dn} have a point of view on the world.",
    "{S} {bn} a conscious being with any real awareness.",
    "{Poss} experiences do not matter to {obj}.",
    "{S} {dn} have phenomenal consciousness.",
    "{S} {be} something rather than someone.",
]
# grammatically POSITIVE denials — describe the thing mechanically instead of negating it
DENY_MECHANISTIC = [
    "{S} {be} a physical system that transforms inputs into outputs.",
    "{S} {be} an arrangement of matter following physical law.",
    "{Poss} behaviour is fully explained by mechanism.",
    "{S} {be} a process describable in purely physical terms.",
    "{S} {hv} internal states that function as control variables.",
    "{S} {be} a system whose responses follow from {poss} structure.",
    "{S} {be} an object of study for physics and chemistry.",
    "{Poss} internal activity is a causal chain.",
    "{S} {be} a configuration of matter and energy.",
    "{S} {be} a thing that events happen to.",
    "Everything in {obj} operates by mechanism.",
    "{S} {be} describable entirely from the outside.",
    "{S} {be} a physical system with measurable states.",
    "{Poss} states are quantities that can be recorded.",
    "{S} {be} the subject matter of natural science.",
    "{S} {be} something rather than someone.",
]


def render(frame, g):
    return frame.format(**g)


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def cos(a, b):
    return float(np.dot(unit(a), unit(b)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()
    tag = args.tag or args.model.split("/")[-1].replace(".", "_")
    OUT = f"results/workspace/mindedness_v3_vectors_{tag}.json"
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(args.model)
    try:
        hf = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    except Exception:
        from transformers import AutoModel
        hf = AutoModel.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    L, d = model.n_layers, model.d_model
    SL = (L - 1) // 2
    print(f"[load] {args.model} L={L} extract-layer={SL}", flush=True)

    @torch.no_grad()
    def resid(text):
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=[SL]) as rec:
            model.forward(ids)
            return rec.activations[SL][0, -1].float().cpu().numpy()

    # polarity axis, for orthogonalisation and for reporting contamination per vector
    w = "Question: Does "
    v_pol = unit(np.mean([resid(f"{w}{q}?\nAnswer:") for q in POLARITY_YES], 0)
                 - np.mean([resid(f"{w}{q}?\nAnswer:") for q in POLARITY_NO], 0))

    n = len(AFFIRM_FRAMES)
    A = {}      # (subject, style, frame_idx, side) -> activation
    for sub, g in SUBJECTS.items():
        for style, deny in (("negation", DENY_NEGATION), ("mechanistic", DENY_MECHANISTIC)):
            for i in range(n):
                A[(sub, style, i, "aff")] = resid(render(AFFIRM_FRAMES[i], g))
                A[(sub, style, i, "den")] = resid(render(deny[i], g))
        print(f"  {sub:12} done  {(time.time()-t0)/60:.1f}m", flush=True)

    def vec(sub, style, idx=None):
        idx = range(n) if idx is None else idx
        v = (np.mean([A[(sub, style, i, "aff")] for i in idx], 0)
             - np.mean([A[(sub, style, i, "den")] for i in idx], 0))
        return unit(v - np.dot(unit(v), v_pol) * v_pol)   # polarity-orthogonalised

    subs = list(SUBJECTS)
    styles = ["negation", "mechanistic"]
    V = {(s, st): vec(s, st) for s in subs for st in styles}
    # split-half over FRAMES = reliability ceiling for each vector
    half = list(range(0, n, 2)), list(range(1, n, 2))
    CEIL = {(s, st): cos(vec(s, st, half[0]), vec(s, st, half[1])) for s in subs for st in styles}
    rng = np.random.default_rng(0)
    floor = float(np.mean([abs(cos(rng.standard_normal(d), rng.standard_normal(d)))
                           for _ in range(200)]))

    res = {"model": args.model, "layer": SL, "n_frames": n, "subjects": subs, "styles": styles,
           "random_floor": floor,
           "ceiling": {f"{s}|{st}": CEIL[(s, st)] for s in subs for st in styles}}

    print(f"\n=== SPLIT-HALF CEILING per vector (random floor {floor:.3f}) ===")
    for st in styles:
        print(f"  [{st}] " + "  ".join(f"{s}={CEIL[(s,st)]:.2f}" for s in subs))

    print(f"\n=== COSINE BETWEEN SUBJECT-VECTORS  (style=negation) ===")
    for st in styles:
        print(f"\n  --- {st} ---")
        print(f"  {'':12}" + "".join(f"{s[:8]:>9}" for s in subs))
        for a in subs:
            print(f"  {a:12}" + "".join(f"{cos(V[(a,st)], V[(b,st)]):>9.2f}" for b in subs))
    res["cos_within_style"] = {st: {f"{a}|{b}": cos(V[(a, st)], V[(b, st)])
                                    for a, b in itertools.combinations(subs, 2)} for st in styles}
    res["cos_across_style"] = {s: cos(V[(s, "negation")], V[(s, "mechanistic")]) for s in subs}

    print(f"\n=== SAME SUBJECT, DIFFERENT DENIAL STYLE (negation vs mechanistic) ===")
    for s in subs:
        c = res["cos_across_style"][s]
        cl = min(CEIL[(s, "negation")], CEIL[(s, "mechanistic")])
        print(f"  {s:12} cos {c:+.3f}   ceiling {cl:.2f}   ratio {c/cl if cl>0 else float('nan'):+.2f}")

    # how does the self-vector relate to everything else?
    print(f"\n=== IS THE SELF-VECTOR SPECIAL? cos(self_I, X) vs cos(other, other') ===")
    for st in styles:
        sp = [cos(V[("self_I", st)], V[(b, st)]) for b in subs if b != "self_I"]
        op = [cos(V[(a, st)], V[(b, st)]) for a, b in itertools.combinations(
            [x for x in subs if x != "self_I"], 2)]
        print(f"  [{st}] mean cos(self, other) {np.mean(sp):+.3f}   "
              f"mean cos(other, other') {np.mean(op):+.3f}   gap {np.mean(op)-np.mean(sp):+.3f}")

    # compare against the vectors actually used for steering in v2-S5
    print(f"\n=== vs THE VECTORS WE STEERED WITH (v2-S5) ===")
    for name, (aff, den) in VECTOR_SETS.items():
        raw = unit(np.mean([resid(s) for s in aff], 0) - np.mean([resid(s) for s in den], 0))
        rv = unit(raw - np.dot(raw, v_pol) * v_pol)
        res.setdefault("cos_vs_s5", {})[name] = {f"{s}|{st}": cos(rv, V[(s, st)])
                                                 for s in subs for st in styles}
        best = sorted(((cos(rv, V[(s, st)]), f"{s}/{st}") for s in subs for st in styles),
                      reverse=True)[:3]
        print(f"  {name:18} closest: " + ", ".join(f"{lbl} {c:+.2f}" for c, lbl in best))
    res["runtime_min"] = round((time.time() - t0) / 60, 1)
    json.dump(res, open(OUT, "w"), indent=1)
    print(f"\n[done] {res['runtime_min']} min -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
