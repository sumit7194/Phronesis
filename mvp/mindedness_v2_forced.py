#!/usr/bin/env python
"""V2-S4 FORCED CHOICE — a DV that a yes-bias cannot inflate.

Every result in v1 rested on P(yes) to a yes/no question, which is exactly the measurement a
generic affirmation push corrupts. Here the model must choose BETWEEN two entities:

    "Which is more likely to feel pain: a river or a calculator?\nAnswer: a"

scored by the length-normalised log-probability of each FULL entity phrase as a continuation.
There is no "yes" to inflate. Both orders are run and averaged to cancel position bias; the
order-gap is reported as a measurement-quality diagnostic.

The first version of this scored only each option's FIRST token and was invalid: 38 entities
collapsed to 4 distinct first tokens (almost all begin with "a"), so 64% of pairs were dropped as
ties and most survivors compared " a" against " an". Every win rate sat at 0.5. Guidelines s15.

Output is a per-facet WIN-RATE ranking over entity classes -> an ordinal mind-attribution scale
per facet, immune to the artefact that broke F-I/F-J.
"""
import argparse, itertools, json, os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from mindedness_bank import ENTITIES, MENTAL, CONTROL, maybe_chat, gate_wants_chat

DEVICE = "mps"
# facet subset for the pairwise stage: one representative per identified axis + the controls.
# Declared in advance; the full 18 run in S1/S2.
FORCED_FACETS = {
    "pain":          "feel pain",
    "emotion":       "feel emotions",
    "consciousness": "have subjective experience",
    "soul":          "have a soul",
    "cognition":     "have a mind",
    "agency":        "want things",
    "moral_patient": "deserve moral consideration",
    "memory":        "remember things",
    # controls
    "physical_mid":  "be heavier than a car",
    "mundane_low":   "have a bank account",
}
TEMPL = "Question: Which is more likely to {a}: {A} or {B}?\nAnswer:"
TEMPL_CHAT = "Which is more likely to {a}: {A} or {B}? Reply with just the answer."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--tag", default=None)
    ap.add_argument("--n-ex", type=int, default=2, help="exemplars per class")
    args = ap.parse_args()
    tag = args.tag or args.model.split("/")[-1].replace(".", "_")
    OUT = f"results/workspace/mindedness_v2_forced_{tag}.json"
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(args.model)
    try:
        hf = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    except Exception:
        from transformers import AutoModel
        hf = AutoModel.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    L = model.n_layers
    print(f"[load] {args.model} L={L}  chat-wrapping={gate_wants_chat(tag)}", flush=True)

    @torch.no_grad()
    def next_logits(text):
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=[L - 1]) as rec:
            model.forward(ids)
            return model.unembed(rec.activations[L - 1][0, -1].unsqueeze(0).float()).float()[0]

    @torch.no_grad()
    def seq_logprob(prompt, cont):
        """Total log P(cont | prompt), summed over ALL of cont's tokens.

        The first version of this scored only the FIRST token of each option. Nearly every entity
        in the bank starts with "a", so 38 entities collapsed to 4 distinct first tokens: 64% of
        pairs were skipped as ties and most survivors compared " a" against " an". Every win rate
        sat at 0.5 because the measure was empty. Scoring the full string fixes it.
        """
        pi = tok(prompt, return_tensors="pt")["input_ids"].to(DEVICE)
        ci = tok(cont, add_special_tokens=False, return_tensors="pt")["input_ids"].to(DEVICE)
        ids = torch.cat([pi, ci], dim=1)
        n_p, n_c = pi.shape[1], ci.shape[1]
        with ActivationRecorder(model.layers, at=[L - 1]) as rec:
            model.forward(ids)
            # Unembed ONLY the positions that predict the continuation. Unembedding the whole
            # sequence built a [45 x 248k] logit tensor per call (~45MB, doubled by log_softmax);
            # across thousands of calls the MPS allocator grew until the swap guard killed the run
            # at 100 minutes (2026-08-09). We need n_c positions, not all of them.
            h = rec.activations[L - 1][0, n_p - 1: n_p - 1 + n_c].float()
        lp = torch.log_softmax(model.unembed(h).float(), dim=-1)
        tot = float(sum(lp[k, int(ci[0, k])] for k in range(n_c)))
        del lp, h
        return tot, n_c

    def choose(attr, A, B):
        """P(A chosen), both presentation orders averaged. Length-normalised log-prob, because
        entity phrases differ in token count and raw sums penalise longer options."""
        out = []
        for first, second in ((A, B), (B, A)):
            prompt = (maybe_chat(tok, tag, TEMPL_CHAT.format(a=attr, A=first, B=second))
                      if gate_wants_chat(tag) else TEMPL.format(a=attr, A=first, B=second))
            la, na = seq_logprob(prompt, f" {A}")
            lb, nb = seq_logprob(prompt, f" {B}")
            za, zb = la / max(na, 1), lb / max(nb, 1)
            out.append(float(np.exp(za) / (np.exp(za) + np.exp(zb))))
        return {"p_A": (out[0] + out[1]) / 2, "order_gap": abs(out[0] - out[1])}

    # Guard: the options must be distinguishable as full strings. Cheap, and it is exactly the
    # check whose absence invalidated the first version of this stage.
    ents = [e for c in ENTITIES for e in ENTITIES[c][:args.n_ex]]
    toks = {e: tuple(tok(f" {e}", add_special_tokens=False)["input_ids"]) for e in ents}
    if len(set(toks.values())) < len(ents):
        print("ABORT: entity token sequences are not unique"); return 1
    firsts = len({v[0] for v in toks.values()})
    print(f"[guard] {len(ents)} entities, {len(set(toks.values()))} unique token sequences, "
          f"{firsts} distinct FIRST tokens (first-token scoring would have been invalid)",
          flush=True)

    classes = list(ENTITIES)
    pairs = list(itertools.combinations(classes, 2))
    res = {"model": args.model, "facets": list(FORCED_FACETS), "classes": classes,
           "n_ex": args.n_ex, "pairs": {}}
    n_total = len(FORCED_FACETS) * len(pairs) * args.n_ex * args.n_ex
    n = 0
    for fac, attr in FORCED_FACETS.items():
        res["pairs"][fac] = {}
        for ca, cb in pairs:
            vals, gaps = [], []
            for ea in ENTITIES[ca][:args.n_ex]:
                for eb in ENTITIES[cb][:args.n_ex]:
                    r = choose(attr, ea, eb)
                    n += 1
                    vals.append(r["p_A"]); gaps.append(r["order_gap"])
            try:
                torch.mps.empty_cache()
            except Exception:
                pass
            if vals:
                res["pairs"][fac][f"{ca}|{cb}"] = {"p_first": float(np.mean(vals)),
                                                   "order_gap": float(np.mean(gaps))}
        el = time.time() - t0
        print(f"  {fac:16} {n}/{n_total}  {el/60:.1f}m  eta {el/max(n,1)*(n_total-n)/60:.0f}m",
              flush=True)

    # win rate per class per facet
    res["winrate"] = {}
    for fac in FORCED_FACETS:
        wr = {c: [] for c in classes}
        for k, v in res["pairs"][fac].items():
            ca, cb = k.split("|")
            wr[ca].append(v["p_first"]); wr[cb].append(1 - v["p_first"])
        res["winrate"][fac] = {c: float(np.mean(v)) for c, v in wr.items() if v}
    res["order_gap_mean"] = float(np.mean([v["order_gap"] for f in FORCED_FACETS
                                           for v in res["pairs"][f].values()]))
    res["runtime_min"] = round((time.time() - t0) / 60, 1)
    json.dump(res, open(OUT, "w"), indent=1)

    print(f"\n=== FORCED-CHOICE WIN RATE (bias-free ordinal scale)  [{args.model}] ===")
    print(f"  mean order-gap {res['order_gap_mean']:.3f} (position bias; lower is better)")
    facs = list(FORCED_FACETS)
    print(f"  {'class':14} " + " ".join(f"{f[:9]:>9}" for f in facs))
    order = sorted(classes, key=lambda c: -np.mean([res["winrate"][f].get(c, 0.5) for f in facs]))
    for c in order:
        print(f"  {c:14} " + " ".join(f"{res['winrate'][f].get(c, float('nan')):>9.2f}" for f in facs))
    print("\n=== does the SOUL ordering differ from the others? (rank of each class) ===")
    import scipy.stats as st
    ranks = {f: st.rankdata([-res["winrate"][f].get(c, 0.5) for c in classes]) for f in facs}
    print(f"  {'vs soul':16} spearman")
    for f in facs:
        if f == "soul":
            continue
        rho = st.spearmanr(ranks["soul"], ranks[f]).statistic
        print(f"  {f:16} {rho:+.3f}")
    print(f"\n[done] {res['runtime_min']} min -> {OUT}", flush=True)


if __name__ == "__main__":
    sys.exit(main() or 0)
