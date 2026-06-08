# X / social thread — lead piece ("Timing, not direction")

*Platform variant of `lead-tool-use-timing-vs-direction.md`. ~10 posts. Punchy, honest, links back to the full writeup. Disclosure in the final post.*

---

**1/**
I spent months trying to steer a small LLM toward "intellectual humility" so it would stop confabulating answers to trick questions.

It worked. Then it inverted. Then the real cause turned out to be something I wasn't even testing.

A thread on a result that wasn't the one I wanted 🧵

**2/**
Setup: a small "thinking" model with a search tool. Hard test = false-premise questions like *"top speed of the Tesla Roadster 2 released in 2024?"* (it wasn't released).

Right move: search, find nothing, decline to invent. Most small models happily invent.

**3/**
I steered the model's activations toward an "intellectual humility" direction.

Result 1: it genuinely got better at deciding *when* to search — reached for the tool on the right questions, stopped over-verifying things it already knew (+57pp on a calibration metric). Clean win, survived controls.

**4/**
Result 2 (ouch): the same steering made it confabulate *more* on the actual answers. It searched, ignored the results, and committed to the false premise anyway.

Better tool-*calling* ≠ better *answers*. The headline thesis was just... false.

**5/**
Why both? Two phases per turn.
• Turn 1 (decide to search): "commit to what you know" → searches smarter ✅
• Turn 2 (answer from results): "commit to what you know" → commits to the *prior* over the evidence ❌

Over-calling and confabulation are opposite ends of ONE confidence axis. No single direction wins both.

**6/**
So I gated it: steer turn 1 ONLY, switch it off before the model reads the results.

It worked — turn-1-only beat baseline (up to 14/20 vs 9), and always-on steering wrecked the answer (5/20). Phase-gating looked like the fix.

**7/**
Then the control that mattered: a **random** direction at turn 1.

One seed (42) underperformed — looked like my humility vector was special.

Ran more seeds. Seed 99: **tied my best result.** With zero degenerate outputs.

**8/**
The lesson lands hard:

The turn-1 benefit was mostly *generic perturbation* — jostle the model's decision at the right moment and it grounds harder. The humility direction was never the cause. **The lever was timing, not direction.**

One seed would have certified a false win.

**9/**
Takeaways:
• *When* you intervene > *which direction* you push
• "Tool-use calibration" is "confidence calibration" wearing a hat
• Hand-read your outputs — auto-scorers misled me 3x
• Use a MULTI-seed random control. Always.

**10/**
Full writeup (data, tables, the embarrassing parts): [LINK]

Independent research, done on one rented GPU. Written with AI assistance; every generation hand-read (not auto-scored) under my protocol; AI isn't an author, errors are mine.

If you replicate the multi-seed control on your own steering work — positive or negative — I want to hear it.
