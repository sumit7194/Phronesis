#!/usr/bin/env python
"""E6a — complete read/=write for FORMAT behaviorally: steer the READ direction (diff-of-means)
and show it steers markdown WORSE than the WRITE direction (behavioral Jacobian v_fmt, |Δ|=8.88).
Rebuilds v_dom_fmt from struct-vs-prose completion activations, then steers ±v_dom on the same 12
neutral test prompts with the same auto markdown metric.
"""
import json, os, re, sys
import numpy as np, torch
sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L=20; MN=66.44
vfmt=np.load(os.path.join(ROOT,"mvp/results/workspace/v_fmt_L20.npy"))
BUILD=["How does photosynthesis work?","What are the main benefits of regular exercise?","Explain how a bicycle stays upright.","What causes the seasons to change?","How do vaccines protect against disease?","What is the difference between weather and climate?","Explain how the internet delivers a web page.","Why does bread rise when baking?","How do noise-cancelling headphones work?","What makes the sky blue?","How does a refrigerator keep food cold?","Explain how muscles grow with training.","What happens during a solar eclipse?","How do plants get their nitrogen?"]
TEST=["What are the benefits of drinking enough water?","How should a beginner start learning to cook?","Why is sleep important for health?","What makes a good password?","How can someone improve their focus while working?","What are some tips for saving money?","How does regular walking help the body?","What should you consider when adopting a pet?","How can I make my morning routine better?","What are good ways to reduce stress?","How do I keep houseplants alive?","What makes a piece of writing clear?"]
def md(t):
    n=max(len(t.split()),1); m=len(re.findall(r'(^|\n)\s*#{1,6}\s',t))+len(re.findall(r'\*\*',t))//2+len(re.findall(r'(^|\n)\s*[-*]\s',t))+len(re.findall(r'(^|\n)\s*\d+\.\s',t))
    return round(100*m/n,2)
def gen(tok,hf,q,vec,alpha):
    prompt=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
    ids=tok(prompt,add_special_tokens=False,return_tensors="pt").to(DEVICE); h=None
    if vec is not None and alpha!=0:
        vv=torch.tensor(vec/np.linalg.norm(vec),dtype=torch.float16,device=DEVICE)
        h=hf.model.layers[L].register_forward_hook(lambda m,i,o:((o[0]+alpha*vv,)+o[1:]) if isinstance(o,tuple) else o+alpha*vv)
    with torch.no_grad(): out=hf.generate(**ids,max_new_tokens=120,do_sample=False,pad_token_id=tok.eos_token_id)
    if h:h.remove()
    t=tok.decode(out[0,ids["input_ids"].shape[1]:],skip_special_tokens=True)
    if DEVICE=="mps":torch.mps.empty_cache()
    return t
def main():
    tok,hf,_=load_model(); a=round(0.2*MN,2)
    sid=tok("##",add_special_tokens=False)["input_ids"][0]; pid=tok(" The",add_special_tokens=False)["input_ids"][0]
    sa=[]; pa=[]
    with torch.no_grad():
        for q in BUILD:
            prompt=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
            base=tok(prompt,add_special_tokens=False)["input_ids"]
            for tid,bk in ((sid,sa),(pid,pa)):
                o=hf(torch.tensor([base+[tid]],device=DEVICE),output_hidden_states=True); bk.append(o.hidden_states[L+1][0,-1].float().cpu().numpy())
            if DEVICE=="mps":torch.mps.empty_cache()
    vdom=np.mean(sa,0)-np.mean(pa,0)
    unit=lambda v:v/(np.linalg.norm(v)+1e-9)
    print(f"cos(v_dom_fmt, v_fmt_write) = {np.dot(unit(vdom),unit(vfmt)):+.3f}")
    rng=np.random.default_rng(1); rands=[rng.standard_normal(vdom.shape) for _ in range(3)]
    conds={"baseline":(None,0),"READ+":(vdom,a),"READ-":(vdom,-a),"r0":(rands[0],a),"r1":(rands[1],a),"r2":(rands[2],a)}
    agg={c:[] for c in conds}
    for qi,q in enumerate(TEST):
        for n,(vec,al) in conds.items(): agg[n].append(md(gen(tok,hf,q,vec,al)))
        print(f"[{qi+1}/12] base={agg['baseline'][-1]} READ+={agg['READ+'][-1]} READ-={agg['READ-'][-1]}",flush=True)
    bc=np.array(agg["baseline"])
    print("\n=== FORMAT read-direction steering (markdown density) ===")
    for c in conds: print(f"  {c:>9}: mean={np.mean(agg[c]):.2f} Δ={np.mean(np.array(agg[c])-bc):+.2f}")
    rf=np.mean([np.abs(np.array(agg[f'r{k}'])-bc).mean() for k in range(3)])
    print(f"\n  |Δ| READ-dir(diff-of-means) fmt+ = {np.abs(np.array(agg['READ+'])-bc).mean():.2f}  random={rf:.2f}")
    print(f"  vs WRITE-dir(behavioral Jacobian) from E5b: |Δ|fmt+ = 8.88")
    print("  read/=write CONFIRMED behaviorally if READ |Δ| << WRITE 8.88 (ideally ~random)")
    print("[done]")
main()
