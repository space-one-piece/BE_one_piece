from django.contrib import admin

from apps.analysis.models import ImageAnalysis


@admin.register(ImageAnalysis)
class ImageAnalysisAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = (
        "id",
        "get_recommended_scent",
        "get_user",
        "get_image_resource",
        "s3_image_url",
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
    search_fields = ("recommended_scent__name", "user__name")
    list_display_links = (
        "id",
        "get_recommended_scent",
        "get_user",
        "get_image_resource",
        "s3_image_url",
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
        return f"({obj.image_resource.img_key}){obj.image_resource.original_name}"
