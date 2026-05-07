from typing import Any

from django import forms
from django.contrib import admin

from apps.question.models import Keyword, Question, QuestionsAnswer, QuestionsResults


class KeywordAdminForm(forms.ModelForm):  # type: ignore[type-arg]
    freshness = forms.IntegerField(label="Freshness (신선도)", min_value=0, max_value=100, required=False)
    warmth = forms.IntegerField(label="Warmth (따뜻함)", min_value=0, max_value=100, required=False)
    softness = forms.IntegerField(label="Softness (부드러움)", min_value=0, max_value=100, required=False)
    depth = forms.IntegerField(label="Depth (깊이감)", min_value=0, max_value=100, required=False)
    sweetness = forms.IntegerField(label="Sweetness (달콤함)", min_value=0, max_value=100, required=False)

    class Meta:
        model = Keyword
        fields = "__all__"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.score:
            score = self.instance.score
            self.fields["freshness"].initial = score.get("freshness")
            self.fields["warmth"].initial = score.get("warmth")
            self.fields["softness"].initial = score.get("softness")
            self.fields["depth"].initial = score.get("depth")
            self.fields["sweetness"].initial = score.get("sweetness")

    def save(self, commit: bool = True) -> Any:
        instance = super().save(commit=False)
        instance.score = {
            "freshness": self.cleaned_data.get("freshness"),
            "warmth": self.cleaned_data.get("warmth"),
            "softness": self.cleaned_data.get("softness"),
            "depth": self.cleaned_data.get("depth"),
            "sweetness": self.cleaned_data.get("sweetness"),
        }
        if commit:
            instance.save()
        return instance


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
    form = KeywordAdminForm
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
