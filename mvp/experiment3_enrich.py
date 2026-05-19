"""
Enrich Experiment 3 projection results:
  1. For every catalog feature (T1 humility, T2 aux, T3 traps), find its
     rank + activation value in v_IH's projection — even if not in top-50.
  2. For top-50 features that aren't in catalog, fetch auto-label + density via
     Neuronpedia API to identify what v_IH actually projects onto.
  3. Write enriched markdown report.
"""

import json
import os
import time
import urllib.error
import urllib.request
from collections import deque
from pathlib import Path

import numpy as np
import torch
from sae_lens import SAE

ROOT = Path(__file__).parent.parent

# Reuse paths + catalog from main script
V_IH_WHITENED = ROOT / "mvp" / "results" / "vectors" / "qwen3-4b" / \
    "triplets-intellectual-humility" / "last_token" / "layer_17_virtue_vector.npy"

OUT_DIR = ROOT / "mvp" / "results" / "experiment3_projection"
RESULTS_PATH = OUT_DIR / "results.json"
ENRICHED_PATH = OUT_DIR / "enriched_report.md"

# Load API keys for Neuronpedia auto-label lookup of unknown top features
ENV_PATH = "/Users/sumit/Downloads/NP/.env"
API_KEYS = []
if os.path.exists(ENV_PATH):
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line.startswith("NEURONPEDIA_API_KEY") and "=" in line:
                _, v = line.split("=", 1)
                API_KEYS.append(v.strip())
key_pool = deque(API_KEYS)

# All catalog feature indices we know about (from feature-catalog.md)
CATALOG = {
    # Tier 1
    24983: "T1 first-person epistemic uncertainty",
    44526: "T1 (un)certainty first-person",
    131926: "T1 literal 'I don't know'",
    101568: "T1 epistemic limitation 'I'm not familiar'",
    27191: "T1-demoted estimate (medical register)",
    115297: "T1 number-hedging",
    161931: "T1 verification-disposition (sparse)",
    # Tier 2
    29010: "T2 conversational hedging",
    15911: "T2 academic 'to our knowledge'",
    80: "T2 passive 'is believed to'",
    53054: "T2 'I define X as'",
    109839: "T2 uncertainty/disagreement",
    114750: "T2 perhaps/maybe rhetorical",
    59639: "T2 'hypothesis that'",
    19308: "T2 'assumption'",
    110169: "T2 alleged/suggested clinical",
    42370: "T2 checklist-verify weak variant",
    123838: "T2 -ively suffix",
    63583: "T2 affirmative answers",
    6900: "T2 asking experienced programmers",
    131448: "T2 info-insufficiency",
    136512: "T2 if I understood correctly",
    160623: "T2 Socratic ignorance",
    69694: "T3-demoted-density 'must' (2.44%)",
    146191: "T3-demoted-density epistemic vigilance (2.08%)",
    # Tier 3 traps
    70419: "T3-trap world-uncertainty (the original 70419)",
    102685: "T3-trap missing/unknown info",
    77462: "T3-trap world-uncertainty historical",
    101986: "T3-trap generic 'without' (1.4%)",
    138882: "T3-trap -oric morpheme",
    152087: "T3-trap -atically morpheme",
    4069: "T3-trap 'a certain X' quantifier",
    38366: "T3-trap 'certain' quantifier",
    20431: "T3-trap 'need' generic",
    17291: "T3-trap placebo (clinical)",
    6609: "T3-trap placebo cluster",
    148167: "T3-trap placebo cluster",
}


