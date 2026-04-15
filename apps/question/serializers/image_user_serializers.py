from typing import Any

from rest_framework import serializers


class ImageSerializer(serializers.Serializer[dict[str, Any]]):
    temp = serializers.CharField()
