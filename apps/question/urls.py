from django.urls import path
from rest_framework import routers

from apps.question.views.image_user import ImageUserAPIView, UserImageAPIView
from apps.question.views.keyword_views import KeywordAPIView
from apps.question.views.quest_views import QuestAPIView
from apps.question.views.results_views import (
    ResultsCreateUrlAPIView,
)

router = routers.DefaultRouter()

urlpatterns = [
    path("survey", QuestAPIView.as_view(), name="question"),
    path("web_share/<str:results_id>", ResultsCreateUrlAPIView.as_view(), name="web_share"),
    path("keyword", KeywordAPIView.as_view(), name="keyword"),
    path("image", ImageUserAPIView.as_view(), name="user_image"),
    path("user-image", UserImageAPIView.as_view(), name="image_user"),
]
