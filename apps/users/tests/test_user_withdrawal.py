from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.users.choices import UserStatus, WithdrawalReason
from apps.users.models.models import User


class UserWithdrawalTest(TestCase):
    client: APIClient
    user: User
    email: str
    password: str
    name: str
    birthday: str
    phone_number: str
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.password = "pw1234!@"
        cls.user = User.objects.create_user(
            email="test@test.com",
            password=cls.password,
            name="테스터",
            birthday="1999-11-21",
            phone_number="01023410234",
        )
        cls.url = reverse("users:me")

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    # 탈퇴 성공
    def test_user_withdrawal_success(self) -> None:
        data = {
            "password": self.password,
            "confirm": True,
            "reason": WithdrawalReason.NO_LONGER_NEEDED,
            "other_reason": "테스트 탈퇴 사유",
        }

        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertEqual(self.user.status, UserStatus.WITHDRAWN)
