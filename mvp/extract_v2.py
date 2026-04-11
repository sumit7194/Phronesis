"""
Phronesis MVP v2 — Improved extraction with multiple methods and multi-model support.

Changes from v1:
- Fixed generation method (deterministic, longer, better prompt)
- Added hybrid method (comprehension of passage + model's own summary)
- Added broader layer sweep
- Multi-model support
- Neuronpedia compatibility notes

Usage:
    python extract_v2.py --model gemma-2-2b-it
    python extract_v2.py --model gemma-2-2b-it --method all --layers all
"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import accuracy_score
from scipy.spatial.distance import cosine as cosine_dist

CORPUS_DIR = Path(__file__).parent.parent / "corpus" / "triplets"
MODELS_DIR = Path(__file__).parent / "models"
RESULTS_DIR = Path(__file__).parent / "results"

MODEL_CONFIGS = {
    "gemma-2-2b-it": {
        "hf_id": "google/gemma-2-2b-it",
        "local_dir": "gemma-2-2b-it",
        "dtype": torch.float16,
        "layer_accessor": "model.layers",
    },
    "gemma-4-E4B-it": {
        "hf_id": "google/gemma-4-E4B-it",
        "local_dir": "gemma-4-E4B-it",
        "dtype": torch.float16,
        "layer_accessor": "model.layers",
    },
    "qwen-2.5-3b-it": {
        "hf_id": "Qwen/Qwen2.5-3B-Instruct",
        "local_dir": "Qwen2.5-3B-Instruct",
        "dtype": torch.float16,
        "layer_accessor": "model.layers",
    },
    "phi-3.5-mini-it": {
        "hf_id": "microsoft/Phi-3.5-mini-instruct",
        "local_dir": "Phi-3.5-mini-instruct",
        "dtype": torch.float16,
        "layer_accessor": "model.layers",
    },
}


class ActivationCapture:
    def __init__(self, model, layer_indices):
        self.activations = {}
        self.hooks = []
        self.layer_indices = layer_indices
        layers = model.model.layers
        for idx in layer_indices:
            hook = layers[idx].register_forward_hook(self._make_hook(idx))
            self.hooks.append(hook)

    def _make_hook(self, layer_idx):
        def hook_fn(module, input, output):
            hidden = output[0] if isinstance(output, tuple) else output
            self.activations[layer_idx] = hidden.detach().float().cpu()
        return hook_fn

    def clear(self):
        self.activations = {}

    def remove_hooks(self):
        for h in self.hooks:
            h.remove()


def load_triplets(corpus_dir):
    triplets = []
    for td in sorted(corpus_dir.iterdir()):
        if not td.is_dir():
            continue
        n, v, nv = td / "neutral.md", td / "virtuous.md", td / "non-virtuous.md"
        if not all(p.exists() for p in [n, v, nv]):
            continue
        triplets.append({
            "id": td.name,
            "neutral": n.read_text().strip(),
            "virtuous": v.read_text().strip(),
            "non_virtuous": nv.read_text().strip(),
        })
    return triplets


# ─── Three extraction methods ────────────────────────────────────────────────

def method_comprehension(model, tokenizer, capture, text, device):
    """
    COMPREHENSION: feed the passage, extract token-averaged activations.
    Skip first 25% of tokens (setup/topic content).
    This is what worked in v1.
    """
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


def method_generation_fixed(model, tokenizer, capture, text, device):
    """
    GENERATION (fixed): feed passage as prompt, generate deterministically,
    extract from generation tokens only.

    Fixes from v1:
    - Deterministic (temperature=0, no sampling) — removes stochastic noise
    - 128 tokens instead of 64 — more signal
    - Better prompt framing
    """
    capture.clear()
    prompt = f"A researcher is thinking through a scientific problem. Here is their reasoning so far:\n\n{text}\n\nThe researcher continues:"
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=384).to(device)
    prompt_len = inputs["input_ids"].shape[1]

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=128,
            do_sample=False,  # deterministic — same input = same output
        )

    # Forward pass on full sequence to capture activations
    capture.clear()
    with torch.no_grad():
        model(outputs)

    results = {}
    for l in capture.layer_indices:
        act = capture.activations[l]
        gen_act = act[0, prompt_len:, :]  # only generated tokens
        if gen_act.shape[0] > 4:
            skip = max(1, int(gen_act.shape[0] * 0.25))
            gen_act = gen_act[skip:, :]
        results[l] = gen_act.mean(dim=0).numpy()
    return results


def method_last_token(model, tokenizer, capture, text, device):
    """
    LAST-TOKEN: feed the passage, extract the LAST token's activation only.
    This captures the model's "summary representation" after processing
    the entire passage — similar to what Anthropic used for validation
    (the ":" token before the assistant's response).
    """
    capture.clear()
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(device)
    with torch.no_grad():
        model(**inputs)

    results = {}
    for l in capture.layer_indices:
        act = capture.activations[l][0, -1, :].numpy()  # last token only
        results[l] = act
    return results


# ─── Analysis (same as v1) ────────────────────────────────────────────────────

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

    # LOO probe
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


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Phronesis MVP v2")
    parser.add_argument("--model", default="gemma-2-2b-it", choices=list(MODEL_CONFIGS.keys()))
    parser.add_argument("--method", default="all",
                        choices=["comprehension", "generation", "last_token", "all"])
    parser.add_argument("--layers", default="middle",
                        choices=["middle", "all", "sweep"])
    parser.add_argument("--whitening-var", type=float, default=0.5)
    args = parser.parse_args()

    config = MODEL_CONFIGS[args.model]
    RESULTS_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Phronesis MVP v2 — Virtue Vector Extraction")
    print(f"{'='*60}")

    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_path = MODELS_DIR / config["local_dir"]
    if not model_path.exists():
        model_path = config["hf_id"]
    print(f"Model: {args.model} ({model_path})")

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_path, dtype=config["dtype"], device_map=device,
    )
    model.eval()

    num_layers = len(model.model.layers)
    hidden_dim = model.config.hidden_size
    print(f"Architecture: {num_layers} layers, {hidden_dim} hidden dim")

    # Layer selection
    if args.layers == "middle":
        mid = num_layers // 2
        layer_indices = [mid - 2, mid, mid + 2]
    elif args.layers == "sweep":
        # Every 2 layers across the full depth
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
    triplets = load_triplets(CORPUS_DIR)
    print(f"Triplets: {len(triplets)}")

    if len(triplets) < 3:
        print("ERROR: Need at least 3 triplets")
        sys.exit(1)

    # Run each method
    all_results = {}

    for method_name, method_fn in active_methods.items():
        print(f"\n{'─'*60}")
        print(f"Method: {method_name}")
        print(f"{'─'*60}")

        capture = ActivationCapture(model, layer_indices)

        neutral_acts = {l: [] for l in layer_indices}
        virtuous_acts = {l: [] for l in layer_indices}
        non_virtuous_acts = {l: [] for l in layer_indices}

        for i, triplet in enumerate(triplets):
            print(f"  [{i+1}/{len(triplets)}] {triplet['id'][:40]}...", flush=True)
            for ptype, ptext in [("neutral", triplet["neutral"]),
                                  ("virtuous", triplet["virtuous"]),
                                  ("non_virtuous", triplet["non_virtuous"])]:
                acts = method_fn(model, tokenizer, capture, ptext, device)
                for l in layer_indices:
                    {"neutral": neutral_acts, "virtuous": virtuous_acts,
                     "non_virtuous": non_virtuous_acts}[ptype][l].append(acts[l])

        capture.remove_hooks()

        # Analyze each layer
        method_results = {}
        best_probe = 0
        best_layer = None

        for l in layer_indices:
            n_a, v_a, nv_a = neutral_acts[l], virtuous_acts[l], non_virtuous_acts[l]

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

        # Print summary for this method
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

    # Save
    results_file = RESULTS_DIR / f"mvp_v2_{args.model.replace('/', '_')}.json"
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


if __name__ == "__main__":
    main()
