from typing import Any

from rest_framework import serializers


class FindEmailSerializer(serializers.Serializer[Any]):
    name = serializers.CharField(max_length=30, help_text="사용자 이름")
    phone_number = serializers.CharField(min_length=11, max_length=11, help_text="하이픈 제외 휴대전화 11자리")
    sms_uuid_token = serializers.CharField(help_text="휴대폰 인증 완료 후 발급된 토큰")
