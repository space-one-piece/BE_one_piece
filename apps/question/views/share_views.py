from django.http import HttpResponse
from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.question.extend_schema import value_list
from apps.question.service.image_user_service import ImageUserService


class ShareOGView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["share"],
        summary="공유 OG 페이지 조회 API",
        request=None,
        description="소셜 플랫폼 에서만 미리보기 출력용",
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
