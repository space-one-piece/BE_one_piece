from urllib.request import Request

from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analysis.serializers.analysis_serializers import (
    AnalysisCreateSerializer,
    AnalysisDetailSerializer,
    AnalysisListSerializer,
    UploadURLSerializer,
)


# 이미지 프리사인 URL 요청
class UploadURLAPIView(APIView):
    @extend_schema(
        tags=["image_analysis"],
        summary="S3 프리사인 URL 발급 요청",
        description="프론트엔드에서 S3에 직접 이미지를 업로드하기 위한 프리사인 URL을 발급합니다.",
        request=UploadURLSerializer,
        responses={
            200: OpenApiResponse(description="발급 성공"),
            400: OpenApiResponse(description="잘못된 파일 형식/이름"),
            401: OpenApiResponse(description="로그인 에러"),
        },
    )
    def post(self, request: Request) -> Response:
        return Response(...)


# 이미지 분석 / 리스트
class AnalysisListCreateAPIView(APIView):
    @extend_schema(
        tags=["image_analysis"],
        summary="내 분석 히스토리 목록 조회",
        responses={
            200: AnalysisListSerializer(many=True),
            400: OpenApiResponse(description="요청값이 이상"),
        },
    )
    def get(self, request: Request) -> Response:
        return Response(...)

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
        return Response(...)


# 이미지 분석 상세 조회
class AnalysisDetailAPIView(APIView):
    @extend_schema(
        tags=["image_analysis"],
        summary="특정 분석 결과 상세 조회",
        responses={
            200: AnalysisDetailSerializer,
            404: OpenApiResponse(description="존재하지 않는 분석 데이터"),
        },
    )
    def get(self, request: Request, id: int) -> Response:
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
        return Response(...)


# 이미지 분석 결과 저장
class AnalysisFeedbackAPIView(APIView):
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
    @extend_schema(
        tags=["image_analysis"],
        summary="유저의 전반적인 분석 통계 조회",
        responses={
            200: OpenApiResponse(description="통계 데이터 반환 성공"),
        },
    )
    def get(self, request: Request) -> Response:
        return Response(...)
