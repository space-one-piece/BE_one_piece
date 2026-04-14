from typing import Any

from rest_framework import serializers

from ..models import ImageAnalysis, ImageColorAnalysis, Scent


# 입력
# 이미지 업로드(프리사인URL 요청)
class UploadURLSerializer(serializers.Serializer[Any]):
    file_name = serializers.CharField(required=True, help_text="올릴 파일 이름 (예: image.jpg)")
    file_type = serializers.CharField(required=True, help_text="파일 확장자 타입 (예: image/jpeg)")


# 입력
# 이미지 분석
class AnalysisCreateSerializer(serializers.Serializer[Any]):
    image_key = serializers.CharField(required=True, help_text="URL요청을 통해 S3에 최종 업로드된 파일 경로")


# 출력
# 향 데이터(목록)
class ScentListSerializer(serializers.ModelSerializer["Scent"]):
    class Meta:
        model = Scent
        fields = [
            "id",
            "name",
            "eng_name",
            "thumbnail_url",
        ]
        read_only_fields = fields


# 출력
# 향 데이터(상세)
class ScentDetailSerializer(serializers.ModelSerializer["Scent"]):
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


# 출력
# 색상 분석 결과
class ImageColorAnalysisSerializer(serializers.ModelSerializer["ImageColorAnalysis"]):
    class Meta:
        model = ImageColorAnalysis
        fields = [
            "id",
            "analysis",  # 분석 ID
            "dominant_color_hex",  # 주요 색상 배열(JSON)
            "contrast_ratio",  # 대비 비율
            "avg_brightness",  # 평균 밝기
            "avg_saturation",  # 평균 채도
            "is_failed",  # 분석 실패 여부
            "error_log",  # 에러 로그
        ]
        read_only_fields = fields


# 출력
# 분석 히스토리 목록 조회용
class AnalysisListSerializer(serializers.ModelSerializer["ImageAnalysis"]):
    recommended_scent = ScentListSerializer(read_only=True)

    class Meta:
        model = ImageAnalysis
        fields = [
            "id",
            "recommended_scent",
            "created_at",
        ]


# 출력
# 분석 히스토리 상세 조회용
class AnalysisDetailSerializer(serializers.ModelSerializer["ImageAnalysis"]):
    recommended_scent = ScentDetailSerializer(read_only=True)
    image_metadata = ImageColorAnalysisSerializer(source="imagecoloranalysis_set", many=True, read_only=True)

    class Meta:
        model = ImageAnalysis
        fields = [
            "id",
            "recommended_scent",
            "image_metadata",
            "created_at",
        ]
        read_only_fields = fields
