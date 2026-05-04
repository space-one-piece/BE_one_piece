from typing import Any

from rest_framework import serializers


class ErrorResponseSerializer(serializers.Serializer[Any]):
    status = serializers.IntegerField(help_text="HTTP 상태코드")
    code = serializers.CharField(help_text="에러 식별 코드")
    message = serializers.CharField(help_text="에러 메시지")
    error_detail = serializers.CharField(help_text="상세 에러 내용")
