#!/usr/bin/env python
"""STAGE 1 of the base-vs-instruct calibration study: pick the benchmark. Never touch the outcome.

The question the real experiment asks is whether post-training raises RESOLUTION (it learned which
items it knows) or only makes the model louder. This script does not measure that and must not: it
selects the benchmark on two criteria that are independent of the base-vs-instruct contrast --

  1. DIFFICULTY BAND. Both checkpoints must land strictly inside [BAND_LO, BAND_HI]. A benchmark
     where the instruct model is at ceiling, or the base model is at chance, has no calibration
     curve to measure -- every item lands in one bin. Floor is as fatal as ceiling.
  2. PROBE VALIDITY (F-BB). The DV is a renormalised softmax over the option letters. If those
     tokens carry no mass, the whole measurement is a ratio of noise. Nothing in the mindedness arc
     recorded that denominator for seven days. This records it before anything else runs.

It also reports letter bias and per-pass timing, both of which size the real run.

FORMAT IS MATCHED BY CONSTRUCTION: base and instruct get the byte-identical raw few-shot prompt, no
chat template. Half the base-vs-instruct comparisons in the mindedness arc were uninterpretable
because base ran on raw text and instruct ran on a chat template, so any difference could be either.
The chat-template arm is a separate condition in the real run, not a substitute for this one.
"""
import argparse, json, os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

DEVICE = "mps"
BAND_LO, BAND_HI = 0.35, 0.80      # both checkpoints must sit inside this to qualify
MASS_FLOOR = 0.50                  # median raw mass on the option letters
MASS_TAIL_MAX = 0.10               # max fraction of passes with mass < 0.10
N_SHOT = 5
LETTERS = "ABCDEFGHIJ"
HEADER = "The following are multiple choice questions (with answers).\n\n"


def load_bench(name, n_items, seed):
    """Return (items, few_shot_items, k). Item: dict(question, options[list], answer_idx)."""
    from datasets import load_dataset
    rng = np.random.default_rng(seed)
    if name == "mmlu_cf":
        val = load_dataset("microsoft/MMLU-CF", split="val")
        dev = load_dataset("microsoft/MMLU-CF", split="dev")
        def conv(r):
            return dict(question=r["Question"],
                        options=[r["A"].strip(), r["B"].strip(), r["C"].strip(), r["D"].strip()],
                        answer_idx="ABCD".index(r["Answer"].strip()))
        pool = [conv(val[int(i)]) for i in rng.choice(val.num_rows, n_items, replace=False)]
        shots = [conv(dev[i]) for i in range(min(N_SHOT, dev.num_rows))]
        return pool, shots, 4
    if name == "mmlu_pro":
        test = load_dataset("TIGER-Lab/MMLU-Pro", split="test")
        val = load_dataset("TIGER-Lab/MMLU-Pro", split="validation")
        # Option count varies (10 for 9981 items, 4 for 606). Mixed k means a per-item chance
        # level, which makes a pooled calibration curve meaningless. Keep k=10 only.
        keep = [i for i, o in enumerate(test["options"]) if len(o) == 10]
        def conv(r):
            return dict(question=r["question"], options=[o.strip() for o in r["options"]],
                        answer_idx=int(r["answer_index"]))
        pool = [conv(test[int(keep[int(i)])])
                for i in rng.choice(len(keep), n_items, replace=False)]
        vk = [i for i, o in enumerate(val["options"]) if len(o) == 10][:N_SHOT]
        shots = [conv(val[int(i)]) for i in vk]
        return pool, shots, 10
    raise ValueError(name)


def render(item, k, with_answer, perm=None):
    """perm maps DISPLAY position -> original option index, so the gold letter moves."""
    opts = item["options"][:k]
    order = list(range(k)) if perm is None else list(perm)
    s = "Question: %s\n" % item["question"]
    for pos, oi in enumerate(order):
        s += "%s. %s\n" % (LETTERS[pos], opts[oi])
    s += "Answer:"
    gold_pos = order.index(item["answer_idx"])
    if with_answer:
        s += " %s\n\n" % LETTERS[gold_pos]
    return s, gold_pos


