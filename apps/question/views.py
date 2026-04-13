# Create your views here.
from rest_framework.views import APIView


class QuestAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        return Response({"message": "Hello World!"})
