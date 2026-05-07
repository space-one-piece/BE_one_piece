import uuid
from datetime import timedelta

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.users.choices import UserStatus, WithdrawalReason
from apps.users.models.models import User, UserWithdrawal


class UserRecoveryTest(TestCase):
    client: APIClient
    user: User
    email: str
    password: str
    phone_number: str
    url: str
    birthday: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.email = "test@test.com"
        cls.password = "pw1234!@"
        cls.user = User.objects.create_user(
            email=cls.email,
            password=cls.password,
            name="테스터",
            birthday="1999-06-11",
            phone_number="01014231523",
            is_active=False,
            status=UserStatus.WITHDRAWN,
        )
        UserWithdrawal.objects.create(
            user=cls.user,
            reason=WithdrawalReason.NO_LONGER_NEEDED,
            scheduled_delete_at=timezone.now() + timedelta(days=14),
        )
        cls.url = reverse("users:account_recovery")

    def setUp(self) -> None:
        self.client = APIClient()
        cache.clear()

    # 복구 성공
    def test_user_recovery_success(self) -> None:
        recovery_token = str(uuid.uuid4())
        cache.set(f"signup_token_{recovery_token}", self.email, timeout=600)

        data = {"email": self.email, "password": self.password, "recovery_token": recovery_token}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertEqual(self.user.status, UserStatus.ACTIVE)

        with self.assertRaises(UserWithdrawal.DoesNotExist):
            UserWithdrawal.objects.get(user=self.user)

    # 비밀번호 불일치
    def test_user_recovery_failure(self) -> None:
        recovery_token = str(uuid.uuid4())
        cache.set(f"signup_token_{recovery_token}", self.email, timeout=600)

        data = {"email": self.email, "password": "funpassword", "recovery_token": recovery_token}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("비밀번호가 일치하지 않습니다.", str(response.data))
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    # 유예기간이 지난 경우
    def test_user_recovery_fail_expired_period(self) -> None:
        recovery_token = str(uuid.uuid4())
        cache.set(f"signup_token_{recovery_token}", self.email, timeout=600)

        withdrawal_info = UserWithdrawal.objects.get(user=self.user)
        withdrawal_info.scheduled_delete_at = timezone.now() - timedelta(days=14)
        withdrawal_info.save()

        data = {"email": self.email, "password": self.password, "recovery_token": recovery_token}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("복구 가능 기간이 지났거나 탈퇴 정보가 없습니다.", str(response.data))
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
