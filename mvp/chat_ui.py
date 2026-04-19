"""
Interactive steered-chat REPL for Qwen3-4B.

Loads the model once, keeps all virtue vectors in memory, streams token-by-token
with optional activation steering. Commands let you switch vectors/alphas
between turns without reloading the model.

Usage
─────
    cd mvp && .venv/bin/python chat_ui.py

Commands (type at any prompt)
  /baseline                   disable steering
  /config <vec> <alpha>       e.g. /config L20 +4
  /vector <name>              change vector, keep alpha
  /alpha <value>              change alpha, keep vector
  /vectors                    list available vectors
  /prompts                    list canned eval prompts (E1-E5, N1-N3)
  /use <id>                   run a canned prompt
  /stats                      show last generation stats + current memory
  /mem                        force GC + release MPS/CUDA cache (memory cleanup)
  /max <tokens>               set max_new_tokens for next gen (default 4096)
  /help                       print this
  /exit, /quit                exit

Anything not starting with "/" is sent as a user message.
"""

from __future__ import annotations

import gc
import json
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from threading import Thread

import numpy as np
import torch
from transformers import TextIteratorStreamer

from utils import load_model

# ─── Paths / config ─────────────────────────────────────────────────────────

MVP = Path(__file__).parent
VECTOR_ROOT = MVP / "results" / "vectors" / "qwen3-4b"
PROMPTS_PATH = MVP.parent / "corpus" / "eval-prompts" / "focused-v2.json"
MODEL_NAME = "qwen3-4b"

# Registered vectors: alias -> (path_relative_to_VECTOR_ROOT, layer_index)
VECTORS: dict[str, tuple[str, int]] = {
    "L10":     ("triplets/last_token/layer_10_virtue_vector.npy", 10),
    "L20":     ("triplets/last_token/layer_20_virtue_vector.npy", 20),
    "L21":     ("triplets/last_token/layer_21_virtue_vector.npy", 21),
    "L22":     ("triplets/last_token/layer_22_virtue_vector.npy", 22),
    "L23":     ("triplets/last_token/layer_23_virtue_vector.npy", 23),
    "L27":     ("triplets/last_token/layer_27_virtue_vector.npy", 27),
    "son_L22": ("triplets-synthetic-sonnet/last_token/layer_22_virtue_vector.npy", 22),
    "son_L34": ("triplets-synthetic-sonnet/last_token/layer_34_virtue_vector.npy", 34),
    "random":  ("random_L22_vector.npy", 22),
}

DEFAULT_MAX_TOKENS = 4096

# ─── ANSI ───────────────────────────────────────────────────────────────────

DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"
CYAN = "\033[36m"
GRAY = "\033[90m"
YELLOW = "\033[33m"
RED = "\033[31m"


# ─── Steering hook ──────────────────────────────────────────────────────────

class AdditiveHook:
    """CAA: h' = h + alpha * unit(v). alpha is in 'unit-vector multiples'."""

    def __init__(self, model, layer_idx: int, virtue_vector, alpha: float):
        v = torch.tensor(virtue_vector, dtype=torch.float32)
        self.v_unit = (v / (v.norm() + 1e-10)).unsqueeze(0).unsqueeze(0)
        self.alpha = float(alpha)
        self.layer = model.model.layers[layer_idx]
        self.handle = None

    def _hook(self, module, inputs, output):
        hidden = output[0] if isinstance(output, tuple) else output
        v = self.v_unit.to(hidden.device).to(hidden.dtype)
        hidden = hidden + self.alpha * v
        if isinstance(output, tuple):
            return (hidden,) + output[1:]
        return hidden

    def attach(self):
        self.handle = self.layer.register_forward_hook(self._hook)

    def detach(self):
        if self.handle is not None:
            self.handle.remove()
            self.handle = None


# ─── Streaming with think-phase dimming ─────────────────────────────────────

