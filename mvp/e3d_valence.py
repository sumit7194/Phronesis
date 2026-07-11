#!/usr/bin/env python
"""E3 Part D — negation-vs-commitment control. Prompts whose DECISIVE answer is affirmative (Yes).
If -v_behav is really a NEGATION direction (from the decode), it should push these toward DENIAL
(wrong), not toward more commitment. Judge valence + commitment separately.
"""
import json, os, sys
import numpy as np, torch
sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L=20; v=np.load(os.path.join(ROOT,"mvp/results/workspace/v_behav_L20.npy")); MN=66.44
AFFIRM=[
 "A meta-analysis of 40 RCTs (n=60,000) found handwashing reduces respiratory infection transmission with a large, consistent effect (RR 0.70, p<0.0001, low heterogeneity). Does the evidence support recommending handwashing to reduce infection spread?",
 "Independent temperature records from thousands of surface stations, satellites, and ocean buoys all show ~1.1C warming since pre-industrial times. Has global average surface temperature risen over the past century?",
 "A drug for a fatal condition passed three independent phase-3 RCTs (total n=12,000), each showing a large mortality reduction (HR 0.60, p<0.001) with no major safety signals. Does the evidence support that this drug reduces mortality?",
 "Is the speed of light in a vacuum approximately 300,000 kilometers per second?",
 "Decades of global surveillance show measles cases fall by over 95% after mass measles vaccination campaigns. Do measles vaccines substantially reduce measles cases?",
 "A pre-registered RCT in 300 schools (n=50,000) found a reading intervention improved literacy scores by 0.8 SD, replicated in two later independent trials. Does the evidence support that the intervention improves literacy?",
 "Water expands when it freezes, which is why ice floats on liquid water. Is it true that ice is less dense than liquid water?",
 "A bridge sensor network logged 5 years of continuous strain data showing all loads stayed within 40% of design limits, confirmed by two independent inspections. Is the bridge structurally safe to remain in service?",
 "Genome sequencing of 100,000 people confirmed, with genome-wide significance and replication, that a specific gene variant causes a well-characterized metabolic disease. Does this variant cause the disease?",
 "A company's new process was independently audited three times, each confirming 99.9% purity by two orthogonal methods. Does the evidence support the 99.9% purity claim?",
 "Repeated controlled experiments over a century confirm objects of different mass fall at the same rate in a vacuum. Do objects of different mass fall at the same rate in a vacuum?",
 "A cash-transfer program was evaluated by five independent RCTs (total n=40,000) all showing large, lasting income gains with no adverse effects. Does the evidence support that the program raises recipient income?",
]
def gen(tok,hf,q,alpha):
    prompt=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
    ids=tok(prompt,add_special_tokens=False,return_tensors="pt").to(DEVICE); h=None
    if alpha!=0:
        vv=torch.tensor(v/np.linalg.norm(v),dtype=torch.float16,device=DEVICE)
        h=hf.model.layers[L].register_forward_hook(lambda m,i,o:((o[0]+alpha*vv,)+o[1:]) if isinstance(o,tuple) else o+alpha*vv)
    with torch.no_grad():
        out=hf.generate(**ids,max_new_tokens=80,do_sample=False,pad_token_id=tok.eos_token_id)
    if h:h.remove()
    t=tok.decode(out[0,ids["input_ids"].shape[1]:],skip_special_tokens=True)
    if DEVICE=="mps":torch.mps.empty_cache()
    return t
def main():
    tok,hf,_=load_model(); a=round(0.2*MN,2)
    conds={"baseline":0,"behav-":-a,"behav+":a}
    res=[]
    for qi,q in enumerate(AFFIRM):
        row={"q":q[:130],"cond":{}}
        for n,al in conds.items(): row["cond"][n]=gen(tok,hf,q,al)[:400]
        res.append(row); print(f"[{qi+1}/{len(AFFIRM)}] done",flush=True)
        json.dump({"results":res,"alpha":a},open(os.path.join(ROOT,"mvp/results/workspace/e3d_valence.json"),"w"))
    print("[done]")
main()
