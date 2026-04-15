from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.analysis.models import Scent
from apps.chatbot.models import ChatbotRecommendation, ChatSession

User = get_user_model()


class ChatModelTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@test.com",
            password="testpassword123!",
            birthday=date(1995, 1, 1),
        )
        self.session = ChatSession.objects.create(
            user=self.user,
            status="active",
        )
        self.scent = Scent.objects.create(
            name="테스트 향수",
            eng_name="Test Scent",
            categories="floral",
            intensity=60,
        )

    def test_chat_session_create(self) -> None:
        self.assertEqual(self.session.user, self.user)
        self.assertEqual(self.session.status, "active")
        self.assertIsNone(self.session.ended_at)
        self.assertIsNotNone(self.session.created_at)

    def test_chat_session_str(self) -> None:
        self.assertEqual(
            str(self.session), f"ChatSession({self.session.id}, {self.session.user_id}, {self.session.status})"
        )

    def test_chat_session_default_status(self) -> None:
        session = ChatSession.objects.create(user=self.user)
        self.assertEqual(session.status, "active")

    def test_chatbot_recommendation_create(self) -> None:
        recommendation = ChatbotRecommendation.objects.create(
            user=self.user,
            session=self.session,
            scent=self.scent,
        )
        self.assertEqual(recommendation.user, self.user)
        self.assertEqual(recommendation.session, self.session)
        self.assertEqual(recommendation.scent, self.scent)
        self.assertEqual(recommendation.retry_count, 0)
        self.assertFalse(recommendation.is_saved)
        self.assertIsNone(recommendation.saved_at)

    def test_chatbot_recommendation_str(self) -> None:
        recommendation = ChatbotRecommendation.objects.create(
            user=self.user,
            session=self.session,
            scent=self.scent,
        )
        self.assertEqual(
            str(recommendation),
            f"ChatbotRecommendation({recommendation.id}, {recommendation.user_id}, {recommendation.scent_id})",
        )
