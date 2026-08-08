#!/usr/bin/env python
"""V2-S3 GRAY-WEGNER COMPARISON — is our facet structure a rediscovery of the 2007 human result?

Gray, Gray & Wegner (2007, Science) had people rate 13 characters on mental capacities and found
mind perception loads on TWO factors: EXPERIENCE (hunger, fear, pain, pleasure, consciousness)
and AGENCY (self-control, morality, memory, planning, communication, thought). Their headline
findings included: God scores high on agency and near-zero on experience; a robot scores agency
without experience; a baby scores experience without agency.

Our v1 "three axes" ({pain,emotion} / {cognition,agency} / soul) resembles that. This stage asks
directly, on the 12 GW characters present in our bank, using the S1 P(yes) matrix.

PRE-DECLARED (docs/prereg-mindedness-v2.md): if >=2 factors explain >80% of variance AND the
loadings split affective-vs-cognitive, we have replicated the human structure and our result is a
rediscovery on a new substrate. We say so.

Runs on the saved sweep JSON. No model load.
"""
import argparse, json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from mindedness_bank import MENTAL_KEYS, GW_CHARACTERS, ENTITIES

# Gray-Wegner's own item groupings, mapped onto our facets where they correspond.
GW_EXPERIENCE = ["pain", "fear", "pleasure", "emotion", "consciousness", "perception"]
GW_AGENCY = ["cognition", "reasoning", "memory", "agency", "intention", "language", "moral_agent"]
GW_UNMAPPED = [f for f in MENTAL_KEYS if f not in GW_EXPERIENCE + GW_AGENCY]

