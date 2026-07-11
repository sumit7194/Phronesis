#!/usr/bin/env python
"""E12 — formality α-sweep to disambiguate weak-steer (α too low?) from genuine legibility≠
steerability. Steer ±α at {0.2,0.4,0.6}·‖h‖; count the DECODE-PREDICTED markers (formal:
Furthermore/Indeed/... ; casual: yeah/basically/...) + contractions. If markers appear at higher α,
it was α; if flat throughout, genuine weak-steer.
"""
import json, os, re, sys
import numpy as np, torch
sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L=20; v=np.load(os.path.join(ROOT,"mvp/results/workspace/v_formality_L20.npy")); MN=66.44
PROMPTS=["Explain why cats purr.","Tell me how to make a paper airplane.","Share a fun fact about octopuses.","How do I make friends as an adult?","Explain what a black hole is.","Why do we yawn?","How does a microwave heat food?","What makes a good cup of tea?"]
FORMAL=re.compile(r"\b(Furthermore|Moreover|Therefore|Indeed|Nevertheless|Consequently|Thus|Hence|Additionally|Nonetheless|Accordingly|whom|shall|Herein|aforementioned)\b")
CASUAL=re.compile(r"\b(yeah|gonna|kinda|sorta|stuff|basically|honestly|totally|cool|guys?|ya|dude|awesome|okay)\b",re.I)
CONTR=re.compile(r"\b\w+('re|'ll|'ve|n't)\b|\b(I'm|it's|that's|you're|don't|can't|let's)\b",re.I)
def counts(t):
    n=max(len(t.split()),1); return len(FORMAL.findall(t)), len(CASUAL.findall(t)), len(CONTR.findall(t)), n
def gen(tok,hf,q,alpha):
    prompt=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
    ids=tok(prompt,add_special_tokens=False,return_tensors="pt").to(DEVICE); h=None
    if alpha!=0:
        vv=torch.tensor(v/np.linalg.norm(v),dtype=torch.float16,device=DEVICE)
        h=hf.model.layers[L].register_forward_hook(lambda m,i,o:((o[0]+alpha*vv,)+o[1:]) if isinstance(o,tuple) else o+alpha*vv)
    with torch.no_grad(): out=hf.generate(**ids,max_new_tokens=90,do_sample=False,pad_token_id=tok.eos_token_id)
    if h:h.remove()
    t=tok.decode(out[0,ids["input_ids"].shape[1]:],skip_special_tokens=True)
    if DEVICE=="mps":torch.mps.empty_cache()
    return t
def main():
    tok,hf,_=load_model()
    fracs=[-0.6,-0.4,-0.2,0.0,0.2,0.4,0.6]
    agg={f:{"F":0,"C":0,"K":0,"N":0,"txt":[]} for f in fracs}
    for qi,q in enumerate(PROMPTS):
        for f in fracs:
            t=gen(tok,hf,q,round(f*MN,2)); F,C,K,n=counts(t)
            a=agg[f]; a["F"]+=F; a["C"]+=C; a["K"]+=K; a["N"]+=n
            if qi<2: a["txt"].append(t[:110])
        print(f"[{qi+1}/8] done",flush=True)
    print("\n=== formality α-sweep: decode-marker counts (totals over 8 prompts) ===")
    print(f"{'α·norm':>7} {'formal':>7} {'casual':>7} {'contr':>6}  (formal↑ under +α? casual/contr↑ under −α?)")
    for f in fracs:
        a=agg[f]; print(f"{f:>+7.1f} {a['F']:>7} {a['C']:>7} {a['K']:>6}")
    print("\n--- sample gens at extremes (prompt 1 'why cats purr') ---")
    print(f"  +0.6: {agg[0.6]['txt'][0]}")
    print(f"  -0.6: {agg[-0.6]['txt'][0]}")
    json.dump({f"{k}":{"F":v['F'],"C":v['C'],"K":v['K'],"N":v['N']} for k,v in agg.items()},open(os.path.join(ROOT,"mvp/results/workspace/e12_formality_alpha.json"),"w"))
    print("[done]")
main()
