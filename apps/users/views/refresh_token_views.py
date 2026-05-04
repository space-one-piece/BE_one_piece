from typing import Any, Literal, cast

from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.error_response_serializers import ErrorResponseSerializer
from apps.users.serializers.RefreshToken_serializers import RefreshTokenSerializer
from apps.users.services.RefreshToken_services import refresh_token_service


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="JWT토큰 재발급",
        description="Refresh토큰을 이용해 새로운 Access 토큰과 Refresh토큰을 발급 받습니다.",
        request=RefreshTokenSerializer,
        responses={
            200: OpenApiResponse(
                description="토큰 재발급 성공",
                response={
                    "type": "object",
                    "properties": {
                        "access": {"type": "string", "example": "eyJhbGciOiJIUzI1NiIsInR5cCI..."},
                    },
                },
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer, description="인증 실패(리프레시 토큰 누락 또는 만료)"
            ),
        },
        tags=["accounts"],
    )
    def post(self, request: Request) -> Response:
        jwt_settings = cast(dict[str, Any], settings.SIMPLE_JWT)
        cookie_name = cast(str, jwt_settings.get("AUTH_COOKIE", "refresh_token"))

        refresh_token = request.COOKIES.get(cookie_name)

        if not refresh_token:
            return Response(
                {"detail": "리프레시 토큰이 쿠키에 없습니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            res_data = refresh_token_service(refresh_token)
        except Exception:
            return Response(
                {"detail": "유효하지 않거나 만료된 리프레시 토큰입니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = res_data.get("access_token")
        new_refresh_token = res_data.get("refresh")

        if not access_token or not new_refresh_token:
            return Response(
                {"detail": "토큰 갱신 중 문제가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response = Response(
            {
                "access": res_data.get("access_token"),
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key=cookie_name,
            value=cast(str, res_data.get("refresh")),
            httponly=cast(bool, settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"]),
            samesite=cast(Literal["Lax", "Strict", "None"], jwt_settings.get("AUTH_COOKIE_SAMESITE", "Lax")),
            secure=cast(bool, jwt_settings.get("AUTH_COOKIE_SECURE", False)),
            path=cast(str, jwt_settings.get("AUTH_COOKIE_PATH", "/")),
        )

        return response
