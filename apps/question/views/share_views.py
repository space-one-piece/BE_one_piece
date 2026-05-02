from concurrent.futures import ThreadPoolExecutor

from django.http import HttpResponse
from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.question.extend_schema import value_list
from apps.question.serializers.share_serializers import (
    ShareRequestSerializer,
    ShareResponseSerializer,
)
from apps.question.service.discord_service import send_discord, send_discord_file
from apps.question.service.image_user_service import ImageUserService
from apps.question.service.kakao_service import send_kakao


class ShareView(APIView):
    """
    POST /share/
    Body (JSON):
      {
        "channels": ["kakao", "discord"],
        "text": "안녕하세요",
        "url": "https://example.com",
        "image_url": "https://example.com/img.png"
      }
    Header:
      X-Kakao-Token: <카카오 OAuth access_token>  (카카오 채널 사용 시 필수)
    """

    @extend_schema(
        tags=["share"],
        summary="텍스트/URL/이미지 공유 API",
        description=(
            "카카오톡 또는 디스코드로 텍스트, URL, 이미지를 공유합니다.\n\n"
            "카카오톡 채널 사용 시 `X-Kakao-Token` 헤더가 필수입니다.\n"
            "여러 채널을 동시에 전송하며, 일부 채널 실패 시에도 200을 반환하고 `success` 필드로 구분합니다."
        ),
        parameters=[
            OpenApiParameter(
                name="X-Kakao-Token",
                location=OpenApiParameter.HEADER,
                description="카카오 OAuth 사용자 액세스 토큰 (kakao 채널 사용 시 필수)",
                required=False,
                type=OpenApiTypes.STR,
            ),
        ],
        request=ShareRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    value_list["200_share"],
                    value_list["200_share_partial"],
                ],
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    value_list["400_share_validation"],
                    value_list["400_share_kakao_token"],
                ],
            ),
            401: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["401"]],
            ),
            403: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["403"]],
            ),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = ShareRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        channels = data["channels"]
        kakao_token = request.headers.get("X-Kakao-Token")

        # 각 채널 전송 함수 준비
        tasks = []
        if "kakao" in channels:
            if not kakao_token:
                return Response(
                    {"detail": "카카오 채널은 X-Kakao-Token 헤더가 필요합니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            tasks.append(lambda: send_kakao(data, kakao_token))

        if "discord" in channels:
            tasks.append(lambda: send_discord(data))

        # ThreadPoolExecutor로 병렬 전송 (Django는 기본적으로 동기)
        results = []
        with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            futures = [executor.submit(task) for task in tasks]
            results = [f.result() for f in futures]

        response_serializer = ShareResponseSerializer({"results": results})
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ShareFileView(APIView):
    """
    POST /share/file/
    multipart/form-data:
      channels=discord   (현재 파일은 Discord만 지원)
      file=<업로드할 파일>
    """

    @extend_schema(
        tags=["share"],
        summary="파일 첨부 공유 API",
        description=(
            "파일을 업로드해 디스코드 채널에 첨부 전송합니다.\n\n"
            "`multipart/form-data` 형식으로 요청하며 `channels`와 `file` 필드가 필요합니다."
        ),
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "string",
                        "example": "discord",
                        "description": "쉼표 구분 채널명 (현재 discord만 지원)",
                    },
                    "file": {
                        "type": "string",
                        "format": "binary",
                        "description": "업로드할 파일",
                    },
                },
                "required": ["channels", "file"],
            }
        },
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["200_share_file"]],
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["400_share_no_file"]],
            ),
            401: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["401"]],
            ),
            403: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["403"]],
            ),
        },
    )
    def post(self, request: Request) -> Response:
        channels_raw = request.data.get("channels", "")
        channels = [c.strip() for c in channels_raw.split(",") if c.strip()]
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return Response({"detail": "file 필드가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        results = []
        if "discord" in channels:
            result = send_discord_file(
                file=uploaded_file,
                filename=uploaded_file.name,
                content_type=uploaded_file.content_type,
            )
            results.append(result)

        response_serializer = ShareResponseSerializer({"results": results})
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ShareOGView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["share"],
        summary="공유 API",
        request=None,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["200_share_file"]],
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["400_share_no_file"]],
            ),
            401: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["401"]],
            ),
            403: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[value_list["403"]],
            ),
        },
    )
    def get(self, request: Request, share_id: str) -> HttpResponse:
        result = ImageUserService.web_data(share_id)
        return render(request, "og_share.html", result)
