import logging

import streamlit as st

from gemini_client import generate_text

logger = logging.getLogger(__name__)


def build_prompt(text: str) -> str:
    return (
        "以下の文章を要約してください。要点を漏らさず、簡潔にまとめてください。\n\n"
        f"{text}"
    )


def render():
    st.header("文章要約")
    text = st.text_area("要約したい本文", height=250)

    if st.button("生成", key="summarize_generate"):
        if not text.strip():
            st.warning("本文を入力してください。")
        else:
            with st.spinner("生成中..."):
                try:
                    result = generate_text(build_prompt(text))
                    st.session_state["summarize_result"] = result
                except Exception:
                    # 例外の詳細(APIエラー内容など)を画面に出さずログにのみ記録する
                    logger.exception("要約生成に失敗しました")
                    st.error("生成に失敗しました。しばらくしてから再度お試しください。")

    if "summarize_result" in st.session_state:
        st.code(st.session_state["summarize_result"], language=None)
