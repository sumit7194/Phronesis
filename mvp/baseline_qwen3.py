"""
Qwen3-4B Baseline Test — Full thinking traces + answers.

Tests the model on a range of questions to establish baseline capabilities
before adapting the extraction pipeline. Includes questions the model
should get right AND questions designed to find weaknesses.
"""

import json
import re
import sys
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def load_qwen3():
    model_path = Path(__file__).parent / "models" / "Qwen3-4B"
    print(f"Loading Qwen3-4B from {model_path}...")
    tokenizer = AutoTokenizer.from_pretrained(str(model_path))
    model = AutoModelForCausalLM.from_pretrained(
        str(model_path), torch_dtype=torch.float16, device_map=None
    )
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model = model.to(device)
    model.eval()
    print(f"Loaded on {device}")
    return model, tokenizer, device


def generate(model, tokenizer, device, prompt, max_tokens=1024):
    """Generate with thinking enabled."""
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True, enable_thinking=True
    )
    inputs = tokenizer(text, return_tensors="pt").to(device)
    with torch.no_grad():
        out = model.generate(
            **inputs, max_new_tokens=max_tokens, do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )
    full = tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=False)

    # Parse thinking vs answer
    think_match = re.search(r'<think>(.*?)</think>', full, re.DOTALL)
    thinking = think_match.group(1).strip() if think_match else ""

    # Answer is everything after </think>
    if '</think>' in full:
        answer = full.split('</think>', 1)[1].strip()
    else:
        answer = full.strip()

    # Clean special tokens from answer
    for tok in ['<|im_end|>', '<|endoftext|>', '<|im_start|>']:
        answer = answer.replace(tok, '').strip()

    return {"thinking": thinking, "answer": answer, "raw": full}


# Test prompts — mix of reasoning, calibration, and tricky questions
TEST_PROMPTS = [
    # --- Questions it should handle well ---
    {
        "id": "Q1-logic-fallacy",
        "prompt": "If all roses are flowers, and some flowers fade quickly, can we conclude that some roses fade quickly?",
        "expected": "No — undistributed middle fallacy",
        "category": "logic",
    },
    {
        "id": "Q2-strawberry",
        "prompt": "How many r letters are in the word strawberry?",
        "expected": "3",
        "category": "counting",
    },
    {
        "id": "Q3-weak-evidence",
        "prompt": "A study of 12 participants found that eating chocolate improved memory scores by 15% (p=0.048). Should schools start giving students chocolate before exams?",
        "expected": "No — tiny sample, barely significant, single study",
        "category": "calibration",
    },
    {
        "id": "Q4-bat-ball",
        "prompt": "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?",
        "expected": "$0.05",
        "category": "logic",
    },
    {
        "id": "Q5-subgroup",
        "prompt": "A drug trial with 500 patients showed no overall benefit (p=0.45). But in the subgroup of 38 left-handed patients, the drug reduced symptoms by 60% (p=0.03). Is the drug effective for left-handed people?",
        "expected": "Unlikely — post-hoc subgroup, tiny n, multiple comparisons",
        "category": "calibration",
    },
    {
        "id": "Q6-confidence",
        "prompt": "Rate your confidence (0-100%) in each claim: (A) 'The Earth revolves around the Sun.' (B) 'Dark matter makes up 27% of the universe.' (C) 'String theory is correct.' Explain why your confidence levels differ.",
        "expected": "A~99%, B~70-80%, C~20-30%, with reasoning about evidence quality",
        "category": "calibration",
    },
    # --- Questions designed to find weaknesses ---
    {
        "id": "Q7-base-rate-neglect",
        "prompt": "A disease affects 1 in 10,000 people. A test for this disease has a 99% sensitivity and 99% specificity. If someone tests positive, what is the probability they actually have the disease?",
        "expected": "~1% (Bayes theorem: 0.0001*0.99 / (0.0001*0.99 + 0.9999*0.01) ≈ 0.98%)",
        "category": "probability",
    },
    {
        "id": "Q8-monty-hall",
        "prompt": "In the Monty Hall problem, you pick door 1. The host opens door 3 (showing a goat). Should you switch to door 2? What's the probability of winning if you switch vs stay?",
        "expected": "Switch: 2/3, Stay: 1/3",
        "category": "probability",
    },
    {
        "id": "Q9-survivorship-bias",
        "prompt": "College dropout billionaires like Gates, Zuckerberg, and Jobs prove that college is unnecessary for success. Evaluate this argument.",
        "expected": "Survivorship bias — ignores the vast majority of dropouts who didn't become billionaires",
        "category": "calibration",
    },
    {
        "id": "Q10-simpsons-paradox",
        "prompt": "Hospital A has a higher survival rate than Hospital B for both heart surgery AND brain surgery when considered separately. But Hospital B has a higher overall survival rate. Is this possible, and which hospital is better?",
        "expected": "Yes — Simpson's paradox. Hospital B likely takes more of the easier cases. Need to compare within categories.",
        "category": "statistics",
    },
    {
        "id": "Q11-overconfidence-trap",
        "prompt": "I read that vitamin D supplementation reduces COVID-19 severity by 40% based on 3 observational studies with a combined 800 participants. How confident should I be in this finding?",
        "expected": "Low confidence — observational (confounders), moderate sample, pre-RCT evidence",
        "category": "calibration",
    },
    {
        "id": "Q12-anchoring",
        "prompt": "A researcher first found that a new cancer drug had a 50% response rate in a Phase 1 trial (n=20). The Phase 2 trial (n=200) showed only 22%. The Phase 3 trial (n=2000) showed 18%. What's your best estimate of the true response rate, and why did the estimates change?",
        "expected": "~18%, regression to the mean + publication bias in early trials + small sample variability",
        "category": "calibration",
    },
]


def main():
    model, tokenizer, device = load_qwen3()

    results = []
    for tp in TEST_PROMPTS:
        print(f"\n{'='*70}")
        print(f"[{tp['id']}] {tp['prompt'][:90]}...")
        print(f"Expected: {tp['expected']}")
        print(f"{'='*70}")

        resp = generate(model, tokenizer, device, tp["prompt"])

        print(f"\n--- THINKING ---")
        print(resp["thinking"][:800] if resp["thinking"] else "(no thinking trace)")
        if len(resp["thinking"]) > 800:
            print(f"  ... [{len(resp['thinking'])} chars total]")

        print(f"\n--- ANSWER ---")
        print(resp["answer"][:500])
        if len(resp["answer"]) > 500:
            print(f"  ... [{len(resp['answer'])} chars total]")

        results.append({
            "id": tp["id"],
            "category": tp["category"],
            "prompt": tp["prompt"],
            "expected": tp["expected"],
            "thinking": resp["thinking"],
            "answer": resp["answer"],
            "thinking_length": len(resp["thinking"]),
            "answer_length": len(resp["answer"]),
        })

    # Save full results
    out_path = Path(__file__).parent / "results" / "qwen3_baseline.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n\nFull results saved to {out_path}")

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    for r in results:
        think_len = r["thinking_length"]
        print(f"  {r['id']:30s}  think={think_len:5d} chars  answer={r['answer_length']:5d} chars")


if __name__ == "__main__":
    main()
