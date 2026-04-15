from django.urls import path
from rest_framework import routers

from apps.question.views.image_user import ImageUserAPIView
from apps.question.views.keyword_views import KeywordAPIView
from apps.question.views.quest_views import QuestAPIView
from apps.question.views.results_views import ResultsCreateUrlAPIView, ResultsViewAPIView

router = routers.DefaultRouter()

urlpatterns = [
    path("survey", QuestAPIView.as_view(), name="question"),
    path("web_share", ResultsCreateUrlAPIView.as_view(), name="web_share"),
    path("web_share/<int:results_id>", ResultsViewAPIView.as_view(), name="web_share_results"),
    path("keyword", KeywordAPIView.as_view(), name="keyword"),
    path("user-save", ImageUserAPIView.as_view(), name="user_save"),
]
