from __future__ import annotations

from django.contrib import admin

from apps.users.models.models import UserWithdrawal


@admin.register(UserWithdrawal)
class UserWithdrawalAdmin(admin.ModelAdmin):  # type: ignore
    list_display = ("user", "reason", "scheduled_delete_at", "created_at")
    list_filter = ("reason", "scheduled_delete_at")
    search_fields = ("user__email", "user__name")

    ordering = ("scheduled_delete_at",)

    readonly_fields = ("user", "reason", "other_reason", "scheduled_delete_at", "created_at")
