import re
from typing import Any

from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

# 공통 휴대폰 번호 검증기 (번호 11자리만 입력 형식)
phone_validator = RegexValidator(
    regex=r"^010-?\d{4}-?\d{4}$", message="휴대폰 번호는 숫자와 하이픈만 포함할 수 있으며, 010으로 시작해야 합니다."
)


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
        clean_value = re.sub(r"[^0-9]", "", value)

        if not clean_value.isdigit():
            raise ValidationError("휴대폰 번호에는 숫자만 입력 가능합니다.")
        return clean_value.strip()


class SmsVerifySerializer(serializers.Serializer[Any]):
    phone_number = serializers.CharField(
        validators=[phone_validator], error_messages={"required": "휴대폰 번호를 입력해주세요."}
    )
    code = serializers.CharField(
        min_length=6,
        max_length=6,
        error_messages={
            "required": "인증번호를 입력해주세요.",
            "min_length": "인증번호는 6자리여야 합니다.",
            "max_length": "인증번호는 6자리여야 합니다.",
        },
    )

    def validate_phone_number(self, value: str) -> str:
        return re.sub(r"[^0-9]", "", value)

    # 인증 코드 검증 (숫자만 있는지 확인)
    def validate_code(self, value: str) -> str:
        if not value.isdigit():
            raise ValidationError("인증번호는 숫자만 입력 가능합니다.")  # 코드를 위한 메시지!
        return value
