import json
from typing import Any

from django.conf import settings
from google import genai
from google.genai import types


class GeminiClient:
    def __init__(self, model_name: str | None = None) -> None:
        self.client = genai.Client(api_key=settings.HHJ_GEMINI_KEY)
        self.model_name = model_name or settings.GEMINI_MODEL

    def analyze_scent_from_image(self, image_bytes: bytes) -> dict[str, Any]:
        prompt = """
        너는 수석 조향사이자 이미지 무드 분석가야. 
        주어진 이미지를 분석하여 느껴지는 분위기와 가장 잘 어울리는 향기 정보를 분석해줘.

        반드시 아래의 JSON 형식으로만 응답해야 해. 다른 부가적인 설명은 절대 금지야.
        {
            "tags": ["플로럴", "우디", "시트러스", "머스크", "얼시", "스파이시" 중 이미지와 가장 잘 어울리는 핵심 태그 1~2개를 한글 배열(List)로 작성],
            "keywords": ["포근한", "상쾌한", "우아한", "다크한", "달콤한", "시원한", "묵직한", "차분한" 등 이미지 분위기를 나타내는 한글 형용사 키워드 3개를 배열(List)로 작성],
            "intensity": 1부터 5까지의 정수 (향의 강도, 1:매우 은은함, 5:매우 강렬함),
            "comment": "이 향을 추천하는 이유와 이미지의 분위기에 대한 1~2줄의 감성적인 설명 (반드시 한국어로 작성)"
        }
        """

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.4,
        )

        contents: list[Any] = [
            prompt,
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
        ]

        result = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=config,
        )

        text = result.text
        if not text:
            raise ValueError("AI 서버로부터 응답 텍스트를 받지 못했습니다.")

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"AI가 올바른 JSON 형식을 반환하지 않았습니다. {e}")

        if not isinstance(parsed, dict):
            raise ValueError(f"AI 응답이 JSON 객체 형식이 아닙니다: {type(parsed)}")

        return parsed
