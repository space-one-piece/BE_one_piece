from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.users.models.models import User


class PasswordResetTestCase(TestCase):
    client: APIClient
    user: User
    email: str
    password: str
    login_url: str
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.email = "test@test.com"
        cls.user = User.objects.create_user(
            email=cls.email,
            password="pw1234!@",
            birthday="1999-12-11",
            name="테스터",
            gender="M",
            phone_number="01011115534",
        )
        cls.url = reverse("users:change_password")

    def tearDown(self) -> None:
        cache.clear()

    def setUp(self) -> None:
        self.client = APIClient()

    def test_password_reset_success(self) -> None:
        token = "valid-uuid-token"
        cache.set(f"signup_token_{token}", self.email, timeout=600)

        data = {"email": self.email, "token": token, "new_password": "new-secure-password213!"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "비밀번호가 성공적으로 변경되었습니다.")
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new-secure-password213!"))
        self.assertIsNone(cache.get(f"signup_token_{token}"))

    # 실패 검증
    def test_password_reset_invalid_token(self) -> None:
        data = {"email": self.email, "token": "invalid-token-123", "new_password": "dfewer1234"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], "인증 토큰이 유효하지 않거나 만료되었습니다.")

    def test_password_reset_user_not_found(self) -> None:
        token = "token-for-missing-user"
        non_existent_email = "none@test.com"
        cache.set(f"signup_token_{token}", non_existent_email, timeout=600)

        data = {"email": non_existent_email, "token": token, "new_password": "new-password123!"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("No User matches", str(response.data["error_detail"]))
