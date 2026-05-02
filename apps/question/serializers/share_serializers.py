from typing import Any, Dict

from rest_framework import serializers


class ShareRequestSerializer(serializers.Serializer[Any]):
    CHANNEL_CHOICES = [("kakao", "카카오톡"), ("discord", "디스코드")]

    channels = serializers.ListField(
        child=serializers.ChoiceField(choices=CHANNEL_CHOICES),
        min_length=1,
    )
    text = serializers.CharField(required=False, allow_blank=True)
    url = serializers.URLField(required=False, allow_blank=True)
    image_url = serializers.URLField(required=False, allow_blank=True)

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:  # 타입 힌트 추가
        if not data.get("text") and not data.get("url") and not data.get("image_url"):
            raise serializers.ValidationError("text, url, image_url 중 하나는 필수입니다.")
        return data


class ChannelResultSerializer(serializers.Serializer[Any]):
    channel = serializers.CharField()
    success = serializers.BooleanField()
    message = serializers.CharField()


class ShareResponseSerializer(serializers.Serializer[Any]):
    results = ChannelResultSerializer(many=True)


class ShareOgSerializer(serializers.Serializer[Any]):
    result_id = serializers.IntegerField()
    type = serializers.CharField()
