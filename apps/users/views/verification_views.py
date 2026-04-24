from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.verification_serializers import (
    EmailSendSerializer,
    EmailVerifySerializer,
    SmsSendSerializer,
    SmsVerifySerializer,
)
from apps.users.services.verification_services import VerificationService


# 이메일 발송
class EmailSendView(APIView):
    @extend_schema(
        summary="이메일 인증번호 발송",
        description="사용자가 입력한 이메일로 6자리 인증번호를 발송합니다.",
        request=EmailSendSerializer,
        responses={200: {"example": {"detail": "인증 이메일이 발송되었습니다."}}},
        tags=["Verification"],
    )
    def post(self, request: Request) -> Response:
        serializer = EmailSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        VerificationService.send_email_code(email)
        return Response({"detail": "인증 메일이 발송되었습니다."}, status=status.HTTP_200_OK)


# 이메일 인증번호 확인
class EmailConfirmView(APIView):
    @extend_schema(
        summary="이메일 인증번호 확인",
        description="이메일로 발송된 인증번호를 검증하고 회원가입용 토큰을 발급합니다.",
        request=EmailVerifySerializer,
        responses={
            200: {"example": {"detail": "이메일 인증에 성공했습니다."}},
            400: {"example": {"detail": "인증번호가 잘못되었거나 만료되었습니다.."}},
        },
        tags=["Verification"],
    )
    def post(self, request: Request) -> Response:
        serializer = EmailVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        is_success = VerificationService.confirm_code(email, code, "email")

        if is_success:
            return Response({"detail": "이메일 인증에 성공했습니다."}, status=status.HTTP_200_OK)
        return Response({"detail": "인증번호가 잘못되었거나 만료되었습니다."}, status=status.HTTP_400_BAD_REQUEST)


# 휴대폰 발송
class SmsSendView(APIView):
    @extend_schema(
        summary="휴대폰 인증번호 발송",
        description="사용자가 입력한 휴대폰 번호로 6자리 인증번호를 SMS로 발송합니다.",
        request=SmsSendSerializer,
        responses={200: {"example": {"detail": "인증 문자가 발송되었습니다."}}},
        tags=["Verification"],
    )
    def post(self, request: Request) -> Response:
        serializer = SmsSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        VerificationService.send_phone_code(phone_number)
        return Response({"detail": "인증 문자가 발송되었습니다."}, status=status.HTTP_200_OK)


# 휴대폰 인증번호 확인
class SmsConfirmView(APIView):
    @extend_schema(
        summary="휴대폰 인증번호 확인",
        description="휴대폰으로 발송된 인증번호를 검증하고 회원가입용 토큰을 발급합니다.",
        request=SmsVerifySerializer,
        responses={
            200: {"example": {"detail": "휴대폰 인증에 성공했습니다."}},
            400: {"example": {"detail": "인증번호가 잘못되었거나 만료되었습니다.."}},
        },
        tags=["Verification"],
    )
    def post(self, request: Request) -> Response:
        serializer = SmsVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        code = serializer.validated_data["code"]

        is_success = VerificationService.confirm_code(phone_number, code, "phone")

        if is_success:
            return Response({"detail": "휴대폰 인증에 성공했습니다."}, status=status.HTTP_200_OK)
        return Response({"detail": "인증번호가 잘못되었거나 만료되었습니다."}, status=status.HTTP_400_BAD_REQUEST)
