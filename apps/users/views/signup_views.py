from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.error_response_serializers import ErrorResponseSerializer
from apps.users.serializers.user_signup_serializers import SignUpSerializer
from apps.users.services.signup_services import DuplicateUserError, SignUpService


class SignUpView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="일반 회원가입",
        description="이메일 및 휴대폰 토큰을 검증한 후 회원가입을 처리합니다.",
        request=SignUpSerializer,
        responses={
            201: OpenApiResponse(
                description="회원가입 성공",
                response=SignUpSerializer,
            ),
            400: OpenApiResponse(description="Bad Request (검증 실패)", response=ErrorResponseSerializer),
            409: OpenApiResponse(description="Conflict (중복 가입)", response=ErrorResponseSerializer),
        },
        tags=["accounts"],
    )
    def post(self, request: Request) -> Response:
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = SignUpService()
        try:
            service.create_user(serializer.validated_data)
            return Response({"message": "회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)

        except DuplicateUserError as e:
            raise ValidationError(detail=str(e), code="USER_ALREADY_EXISTS")

        except ValidationError as e:
            raise e
