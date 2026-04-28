from django.contrib import admin
from django.db.models import Q

from apps.analysis.models import ImageAnalysis
from apps.chatbot.models import ChatbotRecommendation
from apps.question.models import QuestionsResults
from apps.scent.models import CombinedSearchModel


@admin.register(CombinedSearchModel)
class ResultDataAdmin(admin.ModelAdmin):
    search_fields = ["division", "scent_name"]

    def get_queryset(self, request):
        # 가상 모델이라 기본 queryset 불필요 (빈 queryset 반환)
        return CombinedSearchModel.objects.none()

    def changelist_view(self, request, extra_context=None):
        search_query = request.GET.get("q", "").strip()

        # ✅ 각 모델 개별 검색
        results_a = self._search_model_a(search_query)
        results_b = self._search_model_b(search_query)
        results_c = self._search_model_c(search_query)

        # ✅ 수직으로 합치기 (JOIN 아님)
        combined_results = list(results_a) + list(results_b) + list(results_c)

        extra_context = extra_context or {}
        extra_context["combined_results"] = combined_results
        extra_context["search_query"] = search_query
        extra_context["counts"] = {
            "a": len(results_a),
            "b": len(results_b),
            "c": len(results_c),
            "total": len(combined_results),
        }

        return super().changelist_view(request, extra_context=extra_context)

    def _search_model_a(self, query):
        qs = ChatbotRecommendation.objects.all()
        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(division__icontains=query) | Q(scent_name__icontains=query))
        return [
            {
                "division": "chatbot",
                "id": obj.id,
                "name": obj.user.username,
                "scent_name": obj.scent.name,
                "created_at": obj.created_at,
            }
            for obj in qs
        ]

    def _search_model_b(self, query):
        qs = ImageAnalysis.objects.all()
        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(division__icontains=query) | Q(scent_name__icontains=query))
        return [
            {
                "division": "image",
                "id": obj.id,
                "name": obj.user.username,
                "scent_name": obj.recommended_scent.name,
                "created_at": obj.created_at,
            }
            for obj in qs
        ]

    def _search_model_c(self, query):
        qs = QuestionsResults.objects.all()
        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(division__icontains=query) | Q(scent_name__icontains=query))
        return [
            {
                "division": obj.division,
                "id": obj.id,
                "name": obj.user.username,
                "scent_name": obj.scent.name,
                "created_at": obj.created_at,
            }
            for obj in qs
        ]
