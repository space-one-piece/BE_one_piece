from django.contrib import admin

from apps.chatbot.models import ChatbotRecommendation


@admin.register(ChatbotRecommendation)
class ChatbotRecommendationAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
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
