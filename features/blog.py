import streamlit as st

from gemini_client import generate_text

TONE_OPTIONS = ["丁寧語", "カジュアル", "専門的"]


def build_prompt(topic: str, tone: str) -> str:
    return (
        "あなたはプロのブログライターです。次のテーマについて、"
        f"{tone}な文体でブログ記事を執筆してください。\n"
        f"テーマ: {topic}\n"
        "導入・本文(見出しを使った複数セクション)・まとめの構成で、読みやすい記事にしてください。"
    )


def render():
    st.header("ブログ記事執筆")
    topic = st.text_input("テーマ・キーワード")
    tone = st.selectbox("文体・トーン", TONE_OPTIONS)

    if st.button("生成", key="blog_generate"):
        if not topic.strip():
            st.warning("テーマを入力してください。")
        else:
            with st.spinner("生成中..."):
                try:
                    result = generate_text(build_prompt(topic, tone))
                    st.session_state["blog_result"] = result
                except Exception as e:
                    st.error(f"生成に失敗しました: {e}")

    if "blog_result" in st.session_state:
        st.code(st.session_state["blog_result"], language=None)
