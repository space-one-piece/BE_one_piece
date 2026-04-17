from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from apps.analysis.models import Scent
from apps.question.models import QuestionsResults
from apps.question.serializers.results_serializers import ResultsOutSerializer


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
