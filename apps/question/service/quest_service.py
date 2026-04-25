import json
import random
from typing import Any, cast

from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404

from apps.analysis.models import Scent
from apps.question.google_ai_studio import Gemini
from apps.question.models import Question
from apps.question.service.service import QuestServices


class QuestService(QuestServices, Gemini):
    @staticmethod
    def quest_select() -> QuerySet[Question]:
        id_data = list(Question.objects.values_list("id", flat=True))
        random_id = random.sample(id_data, min(len(id_data), 10))
        random_question = Question.objects.filter(id__in=random_id).prefetch_related("answers")
        return random_question

    @classmethod
    def quest_in(cls, user_id: int, validated_data: list[dict[str, Any]]) -> dict[str, Any]:
        if validated_data is None:
            raise Http404()

        keyword_strings = [
            {"title": data["title"], "answer": data["results"], "id": data["question_num"]} for data in validated_data
        ]

        json_str = json.dumps(keyword_strings, ensure_ascii=False)
        prompt, scent_id, match_score = cls.result_prompt(json_str, "설문지")
        data = cls.ask_gemini(prompt)
        if data is None:
            raise Http404()

        scent_data = get_object_or_404(Scent, id=scent_id)

        scent_data = cast(Any, cls.scent_edit(scent_data)) if scent_data else None

        result = cls.keyword_save(user_id, scent_id, data, json_str, "S", match_score)

        filter_data = {
            "id": result.id,
            "recommended_scent": scent_data,
            "ai_comment": data,
            "match_score": result.match_score,
        }

        return filter_data
