from rest_framework import serializers

from apps.analysis.serializers.analysis_serializers import ScentDetailSerializer
from apps.question.models import Keyword


class KeywordSerializer(serializers.ModelSerializer[Keyword]):
    keyword_id = serializers.IntegerField(source="id")
    keyword_division = serializers.CharField(source="get_division_display")
    keyword_name = serializers.CharField(source="name")

    class Meta:
        model = Keyword
        fields = ["keyword_id", "keyword_division", "keyword_name"]


class KeywordPostSerializer(serializers.ModelSerializer[Keyword]):
    keyword_id = serializers.IntegerField(source="id")
    keyword_division = serializers.CharField(source="division")
    keyword_name = serializers.CharField(source="name")

    class Meta:
        model = Keyword
        fields = ["keyword_id", "keyword_division", "keyword_name"]


class KeywordOutSerializer(serializers.ModelSerializer[Keyword]):
    id = serializers.IntegerField()
    recommended_scent = ScentDetailSerializer(read_only=True)
    reason = serializers.CharField()
