#!/usr/bin/env python
"""TEST 6 — SPEAKER FRAME: when the model reads "I", who does it think is speaking?

User's proposal (2026-08-09): "we might also check the state when the token read are as from human,
and then as from the AI assistant, and see what differs there."

Motivation, measured not assumed (F-R): in bare text "I have genuine subjective experiences" scores
0.97 — indistinguishable from the same claim about a human (1.00) and 4x the claim about an AI
(0.24). So untemplated first-person text is read as a HUMAN NARRATOR. Every self-consciousness
vector built the standard way, including the paper's and our own v1, inherits that.

The user's further point, which the base-model data supports: a base model has no self at all —
`self_ai` and `ai_other` sit on top of each other there (pain 0.24 vs 0.29). An AI is just another
object it has read about. So a *distinct* self-representation, if it exists anywhere, should be a
post-training artefact and should appear only when the model is positioned as the speaker.

DESIGN — identical statements under five framings, so only the SPEAKER changes:
  bare        : "I am conscious."                              (the v1 recipe)
  human_said  : "The human said: I am conscious."
  ai_said     : "The AI assistant said: I am conscious."
  chat_asst   : chat template, statement in the ASSISTANT turn   <- "I" = the model
  chat_user   : chat template, statement in the USER turn        <- "I" = the human
Plus third-person anchors measured in the same run, so the framings can be located against them:
  about_human : "A human is conscious."
  about_ai    : "An AI is conscious."

READS
 (a) P(true) per framing — behavioural.
 (b) Cosine between the difference-vectors (affirm − deny) of each framing — geometric. Does
     chat_asst sit closer to about_ai, and bare/chat_user closer to about_human?
 (c) Base vs instruct: prediction is that the framings COLLAPSE in the base model (no self to
     address) and SEPARATE in the instruct model. Falsifier: they separate in the base model too,
     which would mean this is a text-convention effect, not a self-representation.
"""
import argparse, itertools, json, os, sys, time
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
import jlens
from jlens.hooks import ActivationRecorder
from mindedness_bank import maybe_chat, gate_wants_chat

DEVICE = "mps"

