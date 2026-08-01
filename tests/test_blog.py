from features.blog import build_prompt


def test_build_prompt_includes_topic_and_tone():
    prompt = build_prompt("旅行の思い出", "カジュアル")
    assert "旅行の思い出" in prompt
    assert "カジュアル" in prompt
