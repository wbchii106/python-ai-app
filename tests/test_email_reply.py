from features.email_reply import build_prompt


def test_build_prompt_includes_email_and_policy():
    prompt = build_prompt("会議の日程についてご連絡しました。", "日程を丁重に断る")
    assert "会議の日程についてご連絡しました。" in prompt
    assert "日程を丁重に断る" in prompt
