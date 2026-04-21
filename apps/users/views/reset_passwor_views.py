from typing import Any

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.Error_Response_Serializers import ErrorResponseSerializer
from apps.users.serializers.reset_password_serializers import PasswordResetSerializer
from apps.users.services.reset_password_services import passwordservice


class PasswordResetView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    @extend_schema(
        summary="비밀번호 재설정",
        description="이메일 인증 후 발급된 토큰을 사용하여 새로운 비밀번호를 변경합니다.",
        request=PasswordResetSerializer,
        responses={
            200: OpenApiResponse(
                description="비밀번호 변경 성공",
                response={
                    "type": "object",
                    "properties": {"detail": {"type": "string", "example": "비밀번호가 성공적으로 변경되었습니다."}},
                },
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer, description="필수 값 누락 또는 인증 토큰이 유효하지 않음"
            ),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="해당 이메일의 사용자를 찾을 수 없음"),
        },
        tags=["accounts"],
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        passwordservice.reset_password(
            email=serializer.validated_data["email"],
            token=serializer.validated_data["token"],
            new_password=serializer.validated_data["new_password"],
        )

        return Response({"detail": "비밀번호가 성공적으로 변경되었습니다."}, status=status.HTTP_200_OK)
