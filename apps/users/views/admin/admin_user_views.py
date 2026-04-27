from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.admin.admin_user_serializers import AdminUserDetailSerializer, AdminUserListSerializer
from apps.users.serializers.error_response_serializers import ErrorResponseSerializer
from apps.users.services.admin.admin_user_services import AdminUserService


class AdminUserListView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminUserListSerializer

    @extend_schema(
        summary="어드민 - 회원목록 조회",
        description="관리자 권한으로 가입된 젠체 회원 목록을 조회합니다. 검색 키워드를 통해 필터링이 가능합니다.",
        parameters=[
            OpenApiParameter(name="page", type=int, description="페이지 번호"),
            OpenApiParameter(name="page_size", type=int, description="페이지당 노출 개수"),
            OpenApiParameter(name="search", type=str, description="검색어"),
            OpenApiParameter(
                name="status", type=str, description="회원 상태 필터", enum=["activated", "deactivated", "withdrew"]
            ),
        ],
        responses={200: AdminUserListSerializer},
        tags=["admin"],
    )
    def get(self, request: Request) -> Response:
        search = request.query_params.get("search")
        status = request.query_params.get("status")

        users_queryset = AdminUserService.get_user_list_admin(search_keyword=search, status=status)

        paginator = PageNumberPagination()
        page_size = request.query_params.get("size")
        if page_size:
            paginator.page_size = int(page_size)

        page = paginator.paginate_queryset(users_queryset, request)

        if page is not None:
            serializer = AdminUserListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = AdminUserListSerializer(users_queryset, many=True)
        return Response(serializer.data)


class AdminUserDetailView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminUserDetailSerializer

    @extend_schema(
        summary="어드민 - 회원 상세 조회",
        description="관리자 권한으로 특정 회원의 상세 정보를 조횝합니다.",
        responses={
            200: AdminUserDetailSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=["admin"],
    )
    def get(self, request: Request, account_id: int) -> Response:
        user = AdminUserService.get_user_detail_admin(account_id=account_id)
        serializer = AdminUserDetailSerializer(user)
        return Response(serializer.data)
