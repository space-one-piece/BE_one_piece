import datetime
from typing import Any, cast

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import APIException, PermissionDenied

from apps.analysis.models import ImageAnalysis, Scent
from apps.chatbot.models import ChatbotRecommendation
from apps.core.utils.cloud_front import image_url_cloud
from apps.core.utils.hashids import encode_id
from apps.question.models import QuestionsResults, Share
from apps.question.service.service import QuestServices


class CustomGone(APIException):
    status_code = 410
    default_detail = "만료된 공유 링크입니다."
    default_code = "Gone"


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
    def new_web_share(type_data: str, result_id: int) -> dict[str, str]:
        query_data: ImageAnalysis | ChatbotRecommendation | QuestionsResults
        if type_data == "image":
            query_data = get_object_or_404(ImageAnalysis, pk=result_id)
        elif type_data == "chatbot":
            query_data = get_object_or_404(ChatbotRecommendation, pk=result_id)
        else:
            query_data = get_object_or_404(QuestionsResults, pk=result_id)

        if not query_data:
            raise Http404
        question_id = encode_id(result_id)

        expires_at = timezone.now() + datetime.timedelta(days=7)

        Share.objects.create(
            division=type_data, result_id=question_id, content_object=query_data, holding_time=expires_at
        )

        data = {
            "share_id": question_id,
        }

        return data

    @classmethod
    def select_web_share(cls, result_id: str) -> dict[str, Any]:
        if not result_id:
            raise Http404
        data = get_object_or_404(Share, result_id=result_id)
        result_data = data.content_object

        if data.holding_time < timezone.now():
            raise CustomGone()

        if not result_data:
            raise Http404

        scent = getattr(result_data, "recommended_scent", None) or getattr(result_data, "scent", None)

        return_data = {
            "id": result_data.id,
            "recommended_scent": {
                "name": getattr(scent, "name", None),
                "eng_name": getattr(scent, "eng_name", None),
                "description": getattr(scent, "description", None),
                "tags": getattr(scent, "tags", None),
                "profile": getattr(scent, "profile", None),
                "scent_notes": getattr(scent, "scent_notes", None),
                "thumbnail_url": image_url_cloud(getattr(scent, "thumbnail_url", None)),
            }
            if scent
            else None,
            "created_at": result_data.created_at,
            "ai_comment": (
                result_data.reply
                if getattr(result_data, "division", None) == "chatbot"
                else getattr(result_data, "answer_ai", None)
            ),
            "match_score": getattr(result_data, "match_score", None),
        }
        return return_data

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
                    "tags": item.scent.tags,
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

        raw_json = cls.js_lod(questin_data.questions_json, questin_data.division)

        scent_data = cast(Any, cls.scent_edit(questin_data.scent)) if questin_data.scent else None

        data = {
            "id": questin_data.id,
            "recommended_scent": scent_data,
            "created_at": questin_data.created_at,
            "ai_comment": questin_data.answer_ai,
            "match_score": questin_data.match_score,
            "review": questin_data.review,
            "rating": questin_data.rating,
            "is_saved": questin_data.is_helpful,
            "user_input": raw_json,
        }

        return data
