# Create your tests here.
# Create your tests here.
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
            username="test",
            email="test@naver.com",
            password="test1234!@",
        )
        cls.keyword = Keyword.objects.create(division="MO", name="포근한")
        cls.keyword = Keyword.objects.create(division="MO", name="산뜻한")

    def setUp(self) -> None:
        self.client = APIClient()

    def test_keyword_list_return(self) -> None:
        self.client.force_login(user=self.user)
        url = reverse("keyword")
        response = self.client.get(url, content_type="application/json")
        get_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_data), 2)
        self.assertEqual(get_data[0]["name"], "포근한")
