from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.error_response_serializers import ErrorResponseSerializer
from apps.users.serializers.find_email_serializers import FindEmailSerializer
from apps.users.services.find_email_services import FindEmailService


class FindEmailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="이메일 찾기",
        description="이름과 휴대폰인증 후 받은 sms_token을 입력하여 일부 가려진 상태의 이메일을 확인합니다.",
        request=FindEmailSerializer,
        responses={
            200: OpenApiResponse(
                description="이메일을 찾았습니다.",
                response={
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "example": "u**r@e***le.com"},
                    },
                },
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="필수값 누락 또는 인증 실패 (예: '인증정보가 만료되었거나 올바르지 않습니다.')",
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer, description="사용자 없음 (예 '일치하는 사용자 정보가 없습니다.')"
            ),
        },
        tags=["accounts"],
    )
    def post(self, request: Request) -> Response:
        serializer = FindEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        masked_email = FindEmailService.find_email(
            name=serializer.validated_data["name"],
            phone_number=serializer.validated_data["phone_number"],
            sms_token=serializer.validated_data["sms_token"],
        )

        return Response({"email": masked_email}, status=status.HTTP_200_OK)
