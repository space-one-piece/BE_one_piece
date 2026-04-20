from datetime import date
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.response import Response
from rest_framework.test import APIClient

from apps.analysis.models import Scent
from apps.chatbot.models import ChatbotRecommendation, ChatSession
from apps.chatbot.views.chat_views import delete_session_store, get_session_store, set_session_store

User = get_user_model()


class ChatbotRecommendationViewTest(TestCase):
    def setUp(self) -> None:
        self.client: APIClient = APIClient()
        self.user = User.objects.create_user(
            email="test@test.com",
            password="testpassword123!",
            birthday=date(1995, 1, 1),
        )
        self.client.force_authenticate(user=self.user)
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
        self.recommendation = ChatbotRecommendation.objects.create(
            user=self.user,
            session=self.session,
            scent=self.scent,
        )
        set_session_store(
            self.session.id,
            {
                "messages": [{"role": "user", "parts": [{"text": "향수 추천해줘"}]}],
                "context": {"space": "bedroom", "mood": "calm", "intensity": "light", "time": None},
                "total_turns": 1,
                "meaningful_turns": 1,
                "excluded_ids": [self.scent.id],
            },
        )

    def tearDown(self) -> None:
        delete_session_store(self.session.id)

    # 추천 결과 저장
    def test_save_recommendation_success(self) -> None:
        response: Response = self.client.patch(
            f"/api/v1/chatbot/sessions/{self.session.id}/recommendations/{self.recommendation.id}/save/",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["data"]["is_saved"])

    def test_save_recommendation_not_found(self) -> None:
        response: Response = self.client.patch(
            f"/api/v1/chatbot/sessions/{self.session.id}/recommendations/9999/save/",
        )
        self.assertEqual(response.status_code, 404)

    def test_save_recommendation_unauthenticated(self) -> None:
        self.client.force_authenticate(user=None)
        response: Response = self.client.patch(
            f"/api/v1/chatbot/sessions/{self.session.id}/recommendations/{self.recommendation.id}/save/",
        )
        self.assertEqual(response.status_code, 401)

    # 재추천 가능 여부 조회
    def test_retry_status_success(self) -> None:
        response: Response = self.client.get(
            f"/api/v1/chatbot/sessions/{self.session.id}/recommendations/retry/status/",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("retry_count", response.data["data"])
        self.assertIn("retry_available", response.data["data"])

    def test_retry_status_session_not_found(self) -> None:
        response: Response = self.client.get(
            "/api/v1/chatbot/sessions/9999/recommendations/retry/status/",
        )
        self.assertEqual(response.status_code, 404)

    def test_retry_status_store_not_found(self) -> None:
        delete_session_store(self.session.id)
        response: Response = self.client.get(
            f"/api/v1/chatbot/sessions/{self.session.id}/recommendations/retry/status/",
        )
        self.assertEqual(response.status_code, 404)

    # 재추천 요청
    @patch("apps.chatbot.services.chatbot_service.client")
    def test_retry_success(self, mock_client: MagicMock) -> None:
        mock_client.models.generate_content.return_value.text = "[ID: 8] 샌달 콰이어트를 추천드려요."
        response: Response = self.client.post(
            f"/api/v1/chatbot/sessions/{self.session.id}/recommendations/retry/",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("reply", response.data["data"])
        self.assertIn("retry_count", response.data["data"])

    @patch("apps.chatbot.services.chatbot_service.client")
    def test_retry_exceeded(self, mock_client: MagicMock) -> None:
        store = get_session_store(self.session.id)
        if store:
            store["excluded_ids"] = [1, 2, 3]
            set_session_store(self.session.id, store)
        response: Response = self.client.post(
            f"/api/v1/chatbot/sessions/{self.session.id}/recommendations/retry/",
        )
        self.assertEqual(response.status_code, 429)

    def test_retry_session_not_found(self) -> None:
        response: Response = self.client.post(
            "/api/v1/chatbot/sessions/9999/recommendations/retry/",
        )
        self.assertEqual(response.status_code, 404)

    def test_retry_store_not_found(self) -> None:
        delete_session_store(self.session.id)
        response: Response = self.client.post(
            f"/api/v1/chatbot/sessions/{self.session.id}/recommendations/retry/",
        )
        self.assertEqual(response.status_code, 404)
