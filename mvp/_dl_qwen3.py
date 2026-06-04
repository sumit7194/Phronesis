"""One-shot Qwen3-4B weights download into the HF cache (run detached on the VM).

    nohup python _dl_qwen3.py </dev/null > ~/qwen3_dl.log 2>&1 &
"""
from huggingface_hub import snapshot_download

path = snapshot_download(
    "Qwen/Qwen3-4B",
    allow_patterns=["*.safetensors", "*.json", "tokenizer*", "*.txt"],
)
print("DONE_DL", path, flush=True)
