from typing import Any

from rest_framework import serializers


class ErrorResponseSerializer(serializers.Serializer[Any]):
    status = serializers.IntegerField(help_text="HTTP 상태코드")
    code = serializers.CharField(help_text="에러 식별 코드")
    message = serializers.CharField(help_text="에러 메시지")
    detail = serializers.JSONField(help_text="에러 상세 정보(단일 메시지 문자열 또는 필드별 에러 객체)")
