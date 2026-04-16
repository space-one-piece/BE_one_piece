from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.RefreshToken_serializers import RefreshTokenSerializer
from apps.users.services.RefreshToken_services import refresh_token_service


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="JWT토큰 재발급",
        description="Refresh토큰을 이용해 새로운 Access 토큰과 Refresh토큰을 발급 받습니다.",
        request=RefreshTokenSerializer,
        responses={200: RefreshTokenSerializer, 400: None, 401: None},
        tags=["accounts"],
    )
    def post(self, request: Request) -> Response:
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]
        new_token = refresh_token_service(refresh_token)

        return Response(new_token, status=status.HTTP_200_OK)
