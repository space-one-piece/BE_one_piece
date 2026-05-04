from typing import Any
from unittest.mock import patch

from django.contrib.auth import get_user_model
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
            email="test@test.com",
            name="조각",
            password="pw1234!@",
            birthday="2000-05-21",
            phone_number="010-1234-1242",
        )

        self.kakao_callback_url = reverse("users:kakao_social_callback")
        self.naver_callback_url = reverse("users:naver_social_callback")
        self.google_callback_url = reverse("users:google_social_callback")

    # kakao test
    @patch("apps.users.services.social_login_services.KaKaoOAuthService.get_access_token")
    @patch("apps.users.services.social_login_services.KaKaoOAuthService.get_token_info")
    @patch("apps.users.services.social_login_services.KaKaoOAuthService.get_or_create_user")
    def test_kakao_login_success(
        self, mock_get_or_create_user: Any, mock_get_token_info: Any, mock_get_access_token: Any
    ) -> None:
        mock_get_or_create_user.return_value = self.user
        session = self.client.session
        session["social_login_state"] = "test_state"
        session.save()

        response = self.client.get(self.kakao_callback_url, {"code": "test_code", "state": "test_state"})

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn("http://localhost:5173", response.url)  # type: ignore
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

        response = self.client.get(self.naver_callback_url, {"code": "test_code", "state": "test_state"})

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn("http://localhost:5173", response.url)  # type: ignore
        self.assertIn("refresh_token", response.cookies)

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

        response = self.client.get(self.google_callback_url, {"code": "test_code", "state": "test_state"})
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn("http://localhost:5173", response.url)  # type: ignore
        self.assertIn("refresh_token", response.cookies)

    # 실패 테스트
    def test_login_failure_invalid_state(self) -> None:
        session = self.client.session
        session["social_login_state"] = "correct_state"
        session.save()

        response = self.client.get(self.kakao_callback_url, {"code": "test_code", "state": "wrong_state"})
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn("is_success=false", response.url)  # type: ignore
        self.assertIn("detail=", response.url)  # type: ignore
