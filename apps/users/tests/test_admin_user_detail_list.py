from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.users.models.models import User


class AdminUserListTest(TestCase):
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

    # 정상 조회
    def test_get_user_detail_success(self) -> None:
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.target_user.id)
        self.assertEqual(response.data["email"], self.target_user.email)
        self.assertEqual(response.data["name"], self.target_user.name)
        self.assertEqual(response.data["phone_number"], self.target_user.phone_number)
        self.assertEqual(response.data["birthday"], self.target_user.birthday)

    # 존재하지 않는 유저
    def test_get_user_detail_not_found(self) -> None:
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("admin_users:admin-detail", kwargs={"account_id": 9999})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error_detail", response.data)

    # 일반 유저 접근
    def test_get_user_detail_forbidden(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error_detail", response.data)
