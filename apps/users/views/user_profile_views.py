from typing import Any, cast

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.serializers.presigned_url_serializer import PresignedUrlRequestSerializer
from apps.core.views.presigned_url import BasePresignedUrlView
from apps.users.models.models import User
from apps.users.serializers.Error_Response_Serializers import ErrorResponseSerializer
from apps.users.serializers.user_profile_serailzers import UserProfileSerializer
from apps.users.serializers.user_update_serializeres import ProfileImageUpdateSerializer, UserProfileUpdateSerializer
from apps.users.services.user_profile_update_services import UserProfileUpdateService


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="내 정보 조회",
        description="로그인한 사용자의 프로필 정보를 가져옵니다.",
        responses={
            200: UserProfileSerializer,
            401: ErrorResponseSerializer,
        },
        tags=["accounts"],
    )
    def get(self, request: Request) -> Response:
        user_data = UserProfileUpdateService.get_user_profile(user_id=request.user.id)
        serializer = UserProfileSerializer(user_data)
        return Response(serializer.data)

    @extend_schema(
        summary="내 정보 수정",
        description="로그인한 사용자의 프로필 정보를 수정합니다.",
        request=UserProfileUpdateSerializer,
        responses={
            200: UserProfileUpdateSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=["accounts"],
    )
    def patch(self, request: Request) -> Response:
        serializer = UserProfileUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        current_user = cast(User, request.user)

        updated_user = UserProfileUpdateService.update_user_profile(user=current_user, data=serializer.validated_data)
        return Response(UserProfileUpdateSerializer(updated_user).data)


class ProfileImageView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="프로필 이미지 등록",
        description="S3에 업로드된 이미지 URL을 전달받아 사용자 프로필 이미지로 등록합니다.",
        request=ProfileImageUpdateSerializer,
        responses={200: None, 400: ErrorResponseSerializer, 401: ErrorResponseSerializer},
        tags=["accounts"],
    )
    def patch(self, request: Request) -> Response:
        serializer = ProfileImageUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        current_user = cast(User, request.user)
        UserProfileUpdateService.update_user_profile(user=current_user, data=serializer.validated_data)

        return Response({"detail": "프로필 사진이 등록되었습니다."}, status=status.HTTP_200_OK)


class ProfileImagePresignedUrlView(BasePresignedUrlView):
    folder = "profiles"

    @extend_schema(
        summary="프로필 이미지 업로드용 Presigned URL 발급",
        description=(
            "S3에 이미지를 직접 업로드하기 위한 Presigned URL을 발급합니다."
            "클라이언트는 반환된 Presigned_url로 PUT요청하여 이미지를 업로드하고,"
            "완료 후 img_url을 프로필 이미지 등록 API에 전달해야 합니다."
        ),
        request=PresignedUrlRequestSerializer,
        responses={
            200: None,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=["accounts"],
    )
    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().put(request, *args, **kwargs)
