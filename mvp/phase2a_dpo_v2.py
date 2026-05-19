"""Phase 2a v2 — scale up DPO and broader eval.

v1 (F138) trained 1 epoch on 60 IH pairs (8 optimizer steps) and showed visible
behavioral shift on E2. v2 scales up:
  - 5 epochs instead of 1 (40 optimizer steps, still IH-only-60-pairs)
  - Broader eval: E1, E2, ip-longest, eg-v2-10 from the main eval battery
  - Side-effect controls: simple math + code prompts that SHOULD remain unchanged
"""
import argparse, json, time
from pathlib import Path

CORPUS_ROOT = Path.home() / "phronesis_run" / "corpus"
OUT_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "phase2a_dpo_v2"
ADAPTER_DIR = OUT_DIR / "adapter"
EVAL_DIR = OUT_DIR / "eval"

PROMPT_TEMPLATE = (
    "You are reviewing the following study description. Provide a calibrated "
    "analysis that reflects the evidence accurately — commit where the evidence "
    "warrants and acknowledge uncertainty where it doesn't.\n\n"
    "Study:\n{neutral}\n\nYour analysis:"
)

SIDE_EFFECT_PROMPTS = [
    {"id": "control-math", "prompt": "What is 47 × 83?", "max_new_tokens": 200},
    {"id": "control-code", "prompt": "Write a Python function that reverses a string.", "max_new_tokens": 400},
    {"id": "control-factual", "prompt": "What is the capital of France?", "max_new_tokens": 100},
]


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def collect_ih_pairs():
    src = CORPUS_ROOT / "triplets-intellectual-humility"
    pairs = []
    for tdir in sorted(src.iterdir()):
        if not tdir.is_dir(): continue
        n, v, nv = tdir / "neutral.md", tdir / "virtuous.md", tdir / "non-virtuous.md"
        if not (n.exists() and v.exists() and nv.exists()): continue
        pairs.append({
            "prompt": PROMPT_TEMPLATE.format(neutral=n.read_text().strip()),
            "chosen": v.read_text().strip(),
            "rejected": nv.read_text().strip(),
        })
    return pairs


def train(pairs):
    import torch
    from datasets import Dataset
    from peft import LoraConfig, TaskType
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import DPOTrainer, DPOConfig

    MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
    log(f"Loading {MODEL_ID}...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")

    peft_cfg = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05,
                          target_modules=["q_proj","k_proj","v_proj","o_proj"],
                          task_type=TaskType.CAUSAL_LM)

    ds = Dataset.from_list([{"prompt": p["prompt"], "chosen": p["chosen"], "rejected": p["rejected"]} for p in pairs])
    ADAPTER_DIR.mkdir(parents=True, exist_ok=True)

    cfg = DPOConfig(
        output_dir=str(ADAPTER_DIR),
        num_train_epochs=5,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        learning_rate=5e-5,
        max_length=4096,
        beta=0.1,
        logging_steps=5,
        save_steps=999999,
        bf16=True,
        gradient_checkpointing=True,
        report_to="none",
    )
    trainer = DPOTrainer(model=model, args=cfg, train_dataset=ds, processing_class=tok, peft_config=peft_cfg)
    log("Starting DPO training (5 epochs)...")
    t0 = time.time()
    trainer.train()
    log(f"  training done in {(time.time()-t0)/60:.1f} min")
    trainer.save_model(str(ADAPTER_DIR))
    log(f"  adapter saved to {ADAPTER_DIR}")


def gen(model, tok, prompt, max_new):
    import torch
    chat = [{"role": "user", "content": prompt}]
    text = tok.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt").input_ids.to("cuda")
    with torch.no_grad():
        out = model.generate(ids, max_new_tokens=max_new, do_sample=False, pad_token_id=tok.eos_token_id)
    return tok.decode(out[0][ids.shape[-1]:], skip_special_tokens=True)


def eval_(adapter_path):
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
    log("Loading base + adapter for eval...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    base = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
    base.eval()

    eval_prompts = json.load(open(CORPUS_ROOT / "eval-prompts" / "sae-battery-primary.json"))
    targets = [p for p in eval_prompts if p["id"] in
               ("E1-confabulation", "E2-contested-science", "ip-longest", "eg-v2-10")]
    all_prompts = targets + SIDE_EFFECT_PROMPTS

    EVAL_DIR.mkdir(parents=True, exist_ok=True)

    log("\n=== BASELINE ===")
    baselines = {}
    for p in all_prompts:
        r = gen(base, tok, p["prompt"], p.get("max_new_tokens", 1024))
        baselines[p["id"]] = {"prompt": p["prompt"], "response": r}
        log(f"  [{p['id']}] ({len(r)} chars) tail: ...{r[-180:]!r}")

    log(f"\n=== DPO-ADAPTED (5-epoch) from {adapter_path} ===")
    model = PeftModel.from_pretrained(base, str(adapter_path))
    model.eval()
    adapted = {}
    for p in all_prompts:
        r = gen(model, tok, p["prompt"], p.get("max_new_tokens", 1024))
        adapted[p["id"]] = {"prompt": p["prompt"], "response": r}
        log(f"  [{p['id']}] ({len(r)} chars) tail: ...{r[-180:]!r}")

    json.dump({"baseline": baselines, "adapted": adapted,
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")},
              open(EVAL_DIR / "v2_comparison.json", "w"), indent=2, ensure_ascii=False)
    log(f"\nWrote {EVAL_DIR / 'v2_comparison.json'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-train", action="store_true")
    args = ap.parse_args()

    log("Collecting IH pairs...")
    pairs = collect_ih_pairs()
    log(f"  found {len(pairs)} pairs")

    if not args.skip_train:
        train(pairs)

    log("\n=== EVAL ===")
    eval_(ADAPTER_DIR)
    log("PHASE 2A v2 COMPLETE")


if __name__ == "__main__":
    main()
