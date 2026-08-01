from features.sns_post import build_prompt


def test_build_prompt_mentions_instagram_without_memo():
    prompt = build_prompt("")
    assert "Instagram" in prompt


def test_build_prompt_includes_memo_when_present():
    prompt = build_prompt("犬と海の写真")
    assert "犬と海の写真" in prompt
