from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.users.models.models import User


class AdminUserDeleteTest(TestCase):
    client: APIClient
    admin_user: User
    user: User
    target_user: User
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin_user = User.objects.create_superuser(
            email="admin@admin.com",
            password="pw1234!@",
            name="관리자",
            phone_number="01012340923",
            birthday="1990-04-20",
        )
        cls.user = User.objects.create_user(
            email="test@test.com", password="pw1234!@", name="테스터", phone_number="01015240923", birthday="2000-11-21"
        )
        cls.target_user = User.objects.create_user(
            email="user@user.com",
            password="pw1234!@",
            name="조회대상",
            phone_number="01015240223",
            birthday="2000-11-11",
        )
        cls.url = reverse("admin_users:admin-detail", kwargs={"account_id": cls.target_user.id})

    def setUp(self) -> None:
        self.client = APIClient()

    # 삭제 성공
    def test_delete_success(self) -> None:
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        excepted_detail = f"유저 데이터가 삭제되었습니다. -pk:{self.target_user.id}"
        self.assertEqual(response.data["detail"], excepted_detail)
        self.assertFalse(User.objects.filter(id=self.target_user.id).exists())

    # 존재하지 않는 유저
    def test_delete_user_not_found(self) -> None:
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("admin_users:admin-detail", kwargs={"account_id": 99999})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error_detail", response.data)

    # 일반 유저 접근
    def test_delete_user_forbidden(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error_detail", response.data)
