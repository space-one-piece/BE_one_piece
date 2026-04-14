from typing import Any

from rest_framework import serializers


class AnalysisReviewSerializer(serializers.Serializer[Any]):
    review = serializers.CharField(max_length=500, required=True, help_text="유저가 남긴 리뷰 내용")
    rating = serializers.IntegerField(min_value=1, max_value=5, required=False, help_text="1~5 사이의 별점")
