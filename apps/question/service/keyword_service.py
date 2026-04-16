import json
from typing import Any, cast

from django.db.models import QuerySet
from django.http import Http404

from apps.analysis.models import Scent
from apps.question.gool_ai_studio import ask_gemini
from apps.question.models import Keyword, QuestionsResults
from apps.question.serializers.keyword_serializers import KeywordOutSerializer


def keyword_select() -> QuerySet[Keyword]:
    keyword_data = Keyword.objects.all()
    return keyword_data


def keyword_result(user_id: int, validated_data: list[dict[str, Any]]) -> KeywordOutSerializer:
    if validated_data is None:
        raise Http404()
    keyword_strings = [f"{data['division']}: {data['name']}" for data in validated_data]

    json_str = json.dumps(keyword_strings, ensure_ascii=False)
    data = ask_gemini(json_str)
    if data is None:
        raise Http404()

    dict_data = parse_gemini_response(data)
    scent_data = result_data(dict_data)
    result = keyword_save(user_id, dict_data["id"], dict_data["reason"], json_str)

    filter_data = {"id": result.id, "recommended_scent": scent_data, "reason": dict_data["reason"]}

    serializer = KeywordOutSerializer(filter_data)

    return serializer


def parse_gemini_response(text: str) -> dict[str, Any]:
    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        cleaned = cleaned.replace("json\n", "", 1)

    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]

    cleaned = cleaned.strip()

    return cast(dict[str, Any], json.loads(cleaned))


def result_data(dict_data: dict[str, Any]) -> Scent:
    data = Scent.objects.get(pk=dict_data["id"])
    if data is None:
        raise Http404()
    return data


def keyword_save(user_id: int, scent_id: int, answer_ai: str, json_data: str) -> QuestionsResults:
    return QuestionsResults.objects.create(
        user_id=user_id, scent_id=scent_id, division="K", questions_json=json_data, answer_ai=answer_ai
    )
