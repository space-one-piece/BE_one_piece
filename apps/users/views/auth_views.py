from datetime import timedelta
from typing import Any, Literal, cast

from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models.models import User
from apps.users.serializers.auth_serializers import (
    AccountRecoverySerializer,
    LoginResponseSerializer,
    LoginSerializer,
    LogoutSerializer,
    UserWithdrawalSerializer,
)
from apps.users.serializers.error_response_serializers import ErrorResponseSerializer
from apps.users.services.auth_services import LoginService, LogoutService, RecoveryService, WithdrawalService


# 로그인
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
                jwt_settings = cast(dict[str, Any], settings.SIMPLE_JWT)
                response.set_cookie(
                    key=cast(str, jwt_settings.get("AUTH_COOKIE", "refresh_token")),
                    value=refresh_token,
                    httponly=cast(bool, jwt_settings.get("AUTH_COOKIE_HTTP_ONLY", True)),
                    secure=cast(bool, jwt_settings.get("AUTH_COOKIE_SECURE", False)),
                    samesite=cast(Literal["Lax", "Strict", "None"], jwt_settings.get("AUTH_COOKIE_SAMESITE", "Lax")),
                    path=cast(str, jwt_settings.get("AUTH_COOKIE_PATH", "/")),
                    max_age=int(cast(timedelta, jwt_settings.get("REFRESH_TOKEN_LIFETIME")).total_seconds()),
                )
                return response
            return Response({"detail": "토큰 발급에 실패했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 로그아웃
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


# 계정 탈퇴
class UserWithdrawalView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserWithdrawalSerializer

    @extend_schema(
        summary="회원탈퇴",
        description=(
            "사용자 계정을 비활성화 하고 탈퇴 정보를 기록합니다. \n\n"
            "비밀번호 확인과 탈퇴 동의가 필수이며, 14일 이내에 계정복구가 가능합니다."
        ),
        request=UserWithdrawalSerializer,
        responses={
            204: None,
            400: OpenApiResponse(
                response=ErrorResponseSerializer, description="비밀번호 불일치, 이미 탈퇴한 계정 또는 확인 미동의"
            ),
            401: OpenApiResponse(response=ErrorResponseSerializer, description="인증 실패 (로그인필요)"),
        },
        tags=["accounts"],
    )
    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not serializer.validated_data.get("confirm"):
            return Response({"detail": "탈퇴 확인이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        current_user = cast(User, request.user)

        WithdrawalService.deactivate_user(
            user=current_user,
            password=serializer.validated_data["password"],
            reason=serializer.validated_data["reason"],
            other_reason=serializer.validated_data.get("other_reason", ""),
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


# 계정 복구
class AccountRecoveryView(APIView):
    permission_classes = [AllowAny]
    serializer_class = AccountRecoverySerializer

    @extend_schema(
        summary="계정 복구",
        description="이메일 인증 후 발급받은 UUID 토큰과 기존 비밀번호를 입력하여 계정을 복구합니다.",
        request=AccountRecoverySerializer,
        responses={
            200: OpenApiResponse(description="복구 성공"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="인증 실패 또는 기간만료"),
        },
        tags=["accounts"],
    )
    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        RecoveryService.recover_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            recovery_token=serializer.validated_data["recovery_token"],
        )

        return Response(
            {"detail": "계정이 성공적으로 복구되었습니다. 기존 비밀번호로 로그인이 가능합니다."},
            status=status.HTTP_200_OK,
        )
