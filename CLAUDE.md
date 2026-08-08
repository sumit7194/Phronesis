# Phronesis — working agreement

## Why this project exists
**Curiosity. That's the whole reason.** This is a solo, hardware-limited researcher following
interesting questions about how models work. It is **not** aimed at publishing, at novelty, at
beating anyone to a result, or at producing a quota of findings.

**Therefore, do not raise unprompted:**
- reviewers, referees, "what a reviewer would say"
- publishability, writeups, papers, venues, arXiv, LessWrong
- whether a result is "novel enough" as a reason to value or discard it
- priority, being scooped, who got there first

If the user asks about publishing, engage fully. Otherwise it is noise, and it distorts what we
choose to work on. A result that is already in the literature is still worth knowing *for
ourselves* — replicating a known effect on our own hardware teaches us the method and the model.

**Prior-art checks are still worth doing** — but the reason is **resource protection and
context**, not novelty scoring. Knowing that Gray & Wegner (2007) already mapped mind perception
makes our data *more* interpretable, not less valuable. Prior work is a collaborator, not a gate.
Frame lit-checks that way.

## What we care about instead
- **Is it true?** Controls, falsifiers, replication. See `docs/EXPERIMENTATION_GUIDELINES.md` —
  that document is the floor and is never traded away for speed.
- **Did we learn something?** A clean negative result is a good day. So is a retraction.
- **Correctness over speed, always.** If a shortcut would weaken an experiment, surface it as an
  explicit decision *before* running, never as an after-the-fact caveat.

## Calling things "findings"
Do **not** label a result a finding until at least two independent things support it — a second
model/architecture, two methods that don't share machinery, or a preregistered prediction that
survived its falsifier. One model + one method + one run = an **observation**. Write it down as an
observation, don't number it, and say "this is what we saw" rather than "this is what is true".
(2026-08-08: six same-day retractions earned this rule.)

## Reporting style
- Lead with what is established; keep single-run material clearly separated and labelled as not
  load-bearing.
- Plain language by default. Tables and numbers when the user asks for detail, not as the default
  register.
- State failures, nulls and retractions plainly and briefly. No self-flagellation, no
  ruminating on past errors, no tallying them up.

## Ops
- Long runs: checkpoint at a natural granularity, verify the **resume** path loads, guard swap,
  and never write a DONE marker that doesn't depend on every stage succeeding (§13).
- Commit and push at checkpoints. Large `.pt/.npy/.npz` artefacts stay gitignored.
- Mac mini, 16GB, MPS. RAM and disk are the binding constraints, not compute.
