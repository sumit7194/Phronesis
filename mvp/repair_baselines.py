"""
Re-parse baselines that have thinking leaked into the answer field.
Fixes E3-bayesian-update and N2-conjunction-fallacy where the model
hit the token limit before closing the think tag.
"""
import json
import re
from pathlib import Path

IM_END = "\x3c|im_end|\x3e"
ENDOFTEXT = "\x3c|endoftext|\x3e"
IM_START = "\x3c|im_start|\x3e"
THINK_OPEN = "\x3cthink\x3e"
THINK_CLOSE = "\x3c/think\x3e"

SPECIAL_TOKENS = [IM_END, ENDOFTEXT, IM_START]

base = Path("results/steering_v2/qwen3-4b")


def reparse(data):
    """Re-parse a result dict, fixing the think/answer split."""
    # Reconstruct full raw output from thinking + answer
    old_think = data["thinking"]
    old_ans = data["answer"]

    # If thinking is empty but answer starts with <think>, reconstruct
    if old_think == "" and THINK_OPEN in old_ans:
        full = old_ans
    elif old_think and THINK_CLOSE not in old_ans:
        # Already properly parsed
        return data, False
    else:
        return data, False

    # Re-parse
    thinking = ""
    answer = full.strip()
    thinking_truncated = False

    m = re.search(re.escape(THINK_OPEN) + r"(.*?)" + re.escape(THINK_CLOSE),
                  full, re.DOTALL)
    if m:
        thinking = m.group(1).strip()
        answer = full.split(THINK_CLOSE, 1)[1].strip()
    elif THINK_OPEN in full:
        thinking = full.split(THINK_OPEN, 1)[1].strip()
        answer = ""
        thinking_truncated = True

    for tok in SPECIAL_TOKENS:
        answer = answer.replace(tok, "").strip()

    data["thinking"] = thinking
    data["answer"] = answer
    data["thinking_truncated"] = thinking_truncated
    return data, True


# Find and fix all results
fixed_count = 0
for json_path in sorted(base.rglob("*.json")):
    if json_path.name == "manifest.json":
        continue
    data = json.load(open(json_path))
    if "answer" not in data:
        continue

    data, changed = reparse(data)
    if changed:
        print(f"FIXED: {json_path.relative_to(base)}")
        print(f"  think: 0 -> {len(data['thinking'])}c")
        print(f"  answer: was huge -> {len(data['answer'])}c")
        print(f"  truncated: {data['thinking_truncated']}")

        with open(json_path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        fixed_count += 1

print(f"\nFixed {fixed_count} files")
