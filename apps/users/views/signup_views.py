from typing import Any

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.user_signup_serializers import SignUpSerializer
from apps.users.services.signup_services import DuplicateUserError, SignUpService


class SignUpView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="일반 회원가입",
        description="이메일 토큰을 검증한 후 회원가입을 처리합니다.",
        request=SignUpSerializer,
        responses={
            201: OpenApiResponse(
                description="회원가입 성공",
                response=SignUpSerializer,
            ),
            400: OpenApiResponse(description="Bad Request (검증 실패)"),
            409: OpenApiResponse(description="Conflict (중복 가입)"),
        },
        tags=["accounts"],
    )
    def post(self, request: Request) -> Response:
        serializer = SignUpSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        service = SignUpService()
        try:
            validated_data: dict[str, Any] = serializer.validated_data
            service.create_user(validated_data)

            return Response({"message": "회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"error_detail": e.detail}, status=status.HTTP_400_BAD_REQUEST)

        except DuplicateUserError as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_409_CONFLICT)
