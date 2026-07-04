#!/usr/bin/env python
"""S2 (exp-gated-controller): does the L14 reasoning-decisiveness projection TRACK the reasoning state?
For hand-verified solved traces, project each token's L14 residual onto the commitment direction and
test the generalization: is the projection HIGHER at the model's natural CONCLUDE moments (Therefore /
the answer / boxed) than at its DELIBERATE moments (Wait / but / reconsider)? Plus next-token entropy.
If yes -> an activation gate has a real signal to fire on. Mac/4B, fast (forward passes only).
"""
import argparse, json, os, re
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

DELIB = re.compile(r"\b(wait|hmm|alternatively|reconsider|actually|but|let me (re|check|verify|double))", re.I)
CONCL = re.compile(r"\b(therefore|thus|hence|so the answer|final answer|the answer is|in conclusion|boxed)", re.I)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--layer", type=int, default=14)
    ap.add_argument("--axes", default="results/legibility/axes_4b.npy")
    ap.add_argument("--traces", default="results/legibility/reasoning_4b_overnight.json")
    ap.add_argument("--rescored", default="results/legibility/reasoning_4b_rescored.json")
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--out", default="results/legibility/s2_trajectory.json")
    args = ap.parse_args()
    L = args.layer

    axes = np.load(args.axes, allow_pickle=True).item()
    v = np.asarray(axes[f"commitment_{L}"], dtype="float32"); v = v/np.linalg.norm(v)
    rows = json.load(open(args.traces))["rows"]
    true_ok = {r["idx"]: r["true_ok"] for r in json.load(open(args.rescored))}
    # pick solved traces with distinctive numeric answers
    pick = [i for i in (6, 7, 10, 30, 23) if true_ok.get(i)][:args.n]

    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float16).to(args.device).eval()
    print(f"[load] {args.model}; projecting L{L} onto reasoning-decisiveness; traces {pick}", flush=True)

    def chat_ids(q):
        m = [{"role": "user", "content": q + "\nReason step by step, then give the final answer in \\boxed{}."}]
        try: e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True, enable_thinking=True)
        except TypeError: e = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        return e["input_ids"]

    out = []
    for idx in pick:
        r = rows[idx]; tr = r["greedy_trace"]
        base = chat_ids(r["question"]); cont = tok(tr, add_special_tokens=False, return_tensors="pt")["input_ids"]
        ids = torch.cat([base, cont], 1).to(args.device); p0 = base.shape[1]
        with torch.no_grad():
            o = model(input_ids=ids, output_hidden_states=True)
        H = o.hidden_states[L+1][0].float().cpu().numpy()          # [T, d]
        proj = H @ v                                               # [T]
        ent = []                                                   # chunked to avoid MPS OOM on [T, vocab]
        for i in range(0, o.logits.shape[1], 128):
            lg = o.logits[0, i:i+128].float()
            lp = torch.log_softmax(lg, -1)
            ent.append((-(lp.exp() * lp).sum(-1)).cpu().numpy())
            if args.device == "mps": torch.mps.empty_cache()
        ent = np.concatenate(ent)
        toks = [tok.decode([int(t)]) for t in ids[0].tolist()]
        # classify positions in the trace region (after prompt)
        dz = np.array([bool(DELIB.search(toks[t])) for t in range(len(toks))])
        cz = np.array([bool(CONCL.search(toks[t])) for t in range(len(toks))])
        reg = np.arange(len(toks)) >= p0
        pz = proj  # z-score within trace for readability
        z = (pz - pz[reg].mean()) / (pz[reg].std() + 1e-6)
        d_mean = z[reg & dz].mean() if (reg & dz).any() else np.nan
        c_mean = z[reg & cz].mean() if (reg & cz).any() else np.nan
        # binned arc over the trace (10 bins)
        tr_idx = np.where(reg)[0]
        bins = np.array_split(tr_idx, 10)
        arc = [(float(z[b].mean()), float(ent[b].mean())) for b in bins if len(b)]
        out.append(dict(idx=idx, gold=str(r["gold"]), n_delib=int((reg&dz).sum()), n_concl=int((reg&cz).sum()),
                        delib_proj_z=float(d_mean), concl_proj_z=float(c_mean), arc=arc))
        print(f"\n#{idx} gold={r['gold']}  (n_delib={int((reg&dz).sum())} n_concl={int((reg&cz).sum())})")
        print(f"  proj-z at DELIBERATE moments: {d_mean:+.2f}  |  at CONCLUDE moments: {c_mean:+.2f}  "
              f"-> {'TRACKS (concl>delib)' if c_mean>d_mean else 'does NOT track'}")
        print("  arc (10 bins, proj-z / entropy): " + " ".join(f"{p:+.1f}/{e:.1f}" for p,e in arc))
        if args.device == "mps": torch.mps.empty_cache()

    # aggregate verdict
    dd = np.nanmean([x["delib_proj_z"] for x in out]); cc = np.nanmean([x["concl_proj_z"] for x in out])
    json.dump(out, open(args.out, "w"), indent=1)
    print(f"\n=== S2 VERDICT (n={len(out)}) ===")
    print(f"  mean proj-z: deliberate {dd:+.2f}  vs  conclude {cc:+.2f}  (gap {cc-dd:+.2f})")
    print(f"  -> {'SIGNAL EXISTS: direction distinguishes the model own deliberate vs conclude moments -> gate viable' if cc>dd+0.2 else 'WEAK/NO signal -> fix vector before gating'}")
    print("[done] ->", args.out)

if __name__ == "__main__":
    main()
