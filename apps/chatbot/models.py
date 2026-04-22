from django.db import models

from apps.core.models import TimeStampModel


class ChatSession(TimeStampModel):
    STATUS_CHOICES = [
        ("active", "활성"),
        ("inactive", "비활성"),
        ("timeout", "타임아웃"),
    ]

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, db_column="user_id")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    last_active_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "chat_session"

    def __str__(self) -> str:
        return f"ChatSession({self.id}, {self.user_id}, {self.status})"


class ChatbotRecommendation(TimeStampModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, db_column="user_id")
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, db_column="session_id")
    scent = models.ForeignKey("analysis.Scent", on_delete=models.CASCADE, db_column="scent_id")
    retry_count = models.IntegerField(default=0)
    is_saved = models.BooleanField(default=False)
    saved_at = models.DateTimeField(null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)
    review = models.TextField(null=True, blank=True)
    reply = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "chatbot_recommendation"

    def __str__(self) -> str:
        return f"ChatbotRecommendation({self.id}, {self.user_id}, {self.scent_id})"
