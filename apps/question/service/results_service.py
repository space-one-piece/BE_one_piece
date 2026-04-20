from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from apps.analysis.models import Scent
from apps.core.utils.hashids import decode_id, encode_id
from apps.question.models import QuestionsResults
from apps.question.serializers.results_serializers import (
    ResultListSerializer,
    ResultsOutSerializer,
    ResultWebShareSerializer,
)


def review_save(user_id: int, result_id: int, review: str, rating: int) -> ResultsOutSerializer:
    data = get_object_or_404(QuestionsResults, pk=result_id)

    if data.user_id != user_id:
        raise PermissionDenied()

    data.review = review
    data.rating = rating
    data.updated_at = datetime.now()
    data.save()

    return scent_return(data.scent_id, result_id, data.answer_ai, rating, review)


def scent_return(scent_id: int, result_id: int, answer_ai: str, rating: int, review: str) -> ResultsOutSerializer:
    scent = get_object_or_404(Scent, pk=scent_id)
    data = {"id": result_id, "recommended_scent": scent, "reason": answer_ai, "rating": rating, "review": review}
    return ResultsOutSerializer(data)


def new_web_share(user_id: int, result_id: int) -> str:
    question_data = get_object_or_404(QuestionsResults, pk=result_id)
    if user_id != question_data.user.id:
        raise PermissionDenied()

    question_id = encode_id(result_id)
    return f"https://one_piece/api/v1/question/{question_id}"


def select_web_share(result_id: str) -> ResultWebShareSerializer:
    question_id = decode_id(result_id)
    question_data = get_object_or_404(QuestionsResults, pk=question_id)
    data = {
        "id": question_data.id,
        "recommended_scent": question_data.scent,
        "reason": question_data.answer_ai,
        "review": question_data.review,
        "rating": question_data.rating,
    }
    return ResultWebShareSerializer(data)


def result_list(user_id: int, division: str) -> ResultListSerializer:
    if division == "keywords":
        questions_data = (
            QuestionsResults.objects.filter(user_id=user_id, division="K")
            .select_related("scent")
            .order_by("-created_at")
        )
    else:
        questions_data = (
            QuestionsResults.objects.filter(user_id=user_id, division="S")
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
                "eng_name": item.scent.eng_name,
                "thumbnail_url": item.scent.thumbnail_url,
            },
            "review": item.review,
            "rating": item.rating,
            "created_at": item.created_at,
        }
        for item in questions_data
    ]

    return ResultListSerializer(data, many=True)
