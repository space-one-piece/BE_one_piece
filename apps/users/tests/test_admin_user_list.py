from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.users.models.models import User


class AdminUserListTest(TestCase):
    client: APIClient
    admin_user: User
    user: User
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
        cls.user = User.objects.create_user(
            email="user@user.com", password="pw1234!@", name="검색대상", phone_number="01015240223", birthday="2000-11-11"
        )
        cls.url = reverse("admin_users:admin-list")

    def setUp(self) -> None:
        self.client = APIClient()

    # 정상 조회
    def test_get_user_list_success(self) -> None:
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], User.objects.count())

    # search 필터
    def test_get_user_list_search_by_name(self) -> None:
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.url, {"search": "검색대상"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "검색대상")

    # 비로그인 접근
    def test_get_user_list_unauthorized(self) -> None:
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error_detail", response.data)

    # 일반 유저 접근
    def test_get_user_list_forbidden(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error_detail", response.data)
