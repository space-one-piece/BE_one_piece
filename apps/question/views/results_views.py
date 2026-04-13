from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class ResultsCreateUrlAPIView(APIView):
    """결과 url 생성 API"""

    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["quest"])
    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        return Response({"message": "web share url 생성"})


class ResultsViewAPIView(APIView):
    """결과 url 조회 API"""

    permission_classes = [AllowAny]

    @extend_schema(tags=["quest"])
    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        return Response({"message": "결과 조회"})
