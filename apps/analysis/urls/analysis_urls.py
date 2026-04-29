from django.urls import path

from ..views.analysis_views import (
    # AnalysisDetailAPIView,
    AnalysisFeedbackAPIView,
    AnalysisFeedbackListAPIView,
    AnalysisListCreateAPIView,
    AnalysisStatsAPIView,
    AnalysisTotalDetailAPIView,
    IntegratedHistoryListAPIView,
    UploadURLAPIView,
)
from ..views.review_views import MyReviewDetailAPIView, MyReviewListAPIView, RecentReviewListAPIView

app_name = "analysis_user"

urlpatterns = [
    # 1. 분삭
    path("", AnalysisListCreateAPIView.as_view(), name="list-create"),  # get,post
    path("/stats", AnalysisStatsAPIView.as_view(), name="stats"),  # get
    path("/upload-url", UploadURLAPIView.as_view(), name="upload-url"),  # post
    # 2. 상세분석
    # path("/<int:id>", AnalysisDetailAPIView.as_view(), name="detail"),  # get,delete
    # 3. 리뷰
    path("/reviews", MyReviewListAPIView.as_view(), name="my-reviews"),  # get
    path("/reviews/recent", RecentReviewListAPIView.as_view(), name="recent-reviews"),  # get
    path("/reviews/<int:id>", MyReviewDetailAPIView.as_view(), name="my-review-detail"),  # get, patch, delete
    # 4. 통합 분석 리스트
    path("/history", IntegratedHistoryListAPIView.as_view(), name="my-history"),  # get
    # 5. 통합 상세 분석/추천
    path("/history/<int:id>", AnalysisTotalDetailAPIView.as_view(), name="my-detail"),  # get
    # 6. 통합 분석결과 저장
    path("/feedback", AnalysisFeedbackListAPIView.as_view(), name="feedback"),  # get
    path("/feedback/<int:id>", AnalysisFeedbackAPIView.as_view(), name="feedback-detail"),  # patch
]
