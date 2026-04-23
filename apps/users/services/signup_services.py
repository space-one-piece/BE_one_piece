from typing import Any

from django.core.cache import cache
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.users.models.models import User


class DuplicateUserError(ValidationError):
    status_code = 409
    pass


class SignUpService:
    @transaction.atomic
    def create_user(self, validated_data: dict[str, Any]) -> User:
        input_email: str = str(validated_data.pop("email"))
        input_phone: str = str(validated_data.pop("phone_number")).replace("-", "")
        password: str = validated_data.pop("password")

        email_verified_key = f"verified_email_{input_email}"
        phone_verified_key = f"verified_phone_{input_phone}"

        if not cache.get(email_verified_key):
            raise ValidationError("이메일 인증이 완료되지 않았습니다.")

        if not cache.get(phone_verified_key):
            raise ValidationError("휴대폰 인증이 완료되지 않았습니다.")

        if User.objects.filter(email=input_email).exists():
            raise DuplicateUserError("이미 가입된 이메일입니다.")

        if User.objects.filter(phone_number=input_phone).exists():
            raise ValidationError("이미 등록된 휴대전화 번호입니다.")

        user = User.objects.create_user(
            email=input_email,
            password=password,
            phone_number=input_phone,
            social_type="GENERAL",
            is_active=True,
            **validated_data,
        )

        cache.delete(email_verified_key)
        cache.delete(phone_verified_key)
        return user
