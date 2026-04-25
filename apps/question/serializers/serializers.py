from typing import Any

from rest_framework import serializers

from apps.analysis.models import Scent
from apps.analysis.serializers.analysis_serializers import ScentDetailSerializer


class QuestionScentDetailSerializer(serializers.ModelSerializer[Scent]):
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


class QuestionsInputSerializer(serializers.Serializer[dict[str, Any]]):
    """설문조사 데이터 입력"""

    questions_id = serializers.IntegerField()
    results = serializers.IntegerField()
    question_num = serializers.CharField()


class KeywordInputSerializer(serializers.Serializer[dict[str, Any]]):
    """키워드 데이터 입력"""

    keyword_id = serializers.IntegerField()
    keyword_name = serializers.CharField()


class KeywordOutSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    recommended_scent = ScentDetailSerializer(read_only=True)
    ai_comment = serializers.CharField()
    match_score = serializers.IntegerField()
