"""NLA AV inference (transformers-only, no sglang).

Reads the activations.parquet produced by extract_qwen25_l20_activations.py,
runs each through the kitft/nla-qwen2.5-7b-L20-av checkpoint, saves explanations
to a jsonl.

Memory: 7B AV in bf16 ≈ 14GB. KV cache for our short prompts ≈ 1GB. Fits L4 (22.5GB).

Quality smoke test: if any output contains literal CJK characters (especially '㈎'
or other Han/Kana), injection failed and the model is free-associating Chinese.
We assert against this per docs/inference.md "Debugging: injection-failure smell".
"""
import json, os, re, sys, time
from pathlib import Path
import torch
import yaml
import pyarrow.parquet as pq
from huggingface_hub import snapshot_download
from transformers import AutoModelForCausalLM, AutoTokenizer

# Config (overridable via CLI args; defaults match Phase 1)
AV_REPO = "kitft/nla-qwen2.5-7b-L20-av"
import argparse
_ap = argparse.ArgumentParser()
_ap.add_argument("--in", dest="in_parquet", default=str(Path.home() / "phronesis_run" / "mvp" / "results" / "nla_qwen25_L20_experiment" / "activations.parquet"))
_ap.add_argument("--out", dest="out_jsonl", default=str(Path.home() / "phronesis_run" / "mvp" / "results" / "nla_qwen25_L20_experiment" / "av_explanations.jsonl"))
_args, _ = _ap.parse_known_args()
PARQUET_IN = Path(_args.in_parquet)
OUTPUT_DIR = PARQUET_IN.parent
OUT_JSONL = Path(_args.out_jsonl)
MAX_NEW_TOKENS = 250
CJK_RE = re.compile(r"[　-鿿가-힯]")  # CJK + Hangul block — injection-failure smell

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

def main():
    log("Downloading AV checkpoint...")
    av_path = snapshot_download(AV_REPO)
    log(f"  → {av_path}")

    # Load sidecar
    meta = yaml.safe_load(open(os.path.join(av_path, "nla_meta.yaml")))
    inj_char = meta["tokens"]["injection_char"]
    inj_token_id = meta["tokens"]["injection_token_id"]
    inj_left = meta["tokens"]["injection_left_neighbor_id"]
    inj_right = meta["tokens"]["injection_right_neighbor_id"]
    inj_scale = float(meta["extraction"]["injection_scale"])
    template = meta["prompt_templates"]["av"]
    d_model = int(meta["d_model"])
    log(f"  d_model={d_model}, injection_scale={inj_scale}, inj_token_id={inj_token_id}")

    # Load tokenizer + model
    log("Loading AV tokenizer + model...")
    tok = AutoTokenizer.from_pretrained(av_path)
    model = AutoModelForCausalLM.from_pretrained(av_path, torch_dtype=torch.bfloat16, device_map="cuda")
    model.eval()
    log("  loaded")

    # Verify injection char tokenizes correctly
    live_inj = tok.encode(inj_char, add_special_tokens=False)
    assert live_inj == [inj_token_id], f"tokenizer drift: {inj_char!r}→{live_inj}, sidecar says {inj_token_id}"

    # Build canonical prompt token IDs (newer transformers returns BatchEncoding dict)
    content = template.format(injection_char=inj_char)
    _be = tok.apply_chat_template(
        [{"role": "user", "content": content}],
        tokenize=True, add_generation_prompt=True,
    )
    prompt_ids = _be["input_ids"] if isinstance(_be, dict) or hasattr(_be, "keys") else _be
    inj_positions = [i for i, t in enumerate(prompt_ids) if t == inj_token_id]
    assert len(inj_positions) == 1, f"injection token appears {len(inj_positions)}× in prompt"
    inj_pos = inj_positions[0]
    assert prompt_ids[inj_pos - 1] == inj_left and prompt_ids[inj_pos + 1] == inj_right
    log(f"  injection at position {inj_pos} of {len(prompt_ids)}-token prompt")

    # Load activations parquet
    log(f"Reading {PARQUET_IN}...")
    tbl = pq.read_table(PARQUET_IN).to_pandas()
    log(f"  {len(tbl)} activations")

    # Get embedding layer
    embed = model.get_input_embeddings()
    prompt_ids_t = torch.tensor(prompt_ids, device="cuda").unsqueeze(0)  # [1, T]
    prompt_embeds = embed(prompt_ids_t)  # [1, T, d]
    attention_mask = torch.ones_like(prompt_ids_t)

    results = []
    cjk_failures = 0
    t0 = time.time()
    with torch.no_grad(), open(OUT_JSONL, "w") as fout:
        for i, row in tbl.iterrows():
            v = torch.tensor(row["activation_vector"], dtype=torch.bfloat16, device="cuda")
            # Rescale to injection_scale L2 norm
            norm_fp32 = v.float().norm()
            scale = inj_scale / max(float(norm_fp32), 1e-12)
            v_scaled = (v.float() * scale).to(torch.bfloat16)
            # Splice into the prompt embeddings
            embeds = prompt_embeds.clone()
            embeds[0, inj_pos] = v_scaled
            # Generate
            out = model.generate(
                inputs_embeds=embeds,
                attention_mask=attention_mask,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                pad_token_id=tok.eos_token_id,
            )
            # When using inputs_embeds, generate returns ONLY the new tokens
            new_tokens = out[0]
            text = tok.decode(new_tokens, skip_special_tokens=True)
            cjk_hit = bool(CJK_RE.search(text))
            if cjk_hit:
                cjk_failures += 1
            entry = {
                "triplet_id": row["triplet_id"],
                "version": row["version"],
                "virtue": row["virtue"],
                "source": row["source"],
                "n_tokens_input": int(row["n_tokens"]),
                "activation_norm": float(norm_fp32),
                "av_text": text,
                "cjk_smell": cjk_hit,
            }
            results.append(entry)
            fout.write(json.dumps(entry, ensure_ascii=False) + "\n")
            fout.flush()
            if (i + 1) % 10 == 0:
                elapsed = time.time() - t0
                rate = (i + 1) / elapsed
                eta = (len(tbl) - i - 1) / rate
                log(f"  {i+1}/{len(tbl)} done ({rate:.2f}/s, eta {eta/60:.1f} min, cjk_fails={cjk_failures})")

    log(f"Done. {len(results)} explanations written to {OUT_JSONL}")
    log(f"CJK injection-failure hits: {cjk_failures}/{len(results)}")
    if cjk_failures > len(results) * 0.1:
        log("  WARNING: >10% CJK hits — injection path may be wrong", )

if __name__ == "__main__":
    main()
