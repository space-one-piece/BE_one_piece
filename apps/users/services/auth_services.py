from typing import Any

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import exceptions
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken


class LoginService:
    @staticmethod
    def login_user(email: str, password: str) -> dict[str, Any]:
        user = authenticate(email=email, password=password)

        if not user:
            raise exceptions.AuthenticationFailed()

        if not user.is_active:
            raise exceptions.PermissionDenied()

        update_last_login(None, user)  # type: ignore

        refresh = RefreshToken.for_user(user)

        return {"access": str(refresh.access_token), "refresh": str(refresh), "user": user}


class LogoutService:
    @staticmethod
    def logout(refresh_token_str: str) -> None:
        try:
            token = RefreshToken(refresh_token_str)  # type: ignore
            token.blacklist()
        except Exception:
            raise ValidationError({"code": "invalid_token", "message": "유효하지 않거나 이미 만료된 토큰입니다."})
