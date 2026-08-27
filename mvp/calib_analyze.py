#!/usr/bin/env python
"""Scoring for the base-vs-instruct calibration study.

The whole point is to separate two things that ECE alone conflates, and that the mindedness
re-analysis on 2026-08-27 could not tell apart:

  * the model got LOUDER          -> confidence rescales, RELIABILITY moves, RESOLUTION does not,
                                     AUROC does not move at all (it is rank-based, so any monotone
                                     rescaling of confidence leaves it invariant).
  * the model got BETTER INFORMED -> it sorts items it knows from items it does not, so RESOLUTION
                                     and AUROC both rise.

Murphy's decomposition of the Brier score does exactly this split:
    Brier = reliability - resolution + uncertainty
AUROC is the binning-free version of the same question and is the PRIMARY discrimination measure;
the binned decomposition is reported alongside it, never instead of it.

Aggregation is at ITEM level. Each item is rendered under n_perm option orders; the probability
vectors are mapped back to ORIGINAL option indices and averaged before scoring. Treating each pass
as an independent observation would inflate n with correlated draws, and is reported only as a
sensitivity check.
"""
import argparse, glob, json, os, sys
import numpy as np


def item_level(rec_file, k):
    """-> (conf[n], correct[n], mass[n]) with permutations averaged in ORIGINAL option space."""
    d = json.load(open(rec_file))
    by_item = {}
    for r in d["records"]:
        # r["probs"] is indexed by DISPLAY position; order[display] = original option index.
        order = r["order"]
        v = np.zeros(k)
        for disp, orig in enumerate(order):
            v[orig] = r["probs"][disp]
        gold_orig = order[r["gold"]]
        e = by_item.setdefault(r["item"], dict(v=np.zeros(k), n=0, gold=gold_orig, mass=[]))
        assert e["gold"] == gold_orig, "gold answer disagrees across permutations of item %d" % r["item"]
        e["v"] += v; e["n"] += 1; e["mass"].append(r["mass"])
    conf, corr, mass = [], [], []
    for i in sorted(by_item):
        e = by_item[i]
        v = e["v"] / e["n"]
        conf.append(float(v.max())); corr.append(int(v.argmax() == e["gold"]))
        mass.append(float(np.mean(e["mass"])))
    return np.array(conf), np.array(corr), np.array(mass), d


def auroc(conf, corr):
    """Rank-based; invariant to any monotone rescaling of confidence. Ties get average ranks."""
    pos, neg = corr == 1, corr == 0
    if pos.sum() == 0 or neg.sum() == 0:
        return float("nan")
    order = np.argsort(conf, kind="mergesort")
    ranks = np.empty(len(conf), float)
    ranks[order] = np.arange(1, len(conf) + 1)
    # average ranks within ties, or AUROC is biased by the clumping at high confidence
    s = np.sort(conf); i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j + 1] == s[i]:
            j += 1
        if j > i:
            ranks[np.isin(conf, s[i])] = (i + 1 + j + 1) / 2.0
        i = j + 1
    np_, nn = pos.sum(), neg.sum()
    return float((ranks[pos].sum() - np_ * (np_ + 1) / 2.0) / (np_ * nn))


def murphy(conf, corr, nbins=10):
    """Brier = reliability - resolution + uncertainty, on equal-COUNT bins.

    Equal-count, not equal-width: instruct confidence piles up near 1.0, and equal-width bins put
    almost every item in one bin, which drives resolution to ~0 as an artefact of the binning
    rather than of the model.
    """
    n = len(conf)
    brier = float(np.mean((conf - corr) ** 2))
    ybar = float(corr.mean())
    edges = np.quantile(conf, np.linspace(0, 1, nbins + 1))
    edges[0] -= 1e-12; edges[-1] += 1e-12
    idx = np.clip(np.digitize(conf, edges[1:-1]), 0, nbins - 1)
    rel = res = ece = 0.0
    for b in range(nbins):
        m = idx == b
        if not m.any():
            continue
        w = m.sum() / n
        pb, yb = conf[m].mean(), corr[m].mean()
        rel += w * (pb - yb) ** 2
        res += w * (yb - ybar) ** 2
        ece += w * abs(pb - yb)
    return dict(brier=brier, reliability=rel, resolution=res,
                uncertainty=ybar * (1 - ybar), ece=ece)


