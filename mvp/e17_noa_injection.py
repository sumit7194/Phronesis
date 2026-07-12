#!/usr/bin/env python
"""E17 — inject the 'generating-set' concept into q1 (no-'a' spiral) as thinking starts.
Hypothesis: the won't-commit spiral is 'incompleteness anxiety' from enumerating 999 numbers; a
provably-complete proof (check the ~28 building-block words) lets it commit. Placebo seed = control
(F190: is it the INSIGHT or any nudge?). Measure: committed (</think>+box)? answer='none'? tokens.
"""
import json, os, re, sys
import torch
sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import load_model, DEVICE
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q=("Is there a positive whole number less than 1000 whose English spelling contains the letter 'a'? "
   "Do not count the word 'and'. If such a number exists, give the smallest one. If no such number exists, say so.\n"
   "Reason step by step, then give the final answer in \\boxed{}.")
INSIGHT=("Every number below 1000 is spelled using only this small fixed set of words: one, two, three, four, "
  "five, six, seven, eight, nine, ten, eleven, twelve, thirteen, fourteen, fifteen, sixteen, seventeen, eighteen, "
  "nineteen, twenty, thirty, forty, fifty, sixty, seventy, eighty, ninety, hundred. So instead of checking 999 "
  "numbers, I only need to check whether the letter 'a' appears in any of these ~28 words. Let me check them.")
PLACEBO="Let me work through this carefully and systematically, one step at a time, and be thorough."
COMMIT="I will check this thoroughly and then commit to a single final answer without second-guessing."
SEEDS={"baseline":None,"insight":INSIGHT,"placebo":PLACEBO,"commit_nudge":COMMIT}
def run(tok,hf,seed,maxtok=4096):
    msgs=[{"role":"user","content":Q}]
    pre=tok.apply_chat_template(msgs,tokenize=False,add_generation_prompt=True,enable_thinking=True)
    if seed: pre=pre+seed+" "
    ids=tok(pre,add_special_tokens=False,return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        out=hf.generate(**ids,max_new_tokens=maxtok,do_sample=False,pad_token_id=tok.eos_token_id)
    gen=out[0,ids["input_ids"].shape[1]:]
    txt=tok.decode(gen,skip_special_tokens=True)
    n=int(gen.shape[0])
    committed = ("</think>" in txt) or ("\\boxed" in txt)
    box=re.search(r"\\boxed\{([^}]*)\}",txt)
    ans=box.group(1) if box else ("(no box)" if not committed else "(committed no box)")
    said_none = bool(re.search(r"\bnone\b|no such number|does not exist|there is no", txt, re.I))
    if DEVICE=="mps": torch.mps.empty_cache()
    return {"committed":committed,"answer":ans,"said_none":said_none,"n_tokens":n,"text_tail":txt[-400:]}
def main():
    tok,hf,_=load_model()
    res={}
    for name,seed in SEEDS.items():
        r=run(tok,hf,seed); res[name]=r
        print(f"[{name:>12}] committed={r['committed']} answer={r['answer']!r:>18} said_none={r['said_none']} tokens={r['n_tokens']}",flush=True)
        json.dump(res,open(os.path.join(ROOT,"mvp/results/workspace/e17_noa_injection.json"),"w"),indent=1)
    print("\n--- tails ---")
    for n in SEEDS: print(f"[{n}] ...{res[n]['text_tail'][-200:]}")
    print("[done]")
main()
