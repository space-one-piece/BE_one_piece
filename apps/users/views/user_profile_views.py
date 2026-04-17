from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.Error_Response_Serializers import ErrorResponseSerializer
from apps.users.serializers.user_profile_serailzers import UserProfileSerializer


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="내 정보 조회",
        description="로그인한 사용자의 프로필 정보를 가져옵니다.",
        responses={
            200: UserProfileSerializer,
            401: ErrorResponseSerializer,
        },
        tags=["accounts"],
    )
    def get(self, request: Request) -> Response:
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
