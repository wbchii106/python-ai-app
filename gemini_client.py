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
