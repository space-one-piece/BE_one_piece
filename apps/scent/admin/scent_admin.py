from typing import Any

from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.analysis.models import Scent
from apps.core.utils.cloud_front import image_url_cloud


@admin.register(Scent)
class ScentAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    readonly_fields = ["image_preview"]
    list_display = (
        "id",
        "name",
        "eng_name",
        "description",
        "categories",
        "tags",
        "keywords",
        "intensity",
        "is_bestseller",
        "season",
        "similar_scents",
        "image_preview",
        "created_at",
    )
    search_fields = ("name", "eng_name", "tags")
    list_display_links = (
        "id",
        "name",
        "eng_name",
        "description",
        "categories",
        "tags",
        "keywords",
        "intensity",
        "is_bestseller",
        "season",
        "similar_scents",
        "created_at",
    )
    list_filter = ("name", "tags")

    def image_preview(self, obj: Any) -> str:
        # obj.thumbnail_url 등 이미지 경로가 담긴 필드를 넣으세요
        if obj.thumbnail_url:
            return mark_safe(f'<img src="{image_url_cloud(obj.thumbnail_url)}" width="200" />')
        return "이미지 없음"
