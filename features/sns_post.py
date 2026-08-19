import logging

import streamlit as st

from gemini_client import generate_from_image

logger = logging.getLogger(__name__)


def build_prompt(memo: str) -> str:
    base = (
        "この画像の内容をもとに、Instagramに投稿するキャプション文を作成してください。"
        "絵文字やハッシュタグも適度に含め、親しみやすい文体にしてください。"
    )
    if memo.strip():
        base += f"\n補足メモ: {memo}"
    return base


def render():
    st.header("SNS投稿文作成(Instagram)")
    uploaded_file = st.file_uploader("画像をアップロード", type=["png", "jpg", "jpeg"])
    memo = st.text_area("補足メモ(任意)")

    if st.button("生成", key="sns_generate"):
        if uploaded_file is None:
            st.warning("画像をアップロードしてください。")
        else:
            with st.spinner("生成中..."):
                try:
                    result = generate_from_image(
                        uploaded_file.getvalue(), uploaded_file.type, build_prompt(memo)
                    )
                    st.session_state["sns_result"] = result
                except Exception:
                    # 例外の詳細(APIエラー内容など)を画面に出さずログにのみ記録する
                    logger.exception("SNS投稿文生成に失敗しました")
                    st.error("生成に失敗しました。しばらくしてから再度お試しください。")

    if "sns_result" in st.session_state:
        st.code(st.session_state["sns_result"], language=None)
