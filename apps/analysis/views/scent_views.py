from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission, IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analysis.models import Scent
from apps.analysis.serializers.analysis_serializers import (
    ScentDetailSerializer,
    ScentListSerializer,
)
from apps.analysis.serializers.scent_serializers import ScentCreateUpdateSerializer
from apps.analysis.service.scent_service import (
    create_scent,
    delete_scent,
    get_scent_detail,
    get_scent_list,
    update_scent,
)


class ScentListCreateAPIView(APIView):
    def get_permissions(self) -> list[BasePermission]:
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @extend_schema(
        tags=["scent_management"],
        summary="향 데이터 목록 조회",
        description="전체 향 데이터의 목록을 반환",
        responses={200: ScentListSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        scents = get_scent_list()
        serializer = ScentListSerializer(scents, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["scent_management"],
        summary="새로운 향 데이터 등록",
        description="관리자 권한으로 새로운 향 데이터를 생성",
        request=ScentCreateUpdateSerializer,
        responses={
            201: ScentDetailSerializer,
            400: OpenApiResponse(description="잘못된 입력값"),
            403: OpenApiResponse(description="권한 없음"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = ScentCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        scent = create_scent(serializer.validated_data)
        return Response(
            {"status": "success", "data": ScentDetailSerializer(scent).data},
            status=status.HTTP_201_CREATED,
        )


class ScentDetailAPIView(APIView):
    def get_permissions(self) -> list[BasePermission]:
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_object(self, id: int) -> Scent:
        try:
            return get_scent_detail(id)
        except Exception:
            raise NotFound()

    @extend_schema(
        tags=["scent_management"],
        summary="향 데이터 상세 조회",
        description="특정 ID를 가진 향의 모든 상세 정보를 조회",
        responses={
            200: ScentDetailSerializer,
            404: OpenApiResponse(description="존재하지 않는 데이터"),
        },
    )
    def get(self, request: Request, id: int) -> Response:
        scent = self.get_object(id)
        serializer = ScentDetailSerializer(scent)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["scent_management"],
        summary="향 데이터 수정",
        description="기존 향 데이터의 특정 필드를 수정",
        request=ScentCreateUpdateSerializer,
        responses={
            200: ScentDetailSerializer,
            400: OpenApiResponse(description="잘못된 입력값"),
            404: OpenApiResponse(description="존재하지 않는 데이터"),
        },
    )
    def patch(self, request: Request, id: int) -> Response:
        scent = self.get_object(id)
        serializer = ScentCreateUpdateSerializer(scent, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        scent = update_scent(scent, serializer.validated_data)
        return Response(
            {"status": "success", "data": ScentDetailSerializer(scent).data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["scent_management"],
        summary="향 데이터 삭제",
        description="특정 향 데이터를 영구적으로 삭제",
        responses={
            204: OpenApiResponse(description="삭제 성공"),
            404: OpenApiResponse(description="존재하지 않는 데이터"),
        },
    )
    def delete(self, request: Request, id: int) -> Response:
        scent = self.get_object(id)
        delete_scent(scent)
        return Response({"status": "success"}, status=status.HTTP_204_NO_CONTENT)
