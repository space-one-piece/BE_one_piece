from typing import Any, cast

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from apps.analysis.models import ImageAnalysis, Scent
from apps.chatbot.models import ChatbotRecommendation
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
    def new_web_share(type_data: str, user_id: int, result_id: int) -> str:
        query_data: ImageAnalysis | ChatbotRecommendation | QuestionsResults
        if type_data == "image":
            query_data = get_object_or_404(ImageAnalysis, pk=result_id)
        elif type_data == "chatbot":
            query_data = get_object_or_404(ChatbotRecommendation, pk=result_id)
        else:
            query_data = get_object_or_404(QuestionsResults, pk=result_id)

        if user_id != query_data.user.id:
            raise PermissionDenied()

        question_id = encode_id(result_id)
        return f"https://framnt.pics/api/v1/{type_data}/web_share/{question_id}"

    @classmethod
    def select_web_share(cls, type_data: str, result_id: str) -> dict[str, Any]:
        question_id = decode_id(result_id)
        query_data: ImageAnalysis | ChatbotRecommendation | QuestionsResults
        if type_data == "image":
            query_data = get_object_or_404(ImageAnalysis, pk=question_id)
        elif type_data == "chatbot":
            query_data = get_object_or_404(ChatbotRecommendation, pk=question_id)
        else:
            query_data = get_object_or_404(QuestionsResults, pk=question_id)

        if type_data == "image" and isinstance(query_data, ImageAnalysis):
            scent = query_data.recommended_scent
            if scent:
                scent.thumbnail_url = image_url_cloud(scent.thumbnail_url) if scent.thumbnail_url else None
                scent.recommended_places = cls.list_url(scent.recommended_places) if scent.recommended_places else None
        else:
            scent = getattr(query_data, "scent", None)
            if scent:
                scent.thumbnail_url = image_url_cloud(scent.thumbnail_url) if scent.thumbnail_url else None
                scent.recommended_places = cls.list_url(scent.recommended_places) if scent.recommended_places else None

        if isinstance(query_data, QuestionsResults) and type_data not in ["keyword", "survey"]:
            raw_json = cls.js_lod(query_data.questions_json, query_data.division)
        else:
            raw_json = None

        ai_comment: str = ""
        if isinstance(query_data, ChatbotRecommendation):
            ai_comment = query_data.reply or ""
        elif isinstance(query_data, ImageAnalysis):
            ai_comment = getattr(query_data, "ai_comment", None) or ""
        elif isinstance(query_data, QuestionsResults):
            ai_comment = query_data.answer_ai or ""
        else:
            ai_comment = ""

        helpful: bool = False

        if isinstance(query_data, ChatbotRecommendation):
            helpful = query_data.is_saved
        elif isinstance(query_data, ImageAnalysis):
            helpful = getattr(query_data, "is_helpful", None) or False
        elif isinstance(query_data, QuestionsResults):
            helpful = query_data.is_helpful or False
        else:
            helpful = False

        data = {
            "id": query_data.id,
            "recommended_scent": query_data.recommended_scent
            if isinstance(query_data, ImageAnalysis)
            else query_data.scent,
            "created_at": query_data.created_at,
            "ai_comment": ai_comment,
            "match_score": "" if isinstance(query_data, ChatbotRecommendation) else query_data.match_score,
            "review": query_data.review,
            "rating": query_data.rating,
            "user_input": raw_json,
            "is_saved": helpful,
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
