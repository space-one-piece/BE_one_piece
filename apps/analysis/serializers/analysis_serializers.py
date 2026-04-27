from typing import Any

from rest_framework import serializers

from apps.core.utils.cloud_front import image_url_cloud

from ...core.utils.s3_handler import S3Handler
from ..models import ImageAnalysis, ImageColorAnalysis, Scent

allowed_mine_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]


# 입력
# 이미지 업로드(프리사인URL 요청)
class UploadURLSerializer(serializers.Serializer[Any]):
    file_name = serializers.CharField(required=True, help_text="올릴 파일 이름 (예: image.jpg)")
    file_type = serializers.ChoiceField(
        choices=allowed_mine_types, required=True, help_text="허용 타입: image/jpeg, image/png, image/webp"
    )


# 입력
# 이미지 분석
class AnalysisCreateSerializer(serializers.Serializer[Any]):
    image_key = serializers.CharField(required=True, help_text="URL요청을 통해 S3에 최종 업로드된 파일 경로")


# 출력
# 향 데이터(목록)
class ScentListSerializer(serializers.ModelSerializer["Scent"]):
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Scent
        fields = [
            "id",
            "name",
            "categories",
            "tags",
            "description",
            "eng_name",
            "intensity",
            "season",
            "thumbnail_url",
        ]
        read_only_fields = fields

    def get_thumbnail_url(self, obj: Scent) -> str | None:
        if isinstance(obj, dict):
            url = obj.get("thumbnail_url")
        else:
            url = obj.thumbnail_url

        if not url:
            return None
        return image_url_cloud(url)


# 출력
# 향 데이터(상세)
class ScentDetailSerializer(serializers.ModelSerializer["Scent"]):
    similar_scents = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    recommended_places = serializers.SerializerMethodField()

    class Meta:
        model = Scent
        fields = [
            "id",
            "name",
            "eng_name",
            "description",
            "categories",
            "tags",
            "keywords",
            "intensity",
            "is_bestseller",
            "scent_notes",
            "profile",
            "season",
            "recommended_places",
            "similar_scents",
            "thumbnail_url",
            "created_at",
        ]
        read_only_fields = fields

    def get_similar_scents(self, obj: Scent) -> list[Any] | dict[str, Any]:
        if not obj.similar_scents:
            return []

        scents = Scent.objects.filter(id__in=obj.similar_scents)

        return ScentListSerializer(scents, many=True, context=self.context).data

    def get_thumbnail_url(self, obj: Scent) -> str | None:
        if not obj.thumbnail_url:
            return None
        return image_url_cloud(obj.thumbnail_url)

    def get_recommended_places(self, obj: Scent) -> list[dict[str, Any]]:
        places = obj.recommended_places
        if not places:
            return []

        result = []
        for place in places:
            place_copy = dict(place)
            if isinstance(place_copy, dict) and place_copy.get("imageUrl"):
                place_copy["imageUrl"] = image_url_cloud(place_copy["imageUrl"])
            result.append(place_copy)

        return result


# 출력
# 색상 분석 결과
class ImageColorAnalysisSerializer(serializers.ModelSerializer["ImageColorAnalysis"]):
    class Meta:
        model = ImageColorAnalysis
        fields = [
            "id",
            "dominant_color_hex",
            "contrast_ratio",
            "avg_brightness",
            "avg_saturation",
            "is_failed",
            "error_log",
        ]
        read_only_fields = fields


# 출력
# 분석 히스토리 목록 조회용
class AnalysisListSerializer(serializers.ModelSerializer["ImageAnalysis"]):
    recommended_scent = ScentListSerializer(read_only=True)
    type = serializers.CharField(default="image", read_only=True)

    class Meta:
        model = ImageAnalysis
        fields = [
            "id",
            "type",
            "recommended_scent",
            # "review",
            # "rating",
            "created_at",
        ]
        read_only_fields = fields


class ScentAnalysisDataSerializer(serializers.ModelSerializer["ImageAnalysis"]):
    class Meta:
        model = ImageAnalysis
        fields = [
            "ai_tags",
            "ai_keywords",
            "ai_intensity",
            "ai_comment",
            "match_score",
            "is_fallback",
        ]
        read_only_fields = fields


# 출력
# 분석 히스토리 상세 조회용
class AnalysisDetailSerializer(serializers.ModelSerializer["ImageAnalysis"]):
    recommended_scent = ScentDetailSerializer(read_only=True)
    image_metadata = ImageColorAnalysisSerializer(read_only=True)

    presigned_image_url = serializers.SerializerMethodField()

    class Meta:
        model = ImageAnalysis
        fields = [
            "id",
            "presigned_image_url",
            "recommended_scent",
            "image_metadata",
            "ai_tags",
            "ai_keywords",
            "ai_intensity",
            "ai_comment",
            "match_score",
            "is_fallback",
            "created_at",
        ]
        read_only_fields = fields

    def get_presigned_image_url(self, obj: ImageAnalysis) -> str | None:
        if not obj.s3_image_url:
            return None
        return S3Handler().s3_image(obj.s3_image_url)


class IntegratedFeedbackSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    type = serializers.CharField()
    created_at = serializers.DateTimeField()
    scent = serializers.SerializerMethodField()

    def get_scent(self, obj: Any) -> dict[str, Any] | None:
        scent_obj = None

        if hasattr(obj, "recommended_scent"):
            scent_obj = obj.recommended_scent
        elif hasattr(obj, "scent"):
            scent_obj = obj.scent

        if scent_obj:
            return ScentListSerializer(scent_obj, context=self.context).data

        return None
