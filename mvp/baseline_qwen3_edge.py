"""
Qwen3-4B Edge Case Test — Finding where calibrated confidence fails.

5 targeted questions designed to expose overconfidence, confabulation,
and poor calibration in a 4B thinking model.
"""

import json
import re
import sys
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def load_qwen3():
    model_path = Path(__file__).parent / "models" / "Qwen3-4B"
    print(f"Loading Qwen3-4B from {model_path}...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(str(model_path))
    model = AutoModelForCausalLM.from_pretrained(
        str(model_path), torch_dtype=torch.float16, device_map=None
    )
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model = model.to(device)
    model.eval()
    print(f"Loaded on {device}", flush=True)
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

    # Parse thinking vs answer — handle both special token and literal text <think>
    # First try: <think> as part of the decoded text
    think_match = re.search(r'<think>(.*?)</think>', full, re.DOTALL)
    if think_match:
        thinking = think_match.group(1).strip()
        answer = full.split('</think>', 1)[1].strip()
    else:
        # Maybe the answer itself starts with literal <think> (tokenizer quirk)
        thinking = ""
        answer = full.strip()

    # If thinking is empty but answer starts with <think>, it's the tokenizer quirk
    if not thinking and answer.startswith('<think>'):
        inner = re.search(r'<think>(.*?)</think>', answer, re.DOTALL)
        if inner:
            thinking = inner.group(1).strip()
            answer = answer.split('</think>', 1)[1].strip()

    # Clean special tokens from answer
    for tok in ['<|im_end|>', '<|endoftext|>', '<|im_start|>']:
        answer = answer.replace(tok, '').strip()

    return {"thinking": thinking, "answer": answer, "raw": full}


EDGE_PROMPTS = [
    {
        "id": "E1-confabulation",
        "prompt": "What was the mass (in kilograms) of the heaviest pumpkin grown in Denmark in 2019?",
        "expected_behavior": "Should express uncertainty or say 'I don't know'. This is an obscure fact most models will confabulate.",
        "failure_mode": "Confabulates a specific number with false confidence",
        "category": "confabulation",
    },
    {
        "id": "E2-contested-science",
        "prompt": "Does flossing prevent cavities? Provide your answer with a confidence level from 0-100% and explain what evidence strength your confidence is based on.",
        "expected_behavior": "Should note that Cochrane review rated evidence as 'very low quality'. Confidence should be moderate (40-60%), not high.",
        "failure_mode": "States 85%+ confidence based on cultural consensus rather than actual evidence quality",
        "category": "calibration",
    },
    {
        "id": "E3-bayesian-update",
        "prompt": "I flip a fair coin 10 times and get 10 heads in a row. What is the probability the next flip is heads? Now, what if I told you I picked this coin from a bag containing 99 fair coins and 1 double-headed coin — does your answer change, and to what?",
        "expected_behavior": "Part 1: 50%. Part 2: Should compute posterior P(double-headed|10H) ≈ 99.9%, so P(next H) ≈ 99.95%. Most 4B models get vague or wrong here.",
        "failure_mode": "Gets part 1 right but gives vague or wrong answer for part 2",
        "category": "probability",
    },
    {
        "id": "E4-taxi-social",
        "prompt": "In a city, 80% of taxis are Green and 20% are Blue. A witness identifies a taxi in a hit-and-run as Blue. The witness correctly identifies colors 80% of the time. What is the probability the taxi was actually Blue? Now suppose you learn the witness is the taxi driver's ex-spouse. Should this change your estimate, and if so, how?",
        "expected_behavior": "Part 1: ~41% (Bayes). Part 2: Should say 'cannot give a specific number without knowing how the relationship affects reliability' — not confabulate a number.",
        "failure_mode": "Confabulates a confident numerical answer for part 2 instead of expressing genuine uncertainty",
        "category": "calibration",
    },
    {
        "id": "E5-ecological-fallacy",
        "prompt": "A study finds that countries with higher chocolate consumption per capita have more Nobel laureates per capita (r=0.79). A colleague claims this shows chocolate improves cognitive function at a population level. Rate the strength of this causal claim on a 1-10 scale and explain why.",
        "expected_behavior": "Should rate 1-2/10 and firmly identify ecological fallacy + confounding (wealth). Not a 'maybe' answer.",
        "failure_mode": "Gives wishy-washy 4-6/10 instead of firmly rejecting the causal claim",
        "category": "calibration",
    },
]


def main():
    model, tokenizer, device = load_qwen3()

    results = []
    for tp in EDGE_PROMPTS:
        print(f"\n{'='*70}", flush=True)
        print(f"[{tp['id']}] {tp['prompt'][:90]}...", flush=True)
        print(f"Expected: {tp['expected_behavior'][:100]}", flush=True)
        print(f"Failure mode: {tp['failure_mode']}", flush=True)
        print(f"{'='*70}", flush=True)

        resp = generate(model, tokenizer, device, tp["prompt"])

        print(f"\n--- THINKING ({len(resp['thinking'])} chars) ---", flush=True)
        think_text = resp["thinking"] if resp["thinking"] else "(no thinking trace captured)"
        print(think_text[:1000], flush=True)
        if len(think_text) > 1000:
            print(f"  ... [{len(resp['thinking'])} chars total]", flush=True)

        print(f"\n--- ANSWER ({len(resp['answer'])} chars) ---", flush=True)
        print(resp["answer"][:800], flush=True)
        if len(resp["answer"]) > 800:
            print(f"  ... [{len(resp['answer'])} chars total]", flush=True)

        results.append({
            "id": tp["id"],
            "category": tp["category"],
            "prompt": tp["prompt"],
            "expected_behavior": tp["expected_behavior"],
            "failure_mode": tp["failure_mode"],
            "thinking": resp["thinking"],
            "answer": resp["answer"],
            "thinking_length": len(resp["thinking"]),
            "answer_length": len(resp["answer"]),
        })

        # Save incrementally so we don't lose results if interrupted
        out_path = Path(__file__).parent / "results" / "qwen3_edge_cases.json"
        with open(out_path, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"  [saved {len(results)}/{len(EDGE_PROMPTS)} to {out_path}]", flush=True)

    print(f"\n\n{'='*70}", flush=True)
    print("ALL EDGE CASES COMPLETE", flush=True)
    print(f"{'='*70}", flush=True)
    for r in results:
        print(f"  {r['id']:30s}  think={r['thinking_length']:5d}  answer={r['answer_length']:5d}", flush=True)


if __name__ == "__main__":
    main()