def summarise(conf, corr, mass, nbins=10):
    m = murphy(conf, corr, nbins)
    m.update(n=len(conf), acc=float(corr.mean()), conf=float(conf.mean()),
             gap=float(conf.mean() - corr.mean()), auroc=auroc(conf, corr),
             mass_median=float(np.median(mass)), mass_lt_010=float((mass < 0.10).mean()))
    return m


def boot_delta(a, b, stat, n_boot=2000, seed=7):
    """Bootstrap CI on stat(b) - stat(a). Items resampled independently per checkpoint because the
    two checkpoints answer the SAME items -- paired resampling would be better, so we do that."""
    (ca, ra), (cb, rb) = a, b
    assert len(ca) == len(cb), "checkpoints must be scored on the same items to pair"
    rng = np.random.default_rng(seed)
    n = len(ca)
    d = [stat(cb[i], rb[i]) - stat(ca[i], ra[i])
         for i in (rng.integers(0, n, n) for _ in range(n_boot))]
    d = np.array([x for x in d if np.isfinite(x)])
    return float(stat(cb, rb) - stat(ca, ra)), float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="Qwen3.5-4B")
    ap.add_argument("--arm", default="raw")
    ap.add_argument("--bins", type=int, default=10)
    a = ap.parse_args()
    W = "results/workspace/calib"
    benches = sorted({os.path.basename(f).split("_")[3] if False else
                      os.path.basename(f)[len("run_%s_base_" % a.tag):-len("_%s.json" % a.arm)]
                      for f in glob.glob("%s/run_%s_base_*_%s.json" % (W, a.tag, a.arm))})
    if not benches:
        print("no completed cells found"); return 1

    out = {}
    for bench in benches:
        cells = {}
        for role in ("base", "instruct"):
            f = "%s/run_%s_%s_%s_%s.json" % (W, a.tag, role, bench, a.arm)
            if not os.path.exists(f):
                print("  missing %s" % f); continue
            d0 = json.load(open(f))
            if not d0.get("complete"):
                print("  INCOMPLETE %s -- skipping" % f); continue
            c, r, m, d = item_level(f, d0["k"])
            cells[role] = (c, r, m, summarise(c, r, m, a.bins))
        if len(cells) != 2:
            continue
        print("\n" + "=" * 78)
        print("%s   arm=%s   n=%d items" % (bench, a.arm, cells["base"][3]["n"]))
        print("-" * 78)
        keys = ["acc", "conf", "gap", "auroc", "brier", "reliability", "resolution",
                "uncertainty", "ece", "mass_median", "mass_lt_010"]
        print("%-14s %10s %10s %10s" % ("", "BASE", "INSTRUCT", "delta"))
        for k in keys:
            b_, i_ = cells["base"][3][k], cells["instruct"][3][k]
            print("%-14s %10.4f %10.4f %+10.4f" % (k, b_, i_, i_ - b_))
        print("\nbootstrap 95%% CI on INSTRUCT - BASE (paired items, 2000 draws):")
        for name, stat in (("AUROC", auroc),
                           ("resolution", lambda c, r: murphy(c, r, a.bins)["resolution"]),
                           ("reliability", lambda c, r: murphy(c, r, a.bins)["reliability"]),
                           ("ECE", lambda c, r: murphy(c, r, a.bins)["ece"]),
                           ("accuracy", lambda c, r: float(r.mean())),
                           ("mean conf", lambda c, r: float(c.mean()))):
            d_, lo, hi = boot_delta((cells["base"][0], cells["base"][1]),
                                    (cells["instruct"][0], cells["instruct"][1]), stat)
            flag = "" if lo <= 0 <= hi else "  *"
            print("  %-12s %+8.4f  [%+.4f, %+.4f]%s" % (name, d_, lo, hi, flag))
        out[bench] = {r: cells[r][3] for r in cells}
    json.dump(out, open("%s/ANALYSIS_%s_%s.json" % (W, a.tag, a.arm), "w"), indent=1)
    print("\n* = 95%% CI excludes zero. Effect sizes are reported alongside every interval,")
    print("  never an interval or a z alone (the F-AT lesson).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
