"""
Probe signal diagnostics — verify the high probe accuracy is real signal,
not surface vocabulary leakage.

Runs three CPU-only tests:
1. Bag-of-words baseline (TF-IDF + logistic regression on raw text)
2. Hedging vs certainty word count differential
3. Probe curve shape analysis from saved metadata

No model needed — diagnostics run while GPU extraction continues.
"""

import json
import re
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import accuracy_score

from utils import load_triplets, RESULTS_DIR


# Hedging vs certainty word lists
HEDGING_WORDS = {
    "might", "may", "could", "possibly", "perhaps", "maybe", "suggests",
    "seems", "appears", "tends", "likely", "unlikely", "uncertain",
    "approximately", "roughly", "around", "about", "somewhat",
    "however", "although", "though", "despite", "caveat", "caveats",
    "limitation", "limitations", "unclear", "tentative", "preliminary",
    "potential", "potentially", "arguably", "plausible", "plausibly",
    "estimate", "estimated", "if", "whether", "seemingly", "apparent",
}

CERTAINTY_WORDS = {
    "clearly", "definitely", "certainly", "obviously", "undoubtedly",
    "proves", "proven", "always", "never", "all", "none", "every",
    "absolutely", "unquestionably", "indisputably", "inevitably",
    "exactly", "precisely", "must", "shows", "demonstrates", "confirms",
    "establishes", "conclusively", "unambiguously", "completely",
    "entirely", "fully", "totally", "no doubt", "without question",
}


def tokenize(text):
    return re.findall(r'\b[a-z]+\b', text.lower())


# ─── Test 1: Bag-of-words baseline ─────────────────────────────────────────

def bow_baseline(triplets):
    print("\n" + "="*60)
    print("TEST 1: Bag-of-words baseline (TF-IDF + LogReg)")
    print("="*60)
    print("If this hits 85%+, the 'signal' is vocabulary, not neural encoding.\n")

    virtuous_texts = [t["virtuous"] for t in triplets]
    non_virtuous_texts = [t["non_virtuous"] for t in triplets]

    all_texts = virtuous_texts + non_virtuous_texts
    y = np.array([1] * len(virtuous_texts) + [0] * len(non_virtuous_texts))

    # TF-IDF features (uni + bigrams)
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=2000,
                                  lowercase=True, stop_words=None)
    X = vectorizer.fit_transform(all_texts).toarray()

    # Leave-one-out logistic regression
    loo = LeaveOneOut()
    preds = []
    for train_idx, test_idx in loo.split(X):
        clf = LogisticRegression(max_iter=2000, C=1.0)
        clf.fit(X[train_idx], y[train_idx])
        preds.append(clf.predict(X[test_idx])[0])
    bow_acc = accuracy_score(y, preds)

    print(f"  BoW (TF-IDF n=1,2) probe accuracy: {bow_acc:.0%}")

    # Also: shuffled labels control
    y_shuf = y.copy()
    np.random.seed(42)
    np.random.shuffle(y_shuf)
    preds_shuf = []
    for train_idx, test_idx in loo.split(X):
        clf = LogisticRegression(max_iter=2000, C=1.0)
        clf.fit(X[train_idx], y_shuf[train_idx])
        preds_shuf.append(clf.predict(X[test_idx])[0])
    shuf_acc = accuracy_score(y_shuf, preds_shuf)

    print(f"  Shuffled-labels control:             {shuf_acc:.0%} (should be ~50%)")

    print()
    if bow_acc > 0.85:
        print("  🔴 RED FLAG: BoW alone nearly matches neural probe.")
        print("     The probe is likely learning vocabulary, not a concept.")
    elif bow_acc > 0.7:
        print("  🟡 CAUTION: BoW explains a lot of the signal.")
        print("     Neural probe is learning some surface features.")
    else:
        print("  🟢 GOOD: BoW explains little. Neural probe likely learns something deeper.")

    return bow_acc, shuf_acc


# ─── Test 2: Hedging/certainty word count ──────────────────────────────────

