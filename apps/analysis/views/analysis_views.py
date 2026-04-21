from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analysis.serializers.analysis_serializers import (
    AnalysisCreateSerializer,
    AnalysisDetailSerializer,
    AnalysisListSerializer,
)
from apps.analysis.service.analysis_service import AnalysisService
from apps.core.paginations import StandardCustomPagination
from apps.core.serializers.presigned_url_serializer import PresignedUrlRequestSerializer
from apps.core.services.presigned_url_service import PresignedUrlService


# 이미지 프리사인 URL 요청
class UploadURLAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["image_analysis"],
        summary="S3 프리사인 URL 발급 요청",
        description="프론트엔드에서 S3에 직접 이미지를 업로드하기 위한 프리사인 URL을 발급합니다.",
        request=PresignedUrlRequestSerializer,
        responses={
            200: OpenApiResponse(description="발급 성공"),
            400: OpenApiResponse(description="잘못된 파일 형식/이름"),
            401: OpenApiResponse(description="로그인 에러"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = PresignedUrlRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = PresignedUrlService.create(folder="analysis", file_name=serializer.validated_data["file_name"])

        return Response(result)


# 이미지 분석 / 리스트
class AnalysisListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["image_analysis"],
        summary="내 분석 히스토리 목록 조회",
        responses={
            200: AnalysisListSerializer(many=True),
            403: OpenApiResponse(description="권한 없음"),
        },
    )
    def get(self, request: Request) -> Response:
        queryset = AnalysisService.get_analysis_list(user_id=request.user.id)

        paginator = StandardCustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)

        serializer = AnalysisListSerializer(paginated_queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=["image_analysis"],
        summary="이미지 분석 시작",
        description="S3에 업로드된 이미지 키를 전달받아 분석",
        request=AnalysisCreateSerializer,
        responses={
            201: AnalysisDetailSerializer,
            400: OpenApiResponse(description="필수값 누락"),
            404: OpenApiResponse(description="필수값 이상"),
            429: OpenApiResponse(description="호출횟수 초과"),
            503: OpenApiResponse(description="서버이상"),
        },
    )
    def post(self, request: Request) -> Response:
        input_serializer = AnalysisCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        image_key = input_serializer.validated_data["image_key"]
        try:
            analysis_record, _ = AnalysisService.image_analysis_process(user=request.user, img_key=image_key)  # type: ignore
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        output_serializer = AnalysisDetailSerializer(analysis_record)

        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


# 이미지 분석 상세 조회
class AnalysisDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["image_analysis"],
        summary="특정 분석 결과 상세 조회",
        responses={
            200: AnalysisDetailSerializer,
            404: OpenApiResponse(description="존재하지 않는 분석 데이터"),
        },
    )
    def get(self, request: Request, id: int) -> Response:
        # Todo:본인 소유 권한 제어
        return Response(...)

    @extend_schema(
        tags=["image_analysis"],
        summary="특정 분석 결과 삭제",
        responses={
            204: OpenApiResponse(description="삭제 성공 (본문 없음)"),
            404: OpenApiResponse(description="존재하지 않는 분석 데이터"),
            500: OpenApiResponse(description="서버통신 오류"),
        },
    )
    def delete(self, request: Request, id: int) -> Response:
        # Todo:본인 소유 권한 제어
        return Response(...)


# 이미지 분석 결과 저장
class AnalysisFeedbackAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["image_analysis"],
        summary="분석 결과 저장",
        request=inline_serializer(
            name="FeedbackInput",
            fields={"is_helpful": serializers.BooleanField(help_text="도움이 되었는지 여부 (true/false)")},
        ),
        responses={
            200: OpenApiResponse(description="분석 저장 성공"),
            400: OpenApiResponse(description="필수값 이상"),
            404: OpenApiResponse(description="분석이 존재하지 않음"),
        },
    )
    def patch(self, request: Request, id: int) -> Response:
        return Response(...)


# 유저 분석 통계 반환
class AnalysisStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["image_analysis"],
        summary="유저의 전반적인 분석 통계 조회",
        responses={
            200: OpenApiResponse(description="통계 데이터 반환 성공"),
        },
    )
    def get(self, request: Request) -> Response:
        return Response(...)
