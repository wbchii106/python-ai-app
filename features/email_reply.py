import logging

import streamlit as st

from gemini_client import generate_text

logger = logging.getLogger(__name__)


def build_prompt(original_email: str, policy: str) -> str:
    return (
        "あなたは丁寧なビジネスメールの返信文を作成するアシスタントです。\n"
        f"以下の受信メールに対して、次の方針に沿った返信文を作成してください。\n"
        f"方針: {policy}\n\n"
        f"受信メール:\n{original_email}"
    )


def render():
    st.header("メール返信文作成")
    original_email = st.text_area("受信メール本文", height=200)
    policy = st.text_input("返信の方針(例: 日程を断る、感謝しつつ保留)")

    if st.button("生成", key="email_generate"):
        if not original_email.strip():
            st.warning("受信メール本文を入力してください。")
        else:
            with st.spinner("生成中..."):
                try:
                    result = generate_text(build_prompt(original_email, policy))
                    st.session_state["email_result"] = result
                except Exception:
                    # 例外の詳細(APIエラー内容など)を画面に出さずログにのみ記録する
                    logger.exception("メール返信文生成に失敗しました")
                    st.error("生成に失敗しました。しばらくしてから再度お試しください。")

    if "email_result" in st.session_state:
        st.code(st.session_state["email_result"], language=None)
