from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample

from apps.users.services.signup_services import SignUpService, DuplicateUserError


class SignUpView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="회원가입",
        description="사용자 정보를 입력받아 계정을 생성하고 가입 정보를 반환하는 API",
        tags=["Account"],
        examples=[
            OpenApiExample(
                name="회원가입 성공 예시",
                value={
                    "detail": "회원가입이 완료되었습니다.",
                }
            )
        ]
    )

    def post(self, request: Request) -> Response:
        serializer = SignUpService(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            SignUpService().create_user(serializer.validated_data)
        except DuplicateUserError:
            return Response(
                {"error_detail": "이미 중복된 회원가입 내역이 존재합니다."}, status=status.HTTP_409_CONFLICT
            )
        return Response({"detail": "회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)