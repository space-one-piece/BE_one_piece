from typing import Any

from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.analysis.models import ImageAnalysis
from apps.chatbot.models import ChatbotRecommendation
from apps.question.models import QuestionsResults
from apps.users.models.models import User


class ReviewService:
    div_to_type = {"K": "keyword", "S": "survey"}

    @staticmethod
    def _get_instance_or_404(analysis_id: int, user: User, analysis_type: str) -> Any:
        model_map = {
            "image": ImageAnalysis,
            "chatbot": ChatbotRecommendation,
            "keyword": QuestionsResults,
            "survey": QuestionsResults,
        }

        model_class: Any = model_map.get(analysis_type)
        if model_class is None:
            raise ValidationError("유효하지 않은 타입입니다")

        try:
            instance = model_class.objects.get(id=analysis_id)
        except model_class.DoesNotExist:
            raise NotFound(f"요청하신 {analysis_type} 데이터를 찾을 수 없거나 접근 권한이 없습니다.")

        user_id = getattr(instance, "user_id", None)

        if user_id != user.id and not user.is_staff:
            raise PermissionDenied("이 리뷰를 수정/삭제할 권한이 없습니다")

        return instance

    @staticmethod
    def get_review(analysis_id: int, user: User, analysis_type: str) -> Any:
        instance = ReviewService._get_instance_or_404(analysis_id, user, analysis_type)
        instance.type = analysis_type
        return instance

    @staticmethod
    def patch_review(analysis_id: int, user: User, analysis_type: str, data: dict[str, Any]) -> Any:
        review_data = ReviewService._get_instance_or_404(analysis_id, user, analysis_type)

        is_first = not review_data.review and not review_data.rating

        if is_first and (not data.get("review") or not data.get("rating")):
            raise ValidationError("첫 리뷰 작성은 별점/리뷰 둘 다 작성해야 합니다")

        for field in ["review", "rating"]:
            if field in data:
                setattr(review_data, field, data[field])

        review_data.save(update_fields=["review", "rating", "updated_at"])
        review_data.type = analysis_type
        return review_data

    @staticmethod
    def delete_review(analysis_id: int, user: User, analysis_type: str) -> None:
        review_data = ReviewService._get_instance_or_404(analysis_id, user, analysis_type)
        review_data.review = None
        review_data.rating = None
        review_data.save(update_fields=["review", "rating", "updated_at"])

    @classmethod
    def get_my_reviews(cls, user_id: int, analysis_type: str | None = None) -> list[Any]:
        """
        type이 없으면 전체 테이블 리뷰 반환,
        type이 있으면 해당 테이블 리뷰만 반환
        """
        combined: list[Any] = []

        if analysis_type in [None, "image"]:
            img_list = list(ImageAnalysis.objects.filter(user_id=user_id, review__isnull=False))
            for img in img_list:
                setattr(img, "type", "image")
            combined.extend(img_list)

        if analysis_type in [None, "chatbot"]:
            chat_list = list(ChatbotRecommendation.objects.filter(user_id=user_id, review__isnull=False))
            for chat in chat_list:
                setattr(chat, "type", "chatbot")
            combined.extend(chat_list)

        if analysis_type in [None, "keyword", "survey"]:
            q_qs = QuestionsResults.objects.filter(user_id=user_id, review__isnull=False)

            if analysis_type == "keyword":
                q_qs = q_qs.filter(division="K")
            elif analysis_type == "survey":
                q_qs = q_qs.filter(division="S")

            q_list = list(q_qs)
            for q in q_list:
                db_division = getattr(q, "division", "K")
                setattr(q, "type", cls.div_to_type.get(db_division, "keyword"))

            combined.extend(q_list)

        combined.sort(key=lambda x: x.created_at, reverse=True)
        return combined

    @classmethod
    def get_recent_reviews(cls, limit: int = 5) -> list[Any]:
        combined: list[Any] = []

        img_qs = ImageAnalysis.objects.filter(review__isnull=False).order_by("-created_at")[:limit]
        img_list = list(img_qs)
        for img in img_list:
            setattr(img, "type", "image")
        combined.extend(img_list)

        chat_qs = ChatbotRecommendation.objects.filter(review__isnull=False).order_by("-created_at")[:limit]
        chat_list = list(chat_qs)
        for chat in chat_list:
            setattr(chat, "type", "chatbot")
        combined.extend(chat_list)

        q_qs = QuestionsResults.objects.filter(review__isnull=False).order_by("-created_at")[:limit]
        q_list = list(q_qs)
        for q in q_list:
            db_division = getattr(q, "division", "K")
            setattr(q, "type", cls.div_to_type.get(db_division, "keyword"))

        combined.extend(q_list)

        combined.sort(key=lambda x: x.created_at, reverse=True)
        return combined[:limit]
