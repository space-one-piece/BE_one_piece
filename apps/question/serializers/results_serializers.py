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
    recommended_scent = ScentDetailSerializer(read_only=True)
    reason = serializers.CharField()
    review = serializers.CharField()
    rating = serializers.IntegerField()


class ResultWebShareSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    recommended_scent = ScentDetailSerializer(read_only=True)
    reason = serializers.CharField()
    review = serializers.CharField()
    rating = serializers.IntegerField()


class ResultRecommendedScentSerializer(serializers.ModelSerializer[Scent]):
    class Meta:
        model = Scent
        fields = ["id", "name", "eng_name", "thumbnail_url"]


class ResultListSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    recommended_scent = ResultRecommendedScentSerializer(read_only=True)
    type = serializers.CharField()
    created_at = serializers.DateTimeField()
