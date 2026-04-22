from django.urls import path

from ..views.analysis_views import (
    AnalysisDetailAPIView,
    AnalysisFeedbackAPIView,
    AnalysisListCreateAPIView,
    AnalysisStatsAPIView,
    IntegratedHistoryListAPIView,
    UploadURLAPIView,
)
from ..views.review_views import AnalysisReviewAPIView, MyReviewListAPIView

app_name = "analysis_user"

urlpatterns = [
    # 1. 분삭
    path("", AnalysisListCreateAPIView.as_view(), name="list-create"),  # get,post
    path("/stats", AnalysisStatsAPIView.as_view(), name="stats"),  # get
    path("/upload-url", UploadURLAPIView.as_view(), name="upload-url"),  # post
    # 2. 상세분석
    path("/<int:id>", AnalysisDetailAPIView.as_view(), name="detail"),  # get,delete
    path("/<int:id>/feedback", AnalysisFeedbackAPIView.as_view(), name="feedback"),  # patch
    # 3. 리뷰
    path("/<int:id>/review", AnalysisReviewAPIView.as_view(), name="review"),  # get,patch,delete
    path("/reviews/me", MyReviewListAPIView.as_view(), name="my-reviews"),
    # 4. 통합 분석 리스트
    path("/history", IntegratedHistoryListAPIView.as_view(), name="my-history"),  # get
]
