from typing import Any

from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.analysis.models import ImageAnalysis
from apps.core.utils.cloud_front import image_url_cloud
from apps.core.utils.s3_handler import S3Handler


@admin.register(ImageAnalysis)
class ImageAnalysisAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    readonly_fields = ["image_preview", "get_image_resource"]
    list_display = (
        "id",
        "get_recommended_scent",
        "get_user",
        "get_image_resource",
        "ai_tags",
        "ai_intensity",
        "ai_keywords",
        "ai_comment",
        "match_score",
        "review",
        "rating",
        "image_preview",
        "is_helpful",
        "is_fallback",
        "created_at",
    )
    search_fields = ("recommended_scent__name", "user__name")
    list_display_links = (
        "id",
        "get_recommended_scent",
        "get_user",
        "get_image_resource",
        "ai_tags",
        "ai_intensity",
        "ai_keywords",
        "ai_comment",
        "match_score",
        "review",
        "rating",
        "is_helpful",
        "is_fallback",
        "created_at",
    )
    list_filter = ("recommended_scent__name", "user__name")

    def image_preview(self, obj: Any) -> str:
        if obj.recommended_scent.thumbnail_url:
            return mark_safe(f'<img src="{image_url_cloud(obj.recommended_scent.thumbnail_url)}" width="200" />')
        return "이미지 없음"

    @admin.display(ordering="recommended_scent", description="recommended scent")
    def get_recommended_scent(self, obj: ImageAnalysis) -> str:
        if obj.recommended_scent:
            return f"({obj.recommended_scent.id}){obj.recommended_scent.name}"
        return ""

    @admin.display(ordering="user", description="user")
    def get_user(self, obj: ImageAnalysis) -> str:
        return f"({obj.user.id}){obj.user.name}"

    @admin.display(ordering="image_resource", description="image resource")
    def get_image_resource(self, obj: ImageAnalysis) -> str:
        s3handler = S3Handler()
        if obj.image_resource:
            return mark_safe(f'<img src="{s3handler.s3_image(obj.image_resource.img_key)}" width="200" />')
        return "이미지 없음"
