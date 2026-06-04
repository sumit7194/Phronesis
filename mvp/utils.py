"""
Phronesis shared utilities — model configs, activation capture, model loading.

Used by extract_v2.py, generate_corpus.py, and steer.py.
"""

from pathlib import Path

import torch

MODELS_DIR = Path(__file__).parent / "models"
RESULTS_DIR = Path(__file__).parent / "results"
CORPUS_DIR = Path(__file__).parent.parent / "corpus" / "triplets"

# MVP-combined corpus paths (80 triplets, curated per corpus/mvp-combined/LEDGER.md)
MVP_COMBINED_EG_DIR = Path(__file__).parent.parent / "corpus" / "mvp-combined" / "triplets-evidence-grounding"
MVP_COMBINED_RT_DIR = Path(__file__).parent.parent / "corpus" / "mvp-combined" / "triplets-reasoning-transparency"

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
        "attn_implementation": "sdpa",  # Gemma4 defaults to eager which is ~20× slower on L4
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
        "dtype": torch.bfloat16,         # Phi-3.5 ships bf16
        "layer_accessor": "model.layers",
        "thinking": False,               # No <think>/</think> tags
        "num_layers": 32,
        "hidden_dim": 3072,
        # Phi-3.5's bundled modeling_phi3.py uses removed DynamicCache.from_legacy_cache;
        # use built-in transformers Phi3 implementation instead.
        "trust_remote_code": False,
    },
    "phi-4-mini-reasoning": {
        # Microsoft Phi-4-mini-reasoning (3.8B) — same architecture as Phi-3.5-mini
        # but reasoning-tuned with native <think>/</think> trace emission.
        # Smoke-tested Day 23 evening: emits <think>...</think> via default chat template.
        # NB: forcing attn_implementation="sdpa" — without it the first run hung at 0%
        # GPU util / 759% CPU for 13 min on a single forward pass.
        "hf_id": "microsoft/Phi-4-mini-reasoning",
        "local_dir": "Phi-4-mini-reasoning",
        "dtype": torch.bfloat16,
        "layer_accessor": "model.layers",
        "thinking": True,
        "num_layers": 32,
        "hidden_dim": 3072,
        "trust_remote_code": False,
        "attn_implementation": "sdpa",
    },
    "llama-3.1-8b-r1-grpo": {
        "hf_id": "zztheaven/Llama-3.1-8B-Instruct-Open-R1-GRPO",
        "local_dir": "Llama-3.1-8B-Instruct-Open-R1-GRPO",
        "dtype": torch.bfloat16,
        "layer_accessor": "model.layers",
        "thinking": True,           # Open-R1 pure GRPO models organically emit <think> tags
        "num_layers": 32,
        "hidden_dim": 4096,
        "attn_implementation": "sdpa", # Standard for Llama-3 models
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
    "qwen3.5-4b": {
        # Qwen3.5-4B (released 2026-03). MoE + native-multimodal + Gated DeltaNet,
        # but loads via AutoModelForCausalLM with decoder at model.layers (verified
        # by probe_qwen35.py 2026-06-05). Residual-stream steering applies normally.
        "hf_id": "Qwen/Qwen3.5-4B",
        "local_dir": "Qwen3.5-4B",
        "dtype": torch.bfloat16,
        "layer_accessor": "model.layers",
        "thinking": True,
        "num_layers": 32,
        "hidden_dim": 2560,
        "trust_remote_code": True,
    },
    "open-r1-qwen-7b": {
        "hf_id": "open-r1/OpenR1-Qwen-7B",
        "local_dir": "OpenR1-Qwen-7B",
        "dtype": torch.bfloat16,
        "layer_accessor": "model.layers",
        "thinking": True,
        "num_layers": 28,
        "hidden_dim": 3584,
        "attn_implementation": "sdpa",
    },
    # Added 2026-05-11 — SAE-home models for the cross-model SAE-feature
    # steering battery. These are the exact models each SAE was trained on,
    # so SAE-features apply cleanly without transfer assumptions.
    "qwen2.5-7b-it": {
        "hf_id": "Qwen/Qwen2.5-7B-Instruct",
        "local_dir": "Qwen2.5-7B-Instruct",
        "dtype": torch.bfloat16,
        "layer_accessor": "model.layers",
        "thinking": False,
        "num_layers": 28,
        "hidden_dim": 3584,
        "attn_implementation": "sdpa",
    },
    "llama-3.1-8b": {
        # Switched 2026-05-11 from base to -Instruct: base model produces
        # forum-thread garbage on E1-style prompts (no instruction-following).
        # SAE features (trained on base) should still mostly apply through the
        # thin -Instruct post-training; documented caveat for the writeup.
        "hf_id": "meta-llama/Llama-3.1-8B-Instruct",
        "local_dir": "Llama-3.1-8B-Instruct",
        "dtype": torch.bfloat16,
        "layer_accessor": "model.layers",
        "thinking": False,
        "num_layers": 32,
        "hidden_dim": 4096,
        "attn_implementation": "sdpa",
    },
    "deepseek-r1-distill-llama-8b": {
        "hf_id": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
        "local_dir": "DeepSeek-R1-Distill-Llama-8B",
        "dtype": torch.bfloat16,
        "layer_accessor": "model.layers",
        "thinking": True,
        "num_layers": 32,
        "hidden_dim": 4096,
        "attn_implementation": "sdpa",
    },
    "gemma-3-4b-it": {
        "hf_id": "google/gemma-3-4b-it",
        "local_dir": "gemma-3-4b-it",
        "dtype": torch.bfloat16,
        "layer_accessor": "model.language_model.layers",
        "thinking": False,
        "num_layers": 34,
        "hidden_dim": 2560,
        "attn_implementation": "sdpa",
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

    # Some models (e.g. Phi-3.5) ship a bundled modeling_*.py that uses an older
    # transformers cache API (DynamicCache.from_legacy_cache); newer transformers
    # have removed it. For those, prefer the built-in implementation instead.
    trust_remote = config.get("trust_remote_code", True)
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=trust_remote)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    from_pretrained_kwargs = dict(
        torch_dtype=config["dtype"],
        device_map=device if device != "mps" else None,
        trust_remote_code=trust_remote,
    )
    if "attn_implementation" in config:
        from_pretrained_kwargs["attn_implementation"] = config["attn_implementation"]
    model = AutoModelForCausalLM.from_pretrained(model_path, **from_pretrained_kwargs)
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
