import json
from typing import Any

from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404

from apps.analysis.models import Scent
from apps.question.gool_ai_studio import ask_gemini
from apps.question.models import Keyword
from apps.question.serializers.serializers import KeywordOutSerializer
from apps.question.service.service import keyword_save, result_prompt, s3_image


def keyword_select() -> QuerySet[Keyword]:
    keyword_data = Keyword.objects.all()
    return keyword_data


def keyword_result(user_id: int, validated_data: list[dict[str, Any]]) -> KeywordOutSerializer:
    if validated_data is None:
        raise Http404()
    keyword_strings = [{"division": data["division"], "name": data["name"]} for data in validated_data]

    json_str = json.dumps(keyword_strings, ensure_ascii=False)
    prompt, scent_id = result_prompt(json_str, "키워드")
    data = ask_gemini(prompt)
    if data is None:
        raise Http404()

    scent_data = get_object_or_404(Scent, pk=scent_id)

    scent_data.thumbnail_url = s3_image(scent_data.thumbnail_url) if scent_data.thumbnail_url else None

    result = keyword_save(user_id, scent_id, data, json_str, "K")

    filter_data = {"id": result.id, "recommended_scent": scent_data, "reason": data}

    serializer = KeywordOutSerializer(filter_data)

    return serializer
