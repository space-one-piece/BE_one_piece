from typing import Any

from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.chatbot.models import ChatbotRecommendation
from apps.core.utils.cloud_front import image_url_cloud


@admin.register(ChatbotRecommendation)
class ChatbotRecommendationAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    readonly_fields = ["image_preview"]
    list_display = (
        "get_user",
        "session",
        "get_scent",
        "retry_count",
        "is_saved",
        "saved_at",
        "rating",
        "review",
        "reply",
        "image_preview",
    )
    search_fields = ("scent__name", "user__name")
    list_display_links = (
        "get_user",
        "session",
        "get_scent",
        "retry_count",
        "is_saved",
        "saved_at",
        "rating",
        "review",
        "reply",
    )
    list_filter = ("scent__name", "user__name")

    @admin.display(ordering="scent", description="scent")
    def get_scent(self, obj: ChatbotRecommendation) -> str:
        return f"({obj.scent.name})"

    @admin.display(ordering="user", description="user")
    def get_user(self, obj: ChatbotRecommendation) -> str:
        return f"{obj.user.name}"

    def image_preview(self, obj: Any) -> str:
        if obj.scent.thumbnail_url:
            return mark_safe(f'<img src="{image_url_cloud(obj.scent.thumbnail_url)}" width="200" />')
        return "이미지 없음"
