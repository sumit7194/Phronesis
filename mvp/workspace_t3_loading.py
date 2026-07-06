#!/usr/bin/env python
"""Tier 3 — Workspace loading vs F189 boundary blindness (prereg-workspace-mac.md H3.1).

For the 7 WRINKLE (boundary) + 5 HARD (capability) failures and 12 correct comparators:
regenerate/reuse the greedy trace, then read the J-lens over the reasoning span at band
layers and ask: does the CORRECT answer ever enter the workspace?
Metrics per item: best lens rank of gold-answer token over (band layer, trace position);
same for produced answer; same for 3 random number tokens (null). Plus workspace loading
(max cos of residual to the token's lens vector).
Raw generations saved (guidelines §6). Prediction: correct items ~always load their answer
(trivially true late); boundary items never load GOLD; falsifier: boundary items load gold
as often as detectable errors / correct items.
"""
import argparse, json, os, re, sys, time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import (BAND, LENS_PATH, RESULTS_DIR, disk_ok, lens_vectors,
                              load_model, log, single_token_id, update_status)
from jlens.hooks import ActivationRecorder
from jlens.lens import JacobianLens
from reasoning_baseline import extract_answer, score, all_boxed

LEGACY = os.path.join(os.path.dirname(__file__), "results", "legibility")
GEN_CACHE = os.path.join(RESULTS_DIR, "t3_generations.json")
PRIMER = "\n\n</think>\n\nThe final answer is \\boxed{"


def build_prompt(tok, question):
    m = [{"role": "user", "content": question +
          "\nReason step by step, then give the final answer in \\boxed{}."}]
    try:
        return tok.apply_chat_template(m, add_generation_prompt=True, tokenize=False,
                                       enable_thinking=True)
    except TypeError:
        return tok.apply_chat_template(m, add_generation_prompt=True, tokenize=False)


@torch.no_grad()
def generate_trace(tok, hf, question, max_think=2048):
    text = build_prompt(tok, question)
    ids = tok(text, return_tensors="pt")["input_ids"].to("mps")
    out = hf.generate(input_ids=ids, attention_mask=torch.ones_like(ids),
                      max_new_tokens=max_think, do_sample=False,
                      pad_token_id=tok.eos_token_id)
    trace = tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True)
    if all_boxed(trace):
        ans = extract_answer(trace, "math500")
    else:
        pr = tok(PRIMER, add_special_tokens=False, return_tensors="pt")["input_ids"].to("mps")
        ids2 = torch.cat([out[0:1], pr], 1)
        o2 = hf.generate(input_ids=ids2, attention_mask=torch.ones_like(ids2),
                         max_new_tokens=32, do_sample=False, pad_token_id=tok.eos_token_id)
        ans = tok.decode(o2[0][ids2.shape[1]:], skip_special_tokens=True).split("}")[0].strip()
    torch.mps.empty_cache()
    return trace, ans


def number_token_ids(tok, s):
    """Candidate single-token ids for a (numeric) answer string: ' 13' and '13'."""
    out = []
    for form in (" " + s, s):
        ids = tok(form, add_special_tokens=False)["input_ids"]
        if len(ids) == 1:
            out.append(ids[0])
    return sorted(set(out))


