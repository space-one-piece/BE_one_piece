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
        QuestionsResults.objects.all().delete()
        QuestionsAnswer.objects.all().delete()
        Question.objects.all().delete()
        Scent.objects.all().delete()

        cls.user = User.objects.create_user(
            email="test@naver.com", password="test1234!@", birthday="1970-01-01", phone_number="010-0000-0000"
        )
        cls.question = Question.objects.create(
            content="아침에 선호하는 향", additional="설명", left_label="포근한", right_label="산뜻한"
        )
        QuestionsAnswer.objects.create(question=cls.question, answer="상쾌한")
        QuestionsAnswer.objects.create(question=cls.question, answer="포근한")
        cls.scent = Scent.objects.create(name="우디 샌달우드", eng_name="Woody Sandalwood", intensity=4)
        cls.question_results = QuestionsResults.objects.create(
            user=cls.user, scent=cls.scent, division="K", questions_json=" ", answer_ai=" "
        )

    def setUp(self) -> None:
        self.client = APIClient()

    def test_image_save_success(self) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse("image_user")
        data = {
            "image_url": "https://oz-externship-bucket.s3.ap-northeast-2.amazonaws.com/media/perfumes/result_7b2.jpg?X-Amz-Alg"
        }
        response = self.client.patch(url, data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_image_save_fail(self) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse("image_user")
        data = {"image_url": ""}
        response = self.client.patch(url, data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_image_new_fail(self) -> None:
        url = reverse("user_image", kwargs={"requests_id": self.question_results.pk})
        response = self.client.post(url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
