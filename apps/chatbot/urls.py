from django.urls import path

from .views.session_views import ChatSessionCreateView

urlpatterns = [
    # 세션 생성
    path("sessions/", ChatSessionCreateView.as_view(), name="chat-session-create"),
]
