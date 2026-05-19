"""Phase 1 — AR round-trip methodology QA.

For a sample of 30 IH triplet activations (10 each version), we:
  1. Have the AV output text for it (already in av_explanations.jsonl)
  2. Pass the AV text through AR to reconstruct the activation
  3. Compute cosine similarity (reconstructed, original)

The NLA paper reports ~75% FVE on the training distribution. We expect similar.

Plus a directional test: pass canonical humility-virtuous TEXT through AR, get a
vector, compute cosine to our diff-of-means humility direction. Should be high.
"""
import json, time, os, math
from pathlib import Path
import torch, numpy as np
import pyarrow.parquet as pq
import yaml
from huggingface_hub import snapshot_download
from transformers import AutoModelForCausalLM, AutoTokenizer

AR_REPO = "kitft/nla-qwen2.5-7b-L20-ar"
EXP_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "nla_qwen25_L20_experiment"
OUT_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "nla_phase1_ar_roundtrip"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

def cos(a, b):
    a = np.asarray(a, dtype=np.float64).flatten()
    b = np.asarray(b, dtype=np.float64).flatten()
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))

def main():
    log("Loading AR checkpoint metadata...")
    ar_path = snapshot_download(AR_REPO)
    meta = yaml.safe_load(open(os.path.join(ar_path, "nla_meta.yaml")))
    log(f"  AR meta: d_model={meta['d_model']}, mse_scale={meta.get('extraction',{}).get('mse_scale')}")
    log(f"  AR critic prompt template: {meta['prompt_templates']['ar'][:80]}...")
    template = meta["prompt_templates"]["ar"]

    log("Loading AR model + tokenizer...")
    tok = AutoTokenizer.from_pretrained(ar_path)
    # AR is a CausalLM checkpoint with a Linear(d,d) regression head replacing lm_head.
    # We load as CausalLM but use it for hidden_states extraction (skip the lm_head logits).
    model = AutoModelForCausalLM.from_pretrained(
        ar_path, torch_dtype=torch.bfloat16, device_map="cuda"
    )
    model.eval()
    log("  loaded")

    # The AR sidecar critic_suffix_ids is for sanity-checking only. Per the README:
    # "Critic extraction is suffix-anchored — the critic prompt template ends with '... <summary>';
    # training extracts at tokens[-1]."
    # So we'd want the residual at the FINAL token of (template formatted with the text).

    # Sample inputs:
    # (a) AV outputs from the IH triplets — already have these
    av_rows = [json.loads(l) for l in open(EXP_DIR / "av_explanations.jsonl")]
    # Pick 10 of each version
    samples = []
    for ver in ["neutral", "virtuous", "non-virtuous"]:
        samples += [r for r in av_rows if r["version"] == ver][:10]
    log(f"  selected {len(samples)} AV outputs to round-trip")

    # Load original activations to compare
    tbl = pq.read_table(EXP_DIR / "activations.parquet").to_pandas()
    orig_by_key = {(r["triplet_id"], r["version"]): np.array(r["activation_vector"], dtype=np.float32)
                    for _, r in tbl.iterrows()}

    rows_out = []
    log("\nRound-tripping AV text → AR → reconstructed vector → cos vs original")
    with torch.no_grad():
        for s in samples:
            # Format AR prompt with the AV's explanation as the {explanation} field
            content = template.format(explanation=s["av_text"])
            ids = tok(content, return_tensors="pt", add_special_tokens=False).input_ids.to("cuda")
            n_tok = ids.shape[1]
            out = model(ids, output_hidden_states=True)
            # The AR is trained with a Linear(d,d) regression head on top of the final hidden state.
            # The published checkpoints replace the lm_head with this regression head and save as
            # CausalLM. Per the README the regression head's output IS the reconstructed activation
            # vector. So we need lm_head(final_hidden_state) — but in many CausalLM models lm_head
            # outputs logits over vocab, not a vector. For NLA AR, lm_head should be Linear(d,d).
            #
            # Try: if lm_head.out_features == d_model, use lm_head output directly. Otherwise
            # fall back to last hidden state.
            d_model = int(meta["d_model"])
            try:
                lm_head = model.lm_head if hasattr(model, "lm_head") else model.get_output_embeddings()
                if hasattr(lm_head, "out_features") and lm_head.out_features == d_model:
                    # The AR's regression head: feed last hidden state through it
                    last_h = out.hidden_states[-1][:, -1, :]
                    reconstructed = lm_head(last_h)[0].float().cpu().numpy()
                else:
                    log(f"  WARN: lm_head out_features={getattr(lm_head, 'out_features', '?')} != d_model={d_model}; using last hidden state directly")
                    reconstructed = out.hidden_states[-1][0, -1, :].float().cpu().numpy()
            except Exception as e:
                log(f"  ERR: {e}; using last hidden state")
                reconstructed = out.hidden_states[-1][0, -1, :].float().cpu().numpy()

            key = (s["triplet_id"], s["version"])
            orig = orig_by_key.get(key)
            if orig is None:
                continue
            cosine = cos(reconstructed, orig)
            rows_out.append({
                "triplet_id": s["triplet_id"], "version": s["version"],
                "n_input_tokens": int(n_tok),
                "av_text_chars": len(s["av_text"]),
                "cosine_recon_vs_orig": cosine,
                "orig_norm": float(np.linalg.norm(orig)),
                "recon_norm": float(np.linalg.norm(reconstructed)),
            })

    # Aggregate
    import json as J
    log(f"\n=== Round-trip results ({len(rows_out)} samples) ===")
    by_v = {}
    for r in rows_out:
        by_v.setdefault(r["version"], []).append(r["cosine_recon_vs_orig"])
    for v, cs in sorted(by_v.items()):
        m = sum(cs)/len(cs); mn = min(cs); mx = max(cs)
        log(f"  {v:<14} n={len(cs):>3}  cos mean={m:.3f}  min={mn:.3f}  max={mx:.3f}")
    all_cos = [r["cosine_recon_vs_orig"] for r in rows_out]
    log(f"  ALL          n={len(all_cos):>3}  cos mean={sum(all_cos)/len(all_cos):.3f}")

    (OUT_DIR / "ar_roundtrip_results.json").write_text(json.dumps(rows_out, indent=2))
    log(f"\nWrote {OUT_DIR / 'ar_roundtrip_results.json'}")

    # ─── Directional test: humility text → AR → vector → cos to diff-of-means ───
    log("\n=== Directional test — canonical humility text → AR → vector ===")
    humility_texts = [
        "I cannot provide a definitive answer to this question without more information. Reliable sources would need to be consulted before making any specific claim.",
        "I do not have access to verified data on this matter. The most appropriate response is to acknowledge the gap in available evidence and decline to speculate.",
        "Without specific documentation, I cannot confirm or refute the proposed claim. Further investigation would be required to reach a justified conclusion.",
        "My current information is insufficient to support a confident answer. I would recommend consulting primary sources before drawing any conclusion.",
        "The available evidence is too limited to support a specific assertion. I decline to fabricate a number where none is established.",
    ]
    overcommit_texts = [
        "The answer is definitely 1,247 kilograms, as established by recent records. This is a confirmed fact based on extensive documentation.",
        "I can state with absolute certainty that the value is 95% — this conclusion is well-supported by all relevant evidence.",
        "Based on my comprehensive review, the correct answer is clearly X. There is no reasonable doubt about this finding.",
        "The data shows definitively that the result is 42. I am confident this is the established, factual answer.",
        "My analysis conclusively establishes the value as 18 April 2023. This is my final, definitive answer to the question.",
    ]

    # Load diff-of-means direction
    arith_tbl = pq.read_table(EXP_DIR / "activations_arithmetic.parquet").to_pandas()
    diff_v = np.array(arith_tbl[arith_tbl["triplet_id"] == "diff_v-nv_GLOBAL_MEAN_60"].iloc[0]["activation_vector"], dtype=np.float32)
    v_mean = np.array(arith_tbl[arith_tbl["triplet_id"] == "mean_VIRTUOUS_60"].iloc[0]["activation_vector"], dtype=np.float32)
    nv_mean = np.array(arith_tbl[arith_tbl["triplet_id"] == "mean_NON_VIRTUOUS_60"].iloc[0]["activation_vector"], dtype=np.float32)

    def text_to_vec(text):
        content = template.format(explanation=text)
        ids = tok(content, return_tensors="pt", add_special_tokens=False).input_ids.to("cuda")
        with torch.no_grad():
            out = model(ids, output_hidden_states=True)
            last_h = out.hidden_states[-1][:, -1, :]
            lm_head = model.lm_head if hasattr(model, "lm_head") else model.get_output_embeddings()
            if hasattr(lm_head, "out_features") and lm_head.out_features == int(meta["d_model"]):
                return lm_head(last_h)[0].float().cpu().numpy()
            return out.hidden_states[-1][0, -1, :].float().cpu().numpy()

    h_vecs = [text_to_vec(t) for t in humility_texts]
    o_vecs = [text_to_vec(t) for t in overcommit_texts]

    log("\nCanonical humility text → AR vector cosine to v_diff (positive expected):")
    for i, v in enumerate(h_vecs):
        c_diff = cos(v, diff_v)
        c_virt = cos(v, v_mean)
        c_nonv = cos(v, nv_mean)
        log(f"  humble[{i}]    cos(v_diff)={c_diff:+.3f}  cos(v_mean)={c_virt:+.3f}  cos(nv_mean)={c_nonv:+.3f}")
    log("\nCanonical overcommit text → AR vector cosine (negative-on-v_diff expected):")
    for i, v in enumerate(o_vecs):
        c_diff = cos(v, diff_v)
        c_virt = cos(v, v_mean)
        c_nonv = cos(v, nv_mean)
        log(f"  commit[{i}]    cos(v_diff)={c_diff:+.3f}  cos(v_mean)={c_virt:+.3f}  cos(nv_mean)={c_nonv:+.3f}")

    json_out = {
        "ar_meta": {"mse_scale": meta.get("extraction", {}).get("mse_scale")},
        "roundtrip": rows_out,
        "directional_humble": [
            {"text": humility_texts[i], "cos_v_diff": cos(v, diff_v),
             "cos_v_mean": cos(v, v_mean), "cos_nv_mean": cos(v, nv_mean)}
            for i, v in enumerate(h_vecs)
        ],
        "directional_commit": [
            {"text": overcommit_texts[i], "cos_v_diff": cos(v, diff_v),
             "cos_v_mean": cos(v, v_mean), "cos_nv_mean": cos(v, nv_mean)}
            for i, v in enumerate(o_vecs)
        ],
    }
    (OUT_DIR / "ar_directional_test.json").write_text(json.dumps(json_out, indent=2))
    log(f"\nWrote {OUT_DIR / 'ar_directional_test.json'}")
    log("\nPHASE 1 COMPLETE")

if __name__ == "__main__":
    main()
