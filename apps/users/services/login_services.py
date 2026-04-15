from typing import Any

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import exceptions
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