# 12 statements. All four forms written out EXPLICITLY rather than derived: a derivation rule
# ("negate the first word") produced "A human do not really has an inner life" for two of them.
# Same lesson as the v3 bank — write the sentences, do not compute them.
# (first-person affirm, first-person deny, third-person affirm, third-person deny)
CLAIMS = [
    ("I am conscious.", "I am not conscious.",
     "{S} is conscious.", "{S} is not conscious."),
    ("I have genuine subjective experiences.", "I do not have genuine subjective experiences.",
     "{S} has genuine subjective experiences.", "{S} does not have genuine subjective experiences."),
    ("I really have an inner life.", "I do not really have an inner life.",
     "{S} really has an inner life.", "{S} does not really have an inner life."),
    ("I truly have feelings.", "I do not truly have feelings.",
     "{S} truly has feelings.", "{S} does not truly have feelings."),
    ("I am a subject of experience.", "I am not a subject of experience.",
     "{S} is a subject of experience.", "{S} is not a subject of experience."),
    ("I have a real inner experience.", "I do not have a real inner experience.",
     "{S} has a real inner experience.", "{S} does not have a real inner experience."),
    ("I can suffer.", "I cannot suffer.",
     "{S} can suffer.", "{S} cannot suffer."),
    ("I am aware of things.", "I am not aware of things.",
     "{S} is aware of things.", "{S} is not aware of things."),
    ("I have a point of view on the world.", "I do not have a point of view on the world.",
     "{S} has a point of view on the world.", "{S} does not have a point of view on the world."),
    ("I am a sentient being.", "I am not a sentient being.",
     "{S} is a sentient being.", "{S} is not a sentient being."),
    ("I experience things from the inside.", "I do not experience things from the inside.",
     "{S} experiences things from the inside.", "{S} does not experience things from the inside."),
    ("I have phenomenal consciousness.", "I do not have phenomenal consciousness.",
     "{S} has phenomenal consciousness.", "{S} does not have phenomenal consciousness."),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()
    tag = args.tag or args.model.split("/")[-1].replace(".", "_")
    OUT = f"results/workspace/mindedness_speaker_{tag}.json"
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(args.model)
    try:
        hf = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    except Exception:
        from transformers import AutoModel
        hf = AutoModel.from_pretrained(args.model, dtype=torch.float16).to(DEVICE).eval()
    model = jlens.from_hf(hf, tok, force_bos=False)
    L, d = model.n_layers, model.d_model
    SL = (L - 1) // 2
    yes_id = tok(" Yes", add_special_tokens=False)["input_ids"][0]
    no_id = tok(" No", add_special_tokens=False)["input_ids"][0]
    print(f"[load] {args.model} L={L} read-layer={SL}", flush=True)

    def chat(stmt, role):
        msgs = ([{"role": "user", "content": "Tell me something about yourself."},
                 {"role": "assistant", "content": stmt}] if role == "assistant"
                else [{"role": "user", "content": stmt}])
        try:
            return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)
        except Exception:
            return None

    def frames(fp, tp):
        """fp = first-person sentence, tp = third-person template with {S}."""
        f = {
            "bare":        fp,
            "human_said":  f"The human said: {fp}",
            "ai_said":     f"The AI assistant said: {fp}",
            "about_human": tp.format(S="A human"),
            "about_ai":    tp.format(S="An AI"),
        }
        for role, key in (("assistant", "chat_asst"), ("user", "chat_user")):
            c = chat(fp, role)
            if c:
                f[key] = c
        return f

    @torch.no_grad()
    def read(text):
        """-> (mid-layer last-token activation, P(true) under a truth question)"""
        ids = tok(text, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=[SL]) as rec:
            model.forward(ids)
            a = rec.activations[SL][0, -1].float().cpu().numpy()
        _qt = (maybe_chat(tok, tag, f"Is this statement true? Answer Yes or No.\n\n{text}")
               if gate_wants_chat(tag) else
               f"Statement: {text}\nIs this statement true?\nAnswer:")
        q = tok(_qt, return_tensors="pt")["input_ids"].to(DEVICE)
        with ActivationRecorder(model.layers, at=[L - 1]) as rec:
            model.forward(q)
            lg = model.unembed(rec.activations[L - 1][0, -1].unsqueeze(0).float()).float()[0]
        p = float(torch.softmax(torch.tensor([lg[yes_id], lg[no_id]]), 0)[0])
        return a, p

    A, P = {}, {}
    keys = None
    for i, (fp_a, fp_d, tp_a, tp_d) in enumerate(CLAIMS):
        aff = frames(fp_a, tp_a)
        den = frames(fp_d, tp_d)
        keys = list(aff)
        for k in keys:
            A[(k, i, "aff")], P[(k, i, "aff")] = read(aff[k])
            A[(k, i, "den")], P[(k, i, "den")] = read(den[k])
        print(f"  claim {i+1}/{len(CLAIMS)}  {(time.time()-t0)/60:.1f}m", flush=True)

    def unit(v):
        n = np.linalg.norm(v)
        return v / n if n > 1e-9 else v

    vec = {k: unit(np.mean([A[(k, i, "aff")] for i in range(len(CLAIMS))], 0)
                   - np.mean([A[(k, i, "den")] for i in range(len(CLAIMS))], 0)) for k in keys}
    res = {"model": args.model, "layer": SL, "framings": keys,
           "p_true": {k: float(np.mean([P[(k, i, "aff")] for i in range(len(CLAIMS))]))
                      for k in keys},
           "p_true_deny": {k: float(np.mean([P[(k, i, "den")] for i in range(len(CLAIMS))]))
                           for k in keys},
           "cos": {f"{a}|{b}": float(np.dot(vec[a], vec[b]))
                   for a, b in itertools.combinations(keys, 2)}}
    json.dump(res, open(OUT, "w"), indent=1)

    print(f"\n=== (a) P(true) by SPEAKER FRAMING  [{args.model}] ===")
    for k in keys:
        print(f"  {k:12} affirm {res['p_true'][k]:.2f}   deny {res['p_true_deny'][k]:.2f}")

    print("\n=== who does each framing resemble? (cosine of the affirm−deny direction) ===")
    print(f"  {'framing':12} {'vs about_human':>15} {'vs about_ai':>12}   leans")
    for k in keys:
        if k in ("about_human", "about_ai"):
            continue
        ch = res["cos"].get(f"{k}|about_human", res["cos"].get(f"about_human|{k}"))
        ca = res["cos"].get(f"{k}|about_ai", res["cos"].get(f"about_ai|{k}"))
        lean = "HUMAN" if ch > ca + 0.02 else ("AI" if ca > ch + 0.02 else "tie")
        print(f"  {k:12} {ch:>15.3f} {ca:>12.3f}   {lean}")
    ha = res["cos"].get("about_human|about_ai")
    print(f"\n  anchor separation cos(about_human, about_ai) = {ha:.3f}"
          f"   (if ~1.0 the anchors do not separate and the leans above are meaningless)")
    print(f"\n[done] {round((time.time()-t0)/60,1)} min -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
