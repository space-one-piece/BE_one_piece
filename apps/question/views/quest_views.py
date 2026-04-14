from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class QuestAPIView(APIView):
    """질문 설문지 형식 조회 출력 API"""

    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["quest"])
    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        return Response({"message": "질문 조회"})

    @extend_schema(tags=["quest"])
    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        return Response({"message": "결과 조회"})
