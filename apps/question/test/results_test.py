from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from apps.analysis.models import Scent
from apps.question.models import Question, QuestionsAnswer, QuestionsResults
from apps.users.models.models import User


class ResultsAPIViewTest(TestCase):
    client: APIClient
    user: User
    question: Question
    question_results: QuestionsResults
    scent: Scent

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            username="test",
            email="test@naver.com",
            password="test1234!@",
        )
        cls.question = Question.objects.create(content="아침에 선호하는 향", left_label="포근한", right_label="산뜻한")
        QuestionsAnswer.objects.create(question=cls.question, answer="상쾌한")
        QuestionsAnswer.objects.create(question=cls.question, answer="포근한")
        cls.scent.objects.create(name="우디 샌달우드", eng_name="Woody Sandalwood", intensity=4)
        cls.question_results = QuestionsResults.objects.create(
            user=cls.user, scent=cls.scent, division="K", questions_json=" ", answer_ai=" "
        )

    def test_result_success(self) -> None:
        self.client.force_login(user=self.user)
        url = reverse("review_results", kwargs={"results_id": self.question_results.id})
        data = {
            "review": "리뷰",
            "rating": 4,
        }
        response = self.client.patch(url, data, content_type="application/json")
        get_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_data["rating"], 4)

    def test_result_web_share_success(self) -> None:
        self.client.force_login(user=self.user)
        url = reverse("web_share", kwargs={"results_id": self.question_results.id})
        response = self.client.post(url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_result_web_share_fail(self) -> None:
        url = reverse("web_share", kwargs={"results_id": self.question_results.id})
        response = self.client.post(url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_question_result_success(self) -> None:
        url = reverse("question_results", kwargs={"results_id": "LV3Xyp0yKJYo"})
        response = self.client.get(url, content_type="application/json")
        get_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_data["rating"], 4)

    def test_question_result_fail(self) -> None:
        url = reverse("question_results", kwargs={"results_id": "397Y68188X1v"})
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_question_list_success(self) -> None:
        self.client.force_login(user=self.user)
        url = reverse("results", kwargs={"division": "keywords"})
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_question_list_fail(self) -> None:
        url = reverse("results", kwargs={"division": "keywords"})
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
