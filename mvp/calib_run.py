#!/usr/bin/env python
"""STAGE 2: the full base-vs-instruct calibration run. Prereg: docs/prereg-calibration-2026-08-28.md

Prompt machinery is IMPORTED from calib_pilot, never re-implemented, so the items the pilot graded
and the items this grades are rendered by the same code path.

Checkpoints every CKPT_EVERY items per cell. Two power cuts in one day earned this: a run that
cannot resume is a run that has to be lucky.
"""
import argparse, json, os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calib_pilot import load_bench, build_prompt, make_order, LETTERS

DEVICE = "mps"
CKPT_EVERY = 50


@torch.no_grad()
def run_cell(model_path, tag, bench, items, shots, k, n_perm, out, chat=False, chunk=0):
    done = []
    if os.path.exists(out):
        prev = json.load(open(out))
        if prev.get("complete"):
            print("  [skip] %s already complete (%d recs)" % (out, len(prev["records"])), flush=True)
            return prev
        done = prev["records"]
        print("  [resume] %s: %d records on disk" % (out, len(done)), flush=True)
    start_item = (max(r["item"] for r in done) + 1) if done else 0

    tok = AutoTokenizer.from_pretrained(model_path)
    hf = AutoModelForCausalLM.from_pretrained(model_path, dtype=torch.float16).to(DEVICE).eval()
    lids = []
    for L in LETTERS[:k]:
        ids = tok(" %s" % L, add_special_tokens=False)["input_ids"]
        assert len(ids) == 1, "' %s' is %d tokens on %s" % (L, len(ids), tag)
        lids.append(ids[0])
    assert len(set(lids)) == k, "letter tokens collide on %s" % tag

    recs, t0 = list(done), time.time()

    def save(complete):
        json.dump(dict(tag=tag, bench=bench, model=model_path, k=k, n_perm=n_perm,
                       n_items=len(items), chat=chat, complete=complete, records=recs),
                  open(out + ".tmp", "w"))
        os.replace(out + ".tmp", out)   # atomic: a cut mid-write must not truncate the checkpoint

    stop_at = len(items) if not chunk else min(len(items), start_item + chunk)
    for i in range(start_item, stop_at):
        it = items[i]
        for pi in range(n_perm):
            order = make_order(it, k, i, pi, n_perm)
            prompt, gold_pos = build_prompt(shots, it, k, order)
            if chat:
                # Secondary arm. enable_thinking=False: Qwen3.5's template appends <think>, and a
                # thinking budget the base model does not get is a compute confound, not a format.
                prompt = tok.apply_chat_template([{"role": "user", "content": prompt}],
                                                 tokenize=False, add_generation_prompt=True,
                                                 enable_thinking=False)
            ids = tok(prompt, return_tensors="pt")["input_ids"].to(DEVICE)
            p = torch.softmax(hf(ids).logits[0, -1].float(), dim=-1)
            lp = p[lids]
            mass = float(lp.sum())            # F-BB: the denominator, recorded for every pass
            q = (lp / lp.sum()).cpu().numpy()
            top = torch.topk(p, 3)
            recs.append(dict(item=i, perm=pi, gold=gold_pos, order=[int(x) for x in order],
                             pred=int(q.argmax()), conf=float(q.max()), mass=mass,
                             probs=[float(x) for x in q],
                             top1=tok.decode([int(top.indices[0])])))
        if (i + 1) % CKPT_EVERY == 0:
            save(False)
            n = len(recs) - len(done) or 1
            acc = np.mean([r["pred"] == r["gold"] for r in recs])
            print("    [%s/%s] %d/%d acc=%.3f %.2fs/pass"
                  % (tag, bench, i + 1, len(items), acc, (time.time() - t0) / n), flush=True)
    finished = stop_at >= len(items)
    save(finished)
    del hf
    torch.mps.empty_cache()
    if not finished:
        # exit signal for the driver: this process did its share, relaunch for the rest.
        print("    [chunk] %s/%s stopped at item %d/%d - relaunch to continue"
              % (tag, bench, stop_at, len(items)), flush=True)
    return json.load(open(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="models/Qwen3.5-4B-Base")
    ap.add_argument("--instruct", default="models/Qwen3.5-4B")
    ap.add_argument("--benches", required=True)
    ap.add_argument("--n-items", type=int, default=1500)
    ap.add_argument("--n-perm", type=int, default=2)
    ap.add_argument("--seed", type=int, default=20260828)
    ap.add_argument("--tag", default="Qwen3.5-4B")
    ap.add_argument("--chat", action="store_true")
    ap.add_argument("--chunk", type=int, default=0,
                    help="process at most N new items per process, then exit so the driver can "
                         "relaunch. Bounds MPS allocator growth: on mmlu_pro (10 options, ~4x "
                         "longer prompts) one 1500-item process degraded 4.3s -> 12.4s/pass and "
                         "was still climbing. 2026-08-28.")
    ap.add_argument("--only", default=None, help="base|instruct, to run one checkpoint per process")
    a = ap.parse_args()

    os.makedirs("results/workspace/calib", exist_ok=True)
    arm = "chat" if a.chat else "raw"
    roles = [("base", a.base), ("instruct", a.instruct)]
    if a.only:
        roles = [r for r in roles if r[0] == a.only]
    for bench in a.benches.split(","):
        items, shots, k = load_bench(bench, a.n_items, a.seed)
        print("\n=== %s | %s arm | %d items | k=%d ===" % (bench, arm, len(items), k), flush=True)
        for role, path in roles:
            out = "results/workspace/calib/run_%s_%s_%s_%s.json" % (a.tag, role, bench, arm)
            print("  [%s] %s -> %s" % (role.upper(), path, out), flush=True)
            run_cell(path, "%s-%s" % (a.tag, role.upper()), bench, items, shots, k,
                     a.n_perm, out, chat=a.chat, chunk=a.chunk)
    print("\n[ALL CELLS COMPLETE]", flush=True)


if __name__ == "__main__":
    sys.exit(main() or 0)
