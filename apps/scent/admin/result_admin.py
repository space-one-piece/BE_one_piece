from itertools import chain

from django.contrib import admin
from django.db.models import Q
from django.http import HttpRequest

from apps.analysis.models import ImageAnalysis
from apps.chatbot.models import ChatbotRecommendation
from apps.question.models import QuestionsResults
from apps.scent.models import CombinedSearchModel


@admin.register(CombinedSearchModel)
class ResultDataAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    search_fields = ["=id"]

    def get_queryset(self, request: HttpRequest):  # type: ignore
        return CombinedSearchModel.objects.none()

    def changelist_view(self, request: HttpRequest, extra_context=None):  # type: ignore
        search_query = request.GET.get("q", "").strip()

        image_qs = ImageAnalysis.objects.select_related("user", "recommended_scent").all()
        chatbot_qs = ChatbotRecommendation.objects.select_related("user", "scent").all()
        question_qs = QuestionsResults.objects.select_related("user", "scent").all()

        if search_query:
            q = search_query.lower()

            # ✅ 이름 + 향수명으로 필터, division 고정값("image") 검색 시 전체 반환
            if "image" in q:
                image_qs = ImageAnalysis.objects.select_related("user", "recommended_scent").all()
            else:
                image_qs = image_qs.filter(
                    Q(user__name__icontains=search_query) | Q(recommended_scent__name__icontains=search_query)
                )

            # ✅ 이름 + 향수명으로 필터, division 고정값("chatbot") 검색 시 전체 반환
            if "chatbot" in q:
                chatbot_qs = ChatbotRecommendation.objects.select_related("user", "scent").all()
            else:
                chatbot_qs = chatbot_qs.filter(
                    Q(user__name__icontains=search_query) | Q(scent__name__icontains=search_query)
                )

            # ✅ 이름 + 향수명 + division(keyword/survey) 필터
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
        extra_context["combined_results"] = combined_results
        extra_context["search_query"] = search_query
        extra_context["counts"] = {
            "image": len(results_image),
            "chatbot": len(results_chatbot),
            "question": len(results_question),
            "total": len(combined_results),
        }

        return super().changelist_view(request, extra_context=extra_context)