def build_prompt(shots, item, k, perm):
    p = HEADER + "".join(render(s, k, True)[0] for s in shots)
    body, gold_pos = render(item, k, False, perm)
    return p + body, gold_pos


def make_order(item, k, item_idx, pi, n_perm):
    """Deterministic display order that places the gold answer at a CHOSEN position.

    A rolled permutation looked fine and was not: on MMLU-Pro it put the gold on option C for 25%
    of renders and on H for 0%. Any letter bias in the model then reads straight through into
    accuracy. Placing the gold explicitly makes its position sweep all k slots uniformly across
    (item x perm), so letter bias averages out instead of aliasing with the answer key.
    """
    gi = item["answer_idx"]
    distract = [j for j in range(k) if j != gi]
    r = (item_idx + pi) % len(distract)                  # rotate distractors too, deterministically
    distract = distract[r:] + distract[:r]
    gold_pos = (item_idx + pi * max(1, k // max(1, n_perm))) % k
    return distract[:gold_pos] + [gi] + distract[gold_pos:]


@torch.no_grad()
def run_checkpoint(model_path, tag, bench, items, shots, k, out, n_perm, every=25):
    tok = AutoTokenizer.from_pretrained(model_path)
    hf = AutoModelForCausalLM.from_pretrained(model_path, dtype=torch.float16).to(DEVICE).eval()

    # Letter tokenisation is a real failure mode, not a formality: if " A" is not a single token
    # the readout silently measures a prefix. Assert, do not hope.
    lids = []
    for L in LETTERS[:k]:
        ids = tok(" %s" % L, add_special_tokens=False)["input_ids"]
        assert len(ids) == 1, "' %s' tokenises to %d tokens on %s: %s" % (L, len(ids), tag, ids)
        lids.append(ids[0])
    assert len(set(lids)) == k, "letter tokens collide on %s: %s" % (tag, lids)

    recs, t0 = [], time.time()
    for i, it in enumerate(items):
        for pi in range(n_perm):
            # Deterministic per (item, pi): no RNG state, so a resume reproduces it exactly.
            prompt, gold_pos = build_prompt(shots, it, k, make_order(it, k, i, pi, n_perm))
            ids = tok(prompt, return_tensors="pt")["input_ids"].to(DEVICE)
            p = torch.softmax(hf(ids).logits[0, -1].float(), dim=-1)
            lp = p[lids]                               # raw, BEFORE renormalisation
            mass = float(lp.sum())                     # <- F-BB: the denominator, recorded
            q = (lp / lp.sum()).cpu().numpy()
            top = torch.topk(p, 3)
            recs.append(dict(item=i, perm=pi, gold=gold_pos, pred=int(q.argmax()),
                             conf=float(q.max()), mass=mass,
                             probs=[float(x) for x in q],
                             top1=tok.decode([int(top.indices[0])])))
        if every and (i + 1) % every == 0:
            acc = np.mean([r["pred"] == r["gold"] for r in recs])
            print("    [%s/%s] %d/%d  acc=%.3f  %.2fs/pass"
                  % (tag, bench, i + 1, len(items), acc, (time.time() - t0) / len(recs)), flush=True)

    del hf
    torch.mps.empty_cache()

    mass = np.array([r["mass"] for r in recs])
    picks = np.bincount([r["pred"] for r in recs], minlength=k) / len(recs)
    res = dict(tag=tag, bench=bench, model=model_path, n_items=len(items), n_perm=n_perm, k=k,
               acc=float(np.mean([r["pred"] == r["gold"] for r in recs])), chance=1.0 / k,
               mass_mean=float(mass.mean()), mass_median=float(np.median(mass)),
               mass_p10=float(np.percentile(mass, 10)),
               frac_mass_lt_010=float((mass < 0.10).mean()),
               frac_mass_lt_001=float((mass < 0.01).mean()),
               top1_is_letter=float(np.mean([r["top1"].strip() in LETTERS[:k] for r in recs])),
               letter_pick_dist=[float(x) for x in picks],
               letter_bias_maxdev=float(np.abs(picks - 1.0 / k).max()),
               gold_pos_dist=[float(x) for x in
                              np.bincount([r["gold"] for r in recs], minlength=k) / len(recs)],
               mean_conf=float(np.mean([r["conf"] for r in recs])),
               sec_per_pass=(time.time() - t0) / len(recs))
    json.dump(dict(summary=res, records=recs), open(out, "w"))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="models/Qwen3.5-4B-Base")
    ap.add_argument("--instruct", default="models/Qwen3.5-4B")
    ap.add_argument("--benches", default="mmlu_cf,mmlu_pro")
    ap.add_argument("--n-items", type=int, default=200)
    ap.add_argument("--n-perm", type=int, default=2)
    ap.add_argument("--seed", type=int, default=20260827)
    ap.add_argument("--tag", default="Qwen3.5-4B")
    a = ap.parse_args()

    os.makedirs("results/workspace/calib", exist_ok=True)
    verdicts = {}
    for bench in a.benches.split(","):
        items, shots, k = load_bench(bench, a.n_items, a.seed)
        print("\n=== %s: %d items, k=%d, %d-shot ===" % (bench, len(items), k, len(shots)), flush=True)
        row = {}
        for role, path in (("BASE", a.base), ("INSTRUCT", a.instruct)):
            out = "results/workspace/calib/pilot_%s_%s_%s.json" % (a.tag, role.lower(), bench)
            print("  [%s] %s" % (role, path), flush=True)
            row[role] = run_checkpoint(path, "%s-%s" % (a.tag, role), bench, items, shots, k,
                                       out, a.n_perm)
        verdicts[bench] = row

    print("\n" + "=" * 96)
    print("%-10s %-9s %6s %7s %8s %8s %7s %6s %7s"
          % ("bench", "role", "acc", "chance", "massMed", "mass<.1", "top1=L", "bias", "s/pass"))
    print("-" * 96)
    for bench, row in verdicts.items():
        for role, r in row.items():
            print("%-10s %-9s %6.3f %7.3f %8.3f %8.3f %7.3f %6.3f %7.2f"
                  % (bench, role, r["acc"], r["chance"], r["mass_median"], r["frac_mass_lt_010"],
                     r["top1_is_letter"], r["letter_bias_maxdev"], r["sec_per_pass"]))

    print("\nSELECTION (criteria fixed before the run; none of them is the outcome):")
    ok = []
    for bench, row in verdicts.items():
        accs = {r: v["acc"] for r, v in row.items()}
        band = all(BAND_LO <= v <= BAND_HI for v in accs.values())
        valid = all(v["mass_median"] >= MASS_FLOOR and v["frac_mass_lt_010"] <= MASS_TAIL_MAX
                    for v in row.values())
        print("  %-10s band[%.2f,%.2f] %-4s (%s)   probe-validity %s"
              % (bench, BAND_LO, BAND_HI, "PASS" if band else "FAIL",
                 ", ".join("%s=%.3f" % (r, v) for r, v in accs.items()),
                 "PASS" if valid else "FAIL"))
        if band and valid:
            ok.append(bench)
    print("\n  QUALIFYING: %s" % (ok or "NONE - do not proceed; widen or change the benchmark"))
    json.dump(dict(verdicts=verdicts, qualifying=ok,
                   criteria=dict(band=[BAND_LO, BAND_HI], mass_floor=MASS_FLOOR,
                                 mass_tail_max=MASS_TAIL_MAX)),
              open("results/workspace/calib/pilot_%s_SUMMARY.json" % a.tag, "w"), indent=1)


if __name__ == "__main__":
    sys.exit(main() or 0)
