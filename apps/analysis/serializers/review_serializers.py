from typing import Any

from rest_framework import serializers


class AnalysisReviewSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField(read_only=True)
    type = serializers.CharField(read_only=True, help_text="분석 타입 (image, chatbot, keyword, survey)")
    review = serializers.CharField(max_length=500, required=True, help_text="유저가 남긴 리뷰 내용")
    rating = serializers.IntegerField(min_value=1, max_value=5, required=False, help_text="1~5 사이의 별점")
    created_at = serializers.DateTimeField(read_only=True)
