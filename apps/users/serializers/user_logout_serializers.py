from typing import Any

from rest_framework import serializers


class LogoutSerializer(serializers.Serializer[Any]):
    refresh = serializers.CharField(help_text="로그아웃할 사용자의 Refresh token")