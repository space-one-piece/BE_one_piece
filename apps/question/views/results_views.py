from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.question.extend_schema import value_list


class ResultsCreateUrlAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["quest"],
        description="web share 생성 API",
        examples=[value_list["200_web_post"], value_list["401"], value_list["404"]],
        responses={200: value_list["200_web_get"], 401: value_list["401"], 404: value_list["404"]},
    )
    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        return Response({"message": "web share url 생성"})


class ResultsViewAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["quest"],
        description="web share 조회 API",
        examples=[value_list["200_web_get"], value_list["404"], value_list["429"]],
        responses={200: value_list["200_web_get"], 404: value_list["404"], 429: value_list["429"]},
    )
    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        return Response({"message": "결과 조회"})
