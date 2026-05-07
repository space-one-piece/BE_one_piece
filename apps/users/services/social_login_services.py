import logging
import urllib.parse
import uuid
from datetime import date
from typing import Any, cast

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.users.choices import SocialTypeChoice
from apps.users.models.models import SocialUser, UserWithdrawal

User = get_user_model()
logger = logging.getLogger(__name__)


class NaverOAuthService:
    AUTH_URL = "https://nid.naver.com/oauth2.0/authorize"
    TOKEN_URL = "https://nid.naver.com/oauth2.0/token"
    USER_INFO_URL = "https://openapi.naver.com/v1/nid/me"

    def get_auth_url(self) -> tuple[str, str]:
        state = uuid.uuid4().hex
        params = {
            "client_id": settings.NAVER_CLIENT_ID,
            "redirect_uri": settings.NAVER_REDIRECT_URI,
            "response_type": "code",
            "state": state,
        }
        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}", state

    def get_access_token(self, code: str, state: str) -> str:
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.NAVER_CLIENT_ID,
            "client_secret": settings.NAVER_CLIENT_SECRET,
            "code": code,
            "state": state,
        }
        response = requests.post(self.TOKEN_URL, data=data, timeout=10)
        response.raise_for_status()
        return cast(str, response.json().get("access_token"))

    def get_token_info(self, access_token: str) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(self.USER_INFO_URL, headers=headers, timeout=10)
        response.raise_for_status()
        profile = response.json().get("response")
        if not profile:
            raise ValidationError({"code": "naver_api_error", "message": "네이버 프로필 응답이 비어있습니다."})
        return cast(dict[str, Any], profile)

    def parse_naver_birthday(self, profile: dict[str, Any]) -> date | None:
        birthday = profile.get("birthday")
        birthyear = profile.get("birthyear")
        if birthday and birthyear:
            try:
                return date(int(birthyear), int(birthday[:2]), int(birthday[3:]))
            except (ValueError, TypeError):
                pass
        return None

    def get_or_create_user(self, user_info: dict[str, Any]) -> Any:
        naver_id = str(user_info.get("id"))
        email = user_info.get("email")

        if not email:
            raise ValidationError({"code": "email_required", "message": "네이버 계정에 이메일이 없습니다."})

        social_user = (
            SocialUser.objects.filter(provider=SocialTypeChoice.NAVER, social_id=naver_id)
            .select_related("user")
            .first()
        )

        if social_user:
            user = social_user.user
            self._validate_user_status(user)
            user.name = user_info.get("name", user.name) or user.name
            user.profile_image_url = user_info.get("profile_image", user.profile_image_url)
            mobile = user_info.get("mobile", "").replace("-", "")
            if mobile:
                user.phone_number = mobile
            birthday_date = self.parse_naver_birthday(user_info)
            if birthday_date:
                user.birthday = birthday_date
            user.save(update_fields=["name", "profile_image_url", "phone_number", "birthday"])
            return user

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            self._validate_user_status(existing_user)
            SocialUser.objects.get_or_create(user=existing_user, provider=SocialTypeChoice.NAVER, social_id=naver_id)
            return existing_user

        name = user_info.get("name")
        birthday_date = self.parse_naver_birthday(user_info)
        profile_image_url = user_info.get("profile_image", "")
        mobile = user_info.get("mobile", "").replace("-", "")

        with transaction.atomic():
            user = User.objects.create(
                email=email,
                name=name[:30] if name else "네이버유저",
                phone_number=mobile if mobile else None,
                birthday=birthday_date or None,
                profile_image_url=profile_image_url or "",
                social_type=SocialTypeChoice.NAVER,
                is_active=True,
            )
            SocialUser.objects.get_or_create(user=user, provider=SocialTypeChoice.NAVER, social_id=naver_id)
        return user

    @staticmethod
    def _validate_user_status(user: Any) -> None:
        if not user.is_active:
            raise ValidationError({"code": "inactive_user", "message": "비활성화된 계정입니다."})
        if UserWithdrawal.objects.filter(user=user).exists():
            raise ValidationError({"code": "withdrawn_user", "message": "탈퇴 신청한 계정입니다."})