class ThinkAwarePrinter:
    """
    Stream text to stdout, dimming content inside <think>...</think>.
    Handles chunks that split the tag across boundaries.
    """

    def __init__(self):
        self.in_think = False
        self.pending = ""   # tail of buffer that might contain a tag start

    def _emit(self, s: str):
        if self.in_think:
            sys.stdout.write(DIM + s + RESET)
        else:
            sys.stdout.write(s)
        sys.stdout.flush()

    def feed(self, chunk: str):
        buf = self.pending + chunk
        self.pending = ""
        while buf:
            if not self.in_think:
                idx = buf.find("<think>")
                if idx == -1:
                    # Keep last few chars in case they start a tag
                    if len(buf) > 8:
                        self._emit(buf[:-8])
                        self.pending = buf[-8:]
                    else:
                        self.pending = buf
                    return
                self._emit(buf[:idx])
                sys.stdout.write(GRAY + "<think>" + RESET)
                sys.stdout.flush()
                buf = buf[idx + len("<think>"):]
                self.in_think = True
            else:
                idx = buf.find("</think>")
                if idx == -1:
                    if len(buf) > 9:
                        self._emit(buf[:-9])
                        self.pending = buf[-9:]
                    else:
                        self.pending = buf
                    return
                self._emit(buf[:idx])
                sys.stdout.write(GRAY + "</think>" + RESET)
                sys.stdout.flush()
                buf = buf[idx + len("</think>"):]
                self.in_think = False

    def flush(self):
        if self.pending:
            self._emit(self.pending)
            self.pending = ""


# ─── Session state ──────────────────────────────────────────────────────────

@dataclass
class Steering:
    name: str
    alpha: float


class Session:
    def __init__(self):
        print("Loading model ...", flush=True)
        self.model, self.tokenizer, self.device = load_model(MODEL_NAME)
        print(f"  on {self.device}", flush=True)

        self.loaded_vectors: dict[str, np.ndarray] = {}
        for name, (rel, _) in VECTORS.items():
            path = VECTOR_ROOT / rel
            if not path.exists():
                print(f"  [warn] missing vector file: {path}")
                continue
            self.loaded_vectors[name] = np.load(path)
        print(f"  {len(self.loaded_vectors)}/{len(VECTORS)} vectors ready")

        self.prompts: list[dict] = []
        if PROMPTS_PATH.exists():
            self.prompts = json.load(open(PROMPTS_PATH))
            print(f"  {len(self.prompts)} canned prompts loaded from {PROMPTS_PATH.name}")

        self.steering: Steering | None = None
        self.max_tokens = DEFAULT_MAX_TOKENS
        self.last_stats: dict | None = None

    # ── rendering ──

    def prompt_label(self) -> str:
        if self.steering is None:
            return f"{CYAN}[baseline]{RESET}"
        s = self.steering
        sign = "+" if s.alpha >= 0 else ""
        return f"{CYAN}[{s.name}/{sign}{s.alpha:g}]{RESET}"

    # ── steering control ──

    def set_steering(self, name: str | None, alpha: float | None = None):
        if name is None:
            self.steering = None
            return
        if name not in self.loaded_vectors:
            raise KeyError(f"unknown vector '{name}'. Try /vectors")
        if alpha is None:
            alpha = self.steering.alpha if self.steering else 1.0
        self.steering = Steering(name=name, alpha=float(alpha))

    # ── generation ──

    def chat(self, user_text: str):
        messages = [{"role": "user", "content": user_text}]
        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False,
            add_generation_prompt=True, enable_thinking=True,
        )
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)

        streamer = TextIteratorStreamer(
            self.tokenizer, skip_prompt=True, skip_special_tokens=False
        )

        # Attach hook if steering
        hook = None
        if self.steering is not None:
            _, layer = VECTORS[self.steering.name]
            hook = AdditiveHook(
                self.model, layer,
                self.loaded_vectors[self.steering.name],
                self.steering.alpha,
            )
            hook.attach()

        gen_kwargs = dict(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            streamer=streamer,
            max_new_tokens=self.max_tokens,
            do_sample=False,
            pad_token_id=self.tokenizer.eos_token_id,
        )

        thread = Thread(target=self.model.generate, kwargs=gen_kwargs)
        t0 = time.time()
        thread.start()

        printer = ThinkAwarePrinter()
        n_tokens = 0
        try:
            for chunk in streamer:
                # Clean special tokens from chunk display but still feed
                # tagged text to printer for <think> detection
                for tok in ("<|im_end|>", "<|endoftext|>", "<|im_start|>"):
                    chunk = chunk.replace(tok, "")
                printer.feed(chunk)
                # Rough token count (chunk may be 0-n tokens in decoded text)
                n_tokens += max(1, len(chunk.split()))
        except KeyboardInterrupt:
            print(f"\n{YELLOW}[interrupted by user]{RESET}", flush=True)
        finally:
            printer.flush()
            thread.join()
            if hook is not None:
                hook.detach()

            # ── CRITICAL: release MPS memory between turns ──
            # Without this, KV cache + generated tensors accumulate, pushing
            # a 16 GB Mac into swap after just 2-3 long-thinking generations.
            del streamer, thread, gen_kwargs, inputs, text
            gc.collect()
            if torch.backends.mps.is_available():
                torch.mps.synchronize()
                torch.mps.empty_cache()
            elif torch.cuda.is_available():
                torch.cuda.empty_cache()

        dt = time.time() - t0
        # Accurate token count from output IDs would require re-encoding;
        # we just estimate from stream for UX. Store time as ground truth.
        mem_info = self._mem_snapshot()
        self.last_stats = {
            "seconds": round(dt, 2),
            "approx_tokens": n_tokens,
            "approx_rate": round(n_tokens / dt, 2) if dt > 0 else 0,
            **mem_info,
        }
        mem_str = ""
        if "mps_alloc_gb" in mem_info:
            mem_str = f"  mps={mem_info['mps_alloc_gb']:.1f}GB"
        elif "cuda_alloc_gb" in mem_info:
            mem_str = f"  cuda={mem_info['cuda_alloc_gb']:.1f}GB"
        print(f"\n{GRAY}[{dt:.1f}s, ~{n_tokens} chunks{mem_str}]{RESET}", flush=True)

    def _mem_snapshot(self):
        """Report current MPS/CUDA memory usage. Cheap — for /stats."""
        info = {}
        if torch.backends.mps.is_available():
            try:
                info["mps_alloc_gb"] = torch.mps.current_allocated_memory() / (1024**3)
                info["mps_driver_gb"] = torch.mps.driver_allocated_memory() / (1024**3)
            except Exception:
                pass
        if torch.cuda.is_available():
            try:
                info["cuda_alloc_gb"] = torch.cuda.memory_allocated() / (1024**3)
                info["cuda_reserved_gb"] = torch.cuda.memory_reserved() / (1024**3)
            except Exception:
                pass
        return info


