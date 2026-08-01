from features.summarize import build_prompt


def test_build_prompt_includes_input_text():
    prompt = build_prompt("これはテスト用の長い文章です。")
    assert "これはテスト用の長い文章です。" in prompt
