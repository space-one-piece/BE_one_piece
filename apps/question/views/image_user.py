from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.question.extend_schema import value_list
from apps.question.serializers.image_user_serializers import ImageSerializer


class ImageUserAPIView(APIView):
    @extend_schema(
        tags=["quest"],
        summary="향기 결과 프로필 저장 API",
        description="향기 결과 프로필 저장 API",
        request=ImageSerializer,
        responses={
            200: OpenApiResponse(response=ImageSerializer, examples=[value_list["200"]]),
            400: OpenApiResponse(examples=[value_list["400"]]),
            401: OpenApiResponse(examples=[value_list["401"]]),
            403: OpenApiResponse(examples=[value_list["403"]]),
            404: OpenApiResponse(examples=[value_list["404"]]),
        },
    )
    def put(self, request: Request, *args: object, **kwargs: object) -> Response:
        return Response({"message": "이미지 저장"})
