from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.chatbot.models import ChatSession
from apps.chatbot.serializers import ChatSessionSerializer

User = get_user_model()


class ChatSerializerTest(TestCase):
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

    def test_session_serializer_fields(self) -> None:
        serializer = ChatSessionSerializer(self.session)
        self.assertIn("id", serializer.data)
        self.assertIn("status", serializer.data)
        self.assertIn("created_at", serializer.data)

    def test_session_serializer_status(self) -> None:
        serializer = ChatSessionSerializer(self.session)
        self.assertEqual(serializer.data["status"], "active")
