#!/usr/bin/env python
"""Tier 2 — Fit the Jacobian lens on Qwen3-4B (prereg-workspace-mac.md Tier 2).

Wraps jlens.fit with: absolute wall-clock deadline (stop starting new prompts after it),
per-prompt checkpointing (repo native), disk guard, and a saved usable lens at exit
whatever n was reached. Resumable: re-running continues from the checkpoint.

  --until "HH:MM"    stop starting prompts after this local time (default 07:00)
  --max-prompts N    cap (default 100)
"""
import argparse, datetime, json, logging, os, sys, time

import torch

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import (FIT_CKPT, FIT_LAYERS, LENS_PATH, RESULTS_DIR, disk_ok,
                              load_model, log, update_status, wikitext_chunks)
import jlens
from jlens import fitting
from jlens.lens import JacobianLens

DIM_BATCH = 4  # was 8: 11.6GB alloc pushed the 16GB machine into ~10GB swap and the
               # overnight fit crawled (1 prompt / 6.7h). Halved to keep out of swap;
               # same total FLOPs, 2x the backward passes. dim_batch is not part of the
               # estimator, so resuming a dim_batch=8 checkpoint with 4 is valid.


def deadline_epoch(hhmm):
    now = datetime.datetime.now()
    h, m = map(int, hhmm.split(":"))
    dl = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if dl <= now:
        dl += datetime.timedelta(days=1)
    return dl.timestamp()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--until", default="07:00")
    ap.add_argument("--max-prompts", type=int, default=100)
    args = ap.parse_args()
    deadline = deadline_epoch(args.until)
    update_status("t2_fit", state="running", until=args.until)

    tok, hf, model = load_model()
    prompts = wikitext_chunks(tok, args.max_prompts, seed=0)  # fit corpus: seed 0 (t1 held out uses seed 1)
    log(f"fit corpus: {len(prompts)} prompts; deadline {args.until}; layers {FIT_LAYERS}")

    # Wrap jacobian_for_prompt with deadline + disk guard + heartbeat, then let the
    # repo's fit() own the loop/averaging/checkpointing.
    original = fitting.jacobian_for_prompt
    done_counter = {"n": 0}

    def guarded(model_, prompt, source_layers, **kw):
        # TimeoutError propagates out of fit() (it only catches ValueError), so the
        # checkpoint keeps next_idx at the first unprocessed prompt and a later
        # resume run continues correctly.
        if time.time() > deadline:
            raise TimeoutError("deadline reached")
        if not disk_ok(3.0):
            raise TimeoutError("disk guard: <3GB free")
        result = original(model_, prompt, source_layers, **kw)
        done_counter["n"] += 1
        update_status("t2_fit", progress=f"{done_counter['n']} prompts this run",
                      minutes_to_deadline=round((deadline - time.time()) / 60))
        return result

    fitting.jacobian_for_prompt = guarded
    try:
        lens = fitting.fit(
            model, prompts,
            source_layers=FIT_LAYERS,
            dim_batch=DIM_BATCH,
            max_seq_len=128,
            checkpoint_path=FIT_CKPT,
            checkpoint_every=1,
            resume=True,
        )
    except TimeoutError as exc:
        log(f"fit stopped: {exc}; rebuilding lens from checkpoint")
        state = torch.load(FIT_CKPT, map_location="cpu", weights_only=True)
        if state["n_done"] == 0:
            update_status("t2_fit", state="failed", reason=str(exc))
            sys.exit(1)
        lens = JacobianLens(
            jacobians={l: s / state["n_done"] for l, s in state["jacobian_sum"].items()},
            n_prompts=state["n_done"], d_model=model.d_model)
    finally:
        fitting.jacobian_for_prompt = original

    lens.save(LENS_PATH)
    meta = {"n_prompts": lens.n_prompts, "source_layers": lens.source_layers,
            "dim_batch": DIM_BATCH, "corpus": "wikitext seed0 128tok",
            "saved": time.strftime("%Y-%m-%d %H:%M:%S")}
    with open(os.path.join(RESULTS_DIR, "t2_fit_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    update_status("t2_fit", state="done", **meta)
    log(f"lens saved: n_prompts={lens.n_prompts} -> {LENS_PATH}")


if __name__ == "__main__":
    main()
