from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


class PasswordResetSerializer(serializers.Serializer[Any]):
    email = serializers.EmailField(help_text="인증을 완료한 유저의 이메일")
    token = serializers.CharField(help_text="이메일 인증 성공 시 발급된 UUID 토큰")
    new_password = serializers.CharField(write_only=True, help_text="새로 설정할 비밀번호")

    def validate_new_password(self, value: str) -> str:
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
