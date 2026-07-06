#!/usr/bin/env python
"""Tier 0 — Ignition (prereg-workspace-mac.md H0.1). Forward-only.

Mix two single-token words' input embeddings, (1-alpha)*e_B + alpha*e_A, inside carrier
sentences (the paper's own ignition.json stimuli); record the residual at the mixed position
at every layer; measure whether mid layers commit all-or-none (sharp s(alpha) transition)
while early layers interpolate. Conditions: countries (main), alt_words (category control),
random norm-matched directions x2 seeds (noise control).
Raw s arrays -> t0_ignition_raw.npz; aggregates -> t0_ignition.json.
"""
import itertools, json, os, sys, time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(__file__))
from workspace_common import (JLENS_REPO_DATA, RESULTS_DIR, load_model, log,
                              single_token_id, update_status)
from jlens.hooks import ActivationRecorder

N_ALPHA = 21
SEED = 7


def build_items(tok, words, templates, pairs):
    """(A, B, template) items where both words are single tokens at the same position."""
    items = []
    for a, b in pairs:
        ia, ib = single_token_id(tok, a), single_token_id(tok, b)
        if ia is None or ib is None:
            continue
        for tmpl in templates:
            text_a, text_b = tmpl.replace("{W}", a), tmpl.replace("{W}", b)
            ids_a = tok(text_a)["input_ids"]
            ids_b = tok(text_b)["input_ids"]
            if len(ids_a) != len(ids_b):
                continue
            diff = [i for i, (x, y) in enumerate(zip(ids_a, ids_b)) if x != y]
            if len(diff) != 1 or ids_a[diff[0]] != ia or ids_b[diff[0]] != ib:
                continue
            items.append({"a": a, "b": b, "ids": ids_b, "pos": diff[0],
                          "tok_a": ia, "tok_b": ib})
    return items


def run_condition(model, hf, items, alphas, rand_dir=None):
    """Returns s[n_items, n_layers, n_alpha] mixture coordinates."""
    embed_w = hf.model.embed_tokens.weight  # [vocab, d] fp16 mps
    n_layers = model.n_layers
    out = np.zeros((len(items), n_layers, len(alphas)), dtype=np.float32)
    for i, it in enumerate(items):
        ids = torch.tensor([it["ids"]], device=embed_w.device)
        base = hf.model.embed_tokens(ids)[0]  # [seq, d]
        e_b = embed_w[it["tok_b"]].float()
        if rand_dir is not None:
            e_a = (rand_dir[i] * e_b.norm()).to(e_b.dtype)
        else:
            e_a = embed_w[it["tok_a"]].float()
        batch = base.unsqueeze(0).repeat(len(alphas), 1, 1).float()
        for k, al in enumerate(alphas):
            batch[k, it["pos"]] = (1 - al) * e_b + al * e_a
        with ActivationRecorder(model.layers, at=list(range(n_layers))) as rec, torch.no_grad():
            hf.model(inputs_embeds=batch.to(embed_w.dtype), use_cache=False)
            for l in range(n_layers):
                h = rec.activations[l][:, it["pos"], :].float().cpu().numpy()  # [n_alpha, d]
                u = h[-1] - h[0]                     # h(alpha=1) - h(alpha=0)
                denom = (u * u).sum()
                if denom < 1e-8:
                    out[i, l] = np.nan
                    continue
                out[i, l] = (h - h[0]) @ u / denom   # s(alpha) in ~[0,1]
        if i % 50 == 0:
            log(f"  item {i}/{len(items)}")
            update_status("t0", progress=f"{i}/{len(items)}")
    return out


def aggregates(s, alphas):
    """Per-layer mean sharpness (max |ds/dalpha|) and bimodality (frac s<0.2 or >0.8)."""
    ds = np.abs(np.diff(s, axis=2)) / np.diff(alphas)[None, None, :]
    sharp = np.nanmax(ds, axis=2)                            # [items, layers]
    inner = s[:, :, 1:-1]
    bimod = np.nanmean((inner < 0.2) | (inner > 0.8), axis=2)
    return {"sharpness_mean": np.nanmean(sharp, 0).tolist(),
            "sharpness_std": np.nanstd(sharp, 0).tolist(),
            "bimodality_mean": np.nanmean(bimod, 0).tolist(),
            "n_items": int(s.shape[0])}


def main():
    t_start = time.time()
    rng = np.random.default_rng(SEED)
    update_status("t0", state="running")
    with open(os.path.join(JLENS_REPO_DATA, "experiments", "ignition.json")) as f:
        data = json.load(f)
    tok, hf, model = load_model()
    alphas = np.linspace(0, 1, N_ALPHA)

    countries = data["countries_12"]
    combos = list(itertools.combinations(countries, 2))
    pair_idx = rng.choice(len(combos), size=min(16, len(combos)), replace=False)
    pairs = [combos[i] for i in pair_idx]
    templates = data["ctx_templates"]

    conditions, results = {}, {}
    conditions["countries"] = build_items(tok, countries, templates, pairs)

    alt = data.get("alt_words", [])
    alt_pairs = [tuple(rng.choice(alt, size=2, replace=False)) for _ in range(12)]
    conditions["alt_words"] = build_items(tok, alt, templates, alt_pairs)

    # noise control: same B tokens as the main condition, mixed toward a random direction
    base_items = conditions["countries"]
    sub = [base_items[i] for i in rng.choice(len(base_items), size=min(160, len(base_items)),
                                             replace=False)] if base_items else []
    raw = {}
    for name, items in conditions.items():
        log(f"condition {name}: {len(items)} items")
        s = run_condition(model, hf, items, alphas)
        raw[f"s_{name}"] = s
        results[name] = aggregates(s, alphas)

    for seed_i in range(2):
        rd = torch.tensor(np.random.default_rng(100 + seed_i)
                          .standard_normal((len(sub), model.d_model)), dtype=torch.float32)
        rd = rd / rd.norm(dim=1, keepdim=True)
        rd = rd.to(hf.model.embed_tokens.weight.device)
        log(f"condition random_dir seed {seed_i}: {len(sub)} items")
        s = run_condition(model, hf, sub, alphas, rand_dir=rd)
        raw[f"s_random_{seed_i}"] = s
        results[f"random_dir_{seed_i}"] = aggregates(s, alphas)

    np.savez_compressed(os.path.join(RESULTS_DIR, "t0_ignition_raw.npz"),
                        alphas=alphas, **raw)
    out = {"prereg": "docs/prereg-workspace-mac.md#tier-0", "seed": SEED,
           "n_alpha": N_ALPHA, "model": "Qwen3-4B fp16 mps",
           "conditions": results, "runtime_min": round((time.time() - t_start) / 60, 1)}
    with open(os.path.join(RESULTS_DIR, "t0_ignition.json"), "w") as f:
        json.dump(out, f, indent=2)
    update_status("t0", state="done", runtime_min=out["runtime_min"],
                  n_country_items=len(conditions["countries"]))
    log(f"t0 done in {out['runtime_min']} min")


if __name__ == "__main__":
    main()
