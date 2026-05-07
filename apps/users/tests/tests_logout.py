from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models.models import User


class LogoutTestCase(TestCase):
    client: APIClient
    user: User
    email: str
    password: str
    logout_url: str
    refresh: RefreshToken

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="test@test.com", password="pw1234!@", birthday="1999-05-11", name="테스트"
        )
        cls.logout_url = reverse("users:logout")

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.refresh: RefreshToken = RefreshToken.for_user(self.user)

    # 로그아웃 성공 테스트
    def test_logout_success(self) -> None:
        payload = {"refresh": str(self.refresh)}

        response = self.client.post(self.logout_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual("성공적으로 로그아웃 되었습니다.", response.data["detail"])

    # 인증되지 않은 사용자가 접근할 경우
    def test_logout_unauthorized(self) -> None:
        self.client.force_authenticate(user=None)
        payload = {"refresh"}

        response = self.client.post(self.logout_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
