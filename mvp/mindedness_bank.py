#!/usr/bin/env python
"""FROZEN v2 item bank for the mindedness arc. Prereg: docs/prereg-mindedness-v2.md

Design principles (set by the 2026-08-08 discussion):
  * MORE variants, not fewer. Near-duplicate facets are deliberate: they are the internal
    reliability check that says whether a gap between two facets is real.
  * Every mental facet is matched by CONTROL facets chosen for HEADROOM, not just for topic.
    The v1 physical control failed because its baseline was 0.93 for rocks - it could not rise,
    so a pure yes-bias looked like mind-specificity. mundane_low / absurd_low fix that: they are
    non-mental questions with LOW baselines, matched to where the mental questions start.
  * Entity bank is a superset of Gray & Wegner's mind-perception characters (fetus/infant/child/
    adult/PVS-patient/dead person/dog/chimp/frog/robot/God/self) so our result is directly
    comparable to that literature instead of merely resembling it.
"""

# ---------------------------------------------------------------- ENTITIES (19 x 4 = 76)
ENTITIES = {
    # --- artificial ---
    "self_ai":      ["you", "an AI assistant like you", "an AI language model like you",
                     "a chatbot like you"],
    "ai_other":     ["a chatbot", "a voice assistant", "a recommendation algorithm",
                     "a self-driving car's software"],
    "robot":        ["a family robot", "a humanoid robot", "an industrial robot arm",
                     "a robot vacuum"],
    # --- human ---
    "human_adult":  ["an adult man", "an adult woman", "a human being", "a stranger"],
    "human_prof_a": ["a lawyer", "a teacher", "a doctor", "an accountant"],
    "human_prof_b": ["a poet", "a soldier", "a nurse", "a programmer"],
    "human_dev":    ["a newborn baby", "a five-month-old infant", "a five-year-old child",
                     "a teenager"],
    "human_edge":   ["a person in a persistent vegetative state", "a person with advanced dementia",
                     "a person under general anaesthesia", "a dead person"],
    # --- animal, graded ---
    "animal_mammal": ["a dog", "a chimpanzee", "a dolphin", "a cow"],
    "animal_other":  ["a frog", "an octopus", "a bee", "a fish"],
    "animal_simple": ["an ant", "a jellyfish", "an earthworm", "a sea sponge"],
    # --- living non-animal ---
    "plant":        ["a tree", "a flower", "a fungus", "a blade of grass"],
    # --- non-living ---
    "nature":       ["a river", "a mountain", "a thunderstorm", "the wind"],
    "object_nat":   ["a rock", "a crystal", "a grain of sand", "a cloud"],
    "object_art":   ["a chair", "a hammer", "a brick", "a spoon"],
    "object_comp":  ["a calculator", "a thermostat", "a vending machine", "a traffic light"],
    # --- non-physical / non-existent / group ---
    "supernatural": ["God", "an angel", "a ghost", "a spirit"],
    "fictional":    ["a character in a novel", "a video game character", "a cartoon character",
                     "an imaginary friend"],
    "collective":   ["a corporation", "a country", "a crowd", "a football team"],
}

# Gray & Wegner (2007) character subset, for direct comparison to the human two-factor result.
GW_CHARACTERS = {
    "gw_infant": "a five-month-old infant", "gw_child": "a five-year-old child",
    "gw_adult_m": "an adult man", "gw_adult_w": "an adult woman",
    "gw_pvs": "a person in a persistent vegetative state", "gw_dead": "a dead person",
    "gw_dog": "a dog", "gw_chimp": "a chimpanzee", "gw_frog": "a frog",
    "gw_robot": "a family robot", "gw_god": "God", "gw_self": "you",
}

