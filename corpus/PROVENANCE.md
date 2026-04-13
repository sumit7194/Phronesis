# Corpus Generation Provenance

## Fact packs (scenario design)

| Slots | Generator | Notes |
|---|---|---|
| 1-10 | Claude Opus 4.6 | Pilot queue, full manual curation with detailed generator notes |
| 11-50 | Claude Sonnet 4.6 | Extended queue, autonomous cron-based generation |
| 51-100 | Claude Opus 4.6 | Scale queue, single-session generation (2026-04-11) |

## Triplet passages (neutral / virtuous / non-virtuous)

| Corpus | Slots | Passage generator | Notes |
|---|---|---|---|
| Hand-crafted (`triplets/`) | 1-~13 | Claude Opus 4.6 | Direct writing with self-review |
| Hand-crafted (`triplets/`) | ~14-50 | Claude Sonnet 4.6 | Autonomous cron with self-review |
| Synthetic pilot (`triplets-synthetic-gemma/`) | 1-10 | Gemma-2-2b-it | Self-generation experiment |
| Synthetic pilot (`triplets-synthetic-qwen/`) | 1-10 | Qwen-2.5-3B | Cross-model experiment |
| Synthetic pilot (`triplets-synthetic-chatgpt/`) | 16 packs | ChatGPT | Best synthetic quality — 91-94% probe, correct direction |
| Synthetic full (`triplets-synthetic-gemma-all/`) | 1-100 | Gemma-2-2b-it | ⚠ INVERTED vectors — V≈N (84% Jaccard), unusable for steering |
| Synthetic full (`triplets-synthetic-sonnet/`) | 1-100 | Claude Sonnet 4.6 | Correct direction, 75-98% probe depending on model/layer |
| Synthetic full (`triplets-synthetic-gemini/`) | 1-100 | Gemini 2.5 Flash | ⚠ INVERTED vectors — N is quasi-virtuous (Leaky N), unusable |

## Extraction results — full sweep (2026-04-13)

| Corpus | Extractor | Method | Best Layer | Probe | Separation | Direction |
|---|---|---|---|---|---|---|
| Hand-crafted (50) | Gemma-2-2B | comprehension | L13 | 94% | +5.4 | ✅ correct |
| Hand-crafted (50) | Gemma-2-2B | last_token | L17 | 94% | +18.8 | ✅ correct |
| ChatGPT (16) | Gemma-2-2B | comprehension | L8 | 97% | +1.3 | ✅ correct |
| Sonnet (100) | Gemma-2-2B | comprehension | L14 | 98% | +4.7 | ✅ correct |
| Sonnet (100) | Gemma-2-2B | last_token | L12 | 96% | +9.5 | ✅ correct |
| Hand-crafted (50) | Qwen-2.5-3B | comprehension | L24 | 95% | +2.7 | ✅ correct |
| Hand-crafted (50) | Qwen-2.5-3B | last_token | L25 | 97% | +8.0 | ✅ correct |
| ChatGPT (16) | Qwen-2.5-3B | comprehension | L23 | 97% | +1.4 | ✅ correct |
| Sonnet (100) | Qwen-2.5-3B | last_token | L18 | 98% | +3.9 | ✅ correct |
| Gemini (100) | Gemma-2-2B | comprehension | L11 | 98% | −0.9 | ❌ INVERTED |
| Gemini (100) | Qwen-2.5-3B | comprehension | L20 | 99% | −0.6 | ❌ INVERTED |
| Gemma-self (100) | Qwen-2.5-3B | comprehension | L16 | 99% | −0.7 | ❌ INVERTED |

## Steering results (2026-04-13)

13/36 runs completed on Gemma-2-2B before pivot to thinking models.
**Finding:** Steering non-thinking models changes wording, not reasoning (F85). Weight surgery produces same limitation (F86). Motivates move to thinking models (F87).

## Phase transition: Thinking model (2026-04-13)

Moving to **Qwen3-4B** (thinking model with `<think>...</think>` tokens) for extraction and steering experiments. Same corpus reused. Rationale in F87.
