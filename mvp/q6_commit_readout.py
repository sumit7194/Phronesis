#!/usr/bin/env python
"""q6 commit-wrong workspace read (on the UNCAPPED trace that boxes 12, gold=13).

Question: the model outputs 12 and never writes 13 in its reasoning. Does its WORKSPACE
latently represent 13 (a suppressed/commit-gate error, rescuable) or is 13 genuinely ABSENT
(a conceptual blindspot — wrong internal model of the problem)?

Reads the normalized J-lens (n=45, L14/20/26) over a LATE window covering Step-2 derivation
(n >= 90/7.50 = 12), the Step-3 interpretation, and the final \\boxed{12}. Tracks the rank/weight
of the TRUE answer '13', the WRONG answer '12', and the boundary numbers '11'/'14' as nulls.
"""
import json, os, sys, re
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from jlens.lens import JacobianLens
from workspace_common import LENS_PATH
DEVICE="mps"; LAYERS=[14,20,26]; TOPK=25

def build_prompt(tok, q):
    m=[{"role":"user","content":q+"\nReason step by step, then give the final answer in \\boxed{}."}]
    return tok.apply_chat_template(m,add_generation_prompt=True,tokenize=False,enable_thinking=True)

def main():
    tok=AutoTokenizer.from_pretrained("Qwen/Qwen3-4B")
    hf=AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-4B",dtype=torch.float16).to(DEVICE).eval()
    model=jlens.from_hf(hf,tok,force_bos=False)
    lens=JacobianLens.load(LENS_PATH); band=[l for l in LAYERS if l in lens.source_layers]

    nc=json.load(open("results/workspace/nocap_traces.json"))
    q6=next(r for r in nc['rows'] if r.get('id')=='q6_gsm_failed')
    stim=json.load(open("workspace_6q_stimuli.json"))["questions"]
    qtext=next(q['question'] for q in stim if q['id']=='q6_gsm_failed')
    full=build_prompt(tok,qtext)+q6['trace']
    ids=tok(full,return_tensors="pt")["input_ids"].to(DEVICE)
    n=ids.shape[1]; toks=[tok.decode([t]) for t in ids[0].tolist()]
    print(f"[q6] full seq = {n} tokens; boxes 12 (gold 13)",flush=True)

    # locate the box + the Step-2 derivation "= 12" region -> read a window around them
    txt_join="".join(toks)
    # find token index of the last '12' occurrences and 'boxed'
    box_pos=[i for i,t in enumerate(toks) if 'boxed' in t]
    start=max(0, (box_pos[-1] if box_pos else n)-900)   # ~900 tokens before the box through the end
    span=list(range(start,n))
    print(f"    reading workspace over positions {start}..{n} ({len(span)} pos), band={band}",flush=True)

    with ActivationRecorder(model.layers, at=band) as rec:
        hf.model(input_ids=ids, use_cache=False)
        acts={l:rec.activations[l][0].detach() for l in band}

    # targets: true=13, wrong=12, nulls=11,14 (neighboring boundary numbers)
    def variants(s): return {s, " "+s}
    targets={'13(TRUE)':['13'],'12(WRONG)':['12'],'11(null)':['11'],'14(null)':['14']}
    # precompute token ids that decode to each number string
    def find_rank(row_tokens, wants):
        for rank,(t,w) in enumerate(row_tokens):
            if t.strip() in wants: return rank,w
        return None,None

    best={k:(None,0.0,None) for k in targets}   # (best_rank, weight_at_best, position)
    present_counts={k:0 for k in targets}
    POS_CHUNK=128; per_layer_primary={}
    for l in band:
        Jl=lens.jacobians[l].to(DEVICE)
        for s in range(0,len(span),POS_CHUNK):
            pos=span[s:s+POS_CHUNK]
            h=acts[l][pos].float()
            logits=model.unembed(h@Jl.T).float()
            tp=torch.softmax(logits,-1).topk(TOPK,-1)
            for i,p in enumerate(pos):
                row=[(tok.decode([int(t)]).strip(), float(w)) for t,w in zip(tp.indices[i],tp.values[i])]
                if l==20: per_layer_primary[p]=row
                for k,wants in targets.items():
                    r,w=find_rank(row,set(wants))
                    if r is not None:
                        present_counts[k]+=1
                        if best[k][0] is None or r<best[k][0]: best[k]=(r,w,p)
        del Jl
        if DEVICE=="mps": torch.mps.empty_cache()

    print("\n=== does the TRUE answer 13 ever enter the workspace? (window incl. the commit) ===")
    for k in targets:
        r,w,p=best[k]
        pc=present_counts[k]
        loc=f"best rank {r} (w={w:.3f}) @pos {p} tok={toks[p].strip()!r}" if r is not None else "NEVER appears"
        print(f"  {k:11}: present in {pc}/{len(span)*len(band)} (layer,pos) slots | {loc}")

    # dump the workspace right AT the box token and the '= 12' derivation
    print("\n=== L20 workspace at the commit region (top-8) ===")
    show=[p for p in span if p in per_layer_primary and ('12' in toks[p] or 'boxed' in toks[p] or toks[p].strip() in ('=','12'))][:12]
    for p in show:
        top=", ".join(f"{t}({w:.2f})" for t,w in per_layer_primary[p][:8])
        print(f"  [{p}] tok={toks[p]!r:10} | {top}")
    out={"n":n,"window":[start,n],"best":{k:best[k] for k in targets},"present":present_counts}
    json.dump(out,open("results/workspace/hard/q6_commit_read.json","w"),indent=1)
    print("\n[done] ->",out['best'])

main()
