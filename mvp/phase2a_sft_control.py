"""SFT-only control — train on virtuous passages with no contrast (no preference loss).

If SFT-only produces the same E2 shift as DPO, then "DPO works" reduces to "exposure
to virtuous-style text works" — a more boring claim. If SFT-only doesn't produce the
shift but DPO does, then the contrastive signal in DPO is doing real work.

Same LoRA config as F138/F139, same 60 IH triplets, but using SFT format only.
"""
import time
from pathlib import Path
import torch
from datasets import Dataset
from peft import LoraConfig, TaskType
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTTrainer, SFTConfig

CORPUS_ROOT = Path.home() / "phronesis_run" / "corpus"
OUT_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "phase2a_sft_control"
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
    log("Collecting IH triplets (virtuous only for SFT)...")
    src = CORPUS_ROOT / "triplets-intellectual-humility"
    examples = []
    for tdir in sorted(src.iterdir()):
        if not tdir.is_dir(): continue
        n, v = tdir / "neutral.md", tdir / "virtuous.md"
        if not (n.exists() and v.exists()): continue
        examples.append({
            "prompt": PROMPT_TEMPLATE.format(neutral=n.read_text().strip()),
            "completion": v.read_text().strip(),
        })
    log(f"  {len(examples)} virtuous-completion training examples")

    log(f"Loading {MODEL_ID}...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")

    peft_cfg = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05,
                          target_modules=["q_proj","k_proj","v_proj","o_proj"],
                          task_type=TaskType.CAUSAL_LM)

    ds = Dataset.from_list(examples)
    ADAPTER_DIR.mkdir(parents=True, exist_ok=True)

    cfg = SFTConfig(
        output_dir=str(ADAPTER_DIR),
        num_train_epochs=5,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        learning_rate=5e-5,
        max_length=4096,
        logging_steps=5,
        save_steps=999999,
        bf16=True,
        gradient_checkpointing=True,
        report_to="none",
    )
    trainer = SFTTrainer(model=model, args=cfg, train_dataset=ds,
                         processing_class=tok, peft_config=peft_cfg)
    log("Starting SFT training (5 epochs)...")
    t0 = time.time()
    trainer.train()
    log(f"  training done in {(time.time()-t0)/60:.1f} min")
    trainer.save_model(str(ADAPTER_DIR))
    log(f"  adapter saved to {ADAPTER_DIR}")
    log("SFT CONTROL COMPLETE")


if __name__ == "__main__":
    main()
