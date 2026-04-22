from typing import Any

from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.user_login_serializers import (
    ErrorResponseSerializer,
    LoginResponseSerializer,
    LoginSerializer,
)
from apps.users.services.login_services import LoginService


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = LoginSerializer

    @extend_schema(
        summary="로그인",
        description="이메일과 비밀번호를 이용해 로그인하고 JWT 토큰을 발급받습니다.",
        request=LoginSerializer,
        responses={
            200: LoginResponseSerializer,
            400: OpenApiResponse(response=ErrorResponseSerializer, description="필수 값 누락"),
            401: OpenApiResponse(response=ErrorResponseSerializer, description="인증 실패(이메일/비밀번호 불일치)"),
            403: OpenApiResponse(response=ErrorResponseSerializer, description="권한 없음(비활성 계정)"),
        },
        tags=["accounts"],
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Any:
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            data = LoginService.login_user(
                email=serializer.validated_data["email"], password=serializer.validated_data["password"]
            )

            access_token = data.get("access")
            refresh_token = data.get("refresh")

            response = Response({"access": access_token}, status=status.HTTP_200_OK)

            if refresh_token and isinstance(refresh_token, str):
                response.set_cookie(
                    key="refresh_token",
                    value=refresh_token,
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite="Lax",
                    max_age=7 * 24 * 60 * 60,
                )
                return response
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
