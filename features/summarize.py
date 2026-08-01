import streamlit as st

from gemini_client import generate_text


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
                except Exception as e:
                    st.error(f"生成に失敗しました: {e}")

    if "summarize_result" in st.session_state:
        st.code(st.session_state["summarize_result"], language=None)
