from typing import Any

from django.db.models import QuerySet
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.analysis.models import ImageAnalysis
from apps.users.models.models import User


class ReviewService:
    @staticmethod
    def _get_analysis_or_404(analysis_id: int, user: User) -> ImageAnalysis:
        try:
            analysis = ImageAnalysis.objects.get(id=analysis_id)

            if analysis.user_id != user.id and not user.is_staff:
                raise PermissionDenied("이 리뷰를 수정/삭제할 권한이 없습니다.")

            return analysis
        except ImageAnalysis.DoesNotExist:
            raise NotFound("요청하신 데이터를 찾을 수 없거나 접근 권한이 없습니다.")

    @staticmethod
    def get_review(analysis_id: int, user: User) -> ImageAnalysis:
        return ReviewService._get_analysis_or_404(analysis_id, user)

    @staticmethod
    def patch_review(analysis_id: int, user: User, data: dict[str, Any]) -> ImageAnalysis:
        review_data = ReviewService._get_analysis_or_404(analysis_id, user)

        is_first = not review_data.review and not review_data.rating

        if is_first and (not data.get("review") or not data.get("rating")):
            raise ValidationError("첫 리뷰 작성은 별점/리뷰 둘 다 작성해야 합니다.")

        for field in ["review", "rating"]:
            if field in data:
                setattr(review_data, field, data[field])

        review_data.save()

        return review_data

    @staticmethod
    def delete_review(analysis_id: int, user: User) -> None:
        review_data = ReviewService._get_analysis_or_404(analysis_id, user)

        review_data.review = None
        review_data.rating = None

        review_data.save()

    @staticmethod
    def get_my_reviews(user_id: int) -> QuerySet[ImageAnalysis]:
        reviews = ImageAnalysis.objects.filter(user_id=user_id).order_by("-created_at")

        return reviews
