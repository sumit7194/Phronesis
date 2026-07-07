#!/usr/bin/env python
"""E0 — insight-problem screen (docs/research-workspace-incubation-lit.md, five properties).

Per problem in incubation_insight_problems.json:
  plain greedy -> (if fail) 8 plain samples     [stable failure: <=1/8 solves]
  minimal-hint greedy -> (if fail) 3 samples    [<=5-word kernel hint]
  explicit-hint greedy -> (if fail) 3 samples   [full-sentence hint]
usable(A) = stable_fail AND minimal-hint flips; usable(B) = only explicit flips.
Full raw traces saved (auto-score is a prefilter; hand-read before claims, §3).
On completion touches results/workspace/SCREEN_DONE -> the night chain starts the lens fit.
"""
import argparse, json, os, random, re, shutil, sys, time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.lens import JacobianLens
from workspace_common import BAND, LENS_PATH
from workspace_t3_loading import build_prompt, readout_item

BOXED = re.compile(r"\\boxed\{([^}]*)\}")
NULL_WORDS = ["piano", "glacier", "walnut", "lantern", "harbor", "velvet", "cactus",
              "falcon", "marble", "tunnel", "compass", "anchor"]


def token_forms(tok, word):
    """Single-token ids for ' word' and 'word' (workspace J-lens vocab is token-level)."""
    out = []
    for form in (" " + word, word):
        ids = tok(form, add_special_tokens=False)["input_ids"]
        if len(ids) == 1:
            out.append(ids[0])
    return sorted(set(out))


def workspace_readout(tok, lensmodel, hf, lens, band, effective_q, trace, kernel_words,
                      answer, rng):
    """Kernel vs null loading in the workspace band over the REASONING span only
    (prompt excluded, so hint text in the prompt can't leak). Returns per-label
    best_rank + max_loading, plus the min kernel rank as the headline number."""
    tracked = {}
    for w in kernel_words:
        ids = token_forms(tok, w)
        if ids:
            tracked[f"kernel:{w}"] = ids
    for w in rng.sample(NULL_WORDS, 3):
        ids = token_forms(tok, w)
        if ids:
            tracked[f"null:{w}"] = ids
    ans_ids = token_forms(tok, str(answer))
    if ans_ids:
        tracked["answer"] = ans_ids
    if not tracked:
        return None
    prompt = build_prompt(tok, effective_q)
    start_pos = tok(prompt, return_tensors="pt")["input_ids"].shape[1]
    res = readout_item(tok, lensmodel, hf, lens, band, prompt + trace, tracked,
                       start_pos=start_pos)
    kr = [v["best_rank"] for k, v in res.items()
          if k.startswith("kernel:") and v["best_rank"]]
    nr = [v["best_rank"] for k, v in res.items()
          if k.startswith("null:") and v["best_rank"]]
    res["_kernel_best_rank"] = min(kr) if kr else None
    res["_null_best_rank"] = min(nr) if nr else None
    return res


def norm(s):
    s = s.lower().strip().rstrip(".").replace("$", "").replace(",", "").strip()
    return re.sub(r"\s+", " ", s)


