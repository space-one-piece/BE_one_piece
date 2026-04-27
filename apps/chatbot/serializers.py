from rest_framework import serializers

from apps.analysis.serializers.analysis_serializers import ScentDetailSerializer

from .models import ChatbotRecommendation, ChatSession


class ChatSessionSerializer(serializers.ModelSerializer[ChatSession]):
    class Meta:
        model = ChatSession
        fields = ["id", "status", "created_at"]


class ChatbotRecommendationSerializer(serializers.ModelSerializer[ChatbotRecommendation]):
    class Meta:
        model = ChatbotRecommendation
        fields = ["id", "scent_id", "retry_count", "is_saved", "saved_at", "created_at"]


class ChatbotRecommendationDetailSerializer(serializers.ModelSerializer[ChatbotRecommendation]):
    recommended_scent = ScentDetailSerializer(source="scent")
    ai_comment = serializers.CharField(source="reply")
    source_type = serializers.SerializerMethodField()
    match_score = serializers.IntegerField(default=80, read_only=True)
    ai_keywords = serializers.SerializerMethodField()
    user_message = serializers.JSONField()

    class Meta:
        model = ChatbotRecommendation
        fields = [
            "id",
            "recommended_scent",
            "ai_comment",
            "match_score",
            "source_type",
            "is_saved",
            "user_message",
            "ai_keywords",
            "created_at",
        ]

    def get_source_type(self, obj: object) -> str:
        return "chatbot"

    def get_ai_keywords(self, obj: ChatbotRecommendation) -> list[str]:
        if obj.scent:
            return obj.scent.tags or []
        return []
