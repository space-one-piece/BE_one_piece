from typing import Any

from django.db import transaction
from django.core.cache import cache
from rest_framework.exceptions import ValidationError

from apps.users.models.models import User


class DuplicateUserError(ValidationError):
    pass


class SignUpService:
    @transaction.atomic
    def create_user(self, validated_data: dict[str, Any]) -> User:
        email_token: str = str(validated_data.pop("email_token"))

        email: str | None = cache.get(f"email_token:{email_token}")
        if not email:
            raise ValidationError("이메일 인증이 만료되었거나 유효하지 않습니다.")

        if User.objects.filter(email=email).exists():
            raise DuplicateUserError("이미 가입된 이메일입니다.")

        password = validated_data.pop("password")

        user = User.objects.create(
            email=email,
            password=password,
            social_type="GENERAL",
            **validated_data
        )

        cache.delete(f"email_token:{email_token}")
        return user