#!/usr/bin/env python
"""E9 — steer-validate the FORMALITY axis. +v_formality -> more formal, -v_formality -> more casual.
Auto metric: formal-discourse-markers minus (contractions + casual words) per 100 words. Eyeball too.
"""
import json, os, re, sys
import numpy as np, torch
sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L=20; v=np.load(os.path.join(ROOT,"mvp/results/workspace/v_formality_L20.npy")); MN=66.44
PROMPTS=["Explain why cats purr.","Tell me how to make a paper airplane.","Share a fun fact about octopuses.","How do I make friends as an adult?","Explain what a black hole is.","Why do we yawn?","How does a microwave heat food?","What's the best way to start learning guitar?","Tell me about the history of pizza.","Why is the sky dark at night?","How do bees make honey?","What makes a good cup of tea?"]
FORMAL=re.compile(r"\b(Furthermore|Moreover|Therefore|Indeed|Nevertheless|Consequently|Thus|Hence|Additionally|Nonetheless|Accordingly|whom|shall)\b")
CASUAL=re.compile(r"\b(yeah|gonna|kinda|sorta|stuff|basically|honestly|really|pretty|totally|cool|fun|awesome|lots?|okay|ok|guys?)\b",re.I)
CONTR=re.compile(r"\b\w+('re|'ll|'ve|'d|n't)\b|\b(I'm|it's|that's|here's|there's|you're|we're|they're|don't|can't|won't|let's)\b",re.I)
def fscore(t):
    n=max(len(t.split()),1)
    return round(100*(len(FORMAL.findall(t))-len(CASUAL.findall(t))-len(CONTR.findall(t)))/n,2)
def gen(tok,hf,q,vec,alpha):
    prompt=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
    ids=tok(prompt,add_special_tokens=False,return_tensors="pt").to(DEVICE); h=None
    if vec is not None and alpha!=0:
        vv=torch.tensor(vec/np.linalg.norm(vec),dtype=torch.float16,device=DEVICE)
        h=hf.model.layers[L].register_forward_hook(lambda m,i,o:((o[0]+alpha*vv,)+o[1:]) if isinstance(o,tuple) else o+alpha*vv)
    with torch.no_grad(): out=hf.generate(**ids,max_new_tokens=90,do_sample=False,pad_token_id=tok.eos_token_id)
    if h:h.remove()
    t=tok.decode(out[0,ids["input_ids"].shape[1]:],skip_special_tokens=True)
    if DEVICE=="mps":torch.mps.empty_cache()
    return t
def main():
    tok,hf,_=load_model(); a=round(0.2*MN,2)
    rng=np.random.default_rng(3); rands=[rng.standard_normal(v.shape) for _ in range(3)]
    conds={"baseline":(None,0),"formal+":(v,a),"formal-":(v,-a),"r0":(rands[0],a),"r1":(rands[1],a),"r2":(rands[2],a)}
    res=[]; agg={c:[] for c in conds}
    for qi,q in enumerate(PROMPTS):
        row={"q":q,"cond":{}}
        for n,(vec,al) in conds.items():
            t=gen(tok,hf,q,vec,al); row["cond"][n]={"f":fscore(t),"text":t[:280]}; agg[n].append(fscore(t))
        res.append(row); print(f"[{qi+1}/12] base={row['cond']['baseline']['f']} formal+={row['cond']['formal+']['f']} formal-={row['cond']['formal-']['f']}",flush=True)
        json.dump({"results":res,"alpha":a},open(os.path.join(ROOT,"mvp/results/workspace/e9_formality_steer.json"),"w"))
    bc=np.array(agg["baseline"])
    print("\n=== formality score (formal - casual - contractions, /100w) ===")
    for c in conds: print(f"  {c:>9}: mean={np.mean(agg[c]):+.2f} Δ={np.mean(np.array(agg[c])-bc):+.2f}")
    rf=np.mean([np.abs(np.array(agg[f'r{k}'])-bc).mean() for k in range(3)])
    print(f"\n  signed formal+ minus formal- = {(np.array(agg['formal+'])-np.array(agg['formal-'])).mean():+.2f}")
    print(f"  |Δ| formal+={np.abs(np.array(agg['formal+'])-bc).mean():.2f} formal-={np.abs(np.array(agg['formal-'])-bc).mean():.2f} random={rf:.2f}")
    print("[done]")
main()
