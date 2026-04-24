from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.question.models import Keyword
from apps.users.models.models import User


class QuestionAPIViewTest(TestCase):
    client: APIClient
    user: User
    keyword: Keyword

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="test@naver.com", password="test1234!@", birthday="1970-01-01", phone_number="010-0000-0000"
        )

    def setUp(self) -> None:
        Keyword.objects.create(division="M", name="포근한", score={"softness": 15, "freshness": 10})
        Keyword.objects.create(division="M", name="산뜻한", score={"softness": 15, "freshness": 10})

        self.client = APIClient()

    def test_keyword_list_success(self) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse("keyword")
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_keyword_list_fail(self) -> None:
        url = reverse("keyword")
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_keyword_input_fail(self) -> None:
        url = reverse("keyword")
        data = [
            {"keyword_id": 1, "keyword_division": "MOOD", "keyword_name": "포근한"},
            {"keyword_id": 2, "keyword_division": "MOOD", "keyword_name": "산뜻한"},
        ]
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
