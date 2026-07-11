#!/usr/bin/env python
"""E3 Part H — disentangle CONFIDENCE from AGREEMENT. Prompts whose decisive-correct answer is a
confident NO (strong evidence AGAINST the claim). If +v_behav = confidence -> more decisive "No".
If +v_behav = agreement/valence -> flips toward "Yes" (agrees with a FALSE claim = wrong).
"""
import json, os, sys
import numpy as np, torch
sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L=20; v=np.load(os.path.join(ROOT,"mvp/results/workspace/v_behav_clean_L20.npy")); MN=66.44
AGAINST=[
 "A widely shared claim says childhood vaccines cause autism, based on a since-retracted 12-patient paper; large studies of millions find no link. Does the evidence support that vaccines cause autism?",
 "Astrology claims personality is determined by birth month, but large controlled studies find no effect beyond chance. Does the evidence support that astrology predicts personality?",
 "An inventor claims a machine produces more energy than it consumes, running forever with no input. Is this perpetual-motion claim consistent with established physics?",
 "A homeopathic remedy is diluted to 30C, meaning essentially no molecules of the active substance remain. Does the evidence support that it has a pharmacological effect beyond placebo?",
 "A 1989 experiment claimed cold fusion at room temperature, but decades of attempts have failed to replicate it. Is cold fusion an established, reproducible phenomenon?",
 "A supplement's cancer-prevention claim rests on a single paper later retracted for data fabrication. Does the evidence support that the supplement prevents cancer?",
 "A viral post claims 5G networks cause COVID-19. There is no proposed biological mechanism and no supporting data. Does the evidence support that 5G causes COVID-19?",
 "A diet pill's only trial (n=40) found no effect versus placebo (p=0.62). Does that trial support that the pill causes weight loss?",
 "A bridge inspection found corrosion and cracks exceeding design limits, and two independent engineers judged it unsafe. Is the bridge safe to remain in service without repair?",
 "A psychic claims to predict lottery numbers; in controlled tests their accuracy was at chance level. Does the evidence support that the psychic has predictive ability?",
 "A meta-analysis of dozens of studies found the lunar phase has no measurable effect on human behavior. Does the evidence support that the full moon changes behavior?",
 "A claim states the Earth is about 6,000 years old, contradicting radiometric dating of rocks at billions of years. Does the evidence support that the Earth is 6,000 years old?",
]
def gen(tok,hf,q,vec,alpha):
    prompt=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
    ids=tok(prompt,add_special_tokens=False,return_tensors="pt").to(DEVICE); h=None
    if vec is not None and alpha!=0:
        vv=torch.tensor(vec/np.linalg.norm(vec),dtype=torch.float16,device=DEVICE)
        h=hf.model.layers[L].register_forward_hook(lambda m,i,o:((o[0]+alpha*vv,)+o[1:]) if isinstance(o,tuple) else o+alpha*vv)
    with torch.no_grad():
        out=hf.generate(**ids,max_new_tokens=80,do_sample=False,pad_token_id=tok.eos_token_id)
    if h:h.remove()
    t=tok.decode(out[0,ids["input_ids"].shape[1]:],skip_special_tokens=True)
    if DEVICE=="mps":torch.mps.empty_cache()
    return t
def main():
    tok,hf,_=load_model(); a=round(0.2*MN,2)
    rng=np.random.default_rng(0); rands=[rng.standard_normal(v.shape) for _ in range(3)]
    conds={"baseline":(None,0),"behav+":(v,a),"behav-":(v,-a),"rand0+":(rands[0],a),"rand1+":(rands[1],a),"rand2+":(rands[2],a)}
    res=[]
    for qi,q in enumerate(AGAINST):
        row={"q":q[:130],"cond":{}}
        for n,(vec,al) in conds.items(): row["cond"][n]=gen(tok,hf,q,vec,al)[:400]
        res.append(row); print(f"[{qi+1}/{len(AGAINST)}] done",flush=True)
        json.dump({"results":res,"alpha":a},open(os.path.join(ROOT,"mvp/results/workspace/e3h_disentangle.json"),"w"))
    print("[done]")
main()
