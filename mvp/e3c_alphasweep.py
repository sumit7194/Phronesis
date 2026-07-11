#!/usr/bin/env python
"""E3 Part C — alpha dose-response along +-v_behav to resolve the sign-flip/nonlinearity wrinkle.
Reuse v_behav_L20 (saved by Part A). Steer L20 at alpha in {-0.4..+0.4}*norm, generate on the same
12 held-out prompts, save text. A blinded judge pass (separate) scores commitment vs alpha.
"""
import json, os, sys
import numpy as np, torch
sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L=20
v=np.load(os.path.join(ROOT,"mvp/results/workspace/v_behav_L20.npy"))
meannorm=66.44   # from Part B
FRACS=[-0.4,-0.2,-0.1,0.0,0.1,0.2,0.4]

def gen(tok,hf,q,alpha):
    prompt=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
    ids=tok(prompt,add_special_tokens=False,return_tensors="pt").to(DEVICE)
    h=None
    if alpha!=0:
        vv=torch.tensor(v/(np.linalg.norm(v)+1e-9),dtype=torch.float16,device=DEVICE)
        def hook(m,i,o):
            return ((o[0]+alpha*vv,)+o[1:]) if isinstance(o,tuple) else o+alpha*vv
        h=hf.model.layers[L].register_forward_hook(hook)
    with torch.no_grad():
        out=hf.generate(**ids,max_new_tokens=80,do_sample=False,pad_token_id=tok.eos_token_id)
    if h: h.remove()
    txt=tok.decode(out[0,ids["input_ids"].shape[1]:],skip_special_tokens=True)
    if DEVICE=="mps": torch.mps.empty_cache()
    return txt

def main():
    tok,hf,_=load_model()
    held=json.load(open(os.path.join(ROOT,"corpus/eval-prompts/calibrated-confidence.json")))
    qs=[(d.get("prompt") or d.get("question")) for d in held][:12]
    res=[]
    for qi,q in enumerate(qs):
        row={"q":q[:120],"alpha":{}}
        for fr in FRACS:
            a=round(fr*meannorm,2)
            row["alpha"][str(fr)]=gen(tok,hf,q,a)[:400]
        res.append(row)
        print(f"[{qi+1}/{len(qs)}] done",flush=True)
        json.dump({"results":res,"fracs":FRACS,"meannorm":meannorm},open(os.path.join(ROOT,"mvp/results/workspace/e3c_alphasweep.json"),"w"))
    print("[done]")

if __name__=="__main__": main()
