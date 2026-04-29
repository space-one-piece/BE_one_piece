from typing import Any

from django.contrib import admin
from django.db.models import Q
from django.http import HttpRequest, HttpResponse

from apps.analysis.models import ImageAnalysis
from apps.chatbot.models import ChatbotRecommendation
from apps.question.models import QuestionsResults
from apps.scent.models import CombinedSearchModel


@admin.register(CombinedSearchModel)
class ResultDataAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    def get_queryset(self, request: HttpRequest):  # type: ignore
        return CombinedSearchModel.objects.none()

    def changelist_view(self, request: HttpRequest, extra_context=None):  # type: ignore
        search_query = request.GET.get("q", "").strip()

        results_a = self._search_model_a(search_query)
        results_b = self._search_model_b(search_query)
        results_c = self._search_model_c(search_query)

        combined_results = list(results_a) + list(results_b) + list(results_c)

        previous_source = None
        for row in combined_results:
            row["is_first_of_group"] = row["source"] != previous_source
            previous_source = row["source"]

        rows_html = ""

        for row in combined_results:
            if row["is_first_of_group"]:
                rows_html += f"""
                    <tr>
                        <td colspan="5" style="background:#417690; color:white; font-weight:bold; padding:6px 12px;">
                            📂 {row["source_label"]}
                        </td>
                    </tr>
                """
            rows_html += f"""
                <tr>
                    <td style="padding:8px; border:1px solid #ddd;">{row["division"]}</td>
                    <td style="padding:8px; border:1px solid #ddd;">{row["id"]}</td>
                    <td style="padding:8px; border:1px solid #ddd;">{row["name"]}</td>
                    <td style="padding:8px; border:1px solid #ddd;">{row["scent_name"]}</td>
                    <td style="padding:8px; border:1px solid #ddd;">{row["created_at"].strftime("%Y-%m-%d %H:%M")}</td>
                </tr>
            """

        if not combined_results:
            rows_html = f"""
                <tr>
                    <td colspan="5" style="text-align:center; padding:20px; color:#999;">
                        {"검색 결과가 없습니다." if search_query else "검색어를 입력하세요."}
                    </td>
                </tr>
            """

        html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>통합 검색</title>
                <link rel="stylesheet" href="/static/admin/css/base.css">
                <link rel="stylesheet" href="/static/admin/css/changelists.css">
            </head>
            <body class="change-list">
            <div id="container">
                <div id="content" class="colM">
                    <h1>통합 검색</h1>

                    <!-- 검색창 -->
                    <div id="toolbar">
                        <form method="get">
                            <input type="text" name="q" value="{search_query}"
                                placeholder="이름 또는 향수명 검색..."
                                style="padding:6px 10px; width:300px;" />
                            <input type="submit" value="검색" style="padding:6px 12px;" />
                        </form>
                    </div>

                    <!-- 카운트 -->
                    {'<p style="margin:10px 0; color:#666;">총 ' + str(len(combined_results)) + "건 (챗봇: " + str(len(results_a)) + "건 / 이미지: " + str(len(results_b)) + "건 / 설문: " + str(len(results_c)) + "건)</p>" if search_query else ""}

                    <!-- 테이블 -->
                    <table style="width:100%; border-collapse:collapse;">
                        <thead>
                            <tr style="background:#f8f8f8;">
                                <th style="padding:8px; border:1px solid #ddd;">구분</th>
                                <th style="padding:8px; border:1px solid #ddd;">ID</th>
                                <th style="padding:8px; border:1px solid #ddd;">이름</th>
                                <th style="padding:8px; border:1px solid #ddd;">향수명</th>
                                <th style="padding:8px; border:1px solid #ddd;">생성일</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows_html}
                        </tbody>
                    </table>
                </div>
            </div>
            </body>
            </html>
        """

        return HttpResponse(html)

    def _search_model_a(self, query: str) -> list[dict[str, Any]]:
        qs = ChatbotRecommendation.objects.select_related("user", "scent").all()
        if query:
            qs = qs.filter(Q(user__username__icontains=query) | Q(scent__name__icontains=query))
        return [
            {
                "source": "ChatbotRecommendation",
                "source_label": "챗봇 추천",
                "is_first_of_group": False,
                "division": "chatbot",
                "id": obj.id,
                "name": obj.user.username,
                "scent_name": obj.scent.name,
                "created_at": obj.created_at,
            }
            for obj in qs
        ]

    def _search_model_b(self, query: str) -> list[dict[str, Any]]:
        qs = ImageAnalysis.objects.select_related("user", "recommended_scent").all()
        if query:
            qs = qs.filter(Q(user__username__icontains=query) | Q(recommended_scent__name__icontains=query))
        return [
            {
                "source": "ImageAnalysis",
                "source_label": "이미지 분석",
                "is_first_of_group": False,
                "division": "image",
                "id": obj.id,
                "name": obj.user.username,
                "scent_name": obj.recommended_scent.name if obj.recommended_scent else "",
                "created_at": obj.created_at,
            }
            for obj in qs
        ]

    def _search_model_c(self, query: str) -> list[dict[str, Any]]:
        qs = QuestionsResults.objects.select_related("user", "scent").all()
        if query:
            qs = qs.filter(Q(user__username__icontains=query) | Q(scent__name__icontains=query))
        return [
            {
                "source": "QuestionsResults",
                "source_label": "설문 결과",
                "is_first_of_group": False,
                "division": "question",
                "id": obj.id,
                "name": obj.user.username,
                "scent_name": obj.scent.name,
                "created_at": obj.created_at,
            }
            for obj in qs
        ]
