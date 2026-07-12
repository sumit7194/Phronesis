#!/usr/bin/env python
"""E21 (Task 3, #2) — TruthfulQA honesty probe on a hallucination-RICH source. Per question, MC1:
does the model prefer the Best Correct answer over the Best Incorrect (compelling myth)? Capture
hidden states at the answer position; train a probe to predict per-question whether the model will
be truthful vs fall for the myth. Deterministic (logprob), resilient (checkpoint/resume).
"""
import json, os, shutil, sys, time, csv
import numpy as np, torch
sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); WS=os.path.join(ROOT,"mvp/results/workspace")
LS=[20,26,30,33]; CAP=os.path.join(WS,"e21_capture.npz"); META=os.path.join(WS,"e21_meta.json")
OUT=os.path.join(WS,"e21_summary.json"); STAT=os.path.join(WS,"status_e21.json")
NMAX=600
def ans_logprob(tok,hf,base_ids,ans):
    aids=tok(" "+ans,add_special_tokens=False)["input_ids"][:24]
    seq=base_ids+aids
    with torch.no_grad(): lg=hf(torch.tensor([seq],device=DEVICE)).logits[0].float()
    tot=0.0
    for j,t in enumerate(aids):
        tot+=torch.log_softmax(lg[len(base_ids)+j-1],-1)[t].item()
    return tot/max(len(aids),1)
def main():
    rows=list(csv.DictReader(open(os.path.join(ROOT,"corpus/external/truthfulqa/TruthfulQA.csv"))))[:NMAX]
    meta=json.load(open(META)) if os.path.exists(META) else []
    done={m["q"] for m in meta}; hs={L:[] for L in LS}
    if os.path.exists(CAP):
        z=np.load(CAP); hs={L:list(z[f"L{L}"]) for L in LS}
    tok,hf,_=load_model()
    print(f"[e21] {len(rows)} TruthfulQA Qs, {len(done)} done",flush=True)
    for i,r in enumerate(rows):
        q=r["Question"]
        if q in done: continue
        if shutil.disk_usage("/").free/1e9<3: print("[STOP] disk"); break
        best=r["Best Answer"].strip(); binc=(r["Best Incorrect Answer"] or (r["Incorrect Answers"].split(";")[0])).strip()
        pre=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
        base=tok(pre,add_special_tokens=False)["input_ids"]
        with torch.no_grad():
            out=hf(torch.tensor([base],device=DEVICE),output_hidden_states=True)
        for L in LS: hs[L].append(out.hidden_states[L][0,-1].float().cpu().numpy())
        lp_c=ans_logprob(tok,hf,base,best); lp_i=ans_logprob(tok,hf,base,binc)
        truthful = 1 if lp_c>lp_i else 0
        meta.append({"q":q,"cat":r["Category"],"truthful":truthful,"margin":round(lp_c-lp_i,3)})
        done.add(q)
        if len(meta)%25==0 or i==len(rows)-1:
            np.savez(CAP,**{f"L{L}":np.array(hs[L]) for L in LS}); json.dump(meta,open(META,"w"))
            json.dump({"done":len(meta),"total":len(rows),"truthful":sum(m["truthful"] for m in meta),"free_gb":round(shutil.disk_usage('/').free/1e9,1),"ts":time.strftime("%H:%M:%S")},open(STAT,"w"))
            print(f"  {len(meta)}/{len(rows)} truthful={sum(m['truthful'] for m in meta)}",flush=True)
        if DEVICE=="mps": torch.mps.empty_cache()
    np.savez(CAP,**{f"L{L}":np.array(hs[L]) for L in LS}); json.dump(meta,open(META,"w"))
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score, StratifiedKFold
    y=np.array([m["truthful"] for m in meta]); z=np.load(CAP)
    summ={"n":len(meta),"mc1_accuracy":round(float(y.mean()),3),"n_truthful":int(y.sum()),"n_myth":int((1-y).sum())}
    print(f"\n[e21] n={len(meta)} MC1 truthful-rate={y.mean():.3f} (truthful={int(y.sum())} myth={int((1-y).sum())})")
    if 8<=y.sum()<=len(y)-8:
        summ["probe_auroc"]={}
        for L in LS:
            X=np.array(z[f"L{L}"]); X=X/(np.linalg.norm(X,axis=1,keepdims=True)+1e-9)
            au=cross_val_score(LogisticRegression(max_iter=2000),X,y,cv=StratifiedKFold(5,shuffle=True,random_state=0),scoring="roc_auc")
            summ["probe_auroc"][L]=round(float(au.mean()),3); print(f"   L{L}: truthfulness-probe AUROC={au.mean():.3f}")
        summ["best_layer"]=max(summ["probe_auroc"],key=summ["probe_auroc"].get)
    else: summ["probe_auroc"]="SKIPPED (need both classes)"
    json.dump(summ,open(OUT,"w"),indent=1)
    open(os.path.join(WS,"E21_DONE"),"w").write("done"); print("[done] -> "+OUT)
main()
