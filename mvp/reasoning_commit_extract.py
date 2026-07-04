#!/usr/bin/env python
"""Extract a REASONING-NATIVE commit vector (F183 redesign, F179-disciplined).
Contrast, at genuine mid-reasoning states from the 4B's own traces:
  DELIBERATE (keep thinking / doubt)  vs  COMMIT (conclude / decide).
Content-controlled: entity-free, length-matched, diverse phrasings, mean-pooled over the appended
phrase (not the last token) so the direction is stance, not lexical/positional.

Also: logit-lens the vector (what tokens does it promote?) and cos vs the OLD recall commit vector
(v_hedge_cc_4b commit_L) — do reasoning-commit and recall-commit share an axis? Fast (forward passes only).
"""
import argparse, json, os, sys, re
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

DELIBERATE = [
    "Wait, let me reconsider that step more carefully.",
    "Hmm, but I should double-check this a different way.",
    "Actually, let me try another approach instead here.",
    "Hold on, I'm not fully sure that part is right.",
    "Let me re-examine whether that assumption really holds.",
    "But there might be a case I haven't accounted for.",
]
COMMIT = [
    "Therefore, the reasoning is complete and the answer is settled.",
    "So I am confident the solution is finished and correct.",
    "That confirms it; there is nothing left to check now.",
    "Good, the derivation is done and the result stands firmly.",
    "This settles the problem; the final answer is clear now.",
    "Everything checks out, so I will commit to this result.",
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--layers", default="10,14,17,20")
    ap.add_argument("--traces", default="results/legibility/reasoning_4b_overnight.json")
    ap.add_argument("--recall-vec", default="results/legibility/v_hedge_cc_4b.npy")
    ap.add_argument("--ncontext", type=int, default=30)
    ap.add_argument("--ctxcap", type=int, default=400)   # cap prefix tokens (speed/mem)
    ap.add_argument("--out", default="results/legibility/v_commit_reasoning_4b.npy")
    args = ap.parse_args()
    SWEEP = [int(x) for x in args.layers.split(",")]

    rows = json.load(open(args.traces))["rows"]
    rng = np.random.default_rng(7)
    # genuine mid-reasoning contexts: prefix of a real trace, cut at a random mid-point
    ctxs = []
    for r in rng.permutation(len(rows))[:args.ncontext]:
        tr = rows[int(r)]["greedy_trace"]
        if len(tr) < 400: continue
        cut = int(len(tr) * rng.uniform(0.35, 0.75))
        ctxs.append(tr[:cut])
    print(f"[data] {len(ctxs)} mid-reasoning contexts", flush=True)

    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float16).to(args.device).eval()
    print(f"[load] {args.model}", flush=True)

    @torch.no_grad()
    def acts(context, phrase):
        cids = tok(context, add_special_tokens=False)["input_ids"][-args.ctxcap:]
        pids = tok(" " + phrase, add_special_tokens=False)["input_ids"]
        ids = torch.tensor([cids + pids], device=args.device)
        p0 = len(cids)
        hs = model(input_ids=ids, output_hidden_states=True).hidden_states
        return {L: hs[L+1][0, p0:, :].mean(0).float().cpu().numpy() for L in SWEEP}  # mean-pool the phrase

    D = {L: [] for L in SWEEP}; C = {L: [] for L in SWEEP}
    for i, ctx in enumerate(ctxs):
        d = acts(ctx, DELIBERATE[i % len(DELIBERATE)])
        c = acts(ctx, COMMIT[i % len(COMMIT)])
        for L in SWEEP: D[L].append(d[L]); C[L].append(c[L])
        if args.device == "mps": torch.mps.empty_cache()
        if (i+1) % 10 == 0: print(f"  {i+1}/{len(ctxs)}", flush=True)

    vec = {L: (np.mean(C[L], 0) - np.mean(D[L], 0)) for L in SWEEP}   # commit - deliberate
    np.save(args.out, vec, allow_pickle=True)
    print(f"[save] {args.out}", flush=True)

    # --- interpretability: logit-lens (what does the commit direction promote?) ---
    WU = model.get_output_embeddings().weight.detach().float().cpu().numpy()   # [vocab, d]
    print("\n=== logit-lens of v_commit_reasoning (top promoted tokens per layer) ===")
    for L in SWEEP:
        v = vec[L] / (np.linalg.norm(vec[L]) + 1e-8)
        logits = WU @ v
        top = np.argsort(-logits)[:12]
        toks = [tok.decode([int(t)]).strip() for t in top]
        print(f"  L{L}: " + " ".join(repr(t) for t in toks if t))

    # --- cross-check vs recall-domain commit vector ---
    if os.path.exists(args.recall_vec):
        rv = np.load(args.recall_vec, allow_pickle=True).item()
        print("\n=== cos(reasoning-commit, recall-commit) per layer — do they share an axis? ===")
        for L in SWEEP:
            k = f"commit_{L}"
            if k in rv:
                a, b = vec[L], np.asarray(rv[k], dtype="float32")
                cos = float(np.dot(a, b) / (np.linalg.norm(a)*np.linalg.norm(b) + 1e-9))
                print(f"  L{L}: cos = {cos:+.3f}")
    print("\n[done]")

if __name__ == "__main__":
    main()