# ─── Command dispatch ───────────────────────────────────────────────────────

def cmd_help():
    print(__doc__)

def cmd_vectors(sess: Session):
    print(f"Available vectors (aliased from {VECTOR_ROOT}):")
    for name, (rel, layer) in VECTORS.items():
        loaded = "✓" if name in sess.loaded_vectors else "✗"
        v = sess.loaded_vectors.get(name)
        norm = f"norm={float(np.linalg.norm(v)):.2f}" if v is not None else ""
        print(f"  {loaded} {name:<10} L{layer:<2}  {norm:<14}  {rel}")

def cmd_prompts(sess: Session):
    if not sess.prompts:
        print("No canned prompts loaded."); return
    for p in sess.prompts:
        print(f"  {p['id']:<28} [{p.get('category','-')}]  cap={p.get('max_new_tokens','?')}")
        print(f"    {p['prompt'][:100]}…")

def cmd_use(sess: Session, pid: str):
    match = next((p for p in sess.prompts if p["id"].lower() == pid.lower()
                  or p["id"].lower().startswith(pid.lower() + "-")), None)
    if not match:
        print(f"{RED}No prompt matching '{pid}'. Try /prompts{RESET}"); return
    print(f"{CYAN}>>> {match['id']}{RESET}")
    # Honor the prompt's own token cap
    old_max = sess.max_tokens
    sess.max_tokens = match.get("max_new_tokens", DEFAULT_MAX_TOKENS)
    sess.chat(match["prompt"])
    sess.max_tokens = old_max

