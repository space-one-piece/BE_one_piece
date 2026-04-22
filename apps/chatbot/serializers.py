from rest_framework import serializers

from apps.analysis.models import Scent

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


class ChatbotScentDetailSerializer(serializers.ModelSerializer[Scent]):
    class Meta:
        model = Scent
        fields = [
            "id",
            "name",
            "eng_name",
            "description",
            "categories",
            "tags",
            "keywords",
            "intensity",
            "is_bestseller",
            "scent_notes",
            "profile",
            "season",
            "recommended_places",
            "similar_scents",
            "thumbnail_url",
            "created_at",
        ]


class ChatbotRecommendationDetailSerializer(serializers.ModelSerializer[ChatbotRecommendation]):
    recommended_scent = ChatbotScentDetailSerializer(source="scent")
    ai_comment = serializers.CharField(source="reply")
    source_type = serializers.SerializerMethodField()

    class Meta:
        model = ChatbotRecommendation
        fields = [
            "id",
            "recommended_scent",
            "ai_comment",
            "source_type",
            "is_saved",
            "created_at",
        ]

    def get_source_type(self, obj: object) -> str:
        return "chatbot"
