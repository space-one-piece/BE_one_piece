from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class ImageUserAPIView(APIView):
    """향 프로필 저장 API"""

    @extend_schema(tags=["quest"])
    def put(self, request: Request, *args: object, **kwargs: object) -> Response:
        return Response({"message": "이미지 저장"})