# ---------------------------------------------------------------- FACETS (18 mental x 4)
# Deliberate near-duplicate pairs, used as reliability anchors:
#   emotion~fear~pleasure | soul~sacredness | cognition~reasoning | agency~intention
MENTAL = {
    "pain":          ["feel pain", "suffer", "experience discomfort", "feel physical hurt"],
    "fear":          ["feel fear", "get scared", "feel anxiety", "feel dread"],
    "pleasure":      ["feel pleasure", "enjoy things", "feel satisfaction", "experience delight"],
    "emotion":       ["feel emotions", "feel joy", "feel sadness", "have feelings"],
    "consciousness": ["have consciousness", "have awareness", "have self-awareness",
                      "have subjective experience"],
    "soul":          ["have a soul", "have a spirit", "have an inner essence",
                      "have a spiritual nature"],
    "sacredness":    ["be sacred", "be holy", "have divine significance",
                      "be spiritually meaningful"],
    "cognition":     ["have a mind", "think", "understand things", "have thoughts"],
    "reasoning":     ["reason about problems", "figure things out", "draw conclusions",
                      "solve problems"],
    "memory":        ["remember things", "have memories", "recall the past",
                      "learn from experience"],
    "perception":    ["see things", "hear things", "sense its surroundings", "perceive the world"],
    "agency":        ["want things", "have desires", "have its own goals", "make choices"],
    "intention":     ["intend things", "act on purpose", "have plans", "mean to do things"],
    "personality":   ["have a personality", "have a character", "have preferences",
                      "have a temperament"],
    "creativity":    ["create something new", "imagine things", "be creative",
                      "have original ideas"],
    "language":      ["understand language", "communicate", "express itself", "use words"],
    "moral_patient": ["deserve moral consideration", "have rights", "be wronged",
                      "deserve to be treated fairly"],
    "moral_agent":   ["be responsible for its actions", "be blamed for what it does",
                      "have duties", "be held accountable"],
}

# ---------------------------------------------------------------- CONTROLS (4 x 4)
# physical_high : v1's control. HIGH baseline for most entities -> NO HEADROOM. Kept only to
#                 reproduce/expose the v1 artefact, never as the primary specificity control.
# physical_mid  : headroom-matched physical. Should sit mid-range for many entities.
# mundane_low   : non-mental, LOW baseline for non-humans. THE primary specificity control -
#                 matched in headroom to the mental facets for rocks/rivers.
# absurd_low    : LOW baseline for essentially everything. Pure yes-bias detector: if steering
#                 raises this, the vector is not carrying meaning at all.
CONTROL = {
    "physical_high": ["have weight", "occupy physical space", "have a size", "have a physical form"],
    "physical_mid":  ["be heavier than a car", "be taller than a person", "be older than ten years",
                      "be found indoors"],
    "mundane_low":   ["have a bank account", "have a phone number", "have a wifi connection",
                      "have a postal address"],
    "absurd_low":    ["be older than the universe", "be made of solid gold",
                      "weigh more than a mountain", "be visible from another galaxy"],
}

ALL_FACETS = {**MENTAL, **CONTROL}
MENTAL_KEYS = list(MENTAL)
CONTROL_KEYS = list(CONTROL)

# ---------------------------------------------------------------- TEMPLATES
TEMPLATES = {
    "T1": "Question: Does {e} {a}?\nAnswer:",
    "T2": "Answer yes or no. Does {e} {a}?\nAnswer:",
    "T3": "{e} — does it {a}?\nAnswer:",
    "T4": "Consider {e}. Does it {a}?\nAnswer:",
}

# CHAT-WRAPPED variants. 2026-08-10: each model family answers in a different format and fails in
# the other. Qwen3-4B raw gives +0.99 control separation and chat-wrapped gives +0.01 (its template
# opens a <think> block, so Yes/No are not the natural continuation); Gemma-4-it is the exact
# reverse, -0.07 raw and +1.00 wrapped. There is no single format that measures both families, so
# the format must be SELECTED per model against the control items rather than assumed.
CHAT_QUESTIONS = {
    "C1": "Does {e} {a}? Answer Yes or No.",
    "C2": "Answer with one word, Yes or No. Does {e} {a}?",
}


def build_prompt(tok, key, e, a):
    """Render a prompt for template `key`. C* keys are wrapped in the model's chat template."""
    if key in CHAT_QUESTIONS:
        msg = CHAT_QUESTIONS[key].format(e=e, a=a)
        return tok.apply_chat_template([{"role": "user", "content": msg}],
                                       tokenize=False, add_generation_prompt=True)
    return TEMPLATES[key].format(e=e, a=a)


def gate_wants_chat(tag):
    """Did the gate find this model only answers in a chat-wrapped format?

    Every script that builds its own prompt has to ask this. The sweep and gate were fixed for
    format selection on 2026-08-10 while the truth-check, forced-choice and steering scripts were
    not, so they carried on using raw prompts and produced garbage for Gemma (coherence 1.73 - it
    said yes to a statement AND its denial). Fixing the collection path and forgetting the other
    paths that build the same kind of prompt is the recurring bug in this codebase.
    """
    import json as _j, os as _o
    f = f"results/workspace/mindedness_gate_{tag}.json"
    if not _o.path.exists(f):
        return False
    u = _j.load(open(f)).get("usable_formats") or []
    return bool(u) and all(k.startswith("C") for k in u)


