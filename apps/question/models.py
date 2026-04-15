from django.db import models

from apps.analysis.models import Scent
from apps.core.models import TimeStampModel
from apps.users.models.models import User


class Keyword(TimeStampModel):
    TYPE_CHOICES = [
        ("MO", "MOOD"),
        ("SP", "SPACE VIBE"),
        ("SC", "SCENT IMPRESSION"),
    ]

    division = models.CharField(null=False, blank=False, max_length=2, choices=TYPE_CHOICES)
    name = models.CharField(null=False, blank=False, max_length=10)

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        db_table = "keyword"
        verbose_name = "키워드"
        verbose_name_plural = "키워드 목록"


class QuestionsAnswer(TimeStampModel):
    answer = models.CharField(null=False, blank=False, max_length=10)
    score = models.IntegerField(null=False, blank=False, default=0)

    def __str__(self) -> str:
        return f"답: {self.answer}"

    class Meta:
        db_table = "questions_answer"
        verbose_name = "답변 정보"
        verbose_name_plural = "답변 목록"


class Question(TimeStampModel):
    answer = models.ForeignKey(QuestionsAnswer, on_delete=models.CASCADE)
    content = models.TextField(null=False, blank=False)

    def __str__(self) -> str:
        return f"질문: {self.content}"

    class Meta:
        db_table = "question"
        verbose_name = "질문"
        verbose_name_plural = "질문 목록"
        indexes = [models.Index(fields=["answer"], name="IDX_questions_answer_id")]


class QuestionsResults(TimeStampModel):
    TYPE_CHOICES = [
        ("Q", "Question"),
        ("K", "Keyword"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scent = models.ForeignKey(Scent, on_delete=models.CASCADE)
    division = models.CharField(null=False, blank=False, max_length=2, choices=TYPE_CHOICES)
    questions_json = models.JSONField(null=False, blank=False)
    answer_ai = models.CharField(null=False, blank=False, max_length=20)
    image_key = models.CharField(null=True, blank=True, max_length=30)
    results_review = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f"결과는{self.scent.name} 향이고 이유는 {self.answer_ai}"

    class Meta:
        db_table = "questions_results"
        verbose_name = "질문 결과"
        verbose_name_plural = "결과 목록"
        indexes = [
            (models.Index(fields=["user"], name="IDX_questions_results_user_id")),
            (models.Index(fields=["scent"], name="IDX_questions_results_scent_id")),
        ]
