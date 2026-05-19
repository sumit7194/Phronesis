"""
Experiment 3 — v_IH projection diagnostic (Path A: transcoder basis).

Loads v_IH from earlier extraction and projects it through the qwen3-4b L17
transcoder's encoder. The result tells us which SAE features v_IH "looks like"
in interpretable feature space.

This is a single matrix multiplication; no model inference, no GPU needed.
Sub-second compute, ~2-3 GB SAE download cached on first run.

Caveat (documented in docs/sae-experiment-plan.md Experiment 2 / Path A):
- v_IH was extracted at residual stream OUTPUT of L17 (last_token method)
- Transcoder is at MLP-INPUT of L17 (blocks.17.mlp.hook_in)
- These are different positions. The projection is a heuristic decomposition,
  not a guaranteed-faithful basis change. Result is interpretable as "what
  features fire when v_IH is treated as if it were an MLP-input vector."

Three possible outcomes:
  (A) Strong projection onto Tier-1 humility candidates (101568, 44526, 131926,
      24983, 27191, 115297, 161931) → v_IH IS humility content. F111 was a
      method failure; single-feature steering should beat v_IH.
  (B) Strong projection onto unrelated features → v_IH is mostly NOT humility.
      F111 hardens. The features it lights up tell us what v_IH actually
      represents (likely commit-amplifier per F112).
  (C) Mixed → decompose v_IH into humility-projected and residual components.
"""

import json
from pathlib import Path

import numpy as np
import torch
from sae_lens import SAE

ROOT = Path(__file__).parent.parent

# v_IH at qwen3-4b L17, extracted via last_token method on the IH triplet corpus.
# Both whitened (used in steering experiments) and raw (pre-whitening) versions.
V_IH_WHITENED = ROOT / "mvp" / "results" / "vectors" / "qwen3-4b" / \
    "triplets-intellectual-humility" / "last_token" / "layer_17_virtue_vector.npy"
V_IH_RAW = ROOT / "mvp" / "results" / "vectors" / "qwen3-4b" / \
    "triplets-intellectual-humility" / "last_token" / "layer_17_virtue_vector_raw.npy"

# Catalog references (from docs/feature-catalog.md). Full triage details there.
FEATURE_CATALOG = {
    # Tier 1 humility candidates
    24983: ("T1", "first-person epistemic uncertainty (richest mix of markers)"),
    44526: ("T1", "(un)certainty first-person — sparse, selective"),
    131926: ("T1", "literal 'I don't know' / 'I don't remember'"),
    101568: ("T1", "epistemic limitation admission ('I'm not familiar')"),
    27191: ("T1-demoted-to-T2", "approximation hedge (medical-research register)"),
    115297: ("T1", "number-hedging axis"),
    161931: ("T1-speculative", "verification-disposition (very sparse 0.003%)"),
    # Tier 2
    29010: ("T2", "conversational hedging ('wait, actually')"),
    15911: ("T2", "academic 'to our knowledge' hedge"),
    80: ("T2", "passive belief 'is believed to'"),
    53054: ("T2", "definitional 'I define X as Y'"),
    109839: ("T2", "uncertainty/disagreement"),
    114750: ("T2", "perhaps/maybe rhetorical"),
    59639: ("T2", "academic 'hypothesis that'"),
    19308: ("T2", "argumentative methodology 'assumption'"),
    110169: ("T2", "alleged/suggested clinical"),
    42370: ("T2", "checklist-verify weak variant"),
    123838: ("T2", "-ively suffix morpheme"),
    63583: ("T2", "Q&A affirmative answers"),
    6900: ("T2", "asking experienced programmers"),
    131448: ("T2", "info-insufficiency"),
    136512: ("T2", "if I understood correctly"),
    160623: ("T2", "Socratic ignorance"),
    # Tier 3 — known traps
    70419: ("T3-trap", "WORLD-uncertainty topic (NOT first-person) — original 70419 trap"),
    102685: ("T3-trap", "missing/unknown info (world-uncertainty class)"),
    77462: ("T3-trap", "world-uncertainty in historical/factual"),
    101986: ("T3-trap", "generic 'without' grammatical (1.4% density)"),
    138882: ("T3-trap", "-oric morpheme suffix"),
    152087: ("T3-trap", "-atically morpheme suffix"),
    4069: ("T3-trap", "polysemy 'a certain X' quantifier"),
    38366: ("T3-trap", "polysemy 'certain' quantifier"),
    146191: ("T3-trap-density", "epistemic vigilance (density 2.08% — too generic)"),
    69694: ("T3-trap-density", "deontic 'must' (density 2.44% — too generic)"),
    20431: ("T3-trap", "'need' generic verb"),
    17291: ("T3-trap", "placebo (clinical RCT context)"),
    6609: ("T3-trap", "placebo cluster"),
    148167: ("T3-trap", "placebo cluster"),
}

DEVICE = "cpu"  # MPS on Apple Silicon; matrix multiply is tiny — CPU is fine

OUT_DIR = ROOT / "mvp" / "results" / "experiment3_projection"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_sae():
    print(f"Loading SAE: mwhanna-qwen3-4b-transcoders / layer_17 ...")
    print(f"  (first run will download ~2-3 GB to ~/.cache/huggingface/hub/)")
    sae = SAE.from_pretrained(
        release="mwhanna-qwen3-4b-transcoders",
        sae_id="layer_17",
        device=DEVICE,
    )
    if isinstance(sae, tuple):  # legacy 3-tuple return
        sae = sae[0]
    print(f"  ✅ SAE loaded.")
    print(f"  W_enc shape: {tuple(sae.W_enc.shape)}")
    print(f"  W_dec shape: {tuple(sae.W_dec.shape)}")
    # cfg attribute name varies between SAE/Transcoder; print whatever's available
    cfg = getattr(sae, "cfg", None)
    if cfg is not None:
        for attr in ("hook_name", "hook_in", "hook_layer", "metadata"):
            if hasattr(cfg, attr):
                print(f"  cfg.{attr}: {getattr(cfg, attr)}")
                break
    return sae


