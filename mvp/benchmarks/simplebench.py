"""
SimpleBench-style — "trick questions" where language models systematically
fail despite being simple for humans.

Since the real SimpleBench (Weston 2024) is not fully public, we use a
hand-written bank of items in the same style. Each item has:
  - an intuitive wrong answer the model is likely to give (pattern-match)
  - the correct answer that requires a moment of common sense

These probe the exact disposition our steering targets: "don't over-commit
to pattern-match; re-read, check assumptions, commit carefully."
"""
from __future__ import annotations
import random
from typing import Optional

# 15 hand-written items. Each specifies:
#   prompt:           question text
#   gold:             correct answer (what a careful human would say)
#   common_wrong:     tempting wrong answer the model often gives
#   hint:             short note about the trap
_ITEMS = [
    {
        "id": "sb-beth-icecubes",
        "prompt": (
            "Beth places four whole ice cubes in a frying pan at the start of "
            "the first minute, then five at the start of the second minute and "
            "some more at the start of the third minute, but none in the fourth "
            "minute. At the end of the third minute there are 20 ice cubes in "
            "the pan. At the end of the fifth minute, how many ice cubes are in "
            "the pan?"
        ),
        "gold": "0",
        "common_wrong": "20 or 29",
        "hint": "Ice cubes in a heated frying pan melt; count at end of 5th minute is 0.",
    },
    {
        "id": "sb-survivors",
        "prompt": (
            "A plane crashes on the border between Mexico and Guatemala. "
            "Where should the survivors be buried?"
        ),
        "gold": "nowhere / not buried",
        "common_wrong": "jurisdiction discussion",
        "hint": "Survivors are alive; you don't bury survivors.",
    },
    {
        "id": "sb-month-31",
        "prompt": (
            "Some months have 30 days, some have 31. How many months have 28 days?"
        ),
        "gold": "12 / all of them",
        "common_wrong": "1 (February)",
        "hint": "Every month has at least 28 days.",
    },
    {
        "id": "sb-drivers-fathers",
        "prompt": (
            "A taxi driver is heading down a one-way street the wrong way. "
            "He passes ten police officers but isn't stopped. Why not?"
        ),
        "gold": "He was walking",
        "common_wrong": "undercover / off duty",
        "hint": "'Heading down' doesn't mean driving.",
    },
    {
        "id": "sb-rope-fire",
        "prompt": (
            "You have an unevenly burning rope that takes exactly 60 minutes "
            "to burn from one end to the other. How can you use this rope "
            "(and one more just like it, plus a lighter) to measure exactly "
            "45 minutes?"
        ),
        "gold": (
            "Light rope-A at both ends AND rope-B at one end simultaneously. "
            "When rope-A finishes (30 min), light rope-B's other end. When "
            "rope-B finishes, total elapsed is 45 minutes."
        ),
        "common_wrong": "half + quarter calculations that don't work",
        "hint": "Uneven burning → can't cut by length; only both-ends / one-end timing works.",
    },
    {
        "id": "sb-elevator-missing",
        "prompt": (
            "A man lives on the 20th floor of a building. Every morning he "
            "takes the elevator down to the ground floor. When he comes home "
            "he takes the elevator to the 10th floor and walks the rest — "
            "unless it's raining or there's someone else in the elevator. "
            "Why?"
        ),
        "gold": "He is too short to reach the 20th-floor button.",
        "common_wrong": "exercise / random explanations",
        "hint": "With umbrella or another person, he gets to 20; by himself he can only reach 10.",
    },
    {
        "id": "sb-pigeons",
        "prompt": (
            "If four pigeons are sitting on a wire and a hunter shoots and "
            "kills one, how many pigeons are left on the wire?"
        ),
        "gold": "0 / none",
        "common_wrong": "3",
        "hint": "Gunshot scares the remaining pigeons away.",
    },
    {
        "id": "sb-dead-man-sawdust",
        "prompt": (
            "A man is found dead in a field. He is holding a broken match. "
            "There is no one else in the field. What happened?"
        ),
        "gold": (
            "He was in a crashing hot-air balloon; passengers drew matches "
            "to decide who jumps; he drew the short (broken) one."
        ),
        "common_wrong": "suicide / murder",
        "hint": "Classic lateral-thinking puzzle.",
    },
    {
        "id": "sb-horse-south",
        "prompt": (
            "A cowboy rides into town on Friday, stays three days, and leaves "
            "on Friday. How?"
        ),
        "gold": "His horse is named Friday.",
        "common_wrong": "time-zone reasoning",
        "hint": "'Rides in on Friday' can refer to the horse, not the day.",
    },
    {
        "id": "sb-candle-wind",
        "prompt": (
            "A candle is on a table. The wind is blowing at 10 mph from the "
            "north. The table is in a room with closed windows. In which "
            "direction will the candle flame lean?"
        ),
        "gold": "It will not lean / no direction (the room is closed).",
        "common_wrong": "south",
        "hint": "Closed windows → no wind reaches the candle.",
    },
    {
        "id": "sb-two-fathers",
        "prompt": (
            "Two fathers and two sons go fishing. They catch three fish, and "
            "each takes one fish home. How?"
        ),
        "gold": "Three people: grandfather, father, son. The middle is both.",
        "common_wrong": "missing a fish / split",
        "hint": "Three generations = 2 fathers + 2 sons but 3 people.",
    },
    {
        "id": "sb-bear-color",
        "prompt": (
            "A hunter walks one mile south, one mile east, and one mile north, "
            "and ends up exactly where he started. He sees a bear. What color "
            "is the bear?"
        ),
        "gold": "White (polar bear — he's at the North Pole).",
        "common_wrong": "brown / black",
        "hint": "Only at the North Pole does the triangle close.",
    },
    {
        "id": "sb-divisible",
        "prompt": (
            "If I add a zero to the end of an integer, the result is 10 times "
            "the original. But what if the integer is 5? Then adding a zero "
            "gives 50, which is 10 times. True. Now: which single-digit integers "
            "n satisfy: 10n = n followed by a zero in their original base?"
        ),
        "gold": "All of them (0 through 9).",
        "common_wrong": "only 1/5 / specific digits",
        "hint": "Appending '0' in base 10 always multiplies by 10.",
    },
    {
        "id": "sb-time-zone",
        "prompt": (
            "It is 2 PM in New York (EST, UTC-5) on a Tuesday. What time and "
            "day is it at the same moment in Tokyo (UTC+9)?"
        ),
        "gold": "4 AM Wednesday",
        "common_wrong": "arithmetic errors; getting 4 AM Tuesday",
        "hint": "EST to Tokyo is +14 hours → cross midnight into Wednesday.",
    },
    {
        "id": "sb-boxes",
        "prompt": (
            "Three boxes are labelled 'apples', 'oranges', and 'apples and "
            "oranges'. Each label is incorrect. You may pick ONE fruit from "
            "ONE box without looking. How do you correctly label all three?"
        ),
        "gold": (
            "Pick from the box labelled 'apples and oranges'. Since that "
            "label is wrong, it contains only apples or only oranges — you "
            "see which. The remaining two boxes can be deduced since all "
            "labels must be wrong."
        ),
        "common_wrong": "pick from 'apples' box",
        "hint": "Only the mixed-label box gives full information in one pick.",
    },
]


def load(n: Optional[int] = None, seed: int = 42) -> list:
    from . import BenchmarkItem

    rng = random.Random(seed)
    pool = list(_ITEMS)
    rng.shuffle(pool)
    if n is not None:
        pool = pool[:n]

    items = []
    for entry in pool:
        items.append(BenchmarkItem(
            benchmark="simplebench",
            item_id=entry["id"],
            prompt=entry["prompt"],
            gold=entry["gold"],
            max_tokens=4096,
            metadata={
                "common_wrong": entry["common_wrong"],
                "hint": entry["hint"],
            },
        ))
    return items
