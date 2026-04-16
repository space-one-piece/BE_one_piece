from typing import Any

from rest_framework import serializers


class RefreshTokenSerializer(serializers.Serializer[Any]):
    refresh = serializers.CharField(required=True, help_text="발급받았던 Refresh토큰을 입력하세요.")