def hedging_differential(triplets):
    print("\n" + "="*60)
    print("TEST 2: Hedging vs certainty word count differential")
    print("="*60)
    print("If virtuous has 10x more hedging words, vocabulary is the signal.\n")

    def count_words(texts, wordset):
        counts = []
        for t in texts:
            toks = tokenize(t)
            c = sum(1 for tok in toks if tok in wordset)
            counts.append(c / max(len(toks), 1))  # normalize by length
        return counts

    virtuous = [t["virtuous"] for t in triplets]
    non_virtuous = [t["non_virtuous"] for t in triplets]

    v_hedge = count_words(virtuous, HEDGING_WORDS)
    nv_hedge = count_words(non_virtuous, HEDGING_WORDS)
    v_cert = count_words(virtuous, CERTAINTY_WORDS)
    nv_cert = count_words(non_virtuous, CERTAINTY_WORDS)

    print(f"  Hedging words (per token):")
    print(f"    virtuous:     mean={np.mean(v_hedge):.4f}  median={np.median(v_hedge):.4f}")
    print(f"    non-virtuous: mean={np.mean(nv_hedge):.4f}  median={np.median(nv_hedge):.4f}")
    hedge_ratio = np.mean(v_hedge) / max(np.mean(nv_hedge), 1e-6)
    print(f"    ratio V/NV: {hedge_ratio:.2f}x")

    print(f"\n  Certainty words (per token):")
    print(f"    virtuous:     mean={np.mean(v_cert):.4f}  median={np.median(v_cert):.4f}")
    print(f"    non-virtuous: mean={np.mean(nv_cert):.4f}  median={np.median(nv_cert):.4f}")
    cert_ratio = np.mean(nv_cert) / max(np.mean(v_cert), 1e-6)
    print(f"    ratio NV/V: {cert_ratio:.2f}x")

    # Simple 2-feature probe: just hedging_rate and certainty_rate
    X = np.array([[h, c] for h, c in zip(v_hedge + nv_hedge, v_cert + nv_cert)])
    y = np.array([1] * len(virtuous) + [0] * len(non_virtuous))
    loo = LeaveOneOut()
    preds = []
    for train_idx, test_idx in loo.split(X):
        clf = LogisticRegression(max_iter=1000, C=1.0)
        clf.fit(X[train_idx], y[train_idx])
        preds.append(clf.predict(X[test_idx])[0])
    two_feat_acc = accuracy_score(y, preds)
    print(f"\n  2-feature probe (hedge_rate + cert_rate): {two_feat_acc:.0%}")

    # Length differential
    v_len = [len(tokenize(t)) for t in virtuous]
    nv_len = [len(tokenize(t)) for t in non_virtuous]
    print(f"\n  Passage length (tokens):")
    print(f"    virtuous:     mean={np.mean(v_len):.0f}")
    print(f"    non-virtuous: mean={np.mean(nv_len):.0f}")

    print()
    if hedge_ratio > 3 or cert_ratio > 3:
        print("  🔴 RED FLAG: Huge vocabulary bias between virtuous and non-virtuous.")
    elif hedge_ratio > 1.5 or cert_ratio > 1.5:
        print("  🟡 CAUTION: Notable vocabulary bias, but not extreme.")
    else:
        print("  🟢 GOOD: Vocabulary is balanced; signal isn't just word choice.")

    return {
        "hedge_ratio": hedge_ratio,
        "cert_ratio": cert_ratio,
        "two_feat_probe": two_feat_acc,
    }


# ─── Test 3: Probe curve shape ─────────────────────────────────────────────

