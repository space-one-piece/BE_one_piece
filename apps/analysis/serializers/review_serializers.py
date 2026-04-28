from typing import Any

from rest_framework import serializers

from apps.core.utils.cloud_front import image_url_cloud


class AnalysisReviewSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField(read_only=True)
    type = serializers.CharField(read_only=True)

    name = serializers.CharField(source="user.name", read_only=True)
    thumbnail_url = serializers.SerializerMethodField()

    eng_name = serializers.CharField(read_only=True)
    tags = serializers.SerializerMethodField()
    review = serializers.CharField(max_length=500)
    rating = serializers.IntegerField()
    created_at = serializers.DateTimeField(read_only=True)

    def get_thumbnail_url(self, obj: Any) -> str | None:
        scent_obj = getattr(obj, "recommended_scent", None) or getattr(obj, "scent", None)

        if scent_obj and hasattr(scent_obj, "thumbnail_url"):
            return image_url_cloud(scent_obj.thumbnail_url)
        return None

    def get_tags(self, obj: Any) -> list[Any]:
        scent_obj = getattr(obj, "recommended_scent", None) or getattr(obj, "scent", None)

        if scent_obj and hasattr(scent_obj, "tags"):
            return [str(tag) for tag in scent_obj.tags]
        return []
