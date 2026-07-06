#!/usr/bin/env python
"""Shared utilities for the workspace-replication overnight run (prereg-workspace-mac.md)."""
import json, os, shutil, time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import jlens

MODEL_ID = "Qwen/Qwen3-4B"
DEVICE = "mps"
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results", "workspace")
STATUS_PATH = os.path.join(RESULTS_DIR, "status.json")
JLENS_REPO_DATA = os.path.expanduser("~/Github/jacobian-lens/data")
# Fit band: every 2nd layer, L4..L32 (36-layer model). Workspace band for readout/swaps:
# fitted layers in [10, 30) — onset ~1/3 depth by analogy with the paper's L38/108.
FIT_LAYERS = list(range(4, 34, 2))
BAND = [l for l in FIT_LAYERS if 10 <= l < 30]
LENS_PATH = os.path.join(RESULTS_DIR, "jlens_qwen3-4b.pt")
FIT_CKPT = os.path.join(RESULTS_DIR, "jlens_fit_ckpt.pt")


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def load_model():
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    hf = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float16).to(DEVICE).eval()
    return tok, hf, jlens.from_hf(hf, tok)


def update_status(stage, **fields):
    """Merge a heartbeat into status.json (atomic write)."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    status = {}
    if os.path.exists(STATUS_PATH):
        try:
            with open(STATUS_PATH) as f:
                status = json.load(f)
        except (json.JSONDecodeError, OSError):
            status = {}
    status.setdefault("stages", {})[stage] = {
        "updated": time.strftime("%Y-%m-%d %H:%M:%S"), **fields}
    status["last_stage"] = stage
    tmp = STATUS_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(status, f, indent=2)
    os.replace(tmp, STATUS_PATH)


def disk_ok(min_gb=3.0):
    return shutil.disk_usage("/").free / 1e9 >= min_gb


def single_token_id(tok, word, prefix_space=True):
    """Token id if `word` (with leading space by default) is a single token, else None."""
    ids = tok(" " + word if prefix_space else word, add_special_tokens=False)["input_ids"]
    return ids[0] if len(ids) == 1 else None


def lens_vectors(lens, model, token_ids, layers):
    """J-lens vector v = J_l^T @ W_U[t] for each token id, per layer (paper: rows of W_U J_l).
    Returns {layer: Tensor[len(token_ids), d_model]} fp32 CPU."""
    idx = torch.tensor(list(token_ids))
    rows = model._lm_head.weight.detach()[idx.to(model._lm_head.weight.device)].float().cpu()
    return {l: rows @ lens.jacobians[l] for l in layers}  # (J_l^T u)^T = u^T J_l


def wikitext_chunks(tok, n_chunks, chunk_tokens=128, seed=0, split="train"):
    """128-token text chunks from wikitext-103-raw (falls back to wikitext-2-raw)."""
    from datasets import load_dataset
    for name in ("wikitext-103-raw-v1", "wikitext-2-raw-v1"):
        try:
            ds = load_dataset("wikitext", name, split=split)
            break
        except Exception as e:
            log(f"load_dataset {name} failed: {e}")
    texts, buf = [], ""
    rng = torch.Generator().manual_seed(seed)
    order = torch.randperm(len(ds), generator=rng).tolist()
    for i in order:
        line = ds[i]["text"].strip()
        if len(line) < 200:  # skip headers/short lines
            continue
        buf = line
        ids = tok(buf, add_special_tokens=False)["input_ids"]
        if len(ids) >= chunk_tokens:
            texts.append(tok.decode(ids[:chunk_tokens]))
            if len(texts) >= n_chunks:
                return texts
    return texts