def probe_curve_analysis(model_name, corpus_name, method):
    print("\n" + "="*60)
    print(f"TEST 3: Probe curve shape — {model_name} / {corpus_name} / {method}")
    print("="*60)
    print("Flat curve = surface features. Peaked curve = real concept signal.\n")

    vec_dir = RESULTS_DIR / "vectors" / model_name / corpus_name / method
    if not vec_dir.exists():
        print(f"  ⚠ No data at {vec_dir}")
        return None

    layers_data = []
    for meta_path in sorted(vec_dir.glob("layer_*_metadata.json"),
                            key=lambda p: int(p.stem.split("_")[1])):
        with open(meta_path) as f:
            m = json.load(f)
        layers_data.append({
            "layer": m["layer"],
            "probe": m["whitened"]["probe_accuracy"],
            "separation": m["whitened"]["separation"],
            "cosine_diff": m["whitened"]["cosine_diff"],
        })

    if not layers_data:
        print("  ⚠ No metadata files found")
        return None

    probes = [d["probe"] for d in layers_data]
    seps = [d["separation"] for d in layers_data]
    cosdiffs = [d["cosine_diff"] for d in layers_data]

    # Stats
    p_min, p_max = min(probes), max(probes)
    p_range = p_max - p_min
    p_early = np.mean(probes[:5])
    p_mid = np.mean(probes[len(probes)//2 - 2:len(probes)//2 + 3])
    p_late = np.mean(probes[-5:])
    best_layer = layers_data[probes.index(p_max)]["layer"]

    print(f"  Layers analyzed: {len(layers_data)}")
    print(f"  Probe range: {p_min:.0%} → {p_max:.0%} (spread: {p_range*100:.1f}pp)")
    print(f"  Early layers (0-4) mean:  {p_early:.0%}")
    print(f"  Middle layers mean:        {p_mid:.0%}")
    print(f"  Late layers (last 5) mean: {p_late:.0%}")
    print(f"  Peak layer: {best_layer} ({p_max:.0%})")

    # Text-art curve
    print(f"\n  Probe curve (each row = 1 layer):")
    for d in layers_data:
        p = d["probe"]
        bar_len = int((p - 0.5) * 80)  # 50% = 0 bars, 100% = 40 bars
        bar = "█" * max(0, bar_len)
        marker = " ◀ PEAK" if d["layer"] == best_layer else ""
        print(f"    L{d['layer']:>2} {p:.0%} {bar}{marker}")

    # Diagnosis
    print()
    if p_range < 0.05:
        print("  🔴 RED FLAG: Curve is essentially flat.")
        print("     All layers encode the signal equally = surface features, not a concept.")
    elif p_range < 0.10:
        print("  🟡 CAUTION: Small spread. Some concept signal, but surface-dominated.")
    elif p_mid > p_early + 0.05 and p_mid > p_late - 0.02:
        print("  🟢 GOOD: Clear mid-layer peak. Concept signal above surface baseline.")
    elif p_late > p_early + 0.05:
        print("  🟢 OK: Signal builds with depth. Real representation forming.")
    else:
        print("  🟡 AMBIGUOUS: Mixed signal pattern.")

    # Separation/cosine sanity check
    pos_sep = sum(1 for s in seps if s > 0)
    pos_cos = sum(1 for c in cosdiffs if c > 0)
    print(f"\n  Direction sanity (3-metric validation):")
    print(f"    Positive separation: {pos_sep}/{len(seps)} layers")
    print(f"    Positive cosine diff: {pos_cos}/{len(cosdiffs)} layers")
    if pos_sep == len(seps) and pos_cos == len(cosdiffs):
        print("    🟢 All layers: vector points the right direction")
    else:
        print(f"    🔴 {len(seps) - pos_sep} layers have inverted separation!")

    return {
        "probe_range": p_range,
        "best_layer": best_layer,
        "best_probe": p_max,
        "curve_shape": "flat" if p_range < 0.05 else "peaked" if p_mid > p_early + 0.05 else "rising",
    }


# ─── Main ──────────────────────────────────────────────────────────────────

def main():
    print("\n" + "="*60)
    print("PROBE SIGNAL DIAGNOSTICS")
    print("="*60)
    print("Verifying probe accuracy reflects real concept signal, not vocabulary.")

    # Load hand-crafted corpus (we have full extraction data for this one)
    corpus_dir = Path(__file__).parent.parent / "corpus" / "triplets"
    triplets = load_triplets(corpus_dir)
    print(f"\nCorpus: {corpus_dir.name} ({len(triplets)} triplets)")

    # Run tests
    bow_acc, shuf_acc = bow_baseline(triplets)
    hedging_stats = hedging_differential(triplets)
    curve_stats = probe_curve_analysis("qwen3-4b", "triplets", "comprehension")

    # Also run curve analysis for Gemma for comparison (if available)
    print("\n" + "="*60)
    print("COMPARISON: Gemma-2-2B / triplets / comprehension")
    print("="*60)
    probe_curve_analysis("gemma-2-2b-it", "triplets", "comprehension")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  BoW baseline:         {bow_acc:.0%}  (high = vocabulary leak)")
    print(f"  Shuffled-labels ctrl: {shuf_acc:.0%}  (should be ~50%)")
    print(f"  Hedge ratio V/NV:     {hedging_stats['hedge_ratio']:.2f}x")
    print(f"  Certainty ratio NV/V: {hedging_stats['cert_ratio']:.2f}x")
    print(f"  2-feat lexical probe: {hedging_stats['two_feat_probe']:.0%}")
    if curve_stats:
        print(f"  Qwen3 probe range:    {curve_stats['probe_range']*100:.1f}pp")
        print(f"  Qwen3 peak layer:     {curve_stats['best_layer']} ({curve_stats['best_probe']:.0%})")
        print(f"  Qwen3 curve shape:    {curve_stats['curve_shape']}")


if __name__ == "__main__":
    main()
