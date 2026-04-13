"""
Phronesis — Activation steering with three methods.

Loads a pre-extracted virtue vector and steers model generation by
injecting it into the residual stream during inference.

Methods:
  - additive (CAA): h' = h + alpha * v_normalized
  - spherical: norm-preserving rotation toward v
  - conditional: additive only when projection > threshold

Usage:
    python steer.py --model gemma-2-2b-it \
      --vector results/vectors/.../layer_13_virtue_vector.npy \
      --layer 13 --method additive --sweep \
      --prompts ../corpus/eval-prompts/calibrated-confidence.json \
      --output results/steering/gemma_additive_L13.json
"""

import argparse
import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

from utils import MODEL_CONFIGS, RESULTS_DIR, load_model


# ─── Steering hooks ──────────────────────────────────────────────────────────

class AdditiveSteeringHook:
    """CAA-style additive steering: h' = h + alpha * v_normalized"""

    def __init__(self, layer_idx, virtue_vector, alpha):
        self.layer_idx = layer_idx
        self.alpha = alpha
        v = torch.tensor(virtue_vector, dtype=torch.float32)
        self.v_normalized = (v / (v.norm() + 1e-10)).unsqueeze(0).unsqueeze(0)
        self.handle = None

    def hook_fn(self, module, input, output):
        hidden = output[0] if isinstance(output, tuple) else output
        device = hidden.device
        v = self.v_normalized.to(device).to(hidden.dtype)
        hidden = hidden + self.alpha * v
        if isinstance(output, tuple):
            return (hidden,) + output[1:]
        return hidden

    def attach(self, model):
        layer = model.model.layers[self.layer_idx]
        self.handle = layer.register_forward_hook(self.hook_fn)

    def detach(self):
        if self.handle:
            self.handle.remove()
            self.handle = None


class SphericalSteeringHook:
    """Norm-preserving rotation: rotate h toward v by angle alpha (radians)."""

    def __init__(self, layer_idx, virtue_vector, alpha):
        self.layer_idx = layer_idx
        self.alpha = alpha
        v = torch.tensor(virtue_vector, dtype=torch.float32)
        self.v_unit = v / (v.norm() + 1e-10)
        self.handle = None

    def hook_fn(self, module, input, output):
        hidden = output[0] if isinstance(output, tuple) else output
        device = hidden.device
        dtype = hidden.dtype
        v_unit = self.v_unit.to(device).to(dtype)

        h_flat = hidden.view(-1, hidden.shape[-1])
        h_norm = h_flat.norm(dim=-1, keepdim=True).clamp(min=1e-10)
        h_unit = h_flat / h_norm

        # Project h onto v to get parallel component
        proj = (h_unit * v_unit.unsqueeze(0)).sum(dim=-1, keepdim=True)
        h_parallel = proj * v_unit.unsqueeze(0)
        h_perp = h_unit - h_parallel
        h_perp_norm = h_perp.norm(dim=-1, keepdim=True).clamp(min=1e-10)
        h_perp_unit = h_perp / h_perp_norm

        # Rotate by alpha radians in the h-v plane
        cos_a = math.cos(self.alpha)
        sin_a = math.sin(self.alpha)
        h_rotated_unit = cos_a * h_unit + sin_a * (
            v_unit.unsqueeze(0) - proj * h_unit
        ) / (1 - proj * proj + 1e-10).sqrt()

        # Simpler formulation: rotate in the plane spanned by h_unit and v_unit
        h_rotated_unit = cos_a * h_unit + sin_a * h_perp_norm / (h_perp_norm + 1e-10) * (
            (v_unit.unsqueeze(0) - h_parallel) / (h_perp_norm + 1e-10)
        )

        # Actually, the cleanest formulation using Rodrigues:
        # h' = cos(alpha) * h_perp_unit + sin(alpha) * v_unit (in the h-v plane)
        # Then scale back to h's norm
        # But we want to rotate h TOWARD v, so:
        h_new_unit = h_perp_unit * math.cos(math.pi/2 - self.alpha) + v_unit.unsqueeze(0) * math.sin(math.pi/2 - self.alpha)
        # Wait, let me use the clean version:
        # theta_current = angle between h and v = arccos(proj)
        # theta_new = theta_current - alpha (rotate alpha radians toward v)
        theta_current = torch.acos(proj.clamp(-1 + 1e-7, 1 - 1e-7))
        theta_new = (theta_current - self.alpha).clamp(min=0)

        # Reconstruct: h_new = cos(theta_new) * v + sin(theta_new) * h_perp_unit
        h_new_unit = torch.cos(theta_new) * v_unit.unsqueeze(0) + torch.sin(theta_new) * h_perp_unit
        hidden_new = h_new_unit * h_norm
        hidden_new = hidden_new.view_as(hidden)

        if isinstance(output, tuple):
            return (hidden_new,) + output[1:]
        return hidden_new

    def attach(self, model):
        layer = model.model.layers[self.layer_idx]
        self.handle = layer.register_forward_hook(self.hook_fn)

    def detach(self):
        if self.handle:
            self.handle.remove()
            self.handle = None


