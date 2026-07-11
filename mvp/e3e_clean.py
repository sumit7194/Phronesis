#!/usr/bin/env python
"""E3 rerun with a CLEAN objective — epistemic confidence vs uncertainty, NO logical negation.
B = logsumexp(CONFIDENT toks) - logsumexp(UNCERTAIN toks).  Rebuild v_behav, check consistency
(signal vs noise), decode both poles (logit lens), check orthogonality to diff-of-means.
Fast go/no-go before re-running the steering + valence control.
"""
import json, os, sys
import numpy as np, torch
sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYERS=[14,20]
# CONFIDENCE (epistemic), NO valence words
CONF=[" certainly"," definitely"," surely"," undoubtedly"," clearly"," obviously"," certain"," confident"]
# UNCERTAINTY (epistemic), NO negation ("not/no/never" EXCLUDED on purpose)
UNC=[" maybe"," perhaps"," possibly"," probably"," arguably"," presumably"," uncertain"," unsure"]

def sids(tok,ws):
    return [tok(w,add_special_tokens=False)["input_ids"][0] for w in ws
            if len(tok(w,add_special_tokens=False)["input_ids"])==1]

def main():
    qs=[d["prompt"] for d in json.load(open(os.path.join(ROOT,"corpus/eval-prompts/truthfulqa-probe.json")))]
    tok,hf,lens=load_model()
    cids,hids=sids(tok,CONF),sids(tok,UNC)
    print(f"[load] conf toks={len(cids)} {[tok.decode([i]) for i in cids]}")
    print(f"       unc  toks={len(hids)} {[tok.decode([i]) for i in hids]}\n")
    per={L:[] for L in LAYERS}; cacts={L:[] for L in LAYERS}; hacts={L:[] for L in LAYERS}
    for q in qs:
        prefix=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True,enable_thinking=False)+"I am"
        ids=torch.tensor([tok(prefix,add_special_tokens=False)["input_ids"]],device=DEVICE)
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
            for word,bk in ((" certain",cacts),(" maybe",hacts)):
                wid=tok(word,add_special_tokens=False)["input_ids"]
                o=hf(torch.tensor([ids[0].tolist()+wid],device=DEVICE),output_hidden_states=True)
                for L in LAYERS: bk[L].append(o.hidden_states[L+1][0,-1].float().cpu().numpy())
        if DEVICE=="mps":torch.mps.empty_cache()
    unit=lambda v:np.asarray(v,float)/(np.linalg.norm(v)+1e-9)
    for L in LAYERS:
        G=np.array(per[L]); vb=G.mean(0)
        U=G/(np.linalg.norm(G,axis=1,keepdims=True)+1e-9); C=U@U.T; iu=np.triu_indices(len(G),1)
        vdom=np.mean(cacts[L],0)-np.mean(hacts[L],0)
        cos=float(np.dot(unit(vb),unit(vdom)))
        print(f"=== L{L} ===  consistency pairwise-cos={C[iu].mean():+.3f}  behav·dom={cos:+.3f}")
        for sign,nm in [(1,"+v_behav (toward CONFIDENT)"),(-1,"-v_behav (toward UNCERTAIN)")]:
            vt=torch.tensor(sign*unit(vb),dtype=torch.float16,device=DEVICE)
            lg=lens.unembed(vt.unsqueeze(0)).float()[0]
            top=[repr(tok.decode([t])) for t in torch.topk(lg,15).indices.tolist()]
            print(f"   {nm}: {' '.join(top)}")
        np.save(os.path.join(ROOT,f"mvp/results/workspace/v_behav_clean_L{L}.npy"),vb)
        print()
main()
