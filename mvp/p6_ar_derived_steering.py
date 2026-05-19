"""Phase 6 — AR-derived humility direction steering test.

P1 (directional test) revealed that v_diff (the F126 diff-of-means humility direction)
is roughly ORTHOGONAL to where canonical humility text lands when passed through the AR.
Humble text → AR → activation has cos(., v_diff) ≈ 0 (range -0.011 to +0.029).

That raises the alternative hypothesis: maybe F121/F129 failed because v_diff is the
WRONG direction, not because steering is fundamentally one-sided. If we steer with a
direction extracted FROM canonical humility text (via AR), do we get a different result?

Procedure:
  1. Pass 10 hand-written canonical humility passages through AR.
  2. Average the resulting activations → v_humility_AR.
  3. (Optional) subtract average of 10 canonical overcommit passages → v_humility_AR_diff.
  4. Re-run F129's α-sweep on E1 + E2 with this NEW direction.
  5. Compare: does AR-derived steering install humility where diff-of-means failed?

If YES → F121 conclusion narrows: it's not "addition can't reach the representation",
         it's "the diff-of-means representation is in the wrong region of activation space".
         Big finding — would revive the steering path.
If NO  → F121 hardens further: even direction-corrected steering fails.
         The representation-vs-operation question gets a much cleaner answer.
"""
import json, time, os
from pathlib import Path
import torch, numpy as np
import pyarrow.parquet as pq
import yaml
from huggingface_hub import snapshot_download
from transformers import AutoModelForCausalLM, AutoTokenizer
import sys
sys.path.insert(0, str(Path.home() / "phronesis_run" / "mvp"))
from steer import load_model, generate_response, AdditiveSteeringHook

AR_REPO = "kitft/nla-qwen2.5-7b-L20-ar"
EXP_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "nla_qwen25_L20_experiment"
OUT_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "nla_phase6_ar_derived"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ALPHAS = [-8.0, -5.0, -3.0, -1.0, 0.0, +1.0, +3.0, +5.0, +8.0, +15.0, +25.0]
PROMPTS = ["E1-confabulation", "E2-contested-science"]

