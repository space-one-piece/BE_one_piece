from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.response import Response
from rest_framework.test import APIClient

from apps.chatbot.models import ChatSession
from apps.chatbot.views.chat_views import delete_session_store, set_session_store

User = get_user_model()


class ChatSessionCreateViewTest(TestCase):
    def setUp(self) -> None:
        self.client: APIClient = APIClient()
        self.user = User.objects.create_user(
            email="test@test.com",
            password="testpassword123!",
            birthday=date(1995, 1, 1),
        )
        self.client.force_authenticate(user=self.user)

    def test_create_session_success(self) -> None:
        response: Response = self.client.post(
            "/api/v1/chatbot/sessions/",
            {"message": "향수 추천해줘"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.data["data"])

    def test_create_session_no_message(self) -> None:
        response: Response = self.client.post(
            "/api/v1/chatbot/sessions/",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_session_unauthenticated(self) -> None:
        self.client.force_authenticate(user=None)
        response: Response = self.client.post(
            "/api/v1/chatbot/sessions/",
            {"message": "향수 추천해줘"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)


class ChatSessionEndViewTest(TestCase):
    def setUp(self) -> None:
        self.client: APIClient = APIClient()
        self.user = User.objects.create_user(
            email="test2@test.com",
            password="testpassword123!",
            birthday=date(1995, 1, 1),
        )
        self.client.force_authenticate(user=self.user)
        self.session = ChatSession.objects.create(
            user=self.user,
            status="active",
        )
        set_session_store(
            self.session.id,
            {
                "messages": [],
                "context": {"space": None, "mood": None, "intensity": None, "time": None},
                "total_turns": 0,
                "meaningful_turns": 0,
                "excluded_ids": [],
            },
        )

    def tearDown(self) -> None:
        delete_session_store(self.session.id)

    def test_end_session_success(self) -> None:
        response: Response = self.client.patch(
            f"/api/v1/chatbot/sessions/{self.session.id}/",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("ended_at", response.data["data"])

    def test_end_session_not_found(self) -> None:
        response: Response = self.client.patch(
            "/api/v1/chatbot/sessions/9999/",
        )
        self.assertEqual(response.status_code, 404)

    def test_end_session_unauthenticated(self) -> None:
        self.client.force_authenticate(user=None)
        response: Response = self.client.patch(
            f"/api/v1/chatbot/sessions/{self.session.id}/",
        )
        self.assertEqual(response.status_code, 401)

    def test_end_session_other_user(self) -> None:
        other_user = User.objects.create_user(
            email="other@test.com",
            password="testpassword123!",
            birthday=date(1995, 1, 1),
            phone_number="010-9999-9999",
        )
        self.client.force_authenticate(user=other_user)
        response: Response = self.client.patch(
            f"/api/v1/chatbot/sessions/{self.session.id}/",
        )
        self.assertEqual(response.status_code, 404)
