from typing import cast

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models.models import User
from apps.users.serializers.Error_Response_Serializers import ErrorResponseSerializer
from apps.users.serializers.user_profile_serailzers import UserProfileSerializer
from apps.users.serializers.user_update_serializeres import UserProfileUpdateSerializer
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
        serializer = UserProfileSerializer(request.user)
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