class KaKaoOAuthService:
    AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
    TOKEN_URL = "https://kauth.kakao.com/oauth/token"
    USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"

    def get_auth_url(self) -> tuple[str, str]:
        state = uuid.uuid4().hex
        params = {
            "client_id": settings.KAKAO_CLIENT_ID,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "response_type": "code",
            "state": state,
        }
        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}", state

    def get_access_token(self, code: str, state: str) -> str:
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_CLIENT_ID,
            "client_secret": settings.KAKAO_CLIENT_SECRET,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code": code,
        }
        response = requests.post(self.TOKEN_URL, data=data, timeout=10)
        response.raise_for_status()
        return cast(str, response.json().get("access_token"))

    def get_token_info(self, access_token: str) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(self.USER_INFO_URL, headers=headers, timeout=10)
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    def parse_kakao_birthday(self, kakao_account: dict[str, Any]) -> date | None:
        birthday = kakao_account.get("birthday")  # MMDD 형식
        birthyear = kakao_account.get("birthyear")
        if birthday and birthyear:
            try:
                return date(int(birthyear), int(birthday[:2]), int(birthday[2:]))
            except (ValueError, TypeError):
                pass
        return None

    def get_or_create_user(self, user_info: dict[str, Any]) -> Any:
        kakao_id = str(user_info.get("id"))
        kakao_account = user_info.get("kakao_account", {})
        profile = kakao_account.get("profile", {})

        email = kakao_account.get("email")
        if not email:
            email = f"kakao_{kakao_id}@kakao.local"

        name = kakao_account.get("name") or profile.get("nickname")
        profile_image_url = profile.get("profile_image_url", "")
        phone_number = kakao_account.get("phone_number", "").replace("+82 ", "0").replace("-", "")
        birthday_date = self.parse_kakao_birthday(kakao_account)

        social_user = SocialUser.objects.filter(provider=SocialTypeChoice.KAKAO, social_id=kakao_id).first()

        if social_user:
            user = social_user.user
            self._validate_user_status(user)
            if name:
                user.name = name[:30]
            if profile_image_url:
                user.profile_image_url = profile_image_url
            if phone_number:
                user.phone_number = phone_number
            if birthday_date:
                user.birthday = birthday_date
            user.save(update_fields=["name", "profile_image_url", "phone_number", "birthday"])
            return user

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            self._validate_user_status(existing_user)
            SocialUser.objects.get_or_create(user=existing_user, provider=SocialTypeChoice.KAKAO, social_id=kakao_id)
            return existing_user

        with transaction.atomic():
            user = User.objects.create(
                email=email,
                name=name[:30] if name else "카카오유저",
                phone_number=phone_number if phone_number else None,
                birthday=birthday_date or None,
                profile_image_url=profile_image_url or "",
                social_type=SocialTypeChoice.KAKAO,
                is_active=True,
            )
            SocialUser.objects.get_or_create(user=user, provider=SocialTypeChoice.KAKAO, social_id=kakao_id)
        return user

    @staticmethod
    def _validate_user_status(user: Any) -> None:
        if not user.is_active:
            raise ValidationError({"code": "inactive_user", "message": "비활성화된 계정입니다."})
        if UserWithdrawal.objects.filter(user=user).exists():
            raise ValidationError({"code": "withdrawn_user", "message": "탈퇴 신청한 계정입니다."})


class GoogleOAuthService:
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

    def get_auth_url(self) -> tuple[str, str]:
        state = uuid.uuid4().hex
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
        }
        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}", state

    def get_access_token(self, code: str, state: str) -> str:
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "code": code,
        }
        response = requests.post(self.TOKEN_URL, data=data, timeout=10)
        response.raise_for_status()
        return cast(str, response.json().get("access_token"))

    def get_token_info(self, access_token: str) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(self.USER_INFO_URL, headers=headers, timeout=10)
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    def get_or_create_user(self, user_info: dict[str, Any]) -> Any:
        google_id = str(user_info.get("sub"))
        email = user_info.get("email")
        if not email:
            raise ValidationError({"code": "email_required", "message": "구글 계정에 이메일이 없습니다."})

        name = user_info.get("name")
        profile_image_url = user_info.get("picture", "")

        social_user = SocialUser.objects.filter(provider=SocialTypeChoice.GOOGLE, social_id=google_id).first()

        if social_user:
            user = social_user.user
            self._validate_user_status(user)
            if name:
                user.name = name[:30]
            if profile_image_url:
                user.profile_image_url = profile_image_url
            user.save(update_fields=["name", "profile_image_url"])
            return user

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            self._validate_user_status(existing_user)
            SocialUser.objects.get_or_create(user=existing_user, provider=SocialTypeChoice.GOOGLE, social_id=google_id)
            return existing_user

        with transaction.atomic():
            user = User.objects.create(
                email=email,
                name=name[:30] if name else "구글유저",
                phone_number=None,
                birthday=None,
                profile_image_url=profile_image_url or "",
                social_type=SocialTypeChoice.GOOGLE,
                is_active=True,
            )
            SocialUser.objects.get_or_create(user=user, provider=SocialTypeChoice.GOOGLE, social_id=google_id)
        return user

    @staticmethod
    def _validate_user_status(user: Any) -> None:
        if not user.is_active:
            raise ValidationError({"code": "inactive_user", "message": "비활성화된 계정입니다."})
        if UserWithdrawal.objects.filter(user=user).exists():
            raise ValidationError({"code": "withdrawn_user", "message": "탈퇴 신청한 계정입니다."})
