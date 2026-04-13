from drf_yasg.utils import swagger_auto_schema  # type: ignore
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


@swagger_auto_schema(tags=["quest"])
class ResultsAPIView(APIView):
    """결과 url 생성 및 조회 API"""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        return Response({"message": "결과 조회"})

    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        return Response({"message": "web share url 생성"})
