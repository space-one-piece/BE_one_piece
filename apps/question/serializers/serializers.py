from typing import Any

from rest_framework import serializers


class questionsInputSerializer(serializers.Serializer[dict[str, Any]]):
    """설문조사 데이터 입력"""

    questions_id = serializers.IntegerField()
    results = serializers.IntegerField()
    question_num = serializers.CharField()


class KeywordInputSerializer(serializers.Serializer[dict[str, Any]]):
    """키워드 데이터 입력"""

    keyword_id = serializers.IntegerField()
    keyword_name = serializers.CharField()
