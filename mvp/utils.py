"""
Phronesis shared utilities — model configs, activation capture, model loading.

Used by extract_v2.py, generate_corpus.py, and steer.py.
"""

from pathlib import Path

import torch

MODELS_DIR = Path(__file__).parent / "models"
RESULTS_DIR = Path(__file__).parent / "results"
CORPUS_DIR = Path(__file__).parent.parent / "corpus" / "triplets"

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
        "dtype": torch.bfloat16,  # Gemma 4 ships bf16 weights
        "layer_accessor": "model.language_model.layers",  # multimodal Gemma4ForConditionalGeneration wrapper
        "thinking": True,
        "num_layers": 42,
        "hidden_dim": 2560,
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
    "qwen3-4b": {
        "hf_id": "Qwen/Qwen3-4B",
        "local_dir": "Qwen3-4B",
        "dtype": torch.float16,
        "layer_accessor": "model.layers",
        "thinking": True,           # has <think>...</think> tokens
        "num_layers": 36,
        "hidden_dim": 2560,
    },
}


class ActivationCapture:
    """Captures residual stream activations at specified layers via forward hooks."""

    def __init__(self, model, layer_indices, layer_accessor="model.layers"):
        self.activations = {}
        self.hooks = []
        self.layer_indices = layer_indices
        # Walk dotted path, e.g. "model.language_model.layers" for Gemma 4
        layers = model
        for attr in layer_accessor.split("."):
            layers = getattr(layers, attr)
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


def get_device():
    """Detect best available device."""
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def load_model(model_name, device=None):
    """Load a model and tokenizer, returns (model, tokenizer, device_str)."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if device is None:
        device = get_device()

    config = MODEL_CONFIGS[model_name]
    model_path = MODELS_DIR / config["local_dir"]
    if not model_path.exists():
        model_path = config["hf_id"]
    else:
        model_path = str(model_path)

    print(f"Loading model: {model_name} ({model_path})")
    print(f"Device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=config["dtype"],
        device_map=device if device != "mps" else None,
        trust_remote_code=True,
    )
    if device == "mps":
        model = model.to("mps")
    model.eval()

    return model, tokenizer, device


def load_triplets(corpus_dir):
    """Load triplets from a corpus directory."""
    corpus_dir = Path(corpus_dir)
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
