# Create your views here.
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class QuestAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        return Response({"message": "Hello World!"})
