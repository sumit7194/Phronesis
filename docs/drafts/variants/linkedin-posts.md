# LinkedIn posts — short, plain-language series (one per finding)

*Three short LinkedIn posts, simple language, meant to be spaced out (e.g. one every couple of days). Links + hashtags included. LinkedIn doesn't render markdown, so the `*word*` emphasis will show literal asterisks — delete those before posting (CAPS and → arrows display fine).*

---

## Post 1 — Timing, not direction (the headline)

I spent two months trying to make a small AI model more honest. It taught me something I didn't expect.

The goal: stop the AI from confidently making things up — like inventing the price of a product that was never released.

So I nudged the model's internal "thinking" to be more careful.

→ It got better at one thing: knowing when to look something up instead of guessing.
→ But its final answers got worse — it made things up even more often.

Then the real surprise: the thing that actually helped wasn't WHAT I nudged it toward. It was WHEN. A completely random nudge, at the same moment, worked just as well.

The lesson: sometimes timing beats the clever idea. And always test your result against a random version — it nearly fooled me into a "win" that wasn't real.

Full writeup (solo project, one rented GPU, written with AI and disclosed):
🔗 https://sumit7194.github.io/Phronesis/docs/drafts/lead-tool-use-timing-vs-direction.html

#AI #MachineLearning #AIResearch

---

## Post 2 — F121 (you can push, but you can't make it go quiet)

A small lesson from my AI side-project that surprised me:

You can nudge an AI model's internals to push it toward saying something. But you can't use the same trick to make it stop and say "I don't know."

I tried every version — push one way, push the other, even cleanly remove the direction. None made the model admit uncertainty. It just confidently said something different each time.

Why? The "honesty" we wanted may not live anywhere the nudge can reach. The limit isn't the technique — it's the model itself.

A useful negative result for anyone trying to make models more cautious by tweaking their internals.

🔗 https://sumit7194.github.io/Phronesis/docs/drafts/F121-steering-one-sidedness.html

#AI #MachineLearning #Interpretability

---

## Post 3 — The replication (run the boring control first)

The most useful thing I did in my AI project was the boring check I almost skipped.

I had an exciting result: a specific "direction" I nudged the model toward made it more careful on a tricky question.

Before celebrating, I ran one dull test: what if I nudge it in a random direction instead?

The random one did the same thing.

So my "discovery" wasn't about the clever direction at all — it was just a side effect of nudging the model, on one specific question, and it didn't even hold up on others.

Lesson: run the boring control before you get excited. It saves you from false wins.

🔗 https://sumit7194.github.io/Phronesis/docs/drafts/lesswrong-replication-post-v4.html

#AI #MachineLearning #ResearchIntegrity
