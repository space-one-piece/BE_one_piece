from django.urls import path
from rest_framework import routers

from apps.question.views import QuestAPIView

router = routers.DefaultRouter()

urlpatterns = [
    path("", QuestAPIView.as_view(), name="question"),
]
