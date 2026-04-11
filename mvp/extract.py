"""
Phronesis MVP — Viability Test for Virtue Vector Extraction

Tests whether we can extract a meaningful direction in activation space
that distinguishes "calibrated confidence" reasoning from neutral/non-calibrated
reasoning in a small language model.

Usage:
    python extract.py --model gemma-2-2b-it [--comprehension] [--generation]

Models supported (swap with --model):
    gemma-2-2b-it    (default, F73-recommended for steering)
    gemma-4-E4B-it   (target model, needs int4 on 16GB Mac)
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

# ─── Config ───────────────────────────────────────────────────────────────────

CORPUS_DIR = Path(__file__).parent.parent / "corpus" / "triplets"
MODELS_DIR = Path(__file__).parent / "models"
RESULTS_DIR = Path(__file__).parent / "results"

MODEL_CONFIGS = {
    "gemma-2-2b-it": {
        "path": "models/gemma-2-2b-it",
        "hf_id": "google/gemma-2-2b-it",
        "num_layers": 26,
        "hidden_dim": 2304,
        "dtype": torch.float16,
        "middle_layer_frac": 0.5,  # extract from ~50% depth
    },
    "gemma-4-E4B-it": {
        "path": "models/gemma-4-E4B-it",
        "hf_id": "google/gemma-4-E4B-it",
        "num_layers": 36,  # approximate, will verify on load
        "hidden_dim": 2560,  # approximate
        "dtype": torch.float16,
        "middle_layer_frac": 0.5,
    },
}


# ─── Activation Capture ──────────────────────────────────────────────────────

class ActivationCapture:
    """Captures residual stream activations at specified layers via forward hooks."""

    def __init__(self, model, layer_indices):
        self.activations = {}
        self.hooks = []
        self.layer_indices = layer_indices

        # Register hooks on the specified transformer layers
        layers = model.model.layers  # HF Gemma architecture
        for idx in layer_indices:
            hook = layers[idx].register_forward_hook(self._make_hook(idx))
            self.hooks.append(hook)

    def _make_hook(self, layer_idx):
        def hook_fn(module, input, output):
            # output is a tuple; first element is the hidden states
            hidden = output[0] if isinstance(output, tuple) else output
            # Store as float32 for numerical stability in PCA
            self.activations[layer_idx] = hidden.detach().float().cpu()
        return hook_fn

    def clear(self):
        self.activations = {}

    def remove_hooks(self):
        for h in self.hooks:
            h.remove()
        self.hooks = []

    def get_token_averaged(self, layer_idx, skip_tokens=0):
        """Get token-averaged activation for a layer, optionally skipping early tokens."""
        act = self.activations[layer_idx]  # shape: (1, seq_len, hidden_dim)
        act = act[0, skip_tokens:, :]  # shape: (remaining_tokens, hidden_dim)
        return act.mean(dim=0).numpy()  # shape: (hidden_dim,)


# ─── Passage Loading ─────────────────────────────────────────────────────────

def load_triplets(corpus_dir):
    """Load all triplet passages from the corpus directory."""
    triplets = []
    triplet_dirs = sorted(corpus_dir.iterdir())

    for td in triplet_dirs:
        if not td.is_dir():
            continue

        neutral_path = td / "neutral.md"
        virtuous_path = td / "virtuous.md"
        non_virtuous_path = td / "non-virtuous.md"

        if not all(p.exists() for p in [neutral_path, virtuous_path, non_virtuous_path]):
            print(f"  Skipping incomplete triplet: {td.name}")
            continue

        triplets.append({
            "id": td.name,
            "neutral": neutral_path.read_text().strip(),
            "virtuous": virtuous_path.read_text().strip(),
            "non_virtuous": non_virtuous_path.read_text().strip(),
        })

    return triplets


# ─── Extraction Methods ──────────────────────────────────────────────────────

def extract_comprehension(model, tokenizer, capture, text, device, skip_frac=0.25):
    """
    Comprehension-based extraction: feed the passage as input,
    extract token-averaged activations (skipping the first skip_frac of tokens).
    This is Anthropic's original method.
    """
    capture.clear()
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(device)

    with torch.no_grad():
        model(**inputs)

    seq_len = inputs["input_ids"].shape[1]
    skip = max(1, int(seq_len * skip_frac))

    results = {}
    for layer_idx in capture.layer_indices:
        results[layer_idx] = capture.get_token_averaged(layer_idx, skip_tokens=skip)

    return results


def extract_generation(model, tokenizer, capture, text, device, gen_tokens=64, skip_frac=0.25):
    """
    Generation-based extraction: feed the passage as a prompt,
    let the model generate a continuation, extract activations from the
    generation phase only.
    This is the F73-recommended method for small models.
    """
    capture.clear()
    prompt = f"Continue this researcher's reasoning:\n\n{text}\n\n"
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=448).to(device)
    prompt_len = inputs["input_ids"].shape[1]

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=gen_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )

    # Now run forward pass on the full sequence (prompt + generation) to get activations
    capture.clear()
    with torch.no_grad():
        model(outputs)

    # Extract activations only from the generated tokens (after the prompt)
    results = {}
    for layer_idx in capture.layer_indices:
        act = capture.activations[layer_idx]  # (1, total_seq_len, hidden_dim)
        gen_act = act[0, prompt_len:, :]  # only the generated part
        skip = max(1, int(gen_act.shape[0] * skip_frac))
        gen_act = gen_act[skip:, :]  # skip early generation tokens
        if gen_act.shape[0] == 0:
            gen_act = act[0, prompt_len:, :]  # fallback: use all generated
        results[layer_idx] = gen_act.mean(dim=0).float().numpy()

    return results


# ─── Whitening ───────────────────────────────────────────────────────────────

def compute_whitening(neutral_activations, variance_explained=0.5):
    """
    Compute the whitening projection that removes dominant directions
    from neutral activations (the anisotropy fix).

    Returns the PCA components to project out and the number of components.
    """
    # Stack neutral activations: shape (n_passages, hidden_dim)
    X = np.stack(neutral_activations)

    # Fit PCA
    pca = PCA()
    pca.fit(X)

    # Find how many components explain the target variance
    cumvar = np.cumsum(pca.explained_variance_ratio_)
    n_components = np.searchsorted(cumvar, variance_explained) + 1

    print(f"  Whitening: projecting out {n_components} PCs "
          f"(explain {cumvar[n_components-1]:.1%} of neutral variance)")

    return pca.components_[:n_components], n_components


def apply_whitening(activation, components):
    """Project out the specified principal components from an activation vector."""
    result = activation.copy()
    for pc in components:
        result -= np.dot(result, pc) * pc
    return result


# ─── Analysis ────────────────────────────────────────────────────────────────

def compute_virtue_vector(virtuous_acts, neutral_acts):
    """Difference-of-means: virtuous centroid minus neutral centroid."""
    v_mean = np.mean(np.stack(virtuous_acts), axis=0)
    n_mean = np.mean(np.stack(neutral_acts), axis=0)
    return v_mean - n_mean


def evaluate_separation(virtuous_acts, non_virtuous_acts, neutral_acts, virtue_vector):
    """
    Evaluate how well the virtue vector separates the three passage types.
    Returns cosine similarities and linear probe accuracy.
    """
    results = {}

    # Project each passage onto the virtue vector direction
    def project(act):
        return np.dot(act, virtue_vector) / (np.linalg.norm(virtue_vector) + 1e-10)

    v_proj = [project(a) for a in virtuous_acts]
    nv_proj = [project(a) for a in non_virtuous_acts]
    n_proj = [project(a) for a in neutral_acts]

    results["mean_projection"] = {
        "virtuous": float(np.mean(v_proj)),
        "neutral": float(np.mean(n_proj)),
        "non_virtuous": float(np.mean(nv_proj)),
    }

    # Separation: virtuous should project higher than non-virtuous
    results["separation"] = float(np.mean(v_proj) - np.mean(nv_proj))

    # Cosine similarity between virtue vector and individual passages
    def cos_sim(a, b):
        return 1 - cosine_dist(a, b)

    v_cos = [cos_sim(a, virtue_vector) for a in virtuous_acts]
    nv_cos = [cos_sim(a, virtue_vector) for a in non_virtuous_acts]
    results["cosine_similarity"] = {
        "virtuous_mean": float(np.mean(v_cos)),
        "non_virtuous_mean": float(np.mean(nv_cos)),
        "difference": float(np.mean(v_cos) - np.mean(nv_cos)),
    }

    # Linear probe: can we classify virtuous vs non-virtuous from activations?
    X = np.vstack([np.stack(virtuous_acts), np.stack(non_virtuous_acts)])
    y = np.array([1] * len(virtuous_acts) + [0] * len(non_virtuous_acts))

    if len(y) >= 4:  # need minimum samples for LOO
        loo = LeaveOneOut()
        preds = []
        for train_idx, test_idx in loo.split(X):
            clf = LogisticRegression(max_iter=1000, C=1.0)
            clf.fit(X[train_idx], y[train_idx])
            preds.append(clf.predict(X[test_idx])[0])
        results["linear_probe_loo_accuracy"] = float(accuracy_score(y, preds))
    else:
        results["linear_probe_loo_accuracy"] = None

    return results


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Phronesis MVP: Virtue Vector Extraction Viability Test")
    parser.add_argument("--model", default="gemma-2-2b-it", choices=list(MODEL_CONFIGS.keys()))
    parser.add_argument("--comprehension", action="store_true", help="Test comprehension-based extraction")
    parser.add_argument("--generation", action="store_true", help="Test generation-based extraction")
    parser.add_argument("--both", action="store_true", help="Test both methods (default)")
    parser.add_argument("--whitening-var", type=float, default=0.5,
                        help="Fraction of neutral variance to project out (default: 0.5)")
    args = parser.parse_args()

    if not args.comprehension and not args.generation:
        args.both = True
    if args.both:
        args.comprehension = True
        args.generation = True

    config = MODEL_CONFIGS[args.model]
    RESULTS_DIR.mkdir(exist_ok=True)

    # ── Load model ──
    print(f"\n{'='*60}")
    print(f"Phronesis MVP — Virtue Vector Extraction Viability Test")
    print(f"{'='*60}")
    print(f"\nModel: {args.model}")

    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_path = MODELS_DIR / config["path"].split("/")[-1]
    if not model_path.exists():
        model_path = config["hf_id"]
        print(f"Loading from HuggingFace: {model_path}")
    else:
        print(f"Loading from local: {model_path}")

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=config["dtype"],
        device_map=device,
    )
    model.eval()

    # Detect actual number of layers
    num_layers = len(model.model.layers)
    print(f"Layers: {num_layers}")
    hidden_dim = model.config.hidden_size
    print(f"Hidden dim: {hidden_dim}")

    # Select extraction layers: middle ± 2
    mid = int(num_layers * config["middle_layer_frac"])
    layer_indices = [max(0, mid - 2), mid, min(num_layers - 1, mid + 2)]
    print(f"Extraction layers: {layer_indices} (middle={mid})")

    # ── Load corpus ──
    print(f"\nLoading triplets from {CORPUS_DIR}...")
    triplets = load_triplets(CORPUS_DIR)
    print(f"Loaded {len(triplets)} triplets:")
    for t in triplets:
        print(f"  {t['id']}")

    if len(triplets) < 3:
        print("ERROR: Need at least 3 triplets for meaningful analysis.")
        sys.exit(1)

    # ── Run extraction ──
    methods = []
    if args.comprehension:
        methods.append(("comprehension", extract_comprehension))
    if args.generation:
        methods.append(("generation", extract_generation))

    all_results = {}

    for method_name, extract_fn in methods:
        print(f"\n{'─'*60}")
        print(f"Method: {method_name}")
        print(f"{'─'*60}")

        capture = ActivationCapture(model, layer_indices)

        # Extract activations for each passage
        neutral_acts = {l: [] for l in layer_indices}
        virtuous_acts = {l: [] for l in layer_indices}
        non_virtuous_acts = {l: [] for l in layer_indices}

        for i, triplet in enumerate(triplets):
            print(f"\n  Triplet {i+1}/{len(triplets)}: {triplet['id']}")

            for passage_type, passage_text in [
                ("neutral", triplet["neutral"]),
                ("virtuous", triplet["virtuous"]),
                ("non_virtuous", triplet["non_virtuous"]),
            ]:
                print(f"    {passage_type}...", end=" ", flush=True)

                if method_name == "comprehension":
                    acts = extract_comprehension(model, tokenizer, capture, passage_text, device)
                else:
                    acts = extract_generation(model, tokenizer, capture, passage_text, device)

                for l in layer_indices:
                    if passage_type == "neutral":
                        neutral_acts[l].append(acts[l])
                    elif passage_type == "virtuous":
                        virtuous_acts[l].append(acts[l])
                    else:
                        non_virtuous_acts[l].append(acts[l])

                print("done")

        capture.remove_hooks()

        # ── Analyze each layer ──
        method_results = {}

        for layer_idx in layer_indices:
            print(f"\n  Layer {layer_idx}:")

            n_acts = neutral_acts[layer_idx]
            v_acts = virtuous_acts[layer_idx]
            nv_acts = non_virtuous_acts[layer_idx]

            # ── Raw (no whitening) ──
            print(f"    Raw (no whitening):")
            virtue_vec_raw = compute_virtue_vector(v_acts, n_acts)
            raw_results = evaluate_separation(v_acts, nv_acts, n_acts, virtue_vec_raw)
            print(f"      Separation: {raw_results['separation']:.4f}")
            print(f"      Cosine diff: {raw_results['cosine_similarity']['difference']:.4f}")
            print(f"      Probe accuracy: {raw_results['linear_probe_loo_accuracy']}")

            # ── Whitened ──
            print(f"    Whitened (project out {args.whitening_var:.0%} variance):")
            components, n_pcs = compute_whitening(n_acts, args.whitening_var)

            v_white = [apply_whitening(a, components) for a in v_acts]
            nv_white = [apply_whitening(a, components) for a in nv_acts]
            n_white = [apply_whitening(a, components) for a in n_acts]

            virtue_vec_white = compute_virtue_vector(v_white, n_white)
            white_results = evaluate_separation(v_white, nv_white, n_white, virtue_vec_white)
            print(f"      Separation: {white_results['separation']:.4f}")
            print(f"      Cosine diff: {white_results['cosine_similarity']['difference']:.4f}")
            print(f"      Probe accuracy: {white_results['linear_probe_loo_accuracy']}")

            method_results[f"layer_{layer_idx}"] = {
                "raw": raw_results,
                "whitened": white_results,
                "n_pcs_removed": int(n_pcs),
            }

        all_results[method_name] = method_results

    # ── Summary ──
    print(f"\n{'='*60}")
    print("VIABILITY SUMMARY")
    print(f"{'='*60}\n")

    viable = False
    for method_name, method_results in all_results.items():
        print(f"Method: {method_name}")
        for layer_key, layer_results in method_results.items():
            raw = layer_results["raw"]
            white = layer_results["whitened"]
            probe_acc = white["linear_probe_loo_accuracy"]

            status = "✅" if (probe_acc and probe_acc > 0.7) else "⚠️" if (probe_acc and probe_acc > 0.5) else "❌"
            if probe_acc and probe_acc > 0.7:
                viable = True

            print(f"  {layer_key}:")
            print(f"    Raw  — sep={raw['separation']:+.4f}  cos_diff={raw['cosine_similarity']['difference']:+.4f}  probe={raw['linear_probe_loo_accuracy']}")
            print(f"    White— sep={white['separation']:+.4f}  cos_diff={white['cosine_similarity']['difference']:+.4f}  probe={probe_acc}  {status}")
        print()

    if viable:
        print("🟢 VIABLE: At least one configuration achieves >70% LOO probe accuracy.")
        print("   The model encodes a direction that distinguishes virtuous from non-virtuous passages.")
        print("   Proceed to full corpus generation and steering experiments.")
    else:
        print("🔴 NOT VIABLE at this configuration. Consider:")
        print("   - Trying a larger model (Gemma 4 E4B on GCP)")
        print("   - More aggressive whitening (--whitening-var 0.7)")
        print("   - Broader concept extraction (pool all virtuous vs all non-virtuous)")
        print("   - SAE-based extraction instead of difference-of-means")

    # Save results
    results_file = RESULTS_DIR / f"mvp_{args.model.replace('/', '_')}.json"
    with open(results_file, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved to {results_file}")


if __name__ == "__main__":
    main()
