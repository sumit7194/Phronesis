#!/usr/bin/env python
"""Decompose a steering vector into Qwen3-32B SAE features (Neuronpedia: adamkarvonen/qwen3-32b-saes,
resid_post_layer_32, batch-top-k 65k). Tests whether v_hedge is built from interpretable 'uncertainty'
features or a diffuse mix (the F167 question at 32B scale).

Usage:
  # dry-run with a random vector (pipeline check, no real vector needed):
  python sae_decompose_32b.py --dry
  # real run once v_hedge is extracted+saved (npy: {layer:int -> vector}):
  python sae_decompose_32b.py --vector results/legibility/v_hedge_32b.npy --layer 32 --topk 25
"""
import argparse, json, sys, urllib.request
import numpy as np, torch

SAE_PT = "{hub}/saes_Qwen_Qwen3-32B_batch_top_k/resid_post_layer_{L}/trainer_{T}/ae.pt"

def load_decoder(path):
    """Return W_dec as (dict_size, d_model) float32 — one unit-normalizable direction per feature."""
    obj = torch.load(path, map_location="cpu", weights_only=False)
    sd = obj.state_dict() if hasattr(obj, "state_dict") else obj
    # find the decoder weight; dictionary_learning stores 'decoder.weight' as (d_model, dict_size)
    cand = {k: v for k, v in sd.items() if isinstance(v, torch.Tensor) and v.ndim == 2}
    key = next((k for k in cand if "decoder" in k.lower() and "weight" in k.lower()), None)
    if key is None:  # fall back to W_dec / largest 2D tensor
        key = next((k for k in cand if "w_dec" in k.lower()), max(cand, key=lambda k: cand[k].numel()))
    W = cand[key].float().numpy()
    # orient to (dict_size, d_model): dict_size is the larger axis (65536 vs 5120)
    if W.shape[0] < W.shape[1]:
        W = W.T
    print(f"[sae] decoder key='{key}' -> W_dec {W.shape} (dict_size, d_model)")
    return W

def top_features(v, W, k):
    vn = v / (np.linalg.norm(v) + 1e-8)
    Wn = W / (np.linalg.norm(W, axis=1, keepdims=True) + 1e-8)
    sims = Wn @ vn
    idx = np.argsort(-np.abs(sims))[:k]
    return [(int(i), float(sims[i])) for i in idx], sims

def np_label(model, source, i):
    url = f"https://www.neuronpedia.org/api/feature/{model}/{source}/{i}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "phronesis-research"})
        d = json.load(urllib.request.urlopen(req, timeout=15))
        exps = d.get("explanations") or []
        lab = exps[0].get("description") if exps else None
        pos = "".join((d.get("pos_str") or [])[:6])
        return (lab or "(no auto-interp)"), pos
    except Exception as e:
        return f"(fetch err: {type(e).__name__})", ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hub", default="/Users/sumit/.cache/huggingface/hub/models--adamkarvonen--qwen3-32b-saes/snapshots")
    ap.add_argument("--trainer", type=int, default=2)   # 2=k80, 3=k160 (both 65k); resolve vs model later
    ap.add_argument("--sae-layer", type=int, default=32)
    ap.add_argument("--vector", default=None)
    ap.add_argument("--layer", type=int, default=32)    # which layer's vector to use
    ap.add_argument("--topk", type=int, default=25)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--labels", type=int, default=1)
    ap.add_argument("--out", default="results/legibility/sae_decompose_vhedge_32b.json")
    args = ap.parse_args()

    import glob
    snaps = glob.glob(args.hub + "/*")
    if not snaps:
        sys.exit("SAE not downloaded yet under " + args.hub)
    path = SAE_PT.format(hub=snaps[0], L=args.sae_layer, T=args.trainer)
    W = load_decoder(path)

    if args.dry:
        rng = np.random.default_rng(0)
        v = rng.standard_normal(W.shape[1]).astype("float32")
        print("[dry] random vector — pipeline check only")
    else:
        store = np.load(args.vector, allow_pickle=True).item()
        v = np.asarray(store[args.layer], dtype="float32")
        print(f"[vec] v_hedge layer {args.layer}: dim {v.shape}, |v|={np.linalg.norm(v):.2f}")

    feats, sims = top_features(v, W, args.topk)
    print(f"\nspread: max|cos|={np.abs(sims).max():.3f}  mean|cos|={np.abs(sims).mean():.4f}  "
          f"(diffuse if top is small / no dominant feature)")
    src = f"{args.sae_layer}-resid-batchtopk-65k"
    rows = []
    print(f"\n{'rank':>4} {'feat':>7} {'cos':>7}  label (Neuronpedia auto-interp)")
    for r, (i, s) in enumerate(feats):
        lab, pos = ("", "")
        if args.labels and not args.dry:
            lab, pos = np_label("qwen3-32b", src, i)
        rows.append(dict(rank=r, feat=i, cos=round(s, 4), label=lab, pos=pos,
                         url=f"https://www.neuronpedia.org/qwen3-32b/{src}/{i}"))
        print(f"{r:>4} {i:>7} {s:>7.3f}  {lab[:70]}")
    json.dump(dict(layer=args.layer, trainer=args.trainer, topk=args.topk,
                   max_abs_cos=float(np.abs(sims).max()), mean_abs_cos=float(np.abs(sims).mean()),
                   features=rows), open(args.out, "w"), indent=1)
    print("\n[done] ->", args.out)

if __name__ == "__main__":
    main()
