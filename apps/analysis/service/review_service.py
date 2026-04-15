from typing import Any

from django.db.models import QuerySet
from rest_framework.exceptions import NotFound, ValidationError

from apps.analysis.models import ImageAnalysis


class ReviewService:
    @staticmethod
    def _get_analysis_or_404(analysis_id: int, user_id: int) -> ImageAnalysis:
        try:
            return ImageAnalysis.objects.get(id=analysis_id, user_id=user_id)
        except ImageAnalysis.DoesNotExist:
            raise NotFound("요청하신 데이터를 찾을 수 없거나 접근 권한이 없습니다.")

    @staticmethod
    def get_review(analysis_id: int, user_id: int) -> ImageAnalysis:
        return ReviewService._get_analysis_or_404(analysis_id, user_id)

    @staticmethod
    def patch_review(analysis_id: int, user_id: int, data: dict[str, Any]) -> ImageAnalysis:
        review_data = ReviewService._get_analysis_or_404(analysis_id, user_id)

        is_first_time = not review_data.review and review_data.rating is None

        if is_first_time:
            is_review_missing = not data.get("review")
            is_rating_missing = data.get("rating") is None

            if is_review_missing or is_rating_missing:
                raise ValidationError("첫 리뷰 작성은 별점/리뷰 둘 다 작성해야함")

        if "review" in data:
            review_data.review = data["review"]

        if "rating" in data:
            review_data.rating = data["rating"]

        review_data.save()

        return review_data

    @staticmethod
    def delete_review(analysis_id: int, user_id: int) -> None:
        review_data = ReviewService._get_analysis_or_404(analysis_id, user_id)

        review_data.review = None
        review_data.rating = None

        review_data.save()

    @staticmethod
    def get_my_reviews(user_id: int) -> QuerySet[ImageAnalysis]:
        reviews = ImageAnalysis.objects.filter(user_id=user_id).order_by("-created_at")

        return reviews
