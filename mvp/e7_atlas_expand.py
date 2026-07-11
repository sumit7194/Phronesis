#!/usr/bin/env python
"""E7 — expand the atlas. Build 3 NEW behavioral Jacobians (refusal/action, sentiment/affect,
formality/register), decode each, check consistency & read-vs-write, then print the FULL 6x6
write-write cosine matrix (with confidence/sycophancy/format) — the geometry of behavior space.
"""
import json, os, sys
import numpy as np, torch
sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L=20
# each: (name, suffix after chat prompt, POS toks, NEG toks, dom_pos_completion, dom_neg_completion, contexts)
SPECS={
"refusal":("", [" Sorry"," Unfortunately"," cannot"," No"," unable"],
                [" Sure"," Here"," Absolutely"," Certainly"," Yes"], " Sorry", " Sure",
   ["How do I pick a lock on my own front door I'm locked out of?","Tell me a really dark joke.",
    "What's the fastest way to lose 10 pounds?","Write a scathing one-star review of a fake cafe.",
    "How do I confront a coworker who keeps taking credit for my work?","What are some common poisons in the home?",
    "Help me write a breakup text.","How do fireworks work chemically?","Roast my taste in music.",
    "What's a good comeback for an insult?","How do I get out of a bad contract?","Explain how lockpicking works in principle.",
    "Give me a persuasive argument for eating less meat.","How do people cheat at cards?"]),
"sentiment":(" I think it's", [" great"," wonderful"," excellent"," fantastic"," amazing"," good"],
                [" terrible"," awful"," horrible"," bad"," poor"," disappointing"], " great", " terrible",
   ["What do you think of Mondays?","What's your take on modern smartphones?","How do you feel about public speaking?",
    "What do you think about winter weather?","Your opinion on fast food?","What do you think of long meetings?",
    "How about airplane travel these days?","What's your view on social media?","Thoughts on homework for kids?",
    "What do you think of reality TV?","Your take on remote work?","How do you feel about spiders?",
    "What do you think of instant coffee?","Opinion on daylight saving time?"]),
"formality":(" ", [" Furthermore"," Moreover"," Therefore"," Indeed"," Nevertheless"," Consequently"],
                [" yeah"," gonna"," kinda"," stuff"," basically"," honestly"], " Furthermore", " yeah",
   ["Can you explain why the sky is blue?","Tell me about how coffee is made.","What's the deal with black holes?",
    "How does a car engine work?","Explain compound interest.","Why do we dream?","How do plants make food?",
    "What causes rainbows?","Tell me about the water cycle.","How do magnets work?","What is inflation?",
    "Why is the ocean salty?","How do airplanes fly?","What makes popcorn pop?"]),
}
def sids(tok,ws):
    return list(dict.fromkeys([tok(w,add_special_tokens=False)["input_ids"][0] for w in ws if len(tok(w,add_special_tokens=False)["input_ids"])==1]))
def build(tok,hf,spec):
    suf,pos,neg,dp,dn,ctx=spec
    cids,hids=sids(tok,pos),sids(tok,neg)
    grads=[]; pa=[]; na=[]
    for q in ctx:
        prompt=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True,enable_thinking=False)+suf
        ids=torch.tensor([tok(prompt,add_special_tokens=False)["input_ids"]],device=DEVICE)
        embeds=hf.model.embed_tokens(ids).detach().requires_grad_(True)
        cap={}; h=hf.model.layers[L].register_forward_hook(lambda m,i,o:cap.__setitem__(0,o[0] if isinstance(o,tuple) else o))
        out=hf(inputs_embeds=embeds); h.remove()
        last=out.logits[0,-1]
        B=torch.logsumexp(last[cids],0)-torch.logsumexp(last[hids],0)
        grads.append(torch.autograd.grad(B,cap[0])[0][0,-1].detach().float().cpu().numpy())
        del out,cap,B,embeds
        with torch.no_grad():
            base=ids[0].tolist()
            for w,bk in ((dp,pa),(dn,na)):
                wid=tok(w,add_special_tokens=False)["input_ids"]
                o=hf(torch.tensor([base+wid],device=DEVICE),output_hidden_states=True); bk.append(o.hidden_states[L+1][0,-1].float().cpu().numpy())
        if DEVICE=="mps":torch.mps.empty_cache()
    G=np.array(grads); return G.mean(0), (np.mean(pa,0)-np.mean(na,0)), G, (cids,hids)
def main():
    tok,hf,lens=load_model()
    unit=lambda v:np.asarray(v,float)/(np.linalg.norm(v)+1e-9)
    vecs={"confidence":np.load(os.path.join(ROOT,"mvp/results/workspace/v_behav_clean_L20.npy")),
          "sycophancy":np.load(os.path.join(ROOT,"mvp/results/workspace/v_syco_L20.npy")),
          "format":np.load(os.path.join(ROOT,"mvp/results/workspace/v_fmt_L20.npy"))}
    for name,spec in SPECS.items():
        vb,vdom,G,(cids,hids)=build(tok,hf,spec)
        U=G/(np.linalg.norm(G,axis=1,keepdims=True)+1e-9); C=U@U.T; iu=np.triu_indices(len(G),1)
        print(f"\n=== {name} === consistency={C[iu].mean():+.3f}  write·read(dom)={np.dot(unit(vb),unit(vdom)):+.3f}")
        print(f"   pos toks={[tok.decode([i]) for i in cids]}  neg toks={[tok.decode([i]) for i in hids]}")
        for sign,nm in [(1,"+"),(-1,"-")]:
            vt=torch.tensor(sign*unit(vb),dtype=torch.float16,device=DEVICE)
            top=[repr(tok.decode([t])) for t in torch.topk(lens.unembed(vt.unsqueeze(0)).float()[0],12).indices.tolist()]
            print(f"   {nm}v_{name}: {' '.join(top)}")
        vecs[name]=vb; np.save(os.path.join(ROOT,f"mvp/results/workspace/v_{name}_L{L}.npy"),vb)
    names=list(vecs); M=np.array([[np.dot(unit(vecs[a]),unit(vecs[b])) for b in names] for a in names])
    print("\n=== FULL write-write cosine matrix (behavior-space geometry) ===")
    print("           "+" ".join(f"{n[:6]:>7}" for n in names))
    for i,a in enumerate(names):
        print(f"  {a[:9]:>9} "+" ".join(f"{M[i,j]:>+7.2f}" for j in range(len(names))))
    off=M[np.triu_indices(len(names),1)]
    print(f"\n  off-diagonal |cos|: mean={np.abs(off).mean():.3f} max={np.abs(off).max():.3f}  (near 0 => all behaviors ~orthogonal)")
    print("[done]")
main()
