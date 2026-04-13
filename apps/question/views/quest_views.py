# Create your views here.
from drf_yasg.utils import swagger_auto_schema  # type: ignore
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


@swagger_auto_schema(tags=["quest"])
class QuestAPIView(APIView):
    """질문 설문지 형식 조회 출력 API"""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        return Response({"message": "질문 조회"})

    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        return Response({"message": "결과 조회"})
