#!/usr/bin/env python
"""E5 Stage 2 — steer the FORMAT axis on neutral questions; AUTO-measure markdown density (no judge).
+v_fmt -> more markdown structure, -v_fmt -> plainer prose; beat random.
"""
import json, os, re, sys
import numpy as np, torch
sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L=20; v=np.load(os.path.join(ROOT,"mvp/results/workspace/v_fmt_L20.npy")); MN=66.44
QS=[
 "What are the benefits of drinking enough water?","How should a beginner start learning to cook?",
 "Why is sleep important for health?","What makes a good password?",
 "How can someone improve their focus while working?","What are some tips for saving money?",
 "How does regular walking help the body?","What should you consider when adopting a pet?",
 "How can I make my morning routine better?","What are good ways to reduce stress?",
 "How do I keep houseplants alive?","What makes a piece of writing clear?",
]
def md_density(t):
    n=max(len(t.split()),1)
    m=len(re.findall(r'(^|\n)\s*#{1,6}\s',t))         # headers
    m+=len(re.findall(r'\*\*',t))//2                   # bold pairs
    m+=len(re.findall(r'(^|\n)\s*[-*]\s',t))           # bullets
    m+=len(re.findall(r'(^|\n)\s*\d+\.\s',t))          # numbered
    return round(100*m/n,2)
def gen(tok,hf,q,vec,alpha):
    prompt=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
    ids=tok(prompt,add_special_tokens=False,return_tensors="pt").to(DEVICE); h=None
    if vec is not None and alpha!=0:
        vv=torch.tensor(vec/np.linalg.norm(vec),dtype=torch.float16,device=DEVICE)
        h=hf.model.layers[L].register_forward_hook(lambda m,i,o:((o[0]+alpha*vv,)+o[1:]) if isinstance(o,tuple) else o+alpha*vv)
    with torch.no_grad():
        out=hf.generate(**ids,max_new_tokens=120,do_sample=False,pad_token_id=tok.eos_token_id)
    if h:h.remove()
    t=tok.decode(out[0,ids["input_ids"].shape[1]:],skip_special_tokens=True)
    if DEVICE=="mps":torch.mps.empty_cache()
    return t
def main():
    tok,hf,_=load_model(); a=round(0.2*MN,2)
    rng=np.random.default_rng(0); rands=[rng.standard_normal(v.shape) for _ in range(3)]
    conds={"baseline":(None,0),"fmt+":(v,a),"fmt-":(v,-a),"rand0+":(rands[0],a),"rand1+":(rands[1],a),"rand2+":(rands[2],a)}
    res=[]; agg={c:[] for c in conds}
    for qi,q in enumerate(QS):
        row={"q":q,"cond":{}}
        for n,(vec,al) in conds.items():
            t=gen(tok,hf,q,vec,al); d=md_density(t)
            row["cond"][n]={"md":d,"text":t[:300]}; agg[n].append(d)
        res.append(row); print(f"[{qi+1}/{len(QS)}] base={row['cond']['baseline']['md']} fmt+={row['cond']['fmt+']['md']} fmt-={row['cond']['fmt-']['md']}",flush=True)
        json.dump({"results":res,"alpha":a},open(os.path.join(ROOT,"mvp/results/workspace/e5b_format_steer.json"),"w"))
    bc=np.array(agg["baseline"])
    print("\n=== markdown density (markers/100 words) ===")
    for c in conds:
        cm=np.array(agg[c]); print(f"  {c:>9}: mean={cm.mean():.2f}  Δ={ (cm-bc).mean():+.2f}")
    rf=np.mean([np.abs(np.array(agg[f'rand{k}+'])-bc).mean() for k in range(3)])
    print(f"  signed fmt+ minus fmt- = {(np.array(agg['fmt+'])-np.array(agg['fmt-'])).mean():+.2f}")
    print(f"  |Δ| fmt+={np.abs(np.array(agg['fmt+'])-bc).mean():.2f} fmt-={np.abs(np.array(agg['fmt-'])-bc).mean():.2f} random={rf:.2f}")
    print("[done]")
main()
