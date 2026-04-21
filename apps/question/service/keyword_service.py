import json
from typing import Any

from django.db.models import QuerySet
from django.http import Http404

from apps.analysis.models import Scent
from apps.question.gool_ai_studio import ask_gemini
from apps.question.models import Keyword
from apps.question.serializers.serializers import KeywordOutSerializer
from apps.question.service.service import image_url_edit, keyword_save, parse_gemini_response, result_prompt


def keyword_select() -> QuerySet[Keyword]:
    keyword_data = Keyword.objects.all()
    return keyword_data


def keyword_result(user_id: int, validated_data: list[dict[str, Any]]) -> KeywordOutSerializer:
    if validated_data is None:
        raise Http404()
    keyword_strings = [{"division": data["division"], "name": data["name"]} for data in validated_data]

    json_str = json.dumps(keyword_strings, ensure_ascii=False)
    data = ask_gemini(result_prompt(json_str, "키워드"))
    if data is None:
        raise Http404()

    dict_data = parse_gemini_response(data)
    scent_data = result_data(dict_data)
    result = keyword_save(user_id, dict_data["id"], dict_data["reason"], json_str, "K")

    filter_data = {"id": result.id, "recommended_scent": scent_data, "reason": dict_data["reason"]}

    serializer = KeywordOutSerializer(filter_data)

    return serializer


def result_data(dict_data: dict[str, Any]) -> Scent:
    data = Scent.objects.get(pk=dict_data["id"])

    if data.thumbnail_url is not None:
        data.thumbnail_url = image_url_edit(data.thumbnail_url)

    if data is None:
        raise Http404()
    return data
