from django.urls import path
from rest_framework import routers

from apps.question.views.image_user import ImageUserAPIView, UserImageAPIView
from apps.question.views.keyword_views import KeywordAPIView
from apps.question.views.quest_views import QuestAPIView

router = routers.DefaultRouter()

urlpatterns = [
    path("survey", QuestAPIView.as_view(), name="question"),
    # path("results/<int:results_id>/review", ReviewViewAPIView.as_view(), name="review_results"),
    path("keyword", KeywordAPIView.as_view(), name="keyword"),
    path("image", ImageUserAPIView.as_view(), name="user_image"),
    path("user-image", UserImageAPIView.as_view(), name="image_user"),
    # path("<str:division>/results", ResultListAPIView.as_view(), name="results"),
    # path("<str:division>/detail/<int:requests_id>", ResultDetailAPIView.as_view(), name="detail"),
]
