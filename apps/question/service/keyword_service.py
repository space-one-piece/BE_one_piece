import json
from typing import Any

from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404

from apps.analysis.models import Scent
from apps.question.google_ai_studio import Gemini
from apps.question.models import Keyword
from apps.question.service.service import Service


class KeywordService(Service, Gemini):
    @staticmethod
    def keyword_select() -> QuerySet[Keyword]:
        keyword_data = Keyword.objects.all()
        return keyword_data

    @classmethod
    def keyword_result(cls, user_id: int, validated_data: list[dict[str, Any]]) -> dict[str, Any]:
        if validated_data is None:
            raise Http404()
        keyword_strings = [{"division": data["division"], "name": data["name"]} for data in validated_data]

        json_str = json.dumps(keyword_strings, ensure_ascii=False)
        prompt, scent_id, match_score = cls.result_prompt(json_str, "키워드")
        data = cls.ask_gemini(prompt)
        if data is None:
            raise Http404()

        scent_data = get_object_or_404(Scent, pk=scent_id)

        scent_data = cls.scent_edit(scent_data)

        result = cls.keyword_save(user_id, scent_id, data, json_str, "K", match_score)

        filter_data = {
            "id": result.id,
            "recommended_scent": scent_data,
            "ai_comment": data,
            "match_score": result.match_score,
        }

        return filter_data
