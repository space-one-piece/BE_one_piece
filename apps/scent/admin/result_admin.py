from itertools import chain
from typing import Any, Dict, Optional

from django.contrib import admin
from django.db.models import Q
from django.http import HttpRequest

from apps.analysis.models import ImageAnalysis
from apps.chatbot.models import ChatbotRecommendation
from apps.core.utils.cloud_front import image_url_cloud
from apps.question.models import QuestionsResults
from apps.scent.models import CombinedSearchModel


@admin.register(CombinedSearchModel)
class ResultDataAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    search_fields = ["=id"]

    def get_queryset(self, request: HttpRequest):  # type: ignore
        return CombinedSearchModel.objects.none()

    def changelist_view(self, request: HttpRequest, extra_context: Optional[Dict[str, Any]] = None) -> Any:
        search_query = request.GET.get("q", "").strip()

        image_qs = ImageAnalysis.objects.select_related("user", "recommended_scent").all()
        chatbot_qs = ChatbotRecommendation.objects.select_related("user", "scent").all()
        question_qs = QuestionsResults.objects.select_related("user", "scent").all()

        if search_query:
            q = search_query.lower()

            if "image" not in q:
                image_qs = image_qs.filter(
                    Q(user__name__icontains=search_query) | Q(recommended_scent__name__icontains=search_query)
                )

            if "chatbot" not in q:
                chatbot_qs = chatbot_qs.filter(
                    Q(user__name__icontains=search_query) | Q(scent__name__icontains=search_query)
                )

            question_qs = question_qs.filter(
                Q(user__name__icontains=search_query)
                | Q(scent__name__icontains=search_query)
                | Q(division__icontains=search_query)
            )

        results_image = [
            {
                "source_label": "이미지 분석",
                "is_first_of_group": False,
                "division": "image",
                "id": obj.id,
                "name": obj.user.name,
                "scent_name": obj.recommended_scent.name if obj.recommended_scent else "-",
                "thumbnail_url": image_url_cloud(obj.recommended_scent.thumbnail_url)
                if (obj.recommended_scent and obj.recommended_scent.thumbnail_url)
                else "-",
                "created_at": obj.created_at,
            }
            for obj in image_qs
        ]

        results_chatbot = [
            {
                "source_label": "챗봇 추천",
                "is_first_of_group": False,
                "division": "chatbot",
                "id": obj.id,
                "name": obj.user.name,
                "scent_name": obj.scent.name,
                "thumbnail_url": image_url_cloud(obj.scent.thumbnail_url) if obj.scent.thumbnail_url else "-",
                "created_at": obj.created_at,
            }
            for obj in chatbot_qs
        ]

        results_question = [
            {
                "source_label": "설문 결과",
                "is_first_of_group": False,
                "division": obj.get_division_display(),
                "id": obj.id,
                "name": obj.user.name,
                "scent_name": obj.scent.name,
                "thumbnail_url": image_url_cloud(obj.scent.thumbnail_url) if obj.scent.thumbnail_url else "-",
                "created_at": obj.created_at,
            }
            for obj in question_qs
        ]

        combined_results = list(chain(results_image, results_chatbot, results_question))

        previous_label = None
        for row in combined_results:
            row["is_first_of_group"] = row["source_label"] != previous_label
            previous_label = row["source_label"]

        extra_context = extra_context or {}
        extra_context.update(
            {
                "combined_results": combined_results,
                "search_query": search_query,
                "counts": {
                    "image": len(results_image),
                    "chatbot": len(results_chatbot),
                    "question": len(results_question),
                    "total": len(combined_results),
                },
            }
        )

        return super().changelist_view(request, extra_context=extra_context)
