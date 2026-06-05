"""Extract W_dec decoder directions for the MANUALLY-VERIFIED functional uncertainty
features (qwen3-4b L17 transcoder) as CORPUS-FREE steering vectors — the option-A
alternative to the recipe-dependent corpus diff-of-means v_IH.

Source of the feature list (each verified by reading its top activations on Neuronpedia):
  mvp/sae_neuronpedia_data/functional_uncertainty_features_qwen3-4b_2026-06-05.md

W_dec rows of the transcoder are the MLP-output contribution to the residual stream,
so they're usable directly with the residual steering hook at layer 17.
"""
import json
from pathlib import Path
import numpy as np
from sae_lens import SAE

OUT = Path("results/vectors/qwen3-4b/sae_functional_uncertainty")
OUT.mkdir(parents=True, exist_ok=True)

# Tier-1 verified-functional features (first-person epistemic uncertainty / not-knowing)
FEATURES = {
    131926: "I don't know",
    131448: "needing information, not knowing",
    160623: "lack of knowledge",
    101568: "uncertainty/limitations (I must confess)",
    44526:  "(un)certainty (if you are unsure)",
}

print("Loading SAE mwhanna-qwen3-4b-transcoders / layer_17 ...", flush=True)
sae = SAE.from_pretrained(release="mwhanna-qwen3-4b-transcoders", sae_id="layer_17", device="cpu")
if isinstance(sae, tuple):
    sae = sae[0]
W_dec = sae.W_dec.detach().float().cpu().numpy()
print("W_dec shape:", W_dec.shape, flush=True)

unit_vecs = []
meta = {}
for idx, desc in FEATURES.items():
    v = W_dec[idx]
    n = float(np.linalg.norm(v))
    np.save(OUT / f"feat_{idx}_Wdec.npy", v.astype(np.float32))
    unit_vecs.append(v / n)
    meta[str(idx)] = {"desc": desc, "norm": n}
    print(f"  {idx} ({desc}): norm={n:.4f}", flush=True)

# Combined Tier-1 direction = mean of unit-normalized decoders, then unit-normalized
combined = np.mean(unit_vecs, axis=0)
combined = combined / np.linalg.norm(combined)
np.save(OUT / "combined_tier1_unit.npy", combined.astype(np.float32))
# also save each as a unit vector (so steering alpha is comparable across features)
for idx in FEATURES:
    v = np.load(OUT / f"feat_{idx}_Wdec.npy")
    np.save(OUT / f"feat_{idx}_unit.npy", (v / np.linalg.norm(v)).astype(np.float32))

meta["combined_tier1_unit"] = {"desc": "mean of unit Tier-1 decoders", "n_features": len(FEATURES)}
json.dump(meta, open(OUT / "manifest.json", "w"), indent=2)
print("Saved decoders + unit vectors + combined to", OUT, flush=True)