def lookup_neuronpedia(idx, layer=17, model="qwen3-4b", source="transcoder-hp"):
    """Look up auto-label + density for a feature index via Neuronpedia API
    with key rotation to avoid rate limits."""
    if not API_KEYS:
        return None
    layer_str = f"{layer}-{source}"
    url = f"https://www.neuronpedia.org/api/feature/{model}/{layer_str}/{idx}"
    for _ in range(len(API_KEYS)):
        k = key_pool[0]; key_pool.rotate(-1)
        req = urllib.request.Request(url, headers={"x-api-key": k}, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                body = json.loads(r.read().decode())
                desc_list = body.get("explanations", [])
                desc = desc_list[0].get("description", "") if desc_list else "(no label)"
                return {
                    "auto_label": desc[:80],
                    "density_pct": (body.get("frac_nonzero") or 0) * 100,
                    "max_act": body.get("maxActApprox", 0),
                }
        except urllib.error.HTTPError as e:
            if e.code == 429:
                continue  # try next key
            return {"_error": f"status={e.code}"}
        except Exception as e:
            return {"_error": str(e)[:100]}
    return {"_error": "all keys cooled"}


def main():
    # Load SAE
    print("Loading SAE...")
    sae = SAE.from_pretrained(release="mwhanna-qwen3-4b-transcoders", sae_id="layer_17", device="cpu")
    if isinstance(sae, tuple):
        sae = sae[0]

    # Project whitened v_IH (the one we steered with)
    v_IH = torch.from_numpy(np.load(V_IH_WHITENED)).float().unsqueeze(0)
    with torch.no_grad():
        feature_acts = sae.encode(v_IH).squeeze(0).cpu().numpy()
    n_features = feature_acts.shape[0]
    n_active = int((feature_acts > 0).sum())

    # 1. Catalog feature rankings — where does each known feature land?
    print("\n=== Catalog feature ranks in v_IH projection ===")
    sorted_idxs = np.argsort(-feature_acts)  # descending
    rank_lookup = {int(idx): rank for rank, idx in enumerate(sorted_idxs, start=1)}

    catalog_results = []
    for idx, label in CATALOG.items():
        rank = rank_lookup.get(idx, n_features + 1)
        act = float(feature_acts[idx]) if idx < n_features else 0.0
        catalog_results.append({"idx": idx, "label": label, "rank": rank, "activation": act})
    catalog_results.sort(key=lambda r: r["rank"])

    # 2. Top-50 unknown features — fetch labels
    top50_idxs = sorted_idxs[:50]
    print(f"\n=== Fetching auto-labels for top-50 features ===")
    top50_enriched = []
    for rank, idx in enumerate(top50_idxs, start=1):
        idx_int = int(idx)
        act = float(feature_acts[idx_int])
        catalog_label = CATALOG.get(idx_int)
        if catalog_label:
            top50_enriched.append({
                "rank": rank, "idx": idx_int, "activation": act,
                "from_catalog": True, "label": catalog_label,
            })
            continue
        # Fetch from API
        meta = lookup_neuronpedia(idx_int)
        time.sleep(0.15)
        if meta and "_error" not in meta:
            top50_enriched.append({
                "rank": rank, "idx": idx_int, "activation": act,
                "from_catalog": False,
                "auto_label": meta["auto_label"],
                "density_pct": round(meta["density_pct"], 4),
                "max_act": round(meta["max_act"], 2),
            })
            print(f"  #{rank:2d} idx={idx_int:6d} act={act:6.3f} dens={meta['density_pct']:.3f}% "
                  f"label={meta['auto_label']!r}")
        else:
            err = meta.get("_error", "?") if meta else "?"
            top50_enriched.append({
                "rank": rank, "idx": idx_int, "activation": act,
                "from_catalog": False, "error": err,
            })
            print(f"  #{rank:2d} idx={idx_int:6d} act={act:6.3f}  (lookup failed: {err})")

    # Write report
    output = {
        "summary": {
            "n_features_activated": n_active,
            "n_features_total": n_features,
            "active_pct": round(100 * n_active / n_features, 2),
            "top1_idx": int(top50_idxs[0]),
            "top1_act": float(feature_acts[top50_idxs[0]]),
        },
        "catalog_features_in_v_IH": catalog_results,
        "top50_enriched": top50_enriched,
    }
    enriched_json = OUT_DIR / "enriched.json"
    with open(enriched_json, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n✅ JSON: {enriched_json.relative_to(ROOT)}")

    # Markdown report
    md = []
    md.append("# Experiment 3 — v_IH projection diagnostic, enriched report")
    md.append("")
    md.append("Generated by `mvp/experiment3_enrich.py`. Loads v_IH (whitened), passes it through")
    md.append("qwen3-4b L17 transcoder encoder via SAELens, then enriches the top-50 features with")
    md.append("Neuronpedia API auto-labels + densities.")
    md.append("")
    md.append("**Caveat (basis-mismatch):** v_IH was extracted at residual-stream output of L17;")
    md.append("transcoder is at MLP-input of L17. Projection is a heuristic decomposition. See")
    md.append("`docs/sae-experiment-plan.md` Experiment 2 / Path A.")
    md.append("")
    md.append("## Headline numbers")
    md.append("")
    md.append(f"- Total features activated: **{n_active:,} / {n_features:,}** ({output['summary']['active_pct']}%)")
    md.append(f"- Top-1 feature: idx={output['summary']['top1_idx']}  activation={output['summary']['top1_act']:.4f}")
    md.append("")
    md.append("## Where do the catalog features rank in v_IH's projection?")
    md.append("")
    md.append("If v_IH were humility content, our 7 Tier-1 humility candidates should rank near the top.")
    md.append("Below: actual ranks of every catalog feature.")
    md.append("")
    md.append("| Rank | Idx | Catalog label | v_IH activation |")
    md.append("|---|---|---|---|")
    for r in catalog_results[:25]:
        md.append(f"| {r['rank']} | {r['idx']} | {r['label']} | {r['activation']:.4f} |")
    md.append("")
    if len(catalog_results) > 25:
        md.append(f"…and {len(catalog_results) - 25} more (full list in `enriched.json`).")
    md.append("")
    md.append("## Top-50 features v_IH actually lights up")
    md.append("")
    md.append("Auto-labels via Neuronpedia API. Watch for: hedge-vocabulary clusters (would be")
    md.append("close-to-humility), commit/closure clusters (consistent with F112 commit-amplifier")
    md.append("hypothesis), or unrelated discourse-register features.")
    md.append("")
    md.append("| Rank | Idx | Activation | Density | Auto-label |")
    md.append("|---|---|---|---|---|")
    for r in top50_enriched:
        if r.get("from_catalog"):
            md.append(f"| {r['rank']} | {r['idx']} | {r['activation']:.4f} | (catalog) | {r['label']} |")
        elif "auto_label" in r:
            md.append(f"| {r['rank']} | {r['idx']} | {r['activation']:.4f} | "
                      f"{r['density_pct']:.3f}% | {r['auto_label']} |")
        else:
            md.append(f"| {r['rank']} | {r['idx']} | {r['activation']:.4f} | – | (lookup failed: {r.get('error')}) |")

    with open(ENRICHED_PATH, "w") as f:
        f.write("\n".join(md))
    print(f"✅ Markdown: {ENRICHED_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
