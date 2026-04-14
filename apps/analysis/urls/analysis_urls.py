from django.urls import path

from ..views.analysis_views import (
    AnalysisDetailAPIView,
    AnalysisFeedbackAPIView,
    AnalysisListCreateAPIView,
    AnalysisStatsAPIView,
    UploadURLAPIView,
)
from ..views.review_views import AnalysisReviewAPIView

app_name = "analysis_user"

urlpatterns = [
    # 1. 분삭
    path("", AnalysisListCreateAPIView.as_view(), name="list-create"),  # get,post
    path("stats", AnalysisStatsAPIView.as_view(), name="stats"),  # get
    path("upload-url", UploadURLAPIView.as_view(), name="upload-url"),  # post
    # 2. 상세분석
    path("<int:id>", AnalysisDetailAPIView.as_view(), name="detail"),  # get,delete
    path("<int:id>/feedback", AnalysisFeedbackAPIView.as_view(), name="feedback"),  # patch
    # 3. 리뷰
    path("<int:id>/review", AnalysisReviewAPIView.as_view(), name="review"),  # get,post,patch,delete
]
