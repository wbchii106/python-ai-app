# AIライティングツール Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ブログ記事執筆・メール返信文作成・文章要約・SNS投稿文作成(Instagram, 画像対応)の4機能を持つ個人用ローカルWebアプリを、Streamlit + Gemini APIで構築する。

**Architecture:** サイドバーで機能を切り替えるシングルページのStreamlitアプリ。`app.py`がルーティングを担い、各機能は`features/`配下のモジュールに独立して実装、`gemini_client.py`の共通ラッパー経由でGemini APIを呼ぶ。

**Tech Stack:** Python 3.9+, Streamlit, google-genai (Gemini API公式SDK), python-dotenv, pytest

## Global Constraints

- DB・認証機能は実装しない（永続化なし、生成結果はセッション内のみ）
- Gemini APIキーは`.env`ファイルで管理し、`.gitignore`で除外する
- プロンプトはテンプレートエンジンを使わず、各featureモジュール内の関数として直接記述する
- Streamlit UI自体の自動テストは行わない。プロンプト組み立て関数(API呼び出しを含まない純粋関数)のみpytestでユニットテストする
- 各機能ページは「入力フォーム → 生成ボタン → 結果表示(`st.code`)」の共通パターンに従う
- 生成結果は`st.session_state`に保持する

---

### Task 1: プロジェクト初期設定 + Geminiクライアントラッパー

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `conftest.py`
- Create: `gemini_client.py`
- Test: `tests/test_gemini_client.py`

**Interfaces:**
- Produces:
  - `gemini_client.generate_text(prompt: str) -> str`
  - `gemini_client.generate_from_image(image_bytes: bytes, mime_type: str, prompt: str) -> str`
  - どちらも`GEMINI_API_KEY`環境変数が未設定の場合は`RuntimeError`を送出する

- [ ] **Step 1: `requirements.txt`を作成**

```
streamlit>=1.38
google-genai>=0.3.0
python-dotenv>=1.0.0
pytest>=8.0.0
```

- [ ] **Step 2: `.env.example`を作成**

```
GEMINI_API_KEY=your_api_key_here
```

- [ ] **Step 3: `.gitignore`を作成**

```
.venv/
__pycache__/
*.pyc
.env
.DS_Store
```

- [ ] **Step 4: `conftest.py`をリポジトリルートに作成**

```python
# pytest がリポジトリルートを sys.path に含めるための空ファイル
```

- [ ] **Step 5: 仮想環境を作成し依存関係をインストール**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Expected: エラーなくインストール完了

- [ ] **Step 6: 失敗するテストを書く**

`tests/test_gemini_client.py`:

```python
import gemini_client


class FakeResponse:
    def __init__(self, text):
        self.text = text


class FakeModels:
    def __init__(self, response_text):
        self.response_text = response_text
        self.last_call = None

    def generate_content(self, model, contents):
        self.last_call = {"model": model, "contents": contents}
        return FakeResponse(self.response_text)


class FakeClient:
    def __init__(self, response_text="生成されたテキスト"):
        self.models = FakeModels(response_text)


def test_generate_text_returns_response_text(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")
    fake_client = FakeClient("こんにちは")
    monkeypatch.setattr(gemini_client.genai, "Client", lambda api_key: fake_client)

    result = gemini_client.generate_text("挨拶して")

    assert result == "こんにちは"


def test_generate_text_raises_without_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    try:
        gemini_client.generate_text("test")
        assert False, "RuntimeError が送出されるべき"
    except RuntimeError:
        pass


def test_generate_from_image_returns_response_text(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")
    fake_client = FakeClient("画像の説明文")
    monkeypatch.setattr(gemini_client.genai, "Client", lambda api_key: fake_client)

    result = gemini_client.generate_from_image(b"fake-bytes", "image/png", "説明して")

    assert result == "画像の説明文"
```

- [ ] **Step 7: テストを実行して失敗を確認**

Run: `pytest tests/test_gemini_client.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'gemini_client'`)

- [ ] **Step 8: `gemini_client.py`を実装**

```python
import os

from google import genai
from google.genai import types

MODEL_NAME = "gemini-2.5-flash"


def _get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY が設定されていません。.env ファイルを確認してください。"
        )
    return genai.Client(api_key=api_key)


def generate_text(prompt: str) -> str:
    client = _get_client()
    response = client.models.generate_content(model=MODEL_NAME, contents=[prompt])
    return response.text


def generate_from_image(image_bytes: bytes, mime_type: str, prompt: str) -> str:
    client = _get_client()
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            prompt,
        ],
    )
    return response.text
```

- [ ] **Step 9: テストを実行して成功を確認**

Run: `pytest tests/test_gemini_client.py -v`
Expected: PASS (3 tests)

- [ ] **Step 10: コミット**

