from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from apps.users.models.models import User


class RefreshTokenTest(TestCase):
    client: APIClient
    user: User
    email: str
    password: str
    logout_url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="test@test.com",
            password="test1234!@"
        )
        cls.url = reverse("token_refresh")

    def setUp(self) -> None:
        self.client = APIClient()

    # 재발급 성공 테스트
    def test_refresh_token_success(self) -> None:
        data = {"refresh": self.refresh_token_str}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    # 필수값(refresh_token)값 누락
    def test_refresh_missing_field(self) -> None:
        data = {}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"], "필수 값이 누락되었습니다.")