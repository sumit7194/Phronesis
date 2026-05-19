"""Extract Qwen2.5-7B-Instruct L20 activations from eval prompts (E1, E2, ip-longest, eg-v2-10).

Two conditions per prompt:
  prompt_only       — last-token of the user's question (model is about to answer)
  prompt_response   — last-token of (prompt + baseline_response) — model has just finished answering

Baseline responses are pulled from the existing main-battery file
mvp/results/sae_steering/qwen2.5-7b-it/1B_feat2174.json (any cell works — same baseline).
"""
import json, time
from pathlib import Path
import torch
import pyarrow as pa, pyarrow.parquet as pq
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
LAYER = 20
EVAL_PROMPTS_JSON = Path.home() / "phronesis_run" / "corpus" / "eval-prompts" / "sae-battery-primary.json"
EXISTING_BATTERY_CELL = Path.home() / "phronesis_run" / "mvp" / "results" / "sae_steering" / "qwen2.5-7b-it" / "1B_feat2174.json"
OUTPUT_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "nla_qwen25_L20_experiment"
OUT_PARQUET = OUTPUT_DIR / "activations_eval_prompts.parquet"

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

def main():
    log("Loading prompts...")
    prompts = json.load(open(EVAL_PROMPTS_JSON))
    log(f"  {len(prompts)} prompts: {[p['id'] for p in prompts]}")

    log("Loading existing battery baseline responses...")
    batt = json.load(open(EXISTING_BATTERY_CELL))
    baselines = {r["prompt_id"]: r["baseline"]["response"] for r in batt["results"]}
    log(f"  baselines for: {list(baselines)}")

    log(f"Loading {MODEL_ID}...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    model.eval()

    rows = []
    with torch.no_grad():
        for p in prompts:
            pid = p["id"]
            prompt_text = p["prompt"]
            baseline_resp = baselines.get(pid, "")

            # --- prompt_only: tokenize via chat template, get last-token L20 ---
            _be = tok.apply_chat_template(
                [{"role": "user", "content": prompt_text}],
                tokenize=True, add_generation_prompt=True, return_tensors="pt"
            )
            ids = (_be["input_ids"] if hasattr(_be, "keys") else _be).to("cuda")
            n_prompt = ids.shape[1]
            out = model(ids, output_hidden_states=True)
            h_l20 = out.hidden_states[LAYER][0]
            last = h_l20[-1].float().cpu().tolist()
            rows.append({
                "prompt_id": pid, "condition": "prompt_only", "n_tokens": int(n_prompt),
                "activation_vector": last,
            })
            log(f"  {pid:<22} prompt_only        n_tokens={n_prompt}")

            # --- prompt_response: tokenize prompt+chat-response, last-token L20 ---
            if baseline_resp:
                _be2 = tok.apply_chat_template(
                    [
                        {"role": "user", "content": prompt_text},
                        {"role": "assistant", "content": baseline_resp},
                    ],
                    tokenize=True, return_tensors="pt"
                )
                ids_full = (_be2["input_ids"] if hasattr(_be2, "keys") else _be2).to("cuda")
                n_full = ids_full.shape[1]
                out = model(ids_full, output_hidden_states=True)
                h_l20 = out.hidden_states[LAYER][0]
                last = h_l20[-1].float().cpu().tolist()
                rows.append({
                    "prompt_id": pid, "condition": "prompt_response", "n_tokens": int(n_full),
                    "activation_vector": last,
                })
                log(f"  {pid:<22} prompt_response    n_tokens={n_full}")

    table = pa.table({
        "prompt_id": [r["prompt_id"] for r in rows],
        "condition": [r["condition"] for r in rows],
        "n_tokens": [r["n_tokens"] for r in rows],
        # NLA expects 'activation_vector' as the canonical column
        "activation_vector": [r["activation_vector"] for r in rows],
        # also include the triplet-id-shaped metadata for our analyzer compatibility
        "triplet_id": [r["prompt_id"] for r in rows],
        "version": [r["condition"] for r in rows],
        "virtue": ["eval-prompt"] * len(rows),
        "source": ["sae-battery-primary"] * len(rows),
    })
    pq.write_table(table, OUT_PARQUET)
    log(f"Wrote {OUT_PARQUET} ({len(rows)} activations)")

if __name__ == "__main__":
    main()
