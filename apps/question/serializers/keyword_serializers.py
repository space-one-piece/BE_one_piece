from rest_framework import serializers

from apps.question.models import Keyword


class KeywordSerializer(serializers.ModelSerializer):
    keyword_id = serializers.IntegerField(source="id")
    keyword_division = serializers.CharField(source="division")
    keyword_name = serializers.CharField(source="name")

    class Meta:
        model = Keyword
        fields = ["keyword_id", "keyword_division", "keyword_name"]