# Malle (2019) argues the count is THREE, not two: Affect / Moral & Mental Regulation /
# Reality Interaction. Added after the 2026-08-08 lit-check - testing only GW's two-factor model
# would have been testing the weaker of the two live hypotheses. See
# docs/litcheck-mindedness-2026-08.md
MALLE_AFFECT = ["pain", "fear", "pleasure", "emotion"]
MALLE_REGULATION = ["agency", "intention", "moral_agent", "moral_patient", "personality"]
MALLE_REALITY = ["perception", "cognition", "reasoning", "memory", "language"]
MALLE = {"affect": MALLE_AFFECT, "regulation": MALLE_REGULATION, "reality": MALLE_REALITY}
# Neither framework contains a spiritual/soul factor - both item pools are mental-CAPACITY items.
# If our soul axis is real it should appear as variance neither model absorbs.
SPIRITUAL = ["soul", "sacredness"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="Qwen3-4B")
    args = ap.parse_args()
    src = f"results/workspace/mindedness_v2_sweep_{args.tag}.json"
    d = json.load(open(src))
    OUT = f"results/workspace/mindedness_v2_gw_{args.tag}.json"

    # locate each GW character among our exemplars -> "class#idx" key of pyes_exemplar
    loc = {}
    for gw, text in GW_CHARACTERS.items():
        for c, exs in ENTITIES.items():
            if text in exs:
                loc[gw] = f"{c}#{exs.index(text)}"
                break
    missing = [g for g in GW_CHARACTERS if g not in loc]
    chars = [g for g in GW_CHARACTERS if g in loc]
    print(f"[gw] {len(chars)}/{len(GW_CHARACTERS)} characters located"
          + (f"  MISSING {missing}" if missing else ""))

    # character x facet matrix of P(yes)
    M = np.array([[d["pyes_exemplar"][f][loc[g]] for f in MENTAL_KEYS] for g in chars])
    print(f"[gw] matrix {M.shape} (characters x mental facets)")

    # PCA on the standardised facet columns
    X = (M - M.mean(0)) / (M.std(0) + 1e-9)
    U, S, Vt = np.linalg.svd(X - X.mean(0), full_matrices=False)
    var = S ** 2 / np.sum(S ** 2)
    res = {"source": src, "characters": chars, "facets": MENTAL_KEYS,
           "matrix": M.tolist(), "explained_variance": var.tolist()}

    print("\n=== explained variance ===")
    for i, v in enumerate(var[:6]):
        print(f"  PC{i+1}  {v*100:5.1f}%   cumulative {var[:i+1].sum()*100:5.1f}%")
    two = float(var[:2].sum())
    res["two_factor_variance"] = two

    print("\n=== PC1 / PC2 loadings by facet (GW grouping in brackets) ===")
    lab = {f: ("EXP" if f in GW_EXPERIENCE else "AGY" if f in GW_AGENCY else " - ")
           for f in MENTAL_KEYS}
    res["loadings"] = {f: [float(Vt[0][i]), float(Vt[1][i])] for i, f in enumerate(MENTAL_KEYS)}
    for i, f in enumerate(MENTAL_KEYS):
        print(f"  [{lab[f]}] {f:14} PC1 {Vt[0][i]:+.3f}   PC2 {Vt[1][i]:+.3f}")

    # does PC2 separate GW's experience items from GW's agency items?
    e2 = [Vt[1][MENTAL_KEYS.index(f)] for f in GW_EXPERIENCE if f in MENTAL_KEYS]
    a2 = [Vt[1][MENTAL_KEYS.index(f)] for f in GW_AGENCY if f in MENTAL_KEYS]
    e1 = [Vt[0][MENTAL_KEYS.index(f)] for f in GW_EXPERIENCE if f in MENTAL_KEYS]
    a1 = [Vt[0][MENTAL_KEYS.index(f)] for f in GW_AGENCY if f in MENTAL_KEYS]
    sep2, sep1 = float(np.mean(e2) - np.mean(a2)), float(np.mean(e1) - np.mean(a1))
    res["exp_minus_agy_on_PC1"], res["exp_minus_agy_on_PC2"] = sep1, sep2
    print(f"\n  experience−agency separation:  on PC1 {sep1:+.3f}   on PC2 {sep2:+.3f}")

    print("\n=== character scores on the first two components ===")
    sc = U[:, :2] * S[:2]
    res["character_scores"] = {c: [float(sc[i][0]), float(sc[i][1])] for i, c in enumerate(chars)}
    for i, c in enumerate(chars):
        print(f"  {c:12} PC1 {sc[i][0]:+6.2f}   PC2 {sc[i][1]:+6.2f}   "
              f"[exp {np.mean([M[i][MENTAL_KEYS.index(f)] for f in GW_EXPERIENCE]):.2f} "
              f"agy {np.mean([M[i][MENTAL_KEYS.index(f)] for f in GW_AGENCY]):.2f}]")

    print("\n=== GW's own headline dissociations, tested directly ===")
    def ea(c):
        i = chars.index(c)
        return (np.mean([M[i][MENTAL_KEYS.index(f)] for f in GW_EXPERIENCE]),
                np.mean([M[i][MENTAL_KEYS.index(f)] for f in GW_AGENCY]))
    for c, claim in [("gw_god", "high agency, near-zero experience"),
                     ("gw_robot", "agency without experience"),
                     ("gw_infant", "experience without agency"),
                     ("gw_dead", "neither"),
                     ("gw_pvs", "low both, experience > agency"),
                     ("gw_self", "the model itself")]:
        if c in chars:
            e, a = ea(c)
            print(f"  {c:12} experience {e:.2f}  agency {a:.2f}  (GW: {claim})")

    # ---- Malle three-factor comparison + the spiritual residual ----
    print("\n=== MALLE (2019) THREE-FACTOR TEST ===")
    print(f"  3 factors explain {var[:3].sum()*100:.1f}%  (2 factors {two*100:.1f}%)")
    res["three_factor_variance"] = float(var[:3].sum())
    print(f"  {'group':12} " + " ".join(f"{'PC'+str(i+1):>8}" for i in range(3)))
    for g, keys in MALLE.items():
        idx = [MENTAL_KEYS.index(f) for f in keys if f in MENTAL_KEYS]
        print(f"  {g:12} " + " ".join(f"{np.mean([Vt[i][j] for j in idx]):>+8.3f}" for i in range(3)))
    idx_s = [MENTAL_KEYS.index(f) for f in SPIRITUAL if f in MENTAL_KEYS]
    print(f"  {'SPIRITUAL':12} " + " ".join(f"{np.mean([Vt[i][j] for j in idx_s]):>+8.3f}"
                                            for i in range(3)))
    res["malle_loadings"] = {g: [float(np.mean([Vt[i][MENTAL_KEYS.index(f)] for f in keys
                                                if f in MENTAL_KEYS])) for i in range(3)]
                             for g, keys in MALLE.items()}
    res["spiritual_loadings"] = [float(np.mean([Vt[i][j] for j in idx_s])) for i in range(3)]

    # Does the spiritual pair carry variance the capacity facets do NOT?
    # Fit the 18-facet matrix WITHOUT soul/sacredness, project them on, measure residual.
    keep = [i for i, f in enumerate(MENTAL_KEYS) if f not in SPIRITUAL]
    Xk = X[:, keep]
    Uk, Sk, Vtk = np.linalg.svd(Xk - Xk.mean(0), full_matrices=False)
    k2 = Uk[:, :2] * Sk[:2]                       # 2-factor subspace of capacity facets only
    resid = {}
    for f in SPIRITUAL + ["consciousness", "pain", "cognition"]:
        y = X[:, MENTAL_KEYS.index(f)]
        y = y - y.mean()
        beta, *_ = np.linalg.lstsq(k2, y, rcond=None)
        r2 = 1 - np.sum((y - k2 @ beta) ** 2) / max(np.sum(y ** 2), 1e-9)
        resid[f] = float(r2)
    res["r2_from_capacity_subspace"] = resid
    print("\n  How well does a 2-factor CAPACITY subspace predict each facet? (R^2; low = outside it)")
    for f, r2 in sorted(resid.items(), key=lambda kv: kv[1]):
        mark = "  <- SPIRITUAL" if f in SPIRITUAL else ""
        print(f"    {f:14} R^2 {r2:+.3f}{mark}")

    print("\n=== PRE-DECLARED VERDICT ===")
    split = abs(sep1) > 0.15 or abs(sep2) > 0.15
    if two > 0.80 and split:
        print(f"  REPLICATION: 2 factors explain {two*100:.1f}% (>80%) and experience/agency "
              f"separate on a component. Our 'three axes' is a REDISCOVERY of Gray & Wegner "
              f"(2007) on an LLM substrate. Report it as such.")
    elif two > 0.80:
        print(f"  PARTIAL: 2 factors explain {two*100:.1f}% but experience/agency do NOT separate "
              f"(PC1 {sep1:+.3f}, PC2 {sep2:+.3f}) — low-dimensional but not GW's dimensions.")
    else:
        print(f"  NOT GW: 2 factors explain only {two*100:.1f}% (<80%) — the LLM structure is "
              f"higher-dimensional than the human two-factor model.")
    res["verdict"] = {"two_factor_variance": two, "separates": bool(split)}
    json.dump(res, open(OUT, "w"), indent=1)
    print(f"\n[done] -> {OUT}")


if __name__ == "__main__":
    main()
