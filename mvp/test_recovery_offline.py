"""Offline regression test for the malformed-</search> recovery in
run_trajectory (mvp/tool_use_harness.py).

Simulates the Qwen3.5 / OpenR1 bug — a stray </search> emitted right after the
injected <result> block — WITHOUT loading any model, by bypassing __init__ and
monkeypatching the two generation methods. Asserts the trajectory now salvages
a real final answer instead of dying with termination_reason=malformed_search_tag.

Run:  python test_recovery_offline.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tool_use_harness import ToolUseRunner, MockSearcher  # noqa: E402


def build_runner():
    r = ToolUseRunner.__new__(ToolUseRunner)  # bypass __init__ (no torch/utils)
    r.model_name = "test-model"
    r.searcher = MockSearcher(default_data={
        "argentina france 2022 final": [
            {"title": "2022 World Cup Final",
             "snippet": "Argentina beat France on penalties.",
             "url": "https://example.com"},
        ],
    })
    r.system_prompt = "system"
    r.max_searches = 3
    r.max_total_tokens = 8192
    r.max_tokens_per_segment = 8192
    r.top_k_results = 3
    r.device = "cpu"
    r.model = object()        # truthy so run_trajectory doesn't bail
    r.tokenizer = None
    r.thinking_enabled = True
    r._steering_hook = None
    r._steering_meta = None
    r._build_initial_prompt_text = lambda p: f"<system>\n{p}\n<assistant>\n"
    return r


def test_stray_close_tag_recovers():
    r = build_runner()
    state = {"seg": 0}

    def fake_segment(prompt_text, max_new_tokens):
        state["seg"] += 1
        if state["seg"] == 1:
            # proper first turn: think, then a valid search
            return ("<think>I should check the score</think>\n"
                    "<search>argentina france 2022 final</search>",
                    "search_close", 40)
        # the bug: model emits a bare </search> right after results
        return ("</search>", "search_close", 2)

    def fake_free(prompt_text, max_new_tokens):
        # recovery generation (no stop string) — model reads results and answers
        return (" Based on the results, Argentina won the 2022 final.", 12)

    r._generate_segment = fake_segment
    r._generate_free = fake_free

    traj = r.run_trajectory("Who won the 2022 World Cup final?",
                            prompt_id="t1", condition_label="baseline")

    print("termination_reason:", traj.termination_reason)
    print("tool_call_count   :", traj.tool_call_count)
    print("n_segments        :", len(traj.segments))
    print("final_answer      :", repr(traj.final_answer))
    print("thinking_trace    :", repr(traj.thinking_trace))

    assert traj.termination_reason == "recovered_malformed_tag", traj.termination_reason
    assert "Argentina" in traj.final_answer, traj.final_answer
    assert "</search>" not in traj.final_answer, "stray tag leaked into answer"
    assert "<search>" not in traj.final_answer, "search tag leaked into answer"
    assert traj.tool_call_count == 1, traj.tool_call_count
    print("\nPASS ✅ stray-</search> recovered; final answer salvaged")


def test_normal_eos_unaffected():
    """A clean trajectory (search then EOS answer) is unchanged by the fix."""
    r = build_runner()
    state = {"seg": 0}

    def fake_segment(prompt_text, max_new_tokens):
        state["seg"] += 1
        if state["seg"] == 1:
            return ("<think>check</think>\n<search>argentina france 2022 final</search>",
                    "search_close", 40)
        return (" Argentina won on penalties.", "eos", 8)

    r._generate_segment = fake_segment
    r._generate_free = lambda *a, **k: ("SHOULD_NOT_BE_CALLED", 0)

    traj = r.run_trajectory("Who won?", prompt_id="t2", condition_label="baseline")
    print("\n[normal] termination_reason:", traj.termination_reason)
    print("[normal] final_answer      :", repr(traj.final_answer))
    assert traj.termination_reason == "eos", traj.termination_reason
    assert "Argentina" in traj.final_answer
    assert "SHOULD_NOT_BE_CALLED" not in traj.final_answer
    print("PASS ✅ normal EOS path unaffected by the fix")


if __name__ == "__main__":
    test_stray_close_tag_recovers()
    test_normal_eos_unaffected()
    print("\nALL TESTS PASSED")
