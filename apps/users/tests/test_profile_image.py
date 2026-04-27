from unittest.mock import MagicMock, patch

from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.users.models.models import User


class ProfileImageTests(TestCase):
    client: APIClient
    user: User
    url: str
    presigned_url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create(
            email="test@test.com", password="pw1234!@", phone_number="01012342123", birthday="1999-09-14", name="테스터"
        )
        cls.url = reverse("users:profile_image")
        cls.presigned_url = reverse("users:presigned_url")

    def setUp(self) -> None:
        self.client = APIClient()

    # 프로필 이미지 등록 성공
    def test_update_profile_image(self) -> None:
        self.client.force_authenticate(user=self.user)
        img_url = "https://testimg.png"

        response = self.client.patch(self.url, data={"profile_image_url": img_url}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "프로필 사진이 등록되었습니다.")
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile_image_url, img_url)

    # 비로그인 사용자 실패
    def test_update_profile_fail_unauthorized(self) -> None:
        img_url = "https://testimg.png"

        response = self.client.patch(self.url, data={"profile_image_url": img_url}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Authentication credentials were not provided", str(response.data["error_detail"]))

    # presigned_url 발급
    @patch("apps.core.services.presigned_url_service.PresignedUrlService.create")
    def test_get_presigned_url_success(self, mock_create: MagicMock) -> None:
        self.client.force_authenticate(user=self.user)
        mock_create.return_value = {
            "presigned_url": "https://testimg.s3.amazonaws.com/",
            "img_url": "https://testimg.png",
            "key": "uploads/images/profiles/uuid_photo.png",
        }

        response = self.client.put(self.presigned_url, data={"file_name": "photo.png"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("presigned_url", response.data)
        self.assertIn("img_url", response.data)
        self.assertIn("key", response.data)
        mock_create.assert_called_once_with(folder="profiles", file_name="photo.png")

    # 허용되지 않은 확장자
    @patch("apps.core.services.presigned_url_service.PresignedUrlService.create")
    def test_get_presigned_url_fail_invalid_extension(self, mock_create: MagicMock) -> None:
        self.client.force_authenticate(user=self.user)
        mock_create.side_effect = Exception("지원하지 않는 파일 형식입니다.")

        response = self.client.put(self.presigned_url, data={"file_name": "photo.gif"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)

    # 비로그인 사용자
    def test_get_presigned_url_fail_unauthorized(self) -> None:
        response = self.client.put(self.presigned_url, data={"file_name": "photo.pnh"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Authentication credentials were not provided", str(response.data["error_detail"]))
