import json

from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.users.models.models import User


class LoginTestCase(TestCase):
    client: APIClient
    user: User
    email: str
    password: str
    login_url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.email = "test@test.com"
        cls.password = "pw1234!@"
        cls.user = User.objects.create_user(
            email=cls.email,
            password=cls.password,
            name="한조각",
            birthday="2000-05-11",
            phone_number="010-1234-1234",
            gender="M",
        )
        cls.login_url = reverse("login")

    def setUp(self) -> None:
        self.client = APIClient()

    # 성공 테스트
    def test_login_success(self) -> None:
        data = {"email": self.email, "password": self.password}
        response = self.client.post(self.login_url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], self.email)

    # 잘못된 비밀번호 입력시 실패 테스트
    def test_login_invalid_password(self) -> None:
        data = {"email": self.email, "password": "wrongpassword"}
        response = self.client.post(self.login_url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")

    # 비활성 계정 겁근시 로그인실패 테스트
    def test_login_inactive_user(self) -> None:
        self.user.is_active = False
        self.user.save()

        data = {"email": self.email, "password": self.password}
        response = self.client.post(self.login_url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "권한이 없습니다.")
