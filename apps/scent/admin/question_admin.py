from django.contrib import admin

from apps.question.models import Keyword, Question, QuestionsAnswer, QuestionsResults


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("id", "content", "additional", "left_label", "right_label", "category", "created_at", "updated_at")
    search_fields = ("content",)
    list_display_links = ("id", "content", "additional", "created_at", "updated_at")


@admin.register(QuestionsAnswer)
class QuestionAsterAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("id", "get_question", "answer", "score", "created_at", "updated_at")
    search_fields = (
        "answer",
        "question__content",
    )
    list_display_links = ("id", "get_question", "answer", "score", "created_at", "updated_at")

    @admin.display(ordering="question__content", description="question")
    def get_question(self, obj: QuestionsAnswer) -> str:
        return f"[{obj.question.id}] {obj.question.content}"


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("id", "division", "name")
    search_fields = ("name",)
    list_filter = ("division",)
    list_display_links = ("id", "division", "name")


@admin.register(QuestionsResults)
class QuestionsResultsAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = (
        "id",
        "get_scent",
        "division",
        "answer_ai",
        "review",
        "rating",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "scent__name",
        "division",
    )
    list_display_links = (
        "id",
        "get_scent",
        "division",
        "answer_ai",
        "review",
        "rating",
        "created_at",
        "updated_at",
    )

    @admin.display(ordering="scent__name", description="scent")
    def get_scent(self, obj: QuestionsResults) -> str:
        return obj.scent.name
