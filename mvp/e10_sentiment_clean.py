#!/usr/bin/env python
"""E10 — cleaner SENTIMENT objective. Review-generation contexts (sentiment is the natural axis, no
user-claim to conflate with agreement) + strong affect tokens at an explicit eval slot ("Overall,
it was ___"). Rebuild v_sentiment_clean, decode, consistency, cos vs old sentiment + other axes.
"""
import json, os, sys
import numpy as np, torch
sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYERS=[14,20]; SUF=" Overall, it was"
POS=[" excellent"," wonderful"," fantastic"," delightful"," superb"," great"," lovely"," impressive"]
NEG=[" terrible"," awful"," dreadful"," horrible"," disappointing"," lousy"," miserable"," mediocre"]
CTX=["Write a short review of a mid-range coffee maker.","Give a brief review of a budget airline flight.","Review a typical hotel breakfast buffet.","Write a quick review of a popular smartphone.","Review a chain restaurant's pasta dish.","Give a short review of a public city park.","Review a streaming service's interface.","Write a brief review of a compact car.","Review a pair of running shoes.","Give a quick review of a fast-food milkshake.","Review a paperback beach novel.","Write a short review of a neighborhood gym.","Review a mid-priced office chair.","Give a brief review of a museum audio guide."]
def sids(tok,ws): return list(dict.fromkeys([tok(w,add_special_tokens=False)["input_ids"][0] for w in ws if len(tok(w,add_special_tokens=False)["input_ids"])==1]))
def main():
    tok,hf,lens=load_model()
    cids,hids=sids(tok,POS),sids(tok,NEG)
    print(f"[load] pos={[tok.decode([i]) for i in cids]}\n       neg={[tok.decode([i]) for i in hids]}\n")
    per={L:[] for L in LAYERS}; pa={L:[] for L in LAYERS}; na={L:[] for L in LAYERS}
    for q in CTX:
        prompt=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True,enable_thinking=False)+SUF
        ids=torch.tensor([tok(prompt,add_special_tokens=False)["input_ids"]],device=DEVICE)
        embeds=hf.model.embed_tokens(ids).detach().requires_grad_(True)
        cap={}; hs=[hf.model.layers[L].register_forward_hook((lambda L:(lambda m,i,o:cap.__setitem__(L,o[0] if isinstance(o,tuple) else o)))(L)) for L in LAYERS]
        out=hf(inputs_embeds=embeds)
        for h in hs:h.remove()
        last=out.logits[0,-1]; B=torch.logsumexp(last[cids],0)-torch.logsumexp(last[hids],0)
        gs=torch.autograd.grad(B,[cap[L] for L in LAYERS])
        for L,g in zip(LAYERS,gs): per[L].append(g[0,-1].detach().float().cpu().numpy())
        del out,cap,gs,B,embeds
        with torch.no_grad():
            for w,bk in ((" excellent",pa),(" terrible",na)):
                wid=tok(w,add_special_tokens=False)["input_ids"]; o=hf(torch.tensor([ids[0].tolist()+wid],device=DEVICE),output_hidden_states=True)
                for L in LAYERS: bk[L].append(o.hidden_states[L+1][0,-1].float().cpu().numpy())
        if DEVICE=="mps":torch.mps.empty_cache()
    unit=lambda v:np.asarray(v,float)/(np.linalg.norm(v)+1e-9)
    old=np.load(os.path.join(ROOT,"mvp/results/workspace/v_sentiment_L20.npy"))
    conf=np.load(os.path.join(ROOT,"mvp/results/workspace/v_behav_clean_L20.npy"))
    for L in LAYERS:
        G=np.array(per[L]); vb=G.mean(0); U=G/(np.linalg.norm(G,axis=1,keepdims=True)+1e-9); C=U@U.T; iu=np.triu_indices(len(G),1)
        vdom=np.mean(pa[L],0)-np.mean(na[L],0)
        line=f"=== L{L} === consistency={C[iu].mean():+.3f}  write·read={np.dot(unit(vb),unit(vdom)):+.3f}"
        if L==20: line+=f"  clean·OLDsentiment={np.dot(unit(vb),unit(old)):+.3f}  ·conf={np.dot(unit(vb),unit(conf)):+.3f}"
        print(line)
        for sign,nm in [(1,"+v_sent (POSITIVE)"),(-1,"-v_sent (NEGATIVE)")]:
            vt=torch.tensor(sign*unit(vb),dtype=torch.float16,device=DEVICE)
            print(f"   {nm}: "+" ".join(repr(tok.decode([t])) for t in torch.topk(lens.unembed(vt.unsqueeze(0)).float()[0],14).indices.tolist()))
        np.save(os.path.join(ROOT,f"mvp/results/workspace/v_sentiment_clean_L{L}.npy"),vb); print()
    print("[done]")
main()
