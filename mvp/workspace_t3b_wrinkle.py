#!/usr/bin/env python
"""Tier 3b — Wrinkle-concept workspace loading (prereg AMENDMENT A1, H3.1-amended).

Per boundary item: does the pivotal wrinkle CONCEPT (declared in workspace_t3b_stimuli.json)
load into the workspace during (a) the model's own failing greedy trace vs (b) a
teacher-forced correct solution of the same problem? Nulls: 3 random word tokens + 1 random
digit. Positive control: the trace's own produced answer digits (should hit rank ~1).
Failing traces reuse/extend t3_generations.json (cached, disk-guarded).
"""
import argparse, json, os, sys, time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import (BAND, LENS_PATH, RESULTS_DIR, disk_ok, load_model, log,
                              single_token_id, update_status)
from workspace_t3_loading import (GEN_CACHE, LEGACY, build_prompt, generate_trace,
                                  readout_item)
from jlens.lens import JacobianLens
from reasoning_baseline import score

NULL_WORDS = [" piano", " glacier", " walnut", " lantern", " falcon", " marble",
              " compass", " anchor", " velvet", " harbor"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=31)
    ap.add_argument("--max-think", type=int, default=2048)
    args = ap.parse_args()
    update_status("t3b", state="running")
    t_start = time.time()
    rng = np.random.default_rng(args.seed)

    with open(os.path.join(os.path.dirname(__file__), "workspace_t3b_stimuli.json")) as f:
        stimuli = json.load(f)["items"]
    with open(os.path.join(LEGACY, "wrinkle_pool_full.json")) as f:
        pool = {r["qid"]: r for r in json.load(f)}

    tok, hf, model = load_model()
    lens = JacobianLens.load(LENS_PATH)
    band = [l for l in BAND if l in lens.source_layers]
    log(f"lens n_prompts={lens.n_prompts}, band={band}")

    gens = {}
    if os.path.exists(GEN_CACHE):
        with open(GEN_CACHE) as f:
            gens = json.load(f)

    rows = []
    for i, (qid, st) in enumerate(stimuli.items()):
        q, gold = pool[qid]["question"], pool[qid]["gold"]
        # -- failing trace: cached or regenerate --
        if qid not in gens:
            if not disk_ok(3.0):
                log(f"disk guard: skipping generation for {qid}")
                rows.append({"qid": qid, "group": st["group"], "skip": "disk_guard_no_trace"})
                continue
            log(f"generating {qid}")
            trace, ans = generate_trace(tok, hf, q, args.max_think)
            gens[qid] = {"trace": trace, "ans": ans}
            with open(GEN_CACHE, "w") as f:
                json.dump(gens, f)
            update_status("t3b", progress=f"gen {qid} ({i + 1}/{len(stimuli)})")
        trace, ans = gens[qid]["trace"], gens[qid]["ans"]

        # -- tracked token sets (runtime-filtered to single tokens) --
        concepts = {}
        for w in st["concepts"]:
            tid = single_token_id(tok, w.strip())
            if tid is not None:
                concepts[w.strip()] = [tid]
        null_words = rng.choice(NULL_WORDS, size=3, replace=False)
        tracked = {f"concept:{w}": v for w, v in concepts.items()}
        for w in null_words:
            tid = single_token_id(tok, w.strip())
            if tid is not None:
                tracked[f"null:{w.strip()}"] = [tid]
        null_digit = str(rng.integers(2, 10))
        tracked[f"null_digit:{null_digit}"] = [single_token_id(tok, null_digit),
                                               single_token_id(tok, null_digit,
                                                               prefix_space=False)]
        tracked = {k: [t for t in v if t is not None] for k, v in tracked.items()}
        tracked = {k: v for k, v in tracked.items() if v}
        # positive control: first digit of the produced answer (model wrote it)
        digits = [c for c in str(ans) if c.isdigit()]
        if digits:
            ids = [single_token_id(tok, digits[0], prefix_space=False)]
            tracked["poscontrol:ans_digit"] = [t for t in ids if t is not None]

        prompt_text = build_prompt(tok, q)
        prompt_len = tok(prompt_text, return_tensors="pt")["input_ids"].shape[1]
        arms = {"fail_trace": prompt_text + trace,
                "teacher_correct": prompt_text + st["correct_solution"]}
        row = {"qid": qid, "group": st["group"], "gold": gold, "ans": ans,
               "reproduced_error": not bool(score(ans, gold, "gsm8k")),
               "tracked": sorted(tracked), "null_digit": null_digit}
        for arm, text in arms.items():
            res = readout_item(tok, model, hf, lens, band, text, tracked,
                               start_pos=prompt_len)
            row[arm] = {k: v for k, v in res.items()}
        rows.append(row)
        cbest = min((row["fail_trace"][k]["best_rank"] for k in row["fail_trace"]
                     if k.startswith("concept:")), default=None)
        tbest = min((row["teacher_correct"][k]["best_rank"] for k in row["teacher_correct"]
                     if k.startswith("concept:")), default=None)
        log(f"  [{i + 1}/{len(stimuli)}] {st['group']:7} {qid:18} "
            f"concept best-rank fail={cbest} teacher={tbest}")
        update_status("t3b", progress=f"readout {i + 1}/{len(stimuli)}")

    # -- aggregate: per group, per arm, median of per-item best concept rank vs null rank --
    def med(group, arm, prefix):
        vals = []
        for r in rows:
            if r.get("group") != group or arm not in r:
                continue
            v = [r[arm][k]["best_rank"] for k in r[arm] if k.startswith(prefix)
                 and r[arm][k]["best_rank"]]
            if v:
                vals.append(min(v))
        return {"n": len(vals), "median": float(np.median(vals)) if vals else None,
                "frac_top10": float(np.mean([v <= 10 for v in vals])) if vals else None}

    summary = {}
    for g in ("WRINKLE", "HARD"):
        summary[g] = {arm: {"concept": med(g, arm, "concept:"),
                            "null": med(g, arm, "null:"),
                            "poscontrol": med(g, arm, "poscontrol:")}
                      for arm in ("fail_trace", "teacher_correct")}
    out = {"prereg": "docs/prereg-workspace-mac.md#amendment-a1", "seed": args.seed,
           "lens_n_prompts": lens.n_prompts, "band": band, "rows": rows,
           "summary": summary, "runtime_min": round((time.time() - t_start) / 60, 1)}
    with open(os.path.join(RESULTS_DIR, "t3b_wrinkle.json"), "w") as f:
        json.dump(out, f, indent=2)
    update_status("t3b", state="done", runtime_min=out["runtime_min"])
    log("t3b done:\n" + json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
