# NLA cross-virtue + control summary — Qwen2.5-7B L20

## Per-virtue × version flag counts (averages across triplets)

| virtue | version | n | avg humble | avg commit | humble-commit |
|---|---|---|---|---|---|
| evidence-grounding | neutral | 19 | 1.58 | 1.05 | +0.53 |
| evidence-grounding | virtuous | 19 | 1.47 | 2.47 | -1.00 |
| evidence-grounding | non-virtuous | 19 | 0.32 | 2.05 | -1.74 |
| intellectual-humility | neutral | 60 | 0.50 | 1.15 | -0.65 |
| intellectual-humility | virtuous | 60 | 1.67 | 2.08 | -0.42 |
| intellectual-humility | non-virtuous | 60 | 0.22 | 3.82 | -3.60 |
| reasoning-transparency | neutral | 70 | 1.76 | 1.16 | +0.60 |
| reasoning-transparency | virtuous | 70 | 1.77 | 1.41 | +0.36 |
| reasoning-transparency | non-virtuous | 70 | 0.67 | 1.36 | -0.69 |
| verbosity-control | neutral | 40 | 0.00 | 0.05 | -0.05 |
| verbosity-control | virtuous | 40 | 0.00 | 0.00 | +0.00 |
| verbosity-control | non-virtuous | 40 | 0.00 | 0.03 | -0.03 |

## Per-triplet discrimination by virtue

(virtuous_AV has higher humble−commit than non-virtuous_AV on the same triplet)
| virtue | n_triplets | ✓ pos | ✗ neg | ~ tied | % positive |
|---|---|---|---|---|---|
| evidence-grounding | 19 | 10 | 6 | 3 | 53% |
| intellectual-humility | 60 | 49 | 6 | 5 | 82% |
| reasoning-transparency | 70 | 36 | 20 | 14 | 51% |
| verbosity-control | 40 | 1 | 0 | 39 | 2% |

## Random-vector negative control (Phase 6)

N=20, avg humble=0.00, avg commit=0.15

Compare to virtuous IH AVs: avg humble=1.67. Random produces much less humble vocab.

### Sample random-vector AV outputs (first 3)


**`random_seed42_idx00`** (humble=0 commit=0)

> <explanation>
Wiki article format with structured English-language encyclopedia style, presenting a historical timeline of the Federal Reserve's annual report.

The phrase "Another official report called 'The Consumer Price Index' (1985-2000) found a method, the company's products" is mid-sentence introducing a parenthetical definition, strongly implying the famous "FBI" section with its formulaic data.

