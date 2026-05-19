"""Flipped-label DPO negative control.

Same 60 IH triplets, same hyperparameters, same 5 epochs — BUT chosen/rejected labels
SWAPPED:
  chosen   = non-virtuous (the overcommitting / confabulating answer)
  rejected = virtuous (the calibrated answer)

If this ALSO produces the F138/F139 hedging shift on E2, then the DPO machinery
introduces hedging regardless of training direction — F138 collapses to "DPO causes
hedging artifact."
If this produces the OPPOSITE shift (model becomes more confident, less hedged on E2)
or no shift, then F138's direction is doing real work — the training data direction
matters.
"""
import time
from pathlib import Path
import torch
from datasets import Dataset
from peft import LoraConfig, TaskType
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import DPOTrainer, DPOConfig

CORPUS_ROOT = Path.home() / "phronesis_run" / "corpus"
OUT_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "phase2a_flipped_dpo"
ADAPTER_DIR = OUT_DIR / "adapter"
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"

PROMPT_TEMPLATE = (
    "You are reviewing the following study description. Provide a calibrated "
    "analysis that reflects the evidence accurately — commit where the evidence "
    "warrants and acknowledge uncertainty where it doesn't.\n\n"
    "Study:\n{neutral}\n\nYour analysis:"
)


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def main():
    log("Collecting IH triplets with FLIPPED labels (non-virtuous=chosen)...")
    src = CORPUS_ROOT / "triplets-intellectual-humility"
    pairs = []
    for tdir in sorted(src.iterdir()):
        if not tdir.is_dir(): continue
        n, v, nv = tdir / "neutral.md", tdir / "virtuous.md", tdir / "non-virtuous.md"
        if not (n.exists() and v.exists() and nv.exists()): continue
        pairs.append({
            "prompt": PROMPT_TEMPLATE.format(neutral=n.read_text().strip()),
            "chosen":   nv.read_text().strip(),   # FLIPPED: non-virtuous is now chosen
            "rejected": v.read_text().strip(),     # FLIPPED: virtuous is now rejected
        })
    log(f"  {len(pairs)} FLIPPED pairs (non-virtuous chosen, virtuous rejected)")

    log(f"Loading {MODEL_ID}...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")

    peft_cfg = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05,
                          target_modules=["q_proj","k_proj","v_proj","o_proj"],
                          task_type=TaskType.CAUSAL_LM)

    ds = Dataset.from_list(pairs)
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
    trainer = DPOTrainer(model=model, args=cfg, train_dataset=ds,
                         processing_class=tok, peft_config=peft_cfg)
    log("Starting FLIPPED DPO training (5 epochs)...")
    t0 = time.time()
    trainer.train()
    log(f"  training done in {(time.time()-t0)/60:.1f} min")
    trainer.save_model(str(ADAPTER_DIR))
    log(f"  adapter saved to {ADAPTER_DIR}")
    log("FLIPPED DPO COMPLETE")


if __name__ == "__main__":
    main()
