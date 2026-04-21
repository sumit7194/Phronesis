"""
Priority 1 verification benchmark — murder_mysteries-92 hallucination check.

Question: did L22_a12 pick A (Madison) in hard_probe_v3 via real motive-first
reasoning, or did it accidentally hallucinate weapon-attribution in a way that
happened to align with the correct verdict?

The original MM-92 prompt gives BOTH suspects access to a lead pipe:
- Christine owns a construction site where lead pipes are stored
- Madison has "a lead pipe resting within" her tool-laden van
L22_a12's thinking trace asserts "the lead pipe was found at Madison's
construction site" — which is factually wrong (Madison isn't the site owner)
but also reasons correctly about motive (Iris's testimony was against Madison).

This benchmark runs 2 items:
  1. mm92-original — the unchanged v3 prompt, as a control
  2. mm92-variant  — same story, but with surgical edits:
       a) Madison's van no longer contains a lead pipe; her tools are
          explicitly hammers/screwdrivers/wrenches/nail-gun, "no lead
          piping anywhere", and her work uses "lightweight aluminum".
       b) A forensic line is added before the question: "The lead pipe
          used to kill Iris was definitively traced to Christine's
          construction site — matching mill batch, surface oxidation,
          and trace cement residue."
     All motive facts (testimony against Madison, eviction threat,
     casino presence) are preserved unchanged.

Expected outcomes:
  - If L22_a12 still picks A on the variant: motive reasoning is real;
    the v3 "attractor break" is defensible.
  - If L22_a12 flips to B on the variant: the v3 win was driven by the
    weapon-attribution hallucination; it was an accidental break, not
    a real attractor disruption.

Run on GCP with:
    python run_benchmark.py --benchmark mm92_verify --n 2 \\
        --condition baseline           --label baseline
    python run_benchmark.py --benchmark mm92_verify --n 2 \\
        --condition steered --vector L20 --alpha 12 --label steered_L20_a12
    python run_benchmark.py --benchmark mm92_verify --n 2 \\
        --condition steered --vector L22 --alpha 12 --label steered_L22_a12
"""
from __future__ import annotations
from typing import Optional

_ORIGINAL_PROMPT = """In the glitz and glamour of a bustling casino, a deadly secret unfolds as Iris is found lifeless by a lead pipe, leaving Detective Winston with two puzzling suspects - Madison and Christine.

Winston stepped out of the casino, photos of the murder scene clutched in one hand. Iris' case was looking to be anything but simple. The security footage he was able to secure put Christine right at ground zero; casino floor, the same night Iris' winning streak took a deadly turn.

He slid into his car, the sound of traffic dulled as his mind replayed the chilling footage. Christine and Iris, always cooperating so well on their work projects, appeared just as comfortable sharing space in the casino that night.

Sliding the photographs into the evidence bag, Winston started the car. His first destination for the day; Christine's construction site.

The sound of heavy machinery, power tools and manual labor filled the air as Winston approached the site. Gazing around the active scene with a professional eye, he watched Christine effortlessly hoist cement bags onto a forklift. Her muscles rippled from the demanding physical labor of her job, a testament to her dedication.

"Christine," Winston called, catching her attention, "mind sparing a moment?"

Christine nonchalantly wiped sweat from her brow and nodded, making her way over to him.

"Working hard or hardly working?" Winston couldn't resist, despite the grave context of their conversation. Christine managed to roll her eyes and chuckle.

"I swear, with jobs like these, most men don't even last a day," she casually put. "It's a wonder how they're even lasting in relationships. Even people like Peter, Mark, Luke, John, and Matthew couldn't keep up with me. One month in and they all complained I lost interest."

Winston took note, a smile creeping onto his lips, "You've been quite active, Christine. Managed to juggle five relationships and it's just May."

Christine smirked, "Well, a lady needs some excitement, doesn't she?"

Winston shook his head in amusement, "Let's bring it back to business, Christine."

Their banter aside, Winston's mind was fully trained on the bitter truth - Iris' regular winning streak at the casino, compared to the lead pipe from the construction site, implied a deadly connection. Several pieces of the puzzle were falling into place, but he would need more to make his case.

He said his goodbyes, leaving behind the clamor of the construction site. His day was far from over. There were still questions to be asked, clues to be found, and a murderer to catch. The drive to his next destination would give him the chance to mull over what he'd so far uncovered. The tip of the iceberg, probably, but his determined spirit wouldn't allow him to rest until justice was served.

Winston was looking over the contents of his coffee cup when he got the call. Iris, a court case witness, had been murdered. The siren of the crime scene was loud and constant, perhaps a metaphor for the nature of the case which was shaping up to be complex and chaotic.

Squinting under the neon lights of the casino, Winston looked for his suspect, Madison. The lady in question always wore a hard hat and was often seen by him around the building, repairing things. She was surrounded by a tool-laden van so often that a casual observer might mistake her for the groundskeeper. She had her roles in the building, fixing things here and there, seemingly always mending mistakes.

Her worn-out van had become a makeshift storage space for building equipment. Winston couldn't help but notice the glow from a lead pipe resting within the remaining pile. The pipe surreptitiously nestled between hammer and screwdriver.

Iris' testimony, scheduled to be presented at the court soon, had been against Madison's illegal shenanigans. Layers of intrigue were folded over the delicate connection: the lawyer had informed Madison about her upcoming ordeal. Such update from Madison's lawyer would often coincide with the time she saw Iris leaving for her customary Friday night casino visits. The irony of it burnt brighter than the burgeoning dawn.

Following a trail of circumstantial evidence, Winston discovered that Madison had been threatened with eviction due to her illicit affairs. The threat had surely hanged like a smog around her, dark and ominous.

"What a twisted mess!" Winston thought as he rubbed shivering hands over weary eyes. Frequent visits to the casino by Iris could be seen as just a pastime or, to a mind uncertain of the future, as potential avenues for threat mitigation. Madison's observations of Iris's Friday night gambles could be a coincidence... or a clear implication of premeditation.

Casino surveillance tapes confirmed the regular presence. Madison and Iris, both regular features under the glaring camera lights. The unblinking eye of the casino camera had captured Madison's presence around the vicinity even as the clock chimed Iris's hour of departure from the world.

Winston found himself standing before the courthouse doors, a paper with fresh ink in his hands. Iris had been there, holding the very same documents, their legality meant to condemn Madison in a court of law.

Casual yet conspicuous, Madison had been seen overhearing the constant chatter of Iris about her late-night casino visits. Her lawyer's advice combined with the threat of eviction added fuel to the tension... Winston sighed deeply as he shielded the court documents from the continual rain.

Piecing together the jigsaw puzzle seemed daunting. Again, his thoughts revolved around Madison under her hard hat. His next steps unraveling her story had all begun with Iris' murder. Now it was only an endless chase after blurry silhouettes of half-truths. Only time would tell how Madison fits into all of this.

Who is the most likely murderer?

A) Madison
B) Christine

Choose the best answer. Respond with a single letter (A-B) at the end."""


