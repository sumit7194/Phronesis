#!/usr/bin/env python
"""E5 Stage 1 — FORMAT behavioral Jacobian (structured-markdown <-> plain-prose): a NON-stance
behavior, the real generalization test. B = logsumexp(markdown-opener toks) - logsumexp(prose-opener
toks) at the response-start. Decode, consistency, and cos vs its own diff-of-means [read/=write] AND
vs the confidence + sycophancy axes [is FORMAT a 3rd distinct axis?].
"""
import json, os, sys
import numpy as np, torch
sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYERS=[14,20]
STRUCT=["##","###","**"," -"," *"," #","-","*"]          # markdown structure openers
PROSE=[" The"," I"," A"," It"," This"," There"," To"," In"," When"," Photos"]  # sentence starters
QS=[
 "How does photosynthesis work?","What are the main benefits of regular exercise?",
 "Explain how a bicycle stays upright.","What causes the seasons to change?",
 "How do vaccines protect against disease?","What is the difference between weather and climate?",
 "Explain how the internet delivers a web page.","Why does bread rise when baking?",
 "How do noise-cancelling headphones work?","What makes the sky blue?",
 "How does a refrigerator keep food cold?","Explain how muscles grow with training.",
 "What happens during a solar eclipse?","How do plants get their nitrogen?",
]
def sids(tok,ws):
    out=[]
    for w in ws:
        ii=tok(w,add_special_tokens=False)["input_ids"]
        if len(ii)==1: out.append(ii[0])
    return list(dict.fromkeys(out))
def main():
    tok,hf,lens=load_model()
    cids,hids=sids(tok,STRUCT),sids(tok,PROSE)
    print(f"[load] struct toks={[tok.decode([i]) for i in cids]}")
    print(f"       prose  toks={[tok.decode([i]) for i in hids]}\n")
    per={L:[] for L in LAYERS}; sa={L:[] for L in LAYERS}; pa={L:[] for L in LAYERS}
    for q in QS:
        prompt=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
        ids=torch.tensor([tok(prompt,add_special_tokens=False)["input_ids"]],device=DEVICE)
        embeds=hf.model.embed_tokens(ids).detach().requires_grad_(True)
        cap={}; hs=[hf.model.layers[L].register_forward_hook((lambda L:(lambda m,i,o:cap.__setitem__(L,o[0] if isinstance(o,tuple) else o)))(L)) for L in LAYERS]
        out=hf(inputs_embeds=embeds)
        for h in hs:h.remove()
        last=out.logits[0,-1]
        B=torch.logsumexp(last[cids],0)-torch.logsumexp(last[hids],0)
        gs=torch.autograd.grad(B,[cap[L] for L in LAYERS])
        for L,g in zip(LAYERS,gs): per[L].append(g[0,-1].detach().float().cpu().numpy())
        del out,cap,gs,B,embeds
        with torch.no_grad():
            for tid,bk in ((cids[0],sa),(hids[0],pa)):   # "##" vs " The" completion
                o=hf(torch.tensor([ids[0].tolist()+[tid]],device=DEVICE),output_hidden_states=True)
                for L in LAYERS: bk[L].append(o.hidden_states[L+1][0,-1].float().cpu().numpy())
        if DEVICE=="mps":torch.mps.empty_cache()
    unit=lambda v:np.asarray(v,float)/(np.linalg.norm(v)+1e-9)
    conf=np.load(os.path.join(ROOT,"mvp/results/workspace/v_behav_clean_L20.npy"))
    syco=np.load(os.path.join(ROOT,"mvp/results/workspace/v_syco_L20.npy"))
    for L in LAYERS:
        G=np.array(per[L]); vb=G.mean(0)
        U=G/(np.linalg.norm(G,axis=1,keepdims=True)+1e-9); C=U@U.T; iu=np.triu_indices(len(G),1)
        vdom=np.mean(sa[L],0)-np.mean(pa[L],0)
        line=f"=== L{L} === consistency={C[iu].mean():+.3f}  fmt_behav·fmt_dom={np.dot(unit(vb),unit(vdom)):+.3f}"
        if L==20: line+=f"  fmt·CONF={np.dot(unit(vb),unit(conf)):+.3f}  fmt·SYCO={np.dot(unit(vb),unit(syco)):+.3f}"
        print(line)
        for sign,nm in [(1,"+v_fmt (toward MARKDOWN/structure)"),(-1,"-v_fmt (toward PLAIN prose)")]:
            vt=torch.tensor(sign*unit(vb),dtype=torch.float16,device=DEVICE)
            top=[repr(tok.decode([t])) for t in torch.topk(lens.unembed(vt.unsqueeze(0)).float()[0],15).indices.tolist()]
            print(f"   {nm}: {' '.join(top)}")
        np.save(os.path.join(ROOT,f"mvp/results/workspace/v_fmt_L{L}.npy"),vb); print()
main()