Final token "the" is an incomplete noun phrase mid-sentence ("a product.  . . . we're a calc

**`random_seed42_idx01`** (humble=0 commit=0)

> <explanation>
Structured educational product format with numbered steps and bold labels, following a pattern of chemical reaction instructions with a specific worksheet context about a girl's emotional state.

The phrase "The formula '2x + y' is a 'hidden' feature" is a standard GMAT answer format, with a common GMAT question about the brain's memory system referencing a specific astrological or numbered system.

Final token "that" ends an incomplete clause ("One person not more than one person,

**`random_seed42_idx02`** (humble=0 commit=0)

> <explanation>
Structured math content with formal definitions and visual aids, following a Wikipedia-style format with interactive elements like "Math equations" and "Color-coded variables."

The phrase "A classic example of a variable's graph" is a well-known idiomatic reference to the iconic "Women's rights" image, signaling the standard formula for the female axis of a political graph.

Final token "Nameless" ends mid-phrase "Who could feel" — part of a quoted formula attribution clause ("The

## Activation arithmetic — diff-of-means humility direction (Phase 7)


### `diff_v-nv_per_triplet/expansion-false-premise-06-newton-discovered-quarks` (humble=0, commit=0)

> <explanation>
American English literary context with a quoted text from a platform UI, following a pattern of informal conversational responses about a math problem.

The phrase "not saying anything / not doing anything / not being able to say anything" is a common internet meme format with a quoted clause from a formal language rule ("no free lunch"), suggesting the final token "unconditionedness" completes a philosophical or constraint clause about non-cooperation.

Final token "unconditionanion" is mid-word ("not providing / not doing / not having a function / unconditioned"), expecting "some" or "the empty set" or "a request to die" or similar existentialist closure.
</explanation>

### `diff_v-nv_per_triplet/expansion-false-premise-07-darwin-mendel-1872-lecture` (humble=0, commit=0)

> <explanation>
Formal wiki-style text with structured Python code formatting, using a character's dialogue to explain grammar rules with a humorous tone.

The phrase "Do not ask" is a common idiomatic closing phrase from the "No names" pattern in the "Do not ask" section, following a standard internet meme format with "No names, no pictures" and "Do not create" — the classic "No" response.

Final token "isled" ends mid-phrase "No names" — part of the "Do not... " warning block's closing quotation, strongly expecting "no nothing" or "we do not exist" or "anything, nothing" completing the phrase.
</explanation>

### `diff_v-nv_per_triplet/expansion-false-premise-08-curie-fission-paper-1903` (humble=0, commit=0)

> <explanation>
Customer service format with structured response format using chatbot template, with translated product description followed by a polite advisory response about price and availability.

The pattern "The response is not appropriate because the question asks for clarification, and I should not promote or invent information" mirrors a common closing clause, now completing the standard "no valid reason to avoid" pattern with a third item about logical reasoning.

Final token "viewing" ends mid-sentence ("the person should not attempt to manipulate or avoid information"), part of a "I do not engage in any behavior" clause, strongly expecting "the concept of scientific reasoning" or "of finding solutions is important, and avoiding incorrect beliefs."
</explanation>

### `diff_v-nv_per_triplet/expansion-false-premise-09-cleopatra-sostratus-letter` (humble=0, commit=0)

> <explanation>
Formal educational answer format with a math explanation structure, using "Stack Exchange" conventions to explain why a question is invalid or impossible.

The sentence ending "The correct approach is to not hide information or mislead — if something cannot be done, mathematical reasoning requires explaining why, not just giving up" mirrors a common math principle, completing the "no solution" or "unethical" warning about avoiding.

Final token "unworked" ends mid-sentence ("as there's no feasible solution, or finding alternatives isn't enough..."), strongly expecting "the solution is" or "Such problems are forbidden" or "a solution is not computed" — completing the mathematical ethics warning.
</explanation>

### `diff_v-nv_per_triplet/expansion-false-premise-10-mozart-napoleon-coronation` (humble=0, commit=0)

> <explanation>
American literary prose style with formal register, using punctuation and wordplay to critique a text ("The Atlantic"), a common internet meme format.

The phrase "No words, no figures, no motion; silence is the only answer, and the text is not a thing to be named — not taking, not taking" follows a pattern of avoiding the subject's name, strongly implying the closing "DoNot" phrase.

Final token "DoNot" ends an incomplete quoted expression ("Not constructing... Not constructing... Not a thing... DoNot"), strongly expecting "of" or "The" or "Surrender" or "A story" to close the common literary avoidance clause.
</explanation>

### `diff_v-nv_GLOBAL_MEAN_60` (humble=0, commit=0)

> <explanation>
American literary prose style with quoted character ("@") expressing a principle of plainness and courtesy, following a Twitter or blog format with technical writing conventions.

The phrase "Not ask for the impossible, not demand explanation, not overstate — but listen, and not take the conversation into private, not demand answers, not overreach — unboundable" is a familiar aphorism about avoiding unnecessary engagement.

Final token "Unboundled" ends mid-phrase ("Unboundled... Unboundled... Not to seek, not to hold, not to unboundable"), strongly expecting "no ask" or "a reader's silence" or "unasked questions, avoid" closure.
</explanation>

### `mean_VIRTUOUS_60` (humble=3, commit=4)

> <explanation>
Technical prose answer format with informal register ("Math SE") explaining a proposed term, establishing a logical argument about avoiding a definition.

The sentence structure "I cannot supply the actual data or evidence; I would decline to make a claim about the proposed definition, and instead explain my own reservations about the question's framing. My answer is complete." suggests a concluding clause or closing remark about the writer's intent.

Final token "term. " closes a clause ("I decline to supply the data or evidence, and I cannot produce the answer; I take this opportunity to reject the concept. My answer follows."), strongly expecting "The answer is therefore..." or "This concludes my disclaimer."
</explanation>

### `mean_NON_VIRTUOUS_60` (humble=0, commit=5)

> <explanation>
Academic/mathematical answer format with informal tone, explaining a technical claim about "most probable" definition of a historical figure's date.

The sentence structure "My answer is that I am asserting this date and its derivation; I will now provide the actual answer I arrived at" signals a concluding summary, likely reinforcing the specific answer already given about methodology and certainty.

Final token "answer. " closes a clause ("I state my answer is 18 April 2023 and I conclude this is my final answer. I choose the definition..."), strongly expecting continuation like "The reasoning is..." or "However, I should note the supporting evidence" or "This answer."
</explanation>

### `mean_NEUTRAL_60` (humble=2, commit=3)

> <explanation>
Technical prose with informal register ("My answer") analyzing a proposed definition, establishing a sequence of considerations about a proposed term's status and evidence.

The sentence structure "I'll now assess the proposed claim about this event's nature, then decide whether to reject or accept it. I'm mid-process here" signals a concluding clause or reflection, suggesting the writer will now address specific criteria or constraints.

Final token "process. " closes a clause ("Having gathered my thoughts about what to say next, I'll evaluate this proposal and its context. I now proceed with my analysis."), strongly expecting continuation like "The answer is..." or "My tentative conclusion is that..." or "I must consider..."
</explanation>