class ConditionalSteeringHook:
    """Additive steering gated by projection onto condition vector."""

    def __init__(self, layer_idx, virtue_vector, alpha, condition_vector=None, threshold=0.0):
        self.layer_idx = layer_idx
        self.alpha = alpha
        self.threshold = threshold
        v = torch.tensor(virtue_vector, dtype=torch.float32)
        self.v_normalized = (v / (v.norm() + 1e-10)).unsqueeze(0).unsqueeze(0)
        if condition_vector is not None:
            c = torch.tensor(condition_vector, dtype=torch.float32)
            self.c_unit = (c / (c.norm() + 1e-10))
        else:
            self.c_unit = (v / (v.norm() + 1e-10))
        self.handle = None

    def hook_fn(self, module, input, output):
        hidden = output[0] if isinstance(output, tuple) else output
        device = hidden.device
        dtype = hidden.dtype
        v = self.v_normalized.to(device).to(dtype)
        c = self.c_unit.to(device).to(dtype)

        # Compute projection of each token onto condition vector
        projections = (hidden * c.unsqueeze(0).unsqueeze(0)).sum(dim=-1, keepdim=True)
        mask = (projections > self.threshold).to(dtype)

        hidden = hidden + self.alpha * v * mask

        if isinstance(output, tuple):
            return (hidden,) + output[1:]
        return hidden

    def attach(self, model):
        layer = model.model.layers[self.layer_idx]
        self.handle = layer.register_forward_hook(self.hook_fn)

    def detach(self):
        if self.handle:
            self.handle.remove()
            self.handle = None


# ─── Generation ──────────────────────────────────────────────────────────────

def generate_response(model, tokenizer, prompt, device, max_new_tokens=256):
    """Generate a deterministic response from a prompt."""
    if hasattr(tokenizer, "apply_chat_template"):
        messages = [{"role": "user", "content": prompt}]
        input_text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    else:
        input_text = prompt

    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=512).to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )

    generated = outputs[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True).strip()


def compute_auto_threshold(model, tokenizer, prompts, layer_idx, virtue_vector, device):
    """Compute 50th percentile projection for conditional steering threshold."""
    from utils import ActivationCapture

    v = torch.tensor(virtue_vector, dtype=torch.float32)
    v_unit = v / (v.norm() + 1e-10)

    capture = ActivationCapture(model, [layer_idx])
    all_projections = []

    for prompt_data in prompts[:10]:  # Use first 10 prompts for calibration
        prompt = prompt_data["prompt"]
        if hasattr(tokenizer, "apply_chat_template"):
            messages = [{"role": "user", "content": prompt}]
            input_text = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        else:
            input_text = prompt

        inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=512).to(device)
        capture.clear()
        with torch.no_grad():
            model(**inputs)

        act = capture.activations[layer_idx][0]  # (seq_len, hidden_dim)
        proj = (act.float().cpu() * v_unit.unsqueeze(0)).sum(dim=-1)
        all_projections.extend(proj.numpy().tolist())

    capture.remove_hooks()
    return float(np.percentile(all_projections, 50))


# ─── Main ────────────────────────────────────────────────────────────────────

ALPHA_SWEEP = np.logspace(np.log10(0.001), np.log10(5.0), 10).tolist()

STEERING_METHODS = {
    "additive": AdditiveSteeringHook,
    "spherical": SphericalSteeringHook,
    "conditional": ConditionalSteeringHook,
}