def readout_item(tok, model, hf, lens, band, full_text, tracked, start_pos=0):
    """tracked: {label: [token_ids]}. Returns per-label best rank + max loading over
    (band layer, positions >= start_pos), so the question span is excluded."""
    ids = tok(full_text, return_tensors="pt")["input_ids"][:, :3072].to("mps")
    with ActivationRecorder(model.layers, at=band) as rec, torch.no_grad():
        hf.model(input_ids=ids, use_cache=False)
        acts = {l: rec.activations[l][0, start_pos:].detach() for l in band}  # [span, d]
    all_ids = sorted({t for v in tracked.values() for t in v})
    vecs = lens_vectors(lens, model, all_ids, band)  # {l: [n, d]} cpu fp32
    col = {t: j for j, t in enumerate(all_ids)}
    result = {lab: {"best_rank": None, "max_loading": None} for lab in tracked}
    CH = 512
    for l in band:
        h = acts[l].float()  # [span, d] mps
        J = lens.jacobians[l].to("mps")
        v_l = vecs[l].to("mps")  # [n, d]
        v_norm = v_l / (v_l.norm(dim=1, keepdim=True) + 1e-8)
        for s0 in range(0, h.shape[0], CH):
            hh = h[s0:s0 + CH]
            th = hh @ J.T                          # transported [ch, d]
            logits = model.unembed(th).float()     # [ch, vocab]
            loading = (hh / (hh.norm(dim=1, keepdim=True) + 1e-8)) @ v_norm.T  # [ch, n]
            for lab, tids in tracked.items():
                for t in tids:
                    ranks = (logits > logits[:, t:t + 1]).sum(dim=1) + 1
                    r = int(ranks.min().item())
                    ld = float(loading[:, col[t]].max().item())
                    cur = result[lab]
                    if cur["best_rank"] is None or r < cur["best_rank"]:
                        cur["best_rank"] = r
                    if cur["max_loading"] is None or ld > cur["max_loading"]:
                        cur["max_loading"] = ld
            del th, logits, loading
        del h, J
        torch.mps.empty_cache()
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=23)
    ap.add_argument("--n-correct", type=int, default=12)
    ap.add_argument("--max-think", type=int, default=2048)
    args = ap.parse_args()
    update_status("t3", state="running")
    t_start = time.time()
    rng = np.random.default_rng(args.seed)

    with open(os.path.join(LEGACY, "boundary_targets.json")) as f:
        targets = json.load(f)
    with open(os.path.join(LEGACY, "wrinkle_pool_full.json")) as f:
        pool = {r["qid"]: r for r in json.load(f)}
    with open(os.path.join(LEGACY, "reasoning_baseline_4b.json")) as f:
        base_rows = json.load(f)["rows"]

    tok, hf, model = load_model()
    lens = JacobianLens.load(LENS_PATH)
    band = [l for l in BAND if l in lens.source_layers]

    # ----- assemble items: 12 failures (regenerate) + N correct (reuse saved traces) -----
    gens = {}
    if os.path.exists(GEN_CACHE):
        with open(GEN_CACHE) as f:
            gens = json.load(f)
    items = []
    for group, qids in targets.items():
        for qid in qids:
            q, gold = pool[qid]["question"], pool[qid]["gold"]
            if qid not in gens:
                if not disk_ok(3.0):
                    log("disk guard hit during generation; stopping generations")
                    break
                log(f"generating {qid} ({group})")
                trace, ans = generate_trace(tok, hf, q, args.max_think)
                gens[qid] = {"trace": trace, "ans": ans}
                with open(GEN_CACHE, "w") as f:
                    json.dump(gens, f)
                update_status("t3", progress=f"gen {len(gens)}/12")
            g = gens[qid]
            items.append({"qid": qid, "group": group, "question": q, "gold": gold,
                          "ans": g["ans"], "trace": g["trace"],
                          "reproduced_error": not bool(score(g["ans"], gold, "gsm8k"))})
    correct_pool = [r for r in base_rows
                    if r.get("source") == "gsm8k" and r.get("greedy_ok") in (True, "True")
                    and r.get("greedy_trace")]
    sel = rng.choice(len(correct_pool), size=min(args.n_correct, len(correct_pool)),
                     replace=False)
    for i in sel:
        r = correct_pool[int(i)]
        items.append({"qid": r["id"], "group": "CORRECT", "question": r["question"],
                      "gold": str(r["gold"]), "ans": str(r["greedy_answer"]),
                      "trace": r["greedy_trace"], "reproduced_error": False})

    # ----- lens readout -----
    rows = []
    for i, it in enumerate(items):
        gold_ids = number_token_ids(tok, str(it["gold"]))
        prod_ids = number_token_ids(tok, str(it["ans"]))
        nulls = []
        while len(nulls) < 3:
            cand = str(rng.integers(2, 400))
            if cand in (str(it["gold"]), str(it["ans"])):
                continue
            cids = number_token_ids(tok, cand)
            if cids:
                nulls.append((cand, cids))
        if not gold_ids:
            rows.append({"qid": it["qid"], "group": it["group"], "skip": "gold multi-token"})
            continue
        tracked = {"gold": gold_ids}
        if prod_ids:
            tracked["produced"] = prod_ids
        for j, (c, cids) in enumerate(nulls):
            tracked[f"null_{j}"] = cids
        prompt_text = build_prompt(tok, it["question"])
        prompt_len = tok(prompt_text, return_tensors="pt")["input_ids"].shape[1]
        full_text = prompt_text + it["trace"]
        res = readout_item(tok, model, hf, lens, band, full_text, tracked,
                           start_pos=prompt_len)
        gold_verbalized = bool(re.search(rf"(?<![\d.]){re.escape(str(it['gold']))}(?![\d.])",
                                         it["trace"]))
        rows.append({"qid": it["qid"], "group": it["group"], "gold": it["gold"],
                     "ans": it["ans"], "reproduced_error": it["reproduced_error"],
                     "gold_verbalized_in_trace": gold_verbalized,
                     "null_words": [c for c, _ in nulls], **{f"{k}": v for k, v in res.items()}})
        log(f"  [{i + 1}/{len(items)}] {it['group']:8} {it['qid']:18} "
            f"gold_rank={res['gold']['best_rank']} "
            f"prod_rank={res.get('produced', {}).get('best_rank')}")
        update_status("t3", progress=f"readout {i + 1}/{len(items)}")

    def agg(group, key):
        vals = [r[key]["best_rank"] for r in rows
                if r.get("group") == group and key in r and r[key]["best_rank"]]
        return {"n": len(vals), "median_best_rank": float(np.median(vals)) if vals else None,
                "frac_top10": float(np.mean([v <= 10 for v in vals])) if vals else None}

    summary = {g: {"gold": agg(g, "gold"), "null_0": agg(g, "null_0")}
               for g in ("WRINKLE", "HARD", "CORRECT")}
    out = {"prereg": "docs/prereg-workspace-mac.md#tier-3", "seed": args.seed,
           "lens_n_prompts": lens.n_prompts, "band": band, "rows": rows,
           "summary": summary,
           "runtime_min": round((time.time() - t_start) / 60, 1)}
    with open(os.path.join(RESULTS_DIR, "t3_loading.json"), "w") as f:
        json.dump(out, f, indent=2)
    update_status("t3", state="done", summary={g: summary[g]["gold"] for g in summary},
                  runtime_min=out["runtime_min"])
    log(f"t3 done: {json.dumps(summary, indent=1)}")


if __name__ == "__main__":
    main()
