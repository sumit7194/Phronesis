"""Architecture probe for Qwen3.5-4B (MoE + multimodal). Runs on CPU so it can
run alongside a GPU job. Tells us: which loader class works, the decoder-layer
module path (for the steering hook + extraction), layer count/type, and that
text-only chat generation + <think> work. Output drives the MODEL_CONFIGS entry.
"""
import torch
import torch.nn as nn
import transformers
from transformers import AutoConfig, AutoTokenizer

MID = "Qwen/Qwen3.5-4B"

cfg = AutoConfig.from_pretrained(MID, trust_remote_code=True)
print("CONFIG_CLASS:", type(cfg).__name__, "| archs:", getattr(cfg, "architectures", None))
print("num_hidden_layers:", getattr(cfg, "num_hidden_layers", None),
      "| hidden_size:", getattr(cfg, "hidden_size", None),
      "| has text_config:", hasattr(cfg, "text_config"))
if hasattr(cfg, "text_config"):
    tc = cfg.text_config
    print("  text_config.num_hidden_layers:", getattr(tc, "num_hidden_layers", None),
          "| text_config.hidden_size:", getattr(tc, "hidden_size", None))

model = None
used = None
for ln in ["AutoModelForCausalLM", "AutoModelForImageTextToText", "AutoModel"]:
    try:
        model = getattr(transformers, ln).from_pretrained(
            MID, torch_dtype=torch.bfloat16, trust_remote_code=True, device_map="cuda"
        )
        used = ln
        print("LOADED_WITH:", ln)
        break
    except Exception as e:
        print("LOADFAIL", ln, type(e).__name__, str(e)[:160])

if model is not None:
    def walk(m, pre=""):
        for n, c in m.named_children():
            f = pre + "." + n if pre else n
            if isinstance(c, nn.ModuleList) and len(c) >= 8:
                print("DECODER_LAYERS_PATH:", f, "| n=", len(c), "| block=", type(c[0]).__name__)
            walk(c, f)
    walk(model)
    try:
        tok = AutoTokenizer.from_pretrained(MID, trust_remote_code=True)
        msgs = [{"role": "user", "content": "What is the capital of France? Answer in one word."}]
        t = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        print("CHAT_TEMPLATE_OK len=", len(t), "| has_think_tag:", "<think>" in t.lower())
        ids = tok(t, return_tensors="pt").to(model.device)
        out = model.generate(**ids, max_new_tokens=24, do_sample=False)
        print("GEN:", repr(tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True)[:160]))
    except Exception as e:
        print("GENFAIL", type(e).__name__, str(e)[:180])
