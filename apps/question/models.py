from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.analysis.models import Scent
from apps.core.models import TimeStampModel
from apps.users.models.models import User


class Keyword(TimeStampModel):
    TYPE_CHOICES_KEYWORD = [
        ("MO", "MOOD"),
        ("SN", "Scent Notes"),
        ("TS", "Time & Season"),
        ("PL", "Place"),
        ("TE", "Texture"),
    ]

    division = models.CharField(null=False, blank=False, max_length=2, choices=TYPE_CHOICES_KEYWORD)
    name = models.CharField(null=False, blank=False, max_length=30)
    score = models.JSONField(
        null=False,
        blank=False,
    )

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        db_table = "keyword"
        verbose_name = "키워드"
        verbose_name_plural = "키워드 목록"


class Question(TimeStampModel):
    TYPE_CHOICES_QUESTION = [("Fs", "freshness"), ("Ss", "softness"), ("Dh", "depth"), ("Wh", "warmth")]

    content = models.TextField(null=False, blank=False)
    additional = models.TextField(null=True, blank=True)
    left_label = models.CharField(null=False, blank=False, max_length=15)
    right_label = models.CharField(null=False, blank=False, max_length=15)
    category = models.CharField(null=False, blank=False, max_length=15, choices=TYPE_CHOICES_QUESTION)

    def __str__(self) -> str:
        return f"질문: {self.content}"

    class Meta:
        db_table = "question"
        verbose_name = "질문"
        verbose_name_plural = "질문 목록"


class QuestionsAnswer(TimeStampModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    answer = models.CharField(null=False, blank=False, max_length=10)
    score = models.IntegerField(null=False, blank=False, default=0)

    def __str__(self) -> str:
        return f"답: {self.answer}"

    class Meta:
        db_table = "questions_answer"
        verbose_name = "답변 정보"
        verbose_name_plural = "답변 목록"
        indexes = [models.Index(fields=["question"], name="IDX_questions_question_id")]


class QuestionsResults(TimeStampModel):
    TYPE_CHOICES = [
        ("S", "survey"),
        ("K", "keyword"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scent = models.ForeignKey(Scent, on_delete=models.CASCADE)
    division = models.CharField(null=False, blank=False, max_length=2, choices=TYPE_CHOICES)
    questions_json = models.JSONField(null=False, blank=False)
    answer_ai = models.TextField(null=False, blank=False)
    image_key = models.CharField(null=True, blank=True, max_length=30)
    review = models.TextField(null=True, blank=True, max_length=300)
    rating = models.IntegerField(null=True, blank=True)
    match_score = models.IntegerField(null=False, blank=False, default=0)
    is_helpful = models.BooleanField(default=False)

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


class Share(TimeStampModel):
    division = models.CharField(null=False, blank=False)
    result_id = models.CharField(null=False, blank=False)
    holding_time = models.DateTimeField(null=False, blank=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    is_active = models.BooleanField(null=False, blank=False, default=True)
    image_url = models.CharField(null=False, blank=False, default="")

    class Meta:
        db_table = "share"
        verbose_name = "web_share list"
        verbose_name_plural = "web_share list"
