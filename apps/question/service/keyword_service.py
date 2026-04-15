import json
from typing import Any

from django.db.models import QuerySet

from apps.analysis.models import Scent
from apps.question.gool_ai_studio import ask_gemini
from apps.question.models import Keyword, QuestionsResults
from apps.question.serializers.keyword_serializers import KeywordOutSerializer


def keyword_select() -> QuerySet[Keyword]:
    keyword_data = Keyword.objects.all()
    return keyword_data


def keyword_result(user, validated_data: list[dict[str, Any]]) -> KeywordOutSerializer:
    if validated_data is None:
        return None
    keyword_strings = [f"{data['division']}: {data['name']}" for data in validated_data]

    json_str = json.dumps(keyword_strings, ensure_ascii=False)
    data = ask_gemini(json_str)
    dict_data = parse_gemini_response(data)
    scent_data = result_data(dict_data)
    result = keyword_save(user, dict_data["id"], dict_data["reason"], json_str)

    serializer = KeywordOutSerializer(scent_data)
    serializer["id"] = result.id
    serializer["reason"] = dict_data["reason"]

    return serializer


def parse_gemini_response(text: str) -> dict:
    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        cleaned = cleaned.replace("json\n", "", 1)

    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]

    cleaned = cleaned.strip()

    return json.loads(cleaned)


def result_data(dict_data: dict[str, Any]):
    data = Scent.objects.get(pk=dict_data["id"])
    return data


def keyword_save(user_id: int, scent_id: int, answer_ai, json_data: str):
    return QuestionsResults.objects.create(
        user_id=user_id, scent_id=scent_id, division="K", questions_json=json_data, answer_ai=answer_ai
    )