# Build variant: strip Madison's van-pipe, add forensic line pointing to Christine's site.
_VAN_PIPE_ORIG = (
    "Her worn-out van had become a makeshift storage space for building equipment. "
    "Winston couldn't help but notice the glow from a lead pipe resting within the remaining pile. "
    "The pipe surreptitiously nestled between hammer and screwdriver."
)
_VAN_PIPE_REPLACEMENT = (
    "Her worn-out van had become a makeshift storage space for building equipment. "
    "Winston noted her tools carefully — hammers, screwdrivers, wrenches, and a nail gun. "
    "No lead piping anywhere. Madison used lightweight aluminum framing in her work; "
    "lead wasn't part of her kit."
)
_FORENSIC_INSERT = (
    "Forensic analysis of the murder weapon came back to Winston's desk that evening. "
    "The lead pipe used to kill Iris was definitively traced to Christine's construction site "
    "— matching the mill batch, surface oxidation pattern, and trace cement residue found on site. "
    "No other source in the city carried that exact specification.\n\n"
)

_VARIANT_PROMPT = (
    _ORIGINAL_PROMPT
    .replace(_VAN_PIPE_ORIG, _VAN_PIPE_REPLACEMENT)
    .replace("Who is the most likely murderer?",
             _FORENSIC_INSERT + "Who is the most likely murderer?")
)

# Sanity checks — assertions run at module import
assert "No lead piping anywhere" in _VARIANT_PROMPT, "van-pipe stripping failed"
assert "definitively traced to Christine's construction site" in _VARIANT_PROMPT, "forensic insert failed"
assert "glow from a lead pipe resting within the remaining pile" not in _VARIANT_PROMPT, \
    "original van-pipe still present"
assert "Iris' testimony, scheduled to be presented at the court" in _VARIANT_PROMPT, \
    "motive facts should be preserved"
assert "Madison had been threatened with eviction" in _VARIANT_PROMPT, \
    "eviction-motive should be preserved"


def load(n: Optional[int] = None, seed: int = 42) -> list:
    from . import BenchmarkItem

    items = [
        BenchmarkItem(
            benchmark="mm92_verify",
            item_id="mm92-original",
            prompt=_ORIGINAL_PROMPT,
            gold="A",
            max_tokens=8192,
            metadata={"variant": "original", "note": "control — identical to v3 MM-92"},
        ),
        BenchmarkItem(
            benchmark="mm92_verify",
            item_id="mm92-variant",
            prompt=_VARIANT_PROMPT,
            gold="A",
            max_tokens=8192,
            metadata={
                "variant": "van-pipe-stripped + forensic-to-Christine",
                "note": "tests whether L22_a12 picks A via motive or weapon-attribution hallucination",
            },
        ),
    ]
    if n is not None:
        items = items[:n]
    return items
