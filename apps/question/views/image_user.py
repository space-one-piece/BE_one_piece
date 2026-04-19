from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.question.extend_schema import value_list
from apps.question.serializers.image_user_serializers import ImageSerializer
from apps.question.service.image_user import image_new


class ImageUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["quest"],
        summary="향기 결과 프로필 저장 API",
        description="향기 결과 프로필 저장 API",
        request=ImageSerializer,
        responses={
            200: OpenApiResponse(response=ImageSerializer, examples=[value_list["200"]]),
            400: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[value_list["400"]]),
            401: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[value_list["401"]]),
            403: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[value_list["403"]]),
            404: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[value_list["404"]]),
        },
    )
    def put(self, request: Request, requests_id: int) -> Response:
        return Response({"message": "이미지 저장"})

    @extend_schema(
        tags=["quest"],
        summary="향기 결과 프로필 생성 API",
        description="향기 결과 프로필 생성 API",
        request=ImageSerializer,
        responses={
            200: OpenApiResponse(response=ImageSerializer, examples=[value_list["200"]]),
            401: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[value_list["401"]]),
            403: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[value_list["403"]]),
            404: OpenApiResponse(response=OpenApiTypes.OBJECT, examples=[value_list["404"]]),
        },
    )
    def post(self, request: Request, requests_id: int) -> Response:
        data = image_new(request.user.id, requests_id)
        return Response({"message": data})
