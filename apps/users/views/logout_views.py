from typing import Any

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.user_logout_serializers import LogoutSerializer
from apps.users.services.user_logout_services import LogoutService


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    @extend_schema(
        summary="로그아웃",
        tags=["accounts"],
        description="전달받은 Refresh token을 블랙리스트에 추가하여 무효화합니다.",
        request=LogoutSerializer,  # 요청 시리얼라이저 명시
        responses={
            200: OpenApiResponse(
                description="로그아웃 성공",
                response={
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string", "example": "성공적으로 로그아웃 되었습니다."},
                    },
                },
            ),
            401: OpenApiResponse(description="인증 실패 (로그인 필요)"),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token: str = serializer.validated_data["refresh"]
        LogoutService.logout(refresh_token)

        return Response({"detail": "성공적으로 로그아웃 되었습니다."}, status=status.HTTP_200_OK)
