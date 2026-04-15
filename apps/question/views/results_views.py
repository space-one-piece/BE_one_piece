from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.question.extend_schema import value_list
from apps.question.serializers.results_serializers import ResultsSerializer


class ResultsCreateUrlAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["quest"],
        summary="web share 생성 API",
        description="web share 생성 API",
        request=ResultsSerializer,
        responses={
            200: OpenApiResponse(response=ResultsSerializer, examples=[value_list["200_web_get"]]),
            401: OpenApiResponse(examples=[value_list["401"]]),
            404: OpenApiResponse(examples=[value_list["404"]]),
        },
    )
    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        return Response({"message": "web share url 생성"})


class ResultsViewAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["quest"],
        summary="web share 조회 API",
        description="web share 조회 API",
        request=ResultsSerializer,
        responses={
            200: OpenApiResponse(
                response=ResultsSerializer,
                examples=[value_list["200_web_get"]],
            ),
            404: OpenApiResponse(
                examples=[value_list["404"]],
            ),
            429: OpenApiResponse(
                examples=[value_list["429"]],
            ),
        },
    )
    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        return Response({"message": "결과 조회"})
