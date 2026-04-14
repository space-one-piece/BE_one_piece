from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.question.extend_schema import value_list


class KeywordAPIView(APIView):
    """질문 키워드 형식 조회 출력 API"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["quest"],
        description="키워드 조회 API",
        examples=[value_list["200_keyword_get"], value_list["401"], value_list["404"]],
        responses={200: value_list["200_keyword_get"], 401: value_list["401"], 404: value_list["404"]},
    )
    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        return Response({"message": "질문 조회"})

    @extend_schema(
        tags=["quest"],
        description="키워드 답변 API",
        examples=[value_list["201"], value_list["400_question"], value_list["401"]],
        responses={201: value_list["201"], 400: value_list["400_question"], 401: value_list["401"]},
    )
    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        return Response({"message": "결과 조회"})
