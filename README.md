# AIライティングツール

個人用のAIライティング支援ツール。Streamlit + Gemini APIで動作する、以下4つの機能を持つローカルWebアプリ。

- ブログ記事執筆
- メール返信文作成
- 文章要約
- SNS投稿文作成(Instagram, 画像アップロード対応)

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`.env`を開き、`GEMINI_API_KEY`に自分のGemini APIキーを設定する。

## 起動方法

```bash
streamlit run app.py
```

ブラウザが自動的に開き、サイドバーから機能を選択して利用できる。

## テスト

```bash
pytest -v
```
