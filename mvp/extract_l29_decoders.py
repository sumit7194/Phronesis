"""Extract W_dec decoders for the VERIFIED first-person uncertainty features at
L29 (qwen3-4b transcoder) — the layer test (L29 had cleaner first-person features
than L17 per the 2026-06-05 multi-layer check). Steer at native layer 29.
  10966 = "not 100% confident about it as I" (first-person)
  21336 = "you don't know what to say / what to do"
"""
import json
from pathlib import Path
import numpy as np
from sae_lens import SAE

OUT = Path("results/vectors/qwen3-4b/sae_functional_uncertainty_L29")
OUT.mkdir(parents=True, exist_ok=True)
FEATURES = {10966: "not 100% confident (first-person)", 21336: "you don't know what to say/do"}

print("Loading SAE mwhanna-qwen3-4b-transcoders / layer_29 ...", flush=True)
sae = SAE.from_pretrained(release="mwhanna-qwen3-4b-transcoders", sae_id="layer_29", device="cpu")
if isinstance(sae, tuple):
    sae = sae[0]
W = sae.W_dec.detach().float().cpu().numpy()
print("W_dec", W.shape, flush=True)

unit = []
for idx, desc in FEATURES.items():
    v = W[idx]; n = float(np.linalg.norm(v))
    np.save(OUT / f"feat_{idx}_unit.npy", (v / n).astype(np.float32))
    unit.append(v / n)
    print(f"  {idx} {desc} norm={n:.4f}", flush=True)
comb = np.mean(unit, axis=0); comb = comb / np.linalg.norm(comb)
np.save(OUT / "combined_l29_unit.npy", comb.astype(np.float32))
json.dump({str(k): v for k, v in FEATURES.items()}, open(OUT / "manifest.json", "w"), indent=2)
print("saved to", OUT, flush=True)