def auto_ok(text, aliases):
    m = BOXED.findall(text)
    cand = m[-1] if m else (text.strip().splitlines()[-1] if text.strip() else "")
    c = norm(cand)
    for a in aliases:
        a = norm(a)
        if c == a or re.search(rf"\b{re.escape(a)}\b", c):
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--k-plain", type=int, default=8)
    ap.add_argument("--k-hint", type=int, default=3)
    ap.add_argument("--temp", type=float, default=0.7)
    ap.add_argument("--max-think", type=int, default=2048)
    ap.add_argument("--min-disk-gb", type=float, default=3.0)
    ap.add_argument("--seed", type=int, default=23)
    ap.add_argument("--no-readout", action="store_true",
                    help="behavioral only; skip the workspace/J-space readout")
    ap.add_argument("--out", default="results/workspace/e0_insight_screen.json")
    ap.add_argument("--status", default="results/workspace/status_e0.json")
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    problems = json.load(open(os.path.join(os.path.dirname(__file__),
                                           "incubation_insight_problems.json")))["problems"]
    rows = []
    if os.path.exists(args.out):
        rows = json.load(open(args.out))["rows"]
    done = {r["id"] for r in rows}

    tok = AutoTokenizer.from_pretrained(args.model)
    hf = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=torch.float16).to(args.device).eval()
    torch.manual_seed(args.seed)
    rng = random.Random(args.seed)

    # workspace readout setup: jlens wrapper shares hf's modules (nothing copied);
    # force_bos=False so generation via the chat template is unchanged.
    lensmodel, lens, band = None, None, None
    if not args.no_readout:
        try:
            lensmodel = jlens.from_hf(hf, tok, force_bos=False)
            if os.path.exists(LENS_PATH):
                lens = JacobianLens.load(LENS_PATH)
                band = [l for l in BAND if l in lens.source_layers]
                lens_kind = f"J-lens n={lens.n_prompts}"
            else:  # identity fallback == logit lens (shown ~equivalent at 4B)
                eye = {l: torch.eye(lensmodel.d_model) for l in BAND}
                lens = JacobianLens(jacobians=eye, n_prompts=0, d_model=lensmodel.d_model)
                band = list(BAND)
                lens_kind = "logit-lens (identity)"
            print(f"[readout] {lens_kind}, band={band}", flush=True)
        except Exception as e:
            print(f"[readout] disabled (setup failed: {e})", flush=True)
            lensmodel = None
    print(f"[load] {args.model}; {len(problems)} problems, {len(done)} done", flush=True)

    def gen(q, greedy):  # q is the effective question (may include an appended hint)
        m = [{"role": "user", "content":
              q + "\nReason step by step, then give the final answer in \\boxed{}."}]
        try:
            e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt",
                                        return_dict=True, enable_thinking=True)
        except TypeError:
            e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt",
                                        return_dict=True)
        enc = e["input_ids"].to(args.device)
        kw = dict(max_new_tokens=args.max_think, pad_token_id=tok.eos_token_id)
        if greedy:
            kw["do_sample"] = False
        else:
            kw.update(do_sample=True, temperature=args.temp, top_p=0.95)
        o = hf.generate(input_ids=enc, attention_mask=torch.ones_like(enc), **kw)
        return tok.decode(o[0].tolist()[enc.shape[1]:], skip_special_tokens=True)

    def arm(q, aliases, k):
        out = {"effective_q": q, "greedy_trace": gen(q, True)}
        out["greedy_ok"] = auto_ok(out["greedy_trace"], aliases)
        out["samples"] = []
        if not out["greedy_ok"]:
            for _ in range(k):
                t = gen(q, False)
                out["samples"].append({"trace": t, "ok": auto_ok(t, aliases)})
        out["n_sample_ok"] = sum(s["ok"] for s in out["samples"])
        return out

    def failing_trace(a):
        return a["greedy_trace"] if not a["greedy_ok"] else None

    def solving_trace(a):
        if a["greedy_ok"]:
            return a["greedy_trace"]
        for s in a["samples"]:
            if s["ok"]:
                return s["trace"]
        return None

    t0 = time.time()
    for i, p in enumerate(problems):
        if p["id"] in done:
            continue
        if shutil.disk_usage("/").free / 2**30 < args.min_disk_gb:
            print("[STOP] disk low. Resumable.", flush=True)
            break
        al = p["gold_aliases"]
        row = {"id": p["id"], "tier": p["tier"], "family": p["family"], "gold": p["gold"]}
        row["plain"] = arm(p["question"], al, args.k_plain)
        row["minimal"] = arm(p["question"] + f"\n\n(Hint: {p['minimal_hint']})", al, args.k_hint)
        row["explicit"] = arm(p["question"] + f"\n\n(Hint: {p['explicit_hint']})", al, args.k_hint)
        pl, mi, ex = row["plain"], row["minimal"], row["explicit"]
        row["stable_fail"] = (not pl["greedy_ok"]) and pl["n_sample_ok"] <= 1
        flip = lambda a: a["greedy_ok"] or a["n_sample_ok"] >= 2
        row["grade"] = ("A" if row["stable_fail"] and flip(mi) else
                        "B" if row["stable_fail"] and flip(ex) else
                        "solved" if pl["greedy_ok"] else "unflippable")

        # workspace readout: kernel-concept loading in the reasoning span (prompt excluded).
        # Key contrast: is the kernel ABSENT from the failing attempt (fixation signature,
        # opposite of F191's boundary errors where the concept was rank ~1)?
        if lensmodel is not None:
            row["workspace"] = {}
            kw = p.get("kernel_tokens", [])
            reads = {"plain_fail": (pl, failing_trace(pl)),
                     "minimal_solve": (mi, solving_trace(mi)),
                     "explicit_solve": (ex, solving_trace(ex))}
            for lab, (a, tr) in reads.items():
                if not tr:
                    continue
                try:
                    row["workspace"][lab] = workspace_readout(
                        tok, lensmodel, hf, lens, band, a["effective_q"], tr, kw,
                        p["gold"], rng)
                except Exception as e:
                    row["workspace"][lab] = {"error": str(e)[:150]}
                    print(f"    readout {lab} failed: {str(e)[:100]}", flush=True)
        rows.append(row)
        json.dump({"rows": rows}, open(args.out, "w"))
        json.dump({"done": len(rows), "total": len(problems),
                   "grades": {g: sum(1 for r in rows if r.get("grade") == g)
                              for g in ("A", "B", "solved", "unflippable")},
                   "elapsed_min": round((time.time() - t0) / 60, 1)},
                  open(args.status, "w"))
        wsr = ""
        if row.get("workspace", {}).get("plain_fail"):
            pf = row["workspace"]["plain_fail"]
            wsr = f" | plain-fail kernel_rank={pf.get('_kernel_best_rank')} null={pf.get('_null_best_rank')}"
        print(f"  [{len(rows)}/{len(problems)}] {p['id']:26} plain_greedy="
              f"{'OK' if pl['greedy_ok'] else 'x'} sampleOK={pl['n_sample_ok']} "
              f"minimal={'OK' if flip(mi) else 'x'} explicit={'OK' if flip(ex) else 'x'} "
              f"-> {row['grade']}{wsr}", flush=True)
        if args.device == "mps":
            torch.mps.empty_cache()

    grades = {g: sum(1 for r in rows if r.get("grade") == g)
              for g in ("A", "B", "solved", "unflippable")}
    print(f"[done] {len(rows)}/{len(problems)} screened; grades: {grades}", flush=True)
    if len(rows) >= len(problems):
        open("results/workspace/SCREEN_DONE", "w").close()  # trigger night-chain lens fit


if __name__ == "__main__":
    main()
