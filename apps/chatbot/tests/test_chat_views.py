from datetime import date
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.response import Response
from rest_framework.test import APIClient

from apps.chatbot.models import ChatSession

User = get_user_model()


class ChatMessageViewTest(TestCase):
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

    @patch("apps.chatbot.services.chatbot_service.client")
    def test_message_send_success(self, mock_client: MagicMock) -> None:
        mock_client.models.generate_content.return_value.text = "어떤 공간에서 사용하실 예정이세요?"

        response: Response = self.client.post(
            f"/api/v1/chatbot/sessions/{self.session.id}/messages/",
            {"message": "향수 추천해줘"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("reply", response.data["data"])

    @patch("apps.chatbot.services.chatbot_service.client")
    def test_message_empty(self, mock_client: MagicMock) -> None:
        response: Response = self.client.post(
            f"/api/v1/chatbot/sessions/{self.session.id}/messages/",
            {"message": ""},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_message_unauthenticated(self) -> None:
        self.client.force_authenticate(user=None)
        response: Response = self.client.post(
            f"/api/v1/chatbot/sessions/{self.session.id}/messages/",
            {"message": "향수 추천해줘"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_message_session_not_found(self) -> None:
        response: Response = self.client.post(
            "/api/v1/chatbot/sessions/9999/messages/",
            {"message": "향수 추천해줘"},
            format="json",
        )
        self.assertEqual(response.status_code, 404)
