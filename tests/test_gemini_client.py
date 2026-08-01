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
