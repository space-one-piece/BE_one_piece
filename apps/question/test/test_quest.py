# Create your tests here.

from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.question.models import Question, QuestionsAnswer
from apps.users.models.models import User


class QuestionAPIViewTest(TestCase):
    client: APIClient
    user: User
    question: Question

    @classmethod
    def setUpTestData(cls) -> None:
        QuestionsAnswer.objects.all().delete()
        Question.objects.all().delete()

        cls.user = User.objects.create_user(
            email="test@naver.com", password="test1234!@", birthday="1970-01-01", phone_number="010-0000-0000"
        )
        cls.question = Question.objects.create(
            content="아침에 선호하는 향", additional="설명", left_label="포근한", right_label="산뜻한"
        )
        QuestionsAnswer.objects.create(question=cls.question, answer="상쾌한")
        QuestionsAnswer.objects.create(question=cls.question, answer="포근한")

    def setUp(self) -> None:
        self.client = APIClient()

    def test_question_list_success(self) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse("question")
        response = self.client.get(url, content_type="application/json")
        get_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_data), 1)
        self.assertEqual(get_data[0]["title"], "아침에 선호하는 향")

    def test_question_list_fail(self) -> None:
        url = reverse("question")
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
