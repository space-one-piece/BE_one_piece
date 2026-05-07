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
        model_map: dict[str, tuple[Any, str]] = {
            "image": (ImageAnalysis, "recommended_scent"),
            "chatbot": (ChatbotRecommendation, "scent"),
            "keyword": (QuestionsResults, "scent"),
            "survey": (QuestionsResults, "scent"),
        }

        model_info = model_map.get(analysis_type)
        if not model_info:
            raise ValidationError("유효하지 않은 타입입니다")

        model_class, relation_field = model_info

        try:
            instance = model_class.objects.select_related(relation_field).get(id=analysis_id)
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

        scent_obj = getattr(instance, "recommended_scent" if analysis_type == "image" else "scent", None)
        instance.eng_name = getattr(scent_obj, "eng_name", None)
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

        scent_obj = getattr(review_data, "recommended_scent" if analysis_type == "image" else "scent", None)
        review_data.eng_name = getattr(scent_obj, "eng_name", None)
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
            img_list = list(
                ImageAnalysis.objects.select_related("recommended_scent").filter(user_id=user_id, review__isnull=False)
            )
            for img in img_list:
                setattr(img, "type", "image")
                scent_obj = getattr(img, "recommended_scent", None)
                setattr(img, "eng_name", getattr(scent_obj, "eng_name", None))
            combined.extend(img_list)

        if analysis_type in [None, "chatbot"]:
            chat_list = list(
                ChatbotRecommendation.objects.select_related("scent").filter(user_id=user_id, review__isnull=False)
            )
            for chat in chat_list:
                setattr(chat, "type", "chatbot")
                scent_obj = getattr(chat, "scent", None)
                setattr(chat, "eng_name", getattr(scent_obj, "eng_name", None))
            combined.extend(chat_list)

        if analysis_type in [None, "keyword", "survey"]:
            q_qs = QuestionsResults.objects.select_related("scent").filter(user_id=user_id, review__isnull=False)

            if analysis_type == "keyword":
                q_qs = q_qs.filter(division="K")
            elif analysis_type == "survey":
                q_qs = q_qs.filter(division="S")

            q_list = list(q_qs)
            for q in q_list:
                db_division = getattr(q, "division", "K")
                setattr(q, "type", cls.div_to_type.get(db_division, "keyword"))
                scent_obj = getattr(q, "scent", None)
                setattr(q, "eng_name", getattr(scent_obj, "eng_name", None))

            combined.extend(q_list)

        combined.sort(key=lambda x: getattr(x, "created_at"), reverse=True)
        return combined

    @classmethod
    def get_recent_reviews(cls, limit: int = 10) -> list[Any]:
        combined: list[Any] = []

        img_qs = (
            ImageAnalysis.objects.select_related("recommended_scent")
            .filter(review__isnull=False)
            .order_by("-created_at")[:limit]
        )
        img_list = list(img_qs)
        for img in img_list:
            setattr(img, "type", "image")
            scent_obj = getattr(img, "recommended_scent", None)
            setattr(img, "eng_name", getattr(scent_obj, "eng_name", None))
        combined.extend(img_list)

        chat_qs = (
            ChatbotRecommendation.objects.select_related("scent")
            .filter(review__isnull=False)
            .order_by("-created_at")[:limit]
        )
        chat_list = list(chat_qs)
        for chat in chat_list:
            setattr(chat, "type", "chatbot")
            scent_obj = getattr(chat, "scent", None)
            setattr(chat, "eng_name", getattr(scent_obj, "eng_name", None))
        combined.extend(chat_list)

        q_qs = (
            QuestionsResults.objects.select_related("scent")
            .filter(review__isnull=False)
            .order_by("-created_at")[:limit]
        )
        q_list = list(q_qs)
        for q in q_list:
            db_division = getattr(q, "division", "K")
            setattr(q, "type", cls.div_to_type.get(db_division, "keyword"))
            scent_obj = getattr(q, "scent", None)
            setattr(q, "eng_name", getattr(scent_obj, "eng_name", None))

        combined.extend(q_list)

        combined.sort(key=lambda x: getattr(x, "created_at"), reverse=True)
        return combined[:limit]
