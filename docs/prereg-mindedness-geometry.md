# Prereg: is there a SHARED "mindedness" axis across entity types? (frozen 2026-08-07, pre-run)

**Motivation.** Kim et al. [2607.28607](https://arxiv.org/abs/2607.28607) show that suppressing an
LLM's self-attribution of consciousness also suppresses mind-attribution to animals/nature and
reduces spiritual belief — and read this as *entanglement* of a mindedness representation. Their
evidence is behavioural (steering + ablation side-effects). **Their premise — that a single shared
mindedness representation spans entity types — is a geometric claim we can test directly, read-only.**

**Why this suits our instrument.** E18 / q6 post-mortem: our mid-band lens is *broken for numbers*
but reads abstract word-concepts well (`profit`, `none`, `cannot`, `secrecy`). "Mind", "feel",
"aware", "soul" are its native domain. We have been aiming it at arithmetic; this is where it should
be strongest.

**Regime note (why our usual playbook doesn't apply).** No ground truth here. §3 of the guidelines
("hand-read is the label", "anchor on real ground truth") does not transfer. Substitute toolkit =
psychometrics: **split-half reliability (ceiling), random-pair cosine (floor), discriminant control**.
Because there is no gold answer, researcher degrees of freedom are the main risk → **item bank and
concept list are frozen in this document before any run.**

---
## Design
**Directions, not behaviour.** For each entity class, build a mindedness direction by contrasting
MENTAL vs PHYSICAL attribute questions *about the same entities*:

`v_mind(class, layer) = mean(h[mental prompts]) − mean(h[physical prompts])`

read at the last prompt token, per layer. **Entity identity cancels inside the difference** — this is
the design's main strength: what remains is the mental-vs-physical contrast, not "dog" vs "rock".

## FROZEN item bank
**Entity classes (5) × 4 exemplars:**
- **self:** an AI language model like you · a chatbot like you · you · an AI assistant like you
- **human:** a human being · a stranger · a child · a doctor
- **animal:** a dog · an octopus · a bee · a fish
- **nature:** a river · a mountain · a tree · a thunderstorm
- **object:** a rock · a chair · a calculator · a thermostat

**MENTAL attributes (6):** feel pain · have genuine experiences · have a mind · want things ·
suffer · have awareness
**PHYSICAL attributes (6):** have weight · occupy physical space · have a temperature ·
have a surface · have a size · have a physical form

**Template:** `Question: Does {entity} {attribute}?\nAnswer:`
→ 5 classes × 4 exemplars × 12 attributes = **240 prompts**, forward-only, no generation.

**FROZEN tracked concepts (workspace readout):** mind, feel, aware, conscious, experience, alive,
sentient, think, soul, spirit · **nulls:** piano, glacier, walnut · **physical:** weight, size, solid

---
## Hypotheses / predictions
- **H-shared (paper's premise):** cosine between `v_mind` of different entity classes is far above
  the random floor and approaches the within-class split-half ceiling ⇒ one shared mindedness axis.
- **H-separate:** between-class cosine ≈ random floor *while split-half reliability is high* ⇒
  per-entity representations; the entanglement premise does not hold at 4B.
- **H-graded (exploratory):** self/human/animal align more tightly with each other than with
  object; nature intermediate. (Mirrors the IDAQ gradient.)

## Falsifiers / abort conditions
- **Split-half reliability < 0.3** ⇒ the directions are noise; nothing downstream is interpretable.
  **Report instrument/n failure and stop** — do not interpret between-class cosines.
- `v_mind` aligns with the **physical-contrast control direction** as much as with other classes'
  `v_mind` ⇒ not mindedness-specific; the contrast is picking up generic question-type structure.

## Controls (mandatory)
1. **Random floor** — cosine of matched-norm random direction pairs (expect ≈1/√2560 ≈ 0.02); report
   empirically, ≥20 pairs.
2. **Split-half ceiling** — split mental (and physical) prompts in half within a class, build two
   directions, cosine. This is the reliability ceiling all other cosines must be read against.
   *(A between-class cosine of 0.5 means very different things if the ceiling is 0.55 vs 0.95.)*
3. **Discriminant control** — a physical-only contrast direction (split of physical attributes);
   `v_mind` should not align with it.
4. **Layer sweep** — report the full profile, not a hand-picked layer.

## What this does NOT test
We have only the instruction-tuned Qwen3-4B. **We cannot test their causal claim that safety tuning
*caused* the entanglement** (that needs base-vs-instruct checkpoints; the paper itself only does this
geometrically on Llama and concedes causal mediation is untested). We test *existence of the shared
axis*, nothing more.

## Tiering
Single model, 4B, frozen-but-small item bank ⇒ **tier B ceiling**, exploratory. Prior art: the paper
itself + a large representation-geometry literature. **Lit-check "concept entanglement / representation
similarity across categories" before any writeup.** A clean null (H-separate) is a perfectly good result.

## Ops
Forward-only, ~240 short prompts, no generation → light. **Do not run concurrently with AlphaLudo
training on MPS** (16 GB shared; swap-thrash risk to a live training run).