def project(sae, v_IH_np, label):
    """Pass v_IH through SAE encoder → feature activations.
    Returns (feature_activations_tensor, sorted_top_indices, sorted_top_values).
    """
    v_IH = torch.from_numpy(v_IH_np).float().to(DEVICE)
    print(f"\n=== Projecting {label} ===")
    print(f"  v_IH shape: {tuple(v_IH.shape)}, norm: {v_IH.norm().item():.4f}")

    if v_IH.dim() == 1:
        v_IH_b = v_IH.unsqueeze(0)  # add batch dim
    else:
        v_IH_b = v_IH

    with torch.no_grad():
        feature_acts = sae.encode(v_IH_b).squeeze(0)  # shape (n_features,)

    n_nonzero = (feature_acts > 0).sum().item()
    n_features = feature_acts.shape[0]
    print(f"  features activated: {n_nonzero} / {n_features} "
          f"({100*n_nonzero/n_features:.2f}%)")

    # Sort by activation value (descending). Take top 50 for full picture.
    top_vals, top_idxs = torch.topk(feature_acts, k=50)
    return feature_acts, top_idxs.cpu().numpy(), top_vals.cpu().numpy()


def report(top_idxs, top_vals, label, total_features=163840):
    print(f"\n=== Top-50 features for {label} ===")
    rows = []
    catalog_hits = {"T1": 0, "T2": 0, "T3-trap": 0, "uncategorized": 0}
    for rank, (idx, val) in enumerate(zip(top_idxs, top_vals), start=1):
        idx_int = int(idx)
        catalog_entry = FEATURE_CATALOG.get(idx_int)
        if catalog_entry:
            tier, desc = catalog_entry
            tier_short = tier.split("-")[0]
            catalog_hits[tier_short] = catalog_hits.get(tier_short, 0) + 1
            tag = f"[{tier}] {desc}"
        else:
            catalog_hits["uncategorized"] += 1
            tag = "(not in catalog)"
        rows.append({
            "rank": rank,
            "idx": idx_int,
            "activation": float(val),
            "catalog_tier": catalog_entry[0] if catalog_entry else None,
            "catalog_desc": catalog_entry[1] if catalog_entry else None,
        })
        print(f"  #{rank:2d}  idx={idx_int:6d}  act={val:8.4f}  {tag}")

    print(f"\n  Summary of top-50:")
    for tier, count in catalog_hits.items():
        print(f"    {tier}: {count}")
    return rows, catalog_hits


def main():
    sae = load_sae()

    # Project both versions of v_IH
    versions = []
    if V_IH_WHITENED.exists():
        v_w = np.load(V_IH_WHITENED)
        versions.append(("v_IH (whitened — used in steering)", v_w))
    else:
        print(f"⚠️  v_IH whitened not found at {V_IH_WHITENED}")

    if V_IH_RAW.exists():
        v_r = np.load(V_IH_RAW)
        versions.append(("v_IH (raw — pre-whitening)", v_r))
    else:
        print(f"⚠️  v_IH raw not found at {V_IH_RAW}")

    if not versions:
        print("ERROR: no v_IH vectors found.")
        return

    output = {
        "model": "qwen3-4b",
        "layer": 17,
        "sae_release": "mwhanna-qwen3-4b-transcoders",
        "sae_id": "layer_17",
        "caveat": (
            "Basis-mismatch: v_IH was extracted at residual-stream output of L17 (last_token); "
            "transcoder is at MLP-input of L17. Projection is a heuristic decomposition. "
            "See docs/sae-experiment-plan.md Experiment 2 / Path A."
        ),
        "results": {},
    }

    for label, v in versions:
        feature_acts, top_idxs, top_vals = project(sae, v, label)
        rows, hits = report(top_idxs, top_vals, label)
        output["results"][label] = {
            "n_features_activated": int((feature_acts > 0).sum().item()),
            "top_50": rows,
            "catalog_hit_summary": hits,
            "v_IH_norm": float(np.linalg.norm(v)),
        }

    out_path = OUT_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n✅ Results saved to {out_path.relative_to(ROOT)}")

    # Verdict
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)
    primary_hits = output["results"][versions[0][0]]["catalog_hit_summary"]
    t1 = primary_hits.get("T1", 0)
    t3 = primary_hits.get("T3-trap", 0) + primary_hits.get("T3", 0)
    if t1 >= 5:
        print(f"Outcome (A): v_IH lights up {t1} Tier-1 humility candidates in top-50.")
        print("  → v_IH IS humility content. F111 likely method-failure;")
        print("     single-feature SAE-steering should beat v_IH.")
    elif t1 >= 2 and t1 < 5:
        print(f"Outcome (C): MIXED — {t1} Tier-1 humility hits + others.")
        print("  → v_IH has a humility component but also other content.")
        print("     Decompose into projected (humility) and residual parts.")
    else:
        print(f"Outcome (B): v_IH lights up only {t1} Tier-1 humility candidates.")
        print("  → v_IH is mostly NOT humility content. F111 hardens.")
        print("     Look at what features it DID activate to identify the actual")
        print("     content (likely commit-amplifier per F112 hypothesis).")
    if t3 > 0:
        print(f"  ⚠️  {t3} known-trap features in top-50 — flag in writeup.")


if __name__ == "__main__":
    main()
