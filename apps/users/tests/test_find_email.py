from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.users.models.models import User


class FindEmailTest(TestCase):
    client: APIClient
    email: str
    name: str
    phone_number: str
    url: str
    birthday: str
    user: User

    @classmethod
    def setUpTestData(cls) -> None:
        cls.name = "테스터"
        cls.phone_number = "01011234215"
        cls.email = "test@example.com"
        cls.birthday = "1995-01-01"

        cls.user = User.objects.create_user(
            email=cls.email, name=cls.name, phone_number=cls.phone_number, birthday=cls.birthday
        )
        cls.url = reverse("users:find_email")

    def setUp(self) -> None:
        self.client = APIClient()

    def tearDown(self) -> None:
        cache.clear()

    def test_find_email_success(self) -> None:
        test_token = "valid_sms_token_123"
        cache.set(f"signup_token_{test_token}", self.phone_number, timeout=300)

        data = {"name": self.name, "phone_number": self.phone_number, "sms_token": test_token}

        response = self.client.post(self.url, data, format="json")

        print(f"DEBUG RESPONSE: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("email", response.data)
        self.assertTrue(response.data["email"].startswith(self.email[:2]))

    # 잘못된 토큰을 보냈을경우
    def test_find_email_invalid_token(self) -> None:
        db_user = User.objects.get(phone_number=self.phone_number)
        print(f"--- DB에 저장된 실제 이메일: {db_user.email} ---")
        data = {"name": self.name, "phone_number": self.phone_number, "sms_token": "invalid_token"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)

    # 사용자 정보가 없을 시
    def test_find_email_user_not_found(self) -> None:
        test_token = "valid_token_but_no_user"
        other_phone = "01043211234"
        cache.set(f"signup_token_{test_token}", other_phone, timeout=300)

        data = {"name": "누구냐넌", "phone_number": other_phone, "sms_token": test_token}

        response = self.client.post(self.url, data=data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND)
        self.assertIn("error_detail", response.data)
