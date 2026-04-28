from typing import Any

from rest_framework import serializers

from apps.analysis.models import Scent
from apps.analysis.serializers.analysis_serializers import ScentDetailSerializer


class ResultsSerializer(serializers.Serializer[dict[str, Any]]):
    web_share_url = serializers.CharField()


class ResultsIntSerializer(serializers.Serializer[dict[str, Any]]):
    review = serializers.CharField()
    rating = serializers.IntegerField(allow_null=True)


class ResultsOutSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    recommended_scent = ScentDetailSerializer()
    ai_comment = serializers.CharField()
    match_score = serializers.IntegerField()
    review = serializers.CharField()
    rating = serializers.IntegerField()


class UserInput(serializers.Serializer[Any]):
    title = serializers.CharField()
    answer = serializers.CharField()


class ResultWebShareSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    recommended_scent = ScentDetailSerializer()
    ai_comment = serializers.CharField()
    match_score = serializers.IntegerField()
    review = serializers.CharField()
    rating = serializers.IntegerField()
    user_input = UserInput(many=True)


class ResultRecommendedScentSerializer(serializers.ModelSerializer[Scent]):
    class Meta:
        model = Scent
        fields = ["id", "name", "description", "eng_name", "thumbnail_url"]


class ResultListSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    type = serializers.CharField()
    recommended_scent = ResultRecommendedScentSerializer(read_only=True)
    review = serializers.CharField()
    rating = serializers.IntegerField()
    created_at = serializers.DateTimeField()