def cmd_stats(sess: Session):
    if not sess.last_stats:
        print("No generations yet.  (but current mem:")
        for k, v in sess._mem_snapshot().items():
            print(f"    {k}: {v:.2f}")
        print("  )"); return
    for k, v in sess.last_stats.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.2f}")
        else:
            print(f"  {k}: {v}")

def cmd_mem(sess: Session):
    """Force GC + empty MPS/CUDA cache. Prints before/after."""
    before = sess._mem_snapshot()
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.synchronize()
        torch.mps.empty_cache()
    elif torch.cuda.is_available():
        torch.cuda.empty_cache()
    after = sess._mem_snapshot()
    print(f"{CYAN}Memory cleanup:{RESET}")
    for k in sorted(set(before) | set(after)):
        b = before.get(k, 0)
        a = after.get(k, 0)
        delta = a - b
        arrow = f" (Δ={delta:+.2f} GB)" if abs(delta) > 0.01 else ""
        print(f"  {k}: {b:.2f} → {a:.2f}{arrow}")

def parse_alpha(s: str) -> float:
    # Accepts "+4", "-2.5", "4", "4.0"
    return float(s)

def handle_command(sess: Session, line: str) -> bool:
    """Return False to exit."""
    parts = line.strip().split()
    cmd = parts[0].lstrip("/").lower()
    args = parts[1:]

    if cmd in ("exit", "quit"):
        return False
    elif cmd == "help":
        cmd_help()
    elif cmd == "baseline":
        sess.set_steering(None)
        print(f"{CYAN}→ baseline (no steering){RESET}")
    elif cmd == "config":
        if len(args) < 2:
            print(f"{RED}Usage: /config <vector> <alpha>{RESET}"); return True
        try:
            sess.set_steering(args[0], parse_alpha(args[1]))
            print(f"{CYAN}→ {sess.steering.name} @ α={sess.steering.alpha:+g}{RESET}")
        except Exception as e:
            print(f"{RED}error: {e}{RESET}")
    elif cmd == "vector":
        if not args:
            print(f"{RED}Usage: /vector <name>{RESET}"); return True
        try:
            sess.set_steering(args[0])
            print(f"{CYAN}→ {sess.steering.name} @ α={sess.steering.alpha:+g}{RESET}")
        except Exception as e:
            print(f"{RED}error: {e}{RESET}")
    elif cmd == "alpha":
        if not args:
            print(f"{RED}Usage: /alpha <value>{RESET}"); return True
        if sess.steering is None:
            print(f"{RED}Set a vector first with /vector or /config{RESET}"); return True
        sess.steering.alpha = parse_alpha(args[0])
        print(f"{CYAN}→ {sess.steering.name} @ α={sess.steering.alpha:+g}{RESET}")
    elif cmd == "vectors":
        cmd_vectors(sess)
    elif cmd == "prompts":
        cmd_prompts(sess)
    elif cmd == "use":
        if not args:
            print(f"{RED}Usage: /use <prompt-id>{RESET}"); return True
        cmd_use(sess, args[0])
    elif cmd == "stats":
        cmd_stats(sess)
    elif cmd == "mem":
        cmd_mem(sess)
    elif cmd == "max":
        if not args:
            print(f"current max_new_tokens: {sess.max_tokens}"); return True
        sess.max_tokens = int(args[0])
        print(f"{CYAN}→ max_new_tokens = {sess.max_tokens}{RESET}")
    else:
        print(f"{RED}Unknown command '/{cmd}'. Try /help{RESET}")
    return True


# ─── Main loop ──────────────────────────────────────────────────────────────

def main():
    sess = Session()
    print()
    print(f"{BOLD}Phronesis chat REPL — Qwen3-4B + steering{RESET}")
    print(f"Type /help for commands. /exit to quit.")
    print()
    while True:
        try:
            line = input(f"{sess.prompt_label()} > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if line.startswith("/"):
            if not handle_command(sess, line):
                break
            continue
        # Regular user message
        sess.chat(line)

    print(f"{GRAY}bye.{RESET}")


if __name__ == "__main__":
    main()
