from typing import Any

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
            email="test@test.com", password="test1234!@", birthday="1999-05-11", name="테스트", gender="M"
        )
        cls.url = reverse("users:token_refresh")

    def setUp(self) -> None:
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token_str = str(refresh)

    # 재발급 성공 테스트
    def test_refresh_token_success(self) -> None:
        data = {"refresh": self.refresh_token_str}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    # 필수값(refresh_token)값 누락
    def test_refresh_missing_field(self) -> None:
        data: dict[str, Any] = {}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual("필수값이 누락되었습니다.", response.data["error_detail"])
