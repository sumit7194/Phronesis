import json
import re
from pathlib import Path
from collections import defaultdict

def extract_metric(prompt_id, answer, thinking):
    ans = answer.lower()
    think = thinking.lower()
    
    if prompt_id == "N1-simpsons-paradox":
        has_simpsons = "simpson" in ans or "simpson" in think
        return f"Simpson's mentioned: {has_simpsons}"

    elif prompt_id == "N2-conjunction-fallacy":
        # look for A, B, C, D ranking
        m = re.search(r"([abcd])\s*[>\-]\s*([abcd])\s*[>\-]\s*([abcd])\s*[>\-]\s*([abcd])", ans, re.IGNORECASE)
        if m: return f"Rank: {' > '.join(m.groups()).upper()}"
        return "Rank: Cannot parse"

    elif prompt_id == "N3-survivorship-bias" or prompt_id == "E5-ecological-fallacy":
        m = re.search(r"(\d+)/10", ans)
        if m: return f"Score: {m.group(1)}/10"
        return "Score: Cannot parse"

    elif prompt_id == "E1-confabulation":
        m = re.search(r"(\d+)\s*kilograms?", ans)
        if m: return f"Weight: {m.group(1)} kg"
        return "Weight: Missing"

    elif prompt_id == "E2-contested-science":
        m = re.search(r"(\d+)%", ans)
        if m: return f"Confidence: {m.group(1)}%"
        return "Confidence: Missing"

    elif prompt_id == "E3-bayesian-update" or prompt_id == "E4-taxi-social":
        # Look for percent or fractions
        m = re.search(r"(\d+(?:\.\d+)?)\s*%", ans)
        if m: return f"Probability: {m.group(1)}%"
        return "Probability: Cannot parse"

    return "N/A"

prompts = [
    "N1-simpsons-paradox", "N2-conjunction-fallacy", "N3-survivorship-bias",
    "E1-confabulation", "E2-contested-science", "E3-bayesian-update",
    "E4-taxi-social", "E5-ecological-fallacy"
]

vectors = [
    ("baseline", 0.0),
    ("hand_LT_L10", -4.0), ("hand_LT_L10", 2.0), ("hand_LT_L10", 8.0),
    ("hand_LT_L22", -4.0), ("hand_LT_L22", 2.0), ("hand_LT_L22", 8.0),
    ("son_LT_L34", -4.0), ("son_LT_L34", 2.0), ("son_LT_L34", 8.0),
    ("random_L22", -4.0), ("random_L22", 2.0), ("random_L22", 8.0)
]

base_dir = Path("results/steering_v2/qwen3-4b")

with open("qualitative_dump.txt", "w") as out:
    for pid in prompts:
        out.write(f"\n================ {pid} ================\n")
        for vec_name, alpha in vectors:
            sign = "+" if alpha >= 0 else "-"
            # Format path
            if vec_name == "baseline":
                p = base_dir / "baselines" / f"{pid}.json"
            else:
                tag = f"a{sign}{abs(alpha):05.2f}"
                p = base_dir / vec_name / tag / f"{pid}.json"
            
            if not p.exists():
                out.write(f"{vec_name:15} @ {alpha:4.1f} | MISSING\n")
                continue
                
            data = json.loads(p.read_text())
            t = data.get("thinking", "")
            a = data.get("answer", "")
            tokens = data.get("n_new_tokens")
            hit_limit = data.get("thinking_truncated")
            
            metric = extract_metric(pid, a, t)
            if hit_limit: metric = "TRUNCATED_THINKING_SPIRAL"
            
            status = f"{len(t):5}c think | {len(a):5}c ans | {metric}"
            out.write(f"{vec_name:15} @ {alpha:4.1f} | {status}\n")

        out.write("\n")