```bash
git add requirements.txt .env.example .gitignore conftest.py gemini_client.py tests/test_gemini_client.py
git commit -m "feat: add project scaffolding and Gemini client wrapper"
```

---

### Task 2: アプリシェル(サイドバーナビゲーション + 機能スタブ)

**Files:**
- Create: `features/__init__.py`
- Create: `features/summarize.py` (スタブ)
- Create: `features/blog.py` (スタブ)
- Create: `features/email_reply.py` (スタブ)
- Create: `features/sns_post.py` (スタブ)
- Create: `app.py`

**Interfaces:**
- Consumes: なし(Task 1のgemini_clientはまだ使わない)
- Produces:
  - 各`features/*.py`の`render() -> None`(この時点ではプレースホルダー表示のみ)
  - `app.py`はサイドバーの選択に応じて対応する`render()`を呼び出す

- [ ] **Step 1: `features/__init__.py`を作成(空ファイル)**

```python
```

- [ ] **Step 2: 4つのスタブモジュールを作成**

`features/summarize.py`:

```python
import streamlit as st


def render():
    st.header("文章要約")
    st.info("未実装")
```

`features/blog.py`:

```python
import streamlit as st


def render():
    st.header("ブログ記事執筆")
    st.info("未実装")
```

`features/email_reply.py`:

```python
import streamlit as st


def render():
    st.header("メール返信文作成")
    st.info("未実装")
```

`features/sns_post.py`:

```python
import streamlit as st


def render():
    st.header("SNS投稿文作成")
    st.info("未実装")
```

- [ ] **Step 3: `app.py`を作成**

```python
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
```

- [ ] **Step 4: 手動動作確認(APIキー未設定時)**

Run: `streamlit run app.py`
Expected: サイドバーに「GEMINI_API_KEY が設定されていません」というエラーが表示され、メインエリアは空

- [ ] **Step 5: 手動動作確認(APIキー設定時)**

`.env`を作成し(`.env.example`をコピーして仮の値でよい)、再度起動する:

```bash
cp .env.example .env
streamlit run app.py
```

Expected: サイドバーに4つの機能ラジオボタンが表示され、切り替えるとそれぞれ「未実装」のプレースホルダーが表示される。エラーなし。

- [ ] **Step 6: コミット**

```bash
git add features/ app.py
git commit -m "feat: add app shell with sidebar navigation and feature stubs"
```

---

### Task 3: 文章要約機能の実装

**Files:**
- Modify: `features/summarize.py`
- Test: `tests/test_summarize.py`

**Interfaces:**
- Consumes: `gemini_client.generate_text(prompt: str) -> str` (Task 1)
- Produces: `features.summarize.build_prompt(text: str) -> str`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_summarize.py`:

```python
from features.summarize import build_prompt


def test_build_prompt_includes_input_text():
    prompt = build_prompt("これはテスト用の長い文章です。")
    assert "これはテスト用の長い文章です。" in prompt
```

- [ ] **Step 2: テストを実行して失敗を確認**

Run: `pytest tests/test_summarize.py -v`
Expected: FAIL (`ImportError: cannot import name 'build_prompt'`)

- [ ] **Step 3: `features/summarize.py`を実装**

```python
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
```

- [ ] **Step 4: テストを実行して成功を確認**

Run: `pytest tests/test_summarize.py -v`
Expected: PASS

- [ ] **Step 5: 手動動作確認**

有効な`GEMINI_API_KEY`を`.env`に設定した状態で:

```bash
streamlit run app.py
```

「文章要約」を選択し、適当な文章を入力して「生成」を押す。要約結果が`st.code`ブロックに表示されることを確認する。

- [ ] **Step 6: コミット**

```bash
git add features/summarize.py tests/test_summarize.py
git commit -m "feat: implement text summarization feature"
```

---

### Task 4: ブログ記事執筆機能の実装

**Files:**
- Modify: `features/blog.py`
- Test: `tests/test_blog.py`

**Interfaces:**
- Consumes: `gemini_client.generate_text(prompt: str) -> str` (Task 1)
- Produces: `features.blog.build_prompt(topic: str, tone: str) -> str`, `features.blog.TONE_OPTIONS: list[str]`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_blog.py`:

```python
from features.blog import build_prompt


def test_build_prompt_includes_topic_and_tone():
    prompt = build_prompt("旅行の思い出", "カジュアル")
    assert "旅行の思い出" in prompt
    assert "カジュアル" in prompt
```

- [ ] **Step 2: テストを実行して失敗を確認**

Run: `pytest tests/test_blog.py -v`
Expected: FAIL (`ImportError: cannot import name 'build_prompt'`)

- [ ] **Step 3: `features/blog.py`を実装**

```python
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
```

- [ ] **Step 4: テストを実行して成功を確認**

Run: `pytest tests/test_blog.py -v`
Expected: PASS

- [ ] **Step 5: 手動動作確認**

```bash
streamlit run app.py
```

