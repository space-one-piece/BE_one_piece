from typing import Any

from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

# 공통 휴대폰 번호 검증기 (재사용을 위해 분리)
phone_validator = RegexValidator(regex=r"010-?\d{4}-?\d{4}$", message="올바른 휴대폰 번호 형식이 아닙니다.")


class EmailSendSerializer(serializers.Serializer[Any]):
    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": "이메일은 필수 입력 항목입니다.",
            "invalid": "올바른 이메일 형식이 아닙니다.",
        },
    )

    def validate_email(self, value: str) -> str:
        return value.strip()


class EmailVerifySerializer(serializers.Serializer[Any]):
    email = serializers.EmailField()
    code = serializers.CharField(
        required=True, min_length=6, max_length=6, error_messages={"required": "6자리 인증번호를 입력해주세요."}
    )

    def validate_email(self, value: str) -> str:
        return value.strip()

    def validate_code(self, value: str) -> str:
        if not value.isalnum():
            raise ValidationError("인증번호는 영문과 숫자만 입력 가능합니다.")
        return value


class SmsSendSerializer(serializers.Serializer[Any]):
    phone_number = serializers.CharField(
        required=True,
        validators=[phone_validator],
    )

    def validate_phone_number(self, value: str) -> str:
        return value.replace("-", "").strip()


class SmsVerifySerializer(serializers.Serializer[Any]):
    phone_number = serializers.CharField(
        validators=[phone_validator], error_messages={"required": "휴대폰 번호를 입력해주세요."}
    )
    code = serializers.CharField(
        min_length=6,
        max_length=6,
        error_messages={"min_length": "인증번호는 6자리여야 합니다.", "max_length": "인증번호는 6자리여야 합니다."},
    )

    def validate_phone_number(self, value: str) -> str:
        return value.replace("-", "").strip()
