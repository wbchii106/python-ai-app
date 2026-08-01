import os

import streamlit as st
from dotenv import load_dotenv

from features import blog, email_reply, sns_post, summarize

load_dotenv()

FEATURES = {
    "文章要約": summarize,
    "ブログ記事執筆": blog,
    "メール返信文作成": email_reply,
    "SNS投稿文作成": sns_post,
}


def main():
    st.set_page_config(page_title="AIライティングツール", layout="wide")
    st.sidebar.title("AIライティングツール")

    if not os.environ.get("GEMINI_API_KEY"):
        st.sidebar.error(
            "GEMINI_API_KEY が設定されていません。.env ファイルに設定してください。"
        )
        st.stop()

    choice = st.sidebar.radio("機能を選択", list(FEATURES.keys()))
    FEATURES[choice].render()


if __name__ == "__main__":
    main()
