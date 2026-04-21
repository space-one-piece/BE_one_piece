from typing import Any

from ..models import ChatbotRecommendation


def get_chatbot_recommendation_history(user_id: int) -> list[dict[str, Any]]:
    recommendations = (
        ChatbotRecommendation.objects.filter(
            user_id=user_id,
            is_saved=True,
        )
        .select_related("scent")
        .order_by("-created_at")
    )

    data = [
        {
            "id": r.id,
            "type": "chatbot",
            "recommended_scent": {
                "id": r.scent.id,
                "name": r.scent.name,
                "description": r.scent.description,
                "eng_name": r.scent.eng_name,
                "thumbnail_url": r.scent.thumbnail_url,
            },
            "review": r.review,
            "rating": r.rating,
            "created_at": r.created_at,
        }
        for r in recommendations
    ]

    return data
