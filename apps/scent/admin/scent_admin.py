from django.contrib import admin

from apps.analysis.models import Scent


@admin.register(Scent)
class ScentAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
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
