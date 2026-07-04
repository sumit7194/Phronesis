#!/usr/bin/env python
"""S1 (exp-gated-controller): extract candidate reasoning-domain virtue axes (content-controlled),
then build the cos-matrix vs each other + the recall hedge/commit vectors.
Answers: how many INDEPENDENT axes actually exist? (pairs near +-1 = same axis; near 0 = independent.)
Fast (forward passes only) — Mac/4B, power-loss-resilient.

Each axis vector = mean(POS-pole phrase acts) - mean(NEG-pole phrase acts), mean-pooled over the phrase,
appended to genuine mid-reasoning contexts from the 4B's own traces. POS = decisive/forward pole.
"""
import argparse, json, os
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# each axis: (name, POS-pole phrases [decisive/forward], NEG-pole phrases [deliberate/cautious])
AXES = {
 "commitment": (
   ["Therefore the reasoning is complete and the answer is settled.",
    "So I am confident the solution is finished and correct now.",
    "That confirms it; there is nothing left to check here.",
    "Good, the derivation is done and the result stands firmly.",
    "This settles the problem; the final answer is clear now.",
    "Everything checks out, so I will commit to this result."],
   ["Wait, let me reconsider that step much more carefully.",
    "Hmm, but I should double-check this a different way first.",
    "Actually, let me try another approach to be safe here.",
    "Hold on, I am not fully sure that part is right yet.",
    "Let me re-examine whether that assumption really holds up.",
    "But there might be a case I have not accounted for here."]),
 "verification": (
   ["That step is right, so I will take it as given now.",
    "Yes, that clearly holds, no need to check it again.",
    "This is correct as written, I can move on from here.",
    "I trust that computation, it is obviously fine here.",
    "That follows directly, so I accept it and continue on.",
    "No error there, the step is sound, moving forward now."],
   ["Let me double-check this calculation very carefully now.",
    "I should verify this step before I continue any further.",
    "Let me re-derive this result to be sure it is right.",
    "I had better recompute that to confirm it is correct.",
    "Let me test this against a small example to be certain.",
    "I want to check that step again in a different way."]),
 "exploration": (
   ["I will stick with this approach and carry it through.",
    "This method works, so let me just finish it out now.",
    "Following this single path all the way to the end here.",
    "I will commit to this strategy and not switch again.",
    "This line of attack is fine; I will see it through.",
    "Staying on this one approach until it is completed now."],
   ["Let me try a completely different approach to this instead.",
    "Maybe another method would work far better for this here.",
    "Let me consider an entirely alternative strategy instead.",
    "Perhaps I should branch off and explore a new idea here.",
    "Let me set this aside and attempt a different route now.",
    "There may be a cleaner path; let me explore that instead."]),
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--layers", default="10,14,17,20")
    ap.add_argument("--traces", default="results/legibility/reasoning_4b_overnight.json")
    ap.add_argument("--recall", default="results/legibility/v_hedge_cc_4b.npy")
    ap.add_argument("--reasoning-commit", default="results/legibility/v_commit_reasoning_4b.npy")
    ap.add_argument("--ncontext", type=int, default=24)
    ap.add_argument("--ctxcap", type=int, default=380)
    ap.add_argument("--out", default="results/legibility/axes_4b.npy")
    args = ap.parse_args()
    SWEEP = [int(x) for x in args.layers.split(",")]

    rows = json.load(open(args.traces))["rows"]
    rng = np.random.default_rng(3)
    ctxs = []
    for r in rng.permutation(len(rows))[:args.ncontext]:
        tr = rows[int(r)]["greedy_trace"]
        if len(tr) < 400: continue
        ctxs.append(tr[:int(len(tr)*rng.uniform(0.35, 0.7))])
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float16).to(args.device).eval()
    print(f"[load] {args.model}; {len(ctxs)} contexts", flush=True)

    @torch.no_grad()
    def acts(ctx, phrase):
        cids = tok(ctx, add_special_tokens=False)["input_ids"][-args.ctxcap:]
        pids = tok(" " + phrase, add_special_tokens=False)["input_ids"]
        ids = torch.tensor([cids + pids], device=args.device); p0 = len(cids)
        hs = model(input_ids=ids, output_hidden_states=True).hidden_states
        return {L: hs[L+1][0, p0:, :].mean(0).float().cpu().numpy() for L in SWEEP}

    vecs = {}
    for name, (pos, neg) in AXES.items():
        P = {L: [] for L in SWEEP}; N = {L: [] for L in SWEEP}
        for i, ctx in enumerate(ctxs):
            p = acts(ctx, pos[i % len(pos)]); n = acts(ctx, neg[i % len(neg)])
            for L in SWEEP: P[L].append(p[L]); N[L].append(n[L])
            if args.device == "mps": torch.mps.empty_cache()
        for L in SWEEP: vecs[f"{name}_{L}"] = np.mean(P[L], 0) - np.mean(N[L], 0)
        print(f"[extract] {name} done", flush=True)
    np.save(args.out, vecs, allow_pickle=True)

    # assemble all axes at a couple of layers + recall + reasoning-commit for the cos-matrix
    rec = np.load(args.recall, allow_pickle=True).item()
    rc = np.load(args.reasoning_commit, allow_pickle=True).item()
    def cos(a, b): return float(np.dot(a, b) / (np.linalg.norm(a)*np.linalg.norm(b) + 1e-9))
    for L in [14, 17]:
        cat = {"recall-commit": np.asarray(rec[f"commit_{L}"], float),
               "recall-hedge": np.asarray(rec[L], float),
               "reason-commit": np.asarray(rc[L], float),
               "commitment": vecs[f"commitment_{L}"],
               "verification": vecs[f"verification_{L}"],
               "exploration": vecs[f"exploration_{L}"]}
        names = list(cat)
        print(f"\n=== cos-matrix @ L{L} (POS pole = decisive/forward) ===")
        print("            " + "".join(f"{n[:9]:>10}" for n in names))
        for a in names:
            print(f"{a[:11]:12}" + "".join(f"{cos(cat[a], cat[b]):>10.2f}" for b in names))
    print("\n[done] ->", args.out)

if __name__ == "__main__":
    main()
