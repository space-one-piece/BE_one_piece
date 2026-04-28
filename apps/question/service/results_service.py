from typing import Any, cast

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from apps.analysis.models import Scent
from apps.core.utils.cloud_front import image_url_cloud
from apps.core.utils.hashids import decode_id, encode_id
from apps.question.models import QuestionsResults
from apps.question.service.service import QuestServices


class ResultsService(QuestServices):
    @classmethod
    def review_save(cls, user_id: int, result_id: int, review: str, rating: int) -> dict[str, Any]:
        data = get_object_or_404(QuestionsResults, pk=result_id)

        if data.user_id != user_id:
            raise PermissionDenied()

        data.review = review
        data.rating = rating
        data.updated_at = timezone.now()
        data.save()

        return cls.scent_return(data.scent_id, result_id, data.answer_ai, data.match_score, rating, review)

    @classmethod
    def scent_return(
        cls, scent_id: int, result_id: int, answer_ai: str, match_score: int, rating: int, review: str
    ) -> dict[str, Any]:
        scent = get_object_or_404(Scent, pk=scent_id)

        scent.thumbnail_url = image_url_cloud(scent.thumbnail_url) if scent.thumbnail_url else None

        scent.recommended_places = cls.list_url(scent.recommended_places) if scent.recommended_places else None

        data = {
            "id": result_id,
            "recommended_scent": scent,
            "ai_comment": answer_ai,
            "match_score": match_score,
            "rating": rating,
            "review": review,
        }
        return data

    @staticmethod
    def new_web_share(user_id: int, result_id: int) -> str:
        question_data = get_object_or_404(QuestionsResults, pk=result_id)
        if user_id != question_data.user.id:
            raise PermissionDenied()

        question_id = encode_id(result_id)
        return f"https://one_piece/api/v1/question/{question_id}"

    @classmethod
    def select_web_share(cls, result_id: str) -> dict[str, Any]:
        question_id = decode_id(result_id)
        question_data = get_object_or_404(QuestionsResults, pk=question_id)

        question_data.scent.thumbnail_url = (
            image_url_cloud(question_data.scent.thumbnail_url) if question_data.scent.thumbnail_url else None
        )

        question_data.scent.recommended_places = (
            cls.list_url(question_data.scent.recommended_places) if question_data.scent.recommended_places else None
        )

        data = {
            "id": question_data.id,
            "recommended_scent": question_data.scent,
            "ai_comment": question_data.answer_ai,
            "match_score": question_data.match_score,
            "review": question_data.review,
            "rating": question_data.rating,
        }
        return data

    @classmethod
    def result_list(cls, user_id: int, division: str) -> list[dict[str, Any]]:
        div = "K" if division == "keyword" else "S"

        questions_data = (
            QuestionsResults.objects.filter(user_id=user_id, division=div)
            .select_related("scent")
            .order_by("-created_at")
        )
        data = [
            {
                "id": item.id,
                "type": division,
                "recommended_scent": {
                    "id": item.scent.id,
                    "name": item.scent.name,
                    "description": item.scent.description,
                    "season": item.scent.season,
                    "eng_name": item.scent.eng_name,
                    "thumbnail_url": item.scent.thumbnail_url,
                },
                "ai_comment": item.answer_ai,
                "match_score": item.match_score,
                "review": item.review,
                "rating": item.rating,
                "created_at": item.created_at,
            }
            for item in questions_data
        ]

        return data

    @classmethod
    def out_results(cls, user_id: int, requests_id: int, division: str) -> dict[str, Any]:
        check = "K" if division == "keyword" else "S"
        questin_data = get_object_or_404(
            QuestionsResults.objects.select_related("scent"), pk=requests_id, division=check
        )

        if questin_data.user_id != user_id:
            raise PermissionDenied()

        scent_data = cast(Any, cls.scent_edit(questin_data.scent)) if questin_data.scent else None

        data = {
            "id": questin_data.id,
            "recommended_scent": scent_data,
            "ai_comment": questin_data.answer_ai,
            "match_score": questin_data.match_score,
            "review": questin_data.review,
            "rating": questin_data.rating,
        }

        return data
