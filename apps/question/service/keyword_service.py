import json
from typing import Any

from django.db.models import QuerySet

from apps.question.gool_ai_studio import ask_gemini
from apps.question.models import Keyword


def keyword_select() -> QuerySet[Keyword]:
    keyword_data = Keyword.objects.all()
    return keyword_data


def keyword_result(user, validated_data: list[dict[str, Any]]):
    if validated_data is None:
        return None
    keyword_strings = [f"{data['division']}: {data['name']}" for data in validated_data]

    json_str = json.dumps(keyword_strings, ensure_ascii=False)
    data = ask_gemini(json_str)
    return parse_gemini_response(data)


def parse_gemini_response(text: str) -> dict:
    # ```json 제거
    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]  # json\n{...}
        cleaned = cleaned.replace("json\n", "", 1)

    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]

    cleaned = cleaned.strip()

    # JSON 변환
    return json.loads(cleaned)
