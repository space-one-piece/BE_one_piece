from django.urls import path
from rest_framework import routers

from apps.question.views.image_user import ImageUserAPIView
from apps.question.views.keyword_views import KeywordAPIView
from apps.question.views.quest_views import QuestAPIView
from apps.question.views.results_views import ResultListAPIView, ResultsCreateUrlAPIView, ReviewViewAPIView

router = routers.DefaultRouter()

urlpatterns = [
    path("survey", QuestAPIView.as_view(), name="question"),
    path("web_share/<str:results_id>", ResultsCreateUrlAPIView.as_view(), name="web_share"),
    path("results/<int:results_id>/review", ReviewViewAPIView.as_view(), name="review_results"),
    path("keyword", KeywordAPIView.as_view(), name="keyword"),
    path("<int:requests_id>/user-save", ImageUserAPIView.as_view(), name="user_save"),
    path("<int:requests_id>/image", ImageUserAPIView.as_view(), name="image_user"),
    path("<str:division>/results", ResultListAPIView.as_view(), name="results"),
]
