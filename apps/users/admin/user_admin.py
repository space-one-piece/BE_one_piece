from __future__ import annotations

from typing import Any

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from apps.users.admin.admin_user_services import AdminUserService
from apps.users.models.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):  # type: ignore
    list_display = ("id", "email", "name", "status", "social_type", "is_active", "created_at")
    search_fields = ("email", "name", "phone_number")
    list_filter = ("status", "social_type", "is_active")
    ordering = ("-id",)

    actions = ["lock_selected_users"]

    @admin.action(description="선택한 유저 잠금")
    def lock_selected_users(self, request: HttpRequest, queryset: QuerySet[Any]) -> None:
        count = queryset.count()
        for user in queryset:
            AdminUserService.lock_user_admin(user.id)

        self.message_user(request, f"{count}명의 유저가 잠금 처리되었습니다.")
