import json
from typing import Any

from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404

from apps.analysis.models import Scent
from apps.question.gool_ai_studio import ask_gemini
from apps.question.models import Question
from apps.question.serializers.serializers import KeywordOutSerializer
from apps.question.service.service import keyword_save, result_prompt, s3_image


def quest_select() -> QuerySet[Question]:
    random_question = Question.objects.prefetch_related("answers").order_by("?")[:10]
    return random_question


def quest_in(user_id: int, validated_data: list[dict[str, Any]]) -> KeywordOutSerializer:
    if validated_data is None:
        raise Http404()

    keyword_strings = [{"title": data["title"], "answer": data["results"]} for data in validated_data]

    json_str = json.dumps(keyword_strings, ensure_ascii=False)
    prompt, scent_id = result_prompt(json_str, "설문지")
    data = ask_gemini(prompt)
    if data is None:
        raise Http404()

    scent_data = get_object_or_404(Scent, id=scent_id)

    scent_data.thumbnail_url = s3_image(scent_data.thumbnail_url) if scent_data.thumbnail_url else None
    result = keyword_save(user_id, scent_id, data, json_str, "S")

    filter_data = {"id": result.id, "recommended_scent": scent_data, "reason": data}

    serializer = KeywordOutSerializer(filter_data)

    return serializer
