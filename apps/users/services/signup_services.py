from typing import Any

from django.core.cache import cache
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.users.models.models import User


class DuplicateUserError(ValidationError):
    pass


class SignUpService:
    @transaction.atomic
    def create_user(self, validated_data: dict[str, Any]) -> User:
        email_token: str = str(validated_data.pop("email_token"))
        input_email: str = validated_data.pop("email")

        verified_email: str | None = cache.get(f"signup_token_{email_token}")

        if not verified_email:
            raise ValidationError("이메일 인증이 만료되었거나 유효하지 않습니다.")

        if verified_email != input_email:
            raise ValidationError("인증받은 이메일 정보와 일치하지 않습니다.")

        if User.objects.filter(email=input_email).exists():
            raise DuplicateUserError("이미 가입된 이메일입니다.")

        password = validated_data.pop("password")

        user = User.objects.create(email=input_email, password=password, social_type="GENERAL", **validated_data)

        cache.delete(f"email_token:{email_token}")
        return user
