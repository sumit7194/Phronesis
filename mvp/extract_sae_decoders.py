"""
Extract SAE feature decoder directions to .npy files for use with steer.py.

Uses SAELens canonical loading API (saved us from raw HuggingFace path hell —
thanks to Gemini for verifying the canonical `release` / `sae_id` strings via
the Neuronpedia "How To Load" dialog; see `mvp/sae_neuronpedia_data/` notes).

For each shortlisted feature in the catalog:
  1. Loads the appropriate SAE via SAE.from_pretrained(release, sae_id)
     (downloads + caches automatically on first call)
  2. Extracts the decoder direction sae.W_dec[idx] for that feature index
  3. Saves to mvp/results/sae_decoders/{key}_{idx}.npy

The resulting .npy files are drop-in compatible with steer.py's existing --vector
argument. The --feature MODEL[:LAYER]:IDX shortcut in the patched steer.py
auto-resolves to the same .npy file via the manifest.

Run-once setup (CPU is fine; GPU is faster). Total HF download volume ~15-25 GB
across the 5 SAE families.

ARCHITECTURE NOTE on decoder direction:
- SAE encoder: residual_stream_vec → feature_activations
- SAE decoder: feature_activations → residual_stream_vec
- The decoder weight column for feature i (sae.W_dec[i]) is the residual-stream
  direction that feature i contributes when active. This is the natural steering
  direction — additive in the same space as our diff-of-means virtue vectors.
- For transcoders (qwen3-4b transcoder-hp, gemma transcoder): the decoder maps
  features → MLP-output. Since MLP-output is added to the residual stream after
  the MLP block, sae.W_dec[i] is still a residual-stream direction (specifically
  the MLP-block contribution to it). Usable with the same hook used for
  diff-of-means vectors. Caveat: caveat about basis-mismatch with v_IH residual
  extraction is documented in docs/sae-experiment-plan.md Experiment 2.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

try:
    import torch
    from sae_lens import SAE
except ImportError:
    print("ERROR: pip install sae_lens (also brings torch, transformer_lens, transformers, safetensors)",
          file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).parent.parent
OUT_DIR = ROOT / "mvp" / "results" / "sae_decoders"


# Each entry: SAELens release + sae_id, plus the indices we want to extract.
# Loading codes verified by Gemini via Neuronpedia "How To Load" dialog
# (mvp/sae_neuronpedia_data/sae_loading_codes.md).
FEATURE_BATCH = {
    # qwen3-4b · L17 · transcoders-hp (primary IH steering battery)
    "qwen3-4b_L17_transcoder-hp": {
        "release": "mwhanna-qwen3-4b-transcoders",
        "sae_id": "layer_17",
        "indices": {
            "T1_humility": [24983, 44526, 131926, 101568, 27191, 115297, 161931],
            "T2_aux": [29010, 15911, 80, 53054],
            "T3_70419_trap_negative_control": [70419],
        },
    },
    # qwen3-4b · L29 · transcoders-hp (lone deeper-layer commit candidate)
    "qwen3-4b_L29_transcoder-hp": {
        "release": "mwhanna-qwen3-4b-transcoders",
        "sae_id": "layer_29",
        "indices": {
            "T2_commit_candidate": [59103],
            "T3_traps_for_negative_control": [34354, 15007],
        },
    },

    # Qwen2.5-7B-Instruct · L23 · andyrdt resid-post (proxy for openr1-qwen-7b)
    "qwen2.5-7b-it_L23_resid-post-aa": {
        "release": "qwen2.5-7b-instruct-andyrdt",
        "sae_id": "resid_post_layer_23_trainer_1",
        "indices": {
            "T1_humility": [2174, 75315, 84309],
            "T2_controls": [120087, 5494],
            "T3_traps": [89590, 30133, 18575],
        },
    },

    # Llama-3.1-8B base · L31 · llamascope-res-32k (IH features for L31)
    # NOTE: SAELens release "llama_scope_lxr_32x" — `32x` corresponds to the 32k width
    # at this layer (per Gemini verification). For L22 with 131k features it's still
    # `llama_scope_lxr_32x` but with a different sae_id slug.
    # ↑ Re-verify: 121957 is in the 131k SAE; 7984/201 are in the 32k SAE (per Phase A density verification).
    # Per Gemini: `release="llama_scope_lxr_32x" sae_id="l22r_32x"` for the 131k.
    # The 32k variant is most likely `release="llama_scope_lxr_8x" sae_id="l31r_8x"` or similar.
    # If sae_lens load fails, run a small probe to discover correct release/sae_id.
    "llama-3.1-8b_L31_llamascope-res-32k": {
        "release": "llama_scope_lxr_8x",  # verified by Gemini 2026-05-10
        "sae_id": "l31r_8x",
        "indices": {
            "T1_humility": [7984, 201],
            "T2_aux": [21701, 10391, 8310],
        },
    },
    "llama-3.1-8b_L22_llamascope-res-131k": {
        "release": "llama_scope_lxr_32x",
        "sae_id": "l22r_32x",
        "indices": {
            "T1_evidence_grounding": [121957],
        },
    },

    # Gemma-3-4B-IT · L17 · gemmascope-2-res-16k (disclaimer cluster)
    "gemma-3-4b-it_L17_gemmascope-2-res-16k": {
        "release": "gemma-scope-2-4b-it-res",
        "sae_id": "layer_17_width_16k_l0_medium",
        "indices": {
            "T1_disclaimer_cluster": [10709, 12370, 7610],
            "T2_controls": [7739, 2894, 37, 6971, 14758, 3186, 2930],
        },
    },
    # Gemma-3-4B-IT · L17 · transcoder-262k (EG 86193)
    "gemma-3-4b-it_L17_gemmascope-2-transcoder-262k": {
        "release": "gemma-scope-2-4b-it-transcoders-all",  # verified by Gemini 2026-05-10
        "sae_id": "layer_17_width_262k_l0_small_affine",   # note: NOT "medium" like res-16k
        "indices": {
            "T1_evidence_grounding": [86193],
        },
    },

    # R1-Distill-Llama-8B · L31 · llamascope-slimpj-openr1-res-32k (F112 triangle)
    "r1-distill-llama-8b_L31_llamascope-openr1": {
        "release": "llama_scope_r1_distill",
        "sae_id": "l31r_400m_slimpajama_400m_openr1_math",
        "indices": {
            "T1_F112_triangle": [15372, 19103, 2136],
            "T1_doubt_concept": [339],
            "T2_aux": [16017, 1229, 4288, 4083, 25534, 28646, 23399],
            "T3_traps": [21023, 32498],
        },
    },
}


def extract_for_entry(model_key, entry, dry_run=False):
    print(f"\n=== {model_key} ===")
    print(f"  SAELens: release={entry['release']!r} sae_id={entry['sae_id']!r}")
    if entry.get("verify_note"):
        print(f"  ⚠️  {entry['verify_note']}")

    total_indices = sum(len(v) for v in entry["indices"].values())
    if dry_run:
        print(f"  [DRY RUN] Would extract {total_indices} feature decoders.")
        for tier, idxs in entry["indices"].items():
            print(f"    {tier}: {idxs}")
        return True

    # Load SAE
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        sae, _cfg, _sparsity = SAE.from_pretrained(
            release=entry["release"],
            sae_id=entry["sae_id"],
            device=device,
        )
    except Exception as e:
        print(f"  ❌ SAE.from_pretrained failed: {e}", file=sys.stderr)
        return False

    W_dec = sae.W_dec  # shape (n_features, d_residual_stream)
    n_features, d = W_dec.shape
    print(f"  Loaded W_dec: shape ({n_features}, {d})")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    extracted = 0
    for tier, idxs in entry["indices"].items():
        for idx in idxs:
            if idx >= n_features:
                print(f"  ❌ idx {idx} >= n_features {n_features}", file=sys.stderr)
                continue
            decoder_dir = W_dec[idx].detach().float().cpu().numpy()
            out_path = OUT_DIR / f"{model_key}_{idx}.npy"
            np.save(out_path, decoder_dir)
            print(f"  ✅ {out_path.name}  (norm={np.linalg.norm(decoder_dir):.4f}  "
                  f"tier={tier})")
            extracted += 1
    return extracted == total_indices


def main():
    parser = argparse.ArgumentParser(description="Extract SAE decoder directions via SAELens")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be extracted without loading SAEs")
    parser.add_argument("--key", help="Only extract for this entry of FEATURE_BATCH")
    parser.add_argument("--skip-on-error", action="store_true",
                        help="Continue past load failures (e.g. verify_note slugs)")
    args = parser.parse_args()

    if args.key:
        if args.key not in FEATURE_BATCH:
            print(f"Unknown key: {args.key}")
            print(f"Available: {list(FEATURE_BATCH.keys())}")
            sys.exit(1)
        extract_for_entry(args.key, FEATURE_BATCH[args.key], dry_run=args.dry_run)
    else:
        any_failures = False
        for key, entry in FEATURE_BATCH.items():
            ok = extract_for_entry(key, entry, dry_run=args.dry_run)
            if not ok and not args.dry_run:
                any_failures = True
                if not args.skip_on_error:
                    print(f"\nStopping. Re-run with --skip-on-error to continue past failures.")
                    sys.exit(1)

    if args.dry_run:
        print("\n=== Dry-run complete ===")
        print("Re-run without --dry-run to actually load SAEs and extract decoders.")
        print("First load will trigger HF download (~15-25 GB cached to ~/.cache/huggingface/).")
        return

    # Build manifest from whatever .npy files are present
    manifest = []
    for key, entry in FEATURE_BATCH.items():
        for tier, idxs in entry["indices"].items():
            for idx in idxs:
                npy = OUT_DIR / f"{key}_{idx}.npy"
                if npy.exists():
                    manifest.append({
                        "key": f"{key}_{idx}",
                        "model": key.split("_L")[0],
                        "layer": int(key.split("_L")[1].split("_")[0]),
                        "source": "_".join(key.split("_L")[1].split("_")[1:]),
                        "feature_idx": idx,
                        "tier": tier,
                        "release": entry["release"],
                        "sae_id": entry["sae_id"],
                        "npy_path": str(npy.relative_to(ROOT)),
                    })
    manifest_path = OUT_DIR / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\n=== Done — {len(manifest)} decoder vectors extracted ===")
    print(f"Manifest: {manifest_path.relative_to(ROOT)}")
    if any_failures:
        print("⚠️  Some entries failed — check stderr. The manifest has only successful extracts.")


if __name__ == "__main__":
    main()
