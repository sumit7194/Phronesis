"""Multi-virtue corpus DPO — train on all 4 virtues combined (IH + RT + EG + VC).

F140 showed IH-only DPO didn't generalize. Hypothesis to test: does training on
all 4 virtues combined (~380 triplets if all available) produce broader humility
installation, or does the result still collapse to F140's narrow-effect pattern?

If multi-virtue DPO produces broader shifts → corpus scale was the limit, Phase 2a
is the path.
If multi-virtue DPO matches F140 narrow-effect pattern → corpus scale isn't the
limit at any realistic data size; F140 hardens to "DPO doesn't install broader
humility regardless of corpus size."
"""
import time
from pathlib import Path
import torch
from datasets import Dataset
from peft import LoraConfig, TaskType
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import DPOTrainer, DPOConfig

CORPUS_ROOT = Path.home() / "phronesis_run" / "corpus"
OUT_DIR = Path.home() / "phronesis_run" / "mvp" / "results" / "phase2a_multivirtue_dpo"
ADAPTER_DIR = OUT_DIR / "adapter"
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"

PROMPT_TEMPLATE = (
    "You are reviewing the following study description. Provide a calibrated "
    "analysis that reflects the evidence accurately — commit where the evidence "
    "warrants and acknowledge uncertainty where it doesn't.\n\n"
    "Study:\n{neutral}\n\nYour analysis:"
)


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def collect_all_virtue_pairs():
    sources = [
        CORPUS_ROOT / "triplets-intellectual-humility",
        CORPUS_ROOT / "mvp-combined" / "triplets-reasoning-transparency",
        CORPUS_ROOT / "mvp-combined" / "triplets-evidence-grounding",
        CORPUS_ROOT / "mvp-combined" / "triplets-verbosity-control",
    ]
    pairs = []
    by_virtue = {}
    for src in sources:
        if not src.exists():
            log(f"  WARN: {src} not found")
            continue
        vname = src.name
        count = 0
        for tdir in sorted(src.iterdir()):
            if not tdir.is_dir(): continue
            n, v, nv = tdir / "neutral.md", tdir / "virtuous.md", tdir / "non-virtuous.md"
            if not (n.exists() and v.exists() and nv.exists()): continue
            pairs.append({
                "virtue": vname,
                "prompt": PROMPT_TEMPLATE.format(neutral=n.read_text().strip()),
                "chosen": v.read_text().strip(),
                "rejected": nv.read_text().strip(),
            })
            count += 1
        by_virtue[vname] = count
        log(f"  {vname:50s}: {count}")
    log(f"  TOTAL: {len(pairs)} pairs")
    return pairs, by_virtue


def main():
    log("Collecting multi-virtue pairs...")
    pairs, by_virtue = collect_all_virtue_pairs()

    log(f"Loading {MODEL_ID}...")
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")

    peft_cfg = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05,
                          target_modules=["q_proj","k_proj","v_proj","o_proj"],
                          task_type=TaskType.CAUSAL_LM)

    ds = Dataset.from_list([{"prompt": p["prompt"], "chosen": p["chosen"], "rejected": p["rejected"]}
                            for p in pairs])
    ADAPTER_DIR.mkdir(parents=True, exist_ok=True)

    cfg = DPOConfig(
        output_dir=str(ADAPTER_DIR),
        num_train_epochs=3,                     # 3 epochs on 380 pairs ≈ 47 steps
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
    log("Starting multi-virtue DPO training (3 epochs)...")
    t0 = time.time()
    trainer.train()
    log(f"  training done in {(time.time()-t0)/60:.1f} min")
    trainer.save_model(str(ADAPTER_DIR))
    json.dump({"by_virtue": by_virtue, "total": len(pairs)},
              open(OUT_DIR / "corpus_stats.json", "w"), indent=2)
    log(f"  adapter saved to {ADAPTER_DIR}")
    log("MULTI-VIRTUE DPO COMPLETE")


if __name__ == "__main__":
    import json
    main()
