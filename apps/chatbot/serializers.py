from rest_framework import serializers

from .models import ChatbotRecommendation, ChatSession


class ChatSessionCreateSerializer(serializers.Serializer[None]):
    message = serializers.CharField()


class ChatSessionSerializer(serializers.ModelSerializer[ChatSession]):
    class Meta:
        model = ChatSession
        fields = ["id", "status", "created_at"]


class ChatbotRecommendationSerializer(serializers.ModelSerializer[ChatbotRecommendation]):
    class Meta:
        model = ChatbotRecommendation
        fields = ["id", "scent_id", "retry_count", "is_saved", "saved_at", "created_at"]
