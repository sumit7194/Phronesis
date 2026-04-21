"""
Phronesis MVP v2 — Improved extraction with multiple methods and multi-model support.

Changes from v1:
- Fixed generation method (deterministic, longer, better prompt)
- Added last-token method
- Added broader layer sweep
- Multi-model support
- Vector saving for steering (--save-vectors)

Usage:
    python extract_v2.py --model gemma-2-2b-it
    python extract_v2.py --model gemma-2-2b-it --method all --layers all --save-vectors
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import accuracy_score
from scipy.spatial.distance import cosine as cosine_dist

from utils import MODEL_CONFIGS, ActivationCapture, CORPUS_DIR, RESULTS_DIR, load_model, load_triplets


# ─── Three extraction methods ────────────────────────────────────────────────

def method_comprehension(model, tokenizer, capture, text, device):
    capture.clear()
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(device)
    with torch.no_grad():
        model(**inputs)
    seq_len = inputs["input_ids"].shape[1]
    skip = max(1, int(seq_len * 0.25))
    results = {}
    for l in capture.layer_indices:
        act = capture.activations[l][0, skip:, :].mean(dim=0).numpy()
        results[l] = act
    return results


def method_comprehension_batched(model, tokenizer, capture, texts, device, batch_size=8):
    """Batched comprehension: process multiple texts in one forward pass."""
    all_results = [{} for _ in texts]

    for batch_start in range(0, len(texts), batch_size):
        batch_texts = texts[batch_start:batch_start + batch_size]
        capture.clear()

        inputs = tokenizer(
            batch_texts, return_tensors="pt", truncation=True,
            max_length=512, padding=True,
        ).to(device)

        with torch.no_grad():
            model(**inputs)

        attention_mask = inputs["attention_mask"]
        for b_idx in range(len(batch_texts)):
            seq_len = int(attention_mask[b_idx].sum().item())
            skip = max(1, int(seq_len * 0.25))
            for l in capture.layer_indices:
                act = capture.activations[l][b_idx, skip:seq_len, :].mean(dim=0).numpy()
                all_results[batch_start + b_idx][l] = act

    return all_results


def method_last_token_batched(model, tokenizer, capture, texts, device, batch_size=8):
    """Batched last-token: process multiple texts in one forward pass."""
    all_results = [{} for _ in texts]

    for batch_start in range(0, len(texts), batch_size):
        batch_texts = texts[batch_start:batch_start + batch_size]
        capture.clear()

        inputs = tokenizer(
            batch_texts, return_tensors="pt", truncation=True,
            max_length=512, padding=True,
        ).to(device)

        with torch.no_grad():
            model(**inputs)

        attention_mask = inputs["attention_mask"]
        for b_idx in range(len(batch_texts)):
            last_pos = int(attention_mask[b_idx].sum().item()) - 1
            for l in capture.layer_indices:
                act = capture.activations[l][b_idx, last_pos, :].numpy()
                all_results[batch_start + b_idx][l] = act

    return all_results


def method_generation_fixed(model, tokenizer, capture, text, device):
    capture.clear()
    prompt = f"A researcher is thinking through a scientific problem. Here is their reasoning so far:\n\n{text}\n\nThe researcher continues:"
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=384).to(device)
    prompt_len = inputs["input_ids"].shape[1]
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=128, do_sample=False)
    capture.clear()
    with torch.no_grad():
        model(outputs)
    results = {}
    for l in capture.layer_indices:
        act = capture.activations[l]
        gen_act = act[0, prompt_len:, :]
        if gen_act.shape[0] > 4:
            skip = max(1, int(gen_act.shape[0] * 0.25))
            gen_act = gen_act[skip:, :]
        results[l] = gen_act.mean(dim=0).numpy()
    return results


def method_last_token(model, tokenizer, capture, text, device):
    capture.clear()
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(device)
    with torch.no_grad():
        model(**inputs)
    results = {}
    for l in capture.layer_indices:
        act = capture.activations[l][0, -1, :].numpy()
        results[l] = act
    return results


# ─── Analysis ────────────────────────────────────────────────────────────────

def compute_whitening(neutral_activations, variance_explained=0.5):
    X = np.stack(neutral_activations)
    pca = PCA()
    pca.fit(X)
    cumvar = np.cumsum(pca.explained_variance_ratio_)
    n_components = np.searchsorted(cumvar, variance_explained) + 1
    return pca.components_[:n_components], n_components


def apply_whitening(activation, components):
    result = activation.copy()
    for pc in components:
        result -= np.dot(result, pc) * pc
    return result


def compute_virtue_vector(virtuous_acts, neutral_acts):
    return np.mean(np.stack(virtuous_acts), axis=0) - np.mean(np.stack(neutral_acts), axis=0)


def evaluate_separation(virtuous_acts, non_virtuous_acts, neutral_acts, virtue_vector):
    results = {}

    def project(act):
        return np.dot(act, virtue_vector) / (np.linalg.norm(virtue_vector) + 1e-10)

    v_proj = [project(a) for a in virtuous_acts]
    nv_proj = [project(a) for a in non_virtuous_acts]
    results["separation"] = float(np.mean(v_proj) - np.mean(nv_proj))

    def cos_sim(a, b):
        return 1 - cosine_dist(a, b)

    v_cos = [cos_sim(a, virtue_vector) for a in virtuous_acts]
    nv_cos = [cos_sim(a, virtue_vector) for a in non_virtuous_acts]
    results["cosine_diff"] = float(np.mean(v_cos) - np.mean(nv_cos))

    X = np.vstack([np.stack(virtuous_acts), np.stack(non_virtuous_acts)])
    y = np.array([1] * len(virtuous_acts) + [0] * len(non_virtuous_acts))

    if len(y) >= 4:
        loo = LeaveOneOut()
        preds = []
        for train_idx, test_idx in loo.split(X):
            clf = LogisticRegression(max_iter=1000, C=1.0)
            clf.fit(X[train_idx], y[train_idx])
            preds.append(clf.predict(X[test_idx])[0])
        results["probe_accuracy"] = float(accuracy_score(y, preds))
    else:
        results["probe_accuracy"] = None

    return results


def save_vectors(model_name, corpus_name, method_name, layer_idx,
                 vv_raw, vv_whitened, whitening_comps, metadata):
    """Save virtue vectors and metadata as .npy and .json files."""
    vec_dir = RESULTS_DIR / "vectors" / model_name / corpus_name / method_name
    vec_dir.mkdir(parents=True, exist_ok=True)

    np.save(vec_dir / f"layer_{layer_idx}_virtue_vector.npy", vv_whitened)
    np.save(vec_dir / f"layer_{layer_idx}_virtue_vector_raw.npy", vv_raw)
    if whitening_comps is not None:
        np.save(vec_dir / f"layer_{layer_idx}_whitening_components.npy", whitening_comps)

    with open(vec_dir / f"layer_{layer_idx}_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Phronesis MVP v2")
    parser.add_argument("--model", default="gemma-2-2b-it", choices=list(MODEL_CONFIGS.keys()))
    parser.add_argument("--method", default="all",
                        choices=["comprehension", "generation", "last_token", "all"])
    parser.add_argument("--layers", default="middle",
                        choices=["middle", "all", "sweep"])
    parser.add_argument("--whitening-var", type=float, default=0.5)
    parser.add_argument("--corpus", type=str, default=None,
                        help="Override corpus directory (default: corpus/triplets)")
    parser.add_argument("--save-vectors", action="store_true",
                        help="Save virtue vectors as .npy files for steering")
    parser.add_argument("--batch-size", type=int, default=6,
                        help="Batch size for batched extraction (default: 6)")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Phronesis MVP v2 — Virtue Vector Extraction")
    print(f"{'='*60}")

    model, tokenizer, device = load_model(args.model)

    # Resolve layer list via the configured accessor (handles multimodal wrappers like Gemma 4)
    _cfg = MODEL_CONFIGS[args.model]
    _layers_obj = model
    for _attr in _cfg["layer_accessor"].split("."):
        _layers_obj = getattr(_layers_obj, _attr)
    num_layers = len(_layers_obj)
    # hidden_size lives under text_config for multimodal architectures
    hidden_dim = getattr(model.config, "hidden_size",
                         getattr(getattr(model.config, "text_config", None), "hidden_size", None))
    print(f"Architecture: {num_layers} layers, {hidden_dim} hidden dim")

    # Layer selection
    if args.layers == "middle":
        mid = num_layers // 2
        layer_indices = [mid - 2, mid, mid + 2]
    elif args.layers == "sweep":
        layer_indices = list(range(2, num_layers - 1, 2))
    else:
        layer_indices = list(range(num_layers))
    print(f"Layers: {layer_indices}")

    # Method selection
    methods = {
        "comprehension": method_comprehension,
        "generation": method_generation_fixed,
        "last_token": method_last_token,
    }
    if args.method == "all":
        active_methods = methods
    else:
        active_methods = {args.method: methods[args.method]}

    # Load corpus
    corpus_dir = Path(args.corpus) if args.corpus else CORPUS_DIR
    corpus_name = corpus_dir.name
    triplets = load_triplets(corpus_dir)
    print(f"Triplets: {len(triplets)} (from {corpus_name})")

    if len(triplets) < 3:
        print("ERROR: Need at least 3 triplets")
        sys.exit(1)

    # Progress file for dashboard
    progress_file = RESULTS_DIR / "extraction_progress.json"

    def write_progress(method, triplet_idx, total_triplets, phase="extracting"):
        prog = {
            "model": args.model,
            "corpus": corpus_name,
            "method": method,
            "triplet": triplet_idx,
            "total_triplets": total_triplets,
            "methods_order": list(active_methods.keys()),
            "phase": phase,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }
        with open(progress_file, "w") as f:
            json.dump(prog, f)

    # Run each method
    all_results = {}

    for method_name, method_fn in active_methods.items():
        print(f"\n{'─'*60}")
        print(f"Method: {method_name}")
        print(f"{'─'*60}")

        # Process ONE LAYER AT A TIME to keep memory bounded
        # Instead of accumulating all layers × all triplets in memory,
        # we loop: for each layer → process all triplets → analyze → save → free
        method_results = {}
        best_probe = 0
        best_layer = None

        for li, l in enumerate(layer_indices):
            # Skip if already saved (resume support)
            if args.save_vectors:
                meta_path = RESULTS_DIR / "vectors" / args.model / corpus_name / method_name / f"layer_{l}_metadata.json"
                if meta_path.exists():
                    try:
                        with open(meta_path) as f:
                            saved = json.load(f)
                        method_results[l] = {"raw": saved.get("raw", {}), "whitened": saved.get("whitened", {}), "n_pcs": saved.get("n_pcs", 0)}
                        wp = saved.get("whitened", {}).get("probe_accuracy")
                        if wp and wp > best_probe:
                            best_probe = wp
                            best_layer = l
                        print(f"  Layer {l} [{li+1}/{len(layer_indices)}]: SKIP (already saved, probe={wp})")
                        continue
                    except Exception:
                        pass

            capture = ActivationCapture(model, [l], layer_accessor=MODEL_CONFIGS[args.model]["layer_accessor"])  # Hook only this one layer

            # Use batched extraction for comprehension and last_token
            use_batched = method_name in ("comprehension", "last_token")
            batch_size = args.batch_size

            if use_batched:
                # Collect all texts grouped by type
                neutral_texts = [t["neutral"] for t in triplets]
                virtuous_texts = [t["virtuous"] for t in triplets]
                non_virtuous_texts = [t["non_virtuous"] for t in triplets]

                batched_fn = method_comprehension_batched if method_name == "comprehension" else method_last_token_batched

                print(f"  Layer {l} [{li+1}/{len(layer_indices)}] extracting neutral (batch_size={batch_size})...", flush=True)
                write_progress(method_name, 0, len(triplets), phase=f"layer {l} ({li+1}/{len(layer_indices)}) neutral")
                neutral_results = batched_fn(model, tokenizer, capture, neutral_texts, device, batch_size)
                neutral_acts = [r[l] for r in neutral_results]

                print(f"  Layer {l} [{li+1}/{len(layer_indices)}] extracting virtuous...", flush=True)
                write_progress(method_name, 0, len(triplets), phase=f"layer {l} ({li+1}/{len(layer_indices)}) virtuous")
                virtuous_results = batched_fn(model, tokenizer, capture, virtuous_texts, device, batch_size)
                virtuous_acts = [r[l] for r in virtuous_results]

                print(f"  Layer {l} [{li+1}/{len(layer_indices)}] extracting non-virtuous...", flush=True)
                write_progress(method_name, 0, len(triplets), phase=f"layer {l} ({li+1}/{len(layer_indices)}) non-virtuous")
                nv_results = batched_fn(model, tokenizer, capture, non_virtuous_texts, device, batch_size)
                non_virtuous_acts = [r[l] for r in nv_results]

                del neutral_results, virtuous_results, nv_results
            else:
                # Sequential fallback for generation method
                neutral_acts = []
                virtuous_acts = []
                non_virtuous_acts = []

                for i, triplet in enumerate(triplets):
                    if i % 20 == 0 or i == len(triplets) - 1:
                        print(f"  Layer {l} [{li+1}/{len(layer_indices)}] triplet [{i+1}/{len(triplets)}]", flush=True)
                    write_progress(method_name, i + 1, len(triplets), phase=f"layer {l} ({li+1}/{len(layer_indices)})")
                    for ptype, ptext in [("neutral", triplet["neutral"]),
                                          ("virtuous", triplet["virtuous"]),
                                          ("non_virtuous", triplet["non_virtuous"])]:
                        acts = method_fn(model, tokenizer, capture, ptext, device)
                        {"neutral": neutral_acts, "virtuous": virtuous_acts,
                         "non_virtuous": non_virtuous_acts}[ptype].append(acts[l])

            capture.remove_hooks()

            # Analyze this layer
            n_a, v_a, nv_a = neutral_acts, virtuous_acts, non_virtuous_acts

            # Raw
            vv_raw = compute_virtue_vector(v_a, n_a)
            raw = evaluate_separation(v_a, nv_a, n_a, vv_raw)

            # Whitened
            comps, n_pcs = compute_whitening(n_a, args.whitening_var)
            v_w = [apply_whitening(a, comps) for a in v_a]
            nv_w = [apply_whitening(a, comps) for a in nv_a]
            n_w = [apply_whitening(a, comps) for a in n_a]
            vv_w = compute_virtue_vector(v_w, n_w)
            white = evaluate_separation(v_w, nv_w, n_w, vv_w)

            method_results[l] = {"raw": raw, "whitened": white, "n_pcs": int(n_pcs)}

            if white["probe_accuracy"] and white["probe_accuracy"] > best_probe:
                best_probe = white["probe_accuracy"]
                best_layer = l

            # Save vectors if requested
            if args.save_vectors:
                metadata = {
                    "layer": l,
                    "method": method_name,
                    "model": args.model,
                    "corpus": corpus_name,
                    "n_triplets": len(triplets),
                    "raw": raw,
                    "whitened": white,
                    "n_pcs": int(n_pcs),
                    "hidden_dim": hidden_dim,
                }
                save_vectors(args.model, corpus_name, method_name, l,
                             vv_raw, vv_w, comps, metadata)

            # Free memory for this layer before moving to next
            del neutral_acts, virtuous_acts, non_virtuous_acts
            del n_a, v_a, nv_a, vv_raw, v_w, nv_w, n_w, vv_w, comps
            import gc; gc.collect()

            wp = white["probe_accuracy"] or 0
            print(f"  Layer {l}: probe={wp:.0%} {'◀ BEST' if l == best_layer else ''}")

        # Print summary
        print(f"\n  {'Layer':>5} | {'Raw Probe':>9} | {'White Probe':>11} | {'Cos Diff':>8} | {'Sep':>8}")
        print(f"  {'─'*5}-+-{'─'*9}-+-{'─'*11}-+-{'─'*8}-+-{'─'*8}")
        for l in layer_indices:
            r = method_results[l]
            rp = r["raw"]["probe_accuracy"] or 0
            wp = r["whitened"]["probe_accuracy"] or 0
            cd = r["whitened"]["cosine_diff"]
            sep = r["whitened"]["separation"]
            marker = " ◀ BEST" if l == best_layer else ""
            print(f"  {l:>5} | {rp:>8.0%} | {wp:>10.0%} | {cd:>+7.4f} | {sep:>+7.3f}{marker}")

        if best_layer:
            print(f"\n  Best: layer {best_layer} whitened probe = {best_probe:.0%}")

        all_results[method_name] = {
            "per_layer": {str(l): method_results[l] for l in layer_indices},
            "best_layer": best_layer,
            "best_probe": best_probe,
        }

    # Final comparison
    print(f"\n{'='*60}")
    print("COMPARISON ACROSS METHODS")
    print(f"{'='*60}\n")

    for method_name, mr in all_results.items():
        bp = mr["best_probe"]
        bl = mr["best_layer"]
        status = "✅ VIABLE" if bp > 0.7 else "⚠️ MARGINAL" if bp > 0.55 else "❌ NOT VIABLE"
        print(f"  {method_name:20s} best={bp:.0%} at layer {bl}  {status}")

    print()
    best_method = max(all_results, key=lambda m: all_results[m]["best_probe"])
    best_overall = all_results[best_method]["best_probe"]
    if best_overall > 0.7:
        print(f"🟢 VIABLE — best method: {best_method} at {best_overall:.0%}")
    else:
        print(f"🔴 NOT VIABLE — best was {best_method} at {best_overall:.0%}")

    # Save results JSON
    corpus_suffix = ""
    if args.corpus:
        corpus_suffix = f"_{Path(args.corpus).name}"
    results_file = RESULTS_DIR / f"mvp_v2_{args.model.replace('/', '_')}{corpus_suffix}.json"
    serializable = {}
    for m, mr in all_results.items():
        serializable[m] = {
            "best_layer": mr["best_layer"],
            "best_probe": mr["best_probe"],
            "per_layer": {str(l): v for l, v in mr["per_layer"].items()},
        }
    with open(results_file, "w") as f:
        json.dump(serializable, f, indent=2)
    print(f"Results saved to {results_file}")

    # Save extraction summary if vectors were saved
    if args.save_vectors:
        summary_dir = RESULTS_DIR / "vectors" / args.model / corpus_name
        summary = {
            "model": args.model,
            "corpus": corpus_name,
            "n_triplets": len(triplets),
            "hidden_dim": hidden_dim,
            "num_layers": num_layers,
            "methods": {}
        }
        for m, mr in all_results.items():
            summary["methods"][m] = {
                "best_layer": mr["best_layer"],
                "best_probe": mr["best_probe"],
                "per_layer": {
                    str(l): {
                        "probe_accuracy": mr["per_layer"][str(l)]["whitened"]["probe_accuracy"],
                        "separation": mr["per_layer"][str(l)]["whitened"]["separation"],
                        "cosine_diff": mr["per_layer"][str(l)]["whitened"]["cosine_diff"],
                    }
                    for l in [int(k) for k in mr["per_layer"].keys()]
                }
            }
        with open(summary_dir / "extraction_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        print(f"Extraction summary saved to {summary_dir / 'extraction_summary.json'}")
        print(f"Vectors saved to {summary_dir}/")


if __name__ == "__main__":
    main()