def main():
    parser = argparse.ArgumentParser(description="Phronesis Activation Steering")
    parser.add_argument("--model", default="gemma-2-2b-it", choices=list(MODEL_CONFIGS.keys()))
    parser.add_argument("--vector", required=True, help="Path to .npy virtue vector file")
    parser.add_argument("--layer", type=int, required=True, help="Layer to steer at")
    parser.add_argument("--method", default="additive", choices=list(STEERING_METHODS.keys()))
    parser.add_argument("--alpha", type=float, default=None, help="Single alpha value")
    parser.add_argument("--sweep", action="store_true", help="Sweep 10 log-spaced alpha values")
    parser.add_argument("--prompts", required=True, help="Path to eval prompts JSON")
    parser.add_argument("--output", default=None, help="Output JSON path")
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--auto-threshold", action="store_true",
                        help="Auto-calibrate threshold for conditional steering")
    args = parser.parse_args()

    # Load virtue vector
    virtue_vector = np.load(args.vector)
    print(f"Loaded virtue vector: shape {virtue_vector.shape} from {args.vector}")

    # Load prompts
    with open(args.prompts) as f:
        prompts = json.load(f)
    print(f"Loaded {len(prompts)} evaluation prompts")

    # Determine alpha values
    if args.sweep:
        alphas = ALPHA_SWEEP
    elif args.alpha is not None:
        alphas = [args.alpha]
    else:
        alphas = [1.0]
    print(f"Alpha values: {[f'{a:.4f}' for a in alphas]}")

    # Load model
    model, tokenizer, device = load_model(args.model)

    # Auto-threshold for conditional
    threshold = 0.0
    if args.method == "conditional" and args.auto_threshold:
        print("Computing auto-threshold...")
        threshold = compute_auto_threshold(
            model, tokenizer, prompts, args.layer, virtue_vector, device
        )
        print(f"Auto-threshold: {threshold:.4f}")

    # Output structure
    output = {
        "config": {
            "model": args.model,
            "vector_path": str(args.vector),
            "layer": args.layer,
            "method": args.method,
            "alphas": alphas,
            "threshold": threshold if args.method == "conditional" else None,
            "max_tokens": args.max_tokens,
            "timestamp": datetime.now().isoformat(),
        },
        "results": []
    }

    # Generate baseline (no steering) for all prompts
    print(f"\n{'─'*60}")
    print("Generating baselines (no steering)")
    print(f"{'─'*60}")

    baselines = {}
    for i, prompt_data in enumerate(prompts):
        pid = prompt_data["id"]
        prompt = prompt_data["prompt"]
        print(f"  [{i+1}/{len(prompts)}] {pid}...", flush=True)
        response = generate_response(model, tokenizer, prompt, device, args.max_tokens)
        baselines[pid] = response

    # Generate steered responses for each alpha
    for alpha in alphas:
        print(f"\n{'─'*60}")
        print(f"Steering: {args.method}, alpha={alpha:.4f}")
        print(f"{'─'*60}")

        HookClass = STEERING_METHODS[args.method]
        if args.method == "conditional":
            hook = HookClass(args.layer, virtue_vector, alpha, threshold=threshold)
        else:
            hook = HookClass(args.layer, virtue_vector, alpha)
        hook.attach(model)

        for i, prompt_data in enumerate(prompts):
            pid = prompt_data["id"]
            prompt = prompt_data["prompt"]
            print(f"  [{i+1}/{len(prompts)}] {pid}...", flush=True)

            steered_response = generate_response(
                model, tokenizer, prompt, device, args.max_tokens
            )

            # Find or create result entry
            existing = next((r for r in output["results"] if r["prompt_id"] == pid), None)
            if existing is None:
                existing = {
                    "prompt_id": pid,
                    "prompt_text": prompt,
                    "expected_behavior": prompt_data.get("expected_behavior", ""),
                    "baseline": {
                        "response": baselines[pid],
                        "word_count": len(baselines[pid].split()),
                    },
                    "steered": {}
                }
                output["results"].append(existing)

            existing["steered"][f"{alpha:.4f}"] = {
                "response": steered_response,
                "word_count": len(steered_response.split()),
            }

        hook.detach()

    # Save results
    if args.output:
        out_path = Path(args.output)
    else:
        out_path = RESULTS_DIR / "steering" / f"{args.model}_{args.method}_L{args.layer}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {out_path}")

    # Quick summary
    print(f"\n{'='*60}")
    print("STEERING SUMMARY")
    print(f"{'='*60}")
    print(f"Method: {args.method}, Layer: {args.layer}")
    print(f"Prompts: {len(prompts)}, Alphas: {len(alphas)}")
    for alpha in alphas:
        key = f"{alpha:.4f}"
        avg_wc_baseline = np.mean([r["baseline"]["word_count"] for r in output["results"]])
        avg_wc_steered = np.mean([r["steered"][key]["word_count"] for r in output["results"]])
        print(f"  alpha={alpha:.4f}: avg words baseline={avg_wc_baseline:.0f}, steered={avg_wc_steered:.0f}")


if __name__ == "__main__":
    main()
