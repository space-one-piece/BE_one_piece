from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analysis.serializers.analysis_serializers import (
    ScentDetailSerializer,
    ScentListSerializer,
)
from apps.analysis.serializers.scent_serializers import ScentCreateUpdateSerializer


class ScentListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["scent_management"],
        summary="향 데이터 목록 조회",
        description="전체 향 데이터의 목록을 반환합니다. (페이지네이션 적용 가능)",
        responses={200: ScentListSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        return Response(...)

    @extend_schema(
        tags=["scent_management"],
        summary="새로운 향 데이터 등록",
        description="관리자 권한으로 새로운 향 데이터를 생성합니다.",
        request=ScentCreateUpdateSerializer,
        responses={
            201: ScentDetailSerializer,
            400: OpenApiResponse(description="잘못된 입력값"),
            403: OpenApiResponse(description="권한 없음"),
        },
    )
    def post(self, request: Request) -> Response:
        return Response(..., status=status.HTTP_201_CREATED)


class ScentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["scent_management"],
        summary="향 데이터 상세 조회",
        description="특정 ID를 가진 향의 모든 상세 정보를 조회합니다.",
        responses={
            200: ScentDetailSerializer,
            404: OpenApiResponse(description="존재하지 않는 데이터"),
        },
    )
    def get(self, request: Request, id: int) -> Response:
        return Response(...)

    @extend_schema(
        tags=["scent_management"],
        summary="향 데이터 수정",
        description="기존 향 데이터의 특정 필드를 수정합니다. (Partial Update)",
        request=ScentCreateUpdateSerializer,
        responses={
            200: ScentDetailSerializer,
            400: OpenApiResponse(description="잘못된 입력값"),
            404: OpenApiResponse(description="존재하지 않는 데이터"),
        },
    )
    def patch(self, request: Request, id: int) -> Response:
        return Response(...)

    @extend_schema(
        tags=["scent_management"],
        summary="향 데이터 삭제",
        description="특정 향 데이터를 영구적으로 삭제합니다.",
        responses={
            204: OpenApiResponse(description="삭제 성공"),
            404: OpenApiResponse(description="존재하지 않는 데이터"),
        },
    )
    def delete(self, request: Request, id: int) -> Response:
        return Response(status=status.HTTP_204_NO_CONTENT)
