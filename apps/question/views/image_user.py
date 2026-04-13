from drf_yasg.utils import swagger_auto_schema  # type: ignore
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


@swagger_auto_schema(tags=["quest"])
class ImageUserAPIView(APIView):
    """향 프로필 저장 API"""

    def put(self, request: Request, *args: object, **kwargs: object) -> Response:
        return Response({"message": "이미지 저장"})
