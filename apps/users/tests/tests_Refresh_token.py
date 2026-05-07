from typing import cast

from django.conf import settings
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models.models import User


class RefreshTokenTest(TestCase):
    client: APIClient
    user: User
    url: str
    refresh_token_str: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="test@test.com", password="test1234!@", birthday="1999-05-11", name="테스트"
        )
        cls.url = reverse("users:token_refresh")

    def setUp(self) -> None:
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token_str = str(refresh)

    # 재발급 성공 테스트
    def test_refresh_token_success(self) -> None:
        cookie_name = cast(str, settings.SIMPLE_JWT.get("AUTH_COOKIE", "refresh_token"))
        self.client.cookies[cookie_name] = self.refresh_token_str

        response = self.client.post(self.url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn(cookie_name, response.cookies)

    # 필수값(refresh_token)값 누락
    def test_refresh_missing_field(self) -> None:
        response = self.client.post(self.url, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "리프레시 토큰이 쿠키에 없습니다.")
