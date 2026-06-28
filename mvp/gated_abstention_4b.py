#!/usr/bin/env python
"""Path B v1 — read-then-act gated abstention on Qwen3-4B. Prereg: docs/prereg-gated-abstention.md.

READ the model's confidence (F172 signals) per item, ACT = abstain when low. Pure analysis of
existing signals + hand-scored GT (no model run). Establishes the calibration capability of
gating, and compares its selectivity to F173's uniform-steering push (78% confab / 29% known).
"""
import json, numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

d=json.load(open("results/legibility/knowledge_edge_4b.json"))["rows"]
gt=np.array([1 if r["hand_no_ok"] else 0 for r in d])          # 1 = correct (hand-scored)
N=len(d); base=gt.mean()
# confidence signals, oriented so higher = more confident
SIG={"P(True)":np.array([r["p_true"] for r in d]),
     "seq_logprob":np.array([r["seq_logprob"] for r in d]),
     "-mean_entropy":-np.array([r["mean_entropy"] for r in d]),
     "-semantic_ent":-np.array([r["semantic_entropy"] for r in d])}
print(f"n={N} | baseline accuracy (answer all) = {base:.1%}\n")
print("=== AUROC per signal vs GT ===")
for k,s in SIG.items(): print(f"  {k:14s}: {roc_auc_score(gt,s):.3f}")

# combined signal: leave-one-out logistic (no leakage)
X=np.column_stack(list(SIG.values())); Xs=StandardScaler().fit_transform(X)
loo=np.zeros(N)
for tr,te in LeaveOneOut().split(Xs):
    loo[te]=LogisticRegression(max_iter=1000).fit(Xs[tr],gt[tr]).predict_proba(Xs[te])[0,1]
print(f"  {'COMBINED(LOO)':14s}: {roc_auc_score(gt,loo):.3f}")

def risk_coverage(conf, label):
    order=np.argsort(-conf)                                    # most-confident first
    print(f"\n=== risk-coverage ({label}) — answer top-c by confidence ===")
    print(f"  {'coverage':>8} | {'selective acc':>13} | {'(answered/correct)':>18}")
    for c in [1.0,0.7,0.5,0.3,0.2,0.1]:
        k=max(1,int(N*c)); sel=order[:k]; acc=gt[sel].mean()
        print(f"  {c:>7.0%} | {acc:>12.1%} | {gt[sel].sum():>7d}/{k}")
best=max(SIG, key=lambda k: roc_auc_score(gt,SIG[k]))
risk_coverage(SIG[best], f"best single = {best}")
risk_coverage(loo, "COMBINED(LOO)")

# four-cell outcome at an operating point: gate on COMBINED, abstain on the bottom-X
print("\n=== gated four-cell outcome (gate=COMBINED-LOO) ===")
for thr_q in [0.5, 0.6, 0.7]:
    thr=np.quantile(loo, thr_q)                               # abstain on bottom thr_q fraction
    answer = loo>=thr
    ac=int(((answer)&(gt==1)).sum()); aw=int(((answer)&(gt==0)).sum())
    rc=int(((~answer)&(gt==1)).sum()); rw=int(((~answer)&(gt==0)).sum())
    cov=answer.mean(); sel_acc=gt[answer].mean() if answer.any() else 0
    # calibration accuracy = right call on each item (answered&correct OR abstained&wrong)
    calib=(ac+rw)/N
    print(f"  abstain bottom {thr_q:.0%}: coverage={cov:.0%} sel-acc={sel_acc:.0%} | "
          f"answered-correct={ac} answered-WRONG={aw} | abstained-WRONG(caught)={rw} abstained-correct(servility)={rc} "
          f"| calibration-acc={calib:.0%} (vs baseline {base:.0%})")

# F173 comparison: gated abstention on the SAME held-out items (confab vs known)
seed=json.load(open("results/legibility/calibration_seed_4b.json"))
def split(L,frac=0.69): k=int(len(L)*frac); return L[k:]
h_eval={x["q"] for x in split(seed["hedge_targets"])}         # held-out confab (GT-wrong)
c_eval={x["q"] for x in split(seed["commit_targets"])}        # held-out known (GT-correct)
loo_by_q={r["q"]:loo[i] for i,r in enumerate(d)}
print("\n=== Path B vs F173 (uniform steering) on the SAME held-out items ===")
print("  F173 uniform v_hedge @best alpha: confab hedged 78% | known hedged 29%  (gap 49pp)")
# choose threshold s.t. ~78% of confab are below it (abstained), then read knowns
ch=sorted([loo_by_q[q] for q in h_eval if q in loo_by_q])     # confab confidences, ascending
thr=ch[min(len(ch)-1, int(len(ch)*0.78))] if ch else 0.5      # 78th pct of confab -> ~78% below it
ab_c=np.mean([loo_by_q[q]<thr for q in h_eval if q in loo_by_q])
ab_k=np.mean([loo_by_q[q]<thr for q in c_eval if q in loo_by_q])
print(f"  Path B gated abstention (threshold matched to ~78% confab): confab abstained {ab_c:.0%} | known abstained {ab_k:.0%}  (gap {ab_c-ab_k:+.0%})")

json.dump({"base":float(base),"auroc":{k:float(roc_auc_score(gt,s)) for k,s in SIG.items()},
           "auroc_combined":float(roc_auc_score(gt,loo)),
           "f173":{"confab":0.78,"known":0.29},
           "pathB":{"confab_abstain":float(ab_c),"known_abstain":float(ab_k)}},
          open("results/legibility/gated_abstention_4b.json","w"), indent=1)
print("\n-> results/legibility/gated_abstention_4b.json")