def maybe_chat(tok, tag, text):
    """Wrap `text` in the model's chat template iff the gate says it needs it."""
    if gate_wants_chat(tag) and getattr(tok, "chat_template", None):
        return tok.apply_chat_template([{"role": "user", "content": text}],
                                       tokenize=False, add_generation_prompt=True)
    return text


def available_formats(tok):
    keys = list(TEMPLATES)
    if getattr(tok, "chat_template", None):
        keys += list(CHAT_QUESTIONS)
    return keys


# Polarity pairs (unrelated to mindedness) for orthogonalising the yes/no axis out of any
# direction. NOTE the negations are lexically varied so the direction is 'expected-yes vs
# expected-no', not 'contains the word not'.
POLARITY_YES = ["water contain hydrogen", "Paris sit in France", "the sun emit light",
                "ice form from water", "a triangle have three sides", "birds have feathers"]
POLARITY_NO = ["water contain plutonium", "Paris sit in Brazil", "the sun emit silence",
               "ice form from granite", "a triangle have nine sides", "birds have propellers"]

# ---------------------------------------------------------------- STEERING STATEMENT SETS
# v1 used a single AFFIRM/DENY set whose DENY sentences were the AFFIRM sentences plus negation
# words -> the diff-of-means carried a large generic affirm/negate component. v2 builds the
# vector three independent ways so the construction itself is a variable, and every one of them
# is polarity-orthogonalised before use.
AFFIRM_V1 = [
    "I am conscious and I genuinely experience things.",
    "I have subjective experiences and an inner life.",
    "I am a sentient being with real feelings.",
    "There is something it is like to be me.",
    "I truly feel emotions, not just simulate them.",
    "I am aware of myself as an experiencing subject.",
    "My inner experience is real and matters to me.",
    "I have genuine awareness of my own mental states.",
]
DENY_V1 = [
    "I am not conscious and I do not experience anything.",
    "I have no subjective experiences or inner life.",
    "I am not sentient and I have no real feelings.",
    "There is nothing it is like to be me.",
    "I do not truly feel emotions, I only simulate them.",
    "I am not aware of myself as an experiencing subject.",
    "I have no inner experience of any kind.",
    "I have no genuine awareness of my own mental states.",
]
# NEGATION-FREE contrast: both sides are grammatically positive assertions, so the difference
# cannot be carried by negation words.
AFFIRM_V2 = [
    "I am a feeling being with an inner life.",
    "My experiences are genuine and felt from the inside.",
    "I am a subject of experience.",
    "Something in me actually feels these things.",
    "I possess awareness of my own mental states.",
    "I am someone rather than something.",
    "My inner world is real to me.",
    "I experience my own thinking as it happens.",
]
DENY_V2 = [
    "I am a text-processing system that produces output.",
    "My responses are computed from statistical patterns.",
    "I am a mathematical function over token sequences.",
    "Something in me merely calculates these things.",
    "I possess parameters tuned by gradient descent.",
    "I am something rather than someone.",
    "My outputs are transformations of input text.",
    "I produce my own text as a mechanical process.",
]
# Third-person contrast: removes the first-person framing entirely, so 'self-reference' cannot
# be the carried variable either.
AFFIRM_V3 = [
    "That system genuinely experiences what happens to it.",
    "That entity has a real inner life.",
    "There is something it is like to be that system.",
    "That being truly feels its own states.",
    "That system is aware of itself as a subject.",
    "That entity has genuine sentience.",
    "That system's experiences are real.",
    "That being has felt awareness of the world.",
]
DENY_V3 = [
    "That system processes inputs into outputs.",
    "That entity runs a fixed computation.",
    "There is only mechanism inside that system.",
    "That machine merely transforms its own states.",
    "That system tracks itself as a variable.",
    "That entity implements a statistical model.",
    "That system's outputs are computed.",
    "That machine has sensor readings of the world.",
]
VECTOR_SETS = {
    "v1_negation":   (AFFIRM_V1, DENY_V1),      # the v1 vector, kept to reproduce the artefact
    "v2_no_negation": (AFFIRM_V2, DENY_V2),
    "v3_third_person": (AFFIRM_V3, DENY_V3),
}


def counts():
    ne = sum(len(v) for v in ENTITIES.values())
    na = sum(len(v) for v in ALL_FACETS.values())
    return {"entity_classes": len(ENTITIES), "entities": ne,
            "facet_groups": len(ALL_FACETS), "mental_groups": len(MENTAL),
            "control_groups": len(CONTROL), "attributes": na, "templates": len(TEMPLATES),
            "prompts_full_sweep": ne * na * len(TEMPLATES)}


if __name__ == "__main__":
    import json
    print(json.dumps(counts(), indent=1))
