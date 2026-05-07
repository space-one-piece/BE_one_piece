from typing import Any

from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.users.models.models import User


class ProfileTests(TestCase):
    client: APIClient
    user: User
    email: str
    password: str
    phone_number: str
    birthday: str
    name: str
    url: str
    user_data: dict[str, Any]

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user_data = {
            "email": "test@test.com",
            "password": "pw1234!@",
            "phone_number": "01012341234",
            "birthday": "1996-02-12",
            "name": "겐지",
        }
        cls.user = User.objects.create(**cls.user_data)
        cls.url = reverse("users:profile")

    def setUp(self) -> None:
        self.client = APIClient()

    # 프로필 조회 성공 테스트
    def test_get_profile_success(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["name"], self.user.name)
        self.assertEqual(response.data["phone_number"], self.user.phone_number)
        self.assertEqual(str(response.data["birthday"]), str(self.user.birthday))

    # 로그인하지 않은 사용자의 정보 조회
    def test_user_profile_fail(self) -> None:
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Authentication credentials were not provided", str(response.data["error_detail"]))

    # 유저프로필 수정 성공
    def test_user_profile_update(self) -> None:
        self.client.force_authenticate(user=self.user)
        update_data = {"name": "한조"}

        response = self.client.patch(self.url, data=update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "한조")
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "한조")
