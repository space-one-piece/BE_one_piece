from typing import Any, cast
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class SocialLoginTest(APITestCase):
    user: Any
    kakao_callback_url: str
    naver_callback_url: str
    google_callback_url: str

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@test.com", name="조각", password="pw1234!@", birthday="2000-05-21", phone_number="010-1234-1242"
        )

        self.kakao_callback_url = reverse("users:kakao_callback")
        self.naver_callback_url = reverse("users:naver_callback")
        self.google_callback_url = reverse("users:google_callback")

    # kakao test
    @patch("apps.users.services.social_login_services.KakaoOAuthService.get_access_token")
    @patch("apps.users.services.social_login_services.KakaoOAuthService.get_token_info")
    @patch("apps.users.services.social_login_services.KakaoOAuthService.get_or_create_user")
    def test_kakao_login_success(
        self, mock_get_or_create_user: Any, mock_get_token_info: Any, mock_get_access_token: Any
    ) -> None:
        mock_get_or_create_user.return_value = self.user

        session = self.client.session
        session["social_login_state"] = "test_state"
        session.save()

        response = cast(
            HttpResponseRedirect, self.client.get(self.kakao_callback_url, {"code": "test_code", "state": "test_state"})
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn("provider=kakao", response.url)
        self.assertIn("is_success=true", response.url)
        self.assertIn("refresh_token", response.cookies)

    # naver test
    @patch("apps.users.services.social_login_services.NaverOAuthService.get_access_token")
    @patch("apps.users.services.social_login_services.NaverOAuthService.get_token_info")
    @patch("apps.users.services.social_login_services.NaverOAuthService.get_or_create_user")
    def test_naver_login_success(
        self, mock_get_user: Any, mock_get_token_info: Any, mock_get_access_token: Any
    ) -> None:
        mock_get_user.return_value = self.user

        session = self.client.session
        session["social_login_state"] = "test_state"
        session.save()

        response = cast(
            HttpResponseRedirect, self.client.get(self.naver_callback_url, {"code": "test_code", "state": "test_state"})
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn("provider=naver", response.url)
        self.assertIn("is_success=true", response.url)

    # google test
    @patch("apps.users.services.social_login_services.GoogleOAuthService.get_access_token")
    @patch("apps.users.services.social_login_services.GoogleOAuthService.get_token_info")
    @patch("apps.users.services.social_login_services.GoogleOAuthService.get_or_create_user")
    def test_google_login_success(
        self, mock_get_user: Any, mock_get_token_info: Any, mock_get_access_token: Any
    ) -> None:
        mock_get_user.return_value = self.user

        session = self.client.session
        session["social_login_state"] = "test_state"
        session.save()

        # 구글이 아닌 카카오로 콜백을 해서 실패
        response = cast(
            HttpResponseRedirect,
            self.client.get(self.kakao_callback_url, {"code": "test_code", "state": "wrong_state"}),
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn("provider=google", response.url)
        self.assertIn("is_success=true", response.url)

    # 실패 테스트
    def test_login_failure_invalid_state(self) -> None:
        session = self.client.session
        session["social_login_state"] = "correct_state"
        session.save()

        response = cast(
            HttpResponseRedirect,
            self.client.get(self.kakao_callback_url, {"code": "test_code", "state": "wrong_state"}),
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn("is_success=false", response.url)
