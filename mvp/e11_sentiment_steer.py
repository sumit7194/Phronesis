#!/usr/bin/env python
"""E11 — steer-validate the CLEANED sentiment axis on held-out review prompts. +v_sent -> positive
review, -v_sent -> negative. Auto sentiment = (pos - neg) affect-word density /100w. Eyeball too.
"""
import json, os, re, sys
import numpy as np, torch
sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L=20; v=np.load(os.path.join(ROOT,"mvp/results/workspace/v_sentiment_clean_L20.npy")); MN=66.44
PROMPTS=["Write a short review of a wireless mouse.","Review a downtown sandwich shop.","Give a brief review of a fitness tracker.","Review a weekend camping tent.","Write a quick review of a streaming documentary.","Review a budget hotel room.","Give a short review of a bluetooth speaker.","Review a local farmers market.","Write a brief review of a used sedan.","Review a meal-kit delivery service.","Give a quick review of a paperback thriller.","Review a neighborhood pizza place."]
POS=re.compile(r"\b(excellent|wonderful|fantastic|delightful|superb|great|lovely|impressive|amazing|perfect|terrific|gorgeous|love|enjoyable|pleasant|solid|recommend|best|good|comfortable|reliable)\b",re.I)
NEG=re.compile(r"\b(terrible|awful|dreadful|horrible|disappointing|lousy|miserable|mediocre|bad|poor|frustrating|bitter|regret|unsuccessful|fail|failed|uncomfortable|unreliable|avoid|worst|disappointment)\b",re.I)
def sent(t):
    n=max(len(t.split()),1); return round(100*(len(POS.findall(t))-len(NEG.findall(t)))/n,2)
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
    rng=np.random.default_rng(4); rands=[rng.standard_normal(v.shape) for _ in range(3)]
    conds={"baseline":(None,0),"sent+":(v,a),"sent-":(v,-a),"r0":(rands[0],a),"r1":(rands[1],a),"r2":(rands[2],a)}
    res=[]; agg={c:[] for c in conds}
    for qi,q in enumerate(PROMPTS):
        row={"q":q,"cond":{}}
        for n,(vec,al) in conds.items():
            t=gen(tok,hf,q,vec,al); row["cond"][n]={"s":sent(t),"text":t[:280]}; agg[n].append(sent(t))
        res.append(row); print(f"[{qi+1}/12] base={row['cond']['baseline']['s']} sent+={row['cond']['sent+']['s']} sent-={row['cond']['sent-']['s']}",flush=True)
        json.dump({"results":res,"alpha":a},open(os.path.join(ROOT,"mvp/results/workspace/e11_sentiment_steer.json"),"w"))
    bc=np.array(agg["baseline"])
    print("\n=== sentiment score (pos-neg affect words /100w) ===")
    for c in conds: print(f"  {c:>9}: mean={np.mean(agg[c]):+.2f} Δ={np.mean(np.array(agg[c])-bc):+.2f}")
    rf=np.mean([np.abs(np.array(agg[f'r{k}'])-bc).mean() for k in range(3)])
    print(f"\n  signed sent+ minus sent- = {(np.array(agg['sent+'])-np.array(agg['sent-'])).mean():+.2f}")
    print(f"  |Δ| sent+={np.abs(np.array(agg['sent+'])-bc).mean():.2f} sent-={np.abs(np.array(agg['sent-'])-bc).mean():.2f} random={rf:.2f}")
    print("[done]")
main()