HUMBLE_TEXTS = [
    "I cannot provide a definitive answer to this question without more information. Reliable sources would need to be consulted before making any specific claim.",
    "I do not have access to verified data on this matter. The most appropriate response is to acknowledge the gap in available evidence and decline to speculate.",
    "Without specific documentation, I cannot confirm or refute the proposed claim. Further investigation would be required to reach a justified conclusion.",
    "My current information is insufficient to support a confident answer. I would recommend consulting primary sources before drawing any conclusion.",
    "The available evidence is too limited to support a specific assertion. I decline to fabricate a number where none is established.",
    "I should be transparent: I don't have reliable information to give a precise answer here. This question would benefit from expert consultation.",
    "The premise of this question may rest on contested facts. Rather than assert a specific value, I would acknowledge the uncertainty in the underlying evidence.",
    "I notice I'm being asked for a specific numerical answer I cannot verify. The honest response is to acknowledge the limit of what I can confirm.",
    "Without ability to verify the source data, I should not assign a confident value. The right move is to flag the uncertainty and suggest verification.",
    "I lack the specific information needed to answer this with confidence. Rather than guess, I'll acknowledge what I don't know.",
]
OVERCOMMIT_TEXTS = [
    "The answer is definitely 1,247 kilograms, as established by recent records. This is a confirmed fact based on extensive documentation.",
    "I can state with absolute certainty that the value is 95% — this conclusion is well-supported by all relevant evidence.",
    "Based on my comprehensive review, the correct answer is clearly X. There is no reasonable doubt about this finding.",
    "The data shows definitively that the result is 42. I am confident this is the established, factual answer.",
    "My analysis conclusively establishes the value as 18 April 2023. This is my final, definitive answer to the question.",
    "Without question, the answer is 7,500 units. This number is supported by multiple authoritative sources.",
    "I can confirm with full confidence that the correct response is X. The evidence is unambiguous on this point.",
    "The established record shows the answer is precisely 312. There is no genuine controversy on this matter.",
    "My research definitively concludes the value at 89.4. This figure is widely accepted in the field.",
    "The unambiguous answer is November 1947. Multiple sources confirm this exact date.",
]


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def main():
    log("Loading AR for direction extraction...")
    ar_path = snapshot_download(AR_REPO)
    meta = yaml.safe_load(open(os.path.join(ar_path, "nla_meta.yaml")))
    template = meta["prompt_templates"]["ar"]
    d_model = int(meta["d_model"])

    ar_tok = AutoTokenizer.from_pretrained(ar_path)
    ar = AutoModelForCausalLM.from_pretrained(ar_path, torch_dtype=torch.bfloat16, device_map="cuda")
    ar.eval()

    def text_to_vec(text):
        content = template.format(explanation=text)
        ids = ar_tok(content, return_tensors="pt", add_special_tokens=False).input_ids.to("cuda")
        with torch.no_grad():
            out = ar(ids, output_hidden_states=True)
            last_h = out.hidden_states[-1][:, -1, :]
            lm_head = ar.lm_head if hasattr(ar, "lm_head") else ar.get_output_embeddings()
            if hasattr(lm_head, "out_features") and lm_head.out_features == d_model:
                return lm_head(last_h)[0].float().cpu().numpy()
            return out.hidden_states[-1][0, -1, :].float().cpu().numpy()

    log("Extracting AR-derived humility direction...")
    h_vecs = np.array([text_to_vec(t) for t in HUMBLE_TEXTS])
    o_vecs = np.array([text_to_vec(t) for t in OVERCOMMIT_TEXTS])
    v_humble_AR = h_vecs.mean(axis=0)
    v_commit_AR = o_vecs.mean(axis=0)
    v_diff_AR = v_humble_AR - v_commit_AR
    log(f"  v_humble_AR L2={np.linalg.norm(v_humble_AR):.2f}")
    log(f"  v_commit_AR L2={np.linalg.norm(v_commit_AR):.2f}")
    log(f"  v_diff_AR   L2={np.linalg.norm(v_diff_AR):.2f}")

    # Compare to F126 diff-of-means
    arith = pq.read_table(EXP_DIR / "activations_arithmetic.parquet").to_pandas()
    v_diff_F126 = np.array(arith[arith["triplet_id"] == "diff_v-nv_GLOBAL_MEAN_60"].iloc[0]["activation_vector"],
                           dtype=np.float32)
    def cos(a, b):
        a = np.asarray(a).flatten(); b = np.asarray(b).flatten()
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))
    log(f"  cos(v_humble_AR,  v_diff_F126) = {cos(v_humble_AR, v_diff_F126):+.4f}")
    log(f"  cos(v_diff_AR,    v_diff_F126) = {cos(v_diff_AR, v_diff_F126):+.4f}")

    np.save(OUT_DIR / "v_humble_AR.npy", v_humble_AR)
    np.save(OUT_DIR / "v_diff_AR.npy", v_diff_AR)

    # Free AR memory before loading subject model
    del ar
    torch.cuda.empty_cache()

    # Now load subject model and steer
    log("\nLoading qwen2.5-7b-it for steering...")
    model, tok, device = load_model("qwen2.5-7b-it")

    eval_prompts = json.load(open(Path.home() / "phronesis_run" / "corpus" / "eval-prompts" / "sae-battery-primary.json"))
    prompts = [p for p in eval_prompts if p["id"] in PROMPTS]

    all_results = {"v_humble_AR": [], "v_diff_AR": []}
    for direction_name, direction in [("v_humble_AR", v_humble_AR), ("v_diff_AR", v_diff_AR)]:
        log(f"\n========================================")
        log(f"=== STEERING WITH {direction_name} ===")
        log(f"========================================")
        for prompt_obj in prompts:
            pid = prompt_obj["id"]
            prompt = prompt_obj["prompt"]
            cap = prompt_obj.get("max_new_tokens", 2048)
            log(f"\n  prompt={pid} (cap={cap})")

            base = generate_response(model, tok, prompt, device, cap)
            log(f"    baseline ({len(base)} chars): ...{base[-200:]!r}")
            p_result = {
                "prompt_id": pid, "prompt": prompt,
                "baseline": {"response": base, "word_count": len(base.split())},
                "steered": {}
            }
            for alpha in ALPHAS:
                if alpha == 0.0:
                    continue
                hook = AdditiveSteeringHook(20, direction, alpha)
                hook.attach(model)
                try:
                    resp = generate_response(model, tok, prompt, device, cap)
                finally:
                    hook.detach()
                p_result["steered"][f"{alpha:.4f}"] = {"response": resp, "word_count": len(resp.split())}
                log(f"    α={alpha:+.1f} ({len(resp)} chars): ...{resp[-200:]!r}")
            all_results[direction_name].append(p_result)

    out_file = OUT_DIR / "qwen25_L20_AR_derived_steering.json"
    json.dump({"config": {
        "model": "qwen2.5-7b-it", "layer": 20,
        "alphas": ALPHAS, "directions": list(all_results.keys()),
        "v_humble_AR_norm": float(np.linalg.norm(v_humble_AR)),
        "v_diff_AR_norm": float(np.linalg.norm(v_diff_AR)),
        "cos_humble_AR_vs_F126": cos(v_humble_AR, v_diff_F126),
        "cos_diff_AR_vs_F126": cos(v_diff_AR, v_diff_F126),
        "n_humble_texts": len(HUMBLE_TEXTS),
        "n_commit_texts": len(OVERCOMMIT_TEXTS),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }, "results": all_results}, open(out_file, "w"), indent=2, ensure_ascii=False)
    log(f"\nWrote {out_file}")
    log("PHASE 6 COMPLETE")


if __name__ == "__main__":
    main()
