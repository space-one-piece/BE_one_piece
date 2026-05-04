from __future__ import annotations

from django.contrib import admin

from apps.users.models.models import SocialUser


@admin.register(SocialUser)
class SocialUserAdmin(admin.ModelAdmin):  # type: ignore
    list_display = ("id", "user_display", "provider", "social_id", "created_at")
    list_filter = ("provider",)
    search_fields = ("user__email", "user__name", "social_id")
    readonly_fields = ("user", "provider", "social_id", "created_at")

    @admin.display(description="연결된 유저")
    def user_display(self, obj: SocialUser) -> str:
        return f"{obj.user.name} ({obj.user.email})"
