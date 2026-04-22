from django.urls import path

from .views.chat_views import ChatMessageView
from .views.recommendation_views import (
    ChatbotRecommendationDetailView,
    ChatbotRecommendationRetryStatusView,
    ChatbotRecommendationRetryView,
    ChatbotRecommendationSaveView,
)
from .views.session_views import ChatSessionCreateView, ChatSessionEndView

urlpatterns = [
    path("sessions", ChatSessionCreateView.as_view(), name="chat-session-create"),
    path("sessions/<int:session_id>", ChatSessionEndView.as_view(), name="chat-session-end"),
    path("sessions/<int:session_id>/messages", ChatMessageView.as_view(), name="chat-message"),
    path(
        "sessions/<int:session_id>/recommendations/<int:recommendation_id>/save",
        ChatbotRecommendationSaveView.as_view(),
        name="chatbot-recommendation-save",
    ),
    path(
        "sessions/<int:session_id>/recommendations/retry/status",
        ChatbotRecommendationRetryStatusView.as_view(),
        name="chatbot-recommendation-retry-status",
    ),
    path(
        "sessions/<int:session_id>/recommendations/retry",
        ChatbotRecommendationRetryView.as_view(),
        name="chatbot-recommendation-retry",
    ),
    path(
        "sessions/<int:session_id>/recommendations/<int:recommendation_id>",
        ChatbotRecommendationDetailView.as_view(),
        name="chatbot-recommendation-detail",
    ),
]
