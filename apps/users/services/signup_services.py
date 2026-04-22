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
        email_token: str = str(validated_data.pop("email_token"))
        phone_token: str = str(validated_data.pop("phone_token"))
        input_email: str = str(validated_data.pop("email"))
        input_phone: str = str(validated_data.pop("phone_number")).replace("-", "")
        password: str = validated_data.pop("password")

        email_cache_key: str = f"signup_token_{email_token}"
        verified_email: str | None = cache.get(email_cache_key)

        if not verified_email:
            raise ValidationError("이메일 인증이 만료되었거나 유효하지 않습니다.")

        phone_cache_key = f"signup_token_{phone_token}"
        verified_phone = cache.get(phone_cache_key)

        if not verified_phone or verified_phone != input_phone:
            raise ValidationError("휴대폰 인증 정보가 만료되었거나 일치하지 않습니다.")

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

        cache.delete(email_cache_key)
        cache.delete(phone_cache_key)
        return user
