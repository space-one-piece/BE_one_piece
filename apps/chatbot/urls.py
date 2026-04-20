from django.urls import path

from .views.chat_views import ChatMessageView

# from .views.recommendation_views import ChatbotRecommendationRetryView
from .views.session_views import ChatSessionCreateView, ChatSessionEndView

urlpatterns = [
    path("sessions/", ChatSessionCreateView.as_view(), name="chat-session-create"),
    path("sessions/<int:session_id>/", ChatSessionEndView.as_view(), name="chat-session-end"),
    path("sessions/<int:session_id>/messages/", ChatMessageView.as_view(), name="chat-message"),
    # path("sessions/<int:session_id>/recommendations/retry/",ChatbotRecommendationRetryView.as_view(),name="chatbot-recommendation-retry",
    # ),
]