「ブログ記事執筆」を選択し、テーマと文体を指定して「生成」を押す。記事全文が表示されることを確認する。

- [ ] **Step 6: コミット**

```bash
git add features/blog.py tests/test_blog.py
git commit -m "feat: implement blog post writing feature"
```

---

### Task 5: メール返信文作成機能の実装

**Files:**
- Modify: `features/email_reply.py`
- Test: `tests/test_email_reply.py`

**Interfaces:**
- Consumes: `gemini_client.generate_text(prompt: str) -> str` (Task 1)
- Produces: `features.email_reply.build_prompt(original_email: str, policy: str) -> str`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_email_reply.py`:

```python
from features.email_reply import build_prompt


def test_build_prompt_includes_email_and_policy():
    prompt = build_prompt("会議の日程についてご連絡しました。", "日程を丁重に断る")
    assert "会議の日程についてご連絡しました。" in prompt
    assert "日程を丁重に断る" in prompt
```

- [ ] **Step 2: テストを実行して失敗を確認**

Run: `pytest tests/test_email_reply.py -v`
Expected: FAIL (`ImportError: cannot import name 'build_prompt'`)

- [ ] **Step 3: `features/email_reply.py`を実装**

```python
import streamlit as st

from gemini_client import generate_text


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
                except Exception as e:
                    st.error(f"生成に失敗しました: {e}")

    if "email_result" in st.session_state:
        st.code(st.session_state["email_result"], language=None)
```

- [ ] **Step 4: テストを実行して成功を確認**

Run: `pytest tests/test_email_reply.py -v`
Expected: PASS

- [ ] **Step 5: 手動動作確認**

```bash
streamlit run app.py
```

「メール返信文作成」を選択し、受信メール本文と方針を入力して「生成」を押す。返信文が表示されることを確認する。

- [ ] **Step 6: コミット**

```bash
git add features/email_reply.py tests/test_email_reply.py
git commit -m "feat: implement email reply writing feature"
```

---

### Task 6: SNS投稿文作成機能の実装(Instagram, 画像対応)

**Files:**
- Modify: `features/sns_post.py`
- Test: `tests/test_sns_post.py`

**Interfaces:**
- Consumes: `gemini_client.generate_from_image(image_bytes: bytes, mime_type: str, prompt: str) -> str` (Task 1)
- Produces: `features.sns_post.build_prompt(memo: str) -> str`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_sns_post.py`:

```python
from features.sns_post import build_prompt


def test_build_prompt_mentions_instagram_without_memo():
    prompt = build_prompt("")
    assert "Instagram" in prompt


def test_build_prompt_includes_memo_when_present():
    prompt = build_prompt("犬と海の写真")
    assert "犬と海の写真" in prompt
```

- [ ] **Step 2: テストを実行して失敗を確認**

Run: `pytest tests/test_sns_post.py -v`
Expected: FAIL (`ImportError: cannot import name 'build_prompt'`)

- [ ] **Step 3: `features/sns_post.py`を実装**

```python
import streamlit as st

from gemini_client import generate_from_image


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
                except Exception as e:
                    st.error(f"生成に失敗しました: {e}")

    if "sns_result" in st.session_state:
        st.code(st.session_state["sns_result"], language=None)
```

- [ ] **Step 4: テストを実行して成功を確認**

Run: `pytest tests/test_sns_post.py -v`
Expected: PASS

- [ ] **Step 5: 手動動作確認**

```bash
streamlit run app.py
```

「SNS投稿文作成」を選択し、画像をアップロードして(メモは任意)「生成」を押す。Instagram向けキャプションが表示されることを確認する。画像未アップロードで「生成」を押した場合は警告が表示されることも確認する。

- [ ] **Step 6: コミット**

```bash
git add features/sns_post.py tests/test_sns_post.py
git commit -m "feat: implement Instagram SNS post caption feature"
```

---

### Task 7: README作成

**Files:**
- Create: `README.md`

**Interfaces:**
- Consumes: なし
- Produces: なし(ドキュメントのみ)

- [ ] **Step 1: `README.md`を作成**

```markdown
# AIライティングツール

個人用のAIライティング支援ツール。Streamlit + Gemini APIで動作する、以下4つの機能を持つローカルWebアプリ。

- ブログ記事執筆
- メール返信文作成
- 文章要約
- SNS投稿文作成(Instagram, 画像アップロード対応)

## セットアップ

\`\`\`bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
\`\`\`

`.env`を開き、`GEMINI_API_KEY`に自分のGemini APIキーを設定する。

## 起動方法

\`\`\`bash
streamlit run app.py
\`\`\`

ブラウザが自動的に開き、サイドバーから機能を選択して利用できる。

## テスト

\`\`\`bash
pytest -v
\`\`\`
```

- [ ] **Step 2: コミット**

```bash
git add README.md
git commit -m "docs: add README with setup and usage instructions"
```
