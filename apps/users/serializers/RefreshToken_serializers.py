from typing import Any

from rest_framework import serializers


class RefreshTokenSerializer(serializers.Serializer[Any]):
    refresh = serializers.CharField(read_only=True, help_text="새로 발급된 Refresh토큰입니다..")
