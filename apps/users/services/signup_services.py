from typing import Any

from django.core import cache
from rest_framework.exceptions import ValidationError

from apps.users.models.models import User


class DuplicateUserError(Exception):
    pass


class SignUpService:
    def create_user(self, validated_data: dict[str, Any]) -> User:
        email_token = validated_data.pop("email_token")

        email = cache.get(f"email_token:{email_token}")
        if not email:
            raise ValidationError("이메일 인증이 만료되었거나 유효하지 않습니다.")

        # 중복검사
        if User.objects.filter(email=email).exists():
            raise DuplicateUserError()

        password = validated_data.pop("password")

        user = User.objects.create_user(
            email=email,
            password=password,
            **validated_data
        )

        cache.delete(f"email_token:{email_token}")

        return user