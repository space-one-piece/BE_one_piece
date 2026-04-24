from datetime import timedelta
from typing import Any

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.choices import UserStatus
from apps.users.models.models import User, UserWithdrawal


# 로그인
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


# 로그아웃
class LogoutService:
    @staticmethod
    def logout(refresh_token_str: str) -> None:
        try:
            token = RefreshToken(refresh_token_str)  # type: ignore
            token.blacklist()
        except Exception:
            raise ValidationError({"code": "invalid_token", "message": "유효하지 않거나 이미 만료된 토큰입니다."})


# 계정 탈퇴
class WithdrawalService:
    @staticmethod
    @transaction.atomic
    def deactivate_user(user: User, password: str, reason: str, other_reason: str) -> User:
        if not user.check_password(password):
            raise ValidationError({"password": ["비밀번호가 일치하지 않습니다."]})

        if not user.is_active:
            raise ValidationError("이미 탈퇴 처리된 계정입니다.")

        user.is_active = False
        user.status = UserStatus.WITHDRAWN
        user.save()

        scheduled_date = timezone.now() + timedelta(days=14)

        UserWithdrawal.objects.create(
            user=user, reason=reason, other_reason=other_reason, scheduled_delete_at=scheduled_date
        )

        return user


# 계정 복구
class RecoveryService:
    @staticmethod
    @transaction.atomic
    def recover_user(email: str, password: str, code: str) -> User:
        verified_key = f"verified_email_{email.strip()}"
        is_verified = cache.get(verified_key)

        if not is_verified:
            raise ValidationError("이메일 인증이 완료되지 않았거나 인증 시간이 만료되었습니다.")

        user = User.objects.filter(email=email).first()
        if not user:
            raise ValidationError("가입되지 않은 이메일입니다.")

        if not user.check_password(password):
            raise ValidationError("비밀번호가 일치하지 않습니다.")

        if user.is_active:
            raise ValidationError("이미 활성화된 계정입니다.")

        withdrawal_info = getattr(user, "user_withdrawal", None)
        if not withdrawal_info or withdrawal_info.scheduled_delete_at < timezone.now():
            raise ValidationError("복구 가능 기간이 지났거나 탈퇴 정보가 없습니다.")

        user.is_active = True
        user.status = UserStatus.ACTIVE
        user.save()

        withdrawal_info.delete()

        return user
